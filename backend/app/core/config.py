# app/core/config.py
import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, AnyHttpUrl

load_dotenv()


class Settings(BaseModel):
    # FastAPI
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "open_learning_assistant")
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")

    # DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://user:pass@postgres:5432/ola",
    )

    # OpenSearch
    OPENSEARCH_HOST: str = os.getenv("OPENSEARCH_HOST", "http://opensearch:9200")
    OPENSEARCH_USER: str = os.getenv("OPENSEARCH_USER", "admin")
    OPENSEARCH_PASSWORD: str = os.getenv("OPENSEARCH_PASSWORD", "admin")
    OPENSEARCH_INDEX: str = os.getenv("OPENSEARCH_INDEX", "content_chunks")

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" | "gemini"
    OLLAMA_BASE_URL: AnyHttpUrl | None = os.getenv(
        "OLLAMA_BASE_URL",
        "http://ollama:11434",
    )
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # Object storage
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "local")  # local | s3 | minio
    STORAGE_BASE_PATH: str = os.getenv("STORAGE_BASE_PATH", "./data/materials")

        # JWT / Auth
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-prod")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30")
    )
    REFRESH_TOKEN_SECRET_KEY: str = os.getenv(
        "REFRESH_TOKEN_SECRET_KEY",
        JWT_SECRET_KEY,
    )



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
