#!/usr/bin/env python3
# Projeto Desenvolvido na Data Science Academy
"""Ingestão da base de conhecimento no ChromaDB.

Carrega FAQs, políticas e produtos como embeddings vetoriais no ChromaDB
para busca semântica pelos agentes de IA.
"""

import logging
import os
import sys
from pathlib import Path

# Silencia warning de CPU do ONNX Runtime (usado internamente pelo ChromaDB)
os.environ["ORT_LOG_LEVEL"] = "ERROR"

# Adiciona backend/ ao sys.path para imports de app.rag.* e app.config
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Silencia erro de telemetria do ChromaDB (bug no posthog.capture do chromadb 0.5.x)
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)


def dsa_main():
    """Executa a ingestão completa da base de conhecimento."""
    from app.rag.ingestion import DocumentIngestionPipeline
    from app.rag.vectorstore import VectorStoreManager
    from app.config import settings

    logger.info("Iniciando ingestão da base de conhecimento...")

    vs_manager = VectorStoreManager(settings.CHROMADB_HOST, settings.CHROMADB_PORT)
    pipeline = DocumentIngestionPipeline(vs_manager)
    results = pipeline.run_full_ingestion()

    logger.info("Ingestão concluída!")
    logger.info(f"  FAQs: {results['faq']} documentos")
    logger.info(f"  Políticas: {results['policies']} chunks")
    logger.info(f"  Produtos: {results['products']} documentos")
    logger.info(f"  Total: {results['total']} documentos no ChromaDB")


if __name__ == "__main__":
    dsa_main()
