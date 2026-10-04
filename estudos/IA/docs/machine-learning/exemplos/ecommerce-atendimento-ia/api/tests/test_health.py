# Projeto Desenvolvido na Data Science Academy

"""Testes dos endpoints de Health e Root."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_dsa_health_check(dsa_client: AsyncClient):
    """GET /health retorna status healthy quando DB conectado."""
    # Mock o engine.connect() para evitar conexao com PostgreSQL real
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    with patch("app.main.engine") as mock_engine:
        mock_engine.connect.return_value = mock_cm
        response = await dsa_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_dsa_health_check_unhealthy(dsa_client: AsyncClient):
    """GET /health retorna 503 quando DB desconectado."""
    with patch("app.main.engine") as mock_engine:
        mock_engine.connect.side_effect = Exception("Connection refused")
        response = await dsa_client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_dsa_root(dsa_client: AsyncClient):
    """GET / retorna info da API."""
    response = await dsa_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
