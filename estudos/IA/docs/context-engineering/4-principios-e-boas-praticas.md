# 4. Princípios e boas práticas

Os documentos anteriores cobriram o quê (conceitos), como recuperar informação (RAG) e como persistir conhecimento (memória e estado). Este documento cobre como montar o contexto final enviado ao modelo a cada chamada: os princípios que guiam essa montagem, e as duas técnicas operacionais que tornam esses princípios aplicáveis na prática, context injection e pruning.

## 4.1 Os quatro princípios

**Relevância:** incluir apenas informação que tem chance real de influenciar a resposta para a tarefa atual. Informação genérica ou tangencial compete por espaço com informação que importa, e pode até distrair o modelo do que é central.

**Organização:** estruturar o contexto de forma que sua função fique clara, instrução separada de dado, documento recuperado separado de histórico de conversa, em vez de despejar tudo como um bloco de texto corrido. Isso facilita tanto a interpretação pelo modelo quanto a depuração por quem está construindo o sistema.

**Clareza:** eliminar ambiguidade na forma como a informação é apresentada. Um documento recuperado sem indicar sua fonte ou data, por exemplo, deixa o modelo (e quem avalia a resposta depois) sem saber se aquela informação ainda é válida.

**Economia de tokens:** cada token no contexto tem um custo, em dinheiro e em espaço disputado dentro da janela de contexto (documento 2). Incluir informação de forma verbosa quando uma versão mais direta transmitiria o mesmo significado é desperdício que se acumula, especialmente em sistemas com muitas chamadas.

Esses quatro princípios não atuam isoladamente, eles frequentemente entram em tensão. Mais organização (por exemplo, marcadores XML explícitos em cada seção) custa tokens adicionais, o que tensiona com economia. Mais relevância (filtrar agressivamente o que entra no contexto) pode reduzir clareza se cortar informação que davacontexto necessário para entender o que sobrou. Não existe uma fórmula fixa que resolve essa tensão para todo caso, a decisão precisa ser calibrada para cada aplicação, com base em avaliação real (documento 1, seção 1.7), não apenas em teoria.

## 4.2 Exemplo: contexto malformado vs. bem formado

A melhor forma de tornar esses princípios concretos é comparar diretamente dois contextos para a mesma tarefa.

**Cenário:** um assistente de suporte precisa responder a pergunta de um cliente sobre política de reembolso, com acesso a um histórico de conversa e a um documento recuperado por RAG.

**Contexto malformado**, violando os quatro princípios simultaneamente:

```
Você é um assistente. Responda o cliente.

Histórico: oi, tudo bem? sim como posso ajudar? queria saber sobre
reembolso. Reembolsos são processados em até 7 dias úteis após a
aprovação da solicitação, respeitando a política vigente descrita
no documento interno de atendimento ao cliente versão 3, que também
cobre trocas, garantia estendida e informações de frete reverso para
produtos com defeito de fabricação constatado por laudo técnico.
ok mas e se eu já usei o produto

Pergunta: posso devolver um produto que já usei?
```

Problemas deste contexto, ligados diretamente aos quatro princípios: o histórico de conversa e o documento recuperado estão misturados em um único bloco, sem marcação (viola organização); o documento trazido fala de prazo de reembolso, frete reverso e garantia estendida, quando a pergunta real é sobre devolução de produto já usado, o que é um tópico relacionado mas distinto (viola relevância); não há indicação de qual parte é instrução, qual é histórico e qual é documento recuperado, nem a data ou versão clara do documento usado (viola clareza); o documento completo foi incluído mesmo que apenas uma fração dele seja potencialmente útil para a pergunta (viola economia de tokens).

**Contexto bem formado**, para a mesma tarefa:

```xml
<instrucoes>
Você é um assistente de suporte. Responda com base apenas no
contexto fornecido abaixo. Se a informação não estiver disponível,
diga que vai verificar e não invente uma resposta.
</instrucoes>

<historico_conversa>
Cliente: Queria saber sobre reembolso.
Assistente: Claro, posso ajudar. Qual sua dúvida específica?
</historico_conversa>

<documentos_recuperados>
<documento fonte="politica_devolucao.md" atualizado_em="2026-08-15">
Produtos podem ser devolvidos em até 30 dias após a compra. Produtos
sem indício de uso têm devolução processada automaticamente. Produtos
com indício de uso passam por avaliação e podem ter reembolso parcial.
</documento>
</documentos_recuperados>

<pergunta_atual>
Posso devolver um produto que já usei?
</pergunta_atual>
```

