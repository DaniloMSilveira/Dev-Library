# 2. ReAct: raciocinar e agir em ciclo

ReAct (de *Reasoning + Acting*) é o padrão em que o agente alterna raciocínio e ação: pensa no que precisa, chama uma ferramenta, lê o resultado e pensa de novo com a informação nova. É o loop básico sobre o qual os outros padrões da trilha são construídos. O *function calling* oferecido pelas APIs de LLM é o protocolo estruturado sobre o qual esse loop costuma ser implementado; o loop em si fica no código da aplicação.

Esta página explica o ciclo, por que ele funciona, como ele aparece no código e onde ele falha. Pressupõe os conceitos de agente e orquestração da [página 1](1-agentes-e-padroes.md).

## 2.1 Termos e definições

**Pensamento (thought):** texto em que o modelo explica o que pretende fazer e por quê. Funciona como rascunho de raciocínio antes da decisão.

**Ação (action):** a ferramenta escolhida e os argumentos dela. O modelo produz a descrição; o código executa.

**Observação (observation):** o resultado real da ferramenta, inserido no contexto pelo código. **Nunca é gerada pelo modelo.**

**Trajetória:** a sequência completa de pensamentos, ações e observações de uma execução. É o que se registra para auditoria e diagnóstico.

**Chain-of-thought (CoT):** técnica em que o modelo escreve o raciocínio passo a passo antes da resposta final, em vez de responder direto. No ReAct, o pensamento cumpre esse papel, mas intercalado com ações.

O padrão foi proposto por Yao et al. no paper *ReAct: Synergizing Reasoning and Acting in Language Models* (2022).

## 2.2 Como funciona

O ciclo se repete até o modelo concluir que tem informação suficiente ou até o limite de passos:

```text
objetivo
   │
   ▼
pensamento ──► ação ──► (código executa a ferramenta) ──► observação
   ▲                                                         │
   └─────────────────────────────────────────────────────────┘
          até: resposta final  OU  limite de passos atingido
```

A cada volta, a trajetória inteira volta para o modelo como contexto. É isso que permite ao agente mudar de rumo: se a observação mostra que a hipótese estava errada, o próximo pensamento parte dessa informação.

O padrão serve para tarefas em que **o próximo passo depende do resultado do passo anterior**. Exemplo: "quantos dias úteis faltam para o vencimento da fatura 881?" exige primeiro descobrir a data de vencimento (consulta ao sistema de faturas) e só depois contar os dias úteis (ferramenta de calendário). Não dá para planejar o segundo passo sem o resultado do primeiro.

### Por que separar pensamento e ação ajuda

- **O pensamento organiza a decisão.** Interpretação: escrever o objetivo imediato e o que falta descobrir antes de cada ação dá ao modelo um rascunho de trabalho, pelo mesmo motivo que o CoT ajuda em problemas de raciocínio, e torna mais fácil corrigir o rumo quando uma observação contradiz a hipótese.
- **A ação ancora o raciocínio em dados.** No paper original, ReAct reduziu problemas de alucinação e de propagação de erro que o CoT sozinho apresentava em tarefas de perguntas e checagem de fatos (HotpotQA e FEVER), porque o agente podia consultar uma fonte externa em vez de depender só do que o modelo sabia. Em tarefas interativas (ambientes simulados de tarefas domésticas e de compras online), o paper relata ganhos de 34 e 10 pontos percentuais de taxa de sucesso sobre métodos de aprendizado por imitação e por reforço, usando só um ou dois exemplos no prompt.
- **A trajetória é auditável.** Fica registrado o que o agente pensou, o que fez e o que recebeu de volta.

## 2.3 ReAct em texto e ReAct com function calling

Há duas formas de implementar o mesmo ciclo.

**ReAct em texto (forma original).** O prompt pede que o modelo escreva em um formato fixo (`Pensamento:`, `Ação:`, `Entrada:`) e o código extrai a ação com um parser. Para impedir que o modelo invente a observação, a chamada usa uma *stop sequence*: a geração para assim que o modelo escreve `Observação:`, e o código insere ali o resultado real.

**Function calling nativo.** A API recebe a lista de ferramentas com seus schemas e devolve a decisão do modelo como um objeto estruturado (nome da ferramenta e argumentos em JSON). O código executa e devolve o resultado em uma mensagem própria. O ciclo é o mesmo; muda só o protocolo.

