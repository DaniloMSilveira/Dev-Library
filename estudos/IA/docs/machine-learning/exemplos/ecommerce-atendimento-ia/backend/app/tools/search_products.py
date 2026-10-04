# Projeto Desenvolvido na Data Science Academy

"""Tool search_products — Busca produtos no catálogo via API."""

import logging
import httpx
from langchain_core.tools import tool
from app.tools import dsa_get_http_client

logger = logging.getLogger(__name__)


@tool
async def dsa_search_products(query: str) -> str:
    """Busca produtos no catálogo por texto. Use para encontrar produtos por nome, categoria ou característica."""
    try:
        client = dsa_get_http_client()
        response = await client.get("/api/v1/products/search", params = {"q": query})
        response.raise_for_status()
        data = response.json()
        products = data.get("items", [])

        if not products:
            return "Nenhum produto encontrado para essa busca."

        results = []
        for p in products[:5]:
            stock_status = "Em estoque" if p.get("stock", 0) > 0 else "Indisponível"
            results.append(
                f"- {p['name']} ({p['brand']}) — R${p['price']:,.2f} | "
                f"Avaliação: {p.get('rating', 0)}/5 | {stock_status}"
            )
        return "\n".join(results)
    except httpx.TimeoutException:
        logger.error("Timeout ao buscar produtos")
        return "O serviço de produtos está demorando para responder. Tente novamente."
    except httpx.ConnectError:
        logger.error("Falha de conexão ao buscar produtos")
        return "Serviço de produtos temporariamente indisponível."
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao buscar produtos: {e.response.status_code}")
        return f"Erro ao buscar produtos (código {e.response.status_code})."


@tool
async def dsa_get_product_details(product_id: str) -> str:
    """Retorna detalhes completos de um produto específico pelo ID."""
    try:
        client = dsa_get_http_client()
        response = await client.get(f"/api/v1/products/{product_id}")
        response.raise_for_status()
        p = response.json()

        specs_str = ""
        if p.get("specs"):
            specs_str = "\n".join(f"  {k}: {v}" for k, v in p["specs"].items())

        stock_status = "Em estoque" if p.get("stock", 0) > 0 else "Indisponível"
        return (
            f"Produto: {p['name']}\n"
            f"Marca: {p['brand']}\n"
            f"Categoria: {p['category']}\n"
            f"Preço: R${p['price']:,.2f}\n"
            f"Avaliação: {p.get('rating', 0)}/5 ({p.get('reviews_count', 0)} avaliações)\n"
            f"Disponibilidade: {stock_status}\n"
            f"Descrição: {p.get('description', '')}\n"
            f"Especificações:\n{specs_str}"
        )
    except httpx.TimeoutException:
        return f"Timeout ao buscar produto {product_id}."
    except httpx.HTTPStatusError:
        return f"Produto {product_id} não encontrado."


@tool
async def dsa_list_by_category(category: str) -> str:
    """Lista produtos de uma categoria específica (smartphones, notebooks, tablets, acessórios, smart_home)."""
    try:
        client = dsa_get_http_client()
        response = await client.get("/api/v1/products", params = {"category": category, "per_page": 10})
        response.raise_for_status()
        data = response.json()

        products = data.get("items", [])
        if not products:
            return f"Nenhum produto encontrado na categoria '{category}'."

        results = []
        for p in products:
            results.append(f"- {p['name']} — R${p['price']:,.2f} ({p['brand']})")
        return f"Produtos na categoria '{category}':\n" + "\n".join(results)
    except httpx.TimeoutException:
        return "Timeout ao listar categoria."
    except httpx.ConnectError:
        return "Serviço de produtos temporariamente indisponível."
    except httpx.HTTPStatusError as e:
        return f"Erro ao listar categoria: {e.response.status_code}"
