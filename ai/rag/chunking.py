from dataclasses import dataclass
import re


@dataclass
class Chunk:
    text: str
    page: int | None
    section: str | None
    number: int


def structure_aware_chunks(pages: list[tuple[int, str]], target_words: int = 450, overlap: int = 60) -> list[Chunk]:
    chunks: list[Chunk] = []
    section = None
    buffer: list[str] = []
    start_page = None
    for page, text in pages:
        for paragraph in re.split(r"\n\s*\n", text):
            paragraph = " ".join(paragraph.split()).strip()
            if not paragraph:
                continue
            if len(paragraph) < 120 and (paragraph.isupper() or paragraph.endswith(":")):
                section = paragraph.rstrip(":")
            words = paragraph.split()
            if start_page is None:
                start_page = page
            if buffer and len(buffer) + len(words) > target_words:
                chunks.append(Chunk(" ".join(buffer), start_page, section, len(chunks)))
                buffer = buffer[-overlap:] if overlap else []
                start_page = page
            buffer.extend(words)
    if buffer:
        chunks.append(Chunk(" ".join(buffer), start_page, section, len(chunks)))
    return chunks
