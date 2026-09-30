import math
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.app.models import KnowledgeChunk, KnowledgeDocument
from ai.embeddings.providers import EmbeddingProvider


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b)) / ((math.sqrt(sum(x*x for x in a)) or 1) * (math.sqrt(sum(y*y for y in b)) or 1))


async def hybrid_retrieve(db: AsyncSession, query: str, embedder: EmbeddingProvider, species: str | None = None, limit: int = 6):
    stmt = select(KnowledgeChunk, KnowledgeDocument).join(KnowledgeDocument).where(KnowledgeDocument.status == "ready", KnowledgeDocument.is_trusted.is_(True))
    if species:
        stmt = stmt.where((KnowledgeDocument.species == species) | (KnowledgeDocument.species.is_(None)))
    rows = (await db.execute(stmt)).all()
    query_embedding = (await embedder.embed([query]))[0]
    normalized_query = query.casefold()
    terms = set(re.findall(r"\w+", normalized_query, re.UNICODE))
    vector_rank = sorted(rows, key=lambda row: cosine(query_embedding, row[0].embedding), reverse=True)
    def keyword_score(row):
        content = row[0].content.casefold()
        tokens = re.findall(r"\w+", content, re.UNICODE)
        counts = {term: tokens.count(term) for term in terms}
        coverage = sum(1 for count in counts.values() if count)
        frequency = sum(min(count, 8) for count in counts.values())
        phrase_bonus = 12 if normalized_query in content else 0
        index_penalty = 0.15 if content.lstrip().startswith("index") else 1.0
        return (coverage * 6 + frequency + phrase_bonus) * index_penalty
    keyword_rank = sorted(rows, key=keyword_score, reverse=True)
    scores: dict[str, float] = {}
    lookup = {}
    vector_weight = 0.15 if embedder.model_name.startswith("hash-fallback") else 1.0
    for ranking, weight in ((vector_rank, vector_weight), (keyword_rank, 1.0)):
        for rank, row in enumerate(ranking[:30], 1):
            if ranking is keyword_rank and keyword_score(row) <= 0:
                continue
            lookup[row[0].id] = row
            scores[row[0].id] = scores.get(row[0].id, 0) + weight / (60 + rank)
    ordered = sorted(scores, key=scores.get, reverse=True)[:limit]
    return [(lookup[key][0], lookup[key][1], scores[key]) for key in ordered]
