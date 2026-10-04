<!-- Projeto Desenvolvido na Data Science Academy -->
# E-commerce com Atendimento Automatizado via Agentes de IA

Plataforma de e-commerce (Tech Store Brasil) com atendimento ao cliente automatizado via Agentes de IA especializados, orquestrados pelo LangGraph e com base de conhecimento vetorial (RAG) via ChromaDB.

## Pré-requisitos

- **Docker e Docker Compose** 
- **Chave de API da OpenAI** 

## Como Executar

```bash
# 1. Configurar variáveis de ambiente
# Edite o .env e preencha OPENAI_API_KEY (obrigatório)

# 2. Subir todos os serviços
docker compose up --build -d

# 3. Acompanhar logs
docker compose logs -f

# 4. Acessar a aplicação
# http://localhost:8501
```

## Testes (Opcionais)

```bash
# Testes da API 
docker compose exec api pytest -v

# Testes do backend 
docker compose exec backend pytest -v
```

## Comandos Úteis

```bash
docker compose down              # Parar serviços (mantém dados)
docker compose down -v           # Parar e remover todos os dados
docker compose restart api       # Reiniciar serviço específico
docker compose run --rm seed     # Re-executar seed do banco
docker compose run --rm ingest   # Re-executar ingestão no ChromaDB
docker compose logs backend      # Ver logs de um serviço
```

## Serviços

| Serviço | Porta | Função |
|---|---|---|
| API (FastAPI) | 8000 | API REST e lógica de negócio |
| Backend (LangGraph) | 8001 | Orquestração de 5 Agentes de IA |
| Frontend (Streamlit) | 8501 | Interface web do e-commerce |
| PostgreSQL | 5432 (localhost) | Banco de dados relacional |
| ChromaDB | 8002 (localhost) | Banco vetorial para RAG |

## Agentes de IA

| Pergunta exemplo | Agente acionado |
|---|---|
| "Quais notebooks vocês têm?" | Product Agent |
| "Qual o status do pedido ORD-001?" | Order Agent |
| "Qual a política de troca?" | FAQ Agent (RAG) |
| "Quero falar com um atendente" | Escalation Agent |
| "Olá, bom dia!" | Router Agent |


