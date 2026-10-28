# 1. Agentes de IA e por que usar padrões

Um agente de IA é um sistema em que um modelo de linguagem decide, durante a execução, quais passos tomar para chegar a um objetivo, chamando ferramentas e observando os resultados. Essa autonomia resolve problemas que um fluxo fixo não resolve, mas cobra um preço: o sistema fica menos previsível, mais caro e mais difícil de auditar. Os design patterns desta trilha são soluções recorrentes para controlar esse preço.

Esta página define o que é um agente, separa agente de workflow e apresenta o mapa dos padrões tratados nas páginas seguintes. Ela parte do ponto em que a trilha de Context Engineering terminou: o loop de orquestração e o uso de ferramentas descritos em [A camada de contexto em uma arquitetura de agente de IA](../context-engineering/5-camada-em-arquitetura-llm.md).

## 1.1 Termos e definições

**LLM (Large Language Model):** o modelo que recebe texto e produz texto. Sozinho, ele responde a uma chamada e para.

**Ferramenta (tool):** uma função do sistema que o modelo pode pedir para executar, como consultar um banco, buscar em documentos ou chamar uma API. O modelo só descreve a chamada; quem executa é o código.

**Orquestração:** o código que liga tudo: monta o contexto, chama o modelo, executa as ferramentas pedidas, devolve os resultados ao modelo e decide quando parar.

**Workflow:** um fluxo em que o desenvolvedor define a sequência de passos no código. O LLM pode aparecer em vários passos, mas não escolhe o caminho.

**Agente:** um fluxo em que o próprio LLM escolhe o próximo passo a cada volta do loop, com base no objetivo e no que já aconteceu.

**Design pattern:** uma solução de arquitetura recorrente para um problema recorrente. O termo vem da engenharia de software clássica e aqui tem o mesmo sentido: um vocabulário comum para decisões de projeto, não uma biblioteca pronta.

## 1.2 Os componentes de um agente

Um agente costuma ser descrito como a soma de quatro componentes:

