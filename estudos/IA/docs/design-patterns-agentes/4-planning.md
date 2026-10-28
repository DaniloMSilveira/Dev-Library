# 4. Planning: planejar antes de executar

Planning (também chamado de *plan-and-execute*) é o padrão em que o agente primeiro monta um plano completo para o objetivo e só depois executa os passos desse plano. Ele separa duas atividades que no [ReAct](2-react.md) acontecem misturadas: decidir o que fazer e fazer.

Esta página explica como o plano é representado, o que se ganha com a separação, como lidar com falhas durante a execução e quando preferir Planning ou ReAct.

## 4.1 Termos e definições

**Planejador (planner):** o papel que recebe o objetivo e a lista de ferramentas disponíveis e devolve um plano. Costuma usar o modelo mais capaz, porque decompor um problema exige visão do todo.

**Executor:** o papel que executa cada passo do plano, com uma ferramenta ou com uma chamada ao modelo. Como cada passo é mais simples que o objetivo inteiro, o executor pode usar um modelo menor e mais barato.

**Plano:** a lista de passos com as dependências entre eles. Cada passo tem um identificador, uma descrição, a ferramenta a usar (opcional) e os passos de que depende.

**DAG (grafo acíclico dirigido):** a forma de representar um plano com dependências: cada passo é um nó, cada dependência é uma seta e não pode haver ciclo (um passo não pode depender, direta ou indiretamente, dele mesmo).

**Replanejamento:** pedir ao planejador um plano novo quando a execução encontra um problema que o plano original não previa.

## 4.2 Como funciona

```text
objetivo ──► planejador ──► plano (DAG) ──► validação ──► executor ──► resultado
                 ▲                                            │
                 └────────── falha em um passo ◄──────────────┘
                             (replanejamento, com limite)
```

Separar planejamento e execução traz três ganhos:

1. **Visibilidade.** O plano existe antes de qualquer ação. Ele pode ser registrado, revisado e, em domínios regulados ou em ações de risco, aprovado por uma pessoa antes da execução.
2. **Otimização.** Com o plano inteiro em mãos, passos sem dependência entre si podem rodar em paralelo, e cada passo pode usar o modelo mais adequado (e mais barato) para ele.
3. **Recuperação localizada.** Quando um passo falha, sabe-se exatamente onde a execução parou e o que já foi feito; replaneja-se a partir dali, em vez de recomeçar.

A ideia de planejar antes de resolver aparece em trabalhos como o *Plan-and-Solve Prompting* (Wang et al., 2023), que pede ao modelo um plano antes da solução para reduzir passos esquecidos em problemas de raciocínio. O *LLMCompiler* (Kim et al., 2023) leva a ideia para chamadas de ferramentas: um planejador produz as tarefas com suas dependências e um executor dispara em paralelo as que estão prontas. Os autores relatam, em relação ao ReAct, até 3,7 vezes menos latência, até 6,7 vezes menos custo e até cerca de 9% mais acurácia nos benchmarks avaliados.

## 4.3 Exemplo concreto

Objetivo: "montar o resumo de inadimplência de outubro para a diretoria". Um plano razoável:

| Passo | Descrição | Ferramenta | Depende de |
|---|---|---|---|
| 1 | Listar faturas vencidas em outubro | `consultar_faturas` | nenhum |
| 2 | Listar pagamentos recebidos em outubro | `consultar_pagamentos` | nenhum |
| 3 | Cruzar faturas e pagamentos para achar as que seguem em aberto | código | 1, 2 |
| 4 | Calcular valor total em aberto e percentual sobre o faturado | código | 3 |
| 5 | Redigir o resumo para a diretoria | LLM | 4 |

