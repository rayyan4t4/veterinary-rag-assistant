from abc import ABC, abstractmethod


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
