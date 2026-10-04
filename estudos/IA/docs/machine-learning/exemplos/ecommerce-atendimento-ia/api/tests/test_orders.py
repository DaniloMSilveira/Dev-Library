# Projeto Desenvolvido na Data Science Academy

"""Testes dos endpoints de Pedidos."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dsa_create_order(dsa_client: AsyncClient, dsa_sample_products, dsa_sample_customer):
    """POST /api/v1/orders cria pedido e retorna dados completos."""
    response = await dsa_client.post(
        "/api/v1/orders",
        json={
            "customer_id": "CUST-001",
            "items": [{"product_id": "PROD-001", "quantity": 1}],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == "CUST-001"
    assert data["status"] == "confirmed"
    assert data["total"] == 7999.90
    assert data["tracking_code"] is not None
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_dsa_create_order_multiple_items(
    dsa_client: AsyncClient, dsa_sample_products, dsa_sample_customer
):
    """POST /api/v1/orders com multiplos itens calcula total corretamente."""
    response = await dsa_client.post(
        "/api/v1/orders",
        json={
            "customer_id": "CUST-001",
            "items": [
                {"product_id": "PROD-001", "quantity": 1},
                {"product_id": "PROD-002", "quantity": 2},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    expected_total = 7999.90 + (6499.90 * 2)
    assert abs(data["total"] - expected_total) < 0.01
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_dsa_create_order_insufficient_stock(
    dsa_client: AsyncClient, dsa_sample_products, dsa_sample_customer
):
    """POST /api/v1/orders com produto sem estoque retorna erro 400."""
    response = await dsa_client.post(
        "/api/v1/orders",
        json={
            "customer_id": "CUST-001",
            "items": [{"product_id": "PROD-020", "quantity": 1}],
        },
    )
    assert response.status_code == 400
    assert "Estoque insuficiente" in response.json()["detail"]


@pytest.mark.asyncio
async def test_dsa_create_order_product_not_found(
    dsa_client: AsyncClient, dsa_sample_products, dsa_sample_customer
):
    """POST /api/v1/orders com produto inexistente retorna erro 400."""
    response = await dsa_client.post(
        "/api/v1/orders",
        json={
            "customer_id": "CUST-001",
            "items": [{"product_id": "PROD-999", "quantity": 1}],
        },
    )
    assert response.status_code == 400
    assert "não encontrado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_dsa_get_order_by_id(dsa_client: AsyncClient, dsa_sample_orders):
    """GET /api/v1/orders/{id} retorna pedido com itens."""
    response = await dsa_client.get("/api/v1/orders/ORD-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "ORD-001"
    assert data["status"] == "shipped"
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_dsa_get_order_not_found(dsa_client: AsyncClient):
    """GET /api/v1/orders/{id_invalido} retorna 404."""
    response = await dsa_client.get("/api/v1/orders/ORD-999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dsa_get_order_by_tracking_code(dsa_client: AsyncClient, dsa_sample_orders):
    """GET /api/v1/orders/tracking/{code} busca por tracking code."""
    response = await dsa_client.get("/api/v1/orders/tracking/BR100000001XX")
    assert response.status_code == 200
    data = response.json()
    assert data["tracking_code"] == "BR100000001XX"


@pytest.mark.asyncio
async def test_dsa_update_order_status(dsa_client: AsyncClient, dsa_sample_orders):
    """PATCH /api/v1/orders/{id}/status atualiza status."""
    response = await dsa_client.patch(
        "/api/v1/orders/ORD-001/status",
        json={"status": "delivered"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "delivered"


@pytest.mark.asyncio
async def test_dsa_invalid_status_transition(dsa_client: AsyncClient, dsa_sample_orders):
    """PATCH com transicao invalida retorna erro 400."""
    # Primeiro marcar como delivered
    await dsa_client.patch("/api/v1/orders/ORD-001/status", json={"status": "delivered"})
    # Tentar voltar para processing (invalido)
    response = await dsa_client.patch(
        "/api/v1/orders/ORD-001/status",
        json={"status": "processing"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_dsa_get_customer_orders(dsa_client: AsyncClient, dsa_sample_orders):
    """GET /api/v1/orders/customer/{customer_id} retorna lista paginada."""
    response = await dsa_client.get("/api/v1/orders/customer/CUST-001")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1
