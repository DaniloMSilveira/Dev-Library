# 1. O que é harness engineering

Um modelo de linguagem, sozinho, recebe texto e devolve texto. Para que ele faça trabalho real (editar código, consultar um banco, abrir um ticket), alguém precisa construir em volta dele as instruções, as ferramentas, as permissões, a memória e as verificações. Esse conjunto é o **harness**, e harness engineering é a disciplina de projetá-lo.

Esta página define o termo, mostra de onde ele veio, como ele se relaciona com prompt engineering e context engineering, e apresenta a ideia que organiza a trilha inteira: cada erro do agente vira uma correção permanente no ambiente. Ela pressupõe a noção de agente da trilha [Design patterns de agentes](../design-patterns-agentes/1-agentes-e-padroes.md).

## 1.1 Termos e definições

**Modelo:** o LLM em si, com seus pesos e sua função de inferência. Na maioria dos casos de uso, quem constrói um agente escolhe entre os modelos disponíveis, mas não muda o que eles são.

**Harness:** tudo o que está em volta do modelo e não é o modelo: instruções de sistema e arquivos como `CLAUDE.md`, definições e executores de ferramentas, permissões, isolamento, memória, verificações, orquestração e observabilidade. A palavra vem dos arreios que conectam a força de um animal a uma carroça: a força existe, mas sem o arreio ela não puxa nada na direção certa. A analogia vale até aí; um harness de software também mede, registra e corrige, o que um arreio não faz.

**Agente:** a combinação dos dois. O texto *The Anatomy of an Agent Harness*, da LangChain (março de 2026), resume isso como **agente = modelo + harness** e tira a consequência prática: se você não é o modelo, você é o harness, ou seja, quase todo o trabalho de quem constrói agentes acontece do lado do harness.

**Harness engineering:** projetar, testar e evoluir o harness como se projeta qualquer sistema de software: com versionamento, testes, revisão e correção de incidentes.

## 1.2 De onde vem o termo

O termo ganhou forma em 2026, a partir da prática com agentes de programação:

| Data | Autor | Contribuição |
|---|---|---|
| 05/02/2026 | Mitchell Hashimoto, *My AI Adoption Journey* | Chama de "harness engineering" o hábito de, a cada erro do agente, investir em uma solução para que ele não se repita: instruções no `AGENTS.md` ou ferramentas programadas, como scripts de verificação |
| 10/03/2026 | Vivek Trivedy, LangChain, *The Anatomy of an Agent Harness* | Formula agente = modelo + harness e lista os componentes: prompts de sistema, ferramentas, skills e MCPs, infraestrutura (sistema de arquivos, sandbox, navegador), orquestração e hooks |
| 02/04/2026 | Birgitta Böckeler, Thoughtworks, em martinfowler.com | Organiza os controles do harness em *guides* e *sensors*, tema da [página 2](2-guides-e-sensors.md) |

A prática é anterior ao nome. Em novembro de 2025, a Anthropic já descrevia em *Effective harnesses for long-running agents* um conjunto de arquivos e rotinas para que um agente trabalhe em várias sessões sem perder o fio: lista de features, log de progresso e script de inicialização. A [página 3](3-instrucoes-memoria-e-contexto.md) trata desses artefatos.

## 1.3 Prompt, contexto e harness

As três disciplinas não competem. Cada uma está contida na seguinte:

| Disciplina | Pergunta que responde | Escopo |
|---|---|---|
| Prompt engineering | Como formular esta chamada ao modelo? | Uma interação |
| Context engineering | O que o modelo precisa ver, em que ordem, ao longo de muitas interações? | A informação que entra no modelo (ver a trilha de [Context Engineering](../context-engineering/1-conceitos-fundamentais.md)) |
| Harness engineering | Que sistema torna o modelo confiável em trabalho real? | Também o que sai do modelo: como é validado, executado, limitado, registrado e corrigido |

Essa hierarquia é uma forma de organizar os conceitos, não uma definição oficial. O ponto útil dela é mostrar onde investir esforço: ajustar o prompt e montar bem o contexto continuam importantes, mas não resolvem um agente que apaga o arquivo errado. Isso se resolve com permissões, verificações e isolamento, que são harness.

