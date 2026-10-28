# 5. Router: direcionar cada pedido para o caminho certo

Router é o padrão em que um componente classifica cada entrada e a envia para a rota mais adequada: um modelo maior ou menor, um pipeline de RAG, um fluxo com ferramentas ou um atendente humano. Diferente dos padrões anteriores, ele não executa um loop. Toma **uma decisão, no início**, e passa o pedido adiante.

Esta página compara as formas de implementar um router, mostra como combiná-las e explica o principal motivo para usá-lo: gastar com modelo caro só o que realmente precisa de modelo caro. Ele aparece como *routing* entre os padrões de workflow descritos pela Anthropic em *Building effective agents*.

## 5.1 Termos e definições

**Rota:** um destino possível para o pedido, com seu modelo, ferramentas e prompt próprios.

**Router:** a função que recebe o pedido e devolve o nome de uma rota.

**Rota de fallback:** o destino usado quando o router não tem confiança suficiente. Costuma ser o caminho mais genérico e seguro, ou o atendimento humano.

**Embedding:** vetor numérico que representa o significado de um texto. Textos com significado parecido têm vetores próximos (ver [2. Contexto, janela e recuperação](../context-engineering/2-contexto-janela-e-recuperacao.md)).

**Cascade:** variante em que o pedido vai primeiro para o modelo mais barato e só sobe para um modelo maior se a resposta não for considerada boa o suficiente.

## 5.2 Como funciona

```text
                     ┌──► rota "duvida_simples"  → modelo pequeno
pedido ──► router ───┼──► rota "dados_da_conta"  → fluxo com ferramentas
                     ├──► rota "problema_tecnico" → modelo grande + base técnica (RAG)
                     └──► fallback               → atendente humano
```

O router vale a pena quando quatro condições aparecem juntas:

1. os pedidos são de fato de tipos diferentes;
2. tratar cada tipo de forma diferente traz ganho claro de custo ou de qualidade;
3. errar a rota tem consequência administrável, porque existe um fallback;
4. a decisão de rota é barata e rápida em comparação com o processamento principal.

## 5.3 Três formas de decidir a rota

| Abordagem | Como decide | Pontos fortes | Pontos fracos |
|---|---|---|---|
| Regras | Palavras-chave, expressões regulares, campos do formulário | Custo quase zero, previsível, fácil de auditar | Frágil a variações de escrita; cada rota nova exige código novo |
| Embeddings | Compara o pedido com exemplos rotulados de cada rota | Barato e rápido; rotas crescem com mais exemplos, sem código novo | Erra em diferenças sutis; os exemplos precisam ser mantidos |
| LLM classificador | Um modelo pequeno recebe o pedido e a descrição das rotas e escolhe uma | Lida com ambiguidade; rota nova é só uma descrição a mais | Uma chamada extra por pedido, com custo e latência; resultado menos previsível |

Um arranjo recomendado é o **híbrido**: regras resolvem os casos óbvios, embeddings resolvem os casos parecidos com exemplos conhecidos, e o LLM entra só quando os dois anteriores não têm confiança. Cada camada só é chamada se a anterior não decidiu.

