# 6. Montando um harness no Claude Code

As páginas anteriores descreveram o harness em termos gerais. Esta mostra como cada conceito vira um arquivo concreto no Claude Code, compara os dois exemplos da trilha (um enxuto e um mais completo) e indica como montar, conferir e manter um harness em um projeto real.

## 6.1 Objetivo e escopo

O guia cobre os arquivos de projeto que o Claude Code lê: instruções, memória, regras, permissões, hooks, sandbox, subagentes, skills e MCP. Ficam de fora a configuração organizacional gerenciada por administradores e os plugins.

Comportamentos, nomes de campos e limites citados aqui foram verificados na documentação oficial do Claude Code em 2026-10-28 e podem mudar entre versões.

**Pré-requisitos:** Claude Code instalado; para os hooks do exemplo completo, Node.js. Conhecer as [páginas 2 a 5](2-guides-e-sensors.md) desta trilha ajuda a entender por que cada arquivo existe.

## 6.2 Cada conceito, um arquivo

| Conceito da trilha | Arquivo no Claude Code | Versionado? | Quando é carregado |
|---|---|---|---|
| Instruções gerais (guide) | `CLAUDE.md` na raiz | Sim | Início de toda sessão |
| Instruções pessoais | `CLAUDE.local.md` na raiz | Não (no `.gitignore`) | Início de toda sessão, depois do `CLAUDE.md` |
| Memória do time | Arquivo importado com `@caminho` | Sim | Junto com quem o importa |
| Memória pessoal do agente | `~/.claude/projects/<projeto>/memory/` | Não | Índice no início; o resto sob demanda |
| Regras por área | `.claude/rules/*.md` com `paths` | Sim | Ao ler ou editar arquivo que casa com `paths` |
| Permissões (bloqueio) | `permissions` em `.claude/settings.json` | Sim | Sempre |
| Permissões pessoais | `.claude/settings.local.json` | Não | Sempre, por cima do arquivo versionado |
| Sensors e bloqueios com lógica | `hooks` em `.claude/settings.json` + scripts | Sim | No evento configurado |
| Isolamento do sistema | `sandbox` em `.claude/settings.json` | Sim | Em cada comando de terminal |
| Procedimentos | `.claude/skills/<nome>/SKILL.md` | Sim | Descrição sempre; corpo quando usado |
| Isolamento de contexto e especialização | `.claude/agents/<nome>.md` | Sim | Quando o Claude delega |
| Integrações | `.mcp.json` na raiz | Sim | Depois de aprovado por cada pessoa |
| Estado de tarefas longas | Arquivos do próprio projeto (`feature_list.json`, `progresso.md`) | Sim | Quando as instruções mandam ler |

Duas regras de convivência entre esses arquivos:

- **Configurações se combinam por nível.** A ordem de precedência é: gerenciada pela organização, linha de comando, `.claude/settings.local.json`, `.claude/settings.json` e `~/.claude/settings.json`. Listas como `permissions.allow` são somadas entre os níveis, em vez de uma substituir a outra.
- **Instruções se somam.** Os `CLAUDE.md` da pasta atual e das pastas acima são todos carregados, do mais geral para o mais específico. Os de subpastas entram quando o Claude mexe em arquivos delas.

## 6.3 Os dois exemplos

Os dois exemplos montam o harness de um mesmo projeto fictício, uma API de faturas em Python, para que a diferença seja só de maturidade:

- [Harness enxuto](exemplos/claude-enxuto/README.md): `CLAUDE.md`, permissões, uma regra por caminho, a memória do time, um subagente revisor e uma skill. É o ponto de partida recomendado.
- [Harness completo](exemplos/claude-completo/README.md): acrescenta hooks, sandbox, regras por área, um segundo subagente, skills de revisão e de incidente, artefatos para tarefas longas e um `.mcp.json`.

Cada README explica arquivo por arquivo o que ele faz, por que está ali e quais são os limites.

