# Harness completo para o Claude Code

Versão mais completa do [harness enxuto](../claude-enxuto/README.md), para o mesmo projeto fictício: uma API de faturas em Python (FastAPI e PostgreSQL). Ela acrescenta o que costuma aparecer quando o agente passa a trabalhar em tarefas longas e o time já colecionou alguns incidentes:

- **sensors automáticos (hooks):** checagens que rodam sozinhas antes e depois de cada ação;
- **isolamento do sistema (sandbox):** restrição de rede e de escrita imposta pelo sistema operacional;
- **regras por pasta:** uma regra para cada parte do código;
- **mais de um subagente:** um para revisar e outro para explorar o código;
- **uma skill de incidente:** transforma um erro em correção permanente;
- **artefatos de continuidade:** arquivos que permitem retomar o trabalho entre sessões.

Só os arquivos do harness existem aqui; o código da aplicação (`app/`, `tests/`, `migrations/`) não faz parte do exemplo. Datas, features, evidências e incidentes são ilustrativos. A explicação conceitual está em [6. Montando um harness no Claude Code](../../6-harness-no-claude-code.md).

## Estrutura

```text
claude-completo/
├── CLAUDE.md                        # instruções gerais: início de sessão, regras, definição de pronto
├── feature_list.json                # escopo: features com status, passos de verificação e evidência
├── progresso.md                     # log de sessões: o que foi feito e o próximo passo
├── init.sh                          # ritual de início: instala e prova que o ambiente está saudável
├── .mcp.json                        # servidor MCP do projeto (ilustrativo)
├── .gitignore                       # mantém segredos e configuração pessoal fora do git
└── .claude/
    ├── settings.json                # permissões, hooks e sandbox
    ├── memoria/
    │   ├── decisoes.md              # decisões do time
    │   └── incidentes.md            # erros do agente e o fix permanente de cada um
    ├── rules/
    │   ├── api.md                   # vale em app/api/
    │   ├── banco.md                 # vale em app/db/ e migrations/
    │   └── testes.md                # vale em tests/
    ├── hooks/
    │   ├── contexto-inicial.mjs     # SessionStart: resume a feature ativa e o último progresso
    │   ├── bloquear-comandos.mjs    # PreToolUse: bloqueia ou pede confirmação de comandos perigosos
    │   ├── proteger-arquivos.mjs    # PreToolUse: impede editar segredos, .git e migrações já commitadas
    │   └── lint-apos-edicao.mjs     # PostToolUse: aponta float e erros de lint logo após a edição
    ├── agents/
    │   ├── revisor.md               # revisa mudanças, sem poder editar
    │   └── explorador.md            # investiga o código e devolve um resumo curto
    └── skills/
        ├── nova-feature/SKILL.md    # planejar, executar, verificar e registrar uma feature
        ├── revisar/SKILL.md         # revisão em subagente separado (context: fork)
        └── registrar-incidente/SKILL.md  # transforma um erro em fix permanente
```

## O que muda em relação ao enxuto

| Parte do harness | Enxuto | Completo |
|---|---|---|
| Instruções | `CLAUDE.md` com regras gerais | Também rotina de início de sessão e definição de pronto |
| Memória do projeto | Um arquivo | Decisões e incidentes separados |
| Regras por caminho | Uma (testes) | Uma por área do código |
| Governança | Permissões | Permissões, hooks que bloqueiam e sandbox |
| Sensors | Testes e lint rodados pelo agente | Também hooks que rodam sozinhos após cada edição |
| Subagentes | Revisor | Revisor e explorador |
| Skills | `/nova-feature` | `/nova-feature`, `/revisar` e `/registrar-incidente` |
| Continuidade entre sessões | Nenhuma | `feature_list.json`, `progresso.md`, `init.sh` e hook de início |
| Integrações | Nenhuma | `.mcp.json` |

## O que cada arquivo faz

### Instruções e memória

**[CLAUDE.md](CLAUDE.md)** acrescenta três seções ao enxuto:

- **Início de sessão:** a rotina que toda sessão segue antes de editar. Ler o progresso, escolher uma única feature e rodar `./init.sh`.
- **Pronto significa:** as condições objetivas para considerar uma feature concluída, incluindo evidência registrada e revisão.
- **Limites:** inclui o caminho para registrar incidentes.

Os dois imports (`@.claude/memoria/decisoes.md` e `@.claude/memoria/incidentes.md`) trazem a memória do time para toda sessão. Os detalhes de cada pasta saíram do `CLAUDE.md` e foram para `.claude/rules/`, para que o arquivo principal continue curto.

