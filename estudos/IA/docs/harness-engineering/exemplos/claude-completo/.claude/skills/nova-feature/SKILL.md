---
name: nova-feature
description: Implementa a próxima feature de feature_list.json do plano à verificação, registrando evidência e progresso. Use quando pedirem para continuar o trabalho ou implementar uma feature.
argument-hint: "[id da feature, opcional]"
---

# Nova feature

Feature indicada (se vazio, use a ativa em `feature_list.json`): $ARGUMENTS

Estado atual do repositório:

!`git status --short`

## Planejar

1. Leia a feature em `feature_list.json`, incluindo os passos de `verificacao`.
2. Se não souber onde o comportamento atual está implementado, peça ao subagente `explorador`.
3. Escreva o plano: arquivos que vai mudar, comportamento esperado e testes que vão provar esse comportamento. Se algo estiver ambíguo, pergunte antes de seguir.

## Executar

4. Escreva os testes primeiro e rode `pytest` para confirmar que falham pelo motivo esperado.
5. Implemente seguindo o `CLAUDE.md` e as regras de `.claude/rules/`.

## Verificar

6. Rode `pytest` e `ruff check .` até passarem.
7. Execute os passos de `verificacao` da feature e anote em `evidencia` o que rodou e o resultado.
8. Rode `/revisar` e corrija os achados graves.
9. Só então mude o `status` da feature para `concluida`. Se não conseguir concluir, mantenha `em_andamento` e registre o bloqueio.

## Registrar

10. Acrescente uma entrada no topo de `progresso.md` com a data, a feature, o que foi feito, a verificação executada e o próximo passo.
