# Projeto Desenvolvido na Data Science Academy

"""Lógica de roteamento entre nós — Conditional edges baseados em intenção."""

import logging
from app.graph.state import AgentState

logger = logging.getLogger(__name__)

INTENT_TO_NODE = {
    "product_inquiry": "product_agent",
    "order_status": "order_agent",
    "faq": "faq_agent",
    "escalation": "escalation_agent",
    "greeting": "__end__",
}


def dsa_route_by_intent(state: AgentState) -> str:
    """Roteia para o próximo nó baseado na intenção classificada."""
    intent = state.get("intent", "")
    
    # Fallback para faq_agent: lida com intenções não reconhecidas via RAG
    next_node = INTENT_TO_NODE.get(intent, "faq_agent")
    logger.info(f"Roteando: intent='{intent}' → node='{next_node}'")
    
    return next_node
