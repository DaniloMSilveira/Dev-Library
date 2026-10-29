---
paths:
  - "app/api/**/*.py"
---

# Rotas da API

- A rota só valida a entrada, chama um serviço de `app/servicos/` e converte o resultado em resposta HTTP.
- Entrada e saída usam schemas Pydantic de `app/api/schemas/`; não devolva modelos do banco direto.
- Erros de negócio viram `HTTPException` com o código do catálogo em `app/api/erros.py`.
- Rota nova precisa de teste em `tests/api/` cobrindo sucesso e pelo menos um erro.