| Componente | Papel | Onde foi tratado no acervo |
|---|---|---|
| Modelo | Raciocina sobre o objetivo e decide a próxima ação | [6. Transformers e LLMs](../machine-learning/6-transformers-e-llms.md) |
| Ferramentas | Permitem agir fora do modelo: ler, calcular, escrever | [5.3 Tooling](../context-engineering/5-camada-em-arquitetura-llm.md#_5-3-tooling-como-um-agente-usa-ferramentas) |
| Memória | Guarda o que precisa sobreviver entre passos e sessões | [3. Memória e estado](../context-engineering/3-memoria-e-estado.md) |
| Orquestração | Executa o loop, aplica limites e trata erros | [5.1 O fluxo de ponta a ponta](../context-engineering/5-camada-em-arquitetura-llm.md#_5-1-o-fluxo-de-ponta-a-ponta) |

O componente que transforma uma chamada a um LLM em um agente é a orquestração. Sem ela, há uma pergunta e uma resposta. Com ela, há um loop que observa o efeito de cada ação e decide a próxima. Os padrões desta trilha são, quase todos, formas diferentes de organizar esse loop.

## 1.3 Agente ou workflow

A diferença entre os dois está em **quem decide o caminho**:

| Aspecto | Workflow | Agente |
|---|---|---|
| Quem define os passos | O desenvolvedor, no código | O modelo, em tempo de execução |
| Previsibilidade | Alta: o caminho é sempre o mesmo | Menor: dois pedidos parecidos podem seguir caminhos diferentes |
| Custo por pedido | Conhecido de antemão | Varia com o número de voltas no loop |
| Teste e auditoria | Testa-se cada passo | É preciso registrar e avaliar trajetórias inteiras |
| Quando usar | O problema tem etapas conhecidas | Os passos só ficam claros durante a execução |

Na prática, os dois se misturam. Um sistema pode ser um workflow na maior parte e deixar um único passo nas mãos de um agente. A recomendação da Anthropic em *Building effective agents* vai na mesma direção: começar pela solução mais simples (às vezes uma única chamada bem montada) e acrescentar autonomia só quando o ganho compensar a perda de previsibilidade e o aumento de custo e latência.

**Exemplo concreto.** Pense em um assistente de suporte de um sistema de contas a pagar:

- "Gerar a segunda via do boleto 4521" tem passos conhecidos: localizar o boleto, gerar o PDF, enviar o link. Um workflow resolve.
- "Por que o pagamento do fornecedor X não aparece no relatório de ontem?" exige investigar: consultar o pagamento, depois o status da integração bancária, depois talvez o log de importação. O próximo passo depende do que o passo anterior revelar. Esse é o terreno de um agente.

## 1.4 Regra de negócio fica no código

Uma decisão de arquitetura vale para todos os padrões: **o que é regra de negócio fica em código determinístico, não dentro do prompt.** Limites de valor, permissões, cálculos e validações escritos em linguagem natural no prompt não podem ser testados com testes unitários, mudam de comportamento quando o modelo muda e não deixam rastro claro em auditoria.

O LLM fica com o que só ele faz bem: interpretar linguagem natural e decidir sob incerteza. O código faz o resto, inclusive conferir se a decisão do modelo é permitida antes de executá-la.

```python
# Ilustrativo: o modelo sugere a ação; o código decide se ela pode ser executada.
LIMITE_ESTORNO_AUTOMATICO = 500.00

def executar_estorno(pedido_id: str, valor: float) -> dict:
    if valor > LIMITE_ESTORNO_AUTOMATICO:
        return {"status": "pendente_aprovacao", "motivo": "valor acima do limite automático"}
    return {"status": "estornado", "pedido_id": pedido_id, "valor": valor}
```

Se o limite estivesse escrito no prompt ("não estorne valores acima de 500"), nada garantiria que o modelo o respeitaria em todos os casos.

## 1.5 O mapa dos padrões

Cada padrão desta trilha responde a um problema específico. A tabela serve como índice; cada linha tem uma página própria.

| Padrão | Problema que resolve | Quando considerar | Página |
|---|---|---|---|
| ReAct | O agente precisa descobrir informação enquanto age | Os passos dependem do resultado das ferramentas | [2. ReAct](2-react.md) |
| Reflection | A primeira resposta não tem qualidade suficiente | O erro custa caro e há tempo para revisar | [3. Reflection](3-reflection.md) |
| Planning | A tarefa tem muitos passos e precisa ser organizada antes | A tarefa pode ser decomposta de antemão e o plano precisa ser auditável | [4. Planning](4-planning.md) |
| Router | Pedidos diferentes pedem modelos ou fluxos diferentes | Há tipos de pedido bem distintos e diferença de custo entre as rotas | [5. Router](5-router.md) |
| Supervisor | Vários especialistas precisam ser coordenados | O caminho entre especialistas só fica claro durante a execução | [6. Supervisor](6-supervisor.md) |
| Colaboração multiagente | Uma única perspectiva não basta | Decisões caras que ganham com perspectivas diferentes | [7. Colaboração entre múltiplos agentes](7-colaboracao-multiagente.md) |

Os padrões não são excludentes. Um sistema real costuma combinar vários: um router decide qual subsistema atende o pedido; dentro dele, um supervisor distribui o trabalho; os workers são agentes ReAct com ferramentas; e a resposta final passa por uma etapa de reflection antes de chegar ao usuário. Escolha cada padrão pelo problema que ele resolve naquele ponto do sistema, não pela novidade.

## 1.6 Limites e riscos comuns a todos os padrões

Todo padrão desta trilha adiciona chamadas ao modelo, e cada chamada adiciona custo, latência e uma nova chance de erro. Alguns cuidados valem para todos:

- **Limite de iterações:** todo loop precisa de um teto, além do critério "o modelo disse que terminou".
- **Saída estruturada:** quando o código precisa interpretar a decisão do modelo, peça um formato estruturado (JSON validado por schema) em vez de texto livre.
- **Observabilidade:** registre cada decisão, ferramenta chamada, resultado e consumo de tokens. Sem isso, um agente que errou não pode ser diagnosticado (ver [5.4 Observabilidade](../context-engineering/5-camada-em-arquitetura-llm.md#_5-4-observabilidade)).
- **Medir antes de complicar:** um padrão mais elaborado só se justifica se melhorar um resultado que você consegue medir.

## 1.7 Resumo

Um agente é um sistema em que o LLM decide o próximo passo dentro de um loop controlado por código, enquanto em um workflow o caminho é fixado pelo desenvolvedor. Essa autonomia é útil quando os passos só aparecem durante a execução, mas traz custo variável e menos previsibilidade. Os design patterns de agentes organizam esse loop para problemas recorrentes: agir e observar (ReAct), revisar (Reflection), planejar (Planning), direcionar (Router), coordenar (Supervisor) e deliberar em grupo (colaboração multiagente). Em todos, a regra de negócio fica no código e o modelo fica com a interpretação e a decisão sob incerteza.

## Fontes

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), Anthropic, publicado em 2024-12-19, consultado em 2026-10-28.
