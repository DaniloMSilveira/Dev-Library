# Projeto Desenvolvido na Data Science Academy

"""Testes do workflow completo do grafo LangGraph."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from langchain_core.messages import AIMessage, HumanMessage


@pytest.mark.asyncio
async def test_dsa_graph_compiles():
    """O grafo LangGraph compila sem erros."""
    from app.graph.workflow import dsa_build_graph

    workflow = dsa_build_graph()
    graph = workflow.compile()
    assert graph is not None


def test_dsa_route_by_intent_product():
    """Roteamento product_inquiry vai para product_agent."""
    from app.graph.edges import dsa_route_by_intent

    state = {"intent": "product_inquiry"}
    assert dsa_route_by_intent(state) == "product_agent"


def test_dsa_route_by_intent_order():
    """Roteamento order_status vai para order_agent."""
    from app.graph.edges import dsa_route_by_intent

    state = {"intent": "order_status"}
    assert dsa_route_by_intent(state) == "order_agent"


def test_dsa_route_by_intent_faq():
    """Roteamento faq vai para faq_agent."""
    from app.graph.edges import dsa_route_by_intent

    state = {"intent": "faq"}
    assert dsa_route_by_intent(state) == "faq_agent"


def test_dsa_route_by_intent_escalation():
    """Roteamento escalation vai para escalation_agent."""
    from app.graph.edges import dsa_route_by_intent

    state = {"intent": "escalation"}
    assert dsa_route_by_intent(state) == "escalation_agent"


def test_dsa_route_by_intent_greeting():
    """Roteamento greeting vai para __end__."""
    from app.graph.edges import dsa_route_by_intent

    state = {"intent": "greeting"}
    assert dsa_route_by_intent(state) == "__end__"


def test_dsa_route_by_intent_unknown():
    """Roteamento desconhecido vai para faq_agent (fallback)."""
    from app.graph.edges import dsa_route_by_intent

    state = {"intent": "unknown"}
    assert dsa_route_by_intent(state) == "faq_agent"
