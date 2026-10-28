# 6. Supervisor: coordenar especialistas

Supervisor é o padrão em que um agente coordenador decide, a cada passo, qual agente especializado (worker) deve trabalhar a seguir, e quando o trabalho está pronto. O supervisor não produz o conteúdo da tarefa: ele distribui, acompanha e encerra.

Esta página explica o papel do supervisor e dos workers, mostra o loop de coordenação e lista os erros de projeto mais comuns. Ela compara o padrão com [Planning](4-planning.md) e [Router](5-router.md), que também decidem "quem faz o quê", mas de outro jeito.

## 6.1 Termos e definições

**Supervisor:** o agente que lê o objetivo e o histórico de execução e devolve uma decisão: qual worker chamar, com qual instrução, ou encerrar.

**Worker:** um agente ou função especializada em um tipo de tarefa (pesquisar, consultar dados, redigir). Pode ser um agente ReAct com ferramentas, uma única chamada a um modelo ou um sistema legado encapsulado.

**Histórico de execução:** o registro das decisões do supervisor e dos resultados dos workers até o momento. É o contexto com que o supervisor decide o próximo passo.

O nome "supervisor" é usado, por exemplo, no ecossistema LangGraph, que tem um pacote `langgraph-supervisor` para esse arranjo, inclusive com supervisores aninhados. A Anthropic descreve um arranjo próximo como *orchestrator-workers*: um LLM central quebra a tarefa, delega subtarefas a workers e **ele mesmo sintetiza** os resultados. Nesta página, a síntese fica com um worker próprio (o redator), e o supervisor só decide. As duas variantes existem; a que separa decisão e conteúdo tem um papel mais estreito e mais fácil de controlar, como discutido na seção 6.4.

## 6.2 Como funciona

```text
                    supervisor ◄──────────────────────┐
             (próximo worker ou FIM)                  │
                        │                             │
     ┌───────────┬──────┴─────┬───────────┐           │
     ▼           ▼            ▼           ▼           │
 cadastro    financeiro   contratos    redator        │
     │           │            │           │           │
     └───────────┴────────────┴───────────┴─resultado─┘
```

A diferença para o Planning está em **quando** as decisões são tomadas. No Planning, o plano inteiro é decidido antes. No Supervisor, a decisão é iterativa: depois de cada resultado, o supervisor olha o que chegou e escolhe o próximo passo. Isso torna o padrão adequado quando não dá para prever o caminho, porque ele depende do que cada worker encontrar.

### Workers como caixas-pretas

O supervisor só precisa saber **que tipo de tarefa** cada worker resolve, não como ele resolve. Para isso, todos os workers seguem o mesmo contrato: recebem uma instrução em texto e devolvem um resultado em texto (ou em um formato estruturado comum). Com o contrato uniforme, adicionar, trocar ou remover um worker não exige reescrever o supervisor; basta atualizar a lista de workers e suas descrições.

## 6.3 Exemplo concreto

Objetivo: "avaliar se o fornecedor Alfa pode ter o limite de compra aumentado". Os workers disponíveis:

| Worker | Especialidade |
|---|---|
| `cadastro` | Situação cadastral e dados da empresa |
| `financeiro` | Histórico de pagamentos e pendências |
| `contratos` | Cláusulas dos contratos vigentes (busca em documentos) |
| `redator` | Parecer final para a área de compras |

Uma execução possível: o supervisor chama `cadastro`; a situação está regular. Chama `financeiro`, que encontra duas notas em disputa. Por causa disso, chama `contratos` para ver o que o contrato diz sobre disputas. Por fim, chama `redator`. Se o histórico financeiro estivesse limpo, ele poderia ter pulado `contratos`. Essa adaptação é o que o Planning, com o plano fixado antes, não faz sem replanejar.

