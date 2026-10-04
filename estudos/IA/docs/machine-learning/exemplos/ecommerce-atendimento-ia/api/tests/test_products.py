# Projeto Desenvolvido na Data Science Academy

"""Testes dos endpoints de Produtos."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dsa_list_products(dsa_client: AsyncClient, dsa_sample_products):
    """GET /api/v1/products retorna lista paginada."""
    response = await dsa_client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 4
    assert len(data["items"]) == 4


@pytest.mark.asyncio
async def test_dsa_get_product_by_id(dsa_client: AsyncClient, dsa_sample_products):
    """GET /api/v1/products/{id} retorna produto correto."""
    response = await dsa_client.get("/api/v1/products/PROD-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "PROD-001"
    assert data["name"] == "iPhone 15 Pro 256GB"
    assert data["price"] == 7999.90


@pytest.mark.asyncio
async def test_dsa_get_product_not_found(dsa_client: AsyncClient, dsa_sample_products):
    """GET /api/v1/products/{id_invalido} retorna 404."""
    response = await dsa_client.get("/api/v1/products/PROD-999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dsa_filter_by_category(dsa_client: AsyncClient, dsa_sample_products):
    """GET /api/v1/products?category=smartphones filtra corretamente."""
    response = await dsa_client.get("/api/v1/products", params={"category": "smartphones"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert item["category"] == "smartphones"


@pytest.mark.asyncio
async def test_dsa_filter_by_price_range(dsa_client: AsyncClient, dsa_sample_products):
    """GET /api/v1/products?min_price=1000&max_price=8000 filtra por faixa de preço."""
    response = await dsa_client.get(
        "/api/v1/products", params={"min_price": 1000, "max_price": 8000}
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert 1000 <= item["price"] <= 8000


@pytest.mark.asyncio
async def test_dsa_search_products(dsa_client: AsyncClient, dsa_sample_products):
    """GET /api/v1/products/search?q=iphone retorna resultados relevantes."""
    response = await dsa_client.get("/api/v1/products/search", params={"q": "iphone"})
    assert response.status_code == 200
    data = response.json()
    items = data.get("items", [])
    assert len(items) >= 1
    assert any("iPhone" in p["name"] for p in items)


@pytest.mark.asyncio
async def test_dsa_list_categories(dsa_client: AsyncClient, dsa_sample_products):
    """GET /api/v1/products/categories retorna categorias."""
    response = await dsa_client.get("/api/v1/products/categories")
    assert response.status_code == 200
    data = response.json()
    assert "smartphones" in data
    assert "notebooks" in data