Este segundo contexto resolve os quatro problemas: cada bloco tem uma função marcada explicitamente (organização); apenas o documento relevante à pergunta real foi incluído, não o documento genérico de política completa (relevância); a fonte e a data do documento estão visíveis, permitindo rastrear a informação e saber se ainda é atual (clareza); e o conteúdo foi resumido ao trecho pertinente, em vez do documento inteiro (economia de tokens). A instrução de "não invente uma resposta" também reforça groundedness, tema já visto no documento 1.

Em código, a montagem desse segundo contexto segue um padrão direto:

```python
def montar_prompt(instrucoes: str, historico: list[dict], documentos: list[dict], pergunta: str) -> str:
    historico_formatado = "\n".join(
        f"{'Cliente' if m['role'] == 'user' else 'Assistente'}: {m['content']}"
        for m in historico
    )

    documentos_formatados = "\n".join(
        f'<documento fonte="{doc["fonte"]}" atualizado_em="{doc["data"]}">\n{doc["trecho"]}\n</documento>'
        for doc in documentos
    )

    return f"""<instrucoes>
{instrucoes}
</instrucoes>

<historico_conversa>
{historico_formatado}
</historico_conversa>

<documentos_recuperados>
{documentos_formatados}
</documentos_recuperados>

<pergunta_atual>
{pergunta}
</pergunta_atual>"""
```

## 4.3 Context injection

Context injection é o processo de decidir, a cada chamada ao modelo, quais blocos de contexto efetivamente entram no prompt final, com base na tarefa específica daquele momento. O nome vem do paralelo com injeção de dependência em engenharia de software: em vez de um prompt fixo e estático, o contexto é "injetado" dinamicamente, montado sob demanda.

Isso significa que o mesmo sistema pode montar prompts bem diferentes para perguntas diferentes, mesmo usando a mesma instrução de base:

```python
class MontadorDeContexto:
    def __init__(self, memoria_semantica, memoria_longo_prazo, instrucoes_base: str):
        self.memoria_semantica = memoria_semantica
        self.memoria_longo_prazo = memoria_longo_prazo
        self.instrucoes_base = instrucoes_base

    def montar_para_pergunta(self, usuario_id: str, pergunta: str, historico: list[dict]) -> str:
        # Recupera apenas memória relevante à pergunta atual (documento 2 e 3),
        # em vez de injetar toda a memória do usuário em toda chamada.
        fatos_relevantes = self.memoria_semantica.buscar_relevante(usuario_id, pergunta, n_resultados=3)
        preferencias = self.memoria_longo_prazo.carregar_fatos(usuario_id)

        blocos = [f"<instrucoes>{self.instrucoes_base}</instrucoes>"]

        if preferencias:
            blocos.append(f"<preferencias_usuario>{preferencias}</preferencias_usuario>")

        if fatos_relevantes:
            fatos_formatados = "\n".join(fatos_relevantes)
            blocos.append(f"<memoria_relevante>{fatos_formatados}</memoria_relevante>")

        blocos.append(f"<pergunta_atual>{pergunta}</pergunta_atual>")

        return "\n\n".join(blocos)
```

O ponto central deste exemplo é que `fatos_relevantes` é buscado por similaridade com a pergunta atual, não despejado por inteiro: isso é o que mantém o contexto focado em relevância (seção 4.1), em vez de crescer sem controle a cada novo fato que o usuário acumula ao longo do tempo. Um erro comum de iniciantes em context injection é confundir "ter memória disponível" com "incluir toda memória disponível em todo prompt": a primeira é o objetivo, a segunda é o caminho mais rápido para estourar a janela de contexto com informação majoritariamente irrelevante para a pergunta específica.

## 4.4 Pruning

Pruning é o processo complementar: remover ou resumir informação que já está no contexto, mas deixou de caber ou deixou de ser a prioridade, à medida que uma conversa ou uma tarefa de agente cresce além do que a janela de contexto comporta.

A forma mais simples de pruning, já vista no documento 3, é truncar o histórico, descartando as mensagens mais antigas. Essa abordagem é fácil de implementar, mas tem um custo real: informação relevante dita no início de uma conversa longa se perde silenciosamente.

Uma estratégia mais cuidadosa combina truncamento com resumo: em vez de descartar mensagens antigas, elas são condensadas em um resumo mais curto, que preserva a essência sem ocupar o espaço de token do histórico completo.

