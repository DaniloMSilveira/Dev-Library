# Harness enxuto para o Claude Code

Estrutura mínima de harness para um projeto que usa o Claude Code. Cada arquivo cobre uma parte do harness descrita na trilha: instruções, memória, permissões, regras por caminho, um subagente e uma skill. É o ponto de partida recomendado: comece por aqui e acrescente peças quando um erro real pedir, como mostra a versão [completa](../claude-completo/README.md).

O projeto é **fictício**: uma API de faturas em Python (FastAPI e PostgreSQL). Só os arquivos do harness existem aqui; o código da aplicação (`app/`, `tests/`, `migrations/`) não faz parte do exemplo. Datas, decisões e incidentes são ilustrativos. A explicação conceitual está em [6. Montando um harness no Claude Code](../../6-harness-no-claude-code.md).

## Estrutura

```text
claude-enxuto/
├── CLAUDE.md                     # instruções gerais, lidas em toda sessão
└── .claude/
    ├── settings.json             # permissões: o que roda sem perguntar, o que pergunta, o que é bloqueado
    ├── memoria.md                # decisões e incidentes do time, importados pelo CLAUDE.md
    ├── rules/
    │   └── testes.md             # regra que só entra no contexto ao mexer em tests/
    ├── agents/
    │   └── revisor.md            # subagente que revisa mudanças sem poder editar
    └── skills/
        └── nova-feature/
            └── SKILL.md          # procedimento /nova-feature: planejar, testar, implementar, verificar
```

## O que cada arquivo faz

### `CLAUDE.md`

[CLAUDE.md](CLAUDE.md) fica na raiz do projeto e é carregado no início de toda sessão. É o principal **guide** do harness: diz ao agente o que é o projeto, como rodar, onde fica cada coisa e o que não fazer. Por isso traz comandos literais (`pytest`, `ruff check .`) em vez de descrições, e regras numeradas e verificáveis em vez de conselhos genéricos.

A linha `@.claude/memoria.md` é um **import**: o conteúdo do arquivo citado é carregado junto com o `CLAUDE.md`. O import organiza, mas não economiza contexto, porque o arquivo importado entra inteiro.

Cuidado: o `CLAUDE.md` orienta, não obriga. O Claude o trata como contexto, e uma regra escrita aqui pode ser descumprida. Por isso as regras com consequência séria também aparecem no `settings.json`.

### `.claude/settings.json`

[settings.json](.claude/settings.json) é a camada de **governança**. Versionado no repositório, vale para todo o time. As regras são avaliadas na ordem `deny`, depois `ask`, depois `allow`, e a primeira que casar decide:

| Lista | O que faz | Neste exemplo |
|---|---|---|
| `allow` | Executa sem perguntar | Rodar testes e lint; editar `app/` e `tests/` |
| `ask` | Pede confirmação a cada vez | Commit, instalar pacote, editar `migrations/` |
| `deny` | Recusa sempre | Ler `.env` (exceto `.env.example`), `git push`, `rm -rf` |

Detalhes de sintaxe:

- `Bash(pytest *)`: o `*` cobre qualquer argumento, então vale para `pytest` e para `pytest tests/api`.
- `Bash(ruff check .)`: sem `*`, a regra vale só para esse comando exato. Um `Bash(ruff check *)` também liberaria `ruff check --fix`, que reescreve arquivos sem perguntar.
- `Edit(/app/**)`: a `/` inicial ancora o caminho na raiz do projeto.
- `Read(!.env.example)`: o `!` abre uma exceção para as regras `deny` listadas antes dele.

Limites que vale conhecer:

- As regras de `Bash` comparam o texto do comando. Elas não impedem o mesmo efeito por outro caminho, como um script Python que apaga arquivos.
- Os `allow` de um arquivo versionado só valem depois que cada pessoa confia na pasta do projeto. Já os `deny` e `ask` valem desde o início.
- No Windows, o Claude Code pode usar a ferramenta PowerShell em vez de Bash, e regras `Bash(...)` não cobrem comandos `PowerShell(...)`. Em times com Windows, repita as regras para os dois.

