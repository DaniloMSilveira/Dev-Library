# API de Faturas

API REST que emite e consulta faturas de clientes. Python 3.12, FastAPI e PostgreSQL.

@.claude/memoria/decisoes.md
@.claude/memoria/incidentes.md

## Início de sessão

Antes de editar qualquer arquivo:

1. Leia `progresso.md` para saber onde a última sessão parou.
2. Leia `feature_list.json` e trabalhe só na feature com `status: em_andamento`. Se não houver, pegue a pendente com o menor número em `prioridade` (1 é a mais urgente) e marque-a como `em_andamento`.
3. Rode `./init.sh`. Se ele falhar, conserte o ambiente antes de começar a feature.

## Comandos

- Preparar e verificar o ambiente: `./init.sh`
- Testes: `pytest`
- Lint: `ruff check .` (formatação com `ruff format .` pede confirmação)
- Subir localmente: `uvicorn app.main:app --reload`
- Nova migração: `alembic revision -m "descricao"`

## Estrutura

- `app/api/`: rotas HTTP, um arquivo por recurso
- `app/servicos/`: regras de negócio
- `app/db/`: acesso ao banco
- `migrations/`: migrações do banco (Alembic)
- `tests/`: espelha a estrutura de `app/`

As regras específicas de cada pasta estão em `.claude/rules/` e entram no contexto quando você trabalha nela.

## Regras

1. Uma feature por vez. Não comece outra antes de concluir ou registrar o bloqueio da atual.
2. Toda mudança de comportamento vem com teste em `tests/`.
3. Regra de negócio fica em `app/servicos/`, nunca na rota.
4. Valores monetários usam `Decimal`, nunca `float`.

## Pronto significa

Uma feature só está concluída quando:

- o comportamento descrito em `feature_list.json` foi implementado;
- `pytest` e `ruff check .` passaram nesta sessão;
- os passos de `verificacao` da feature foram executados e o resultado foi anotado em `evidencia`;
- o subagente `revisor` não deixou achado grave em aberto;
- `progresso.md` ganhou uma entrada com o que foi feito e o próximo passo.

## Limites

- Não faça commit, push ou deploy sem pedido explícito.
- Não leia nem escreva `.env`. Variáveis novas entram em `.env.example` com valor fictício.
- Erros que se repetem viram incidente: use `/registrar-incidente`.
