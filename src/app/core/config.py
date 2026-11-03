from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Knowledge Assistant"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    data_dir: str = "./data"
    upload_dir: str = "./data/uploads"
    chroma_dir: str = "./data/chroma"
    conversation_file: str = "./data/conversations.json"
    max_upload_size_mb: int = 20
    allowed_extensions: str = "pdf,docx,txt,csv"
    chunk_size: int = 900
    chunk_overlap: int = 120
    top_k: int = 5
    similarity_threshold: float = 0.35
    embedding_model: str = "all-MiniLM-L6-v2"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {x.strip().lower() for x in self.allowed_extensions.split(",") if x.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