```text
claude-enxuto/                      claude-completo/
├── CLAUDE.md                       ├── CLAUDE.md
└── .claude/                        ├── feature_list.json
    ├── settings.json               ├── progresso.md
    ├── memoria.md                  ├── init.sh
    ├── rules/testes.md             ├── .mcp.json
    ├── agents/revisor.md           ├── .gitignore
    └── skills/nova-feature/        └── .claude/
                                        ├── settings.json   (permissões, hooks, sandbox)
                                        ├── memoria/        (decisões, incidentes)
                                        ├── rules/          (api, banco, testes)
                                        ├── hooks/          (4 scripts Node.js)
                                        ├── agents/         (revisor, explorador)
                                        └── skills/         (nova-feature, revisar, registrar-incidente)
```

A passagem de um para o outro não deve ser feita de uma vez. O caminho saudável é usar o enxuto e acrescentar cada peça do completo quando um incidente real pedir, registrando o motivo na memória do time.

## 6.4 Passo a passo para um projeto real

1. **Gere uma primeira versão das instruções.** O comando `/init` analisa o repositório e propõe um `CLAUDE.md` com comandos e convenções encontrados. Se já existir um, ele sugere melhorias em vez de sobrescrever. Revise o resultado: tire o que o agente descobre sozinho lendo o código e acrescente o que ele não teria como saber.
2. **Crie o `.claude/settings.json` com permissões.**
   - Em `deny`, o que nunca deve acontecer: ler segredos, push, comandos destrutivos.
   - Em `ask`, o que precisa de confirmação: commit, instalação de pacotes, pastas sensíveis.
   - Em `allow`, só os comandos seguros e frequentes, para reduzir interrupções.
