# Incidentes

Erros do agente que viraram uma correção permanente no harness. Cada entrada diz o que aconteceu, a causa e em que nível o fix foi feito: instrução, sensor ou bloqueio estrutural.

- 2026-10-14: o agente editou uma migração já aplicada para corrigir o nome de uma coluna.
  Causa: nada impedia a edição. Fix (bloqueio): `.claude/hooks/proteger-arquivos.mjs` recusa, pelas ferramentas de edição, alterar migração já commitada.
- 2026-10-20: o agente declarou a feature FAT-001 pronta sem rodar os testes de integração; ela voltou para `em_andamento` e foi reverificada no dia seguinte.
  Causa: o critério de pronto não estava escrito. Fix (instrução): seção "Pronto significa" no `CLAUDE.md`.
- 2026-10-24: um `float` entrou no cálculo de juros e gerou diferença de centavos.
  Causa: a regra existia, mas não era verificada. Fix (sensor): `.claude/hooks/lint-apos-edicao.mjs` acusa `float` em arquivos de `app/servicos/` logo depois de cada edição.
