# Projeto Desenvolvido na Data Science Academy

"""FAQ Agent — Responde perguntas frequentes usando RAG sobre a base de conhecimento."""

import logging
from langchain_core.messages import AIMessage
from app.agents.utils import dsa_create_llm, dsa_get_last_message
from app.graph.state import AgentState
from app.prompts.faq import FAQ_SYSTEM_PROMPT
from app.tools.search_knowledge import dsa_search_knowledge_base

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "Desculpe, estou com dificuldades para acessar a base de conhecimento no momento. "
    "Posso transferir você para um atendente humano se preferir."
)


async def dsa_faq_agent(state: AgentState) -> dict:
    """Responde perguntas usando a base de conhecimento via RAG."""
    last_message = dsa_get_last_message(state)

    try:
        context = await dsa_search_knowledge_base.ainvoke(last_message)
        logger.info(f"FAQ Agent: contexto recuperado ({len(context)} chars)")

        system_prompt = FAQ_SYSTEM_PROMPT.format(context = context)

        llm = dsa_create_llm()

        response = await llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": last_message},
        ])

        answer = response.content
    except Exception:
        logger.exception("Erro no FAQ Agent")
        answer = FALLBACK_RESPONSE
        context = ""

    sources = []
    if "[Fonte" in context:
        for line in context.split("\n"):
            if line.startswith("[Fonte"):
                sources.append({"source": line.strip("[]")})

    return {
        "messages": [AIMessage(content = answer)],
        "agent_used": "faq_agent",
        "sources": sources,
    }