## 1.4 O que é e o que não é harness

Um teste simples ajuda a classificar: **se você trocar o modelo por outro de outro fornecedor, isso continua lá?** Se continua, é harness.

| Fica com o modelo | Fica no harness |
|---|---|
| Pesos e treinamento | Instruções (`CLAUDE.md`, `AGENTS.md`, prompts de sistema) |
| Capacidade de raciocínio e de geração | Ferramentas: schemas e código que as executa |
| Tamanho máximo da janela de contexto | Permissões, sandbox e aprovação humana |
| | Memória entre sessões e gestão do contexto |
| | Verificações: testes, lint, validação de schema, revisão |
| | Orquestração: subagentes, roteamento, loops |
| | Logs, métricas e avaliações |

Uma consequência dessa divisão: o modelo é probabilístico, mas o harness é código e configuração, e pode ser testado, versionado e revisado como qualquer software. Quem já trabalha com engenharia de software já tem a maior parte das habilidades necessárias.

## 1.5 O fix permanente

A ideia central da disciplina vem do texto de Hashimoto: **quando o agente erra, o trabalho é mudar o ambiente para que aquele erro não aconteça de novo**, e não só pedir com mais ênfase na próxima vez.

**Exemplo concreto.** O agente editou um arquivo de migração de banco que já tinha sido aplicado em produção. Há três respostas possíveis, em ordem crescente de força:

1. **Instrução:** acrescentar ao `CLAUDE.md` "não edite migrações existentes". Reduz a chance do erro, mas o modelo ainda pode ignorar.
2. **Sensor:** um teste ou script que detecta migração alterada e reprova a mudança. O erro pode acontecer, mas não passa despercebido.
3. **Bloqueio:** um hook ou permissão que recusa a edição antes de ela acontecer. O erro deixa de ser possível pelo caminho bloqueado; a [página 4](4-ferramentas-permissoes-e-sandbox.md#_4-4-permissoes-na-pratica) mostra por que cada bloqueio cobre um caminho e não todos.

A [página 2](2-guides-e-sensors.md) detalha quando usar cada nível. O [exemplo completo](exemplos/claude-completo/README.md) da trilha registra justamente esse incidente e o resolve com um hook.

## 1.6 Limites e quando investir

- **Comece simples.** Um arquivo de instruções bem escrito, permissões básicas e os testes do projeto já cobrem boa parte dos problemas. Peças mais elaboradas (hooks, subagentes, artefatos de estado) devem entrar quando um problema real pedir.
- **Harness não compensa um modelo inadequado para a tarefa.** Ele torna o agente mais previsível e verificável, mas não cria capacidade que o modelo não tem.
- **Todo controle tem custo.** Cada verificação acrescenta tempo, cada confirmação humana acrescenta atrito. O objetivo é o mínimo de controle que deixa o risco aceitável.
- **O harness envelhece.** Instruções e regras desatualizadas ou contraditórias pioram o comportamento. Ele precisa de revisão periódica, como qualquer código.

## 1.7 Resumo

Harness é tudo o que envolve o modelo e o transforma em um agente útil: instruções, ferramentas, permissões, memória, verificações e orquestração. Quem constrói agentes não controla o modelo, mas controla o harness, e por isso harness engineering é onde está a maior parte do trabalho. A disciplina contém o prompt engineering e o context engineering, e acrescenta o que acontece depois que o modelo responde. Seu princípio central é o fix permanente: cada erro vira uma mudança no ambiente, da instrução ao bloqueio estrutural.

## Fontes

- Mitchell Hashimoto, [My AI Adoption Journey](https://mitchellh.com/writing/my-ai-adoption-journey), 2026-02-05, consultado em 2026-10-28.
- Vivek Trivedy, [The Anatomy of an Agent Harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness), LangChain, 2026-03-10, consultado em 2026-10-28.
- Birgitta Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html), martinfowler.com, 2026-04-02, consultado em 2026-10-28.
- Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 2025-11-26, consultado em 2026-10-28.
