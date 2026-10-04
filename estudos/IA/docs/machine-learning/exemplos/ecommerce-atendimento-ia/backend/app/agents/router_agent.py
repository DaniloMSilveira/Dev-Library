# Projeto Desenvolvido na Data Science Academy

"""Router Agent — Classifica a intenção do usuário e roteia para o agente especialista."""

import logging
from langchain_core.messages import AIMessage
from app.agents.utils import dsa_create_llm, dsa_get_last_message
from app.graph.state import AgentState
from app.prompts.router import ROUTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Resposta pré-definida para saudações — economiza tokens e reduz latência
GREETING_RESPONSE = (
    "Olá! Sou o assistente virtual da Tech Store Brasil. Posso ajudar com:\n"
    "- Consultas sobre produtos\n"
    "- Status de pedidos\n"
    "- Políticas de troca/devolução\n"
    "- Recomendações personalizadas\n\n"
    "Como posso ajudar?"
)

VALID_INTENTS = {"product_inquiry", "order_status", "faq", "escalation", "greeting"}

FALLBACK_RESPONSE = (
    "Desculpe, estou com dificuldades técnicas no momento. "
    "Posso transferir você para um atendente humano se preferir."
)


async def dsa_router_agent(state: AgentState) -> dict:
    """Classifica a intenção do usuário e define o próximo agente."""
    last_message = dsa_get_last_message(state)

    try:
        llm = dsa_create_llm()

        response = await llm.ainvoke([
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": last_message},
        ])

        intent = response.content.strip().lower().replace('"', "").replace("'", "")
        logger.info(f"Intent classificada: '{intent}' para mensagem: '{last_message[:50]}...'")

        # Validar intent contra whitelist
        if intent not in VALID_INTENTS:
            logger.warning(f"Intent desconhecida '{intent}', usando fallback 'faq'")
            intent = "faq"

    except Exception:
        logger.exception("Erro ao classificar intent")
        return {
            "intent": "faq",
            "agent_used": "router_agent",
            "messages": [AIMessage(content = FALLBACK_RESPONSE)],
            "sources": [],
            "should_escalate": False,
        }

    if intent == "greeting":
        return {
            "intent": "greeting",
            "agent_used": "router_agent",
            "messages": [AIMessage(content = GREETING_RESPONSE)],
            "sources": [],
            "should_escalate": False,
        }

    return {
        "intent": intent,
        "agent_used": "",
        "sources": [],
        "should_escalate": False,
    }
