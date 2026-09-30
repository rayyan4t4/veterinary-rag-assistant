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
    terms = set(re.findall(r"\w+", query.casefold(), re.UNICODE))
    vector_rank = sorted(rows, key=lambda row: cosine(query_embedding, row[0].embedding), reverse=True)
    keyword_rank = sorted(rows, key=lambda row: len(terms & set(re.findall(r"\w+", row[0].content.casefold(), re.UNICODE))), reverse=True)
    scores: dict[str, float] = {}
    lookup = {}
    for ranking in (vector_rank, keyword_rank):
        for rank, row in enumerate(ranking[:30], 1):
            lookup[row[0].id] = row
            scores[row[0].id] = scores.get(row[0].id, 0) + 1 / (60 + rank)
    ordered = sorted(scores, key=scores.get, reverse=True)[:limit]
    return [(lookup[key][0], lookup[key][1], scores[key]) for key in ordered]
