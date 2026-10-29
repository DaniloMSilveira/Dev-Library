# API de Faturas

API REST que emite e consulta faturas de clientes. Python 3.12, FastAPI e PostgreSQL.

@.claude/memoria.md

## Comandos

- Instalar dependências: `pip install -r requirements-dev.txt`
- Testes: `pytest`
- Lint: `ruff check .`
- Subir localmente: `uvicorn app.main:app --reload`

## Estrutura

- `app/api/`: rotas HTTP, um arquivo por recurso
- `app/servicos/`: regras de negócio
- `app/db/`: acesso ao banco
- `migrations/`: migrações do banco (Alembic)
- `tests/`: espelha a estrutura de `app/`

## Regras

1. Toda mudança de comportamento vem com teste em `tests/`.
2. Regra de negócio fica em `app/servicos/`, nunca na rota.
3. Valores monetários usam `Decimal`, nunca `float`.
4. Não altere uma migração que já existe em `migrations/`; crie uma nova.
5. Antes de dizer que terminou, rode `pytest` e `ruff check .` e informe o resultado.

## Limites

- Não faça commit, push ou deploy sem pedido explícito.
- Não leia nem escreva `.env`. Variáveis novas entram em `.env.example` com valor fictício.
