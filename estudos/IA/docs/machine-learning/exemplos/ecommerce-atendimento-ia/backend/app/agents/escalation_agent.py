# Projeto Desenvolvido na Data Science Academy

"""Escalation Agent — Identifica necessidade de atendimento humano e encaminha."""

import random
import string
from langchain_core.messages import AIMessage
from app.graph.state import AgentState


def dsa_generate_protocol() -> str:
    """Gera um número de protocolo aleatório."""
    num = "".join(random.choices(string.digits, k = 8))
    
    return f"PROT-{num}"


async def dsa_escalation_agent(state: AgentState) -> dict:
    """Encaminha para atendimento humano com número de protocolo."""
    protocol = dsa_generate_protocol()

    message = (
        f"Entendo sua solicitação e agradeço pela paciência.\n\n"
        f"Estou transferindo você para um de nossos atendentes humanos. "
        f"Seu número de protocolo é: **{protocol}**\n\n"
        f"Nossa equipe de atendimento humano está disponível de "
        f"segunda a sexta-feira, das 8h às 18h.\n\n"
        f"Por favor, guarde o número de protocolo para referência. "
        f"Um atendente entrará em contato em breve."
    )

    return {
        "messages": [AIMessage(content = message)],
        "agent_used": "escalation_agent",
        "should_escalate": True,
        "sources": [],
    }
