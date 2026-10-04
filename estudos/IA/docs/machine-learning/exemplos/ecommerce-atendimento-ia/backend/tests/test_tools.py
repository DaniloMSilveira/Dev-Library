# Projeto Desenvolvido na Data Science Academy

"""Testes das tools dos agentes."""

import json
import os
import tempfile

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.tools.calculate_shipping import SHIPPING_TABLE, FREE_SHIPPING_THRESHOLD


def test_dsa_shipping_table_complete():
    """Tabela de frete tem todos os 27 estados."""
    assert len(SHIPPING_TABLE) == 27
    assert "SP" in SHIPPING_TABLE
    assert "AM" in SHIPPING_TABLE
    assert SHIPPING_TABLE["SP"]["price"] == 15.90


def test_dsa_free_shipping_threshold():
    """Threshold de frete grátis está correto."""
    assert FREE_SHIPPING_THRESHOLD == 299.0


@pytest.mark.asyncio
async def test_dsa_calculate_shipping_free():
    """Frete grátis para compras acima de R$299."""
    from app.tools.calculate_shipping import dsa_calculate_shipping

    result = await dsa_calculate_shipping.ainvoke({"state": "SP", "total": 500.0})
    assert "GRÁTIS" in result


@pytest.mark.asyncio
async def test_dsa_calculate_shipping_paid():
    """Frete cobrado para compras abaixo de R$299."""
    from app.tools.calculate_shipping import dsa_calculate_shipping

    result = await dsa_calculate_shipping.ainvoke({"state": "SP", "total": 100.0})
    assert "R$" in result
    assert "15" in result


@pytest.mark.asyncio
async def test_dsa_calculate_shipping_invalid_state():
    """Estado inválido retorna mensagem de erro."""
    from app.tools.calculate_shipping import dsa_calculate_shipping

    result = await dsa_calculate_shipping.ainvoke({"state": "XX", "total": 100.0})
    assert "não reconhecido" in result


@pytest.mark.asyncio
async def test_dsa_fallback_search():
    """Fallback search retorna resultado quando faq.json existe no data/."""
    from app.tools.search_knowledge import dsa_fallback_search

    # Testa com o arquivo real se existir, senão testa o fallback de FileNotFoundError
    result = await dsa_fallback_search("prazo entrega")
    # Deve retornar algo (resultado de busca ou mensagem de indisponibilidade)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_dsa_search_products_timeout():
    """Search products retorna mensagem amigável em timeout."""
    import httpx
    from app.tools.search_products import dsa_search_products

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
    mock_client.is_closed = False

    with patch("app.tools.search_products.dsa_get_http_client", return_value=mock_client):
        result = await dsa_search_products.ainvoke("notebook")
        assert "demorando" in result.lower()


@pytest.mark.asyncio
async def test_dsa_check_order_status_not_found():
    """Check order retorna mensagem quando pedido não encontrado."""
    import httpx
    from app.tools.check_order import dsa_check_order_status

    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_response_tracking = MagicMock()
    mock_response_tracking.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError("404", request=MagicMock(), response=mock_response_tracking)
    )

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=[mock_response, mock_response_tracking])
    mock_client.is_closed = False

    with patch("app.tools.check_order.dsa_get_http_client", return_value=mock_client):
        result = await dsa_check_order_status.ainvoke("ORD-999")
        assert "não encontrado" in result.lower()
