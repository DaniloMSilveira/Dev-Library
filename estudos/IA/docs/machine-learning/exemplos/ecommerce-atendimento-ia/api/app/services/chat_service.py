# Projeto Desenvolvido na Data Science Academy

"""Serviço de Chat — Camada de aplicação responsável por orquestrar
a comunicação entre o usuário, a persistência de conversas e o backend de IA.

Este serviço atua como um "facade" entre:
- Banco de dados (histórico de conversa)
- Backend de Agentes de IA (respostas inteligentes)
- Contratos de entrada/saída (schemas)

Diferente do OrderService, aqui optamos por commit explícito ao final
para garantir persistência da interação completa (user + assistant).
"""

import logging
from datetime import datetime
from uuid import uuid4
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.conversation import Conversation
from app.schemas.chat_schema import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class ChatService:
    """Serviço responsável pelo fluxo de chat com Agentes de IA.

    Responsabilidades principais:
    - Gerenciar ciclo de vida de conversas
    - Persistir histórico (chat memory)
    - Orquestrar chamada ao backend de IA
    - Tratar falhas externas de forma resiliente

    Observação:
    O histórico é armazenado como JSON (lista de mensagens),
    o que simplifica leitura, mas exige cuidado com mutabilidade.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_or_create_conversation(self, conversation_id: str | None, customer_id: str | None = None) -> Conversation:
        """Recupera uma conversa existente ou cria uma nova.

        Estratégia:
        - Se conversation_id for fornecido, tenta recuperar
        - Caso não exista, cria nova conversa
        - Garante que sempre retornamos uma instância válida

        """
        if conversation_id:
            result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
            conversation = result.scalar_one_or_none()

            if conversation:
                return conversation

        # Criação de nova conversa
        conversation = Conversation(
            id=str(uuid4()),
            customer_id=customer_id,
            messages=[]  # histórico inicial vazio
        )

        self.db.add(conversation)

        # flush para gerar persistência sem finalizar transação
        await self.db.flush()

        # refresh garante sincronização com o estado do banco
        await self.db.refresh(conversation)

        return conversation

    async def _add_message(self, conversation_id: str, role: str, content: str) -> Conversation | None:
        """Adiciona uma mensagem ao histórico da conversa.

        Pontos importantes:
        - O campo messages é JSON 
        - SQLAlchemy NÃO detecta mutações internas em listas/dicts automaticamente
        - Por isso, criamos uma nova lista (copy-on-write)

        Sem isso, a alteração pode não ser persistida.
        """
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = result.scalar_one_or_none()

        if not conversation:
            return None

        # Copy-on-write para garantir que o ORM detecte mudança
        messages = list(conversation.messages) if conversation.messages else []

        messages.append({
            "role": role,  # "user" ou "assistant"
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Substituição completa do JSON (importante para tracking de mudança)
        conversation.messages = messages

        # Atualiza timestamp de última modificação
        conversation.updated_at = datetime.utcnow()

        # flush para persistir sem commit
        await self.db.flush()

        # refresh garante consistência com o banco
        await self.db.refresh(conversation)

        return conversation

    async def dsa_process_message(self, chat_request: ChatRequest) -> ChatResponse:
        """Fluxo principal de processamento de mensagem.

        Pipeline:
        1. Recupera ou cria conversa
        2. Persiste mensagem do usuário
        3. Monta histórico
        4. Chama backend de IA
        5. Trata erros de integração
        6. Persiste resposta do agente
        7. Commit da transação

        Este método é o ponto central de integração com Agentes de IA.
        """

        # Garante existência da conversa
        conversation = await self._get_or_create_conversation(chat_request.conversation_id)

        # Persistência da mensagem do usuário
        await self._add_message(
            conversation.id,
            "user",
            chat_request.message
        )

        # Construção do histórico no formato esperado pelo backend
        history = []
        if conversation.messages:
            for msg in conversation.messages:
                history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        try:
            # Cliente HTTP assíncrono
            # timeout protege contra chamadas longas ou travadas
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.BACKEND_URL}/chat",
                    json={
                        "message": chat_request.message,
                        "history": history,
                    },
                )

                # Levanta exceção para status != 2xx
                response.raise_for_status()

                agent_response = response.json()

        except httpx.TimeoutException:
            # Timeout: backend demorou além do limite
            logger.error("Timeout ao chamar serviço de backend")

            agent_response = {
                "response": "Desculpe, o tempo de resposta excedeu o limite. "
                "Por favor, tente novamente em alguns instantes.",
                "agent_used": "error_handler",
                "sources": [],
            }

        except httpx.ConnectError:
            # Falha de rede ou serviço indisponível
            logger.error("Falha de conexão com serviço de backend")

            agent_response = {
                "response": "Desculpe, o servico de atendimento esta temporariamente indisponivel. "
                "Por favor, tente novamente em alguns instantes.",
                "agent_used": "error_handler",
                "sources": [],
            }

        except httpx.HTTPError as e:
            # Erros HTTP genéricos (4xx, 5xx)
            logger.error(f"Erro ao chamar serviço de backend: {e}")

            agent_response = {
                "response": "Desculpe, estou com dificuldades tecnicas no momento. "
                "Por favor, tente novamente em alguns instantes.",
                "agent_used": "error_handler",
                "sources": [],
            }

        # Persistência da resposta do agente
        await self._add_message(
            conversation.id,
            "assistant",
            agent_response["response"]
        )

        # Commit final:
        # Garante atomicidade da interação completa (user + assistant)
        await self.db.commit()

        return ChatResponse(
            response=agent_response["response"],
            conversation_id=conversation.id,
            agent_used=agent_response.get("agent_used", "unknown"),
            sources=agent_response.get("sources", []),
        )

    async def dsa_get_conversation(self, conversation_id: str) -> dict | None:
        """Recupera histórico completo de uma conversa.

        Retorna estrutura serializável para API.

        Observação:
        Não há paginação aqui. Em produção, conversas longas
        devem ser paginadas ou truncadas para evitar payloads grandes.
        """
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = result.scalar_one_or_none()

        if not conversation:
            return None

        return {
            "id": conversation.id,
            "messages": conversation.messages,
            "created_at": conversation.created_at.isoformat(),
        }


        