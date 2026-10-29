---
name: revisar
description: Revisa as mudanças não commitadas em um subagente independente, sem ferramentas de edição. Use antes de concluir uma feature ou quando pedirem revisão.
context: fork
agent: revisor
---

# Revisar mudanças

Arquivos alterados desde o último commit:

!`git diff --stat`

Revise essas mudanças seguindo as suas instruções de revisor. Considere também a feature com `status: em_andamento` em `feature_list.json`: a mudança faz o que a feature pede, e só isso?
