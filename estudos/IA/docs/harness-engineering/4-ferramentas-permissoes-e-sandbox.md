# 4. Ferramentas, permissões e isolamento

As ferramentas são o ponto em que o agente sai do texto e afeta o mundo: edita arquivos, roda comandos, consulta APIs. É também onde os erros têm consequência real. Esta parte do harness responde a duas perguntas: como desenhar ferramentas que o modelo use corretamente, e como garantir que, mesmo quando ele erra, o dano fique contido.

A mecânica de tool calling (schema, executor e devolução do resultado ao modelo) está em [5.3 Tooling](../context-engineering/5-camada-em-arquitetura-llm.md#_5-3-tooling-como-um-agente-usa-ferramentas), na trilha de Context Engineering. Aqui o foco é o desenho das ferramentas e a governança em volta delas.

## 4.1 Termos e definições

**Ferramenta:** função exposta ao modelo por meio de um schema (nome, descrição e parâmetros) e executada pelo harness quando o modelo pede.

**Menor privilégio:** dar ao agente só o acesso de que a tarefa precisa. Um agente que só lê não recebe permissão de escrita; um agente que trabalha em um projeto não acessa pastas fora dele.

**Permissão:** regra que decide se uma chamada de ferramenta roda direto, pede confirmação ou é recusada.

**Hook:** comando que o harness executa automaticamente em um evento, como antes ou depois de uma chamada de ferramenta, e que pode bloquear, modificar ou complementar o fluxo.

**Sandbox:** isolamento imposto pelo sistema operacional, que limita o que um processo pode ler, escrever e acessar na rede, qualquer que seja o comando.

**MCP (Model Context Protocol):** protocolo aberto que padroniza como um agente descobre e chama ferramentas e fontes de dados expostas por servidores externos.

## 4.2 Desenhando ferramentas

O modelo escolhe e usa uma ferramenta a partir do que está escrito no schema. Algumas práticas reduzem os erros de escolha e de parâmetro:

- **Nome descritivo e específico:** `consultar_fatura` em vez de `get` ou `processar`.
- **Descrição que diz quando usar e quando não usar.** A segunda parte é a mais esquecida e a que mais evita chamadas erradas: "não use para criar faturas; para isso, use `emitir_fatura`".
- **Restrições no schema, não só na descrição.** Formato com `pattern`, valores possíveis com `enum`, limites de tamanho. O executor valida antes de rodar e devolve o erro ao modelo se a validação falhar.
- **Uma responsabilidade por ferramenta.** Ferramentas pequenas e específicas são escolhidas com mais acerto do que uma ferramenta que faz tudo.
- **Erro como informação.** Uma falha da ferramenta volta ao modelo como resultado legível ("fatura 999 não encontrada; confirme o número"), para ele poder reagir, em vez de derrubar o loop.

Ferramentas que apagam, enviam, publicam ou cobram merecem camadas extras: confirmação humana, ou uma janela de reversão (exclusão lógica que pode ser desfeita por um tempo).

## 4.3 Camadas de proteção

Nenhum controle sozinho é suficiente, porque cada um falha de um jeito. A abordagem é a de defesa em profundidade, herdada da segurança da informação: várias camadas, cada uma cobrindo uma falha diferente.

| Camada | O que impede | Exemplo no Claude Code |
|---|---|---|
| Ferramentas disponíveis | O agente nem vê a ferramenta | Lista `tools` de um subagente; regra `deny` com o nome da ferramenta |
| Permissões por padrão | Comandos e caminhos específicos | `allow`, `ask` e `deny` no `settings.json` |
| Hooks | Casos que dependem de lógica | Hook `PreToolUse` que recusa editar uma migração que já existe |
| Sandbox | Acesso a arquivos e rede, qualquer que seja o comando | `sandbox.enabled` com lista de domínios permitidos |
| Aprovação humana | Ações irreversíveis | Regras em `ask`, que pedem confirmação a cada vez |

Para agentes que rodam sem supervisão, como em pipelines de CI, entra ainda a camada de infraestrutura: um container descartável por execução, sem credenciais além das necessárias e com saída de rede restrita.

## 4.4 Permissões na prática

No Claude Code, as permissões ficam em `.claude/settings.json` (versionado, vale para o time) e podem ser complementadas em `.claude/settings.local.json` (pessoal, fora do git). As regras são avaliadas na ordem **deny, ask, allow**, e a primeira que casar decide, independentemente de qual é mais específica.

```json
{
  "permissions": {
    "allow": ["Bash(pytest *)", "Edit(/app/**)"],
    "ask": ["Bash(git commit *)", "Edit(/migrations/**)"],
    "deny": ["Read(.env)", "Read(.env.*)", "Bash(git push *)"]
  }
}
```

Leitura do exemplo:

- `Bash(pytest *)` libera qualquer execução de `pytest`, com ou sem argumentos;
- `Edit(/app/**)` libera edições em `app/` (a `/` inicial ancora na raiz do projeto);
- os `deny` impedem ler arquivos de segredos e fazer push. Um padrão que começa com `!` abre uma exceção às regras de caminho listadas antes dele no mesmo arquivo: `Read(!.env.example)` depois de `Read(.env.*)` mantém o arquivo de exemplo legível.

Os limites dessas regras precisam ser conhecidos para não gerar falsa segurança:

- **Regras de Bash comparam o texto do comando.** O Claude Code reconhece operadores como `&&` e `|`, e uma regra `allow` não libera um comando composto se alguma parte dele não estiver liberada. Mesmo assim, a documentação avisa que uma regra `deny` cobre a forma como o comando costuma ser escrito, não o programa em si: o mesmo efeito pode vir por outro caminho, como um script.
- **Regras de `Read` e `Edit` cobrem as ferramentas de arquivo e comandos reconhecidos** como `cat` e `head`. Elas não cobrem um script Python que abre o arquivo por conta própria.
- **Para garantia no nível do sistema operacional, o caminho é o sandbox.**

## 4.5 Hooks como portão

Hooks preenchem o espaço entre a permissão (padrões fixos) e o sandbox (isolamento amplo): eles rodam código seu em cada evento, com acesso aos detalhes da chamada.

No Claude Code, o hook recebe o evento em JSON pela entrada padrão, incluindo `tool_name` e `tool_input`. O código de saída define o efeito:

| Saída do hook | Efeito |
|---|---|
| `exit 0` | Segue o fluxo normal de permissões |
| `exit 2` | Bloqueia a chamada (em `PreToolUse`) e devolve o texto do stderr ao Claude como motivo |
| `exit 0` com JSON `permissionDecision` | Decide explicitamente: permitir, negar ou perguntar ao usuário |
| Outro código | Erro não bloqueante: a ação segue e o usuário vê um aviso |

Um cuidado: o código de saída 1, o padrão de erro no Unix, **não bloqueia**. Para impor uma política, o hook precisa sair com 2.

Dois exemplos do que só um hook expressa bem:

- recusar a edição de uma migração que **já existe**, mas permitir criar uma nova;
- depois de cada edição, rodar o lint no arquivo alterado e devolver os problemas ao agente para correção imediata.

Os dois estão implementados e testados no [exemplo completo](exemplos/claude-completo/README.md).

## 4.6 Sandbox

O sandbox do Claude Code isola os comandos de terminal no nível do sistema operacional:

- **Escrita:** restrita, por padrão, à pasta do projeto (e subpastas), às pastas adicionadas à sessão e à pasta temporária do usuário.
- **Rede:** passa por um proxy que só deixa sair para os domínios listados em `sandbox.network.allowedDomains`. Conexões com serviços da própria máquina, como um banco local, ficam bloqueadas por padrão; comandos que precisam delas podem ir para `sandbox.excludedCommands`, que os roda fora do sandbox e ainda pelo fluxo de permissões.

Como a restrição não depende do texto do comando, vale também para scripts e subprocessos. Com o sandbox ligado, comandos isolados rodam sem perguntar, mas as regras `ask` e `deny` com conteúdo, como `Bash(git push *)`, continuam valendo.

```json
{
  "sandbox": {
    "enabled": true,
    "network": { "allowedDomains": ["pypi.org", "files.pythonhosted.org"] }
  }
}
```

Ele tem limites de alcance que vale anotar (verificados na documentação em 2026-10-28):

- funciona no macOS, no Linux e no WSL2, mas **não no Windows nativo**, onde os comandos rodam sem isolamento;
- cobre os comandos de terminal; as ferramentas de arquivo embutidas, os servidores MCP e os hooks rodam fora dele;
- por padrão, a maior parte da máquina continua legível. Bloquear a leitura de pastas como `~/.ssh` exige configurar `sandbox.filesystem.denyRead`.

## 4.7 MCP: padroniza a interface, não a segurança

O MCP resolve um problema de integração: em vez de escrever um adaptador para cada combinação de agente e serviço, o serviço expõe um servidor MCP uma vez e qualquer cliente compatível o usa. No Claude Code, servidores compartilhados pelo time ficam em `.mcp.json` na raiz do projeto, e credenciais entram por variáveis de ambiente (`${API_KEY}`), nunca escritas no arquivo.

O protocolo define **como** as ferramentas são descobertas e chamadas, não **se** devem ser usadas. Cada servidor MCP acrescenta ferramentas ao agente, e cada ferramenta nova precisa da mesma governança das outras: permissões (as ferramentas aparecem como `mcp__<servidor>__<ferramenta>`), confirmação para o que é destrutivo e desconfiança sobre o conteúdo que o servidor devolve, que pode trazer instruções maliciosas embutidas. O Claude Code pede aprovação antes de usar servidores declarados no `.mcp.json` de um projeto.

## 4.8 Resumo

Ferramentas bem desenhadas têm nome específico, descrição que diz quando não usar, restrições no schema e erros legíveis. Como nenhum controle é suficiente sozinho, a governança empilha camadas: ferramentas disponíveis, permissões, hooks, sandbox e aprovação humana. Permissões por padrão de comando têm brechas conhecidas; hooks resolvem casos que dependem de lógica; o sandbox impõe limites no nível do sistema operacional, onde ele é suportado. O MCP facilita a integração, mas cada ferramenta que ele traz entra sob as mesmas regras.

## Fontes

- Claude Code, documentação oficial de [permissões](https://code.claude.com/docs/en/permissions), [hooks](https://code.claude.com/docs/en/hooks), [sandbox](https://code.claude.com/docs/en/sandboxing) e [MCP](https://code.claude.com/docs/en/mcp), consultado em 2026-10-28.