```python
# Ilustrativo: loop do supervisor com decisão estruturada e salvaguardas.
from typing import Literal
from pydantic import BaseModel

WORKERS = {
    "cadastro": worker_cadastro,
    "financeiro": worker_financeiro,
    "contratos": worker_contratos,
    "redator": worker_redator,
}

class Decisao(BaseModel):
    proximo: Literal["cadastro", "financeiro", "contratos", "redator", "FIM"]
    instrucao: str
    justificativa: str

def supervisionar(objetivo: str, max_passos: int = 8) -> list[dict]:
    historico: list[dict] = []
    for _ in range(max_passos):
        decisao = Decisao(**decidir_proximo(objetivo, historico))  # chamada ao LLM supervisor

        if decisao.proximo == "FIM":
            break

        ultimas = [(h["worker"], h["instrucao"]) for h in historico[-2:]]
        if ultimas.count((decisao.proximo, decisao.instrucao)) == 2:
            historico.append({"worker": "sistema", "instrucao": "", "resultado": "Execução interrompida: decisão repetida."})
            break

        resultado = WORKERS[decisao.proximo](decisao.instrucao)
        historico.append({"worker": decisao.proximo, "instrucao": decisao.instrucao, "resultado": resultado})
    return historico
```

O `Literal` no schema impede que o supervisor invente um worker. O limite de passos e a detecção de decisão repetida param execuções que não progridem. O campo `justificativa` não é usado pelo código, mas vai para o log, o que torna cada decisão auditável.

## 6.4 Erros de projeto comuns

- **Supervisor que executa.** Se o prompt do supervisor permite que ele responda conteúdo, ele tende a "resolver sozinho" em vez de delegar, sem as ferramentas e o contexto do worker certo. Restrinja a saída dele ao schema de decisão.
- **Supervisor sobrecarregado.** Quanto mais decisões o supervisor acumula (validar, corrigir, resumir, formatar), mais longo fica o prompt dele e mais cara cada volta. Mantenha o papel dele restrito a escolher o próximo worker e encerrar.
- **Workers demais.** Com muitos workers de descrições parecidas, o prompt cresce e a chance de escolha errada aumenta. Quando a lista ficar difícil de distinguir, agrupe os workers em equipes, cada uma com seu próprio supervisor, abaixo de um supervisor geral (hierarquia de supervisores).
- **Histórico que cresce sem controle.** Passar o resultado integral de cada worker ao supervisor em toda volta infla o contexto. Em geral, ele precisa de um resumo do resultado para decidir, não do conteúdo inteiro; o conteúdo vai direto para quem vai usá-lo, como o redator.

## 6.5 Supervisor, Planning e Router

| Aspecto | Supervisor | Planning | Router |
|---|---|---|---|
| Quando decide | A cada passo, depois de ver o resultado anterior | Uma vez, antes de executar | Uma vez, na entrada |
| Adaptação a surpresas | Alta | Exige replanejamento | Nenhuma depois da decisão |
| Chamadas de coordenação | Uma por passo | Uma de planejamento (mais replanejamentos) | Uma, ou nenhuma se for por regras |
| Auditoria | Cada decisão fica registrada com justificativa | O plano completo existe antes da execução | A rota escolhida fica registrada |
| Caso típico | Tarefas heterogêneas e imprevisíveis | Tarefas decomponíveis de antemão | Pedidos de tipos distintos |

## 6.6 Limites, trade-offs e quando usar

O supervisor é ponto único de falha e de custo: se ele decide mal, todo o sistema segue o caminho errado, e cada passo paga uma chamada de coordenação além do trabalho do worker. Use o padrão quando houver especialidades realmente distintas e o caminho entre elas depender do que for descoberto. Se a sequência de especialistas for sempre a mesma, um workflow fixo é mais barato e mais previsível. Se a decisão for só na entrada, um router basta.

## 6.7 Resumo

No padrão Supervisor, um coordenador escolhe a cada passo qual worker especializado chama, com base no histórico, e decide quando encerrar. Os workers são caixas-pretas com contrato uniforme, o que facilita trocá-los. As salvaguardas essenciais são a decisão estruturada, o limite de passos e a detecção de repetição. O padrão se adapta melhor que o Planning a caminhos imprevisíveis, ao custo de uma chamada de coordenação por passo.

## Fontes

- [langgraph-supervisor](https://pypi.org/project/langgraph-supervisor/), página do pacote no PyPI, consultado em 2026-10-28.
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), Anthropic, publicado em 2024-12-19, consultado em 2026-10-28.