### `.claude/memoria.md`

[memoria.md](.claude/memoria.md) é a **memória do projeto**: decisões e incidentes que não aparecem no código, escritos pelo time e versionados. Está separada do `CLAUDE.md` para que as instruções continuem curtas e as decisões tenham um lugar próprio para crescer.

O incidente registrado mostra o **fix permanente** em ação: depois que o agente editou uma migração aplicada, o time criou uma regra no `CLAUDE.md` (guide) e passou a exigir confirmação para editar `migrations/` (governança).

Ela não é a memória automática do Claude Code. A memória automática é escrita pelo próprio Claude, fica na máquina de cada pessoa (`~/.claude/projects/<projeto>/memory/`) e não é versionada. As duas convivem: esta é do time, a automática é individual.

### `.claude/rules/testes.md`

[testes.md](.claude/rules/testes.md) é uma **regra por caminho**. O campo `paths` no início do arquivo faz com que ela só entre no contexto quando o Claude ler ou editar um arquivo que case com `tests/**/*.py`. Assim, instruções que valem para uma parte do código não ocupam contexto o tempo todo. Uma regra sem `paths` seria carregada sempre, como o `CLAUDE.md`.

### `.claude/agents/revisor.md`

[revisor.md](.claude/agents/revisor.md) define um **subagente**: um agente com contexto próprio, prompt próprio e ferramentas limitadas.

- `name` e `description` são obrigatórios. A descrição é o que o Claude lê para decidir quando delegar a revisão.
- `tools: Read, Grep, Glob, Bash` é uma lista fechada. Sem `Edit` e `Write`, o revisor não tem as ferramentas de edição, e isso é estrutural.
- Mas ele tem `Bash`, de que precisa para rodar `pytest`. Por comandos de terminal, ainda conseguiria escrever em arquivos (com `sed -i` ou um redirecionamento `>`, por exemplo), e só pediria confirmação porque esses comandos não estão no `allow`. A frase "use Bash só para leitura" no prompt é um guide, não um bloqueio. Para um revisor que estruturalmente não escreve, tire o `Bash` da lista; o custo é ele não poder rodar os testes.
- `model: sonnet` escolhe o modelo do subagente.

A revisão roda em contexto separado e devolve só o resultado. Assim, quem revisa não carrega o raciocínio de quem escreveu, e os arquivos lidos na revisão não ocupam o contexto principal.

### `.claude/skills/nova-feature/SKILL.md`

[SKILL.md](.claude/skills/nova-feature/SKILL.md) é uma **skill**: um procedimento que pode ser chamado com `/nova-feature descrição da feature` ou carregado pelo Claude quando a `description` combinar com o pedido. O `$ARGUMENTS` recebe o texto digitado depois do comando.

O procedimento segue planejar, executar e verificar: testes antes, implementação, `pytest` e `ruff`, revisão pelo subagente e relato do que foi rodado. Só o nome e a descrição ficam no contexto o tempo todo; o corpo da skill é carregado quando ela é usada.

## Como usar em um projeto real

1. Copie `CLAUDE.md` e a pasta `.claude/` para a raiz do seu repositório.
2. Troque nomes, comandos, pastas e regras pelos do seu projeto. Não mantenha regras que você não verifica.
3. Abra o Claude Code na raiz do projeto e confira o que foi carregado:
   - `/status` lista os arquivos de configuração lidos;
   - `/memory` mostra os arquivos de instrução e memória;
   - o menu `/` mostra a skill `/nova-feature`;
   - para testar o subagente, peça uma revisão citando o nome dele ("use o revisor para revisar as mudanças").
4. Use por algumas semanas. Cada erro do agente que poderia ter sido evitado vira uma linha em `memoria.md` e uma correção em um destes arquivos.

## Limpeza

O exemplo não cria recursos externos. Para remover o harness de um projeto, apague `CLAUDE.md` e a pasta `.claude/`. Configurações pessoais ficam em `.claude/settings.local.json` e `CLAUDE.local.md`, que não fazem parte deste exemplo.
