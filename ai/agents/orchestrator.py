from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.app.schemas import ChatRequest, ChatResponse, Citation
from ai.embeddings.providers import HashEmbeddingProvider
from ai.retrieval.hybrid import hybrid_retrieve
from ai.safety.triage import assess_triage

SAFETY_DISCLAIMER = "Online guidance cannot confirm a diagnosis and does not replace an examination by a licensed veterinarian."


async def answer(request: ChatRequest, db: AsyncSession) -> ChatResponse:
    triage = assess_triage(request.text, request.language)
    if triage.urgency == "emergency":
        return ChatResponse(answer=f"SEEK URGENT VETERINARY CARE. {triage.recommended_action}", language=request.language, urgency="emergency", citations=[], disclaimer=SAFETY_DISCLAIMER, suggested_next_questions=[], retrieval_metadata={"safety_short_circuit": True})
    embedder = HashEmbeddingProvider()
    evidence = await hybrid_retrieve(db, request.text, embedder, request.species.value if request.species else None)
    citations = [Citation(document_title=doc.title, source_organization=doc.source_organization, page=chunk.page_number, section=chunk.section_heading, source_url=doc.source_url, chunk_id=chunk.id, document_id=doc.id, excerpt=chunk.content[:360]) for chunk, doc, _ in evidence]
    if not citations:
        message = "میرے پاس ویٹرنری علم کی بنیاد میں اتنی قابل اعتماد معلومات نہیں ہیں کہ میں اعتماد سے جواب دے سکوں۔" if request.language == "ur" else "I do not have enough reliable information in the veterinary knowledge base to answer this confidently."
    else:
        findings = "\n\n".join(f"[{i}] {c.excerpt}" for i, c in enumerate(citations, 1))
        prefix = "Clinical considerations (not a diagnosis):" if request.mode == "veterinarian" else "What the available veterinary sources suggest:"
        message = f"{prefix}\n\n{findings}\n\nDiscuss these findings with a veterinarian who can examine the animal."
    return ChatResponse(answer=message, language=request.language, urgency=triage.urgency, citations=citations, disclaimer=SAFETY_DISCLAIMER, suggested_next_questions=["What changes should I monitor?", "What information should I bring to the veterinarian?"], retrieval_metadata={"retrieved": len(evidence), "strategy": "hybrid_rrf", "reranking": "disabled"})
