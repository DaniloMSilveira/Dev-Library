# Projeto Desenvolvido na Data Science Academy

"""Compilação e execução do grafo LangGraph — Workflow completo de agentes."""

import logging
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from app.agents.escalation_agent import dsa_escalation_agent
from app.agents.faq_agent import dsa_faq_agent
from app.agents.order_agent import dsa_order_agent
from app.agents.product_agent import dsa_product_agent
from app.agents.router_agent import dsa_router_agent
from app.graph.edges import dsa_route_by_intent
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def dsa_build_graph() -> StateGraph:
    """Constrói o grafo de agentes."""
    workflow = StateGraph(AgentState)

    workflow.add_node("router_agent", dsa_router_agent)
    workflow.add_node("product_agent", dsa_product_agent)
    workflow.add_node("order_agent", dsa_order_agent)
    workflow.add_node("faq_agent", dsa_faq_agent)
    workflow.add_node("escalation_agent", dsa_escalation_agent)

    workflow.set_entry_point("router_agent")

    workflow.add_conditional_edges(
        "router_agent",
        dsa_route_by_intent,
        {
            "product_agent": "product_agent",
            "order_agent": "order_agent",
            "faq_agent": "faq_agent",
            "escalation_agent": "escalation_agent",
            "__end__": END,
        },
    )

    workflow.add_edge("product_agent", END)
    workflow.add_edge("order_agent", END)
    workflow.add_edge("faq_agent", END)
    workflow.add_edge("escalation_agent", END)

    return workflow


graph = dsa_build_graph().compile()


async def dsa_run_workflow(message: str, history: list | None = None) -> dict:
    """Executa o workflow de agentes para uma mensagem."""
    messages = []
    if history:
        for msg in history:
            try:
                if msg.get("role") == "user" and msg.get("content"):
                    messages.append(HumanMessage(content=msg["content"]))
            except (AttributeError, TypeError):
                logger.warning(f"Mensagem de histórico inválida ignorada: {msg}")
                continue
    messages.append(HumanMessage(content=message))

    initial_state: AgentState = {
        "messages": messages,
        "intent": "",
        "agent_used": "",
        "sources": [],
        "should_escalate": False,
    }

    result = await graph.ainvoke(initial_state)

    response_message = ""
    if result["messages"]:
        response_message = result["messages"][-1].content

    return {
        "response": response_message,
        "agent_used": result.get("agent_used", "unknown"),
        "sources": result.get("sources", []),
    }
