# Projeto Desenvolvido na Data Science Academy

"""Testes dos endpoints de Clientes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dsa_create_customer(dsa_client: AsyncClient):
    """POST /api/v1/customers cria cliente e retorna dados."""
    response = await dsa_client.post(
        "/api/v1/customers",
        json={"name": "Joao Santos", "email": "joao@email.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Joao Santos"
    assert data["email"] == "joao@email.com"
    assert data["id"].startswith("CUST-")


@pytest.mark.asyncio
async def test_dsa_create_customer_idempotent(dsa_client: AsyncClient):
    """POST com email existente retorna cliente existente."""
    await dsa_client.post(
        "/api/v1/customers",
        json={"name": "Ana Costa", "email": "ana@email.com"},
    )
    response = await dsa_client.post(
        "/api/v1/customers",
        json={"name": "Ana Costa Outro Nome", "email": "ana@email.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ana Costa"


@pytest.mark.asyncio
async def test_dsa_get_customer_by_id(dsa_client: AsyncClient, dsa_sample_customer):
    """GET /api/v1/customers/{id} retorna cliente."""
    response = await dsa_client.get("/api/v1/customers/CUST-001")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maria Silva"


@pytest.mark.asyncio
async def test_dsa_get_customer_not_found(dsa_client: AsyncClient):
    """GET /api/v1/customers/{id_invalido} retorna 404."""
    response = await dsa_client.get("/api/v1/customers/CUST-999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dsa_get_customer_by_email(dsa_client: AsyncClient, dsa_sample_customer):
    """GET /api/v1/customers/email/{email} retorna cliente."""
    response = await dsa_client.get("/api/v1/customers/email/maria.silva@email.com")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "CUST-001"


@pytest.mark.asyncio
async def test_dsa_get_customer_by_email_not_found(dsa_client: AsyncClient):
    """GET /api/v1/customers/email/{email_invalido} retorna 404."""
    response = await dsa_client.get("/api/v1/customers/email/inexistente@email.com")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dsa_create_customer_invalid_email(dsa_client: AsyncClient):
    """POST com email invalido retorna 422."""
    response = await dsa_client.post(
        "/api/v1/customers",
        json={"name": "Teste", "email": "email-invalido"},
    )
    assert response.status_code == 422
