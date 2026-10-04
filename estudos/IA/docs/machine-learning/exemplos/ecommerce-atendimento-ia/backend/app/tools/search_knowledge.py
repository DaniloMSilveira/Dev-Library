# Projeto Desenvolvido na Data Science Academy

"""Tool search_knowledge — Busca na base de conhecimento via ChromaDB (RAG)."""

import logging
from langchain_core.tools import tool
from app.rag.retriever import KnowledgeBaseRetriever
from app.rag.vectorstore import vectorstore_manager

logger = logging.getLogger(__name__)


@tool
async def dsa_search_knowledge_base(query: str) -> str:
    """Busca na base de conhecimento da loja (FAQ, políticas, termos). Use para perguntas sobre regras, políticas e procedimentos."""
    try:
        retriever = KnowledgeBaseRetriever(vectorstore_manager)
        context = await retriever.retrieve_with_context(query, top_k = 5)
        return context
    except Exception as e:
        logger.error(f"Erro ao buscar no ChromaDB: {e}")
        # Fallback: busca por keywords no JSON quando ChromaDB está indisponível
        return await dsa_fallback_search(query)


async def dsa_fallback_search(query: str) -> str:
    """Busca fallback no FAQ JSON quando ChromaDB não está disponível."""
    import json
    from pathlib import Path

    faq_path = Path(__file__).parent.parent.parent.parent / "data" / "faq.json"
    try:
        with open(faq_path, "r", encoding = "utf-8") as f:
            faqs = json.load(f)
    except FileNotFoundError:
        return "Base de conhecimento indisponível no momento."

    query_lower = query.lower()
    scored = []
    for faq in faqs:
        # Keywords valem 2 pontos (match direto), palavras na pergunta valem 1
        score = sum(2 for kw in faq.get("keywords", []) if kw.lower() in query_lower)
        if any(word in faq["question"].lower() for word in query_lower.split()):
            score += 1
        if score > 0:
            scored.append((score, faq))

    scored.sort(key = lambda x: x[0], reverse = True)
    if not scored:
        return "Nenhuma informação relevante encontrada na base de conhecimento."

    # Formato compatível com o retriever (labels de fonte)
    parts = []
    for i, (_, faq) in enumerate(scored[:3], 1):
        parts.append(
            f"[Fonte {i} - faq]\nPergunta: {faq['question']}\nResposta: {faq['answer']}"
        )
    return "\n\n---\n\n".join(parts)



    
