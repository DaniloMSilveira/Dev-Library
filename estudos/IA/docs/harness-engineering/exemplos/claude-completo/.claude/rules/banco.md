---
paths:
  - "app/db/**/*.py"
  - "migrations/**/*.py"
---

# Banco de dados

- Consultas usam parâmetros do SQLAlchemy; nunca monte SQL concatenando texto.
- Mudança de esquema sempre por migração nova: `alembic revision -m "descricao"`.
- Migração que remove coluna ou tabela precisa de confirmação humana antes de ser criada.
- Toda migração nova tem `downgrade` funcional.