| Aspecto | ReAct em texto | Function calling nativo |
|---|---|---|
| Interpretação da ação | Parser escrito por você, sensível a variações de formato | Estruturada pela API |
| Compatibilidade | Qualquer modelo que gere texto | Modelos e APIs com suporte a ferramentas |
| Visibilidade do raciocínio | Total: o pensamento está no texto | Depende do modelo e da API |
| Uso típico | Estudo do mecanismo, modelos sem suporte a ferramentas | A maioria dos sistemas em produção |

O esqueleto abaixo mostra o loop no estilo function calling, sem depender de um SDK específico. A função `chamar_llm` é ilustrativa: representa a chamada à API do provedor e devolve ou uma resposta final ou um pedido de ferramenta.

```python
# Ilustrativo: o loop ReAct no estilo function calling.
FERRAMENTAS = {
    "consultar_fatura": lambda numero: {"numero": numero, "vencimento": "2026-11-10"},
    "contar_dias_uteis": lambda ate: {"dias_uteis": 8},
}

def agente_react(pergunta: str, max_passos: int = 6) -> str:
    mensagens = [{"papel": "usuario", "conteudo": pergunta}]

    for _ in range(max_passos):
        decisao = chamar_llm(mensagens, ferramentas=list(FERRAMENTAS))

        if decisao["tipo"] == "resposta_final":
            return decisao["conteudo"]

        nome, argumentos = decisao["ferramenta"], decisao["argumentos"]
        if nome not in FERRAMENTAS:
            observacao = {"erro": f"ferramenta desconhecida: {nome}"}
        else:
            try:
                observacao = FERRAMENTAS[nome](**argumentos)
            except Exception as erro:
                observacao = {"erro": str(erro)}

        mensagens.append({"papel": "assistente", "ferramenta": nome, "argumentos": argumentos})
        mensagens.append({"papel": "ferramenta", "nome": nome, "conteudo": observacao})

    return "Não consegui concluir dentro do limite de passos."
```

Três detalhes do código são parte do padrão, não acessórios:

- a observação vem de `FERRAMENTAS[nome](...)`, nunca do modelo;
- um erro de ferramenta vira observação, para o modelo poder reagir (tentar outro caminho ou avisar o usuário), em vez de derrubar o loop;
- `max_passos` encerra a execução mesmo que o modelo nunca declare que terminou.

## 2.4 Limites, trade-offs e quando usar

**Quando usar:** a informação necessária só aparece durante a execução, o ambiente muda (dados ao vivo, APIs externas) e responder rápido importa mais do que ter um plano completo antes.

**Riscos e cuidados:**

- **Loops improdutivos.** O agente pode repetir a mesma ação esperando outro resultado. Além do limite de passos, vale detectar chamadas repetidas com os mesmos argumentos.
- **Custo crescente por passo.** Como a trajetória inteira volta ao modelo a cada volta, o número de tokens de entrada cresce a cada passo. Trajetórias longas pedem resumo ou poda do histórico (ver [4. Princípios e boas práticas](../context-engineering/4-principios-e-boas-praticas.md)).
- **Decisão local.** O ReAct escolhe um passo de cada vez e não enxerga a tarefa inteira. Em tarefas longas e decomponíveis, isso gera passos desnecessários; é o caso de usar [Planning](4-planning.md).
- **Execução de saída do modelo.** Argumentos produzidos pelo modelo são dados não confiáveis. Nunca passe esses argumentos para `eval`, shell ou SQL montado por concatenação; valide e use APIs parametrizadas.
- **Ações irreversíveis.** Ferramentas que pagam, apagam ou enviam algo precisam de confirmação ou de limites definidos no código (ver a [seção 1.4](1-agentes-e-padroes.md#_1-4-regra-de-negocio-fica-no-codigo)).

## 2.5 Resumo

ReAct é o ciclo pensamento → ação → observação, repetido até haver resposta ou até o limite de passos. O pensamento melhora a decisão, a ação traz dados reais e a observação é sempre produzida pelo código, nunca pelo modelo. Function calling nativo é a mesma ideia com protocolo estruturado e é a forma usual em produção. O padrão brilha quando o próximo passo depende do anterior e perde eficiência em tarefas longas que poderiam ser planejadas de antemão.

## Fontes

- Yao et al., [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629), 2022 (ICLR 2023), consultado em 2026-10-28.
