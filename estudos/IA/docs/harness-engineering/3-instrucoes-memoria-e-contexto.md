# 3. Instruções, memória e contexto

Cada sessão de um agente começa do zero: o modelo não lembra da conversa de ontem, das convenções do projeto nem do erro que cometeu na semana passada. Tudo o que ele sabe ao começar vem do harness, por meio de arquivos de instruções, memória e artefatos de estado. E tudo isso disputa espaço na mesma janela de contexto.

Esta página trata da parte do harness que decide **o que o agente sabe**: o que entra em um arquivo de instruções, como carregar informação só quando ela é necessária, como a memória funciona entre sessões e quais artefatos permitem que um agente trabalhe por vários dias em uma mesma tarefa. Os fundamentos de janela de contexto e memória estão na trilha de [Context Engineering](../context-engineering/3-memoria-e-estado.md); aqui o foco é como o harness os organiza.

## 3.1 Termos e definições

**Arquivo de instruções (rules file):** arquivo de texto versionado no repositório que o agente lê ao começar a trabalhar. O nome varia por ferramenta: `CLAUDE.md` no Claude Code, `AGENTS.md` como formato aberto usado por várias ferramentas, `.github/copilot-instructions.md` no GitHub Copilot.

**Import:** referência dentro de um arquivo de instruções que inclui o conteúdo de outro arquivo. No Claude Code, a sintaxe é `@caminho/do/arquivo`.

**Regra por caminho:** instrução que só entra no contexto quando o agente trabalha em arquivos de determinada pasta ou extensão.

**Carregamento progressivo:** colocar no contexto inicial só um índice curto (nomes e descrições) e carregar o conteúdo completo quando ele for usado. As skills do Claude Code funcionam assim.

**Context rot:** a queda de qualidade das respostas à medida que o contexto se enche de material acumulado, como resultados longos de ferramentas, tentativas descartadas e informação desatualizada.

**Compactação:** resumir a conversa até o momento para liberar espaço na janela, mantendo decisões e estado e descartando o resto.

## 3.2 O que vai no arquivo de instruções

O arquivo de instruções é o guide mais importante do harness, porque está presente em toda sessão. O que costuma valer a pena incluir:

| Seção | Conteúdo | Por que ajuda |
|---|---|---|
| Contexto | O que o projeto é, em uma ou duas frases, e a stack | Evita suposições erradas sobre linguagem e frameworks |
| Comandos | Comandos literais para instalar, testar, rodar lint e subir localmente | O agente roda o comando certo em vez de adivinhar |
| Estrutura | Onde fica cada tipo de código | Reduz buscas e arquivos criados no lugar errado |
| Regras | Convenções verificáveis, numeradas e no imperativo | "Use `Decimal` para dinheiro" funciona; "siga boas práticas" não |
| Limites | O que o agente não deve fazer sem pedido explícito | Deixa claro o que é proibido, sem depender de dedução |
| Rotina e critério de pronto | Como começar uma sessão e quando algo está concluído | Evita que o agente declare sucesso sem verificar |

E o que **não** deve entrar:

- **O que o agente descobre lendo o código**, como a lista de todos os arquivos ou a explicação de cada função. Ocupa espaço e desatualiza.
- **Regras que valem só para uma parte do projeto.** Elas vão para regras por caminho, que só carregam quando são relevantes.
- **Documentação longa.** O arquivo aponta para ela, em vez de copiá-la.

### Manter curto

A documentação do Claude Code recomenda arquivos `CLAUDE.md` com menos de 200 linhas, porque arquivos maiores consomem mais contexto e reduzem a aderência às instruções. Ela também alerta que instruções contraditórias fazem o Claude escolher uma delas de forma arbitrária. Dois cuidados decorrem disso:

