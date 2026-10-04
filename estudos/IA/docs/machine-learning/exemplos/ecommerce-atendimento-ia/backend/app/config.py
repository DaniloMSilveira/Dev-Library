# Projeto Desenvolvido na Data Science Academy
"""Configurações do backend via Pydantic BaseSettings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações do backend."""

    OPENAI_API_KEY: str = ""
    API_URL: str = "http://api:8000"
    CHROMADB_HOST: str = "chromadb"
    CHROMADB_PORT: int = 8000
    MODEL_NAME: str = "gpt-5-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    DEBUG: bool = False
    HTTP_TIMEOUT: float = 10.0
    MIN_SIMILARITY: float = 0.5

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v == "coloque-aqui-sua-api":
            raise ValueError(
                "OPENAI_API_KEY deve ser configurada. "
                "Defina a variável de ambiente OPENAI_API_KEY com sua chave da OpenAI."
            )
        return v

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
