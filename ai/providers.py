from abc import ABC, abstractmethod
import httpx


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system: str, user: str, evidence: list[str]) -> str: ...


class VisionProvider(ABC):
    @abstractmethod
    async def observe(self, image: bytes, mime_type: str) -> dict: ...


class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio: bytes, language: str | None) -> str: ...


class TextToSpeechProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, language: str) -> bytes: ...


class RerankerProvider(ABC):
    @abstractmethod
    async def rerank(self, query: str, documents: list[str]) -> list[int]: ...


class OpenRouterLLMProvider(LLMProvider):
    """Small OpenAI-compatible adapter; keys stay server-side."""

    def __init__(self, api_key: str, model: str, site_url: str = ""):
        self.api_key = api_key
        self.model = model or "openrouter/auto"
        self.site_url = site_url

    async def generate(self, system: str, user: str, evidence: list[str]) -> str:
        context = "\n\n".join(f"SOURCE {i}:\n{text}" for i, text in enumerate(evidence, 1))
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "max_tokens": 700,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Question: {user}\n\nTrusted evidence:\n{context}"},
            ],
        }
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
