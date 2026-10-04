# Projeto Desenvolvido na Data Science Academy

"""Testes unitários de cada agente especializado."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from langchain_core.messages import AIMessage, HumanMessage


def _make_state(message: str) -> dict:
    """Cria um AgentState válido para testes."""
    return {
        "messages": [HumanMessage(content=message)],
        "intent": "",
        "agent_used": "",
        "sources": [],
        "should_escalate": False,
    }


@pytest.mark.asyncio
async def test_dsa_router_agent_greeting():
    """Router Agent classifica saudação como greeting."""
    mock_response = MagicMock()
    mock_response.content = "greeting"

    with patch("app.agents.utils.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_cls.return_value = mock_llm

        from app.agents.router_agent import dsa_router_agent

        result = await dsa_router_agent(_make_state("Oi, tudo bem?"))
        assert result["intent"] == "greeting"
        assert result["agent_used"] == "router_agent"


@pytest.mark.asyncio
async def test_dsa_router_agent_product_inquiry():
    """Router Agent classifica consulta de produto."""
    mock_response = MagicMock()
    mock_response.content = "product_inquiry"

    with patch("app.agents.utils.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_cls.return_value = mock_llm

        from app.agents.router_agent import dsa_router_agent

        result = await dsa_router_agent(_make_state("Quero ver notebooks"))
        assert result["intent"] == "product_inquiry"


@pytest.mark.asyncio
async def test_dsa_router_agent_order_status():
    """Router Agent classifica consulta de pedido."""
    mock_response = MagicMock()
    mock_response.content = "order_status"

    with patch("app.agents.utils.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_cls.return_value = mock_llm

        from app.agents.router_agent import dsa_router_agent

        result = await dsa_router_agent(_make_state("Cade meu pedido?"))
        assert result["intent"] == "order_status"


@pytest.mark.asyncio
async def test_dsa_router_agent_faq():
    """Router Agent classifica pergunta FAQ."""
    mock_response = MagicMock()
    mock_response.content = "faq"

    with patch("app.agents.utils.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_cls.return_value = mock_llm

        from app.agents.router_agent import dsa_router_agent

        result = await dsa_router_agent(_make_state("Qual a politica de troca?"))
        assert result["intent"] == "faq"


@pytest.mark.asyncio
async def test_dsa_router_agent_escalation():
    """Router Agent classifica pedido de escalação."""
    mock_response = MagicMock()
    mock_response.content = "escalation"

    with patch("app.agents.utils.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_cls.return_value = mock_llm

        from app.agents.router_agent import dsa_router_agent

        result = await dsa_router_agent(_make_state("Quero falar com atendente"))
        assert result["intent"] == "escalation"


@pytest.mark.asyncio
async def test_dsa_router_agent_unknown_intent_fallback():
    """Router Agent com intent desconhecida faz fallback para faq."""
    mock_response = MagicMock()
    mock_response.content = "alguma_coisa_desconhecida"

    with patch("app.agents.utils.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_cls.return_value = mock_llm

        from app.agents.router_agent import dsa_router_agent

        result = await dsa_router_agent(_make_state("xyz abc"))
        assert result["intent"] == "faq"


@pytest.mark.asyncio
async def test_dsa_router_agent_llm_failure():
    """Router Agent retorna fallback quando LLM falha."""
    with patch("app.agents.utils.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))
        mock_llm_cls.return_value = mock_llm

        from app.agents.router_agent import dsa_router_agent

        result = await dsa_router_agent(_make_state("Qualquer coisa"))
        assert result["intent"] == "faq"
        assert "dificuldades" in result["messages"][0].content.lower()


@pytest.mark.asyncio
async def test_dsa_escalation_agent():
    """Escalation Agent retorna mensagem com número de protocolo."""
    from app.agents.escalation_agent import dsa_escalation_agent

    result = await dsa_escalation_agent(_make_state("Quero falar com atendente"))
    assert result["agent_used"] == "escalation_agent"
    assert result["should_escalate"] is True
    assert "PROT-" in result["messages"][0].content
    assert "segunda a sexta" in result["messages"][0].content
