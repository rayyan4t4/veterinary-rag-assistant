from abc import ABC, abstractmethod
import hashlib
import math
import re


class EmbeddingProvider(ABC):
    model_name: str
    dimension: int

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic offline fallback for pipeline tests, not clinical semantic retrieval."""
    def __init__(self, model_name: str = "hash-fallback-v1", dimension: int = 1024):
        self.model_name, self.dimension = model_name, dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        results = []
        for text in texts:
            vector = [0.0] * self.dimension
            for token in re.findall(r"\w+", text.casefold(), re.UNICODE):
                digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimension
                vector[index] += 1.0 if digest[4] % 2 else -1.0
            norm = math.sqrt(sum(x * x for x in vector)) or 1.0
            results.append([x / norm for x in vector])
        return results
