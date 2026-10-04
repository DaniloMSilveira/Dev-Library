# Projeto Desenvolvido na Data Science Academy

"""Schemas Pydantic para Chat."""

from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema de request para chat."""

    message: str = Field(min_length=1, max_length=5000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    """Schema de response do chat."""

    response: str
    conversation_id: str
    agent_used: str
    sources: list[dict] | None = None


class ConversationResponse(BaseModel):
    """Schema de resposta para histórico de conversa."""

    id: str
    messages: list[dict]
    created_at: datetime
