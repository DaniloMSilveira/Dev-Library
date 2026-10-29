---
tema: Harness engineering
area: IA
status: documentado
criado-em: 2026-10-28
documentado-em:
  - estudos/IA/docs/harness-engineering/1-o-que-e-harness.md
  - estudos/IA/docs/harness-engineering/2-guides-e-sensors.md
  - estudos/IA/docs/harness-engineering/3-instrucoes-memoria-e-contexto.md
  - estudos/IA/docs/harness-engineering/4-ferramentas-permissoes-e-sandbox.md
  - estudos/IA/docs/harness-engineering/5-verificacao-e-evolucao.md
  - estudos/IA/docs/harness-engineering/6-harness-no-claude-code.md
  - estudos/IA/docs/harness-engineering/exemplos/claude-enxuto/
  - estudos/IA/docs/harness-engineering/exemplos/claude-completo/
---

# Harness engineering

## O que aprendi

Resumo com palavras próprias do material estudado (ver Fontes). Nenhum trecho ou código do material original foi copiado.

**Ideia central.** Um agente é o modelo mais tudo o que está em volta dele: instruções, ferramentas, permissões, memória, verificações, orquestração e observabilidade. Esse "em volta" é o harness. Quem usa ou constrói agentes não muda o modelo, só escolhe entre os disponíveis; o que dá para projetar, testar e versionar é o harness. Harness engineering contém context engineering, que contém prompt engineering.

**Fix permanente.** Cada erro do agente deve virar uma melhoria no ambiente, para que o mesmo erro não volte. Há uma hierarquia de força: regra escrita (só reduz a chance), sensor automático (detecta e bloqueia), restrição estrutural (torna a ação impossível). Se o erro se repete apesar da regra, sobe-se um nível.

**Guides e sensors.** Guides atuam antes da ação (system prompt, CLAUDE.md/AGENTS.md, descrição de ferramentas): persuadem. Sensors atuam depois (schema, testes, lint, revisão por outro modelo, aprovação humana): impõem. Precisa dos dois. Ação irreversível pede controle estrutural, não só instrução.

**Instruções (rules files).** Arquivo versionado no repositório que o agente lê ao começar: contexto do projeto, stack, comandos literais, convenções, áreas proibidas, padrão de PR, histórico de incidentes. Específico, imperativo, agrupado por tema e curto; começar pequeno e crescer a cada erro real.

**Ferramentas e governança.** Ferramenta = schema (nome, descrição com quando usar e quando não usar, parâmetros com restrições) + executor no harness, que valida, aplica permissões e só então executa. Menor privilégio. Camadas de isolamento (container, filesystem, rede, lista de comandos, aprovação humana): cada uma cobre uma falha diferente. MCP padroniza a interface das ferramentas, não a segurança.

**Memória e contexto.** Memória de trabalho (janela atual), episódica (interações passadas) e semântica (conhecimento). Context rot: qualidade cai quando o contexto enche; resolve-se com compactação, resumo e recomeço com contexto enxuto, não com janela maior.

**Verificação.** Sensors em cascata, do mais barato (determinístico) ao mais caro (LLM-juiz, humano), falhando rápido. Loop planejar-executar-verificar com limite de iterações. Testes, lint e hooks de pre-commit como sensors. Humano no loop para o irreversível, o incerto e o regulado, no mínimo necessário.

**Evolução.** Medir qualidade, operação e experiência juntas. Evals como testes do agente; cada bug vira um caso permanente. Ciclo: produção → observação → incidente → causa raiz → fix permanente → eval de regressão.

**Agentes de longa duração.** Artefatos que dão continuidade entre sessões: lista de features com status e evidência, log de progresso, script de inicialização e rotina de início de sessão.

## Fontes

- E-book de curso sobre agent harness engineering (material pago, consultado localmente e não versionado).
- Fontes públicas conferidas em 2026-10-28: Mitchell Hashimoto, "My AI Adoption Journey" (2026-02-05); LangChain, "The Anatomy of an Agent Harness" (2026-03-10); Birgitta Böckeler, "Harness engineering for coding agent users", martinfowler.com (2026-04-02); Anthropic, "Effective harnesses for long-running agents" (2025-11-26); documentação do Claude Code (memory, settings, permissions, hooks, sub-agents, skills, mcp, sandboxing).

## Exemplos, comandos ou código

Nenhum código do material guardado aqui. Os exemplos práticos serão estruturas próprias de harness para o Claude Code.

## Dúvidas e pontos a confirmar

- [agente] O material atribui a fórmula "Agent = Model + Harness" a Hashimoto; ela aparece no texto da LangChain, não no post dele.
- [agente] Os números do material (variação de 22 pontos no SWE-bench, +13,7 pontos no Terminal Bench, "88% dos projetos não chegam à produção", taxas de acurácia) não foram encontrados nas fontes citadas. Ficam fora da documentação.
- [agente] O material diz que o termo context engineering foi cunhado em dezembro de 2025; não confirmado. Fica fora.

## Como quero a documentação

Nova trilha na área IA, com exemplo prático de estrutura de harness para o Claude Code em duas versões: uma enxuta e uma mais completa, explicando cada arquivo.
