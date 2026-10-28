# 3. Reflection: revisar antes de entregar

Reflection é o padrão em que o agente avalia a própria saída contra critérios definidos e, se encontrar problemas, produz uma nova versão antes de entregar. Ele parte de uma constatação simples: a primeira resposta de um LLM costuma ser aceitável, mas nem sempre é a melhor que o mesmo modelo consegue produzir quando recebe uma crítica específica.

Esta página explica os papéis do padrão, como definir quando parar, quanto ele custa e quando ele não ajuda. Ela usa o loop de agente da [página 2](2-react.md), mas o padrão também funciona em fluxos sem ferramentas.

## 3.1 Termos e definições

**Gerador:** o papel que produz a saída (um texto, um código, uma análise) e, depois, as versões revisadas.

**Crítico:** o papel que avalia a saída contra critérios explícitos e devolve uma lista de problemas. Pode ser o mesmo modelo com outro prompt, outro modelo ou um verificador que não é LLM (testes, compilador, validador de schema).

**Critério de parada:** a regra que encerra o ciclo de revisão.

**Feedback externo:** sinal que vem de fora do modelo, como o resultado de testes, a saída de um compilador ou uma consulta a uma fonte de dados. Se opõe à autocrítica, em que o modelo só relê o próprio texto.

## 3.2 Como funciona

```text
tarefa ──► gerador ──► saída v1 ──► crítico ──► aprovado? ── sim ──► entrega
                          ▲                        │
                          │                       não
                          └── gerador revisa ◄── lista de problemas
```

O ciclo tem três partes:

1. **Gerar** a primeira versão.
2. **Criticar** contra critérios explícitos, devolvendo um resultado estruturado.
3. **Revisar** a saída usando a crítica como entrada, e voltar ao passo 2.

### O crítico precisa ser específico

Um crítico que responde "está bom" ou "pode melhorar" não dá ao gerador nada para corrigir. A crítica útil aponta problemas verificáveis: "o texto promete reembolso em 5 dias, mas a política informada é de 10 dias úteis", "a função não trata lista vazia". Duas práticas ajudam:

- **Critérios no prompt do crítico:** uma lista do que verificar, ligada ao objetivo da tarefa.
- **Saída estruturada:** o crítico devolve JSON validado, com campos como `aprovado`, `problemas` e `sugestoes`. O código decide o próximo passo lendo `aprovado`, sem interpretar texto livre.

```python
# Ilustrativo: contrato da crítica, validado antes de ser usado.
from pydantic import BaseModel

class Critica(BaseModel):
    aprovado: bool
    problemas: list[str]
    sugestoes: list[str]

CRITERIOS = [
    "O prazo de reembolso citado é exatamente o da política informada.",
    "O texto não promete nada que a política não prevê.",
    "O tom é cordial e não culpa o cliente.",
]
```

### Critérios de parada

Iterar demais aumenta custo e latência; iterar de menos desperdiça o padrão. Na prática, combinam-se três condições, e a primeira que acontecer encerra o ciclo:

| Critério | Encerra quando | Observação |
|---|---|---|
| Aprovação | O crítico marca `aprovado: true` | Depende da qualidade do crítico |
| Limite de iterações | Atinge o número máximo de revisões | Obrigatório: garante que o ciclo termina |
| Convergência | Duas versões seguidas quase não diferem | Indica que mais revisões não vão mudar o resultado |

Quando o limite é atingido sem aprovação, o sistema precisa de uma decisão explícita: entregar a última versão com um aviso, devolver a melhor versão segundo o crítico ou encaminhar para revisão humana.

## 3.3 Exemplo concreto

Um agente redige respostas a pedidos de reembolso de clientes. A política informada no contexto diz que reembolsos são processados em até 10 dias úteis e não cobrem frete.

1. O gerador escreve uma resposta cordial que diz "seu reembolso, incluindo o frete, cai em 5 dias".
2. O crítico, com os critérios acima, devolve `aprovado: false` e dois problemas: prazo diferente da política e promessa de reembolso do frete.
3. O gerador reescreve com esses dois pontos.
4. O crítico aprova; a resposta é entregue.

