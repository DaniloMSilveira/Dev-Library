# Projeto Desenvolvido na Data Science Academy

"""Lógica de retrieval — Busca semântica na base de conhecimento."""

import logging
from dataclasses import dataclass
from app.config import settings
from app.rag.vectorstore import VectorStoreManager

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
    """Documento recuperado da base de conhecimento."""

    content: str
    metadata: dict
    similarity_score: float


class KnowledgeBaseRetriever:
    """Recupera documentos relevantes da base de conhecimento."""

    def __init__(self, vectorstore: VectorStoreManager):
        self.collection = vectorstore.get_or_create_collection()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_category: str | None = None,
        min_similarity: float | None = None,
    ) -> list[RetrievedDocument]:
        """Busca documentos similares à query."""
        if min_similarity is None:
            min_similarity = settings.MIN_SIMILARITY

        where_filter = None
        if filter_category:
            where_filter = {"source": filter_category}

        results = self.collection.query(
            query_texts = [query],
            n_results = top_k,
            where = where_filter,
            include = ["documents", "metadatas", "distances"],
        )

        documents = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i] if results["distances"] else 1.0
                # ChromaDB retorna distância cosseno (0=idêntico); convertemos para similaridade
                similarity = 1.0 - distance

                if similarity >= min_similarity:
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    documents.append(RetrievedDocument(
                        content = doc,
                        metadata = metadata,
                        similarity_score = similarity,
                    ))

        documents.sort(key = lambda d: d.similarity_score, reverse = True)
        return documents

    async def retrieve_with_context(self, query: str, top_k: int = 5) -> str:
        """Recupera documentos e formata como contexto para o LLM."""
        docs = await self.retrieve(query, top_k)
        if not docs:
            return "Nenhuma informação relevante encontrada na base de conhecimento."

        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            context_parts.append(
                f"[Fonte {i} - {source}]\n{doc.content}"
            )
        return "\n\n---\n\n".join(context_parts)