3. **Separe a memória do time** em um arquivo importado pelo `CLAUDE.md`, com decisões e incidentes datados.
4. **Mova regras específicas para `.claude/rules/`** quando o `CLAUDE.md` passar de algumas dezenas de linhas ou quando uma regra só valer para uma pasta.
5. **Transforme procedimentos repetidos em skills.** Se você explica a mesma sequência ao agente toda semana, ela é uma skill.
6. **Crie subagentes para isolar contexto ou restringir ferramentas**, como um revisor que não edita ou um explorador que só lê.
7. **Acrescente hooks e sandbox quando os incidentes pedirem**, seguindo a hierarquia da [página 2](2-guides-e-sensors.md#_2-5-a-hierarquia-de-fixes).

## 6.5 Verificação

Comandos para conferir o que o Claude Code carregou, todos dentro de uma sessão:

| Comando | O que mostra |
|---|---|
| `/status` | Os arquivos de configuração lidos na sessão (linha *Setting sources*) |
| `/memory` | Os arquivos `CLAUDE.md` e a memória automática; permite editar e ligar ou desligar a memória automática |
| `/permissions` | As regras `allow`, `ask` e `deny` em vigor, por origem |
| `/hooks` | Os hooks registrados |
| `/context` | Quanto da janela está ocupado e por quê |
| `/doctor` | Diagnóstico de instalação, configurações e `CLAUDE.md`, com sugestões de correção |

Para testar um hook sem abrir uma sessão, rode o script passando um evento simulado pela entrada padrão e confira o código de saída. O README do exemplo completo descreve os casos testados dessa forma.

## 6.6 Este repositório como caso real

O próprio Dev Library usa um harness do Claude Code para transformar rascunhos em páginas como esta:

- [CLAUDE.md](https://github.com/DaniloMSilveira/Dev-Library/blob/main/CLAUDE.md) traz o propósito, a estrutura, os comandos e as regras gerais, e importa a memória do projeto em [.claude/memoria.md](https://github.com/DaniloMSilveira/Dev-Library/blob/main/.claude/memoria.md).
- [.claude/rules/guia-de-estilo.md](https://github.com/DaniloMSilveira/Dev-Library/blob/main/.claude/rules/guia-de-estilo.md) usa `paths` para entrar no contexto só quando o trabalho é em `estudos/`.
- As skills de [.claude/skills/](https://github.com/DaniloMSilveira/Dev-Library/tree/main/.claude/skills) cobrem o fluxo de registrar, planejar, escrever e revisar. A de revisão roda no subagente [revisor-documentacao](https://github.com/DaniloMSilveira/Dev-Library/blob/main/.claude/agents/revisor-documentacao.md), que não tem ferramentas de edição. Ele tem `Bash` para rodar as verificações, e ficar só na leitura por esse caminho é uma instrução, não um bloqueio.
- [.claude/settings.json](https://github.com/DaniloMSilveira/Dev-Library/blob/main/.claude/settings.json) faz cinco coisas:
  - nega a leitura de segredos e credenciais (`.env`, chaves, estados do Terraform, `~/.ssh`, `~/.aws`) e comandos que publicam ou destroem: push forçado, `terraform apply` e `destroy`, `kubectl delete`, `npm publish`;
  - pede confirmação para commit, push, comandos git que descartam alterações, `rm -rf`, CLIs de nuvem, instalação de pacotes e mudanças na configuração do site;
  - repete as regras para Bash e PowerShell, porque o repositório é usado no Windows;
  - exclui os `CLAUDE.md` e as regras destes exemplos com `claudeMdExcludes`, para que as instruções do projeto fictício não entrem nas sessões do repositório;
  - nega as skills dos exemplos com regras `Skill(...)`, porque o Claude Code carrega as skills de uma subpasta quando trabalha em arquivos dela.
- `npm run verificar` é o sensor computacional do fluxo: confere estrutura, links e marcas de material de terceiros, e roda o build do site.

## 6.7 Custos e riscos

- **O harness versionado executa código.** Hooks em `.claude/settings.json` rodam comandos na máquina de quem abre o projeto. Revise mudanças em `.claude/` e no `.mcp.json` com o mesmo cuidado de um script de build. O Claude Code exige que cada pessoa confie na pasta antes de aplicar parte dessas configurações, e pede aprovação para servidores MCP do projeto.
- **Segredos nunca entram nesses arquivos.** Credenciais de MCP vêm de variáveis de ambiente, e o `.gitignore` deve cobrir `.env`, `.claude/settings.local.json` e `CLAUDE.local.md`.
- **Regras de permissão não são isolamento.** Elas comparam o texto do comando. Onde a garantia importa, use o sandbox, que não roda no Windows nativo, ou rode o agente em um ambiente isolado.
- **Cada peça custa contexto ou tempo.** Instruções longas consomem a janela, e hooks pesados atrasam cada passo. Prefira poucas peças que você entende e verifica.
- **O harness precisa de manutenção.** Revise periodicamente instruções, regras e memória para remover o que ficou desatualizado ou contraditório. O `/doctor` ajuda a encontrar problemas nos arquivos de instrução.

## 6.8 Limpeza

Para remover o harness de um projeto: apague `CLAUDE.md`, a pasta `.claude/` e o `.mcp.json`, e os artefatos de estado se existirem. A memória automática fica fora do repositório, em `~/.claude/projects/<projeto>/memory/`, e pode ser desligada pelo `/memory`. Aprovações de servidores MCP do projeto podem ser reiniciadas com `claude mcp reset-project-choices`.

## 6.9 Resumo

No Claude Code, cada parte do harness tem um arquivo:

- **o que orienta:** `CLAUDE.md`, regras e skills;
- **o que lembra:** a memória do time, versionada, e a memória automática, pessoal;
- **o que impõe:** permissões, hooks e sandbox;
- **o que isola:** subagentes;
- **o que conecta:** `.mcp.json`.

O exemplo enxuto reúne o mínimo útil, e o completo mostra até onde o harness pode chegar quando os incidentes pedirem. A ordem recomendada é começar pequeno, conferir o que foi carregado com `/status`, `/memory` e `/hooks`, e acrescentar cada peça em resposta a um erro real.

## Fontes

- Claude Code, documentação oficial de [memória e CLAUDE.md](https://code.claude.com/docs/en/memory), [configurações](https://code.claude.com/docs/en/settings), [permissões](https://code.claude.com/docs/en/permissions), [hooks](https://code.claude.com/docs/en/hooks), [sandbox](https://code.claude.com/docs/en/sandboxing), [subagentes](https://code.claude.com/docs/en/sub-agents), [skills](https://code.claude.com/docs/en/skills), [MCP](https://code.claude.com/docs/en/mcp) e [comandos](https://code.claude.com/docs/en/commands), consultado em 2026-10-28.
