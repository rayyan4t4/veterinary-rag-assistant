from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    database_url: str = "sqlite+aiosqlite:///./vet_assistant.db"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    llm_provider: str = "disabled"
    llm_model: str = ""
    llm_api_key: str = ""
    embedding_provider: str = "hash"
    embedding_model: str = "BAAI/bge-m3"
    embedding_dimension: int = 1024
    reranker_provider: str = "disabled"
    vision_provider: str = "disabled"
    stt_provider: str = "disabled"
    tts_provider: str = "browser"
    max_upload_mb: int = 20
    rag_candidate_limit: int = 20
    rag_context_limit: int = 6
    rag_chunk_tokens: int = 450
    rag_chunk_overlap: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