**[decisoes.md](.claude/memoria/decisoes.md)** guarda as decisões de projeto que o código não mostra, uma por linha e com data.

**[incidentes.md](.claude/memoria/incidentes.md)** registra cada erro do agente com a causa e o **nível do fix**. Os três incidentes ilustram a hierarquia:

| Incidente | Fix | Nível |
|---|---|---|
| Faltava escrever o critério de pronto | Seção nova no `CLAUDE.md` | Instrução (guide) |
| Faltava verificar a regra do `Decimal` | Hook que roda após cada edição | Sensor |
| Nada impedia editar uma migração | Hook que recusa a edição | Bloqueio estrutural |

### Regras por caminho

**[api.md](.claude/rules/api.md)**, **[banco.md](.claude/rules/banco.md)** e **[testes.md](.claude/rules/testes.md)** usam o campo `paths` para entrar no contexto só quando o Claude mexe em arquivos daquela área. `banco.md` tem dois padrões, para `app/db/` e `migrations/`.

### Governança: `.claude/settings.json`

**[settings.json](.claude/settings.json)** junta três mecanismos.

**Permissões.** Seguem a mesma lógica do enxuto (`deny`, depois `ask`, depois `allow`), com mais casos:

- `allow` libera `./init.sh`, a criação de migrações (`alembic revision`) e a edição dos arquivos de estado;
- `allow` também libera `WebFetch` só para a documentação do FastAPI e do SQLAlchemy;
- `allow` libera `ruff check .` exatamente assim, sem `*`, para não liberar `ruff check --fix` nem `ruff format`, que reescrevem arquivos;
- `ask` exige confirmação para aplicar migrações, para `rm -rf` e para editar o próprio harness (`CLAUDE.md` e `.claude/`);
- `deny` bloqueia chaves privadas, `~/.ssh`, `~/.aws`, `curl` e `wget`.

Atenção a um efeito de composição: `./init.sh` está no `allow` e roda `pip install` por dentro. Assim, a instalação de pacotes feita pelo script não passa pelo `ask` de `Bash(pip install *)`, porque a regra compara o comando que o Claude digita, não o que o script executa. É aceitável aqui porque o script é versionado e revisado, mas mostra por que liberar um script equivale a liberar tudo o que ele faz.

**Hooks.** Cada hook é um comando que o Claude Code executa em um evento. O formato tem três níveis: o evento (`PreToolUse`), um grupo com `matcher` (o nome da ferramenta, como `Bash` ou `Edit|Write`) e a lista de comandos. `${CLAUDE_PROJECT_DIR}` é a raiz do projeto, para o caminho funcionar de qualquer pasta.

**Sandbox.** `sandbox.enabled` isola os comandos de terminal no nível do sistema operacional:

- a escrita fica restrita à pasta do projeto (e subpastas) e à pasta temporária do usuário. O ambiente virtual do Python precisa estar dentro do projeto, em `.venv/`, para o `pip install` funcionar;
- a rede passa por um proxy que só deixa sair para os domínios de `allowedDomains`, aqui o PyPI para instalar pacotes;
- `excludedCommands` roda `alembic upgrade` fora do sandbox, porque ele precisa conectar no PostgreSQL local, e conexões com serviços da máquina ficam bloqueadas por padrão. Um comando excluído roda com acesso total, mas continua passando pelas permissões: aqui, pelo `ask`.

Diferente das regras de `Bash`, o sandbox não depende do texto do comando: vale também para scripts chamados por esses comandos. Com ele ligado, comandos dentro do sandbox rodam sem perguntar, mas as regras `ask` e `deny` com conteúdo (como `Bash(git commit *)`) continuam valendo. Para subir o servidor local com `uvicorn` no macOS, seria preciso ainda `sandbox.network.allowLocalBinding`. O sandbox funciona no macOS, no Linux e no WSL2. No Windows nativo não é suportado, e os comandos rodam sem isolamento.

### Hooks: `.claude/hooks/`

Os hooks recebem o evento em JSON pela entrada padrão. Para os eventos de ferramenta, o JSON traz `tool_name` e `tool_input`, com `command` no Bash e `file_path` no Edit e no Write. O código de saída define o efeito:

| Saída | Efeito |
|---|---|
| `exit 0` sem texto | Segue o fluxo normal de permissões |
| `exit 0` com JSON na saída padrão | Permite decisões estruturadas, como `permissionDecision: "ask"` |
| `exit 2` | Bloqueia (em `PreToolUse`) ou avisa (em `PostToolUse`); o texto do stderr volta para o Claude |
| Outro código | Erro que não bloqueia; o usuário vê um aviso |

