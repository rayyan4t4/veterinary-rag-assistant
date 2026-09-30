"""Memory-bounded ingestion for large, text-native PDFs."""
import argparse
import asyncio
import hashlib
from pathlib import Path

from pypdf import PdfReader
from sqlalchemy import delete, select

from ai.embeddings.providers import HashEmbeddingProvider
from ai.rag.chunking import structure_aware_chunks
from ai.safety.prompt_injection import flag_untrusted_instructions
from apps.api.app.config import get_settings
from apps.api.app.db import SessionLocal, engine
from apps.api.app.models import Base, KnowledgeChunk, KnowledgeDocument


async def ingest_pdf(path: Path, title: str, organization: str) -> None:
    settings = get_settings()
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    reader = PdfReader(str(path))
    embedder = HashEmbeddingProvider(dimension=settings.embedding_dimension)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        existing = await db.scalar(
            select(KnowledgeDocument).where(KnowledgeDocument.checksum == checksum)
        )
        if existing and existing.status == "ready":
            count = len(
                (await db.scalars(
                    select(KnowledgeChunk).where(KnowledgeChunk.document_id == existing.id)
                )).all()
            )
            print(f"Already indexed: document={existing.id} chunks={count}", flush=True)
            return
        if existing:
            document = existing
            await db.execute(
                delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document.id)
            )
            document.status = "processing"
            document.error = None
        else:
            document = KnowledgeDocument(
                title=title,
                filename=path.name,
                checksum=checksum,
                source_organization=organization,
                source_url=None,
                species="livestock",
                topic="clinical veterinary medicine",
                language="en",
                status="processing",
                is_trusted=True,
            )
            db.add(document)
        await db.commit()
        await db.refresh(document)

        chunk_number = 0
        for page_index, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            chunks = structure_aware_chunks(
                [(page_index, text)],
                settings.rag_chunk_tokens,
                settings.rag_chunk_overlap,
            )
            vectors = await embedder.embed([chunk.text for chunk in chunks])
            for chunk, vector in zip(chunks, vectors):
                db.add(
                    KnowledgeChunk(
                        document_id=document.id,
                        chunk_number=chunk_number,
                        content=chunk.text,
                        page_number=page_index,
                        section_heading=chunk.section,
                        embedding=vector,
                        embedding_model=embedder.model_name,
                        metadata_json={
                            "extraction_method": "native_pdf",
                            "injection_markers": flag_untrusted_instructions(chunk.text),
                            "source_status": "private_academic_copy",
                        },
                    )
                )
                chunk_number += 1
            if page_index % 25 == 0:
                await db.commit()
            if page_index % 100 == 0 or page_index == len(reader.pages):
                print(
                    f"pages={page_index}/{len(reader.pages)} chunks={chunk_number}",
                    flush=True,
                )
        document.status = "ready"
        await db.commit()
        print(
            f"Indexed document={document.id} pages={len(reader.pages)} chunks={chunk_number} "
            f"embedding_model={embedder.model_name}",
            flush=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--organization", required=True)
    args = parser.parse_args()
    asyncio.run(ingest_pdf(args.pdf.resolve(), args.title, args.organization))


if __name__ == "__main__":
    main()
