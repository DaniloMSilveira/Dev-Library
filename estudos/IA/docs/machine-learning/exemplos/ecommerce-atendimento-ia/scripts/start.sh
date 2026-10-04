#!/bin/bash
# Projeto Desenvolvido na Data Science Academy
# Script de inicialização completa da aplicação e-commerce.
# Orquestra a subida dos serviços Docker na ordem correta de dependências.

# "set -e" faz o script parar imediatamente se QUALQUER comando falhar.
# Sem isso, o script continuaria mesmo após erros, podendo deixar
# o sistema em estado inconsistente (ex: frontend sem api).
set -e

echo "Iniciando E-commerce AI Assistant..."

# Etapa 1: Build de todas as imagens Docker (compila Dockerfiles).
# Só reconstrói camadas que mudaram (Docker layer caching).
docker compose build

# Etapa 2: Subir infraestrutura primeiro (banco de dados + vector store).
# A flag -d (detached) roda os containers em segundo plano.
# Os healthchecks definidos no docker-compose.yml garantem que PostgreSQL
# e ChromaDB estão prontos antes de outros serviços tentarem conectar.
docker compose up -d db chromadb

# Etapa 3: Subir a API (depende do banco estar healthy via depends_on).
# O Docker Compose aguarda o healthcheck do "db" retornar sucesso antes de iniciar.
docker compose up -d api

# Etapa 4: Executar seed e ingestão (serviços de execução única).
# SEM a flag -d: o script AGUARDA a conclusão antes de continuar.
# Isso garante que os dados estejam carregados antes do frontend subir.
# - seed: carrega dados iniciais no PostgreSQL (produtos, clientes, pedidos)
# - ingest: indexa a base de conhecimento no ChromaDB (embeddings para RAG)
docker compose up seed ingest
echo "Dados carregados!"

# Etapa 5: Subir backend (agentes de IA) e frontend (dependem da API healthy).
# Com -d para rodar em background (serviços de longa duração).
docker compose up -d backend frontend
echo ""
echo "Aplicação disponível em:"
echo "   Frontend:  http://localhost:8501"
echo "   API:       http://localhost:8000/docs"
echo "   Backend:   http://localhost:8001/docs"
echo "   ChromaDB:  http://localhost:8002"