Os quatro scripts estão em Node.js para funcionar igual no Windows, no macOS e no Linux, sem depender de `jq`.

- **[contexto-inicial.mjs](.claude/hooks/contexto-inicial.mjs)** (`SessionStart`): no início da sessão, tudo o que o hook imprime entra no contexto. Ele imprime a feature da vez e a última entrada de `progresso.md`, adiantando a rotina de início do `CLAUDE.md`.
- **[bloquear-comandos.mjs](.claude/hooks/bloquear-comandos.mjs)** (`PreToolUse`, `Bash`): antes de cada comando, faz uma de duas coisas:
  - **bloqueia** com `exit 2` o `rm` recursivo apontado para a raiz ou para a pasta do usuário (em formas como `rm -rf /`, `rm -r -f ~/` e `rm -rf $HOME/*`), push forçado, `curl ... | sh` e `DROP TABLE`/`DROP DATABASE`;
  - **pede confirmação** com JSON de `permissionDecision: "ask"` para `git reset --hard` e `alembic downgrade`.

  Os padrões são ilustrativos e comparam texto, então têm brechas e falsos positivos:
  - um script pode apagar a mesma pasta sem que o comando cite `rm`;
  - `grep "DROP TABLE" migrations/` é bloqueado sem motivo;
  - `git push --force-with-lease` também é bloqueado.

  Por isso o hook é uma camada a mais, junto com o `ask` de `rm -rf` e o sandbox, e não a única.
- **[proteger-arquivos.mjs](.claude/hooks/proteger-arquivos.mjs)** (`PreToolUse`, `Edit|Write`):
  - recusa editar `.env*` (exceto `.env.example`) e qualquer coisa em `.git/`;
  - recusa editar uma migração **já commitada**, conferindo com `git cat-file -e HEAD:<arquivo>`. Uma migração gerada por `alembic revision` e ainda não commitada continua editável, para o agente preencher o `upgrade` e o `downgrade`.

  Essa diferença, entre uma migração já aplicada e uma nova, uma regra de permissão por caminho não consegue expressar; um hook consegue. O hook só vê as ferramentas `Edit` e `Write`: um comando de terminal ou um script ainda poderia alterar o arquivo. É um bloqueio das ferramentas de edição, não do sistema de arquivos.
- **[lint-apos-edicao.mjs](.claude/hooks/lint-apos-edicao.mjs)** (`PostToolUse`, `Edit|Write`): depois de cada edição de `.py`, faz duas checagens:
  - procura `float` em `app/servicos/`, por texto simples, ignorando só as linhas que são inteiras comentário;
  - roda `ruff check` no arquivo.

  Como a edição já aconteceu, o `exit 2` não desfaz nada: devolve os problemas para o Claude corrigir no passo seguinte. Se o `ruff` não estiver instalado, essa etapa é pulada em silêncio e o hook não bloqueia.

### Subagentes: `.claude/agents/`

- **[revisor.md](.claude/agents/revisor.md)** é o mesmo revisor do enxuto, com uma lista do que procurar e a classificação **grave** ou **melhoria**, que a skill `/nova-feature` usa para decidir se pode concluir. Como no enxuto, ele não tem as ferramentas de edição, mas tem `Bash` para rodar os testes; não escrever por comandos de terminal é uma instrução dele, não um bloqueio.
- **[explorador.md](.claude/agents/explorador.md)** investiga o código e devolve um resumo de no máximo 20 linhas. Ele usa `model: haiku`, um modelo menor e mais barato, e só ferramentas de leitura. O ganho é de contexto: os arquivos que ele lê ficam no contexto dele, e só o resumo volta para a conversa principal.

### Skills: `.claude/skills/`

- **[nova-feature](.claude/skills/nova-feature/SKILL.md):** o ciclo planejar, executar e verificar, amarrado aos artefatos de estado.
  - A linha ``!`git status --short` `` é **injeção de contexto dinâmico**: o comando roda antes de o Claude ler a skill, e a saída substitui a linha.
  - A feature só muda para `concluida` depois de testes, verificação com evidência e revisão.
- **[revisar](.claude/skills/revisar/SKILL.md):** `context: fork` com `agent: revisor` faz a skill rodar em um subagente separado, do tipo `revisor`, com as ferramentas dele. É o mesmo mecanismo que este repositório usa no `/revisar-documentacao`.
- **[registrar-incidente](.claude/skills/registrar-incidente/SKILL.md):** o ciclo do fix permanente em forma de procedimento.
  - Escolhe o nível do fix (instrução, sensor ou bloqueio), prova que funciona e registra em `incidentes.md`.
  - `disable-model-invocation: true` impede que o Claude a acione sozinho: registrar incidente é decisão de quem usa.