```python
class GerenciadorDeHistorico:
    def __init__(self, llm_client, limite_mensagens_recentes: int = 10):
        self.llm_client = llm_client
        self.limite_mensagens_recentes = limite_mensagens_recentes
        self.resumo_acumulado: str = ""
        self.mensagens_recentes: list[dict] = []

    def adicionar_mensagem(self, mensagem: dict) -> None:
        self.mensagens_recentes.append(mensagem)

        if len(self.mensagens_recentes) > self.limite_mensagens_recentes:
            mensagens_a_resumir = self.mensagens_recentes[:-self.limite_mensagens_recentes]
            self.mensagens_recentes = self.mensagens_recentes[-self.limite_mensagens_recentes:]
            self._atualizar_resumo(mensagens_a_resumir)

    def _atualizar_resumo(self, mensagens: list[dict]) -> None:
        texto_mensagens = "\n".join(f"{m['role']}: {m['content']}" for m in mensagens)
        prompt_resumo = f"""Resumo da conversa até agora: {self.resumo_acumulado}

Novas mensagens a incorporar ao resumo:
{texto_mensagens}

Gere um resumo atualizado e conciso, preservando decisões e fatos importantes."""

        self.resumo_acumulado = self.llm_client.generate(prompt_resumo)

    def contexto_atual(self) -> str:
        mensagens_formatadas = "\n".join(
            f"{m['role']}: {m['content']}" for m in self.mensagens_recentes
        )
        return f"<resumo_conversa_anterior>{self.resumo_acumulado}</resumo_conversa_anterior>\n\n<mensagens_recentes>{mensagens_formatadas}</mensagens_recentes>"
```

Esta estratégia tem um custo adicional óbvio: gerar o resumo exige uma chamada extra ao modelo, o que soma latência e custo de tokens (tensionando diretamente com o princípio de economia da seção 4.1). A decisão entre truncamento simples e resumo incremental depende de quanto a aplicação pode tolerar perder informação do início da conversa, versus quanto pode tolerar o custo extra de gerar resumos.

Outra forma de pruning, mais seletiva, é remover apenas blocos específicos que perderam relevância, sem tocar no restante do contexto, por exemplo, remover um documento recuperado por RAG que foi usado para responder uma pergunta anterior na mesma sessão, mas que não tem relação com a pergunta atual, em vez de deixá-lo acumulado indefinidamente a cada nova pergunta da mesma conversa.

## 4.5 Boas práticas de implementação

**Meça antes de otimizar:** context injection e pruning são, antes de tudo, decisões de engenharia que precisam de dados para serem calibradas corretamente. Registre groundedness, taxa de resposta sem suporte e custo de token por chamada (documento 1, seção 1.7) antes de decidir se uma estratégia de pruning está sendo agressiva demais ou branda demais.

**Prefira cortar documento, não truncar no meio de uma frase:** ao fazer pruning de um documento recuperado por RAG, corte por unidade de sentido (um parágrafo, uma seção), nunca por número fixo de caracteres que pode partir uma frase ao meio, pelo mesmo motivo já discutido para chunking no documento 2.

**Marque explicitamente o que foi removido:** quando pruning descarta uma parte do histórico ou de um documento, é útil deixar um marcador (mesmo que não visível ao usuário final) indicando que houve corte, para facilitar depuração quando uma resposta parecer faltar contexto que deveria estar disponível.

**Separe o que é injetado sempre do que é injetado sob demanda:** instrução do sistema e, em alguns casos, poucas preferências centrais do usuário fazem sentido em todo prompt. Memória semântica e documentos recuperados, por sua natureza, deveriam ser buscados e injetados apenas quando relevantes à pergunta atual (seção 4.3), não anexados de forma fixa a cada chamada.

**Teste o sistema com contexto propositalmente malformado:** incluir um teste automatizado que verifica como o sistema se comporta quando um documento recuperado contém uma instrução embutida (o cenário de prompt injection do documento 1), ou quando o histórico está incompleto por causa de pruning agressivo, ajuda a identificar falhas antes que aconteçam em produção.

## 4.6 Resumo

Relevância, organização, clareza e economia de tokens são os quatro princípios que guiam a montagem de contexto, e eles frequentemente entram em tensão entre si, exigindo calibração baseada em avaliação real, não em teoria. Context injection é a prática de montar o contexto dinamicamente, buscando apenas o que é relevante para a tarefa atual, em vez de anexar tudo que está disponível. Pruning é o processo complementar de remover ou resumir informação que deixou de caber ou de ser prioridade, à medida que uma conversa ou tarefa cresce. Dominar os dois é o que diferencia um sistema que aplica os quatro princípios na prática de um sistema que apenas os cita.
