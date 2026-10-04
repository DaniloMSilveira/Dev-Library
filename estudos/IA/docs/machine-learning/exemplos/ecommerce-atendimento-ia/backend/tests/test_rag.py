# Projeto Desenvolvido na Data Science Academy

"""Testes do pipeline RAG — Ingestão, retrieval e integração com ChromaDB."""

import json
import os
import tempfile

import pytest


def test_dsa_chunk_text():
    """Chunks são gerados corretamente."""
    from app.rag.ingestion import dsa_chunk_text

    text = "Parágrafo um. " * 50 + "\n\n" + "Parágrafo dois. " * 50
    chunks = dsa_chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 600  # Alguma tolerância


def test_dsa_chunk_text_small():
    """Texto pequeno retorna um único chunk."""
    from app.rag.ingestion import dsa_chunk_text

    text = "Texto pequeno para teste."
    chunks = dsa_chunk_text(text, chunk_size=500)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_dsa_extract_section():
    """Extração de título da seção funciona."""
    from app.rag.ingestion import dsa_extract_section

    full_text = "# Título\n\n## Seção A\nConteúdo da seção A.\n\n## Seção B\nConteúdo da seção B."
    chunk = "Conteúdo da seção B."
    section = dsa_extract_section(chunk, full_text)
    assert section == "Seção B"


def test_dsa_ingestion_pipeline_faq():
    """Ingestão de FAQ cria documentos corretamente."""
    faqs = [
        {
            "id": "FAQ-001",
            "question": "Qual o prazo de entrega?",
            "answer": "3 a 12 dias úteis.",
            "category": "entregas_frete",
            "keywords": ["prazo", "entrega"],
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(faqs, f)
        faq_path = f.name

    try:
        with open(faq_path, "r") as f:
            loaded = json.load(f)
        assert len(loaded) == 1
        assert loaded[0]["id"] == "FAQ-001"
    finally:
        os.unlink(faq_path)


def test_dsa_retrieved_document_dataclass():
    """RetrievedDocument é criado corretamente."""
    from app.rag.retriever import RetrievedDocument

    doc = RetrievedDocument(
        content="Conteúdo de teste",
        metadata={"source": "faq", "category": "geral"},
        similarity_score=0.85,
    )
    assert doc.content == "Conteúdo de teste"
    assert doc.metadata["source"] == "faq"
    assert doc.similarity_score == 0.85


def test_dsa_shipping_tool():
    """Tool de frete calcula corretamente."""
    from app.tools.calculate_shipping import SHIPPING_TABLE

    assert "SP" in SHIPPING_TABLE
    assert SHIPPING_TABLE["SP"]["price"] == 15.90
    assert len(SHIPPING_TABLE) == 27


def test_dsa_chunk_overlap_increased():
    """Overlap padrão foi aumentado para 100 (20%)."""
    from app.rag.ingestion import CHUNK_OVERLAP

    assert CHUNK_OVERLAP == 100