### Continuidade entre sessões

Estes três arquivos seguem a ideia descrita pela Anthropic em *Effective harnesses for long-running agents*: cada sessão começa sem memória da anterior, então o estado precisa estar em arquivos que a próxima sessão lê.

- **[feature_list.json](feature_list.json)** é o **escopo verificável**.
  - Cada feature tem prioridade, passos de verificação, `status` (`pendente`, `em_andamento` ou `concluida`) e `evidencia`.
  - Uma feature só é concluída com evidência registrada, e só uma fica em andamento por vez.
  - O formato JSON, em vez de texto livre, dificulta que o agente reescreva o escopo sem perceber.
- **[progresso.md](progresso.md)** é o **log de sessões**: o que foi feito, como foi verificado e o próximo passo, da entrada mais recente para a mais antiga.
- **[init.sh](init.sh)** é o **ritual de início**.
  - Instala dependências, roda o lint e roda os testes.
  - `set -euo pipefail` faz qualquer falha interromper o script, então um ambiente quebrado aparece antes de a feature começar, e não no meio dela.

### Integrações e git

- **[.mcp.json](.mcp.json)** declara servidores MCP compartilhados pelo time. O servidor `docs-internos` é **ilustrativo**: não existe.
  - `${DOCS_MCP_URL}` e `${DOCS_MCP_TOKEN}` são lidos das variáveis de ambiente de cada pessoa, e o token nunca fica no arquivo.
  - O Claude Code pede aprovação antes de usar um servidor declarado em `.mcp.json`.
- **[.gitignore](.gitignore)** mantém fora do git os segredos e a configuração pessoal (`.claude/settings.local.json` e `CLAUDE.local.md`), que cada pessoa pode ter sem afetar o time.

## Verificação feita

- **JSON:** todos os arquivos JSON do exemplo (`settings.json`, `feature_list.json`, `.mcp.json`) foram validados com Node.js.
- **Hooks:** os quatro scripts foram executados com eventos simulados na entrada padrão, em um projeto de teste com repositório git, `feature_list.json`, `progresso.md`, uma migração commitada, uma migração nova não commitada e um serviço com `float`. Os resultados conferiram com o esperado:
  - `bloquear-comandos.mjs`:
    - deixou passar `pytest -q`, `rm -rf build/`, `rm -rf ./tmp`, `rm -rf ~/projeto` e `rm arquivo.txt`;
    - bloqueou `rm -rf /`, `rm -rf ~`, `rm -rf ~/`, `rm -rf /*`, `rm -rf $HOME/`, `rm -rf ${HOME}`, `rm -r -f /`, `rm --recursive --force /` e `rm -rf / && echo x`;
    - bloqueou push forçado, `curl ... | bash` e `DROP TABLE`;
    - pediu confirmação para `git reset --hard`.
  - `proteger-arquivos.mjs`:
    - bloqueou `.env`, `.env.producao`, `.git/config` e a migração commitada;
    - liberou `.env.example`, a migração nova ainda não commitada e um arquivo de serviço.
  - `lint-apos-edicao.mjs` apontou o `float` da linha de código e ignorou a linha de comentário.
  - `contexto-inicial.mjs` imprimiu a feature FAT-002 e a última entrada do progresso.
- **Não verificado:** o lint com `ruff` (a ferramenta não estava instalada), o `init.sh` (depende do projeto real) e o comportamento dentro de uma sessão do Claude Code. A primeira sessão real deve confirmar esses pontos com `/status` e `/hooks`.

## Como usar em um projeto real

1. Comece pelo [harness enxuto](../claude-enxuto/README.md) e traga peças deste exemplo à medida que os incidentes pedirem.
2. Copie os arquivos para a raiz do repositório e troque comandos, pastas, regras e padrões dos hooks pelos do seu projeto.
3. Os hooks exigem Node.js instalado. Confira com `/hooks` se foram registrados.
4. No Windows nativo, retire a seção `sandbox` ou rode o Claude Code no WSL2.

## Limpeza

O exemplo não cria recursos externos. Para remover o harness, apague `CLAUDE.md`, `.claude/`, `.mcp.json` e os artefatos de estado (`feature_list.json`, `progresso.md`, `init.sh`). Aprovações de servidores MCP podem ser reiniciadas com `claude mcp reset-project-choices`.
