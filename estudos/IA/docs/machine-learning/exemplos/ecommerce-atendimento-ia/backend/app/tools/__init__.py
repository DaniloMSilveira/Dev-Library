# Projeto Desenvolvido na Data Science Academy

"""Tools dos agentes — Singleton de httpx.AsyncClient para connection pooling."""

import httpx
from app.config import settings

# Singleton para reutilizar conexões entre tools (evita criar novo client a cada chamada)
_http_client: httpx.AsyncClient | None = None


def dsa_get_http_client() -> httpx.AsyncClient:
    """Retorna o httpx.AsyncClient compartilhado entre tools."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            base_url = settings.API_URL,
            timeout = settings.HTTP_TIMEOUT,
            follow_redirects = True,
        )

    return _http_client
