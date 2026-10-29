# Decisões

Decisões de projeto que não aparecem no código. Uma linha por decisão, com data. Quando uma decisão mudar, edite a linha e registre a data da mudança.

- 2026-09-02: datas de vencimento são gravadas em UTC e exibidas no fuso do cliente.
- 2026-09-15: o cálculo de multa e juros fica só em `app/servicos/encargos.py`, para existir uma única fonte de verdade.
- 2026-10-03: a API não apaga faturas; cancelamento muda o `status` para `cancelada` e mantém o registro.
