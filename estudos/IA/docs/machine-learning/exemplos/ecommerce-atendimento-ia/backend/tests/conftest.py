# Projeto Desenvolvido na Data Science Academy

"""Fixtures de teste — Mocks para API, ChromaDB e OpenAI."""

import os

import pytest

# Definir variáveis de ambiente para testes antes de importar módulos
os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing-only-not-real"
os.environ["API_URL"] = "http://localhost:8000"
os.environ["CHROMADB_HOST"] = "localhost"
os.environ["CHROMADB_PORT"] = "8000"


@pytest.fixture
def dsa_mock_llm_response():
    """Retorna uma resposta mock do LLM."""
    class MockResponse:
        def __init__(self, content, tool_calls=None):
            self.content = content
            self.tool_calls = tool_calls or []
    return MockResponse


@pytest.fixture
def dsa_sample_faq_data():
    """Retorna dados mock de FAQ."""
    return [
        {
            "id": "FAQ-001",
            "question": "Qual o prazo de entrega?",
            "answer": "O prazo de entrega varia de 3 a 12 dias úteis dependendo da região.",
            "category": "entregas_frete",
            "keywords": ["prazo", "entrega", "dias", "envio"],
        },
        {
            "id": "FAQ-002",
            "question": "Qual a política de troca?",
            "answer": "Você tem até 30 dias para solicitar troca ou devolução.",
            "category": "trocas_devolucoes",
            "keywords": ["troca", "devolução", "30 dias"],
        },
    ]
