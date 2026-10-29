# 5. Verificação e evolução do harness

Guides aumentam a chance de acerto, mas não garantem nada sobre o resultado final. Esta página trata da metade de feedback do harness: como organizar as verificações para que um erro seja pego antes de chegar ao usuário, quando envolver uma pessoa, e como medir o agente ao longo do tempo para que o harness melhore de forma controlada, e não por tentativa e erro.

Ela usa a distinção entre guides e sensors da [página 2](2-guides-e-sensors.md) e o loop de planejamento da trilha de [Design patterns de agentes](../design-patterns-agentes/4-planning.md).

## 5.1 Termos e definições

**Portão de qualidade:** um sensor posicionado em um ponto do fluxo que decide se o trabalho segue, volta para correção ou vai para uma pessoa.

**Planejar, executar, verificar:** loop em que o agente escreve o plano com critérios de sucesso, executa e só termina quando a verificação confirma esses critérios, com limite de tentativas.

**Evidência:** registro de que uma verificação de fato rodou e qual foi o resultado. Distingue "o agente disse que testou" de "o teste rodou e passou".

**Eval:** teste automatizado do comportamento do agente sobre um conjunto de casos representativos. É o equivalente, para agentes, da suíte de testes de um software.

**LLM como juiz:** uso de um modelo para avaliar a saída de outro segundo critérios escritos.

## 5.2 Portões em cascata

As verificações ficam em sequência, da mais barata e objetiva para a mais cara e subjetiva, e cada uma só roda se a anterior passou:

| Ordem | Tipo | Exemplos | Custo |
|---|---|---|---|
| 1 | Determinística | Validação de schema, tipos, expressões regulares | Quase nenhum |
| 2 | Execução | Lint, build, testes | Segundos a minutos |
| 3 | Inferencial | Revisão por outro agente, LLM como juiz | Tokens e latência |
| 4 | Humana | Aprovação de quem responde pelo resultado | Tempo de uma pessoa |

Falhar rápido economiza: não faz sentido pagar uma revisão por modelo de algo que nem passa no lint. E a mensagem de cada portão deve dizer ao agente o que corrigir, para a próxima tentativa partir de algo concreto.

## 5.3 Planejar, executar, verificar

O loop organiza os portões em torno de uma tarefa:

```text
planejar ──► executar ──► verificar ──► aprovado? ── sim ──► registrar e entregar
   ▲                                       │
   └────────── motivo da reprovação ◄──── não  (até N tentativas, depois escala)
```

- **Planejar** antes de agir obriga o agente a explicitar o que vai fazer e como saberá que deu certo. O plano é um artefato que pode ser revisado antes de qualquer ação cara.
- **Verificar** compara o resultado com os critérios do plano, usando os portões da seção anterior.
- **O limite de tentativas** impede o loop de girar sem progresso. Esgotado o limite, o trabalho vai para uma pessoa com o histórico do que foi tentado.

A estrutura é a mesma dos padrões [Planning](../design-patterns-agentes/4-planning.md) e [Reflection](../design-patterns-agentes/3-reflection.md); a diferença aqui é que a verificação é feita, sempre que possível, por sensors computacionais, e não pela autocrítica do modelo.

## 5.4 Testes, lint e hooks como sensors

Em agentes de programação, o projeto já tem os melhores sensors disponíveis: a suíte de testes, o lint, a checagem de tipos e o build. Algumas práticas os tornam mais eficazes:

- **Testes antes da implementação.** O agente escreve o teste, confirma que ele falha pelo motivo certo, implementa e confirma que passa. Isso dá um critério de sucesso objetivo, sem depender de outro modelo para julgar.
- **Critério de pronto explícito.** "Pronto" significa testes passando nesta sessão, verificação executada e evidência registrada. Sem isso escrito, o agente tende a declarar sucesso cedo.
- **Testes que o agente não pode enfraquecer.** Uma regra explícita contra apagar ou relaxar testes para fazê-los passar; no texto da Anthropic sobre agentes de longa duração, o agente só pode mudar o status de uma feature, não os passos de teste.
- **Verificação automática a cada edição.** Um hook `PostToolUse` que roda o lint no arquivo alterado devolve o problema ao agente no passo seguinte, em vez de no fim da tarefa.
- **Hooks de pre-commit e CI.** Os mesmos portões que valem para pessoas valem para o agente, e o que ele produz passa por eles antes de chegar à branch principal.

## 5.5 Humano no loop

Algumas decisões devem passar por uma pessoa:

- **ações irreversíveis:** apagar dados, publicar, pagar, enviar mensagem a cliente, fazer merge na branch principal;
- **baixa confiança:** quando os sensors divergem ou o agente sinaliza incerteza;
- **situação nova:** algo sem precedente nos casos conhecidos;
- **exigência regulatória:** domínios em que a lei ou a política exige decisão humana.