- **Import organiza, mas não economiza.** O arquivo importado é carregado inteiro junto com o que o importa. Para economizar contexto, use regras por caminho ou skills.
- **Comece pequeno e cresça com o uso.** Uma primeira versão com o contexto do projeto, três comandos e as regras essenciais é suficiente. As linhas novas devem vir de erros reais do agente, como no fix permanente da [página 1](1-o-que-e-harness.md#_1-5-o-fix-permanente).

## 3.3 Carregar só o que é necessário

A janela de contexto é finita, e o que entra nela sem necessidade dilui o que importa. Por isso um bom harness carrega informação em camadas:

| Camada | Quando entra no contexto | No Claude Code |
|---|---|---|
| Instruções gerais | Sempre, no início da sessão | `CLAUDE.md` da raiz e regras sem `paths` |
| Instruções de uma pasta | Quando o agente lê ou edita um arquivo daquela pasta | `CLAUDE.md` em subpastas e regras com `paths` |
| Procedimentos | Só o nome e a descrição ficam sempre; o corpo entra quando o procedimento é usado | Skills (`.claude/skills/<nome>/SKILL.md`) |
| Trabalho pesado de leitura | Fica em outro contexto; só o resumo volta | Subagentes |

O último item é um uso importante de subagentes que não tem a ver com especialização: **isolar contexto**. Um subagente que lê 30 arquivos para descobrir onde um cálculo é feito devolve um resumo de poucas linhas, e a conversa principal não fica carregando aqueles 30 arquivos. A trilha de [Design patterns de agentes](../design-patterns-agentes/6-supervisor.md) trata de coordenação entre agentes; aqui o ganho é só de contexto.

## 3.4 Memória entre sessões

Há dois tipos de memória persistente com papéis diferentes:

| | Memória do projeto | Memória pessoal do agente |
|---|---|---|
| Quem escreve | O time | O próprio agente, a partir de correções e preferências |
| Onde fica | Arquivos versionados no repositório | Fora do repositório, na máquina de cada pessoa |
| O que guarda | Decisões, incidentes, convenções do time | Preferências e aprendizados de quem usa |
| Exemplo | `.claude/memoria.md` importado pelo `CLAUDE.md` | Memória automática do Claude Code |

No Claude Code, a memória automática fica em `~/.claude/projects/<projeto>/memory/`, com um índice `MEMORY.md` e um arquivo por anotação. Só as primeiras 200 linhas (ou 25 KB) do índice são carregadas no início de cada sessão; os demais arquivos são lidos sob demanda. Ela pode ser desligada por projeto com `"autoMemoryEnabled": false` nas configurações.

A memória do projeto, por ser versionada, passa por revisão como o código e vale para todos. É o lugar certo para o histórico de incidentes, que ensina ao agente o que já deu errado.

## 3.5 Context rot e compactação

Em sessões longas, a janela se enche de resultados de ferramentas, tentativas descartadas e informação que já mudou. As instruções do início ficam proporcionalmente menores no meio de tanto material, e a qualidade cai: o agente repete passos, esquece restrições e dá respostas mais genéricas.

Uma janela maior adia o problema, mas não o resolve. O que resolve é o harness cuidar do que está no contexto:

- **Compactar:** resumir a conversa mantendo decisões e estado. No Claude Code, `/compact` faz isso sob demanda e aceita instruções sobre o que preservar; `/context` mostra quanto da janela está ocupado e por quê.
- **Recomeçar com contexto enxuto:** encerrar a sessão e começar outra, carregando só o necessário a partir de arquivos de estado.
- **Isolar:** mandar leituras extensas para subagentes, como na seção 3.3.

As duas últimas estratégias dependem de o estado do trabalho estar **em arquivos**, e não só na conversa. É o tema da próxima seção.

## 3.6 Agentes que trabalham em várias sessões

Em *Effective harnesses for long-running agents* (novembro de 2025), a Anthropic descreve como fazer um agente avançar em uma aplicação grande ao longo de muitas sessões, cada uma começando sem memória da anterior. A solução é um conjunto de artefatos que guardam o estado:

| Artefato | Papel |
|---|---|
| Lista de features (`feature_list.json`) | Escopo verificável. Cada item tem descrição, passos de teste e um campo indicando se passa. O agente só altera esse campo e não pode remover nem editar os testes |
| Log de progresso (`claude-progress.txt`) | O que cada sessão fez, para a próxima saber onde parou |
| Script de inicialização (`init.sh`) | Prepara e sobe o ambiente de forma padronizada |
| Histórico do git | Commits descritivos a cada mudança, para entender o que foi feito e voltar a um estado bom |

Cada sessão segue a mesma rotina: confirmar o diretório, ler o progresso e o histórico do git, escolher a feature de maior prioridade ainda não concluída, rodar o script de inicialização e fazer um teste básico antes de mexer em qualquer coisa.

Duas escolhas do texto merecem destaque:

- **Uma feature por vez.** Os autores relatam que isso foi essencial para evitar que o agente tentasse construir tudo de uma vez.
- **JSON em vez de Markdown para a lista de features**, porque o modelo tende a reescrever indevidamente um arquivo de texto livre com mais facilidade.

O [exemplo completo](exemplos/claude-completo/README.md) da trilha adapta essa ideia com `feature_list.json`, `progresso.md`, `init.sh` e um hook que resume o estado no início da sessão.

## 3.7 Limites e trade-offs

- **Instruções não são garantias.** Tudo nesta página é guide: influencia o agente, mas não impede nada. O que não pode acontecer precisa de controle estrutural (ver a [página 4](4-ferramentas-permissoes-e-sandbox.md)).
- **Memória errada é pior que memória nenhuma.** Uma decisão que mudou e não foi atualizada leva o agente a agir com segurança na direção errada. Memórias precisam de data e de revisão.
- **Artefatos de estado só funcionam se forem mantidos.** Se o agente não atualizar o progresso ao fim da sessão, a próxima começa com informação velha. Por isso a atualização faz parte do critério de pronto.
- **Carregamento sob demanda depende de boa descrição.** Uma skill ou subagente com descrição vaga não é usado quando deveria. A descrição é o que o modelo lê para decidir.

## 3.8 Resumo

O que o agente sabe ao começar vem do harness. O arquivo de instruções traz contexto, comandos, estrutura, regras e limites, e deve ser curto e crescer a partir de erros reais. Informação que vale só às vezes entra sob demanda, por regras por caminho, skills e subagentes. A memória do projeto é versionada e compartilhada; a memória automática é pessoal. Contra o context rot, o caminho é compactar, recomeçar e isolar, e para isso o estado do trabalho precisa estar em arquivos, como a lista de features, o log de progresso e o script de inicialização.

## Fontes

- Claude Code, [How Claude remembers your project](https://code.claude.com/docs/en/memory), documentação oficial, consultado em 2026-10-28.
- Claude Code, documentação oficial de [skills](https://code.claude.com/docs/en/skills) e de [subagentes](https://code.claude.com/docs/en/sub-agents), consultado em 2026-10-28.
- Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 2025-11-26, consultado em 2026-10-28.
