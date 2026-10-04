# Projeto Desenvolvido na Data Science Academy

"""Testes dos endpoints de Chat."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_dsa_send_message(dsa_client: AsyncClient):
    """POST /api/v1/chat com mensagem valida retorna resposta."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value={
        "response": "Ola! Como posso ajudar?",
        "agent_used": "router_agent",
        "sources": [],
    })

    mock_http_client = AsyncMock()
    mock_http_client.post = AsyncMock(return_value=mock_resp)

    with patch("app.services.chat_service.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        response = await dsa_client.post(
            "/api/v1/chat/",
            json={"message": "Ola, tudo bem?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "agent_used" in data


@pytest.mark.asyncio
async def test_dsa_send_empty_message(dsa_client: AsyncClient):
    """POST /api/v1/chat com mensagem vazia retorna erro 422."""
    response = await dsa_client.post("/api/v1/chat/", json={"message": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_dsa_send_no_message(dsa_client: AsyncClient):
    """POST /api/v1/chat sem campo message retorna erro 422."""
    response = await dsa_client.post("/api/v1/chat/", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_dsa_get_conversation_not_found(dsa_client: AsyncClient):
    """GET /api/v1/chat/{id} com ID inexistente retorna 404."""
    response = await dsa_client.get("/api/v1/chat/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dsa_send_message_agent_failure(dsa_client: AsyncClient):
    """POST /api/v1/chat quando agente falha retorna resposta de fallback."""
    import httpx as httpx_lib

    with patch("app.services.chat_service.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post = AsyncMock(side_effect=httpx_lib.ConnectError("Connection refused"))
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)

        response = await dsa_client.post(
            "/api/v1/chat/",
            json={"message": "Ola"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_used"] == "error_handler"
        assert "indisponivel" in data["response"].lower() or "dificuldades" in data["response"].lower()
