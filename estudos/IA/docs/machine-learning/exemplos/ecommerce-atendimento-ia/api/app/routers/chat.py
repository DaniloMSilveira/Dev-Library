# Projeto Desenvolvido na Data Science Academy

"""Router de Chat — Endpoint de comunicação com os agentes de IA."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import dsa_get_db
from app.schemas.chat_schema import ChatRequest, ChatResponse, ConversationResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def dsa_send_message(chat_request: ChatRequest, db: AsyncSession = Depends(dsa_get_db)) -> ChatResponse:
    """Envia mensagem e recebe resposta do agente de IA."""
    service = ChatService(db)
    return await service.dsa_process_message(chat_request)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def dsa_get_conversation(conversation_id: str, db: AsyncSession = Depends(dsa_get_db)) -> ConversationResponse:
    """Retorna histórico de uma conversa."""
    service = ChatService(db)
    conversation = await service.dsa_get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return ConversationResponse(**conversation)
