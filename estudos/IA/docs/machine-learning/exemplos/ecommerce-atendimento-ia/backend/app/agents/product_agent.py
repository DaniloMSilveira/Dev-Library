# Projeto Desenvolvido na Data Science Academy

"""Product Agent — Responde consultas sobre produtos, especificações e recomendações."""

from app.agents.utils import dsa_create_tool_agent
from app.prompts.product import PRODUCT_SYSTEM_PROMPT
from app.tools.search_products import dsa_get_product_details, dsa_list_by_category, dsa_search_products

dsa_product_agent = dsa_create_tool_agent(
    tools = [dsa_search_products, dsa_get_product_details, dsa_list_by_category],
    system_prompt = PRODUCT_SYSTEM_PROMPT,
    agent_name = "product_agent",
    context_label = "Informações do catálogo",
)
