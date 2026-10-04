# Projeto Desenvolvido na Data Science Academy
"""Configurações da aplicação via Pydantic BaseSettings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da API carregadas de variáveis de ambiente."""

    APP_NAME: str = "Tech Store Brasil"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://ecommerce_user:ecommerce_pass@db:5432/ecommerce"
    BACKEND_URL: str = "http://backend:8001"
    ALLOWED_ORIGINS: str = "http://localhost:8501"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
