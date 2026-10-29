# 2. Guides e sensors: orientar antes, verificar depois

Um harness tem muitas peças, mas quase todas cumprem um de dois papéis: orientar o agente **antes** de ele agir, ou verificar o resultado **depois**. Böckeler chama as primeiras de *guides* e as segundas de *sensors*. A distinção ajuda a decidir, diante de um problema, que tipo de controle construir.

Esta página define os dois tipos, mostra por que um não substitui o outro, separa controles determinísticos de controles baseados em modelo e apresenta a hierarquia que orienta o fix permanente da [página 1](1-o-que-e-harness.md#_1-5-o-fix-permanente).

## 2.1 Termos e definições

**Guide (controle feedforward):** atua antes da ação, aumentando a chance de o agente acertar de primeira. Exemplos: o `CLAUDE.md`, as regras do projeto, a descrição de uma ferramenta, um exemplo de saída esperada.

**Sensor (controle de feedback):** atua depois da ação, observando o resultado e permitindo correção. Exemplos: testes, lint, checagem de tipos, validação de schema, revisão por outro agente, aprovação humana.

**Controle computacional:** determinístico, rápido e barato, roda como código comum. Testes, linters, type checkers e análises estruturais.

**Controle inferencial:** usa um modelo para julgar algo que código não captura bem, como "esta mudança resolve o que a tarefa pedia?". Mais lento, mais caro e não determinístico.

**Bloqueio estrutural:** um controle que impede a ação antes de ela acontecer, independentemente do que o modelo decidiu. Permissões negadas, hooks que recusam a chamada e isolamento do sistema operacional.

## 2.2 Por que precisa dos dois

Os dois tipos falham de formas complementares:

- **Só guides:** o agente recebe boas instruções, mas ninguém confere se ele as seguiu. As regras viram expectativa, não garantia.
- **Só sensors:** os erros são pegos, mas o agente continua cometendo os mesmos, porque nada mudou no que ele sabe antes de agir. O resultado é retrabalho constante.

Na prática, guides reduzem a quantidade de erros e sensors pegam os que sobram. O artigo de Böckeler acrescenta um detalhe útil: sensors funcionam melhor quando a mensagem de erro é escrita para o modelo ler, dizendo o que está errado e o que fazer, em vez de só reprovar.

## 2.3 Persuadir não é impor

Uma instrução, por mais clara que seja, entra no contexto do modelo como texto. A documentação do Claude Code é explícita: o `CLAUDE.md` e a memória são tratados como contexto, não como configuração imposta, e para bloquear uma ação independentemente do que o Claude decidir, o caminho é um hook `PreToolUse`.

Daí uma regra de decisão:

| O que você precisa | Tipo de controle | Exemplo |
|---|---|---|
| Que algo fique **mais provável** | Guide | "Use `Decimal` para valores monetários" no `CLAUDE.md` |
| **Perceber** quando algo dá errado | Sensor | Teste que falha se aparecer `float` no cálculo de juros |
| Que algo **não aconteça** | Bloqueio estrutural | Permissão `deny` para `git push`, hook que recusa editar `.env` |

Ações reversíveis (renomear uma variável, reorganizar um texto) podem viver só com guides e sensors. Ações irreversíveis ou com efeito fora do repositório (apagar dados, publicar, pagar, enviar mensagem a cliente) pedem bloqueio ou aprovação humana.

## 2.4 Computacional antes de inferencial

Entre os sensors, a ordem importa. Controles computacionais são baratos e confiáveis, então rodam primeiro e barram o que conseguem. Os inferenciais, como revisão por outro modelo, ficam para o que código não consegue julgar.

```text
saída do agente
   │
   ├─► schema / tipos ........ computacional, milissegundos
   ├─► lint .................. computacional, segundos
   ├─► testes ................ computacional, segundos a minutos
   ├─► revisão por modelo .... inferencial, custo de tokens
   └─► aprovação humana ...... só para o que é irreversível ou de alto risco
```

Cada etapa só roda se a anterior passou. Não faz sentido pagar uma revisão por modelo de um código que nem compila. A [página 5](5-verificacao-e-evolucao.md) detalha esse encadeamento.

Böckeler também agrupa os controles pelo que eles regulam:

| Categoria | O que regula | Situação descrita no artigo |
|---|---|---|
| Manutenibilidade | Qualidade interna do código | A mais fácil de construir, porque linters e analisadores já existem |
| Adequação à arquitetura | Características como desempenho e padrões de log | Usa a ideia de *fitness functions*: testes que verificam propriedades da arquitetura |
| Comportamento | Se a aplicação faz o que deveria | O ponto mais difícil; testes gerados pelo próprio agente ainda não bastam |

## 2.5 A hierarquia de fixes

Quando o agente erra, a pergunta da [página 1](1-o-que-e-harness.md) é em que nível corrigir. Uma heurística útil, usada como recomendação e não como regra fixa:

1. **Primeira ocorrência, por falta de informação:** um guide. Talvez o agente simplesmente não soubesse. Uma linha no `CLAUDE.md` ou em uma regra resolve.
2. **O erro se repetiu apesar do guide:** um sensor. A instrução não bastou, então o erro precisa ser detectado automaticamente.
3. **O erro é grave ou se repetiu apesar do sensor:** um bloqueio estrutural. A ação deixa de ser possível.

Um efeito colateral desejável: com o tempo, o arquivo de instruções fica mais curto, porque as regras que mais importam viraram sensors e bloqueios e não precisam mais depender só do texto.

O [exemplo completo](exemplos/claude-completo/README.md) registra três incidentes, um em cada nível, no arquivo `.claude/memoria/incidentes.md`.

## 2.6 Limites e trade-offs

- **Sensors demais tornam o agente lento.** Cada verificação acrescenta tempo a cada passo. Coloque as caras no fim do fluxo, não em cada edição.
- **Bloqueios por texto de comando têm brechas.** Uma regra que nega `rm -rf` compara o texto do comando, e o mesmo efeito pode vir de um script. Para garantia no nível do sistema, é preciso isolamento (ver a [página 4](4-ferramentas-permissoes-e-sandbox.md)).
- **Sensors inferenciais erram.** Um modelo revisando outro pode aprovar o que está errado ou reprovar o que está certo. Use-os como apoio, não como única barreira para o que é crítico.
- **Bloqueio demais impede trabalho.** Se o agente precisa de confirmação para tudo, as pessoas passam a aprovar sem ler. Reserve o bloqueio e a aprovação para o que de fato tem risco.

## 2.7 Resumo

Guides orientam o agente antes de agir e sensors verificam depois; um sem o outro deixa erros passarem ou se repetirem. Instruções persuadem, mas não impõem: o que não pode acontecer precisa de bloqueio estrutural. Entre os sensors, os computacionais vêm antes dos inferenciais, por custo e confiabilidade. Diante de um erro, corrige-se no nível mais baixo que resolve e sobe-se na hierarquia (instrução, sensor, bloqueio) quando o erro se repete ou é grave.

## Fontes

- Birgitta Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html), martinfowler.com, 2026-04-02, consultado em 2026-10-28.
- Claude Code, [How Claude remembers your project](https://code.claude.com/docs/en/memory), documentação oficial, consultado em 2026-10-28.
