# Projeto Desenvolvido na Data Science Academy

"""Interface com ChromaDB — Gerencia collections e operações vetoriais."""

import logging
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

# Silencia erro de telemetria do ChromaDB (bug no posthog.capture do chromadb 0.5.x)
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Gerencia a conexão e operações com o ChromaDB (lazy initialization)."""

    def __init__(self, host: str | None = None, port: int | None = None):
        self.host = host or settings.CHROMADB_HOST
        self.port = port or settings.CHROMADB_PORT
        self._client: chromadb.HttpClient | None = None
        self._collection = None

    @property
    def client(self) -> chromadb.HttpClient:
        """Retorna o cliente ChromaDB (lazy initialization)."""
        if self._client is None:
            self._client = chromadb.HttpClient(host = self.host, port = self.port)
        return self._client

    def get_embedding_function(self):
        """Retorna a função de embedding OpenAI."""
        return embedding_functions.OpenAIEmbeddingFunction(api_key = settings.OPENAI_API_KEY, model_name = settings.EMBEDDING_MODEL)

    def get_or_create_collection(self):
        """Retorna collection existente ou cria nova."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name = "knowledge_base",
                embedding_function = self.get_embedding_function(),
                metadata = {"hnsw:space": "cosine"},
            )
        return self._collection

    def get_collection_stats(self) -> dict:
        """Retorna total de documentos e contagem por categoria."""
        collection = self.get_or_create_collection()
        total = collection.count()

        return {
            "total_documents": total,
            "collection_name": "knowledge_base",
        }

    def health_check(self) -> bool:
        """Verifica se o ChromaDB está acessível."""
        try:
            self.client.heartbeat()
            return True
        except Exception:
            logger.exception("ChromaDB health check falhou")
            return False


vectorstore_manager = VectorStoreManager()