```python
# Ilustrativo: router híbrido em camadas. embed() e classificar_com_llm() representam
# chamadas a um modelo de embeddings e a um LLM pequeno.
import re
import numpy as np

ROTAS = {"duvida_simples", "dados_da_conta", "problema_tecnico"}

REGRAS = [
    (re.compile(r"\b(segunda via|boleto|fatura)\b", re.I), "dados_da_conta"),
    (re.compile(r"\b(erro \d{3}|não carrega|travou)\b", re.I), "problema_tecnico"),
]

EXEMPLOS = {  # vetores calculados uma vez, na inicialização
    "duvida_simples": [embed("Qual o horário de atendimento?"), embed("Vocês emitem nota fiscal?")],
    "dados_da_conta": [embed("Quero mudar a data de vencimento"), embed("Quanto devo hoje?")],
    "problema_tecnico": [embed("A integração parou de enviar pedidos"), embed("O relatório sai em branco")],
}

def cosseno(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def rotear(pedido: str, limiar: float = 0.80) -> str:
    for padrao, rota in REGRAS:                      # 1. regras
        if padrao.search(pedido):
            return rota

    vetor = embed(pedido)                            # 2. exemplo mais parecido
    melhor_rota, melhor_score = max(
        ((rota, max(cosseno(vetor, ex) for ex in exemplos)) for rota, exemplos in EXEMPLOS.items()),
        key=lambda par: par[1],
    )
    if melhor_score >= limiar:
        return melhor_rota

    rota = classificar_com_llm(pedido, sorted(ROTAS))  # 3. LLM para os ambíguos
    return rota if rota in ROTAS else "fallback"       # nunca confie em rota fora da lista
```

Dois detalhes importam: o limiar de similaridade precisa ser calibrado com pedidos reais (não existe um valor universal), e a resposta do LLM é conferida contra a lista de rotas antes de ser usada.

## 5.4 Custo: onde o router se paga

O ganho principal do router é econômico. Sem ele, todos os pedidos vão para o modelo capaz de lidar com o pior caso. Com ele, o modelo caro só recebe o que precisa dele.

**Exemplo ilustrativo** (números hipotéticos, só para mostrar a conta): se 60% dos pedidos podem ir para um modelo que custa 1/20 do modelo grande, o custo relativo por pedido passa a ser:

```text
0,60 × 0,05  +  0,40 × 1,00  =  0,43   →   cerca de 57% de redução
```

A conta só fecha se forem incluídos:

- **o custo do próprio router**, que é desprezível para regras, pequeno para embeddings e relevante para um LLM classificador;
- **o custo dos erros de rota**, como pedidos difíceis mandados ao modelo pequeno, que respondem mal e voltam como reclamação ou retrabalho.

Para pedidos repetidos com frequência, guardar a rota já decidida em cache elimina o custo do router nesses casos.

### Cascade

Na variante cascade, não há classificação prévia: o pedido vai ao modelo mais barato, um verificador avalia a resposta e, se ela não passar, o pedido sobe para o próximo modelo. O FrugalGPT (Chen et al., 2023) estudou essa estratégia, com um componente aprendido que decide quando escalar, e relatou desempenho equivalente ao do GPT-4 com até 98% de redução de custo nos conjuntos avaliados. O preço é latência maior nos pedidos difíceis, que passam por mais de um modelo.

## 5.5 Limites, trade-offs e quando usar

- **Router não é Supervisor.** O router decide uma vez, na entrada. Se a tarefa exige várias decisões ao longo da execução sobre quem trabalha a seguir, o padrão certo é o [Supervisor](6-supervisor.md).
- **Rotas demais confundem.** Com muitas rotas parecidas, a precisão cai em qualquer abordagem. Agrupe rotas próximas ou crie um segundo nível de roteamento.
- **Distribuição muda com o tempo.** Novos produtos e novas dúvidas criam pedidos que nenhum exemplo cobre. Monitore a taxa de fallback e a de rotas corrigidas manualmente.
- **Sem heterogeneidade real, não há ganho.** Se quase todos os pedidos precisam do mesmo modelo, o router só adiciona latência.

## 5.6 Resumo

O router classifica cada pedido uma única vez e o envia para a rota adequada. Regras são baratas e previsíveis, embeddings generalizam a partir de exemplos e um LLM classificador resolve ambiguidade com custo maior; a combinação em camadas, com fallback, é o arranjo mais robusto. O ganho principal é de custo, desde que a conta inclua o custo do router e dos erros de rota. O cascade troca a classificação prévia por tentativas em modelos cada vez maiores.

## Fontes

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), Anthropic, publicado em 2024-12-19, consultado em 2026-10-28.
- Chen et al., [FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance](https://arxiv.org/abs/2305.05176), 2023, consultado em 2026-10-28.
