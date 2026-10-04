# Projeto Desenvolvido na Data Science Academy

"""Estado compartilhado do grafo LangGraph."""

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Estado compartilhado entre todos os nós do grafo."""

    messages: Annotated[list[BaseMessage], add_messages]
    intent: str
    agent_used: str
    sources: list[dict]
    should_escalate: bool