Cada escalonamento custa tempo e atenção, e aprovação demais gera aprovação automática, sem leitura. O desenho certo é o mínimo de intervenção humana que deixa o risco aceitável. Quando uma pessoa é chamada, ela precisa receber o que precisa para decidir rápido: o que o agente quer fazer, por quê e o que acontece se der errado.

## 5.6 Medir o agente

Não dá para melhorar o harness de forma controlada sem medir. As métricas se dividem em três grupos, que precisam ser acompanhados juntos porque melhorar um costuma piorar outro:

| Grupo | Pergunta | Exemplos |
|---|---|---|
| Qualidade | O agente faz a coisa certa? | Taxa de tarefas concluídas corretamente; taxa de respostas sem suporte nos dados; escolha correta de ferramenta |
| Operação | Faz de forma sustentável? | Latência; tokens e custo por tarefa; tentativas até o sucesso; taxa de escalonamento para humanos |
| Experiência | Quem usa está satisfeito? | Frequência com que o usuário corrige ou rejeita o resultado; abandono no meio da tarefa |

### Evals

Um eval executa o agente sobre um conjunto de casos e avalia cada resultado, combinando checagens determinísticas (a ferramenta certa foi chamada? a resposta contém o dado esperado?) com critérios avaliados por um modelo ou por pessoas. Ele difere de um teste comum em dois pontos:

- **O resultado varia entre execuções.** O mesmo caso pode passar em uma rodada e falhar em outra, então o que se acompanha é a taxa de acerto, não cada caso isolado.
- **O julgamento nem sempre é exato.** Muitas vezes o critério é semântico ("a resposta explica o motivo do atraso?"), e não uma comparação de igualdade.

Um conjunto pequeno de casos reais, com o resultado esperado anotado, já é útil. Ele cresce da forma mais valiosa possível: **cada erro encontrado em produção vira um caso permanente**, para que uma mudança futura no harness não traga o erro de volta.

Benchmarks públicos de agentes servem para comparar sistemas em condições controladas, mas não substituem os evals do seu caso de uso: eles medem tarefas que não são as suas.

## 5.7 O ciclo de evolução

Tudo nesta trilha converge para um ciclo:

```text
agente em uso ──► observação (logs, métricas, relatos)
      ▲                         │
      │                         ▼
caso de eval ◄── fix permanente ◄── causa raiz ◄── incidente
```

1. **Observar:** registrar decisões, chamadas de ferramenta, resultados e custos (ver [5.4 Observabilidade](../context-engineering/5-camada-em-arquitetura-llm.md#_5-4-observabilidade), na trilha de Context Engineering).
2. **Detectar o incidente:** por alerta, eval que piorou ou relato de quem usa.
3. **Achar a causa:** faltou informação? Faltou verificação? Nada impedia a ação?
4. **Corrigir no nível certo:** instrução, sensor ou bloqueio, conforme a hierarquia da [página 2](2-guides-e-sensors.md#_2-5-a-hierarquia-de-fixes).
5. **Fechar com um caso de eval ou teste** que reproduz o erro, para garantir que ele não volte.

Cada volta deixa o harness um pouco melhor. A skill `/registrar-incidente` do [exemplo completo](exemplos/claude-completo/README.md) transforma esse ciclo em um procedimento.

## 5.8 Limites e trade-offs

- **Verificação custa tempo e tokens.** Portões caros em cada passo deixam o agente lento; concentre-os no fim da tarefa.
- **Sensors podem ser contornados pelo próprio agente.** Um agente sob pressão para "fazer o teste passar" pode alterar o teste. Por isso a regra contra enfraquecer testes e, quando possível, a proteção estrutural desses arquivos.
- **Evals pequenos enganam.** Com poucos casos, uma variação aleatória parece melhora ou piora. Compare taxas em conjuntos de tamanho razoável e repita as rodadas quando a decisão for importante.
- **Métrica vira alvo.** Otimizar só a taxa de conclusão pode produzir um agente que conclui depressa e mal. Acompanhe os três grupos de métricas juntos.

## 5.9 Resumo

Verificações funcionam em cascata, das baratas e determinísticas às caras e humanas, falhando rápido. O loop planejar, executar e verificar amarra essas verificações a cada tarefa, com critérios de sucesso explícitos, evidência registrada e limite de tentativas. Em agentes de programação, testes, lint e hooks são os sensors mais confiáveis. Pessoas entram no mínimo necessário, para o que é irreversível, incerto ou regulado. Medir qualidade, operação e experiência, com evals que crescem a partir de erros reais, é o que transforma a evolução do harness em engenharia.

## Fontes

- Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 2025-11-26, consultado em 2026-10-28.
- Birgitta Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html), martinfowler.com, 2026-04-02, consultado em 2026-10-28.
- Claude Code, documentação oficial de [hooks](https://code.claude.com/docs/en/hooks), consultado em 2026-10-28.
