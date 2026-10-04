# Projeto Desenvolvido na Data Science Academy

"""Tool check_order — Consulta status de pedido via API."""

import logging
import httpx
from langchain_core.tools import tool
from app.tools import dsa_get_http_client

logger = logging.getLogger(__name__)

# Tradução de status técnicos (inglês) para rótulos amigáveis (português)
STATUS_LABELS = {
    "confirmed": "Confirmado",
    "processing": "Em preparação",
    "shipped": "Enviado",
    "delivered": "Entregue",
    "cancelled": "Cancelado",
}


@tool
async def dsa_check_order_status(order_identifier: str) -> str:
    """Consulta o status de um pedido pelo ID (ex: ORD-001) ou código de rastreamento (ex: BR100000001XX)."""
    order_identifier = order_identifier.strip().upper()
    try:
        client = dsa_get_http_client()
        
        # Tenta buscar como ID; se 404, tenta como código de rastreamento (fallback)
        response = await client.get(f"/api/v1/orders/{order_identifier}")
        if response.status_code == 404:
            response = await client.get(f"/api/v1/orders/tracking/{order_identifier}")
        
        response.raise_for_status()
        order = response.json()

        status_label = STATUS_LABELS.get(order["status"], order["status"])
        tracking = order.get("tracking_code") or "Ainda não disponível"

        items_str = ""
        for item in order.get("items", []):
            name = item.get("product_name", item["product_id"])
            items_str += f"\n  - {name} (x{item['quantity']}) — R${item['unit_price']:,.2f}"

        return (
            f"Pedido: {order['id']}\n"
            f"Status: {status_label}\n"
            f"Total: R${order['total']:,.2f}\n"
            f"Código de rastreamento: {tracking}\n"
            f"Data do pedido: {order['created_at'][:10]}\n"
            f"Itens:{items_str}"
        )
    except httpx.TimeoutException:
        logger.error(f"Timeout ao consultar pedido {order_identifier}")
        return "O serviço de pedidos está demorando. Tente novamente em instantes."
    except httpx.ConnectError:
        logger.error("Falha de conexão ao consultar pedido")
        return "Serviço de pedidos temporariamente indisponível."
    except httpx.HTTPStatusError:
        return f"Pedido '{order_identifier}' não encontrado. Verifique o número do pedido ou código de rastreamento."


@tool
async def dsa_get_customer_orders(customer_email: str) -> str:
    """Lista pedidos de um cliente pelo e-mail."""
    try:
        client = dsa_get_http_client()
        response = await client.get(f"/api/v1/customers/email/{customer_email}")
        response.raise_for_status()
        customer = response.json()

        response = await client.get(f"/api/v1/orders/customer/{customer['id']}")
        response.raise_for_status()
        data = response.json()
        orders = data.get("items", data) if isinstance(data, dict) else data

        if not orders:
            return f"Nenhum pedido encontrado para {customer_email}."

        results = []
        for o in orders:
            status_label = STATUS_LABELS.get(o["status"], o["status"])
            results.append(
                f"- {o['id']} | {status_label} | R${o['total']:,.2f} | {o['created_at'][:10]}"
            )
        return f"Pedidos de {customer['name']}:\n" + "\n".join(results)
    except httpx.TimeoutException:
        logger.error(f"Timeout ao buscar pedidos do cliente {customer_email}")
        return "O serviço está demorando. Tente novamente."
    except httpx.ConnectError:
        return "Serviço temporariamente indisponível."
    except httpx.HTTPStatusError:
        return f"Cliente com e-mail '{customer_email}' não encontrado."
