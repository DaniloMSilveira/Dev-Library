# Projeto Desenvolvido na Data Science Academy

"""Ingestão de documentos — Processa FAQ, políticas e produtos para o ChromaDB."""

import json
import logging
from pathlib import Path
from app.rag.vectorstore import VectorStoreManager

logger = logging.getLogger(__name__)

DATA_DIR = Path("/app/data") if Path("/app/data").exists() else Path(__file__).parent.parent.parent.parent / "data"

# Tamanho de cada chunk
CHUNK_SIZE = 500

# Overlap de 20% evita perda de informação nas fronteiras entre chunks
CHUNK_OVERLAP = 100


def dsa_chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Segmenta texto em chunks usando separadores hierárquicos."""
    separators = ["\n\n", "\n", ". ", " "]
    chunks = []
    segments = [text]

    for sep in separators:
        new_segments = []
        for segment in segments:
            if len(segment) <= chunk_size:
                new_segments.append(segment)
            else:
                parts = segment.split(sep)
                current = ""
                for part in parts:
                    candidate = current + sep + part if current else part
                    if len(candidate) <= chunk_size:
                        current = candidate
                    else:
                        if current:
                            new_segments.append(current)
                        current = part
                if current:
                    new_segments.append(current)
        segments = new_segments

    return [s.strip() for s in segments if s.strip()]


def dsa_extract_section(chunk: str, full_text: str) -> str:
    """Extrai o título da seção mais próxima ao chunk."""
    pos = full_text.find(chunk[:50])
    if pos == -1:
        return "geral"
    preceding = full_text[:pos]
    for line in reversed(preceding.split("\n")):
        if line.startswith("## "):
            return line.replace("## ", "").strip()
        if line.startswith("# "):
            return line.replace("# ", "").strip()
    return "geral"


class DocumentIngestionPipeline:
    """Pipeline de ingestão de documentos no ChromaDB."""

    def __init__(self, vectorstore: VectorStoreManager):
        self.vectorstore = vectorstore
        self.collection = vectorstore.get_or_create_collection()

    def ingest_faq(self, faq_path: str | None = None) -> int:
        """Ingere FAQ no ChromaDB."""
        path = Path(faq_path) if faq_path else DATA_DIR / "faq.json"
        with open(path, "r", encoding="utf-8") as f:
            faqs = json.load(f)

        documents, metadatas, ids = [], [], []
        for faq in faqs:
            doc = f"Pergunta: {faq['question']}\nResposta: {faq['answer']}"
            documents.append(doc)
            metadatas.append({
                "source": "faq",
                "category": faq["category"],
                "faq_id": faq["id"],
                "type": "faq",
            })
            ids.append(f"faq-{faq['id']}")

        self.collection.upsert(documents = documents, metadatas = metadatas, ids = ids)
        logger.info(f"FAQ: {len(documents)} documentos ingeridos")
        return len(documents)

    def ingest_policies(self, policies_path: str | None = None) -> int:
        """Ingere políticas segmentadas no ChromaDB."""
        path = Path(policies_path) if policies_path else DATA_DIR / "policies.md"
        with open(path, "r", encoding="utf-8") as f:
            full_text = f.read()

        chunks = dsa_chunk_text(full_text)
        documents, metadatas, ids = [], [], []

        for i, chunk in enumerate(chunks):
            section = dsa_extract_section(chunk, full_text)
            documents.append(chunk)
            metadatas.append({
                "source": "policies",
                "section": section,
                "chunk_index": i,
                "type": "policy",
            })
            ids.append(f"policy-chunk-{i:03d}")

        self.collection.upsert(documents = documents, metadatas = metadatas, ids = ids)
        logger.info(f"Políticas: {len(documents)} chunks ingeridos")
        return len(documents)

    def ingest_product_descriptions(self, products_path: str | None = None) -> int:
        """Ingere descrições de produtos no ChromaDB."""
        path = Path(products_path) if products_path else DATA_DIR / "products.json"
        with open(path, "r", encoding="utf-8") as f:
            products = json.load(f)

        documents, metadatas, ids = [], [], []

        for p in products:
            specs_str = ", ".join(f"{k}: {v}" for k, v in p["specs"].items())
            doc = (
                f"Produto: {p['name']}\n"
                f"Categoria: {p['category']}\n"
                f"Marca: {p['brand']}\n"
                f"Descrição: {p['description']}\n"
                f"Preço: R${p['price']:,.2f}\n"
                f"Especificações: {specs_str}"
            )
            documents.append(doc)
            metadatas.append({
                "source": "products",
                "category": p["category"],
                "product_id": p["id"],
                "type": "product",
            })
            ids.append(f"product-{p['id']}")

        self.collection.upsert(documents = documents, metadatas = metadatas, ids = ids)
        logger.info(f"Produtos: {len(documents)} documentos ingeridos")
        return len(documents)

    def run_full_ingestion(self) -> dict:
        """Executa todas as ingestões e retorna resumo."""
        faq_count = self.ingest_faq()
        policies_count = self.ingest_policies()
        products_count = self.ingest_product_descriptions()

        total = faq_count + policies_count + products_count
        return {
            "faq": faq_count,
            "policies": policies_count,
            "products": products_count,
            "total": total,
        }