Os passos 1 e 2 não dependem de nada e podem rodar ao mesmo tempo. Os passos 3 e 4 são determinísticos e ficam com o código, não com o modelo (ver [1.4](1-agentes-e-padroes.md#_1-4-regra-de-negocio-fica-no-codigo)). Só o passo 5 precisa de um LLM.

O plano vem do modelo como JSON. Antes de executar, o código valida a estrutura e as dependências. O trecho abaixo usa Pydantic para o schema e o `graphlib` da biblioteca padrão do Python para ordenar os passos e detectar ciclos. A função `executar_passo` é ilustrativa.

```python
# Ilustrativo: validação do plano e execução em lotes respeitando dependências.
from graphlib import TopologicalSorter
from pydantic import BaseModel

class Passo(BaseModel):
    id: int
    descricao: str
    ferramenta: str | None = None
    depende_de: list[int] = []

class Plano(BaseModel):
    objetivo: str
    passos: list[Passo]

def validar_plano(plano: Plano, ferramentas: set[str]) -> TopologicalSorter:
    ids = {p.id for p in plano.passos}
    if len(ids) != len(plano.passos):
        raise ValueError("Plano com id de passo repetido")
    for passo in plano.passos:
        if passo.ferramenta and passo.ferramenta not in ferramentas:
            raise ValueError(f"Passo {passo.id}: ferramenta inexistente {passo.ferramenta}")
        if not set(passo.depende_de) <= ids:
            raise ValueError(f"Passo {passo.id}: depende de passo inexistente")

    grafo = TopologicalSorter({p.id: set(p.depende_de) for p in plano.passos})
    grafo.prepare()  # levanta CycleError se houver dependência circular
    return grafo

def executar_plano(plano: Plano, grafo: TopologicalSorter) -> dict[int, object]:
    passos = {p.id: p for p in plano.passos}
    resultados: dict[int, object] = {}
    while grafo.is_active():
        prontos = grafo.get_ready()  # passos cujas dependências já terminaram
        for id_passo in prontos:     # este lote poderia rodar em paralelo
            passo = passos[id_passo]
            entradas = {dep: resultados[dep] for dep in passo.depende_de}
            resultados[id_passo] = executar_passo(passo, entradas)
            grafo.done(id_passo)
    return resultados
```

Se `Plano(**json_do_modelo)` ou `validar_plano` falharem, o plano é rejeitado **antes** de qualquer ação, e o planejador pode ser chamado de novo com a mensagem de erro. Validar primeiro é mais barato do que descobrir o problema no meio da execução.

## 4.4 Replanejamento

Planos encontram imprevistos: uma API fora do ar, um dado em formato inesperado, um passo que devolve vazio. Em vez de abortar tudo, o executor devolve ao planejador:

- o objetivo original;
- os passos já concluídos e os resultados deles;
- o passo que falhou e o erro.

O planejador produz um plano novo para o que falta, aproveitando o que já foi feito. Dois limites evitam que isso vire um loop caro:

- **Número máximo de replanejamentos** por execução. Atingido o limite, o sistema para e reporta o que conseguiu.
- **Detecção de plano repetido:** se o novo plano é praticamente igual ao anterior, o problema provavelmente não se resolve replanejando (por exemplo, uma credencial inválida), e insistir só gasta tokens.

## 4.5 Planning, ReAct ou os dois

| Aspecto | Planning | ReAct |
|---|---|---|
| Quando decide | Antes de executar, para a tarefa inteira | A cada passo |
| Melhor para | Tarefas decomponíveis de antemão, com requisitos de auditoria | Ambientes dinâmicos, em que a informação aparece durante a execução |
| Paralelismo | Natural: os passos independentes ficam visíveis no plano | Difícil: um passo de cada vez |
| Reação a surpresas | Exige replanejamento explícito | Imediata, no próximo pensamento |
| Custo | Uma chamada de planejamento mais passos baratos | Uma chamada ao modelo por passo, com o contexto crescendo |

As duas abordagens se combinam bem: Planning define os passos no nível macro, e cada passo que envolve investigação é executado por um pequeno agente ReAct.

## 4.6 Limites, trade-offs e quando usar

- **Planos frágeis.** O plano reflete o que o planejador sabia antes de começar. Em tarefas exploratórias, ele erra cedo e o replanejamento vira rotina; nesse caso, ReAct é mais adequado.
- **Overhead em tarefas curtas.** Para dois ou três passos, a chamada de planejamento custa mais do que economiza.
- **Plano ruim, execução fiel.** O executor segue o plano mesmo que ele esteja errado. A validação estrutural pega erros de formato, mas não erros de lógica; para ações de risco, inclua aprovação humana do plano.
- **Decomposição hierárquica.** Tarefas muito grandes podem ter um plano de alto nível em que cada passo é expandido em um subplano. Ajuda a controlar a complexidade, mas multiplica as chamadas de planejamento.

## 4.7 Resumo

Planning separa decidir de executar: um planejador produz um plano com dependências, o código valida esse plano e um executor percorre os passos, rodando em paralelo os independentes. O padrão ganha em visibilidade, custo e recuperação de falhas em tarefas decomponíveis e auditáveis, e perde para o ReAct em tarefas exploratórias. O replanejamento é o mecanismo de recuperação e precisa sempre de limite.

## Fontes

- Wang et al., [Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models](https://arxiv.org/abs/2305.04091), 2023, consultado em 2026-10-28.
- Kim et al., [An LLM Compiler for Parallel Function Calling](https://arxiv.org/abs/2312.04511), 2023 (ICML 2024), consultado em 2026-10-28.
- [graphlib: Functionality to operate with graph-like structures](https://docs.python.org/3/library/graphlib.html), documentação do Python, consultado em 2026-10-28.
