import asyncio

from ai.embeddings.providers import HashEmbeddingProvider
from ai.retrieval.hybrid import hybrid_retrieve
from apps.api.app.db import SessionLocal


async def main() -> None:
    async with SessionLocal() as db:
        rows = await hybrid_retrieve(
            db,
            "clinical signs and diagnosis of pneumonia in cattle",
            HashEmbeddingProvider(),
            species="livestock",
            limit=3,
        )
        print(f"RESULTS {len(rows)}")
        for index, (chunk, _, score) in enumerate(rows, 1):
            excerpt = chunk.content[:180].replace("\n", " ")
            print(f"{index} PAGE {chunk.page_number} SCORE {score:.6f} TEXT {excerpt}")


if __name__ == "__main__":
    asyncio.run(main())