**Analogia:** é a revisão de um texto por um colega com uma checklist na mão. A analogia deixa de valer em um ponto importante: quando gerador e crítico são o mesmo modelo, o "colega" tem os mesmos pontos cegos do autor. Por isso, sempre que existir um verificador externo (testes, validador, consulta a dados), ele é um crítico melhor do que a autocrítica.

## 3.4 Variantes

| Variante | O que muda |
|---|---|
| Self-Refine | O mesmo modelo gera, critica e revisa, só com prompts diferentes, sem treino adicional. Os autores relatam melhora média de cerca de 20 pontos percentuais em sete tarefas em relação à geração em uma passada. |
| Reflexion | Depois de cada tentativa, o agente escreve uma reflexão sobre o que deu errado e guarda essa reflexão em memória, que é usada nas tentativas seguintes. Em geração de código, os autores relatam 91% de pass@1 no HumanEval (benchmark de problemas de programação em Python verificados por testes), contra 80% do GPT-4 da época. Pass@1 mede uma única solução avaliada por problema; no Reflexion, essa solução sai depois das tentativas internas guiadas por testes que o próprio agente gera. |
| Crítica guiada por princípios | O crítico avalia a saída contra uma lista de princípios ou políticas escritas. A ideia vem do Constitutional AI, da Anthropic, que usa autocrítica e revisão guiadas por princípios **durante o treino** do modelo. Usar a mesma ideia em tempo de execução é uma adaptação, não o método do paper. |

## 3.5 Limites, trade-offs e quando usar

**Custo.** Cada ciclo acrescenta pelo menos uma chamada de crítica e, se houver revisão, mais uma de geração. Com um limite de três revisões, o pior caso é a geração inicial mais três pares de crítica e revisão, ou sete chamadas, para uma resposta que, sem o padrão, seria uma. Se a última versão também passar pelo crítico antes da entrega, como no exemplo prático, são oito.

**A autocrítica não é garantia.** Huang et al. (2023) mostraram que, em tarefas de raciocínio, pedir ao modelo que corrija a própria resposta **sem feedback externo** não melhora o resultado de forma confiável e às vezes piora: o modelo troca uma resposta certa por uma errada. Os ganhos mais sólidos aparecem quando o crítico tem acesso a algo que o gerador não tinha, como testes, critérios explícitos ou dados.

| Cenário | Reflection ajuda? | Motivo |
|---|---|---|
| Geração de código com testes disponíveis | Sim | Os testes são um crítico externo objetivo |
| Texto longo com requisitos explícitos (política, formato) | Sim | Os critérios tornam a crítica verificável |
| Análise ou argumentação de alto impacto | Em geral sim | Um segundo passe encontra lacunas, de preferência com outro modelo ou prompt |
| Pergunta factual simples | Não | Custo extra sem ganho perceptível |
| Chamada de ferramenta determinística | Não | A própria ferramenta valida o resultado |
| Resposta com latência crítica (chat em tempo real) | Raramente | O tempo das chamadas extras é perceptível para o usuário |

Antes de adotar o padrão em escala, compare a qualidade com e sem Reflection em um conjunto de casos reais e confira se o ganho justifica o custo.

## 3.6 Resumo

Reflection separa os papéis de gerar e criticar e repete a revisão até a aprovação, até um limite de iterações ou até as versões convergirem. O padrão depende de um crítico específico, com critérios explícitos e saída estruturada, e funciona melhor quando esse crítico tem feedback externo, como testes ou dados. Ele multiplica o custo por resposta, então deve ser aplicado onde o erro custa caro e o ganho pode ser medido.

## Fontes

- Madaan et al., [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651), 2023, consultado em 2026-10-28.
- Shinn et al., [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366), 2023, consultado em 2026-10-28.
- Bai et al., [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073), 2022, consultado em 2026-10-28.
- Huang et al., [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798), 2023 (ICLR 2024), consultado em 2026-10-28.
