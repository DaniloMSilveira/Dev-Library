# Projeto Desenvolvido na Data Science Academy

"""Order Agent — Consulta status de pedidos, rastreamento e histórico de compras."""

from app.agents.utils import dsa_create_tool_agent
from app.prompts.order import ORDER_SYSTEM_PROMPT
from app.tools.calculate_shipping import dsa_calculate_shipping
from app.tools.check_order import dsa_check_order_status, dsa_get_customer_orders

dsa_order_agent = dsa_create_tool_agent(
    tools = [dsa_check_order_status, dsa_get_customer_orders, dsa_calculate_shipping],
    system_prompt = ORDER_SYSTEM_PROMPT,
    agent_name = "order_agent",
    context_label = "Informações do pedido",
)
