# Projeto Desenvolvido na Data Science Academy

"""Entrypoint do backend — FastAPI com endpoints de chat, RAG e health."""

import logging
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from app.config import settings
from app.graph.workflow import dsa_run_workflow

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title = "Tech Store Brasil — Agentes de IA",
    description = "Serviço de agentes de IA para atendimento automatizado via LangGraph",
    version = "1.0.0",
)


class ChatRequest(BaseModel):
    """Request para o endpoint de chat."""

    message: str = Field(min_length = 1, max_length = 5000)
    history: list[dict] | None = None


class ChatResponse(BaseModel):
    """Response do endpoint de chat."""

    response: str
    agent_used: str
    sources: list[dict] = []


@app.post("/chat", response_model = ChatResponse)
async def dsa_chat(request: ChatRequest) -> ChatResponse:
    """Recebe mensagem, executa workflow de agentes e retorna resposta."""
    logger.info(f"Mensagem recebida: '{request.message[:80]}...'")
    result = await dsa_run_workflow(request.message, request.history)
    logger.info(f"Agente usado: {result['agent_used']}")
    return ChatResponse(**result)


@app.get("/health")
async def dsa_health() -> dict:
    """Health check do backend."""
    return {
        "status": "healthy",
        "service": "backend",
        "model": settings.MODEL_NAME,
    }


@app.get("/rag/status")
async def dsa_rag_status() -> dict:
    """Verifica status do ChromaDB e da base de conhecimento."""
    try:
        # Import local para evitar falha na inicialização se o ChromaDB estiver offline
        from app.rag.vectorstore import vectorstore_manager

        stats = vectorstore_manager.get_collection_stats()
        return {
            "chromadb_connected": True,
            "total_documents": stats["total_documents"],
            "collections": [stats["collection_name"]],
        }
    except Exception as e:
        logger.error(f"ChromaDB status check failed: {e}")
        return {
            "chromadb_connected": False,
            "error": str(e),
        }


@app.get("/rag/search")
async def dsa_rag_search(q: str = Query(..., description = "Query de busca")) -> dict:
    """Busca na base de conhecimento (endpoint de debug)."""
    try:
        from app.rag.retriever import KnowledgeBaseRetriever
        from app.rag.vectorstore import vectorstore_manager

        retriever = KnowledgeBaseRetriever(vectorstore_manager)
        docs = await retriever.retrieve(q, top_k = 3)
        return {
            "query": q,
            "results": [
                {
                    "content": doc.content[:200],
                    "metadata": doc.metadata,
                    "similarity_score": round(doc.similarity_score, 4),
                }
                for doc in docs
            ],
        }
    except Exception as e:
        return {"query": q, "error": str(e)}


@app.get("/")
async def dsa_root() -> dict:
    """Informações básicas do serviço."""
    return {
        "name": "Tech Store Brasil — Agentes de IA",
        "version": "1.0.0",
        "docs": "/docs",
    }
