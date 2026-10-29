# Memória do projeto

Decisões e incidentes que valem para todo o time e não aparecem no código. Este arquivo é importado pelo `CLAUDE.md`. Atualize quando uma decisão mudar.

## Decisões

- 2026-09-02: datas de vencimento são gravadas em UTC e exibidas no fuso do cliente.
- 2026-09-15: o cálculo de multa e juros fica só em `app/servicos/encargos.py`, para existir uma única fonte de verdade.

## Incidentes

- 2026-10-14: o agente editou uma migração já aplicada em produção para corrigir o nome de uma coluna. Fix: regra 4 do `CLAUDE.md` e `Edit(/migrations/**)` passou a pedir confirmação no `.claude/settings.json`.
