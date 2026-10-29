---
name: nova-feature
description: Implementa uma feature da API de Faturas do plano à verificação. Use quando pedirem uma funcionalidade nova ou uma mudança de comportamento.
argument-hint: "[descrição da feature]"
---

# Nova feature

Feature pedida: $ARGUMENTS

1. **Planeje antes de editar.** Liste os arquivos que vai mudar, o comportamento esperado e os testes que vão provar esse comportamento. Se algo estiver ambíguo, pergunte antes de seguir.
2. **Escreva os testes primeiro** em `tests/` e rode `pytest` para confirmar que falham pelo motivo esperado.
3. **Implemente** seguindo as regras do `CLAUDE.md`.
4. **Verifique:** rode `pytest` e `ruff check .` até os dois passarem.
5. **Peça revisão** ao subagente `revisor` e corrija os achados.
6. **Relate** o que mudou, os comandos que rodou com o resultado de cada um e o que ficou pendente.
