---
name: registrar-incidente
description: Transforma um erro do agente em uma correção permanente do harness e registra o incidente.
argument-hint: "[o que deu errado]"
disable-model-invocation: true
---

# Registrar incidente

Erro relatado: $ARGUMENTS

1. **Reconstitua o que aconteceu:** o que o agente fez, em que arquivo ou comando, e qual instrução ou contexto ele tinha naquele momento.
2. **Ache a causa:** faltou informação, a regra existia mas não era verificada, ou nada impedia a ação?
3. **Escolha o nível do fix**, consultando `.claude/memoria/incidentes.md` para ver se o erro já aconteceu:
   - primeira ocorrência por falta de informação: **instrução** (`CLAUDE.md` ou uma regra em `.claude/rules/`);
   - erro repetido apesar da instrução: **sensor** (hook PostToolUse, teste ou lint);
   - ação irreversível ou repetida apesar do sensor: **bloqueio** (regra `deny` no `settings.json` ou hook PreToolUse).
4. **Proponha o fix** ao usuário, com o arquivo e o trecho exatos, e aplique depois da confirmação. Alterações em `.claude/` e no `CLAUDE.md` pedem confirmação pelo `settings.json`.
5. **Prove que o fix funciona:** reproduza a situação original ou rode o hook com uma entrada simulada.
6. **Registre** em `.claude/memoria/incidentes.md`: data, o que aconteceu, a causa e o fix com o nível escolhido.
