# 5. A camada de contexto em uma arquitetura de agente de IA

Os documentos anteriores trataram cada peça isoladamente: recuperação (documento 2), memória e estado (documento 3), montagem do contexto final (documento 4). Este documento mostra como essas peças se conectam dentro de um sistema real, na ordem em que uma requisição efetivamente passa por elas, e cobre os componentes que ainda não tinham sido tratados: tooling, orquestração, observabilidade e diagnóstico de falhas.

## 5.1 O fluxo de ponta a ponta

Antes de falar em componentes isolados, vale ver o caminho completo que uma pergunta percorre em um sistema agentic típico, com RAG e tooling:

```
1. Pergunta do usuário chega ao sistema
2. Orquestrador decide: isso precisa de busca de contexto, de uma ferramenta, ou pode ser respondido direto?
3. Se precisa de contexto: embedding da pergunta -> busca vetorial -> re-ranking (documento 2)
4. Memória relevante é buscada (documento 3) e injetada junto ao contexto recuperado (documento 4)
5. Prompt final é montado e enviado ao LLM
6. LLM responde com texto, ou com uma decisão de chamar uma ferramenta (tool call)
7. Se for tool call: o orquestrador executa a ferramenta, captura o resultado,
   e volta ao passo 5 com o resultado da ferramenta incorporado ao contexto
8. Quando o LLM retorna uma resposta final (não mais um tool call), ela é entregue ao usuário
9. Em paralelo a todos os passos acima, cada etapa é registrada para observabilidade (seção 5.4)
```

O passo 7 é o que transforma esse fluxo de "uma chamada de RAG" em "um agente": existe um loop, não uma única passagem linear. O número de voltas nesse loop não é fixo, depende de quantas ferramentas o modelo decide chamar até considerar a tarefa completa, o que é também a origem de boa parte dos riscos de confiabilidade tratados na seção 5.5.

## 5.2 Componentes do sistema

Cada caixa do fluxo acima corresponde a um componente com responsabilidade própria. Esta lista não repete os elementos de contexto do documento 1 (instruções, histórico, memória, documentos, estado), que descrevem o que compõe o contexto; aqui o foco é em qual peça de software é responsável por produzir ou consumir cada um desses elementos.

**Orquestrador:** o componente central, que decide a sequência de passos do fluxo acima: quando buscar contexto, quando chamar o LLM, quando executar uma ferramenta, e quando considerar a tarefa concluída. É o componente mais específico de cada aplicação, já que a lógica de decisão depende diretamente do domínio.

**Camada de recuperação:** os componentes de busca vetorial, chunking e re-ranking vistos no documento 2, responsáveis por transformar uma pergunta em um conjunto de documentos relevantes.

**Camada de memória:** os armazenamentos de memória de curto prazo, longo prazo, semântica e episódica vistos no documento 3, responsáveis por persistir e recuperar o que o sistema "sabe" entre interações.

**Montador de contexto:** o componente que decide, a cada chamada, o que efetivamente entra no prompt final, aplicando os princípios e técnicas do documento 4 (relevância, injeção, pruning).

**Registro de ferramentas (tool registry):** a definição de quais ferramentas o agente pode chamar, com seus parâmetros e descrições. Tratado em detalhe na seção 5.3.

**Executor de ferramentas:** o componente que efetivamente roda o código de uma ferramenta quando o LLM decide chamá-la, captura o resultado (ou o erro), e devolve isso ao orquestrador para ser incorporado ao próximo prompt.

**Camada de observabilidade:** instrumentação que registra cada chamada ao LLM, cada chamada de ferramenta, e os resultados de cada etapa, para permitir diagnóstico posterior. Tratada na seção 5.4.

## 5.3 Tooling: como um agente usa ferramentas

Tool use (ou function calling) é o mecanismo pelo qual um LLM, em vez de apenas gerar texto livre, retorna uma estrutura indicando que uma função específica deveria ser chamada, com quais argumentos. O modelo nunca executa a função diretamente, ele apenas decide e descreve a chamada; a execução é responsabilidade do orquestrador.

Cada ferramenta precisa ser descrita ao modelo de forma que ele saiba quando e como usá-la. Essa descrição, no formato usado pela maioria das APIs de LLM atuais, é um schema JSON:

```python
ferramentas_disponiveis = [
    {
        "name": "consultar_status_pedido",
        "description": "Consulta o status atual de um pedido pelo número do pedido. Use quando o usuário perguntar sobre um pedido específico.",
        "parameters": {
            "type": "object",
            "properties": {
                "numero_pedido": {
                    "type": "string",
                    "description": "O número de identificação do pedido, por exemplo PED-12345",
                },
            },
            "required": ["numero_pedido"],
        },
    },
    {
        "name": "iniciar_devolucao",
        "description": "Inicia o processo de devolução de um produto. Use apenas após confirmar com o usuário que ele deseja devolver.",
        "parameters": {
            "type": "object",
            "properties": {
                "numero_pedido": {"type": "string"},
                "motivo": {"type": "string", "description": "Motivo da devolução informado pelo usuário"},
            },
            "required": ["numero_pedido", "motivo"],
        },
    },
]
```

A qualidade da descrição (`description`) de cada ferramenta e de cada parâmetro importa tanto quanto a qualidade de uma instrução de sistema: é a partir dela que o modelo decide se e quando chamar aquela ferramenta. Uma descrição vaga, como apenas `"Consulta pedido"`, dá ao modelo menos sinal sobre quando usar a ferramenta do que uma descrição que explica o gatilho esperado, como no exemplo acima.

O orquestrador precisa então mapear o nome da ferramenta retornado pelo modelo para o código real que a executa:

```python
def consultar_status_pedido(numero_pedido: str) -> dict:
    # Lógica real de consulta ao sistema de pedidos
    return {"numero_pedido": numero_pedido, "status": "Em transporte"}

def iniciar_devolucao(numero_pedido: str, motivo: str) -> dict:
    # Lógica real de abertura de devolução
    return {"numero_pedido": numero_pedido, "devolucao_id": "DEV-789", "status": "Iniciada"}

executores = {
    "consultar_status_pedido": consultar_status_pedido,
    "iniciar_devolucao": iniciar_devolucao,
}

def executar_ferramenta(nome_ferramenta: str, argumentos: dict) -> dict:
    if nome_ferramenta not in executores:
        return {"erro": f"Ferramenta '{nome_ferramenta}' não reconhecida."}

    try:
        return executores[nome_ferramenta](**argumentos)
    except Exception as erro:
        # Um erro de execução vira parte do contexto da próxima chamada,
        # não uma exceção que derruba o processo do agente (seção 5.5).
        return {"erro": f"Falha ao executar '{nome_ferramenta}': {str(erro)}"}
```

O `try/except` ali não é incidental: uma ferramenta pode falhar por motivos completamente alheios ao modelo (um serviço externo fora do ar, um timeout), e o agente precisa conseguir continuar o loop de forma sensata mesmo diante dessa falha, em vez de travar. O resultado, incluindo um erro, volta para o modelo como parte do próximo contexto, permitindo que ele decida como reagir, por exemplo, informando o usuário que não conseguiu completar a ação.

Como visto no documento 1, seção 1.3, uma ferramenta que executa uma ação de alto risco (enviar algo, modificar um registro, iniciar um processo irreversível) nunca deveria ser chamada automaticamente com base apenas na decisão do modelo, sem algum tipo de confirmação ou limite de permissão definido pelo sistema, exatamente pelo risco de uma instrução maliciosa embutida em um documento recuperado influenciar essa decisão.

## 5.4 Observabilidade

Observabilidade, neste contexto, é a capacidade de responder, depois do fato, perguntas como: por que o agente deu essa resposta, por que chamou essa ferramenta, quanto essa interação custou, e onde um comportamento inesperado começou. Sem instrumentação explícita, um sistema agentic é uma caixa-preta: o loop de decisão do passo 7 da seção 5.1 pode rodar várias vezes antes de retornar uma resposta final, e sem registro de cada volta, é praticamente impossível entender o que aconteceu quando algo sai errado.

Os elementos mínimos de observabilidade para um sistema desses incluem registrar, para cada chamada ao LLM: o prompt completo enviado (contexto final, após toda a montagem dos documentos 2 a 4), a resposta recebida, se houve uma tool call e qual, quantos tokens foram usados, e quanto tempo a chamada levou.

```python
import time
import uuid
import logging

logger = logging.getLogger("agente.observabilidade")

class RegistroDeExecucao:
    def __init__(self):
        self.trace_id = str(uuid.uuid4())
        self.passos: list[dict] = []

    def registrar_chamada_llm(self, prompt: str, resposta: str, tokens_usados: int, duracao_segundos: float) -> None:
        self.passos.append({
            "tipo": "chamada_llm",
            "prompt_tamanho_caracteres": len(prompt),
            "resposta": resposta[:200],  # trunca para log, não grava a resposta inteira
            "tokens_usados": tokens_usados,
            "duracao_segundos": duracao_segundos,
        })
        logger.info(f"[{self.trace_id}] Chamada LLM: {tokens_usados} tokens, {duracao_segundos:.2f}s")

    def registrar_chamada_ferramenta(self, nome_ferramenta: str, argumentos: dict, resultado: dict, duracao_segundos: float) -> None:
        self.passos.append({
            "tipo": "chamada_ferramenta",
            "ferramenta": nome_ferramenta,
            "argumentos": argumentos,
            "resultado": resultado,
            "duracao_segundos": duracao_segundos,
        })
        logger.info(f"[{self.trace_id}] Ferramenta '{nome_ferramenta}': {duracao_segundos:.2f}s")

    def resumo(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "total_passos": len(self.passos),
            "total_tokens": sum(p.get("tokens_usados", 0) for p in self.passos),
            "duracao_total_segundos": sum(p["duracao_segundos"] for p in self.passos),
        }
```

Um `trace_id` único por execução (não por chamada individual) é o que permite reconstruir, depois, a sequência inteira de passos de uma única interação do usuário, mesmo que ela tenha envolvido múltiplas voltas no loop de ação-observação. Ferramentas especializadas de observabilidade para LLM, como LangSmith, Langfuse ou Arize Phoenix, formalizam esse mesmo conceito de trace com recursos adicionais de visualização e comparação entre execuções, mas o princípio por trás é o mesmo deste exemplo simplificado.

## 5.5 Engenharia de confiabilidade e diagnóstico de falhas

Diferente de um sistema tradicional, onde uma falha geralmente é determinística (a mesma entrada produz o mesmo erro), falhas em sistemas com LLM podem ser intermitentes: a mesma pergunta, no mesmo contexto, pode ocasionalmente gerar uma resposta correta e ocasionalmente uma resposta errada, por causa da natureza probabilística da geração de texto. Isso exige práticas de confiabilidade adaptadas a essa realidade.

**Retry com critério, não automático:** repetir uma chamada que falhou (por erro de rede, por exemplo) é uma prática padrão, mas repetir automaticamente uma chamada que teve uma resposta de baixa qualidade (não um erro técnico, mas uma resposta que não atende ao esperado) é mais delicado. Um retry ingênuo pode gerar o mesmo problema de novo, já que o contexto enviado não mudou.

```python
def chamar_llm_com_retry(prompt: str, llm_client, max_tentativas: int = 3) -> str:
    ultimo_erro = None

    for tentativa in range(max_tentativas):
        try:
            return llm_client.generate(prompt)
        except RateLimitError:
            # Erro técnico: esperar e tentar de novo faz sentido.
            tempo_espera = 2 ** tentativa  # backoff exponencial
            time.sleep(tempo_espera)
            continue
        except Exception as erro:
            ultimo_erro = erro
            break  # erro não recuperável por retry simples, não insiste

    raise RuntimeError(f"Falha ao chamar LLM após {max_tentativas} tentativas: {ultimo_erro}")
```

**Validação de saída estruturada:** quando o modelo deve retornar um formato específico (JSON, uma tool call com parâmetros de tipos corretos), validar essa saída antes de usá-la evita que um erro de formatação do modelo se propague como um erro mais difícil de rastrear mais adiante no sistema, por exemplo, dentro do executor de ferramentas da seção 5.3.

**Circuit breaker para ferramentas externas:** se uma ferramenta específica está falhando repetidamente (um serviço externo fora do ar, por exemplo), interromper temporariamente as tentativas de chamá-la, em vez de deixar o agente insistir repetidamente, economiza tempo e custo, e permite que o agente informe o usuário de forma mais direta em vez de ficar tentando algo que não vai funcionar.

**Limite no número de voltas do loop:** sem um limite explícito de quantas vezes o loop de ação-observação (passo 7 da seção 5.1) pode repetir, um agente mal calibrado pode entrar em um ciclo chamando ferramentas repetidamente sem avançar em direção a uma resposta final, consumindo tokens e tempo sem necessidade.

```python
def executar_loop_agente(pergunta: str, llm_client, max_iteracoes: int = 5) -> str:
    contexto = montar_contexto_inicial(pergunta)

    for iteracao in range(max_iteracoes):
        resposta = llm_client.generate(contexto, tools=ferramentas_disponiveis)

        if resposta.tipo == "texto_final":
            return resposta.conteudo

        resultado_ferramenta = executar_ferramenta(resposta.nome_ferramenta, resposta.argumentos)
        contexto = adicionar_resultado_ao_contexto(contexto, resposta, resultado_ferramenta)

    return "Não foi possível completar a tarefa dentro do limite de tentativas."
```

**Diagnóstico com os registros de observabilidade:** quando um usuário reporta uma resposta ruim, o primeiro passo de diagnóstico é recuperar o trace completo daquela execução (seção 5.4) e verificar, em ordem: o contexto recuperado foi relevante (problema de recuperação, documento 2)? A memória injetada estava correta (problema de memória, documento 3)? O prompt final estava bem montado (problema de injeção ou pruning, documento 4)? O modelo chamou a ferramenta certa, com os argumentos certos (problema de tooling, seção 5.3)? Ou o modelo teve acesso a tudo que precisava e ainda assim gerou uma resposta ruim (problema do próprio modelo, que nenhuma camada de contexto resolve sozinha)? Seguir essa ordem evita o erro comum de assumir que toda resposta ruim é "o modelo alucinando", quando com frequência a causa real está em uma das camadas anteriores ao modelo.

## 5.6 Benefícios condicionais e riscos

Uma camada de contexto bem arquitetada reduz a chance de respostas irrelevantes ou desatualizadas, permite que o sistema use informação proprietária sem precisar re-treinar o modelo, e viabiliza tarefas de múltiplos passos por meio de tooling. Nenhum desses benefícios é automático: eles dependem diretamente da qualidade de cada componente descrito neste documento, e de medição contínua (documento 1, seção 1.7) para confirmar que estão de fato sendo entregues.

Os riscos também são reais e já foram tratados ao longo da série: prompt injection via documentos recuperados ou resultados de ferramentas (documento 1), vazamento de memória entre usuários por falta de isolamento (documento 3), loops sem limite consumindo custo sem necessidade (seção 5.5 deste documento), e ferramentas de alto risco sendo chamadas sem supervisão adequada (seção 5.3). Nenhuma dessas é uma falha teórica rara, são os modos de falha mais comuns relatados em sistemas agentic reais em produção.

## 5.7 Resumo

Um sistema agentic conecta recuperação, memória, montagem de contexto, tooling e orquestração em um loop, não em uma passagem linear única. Tooling exige descrições de qualidade para que o modelo decida corretamente quando e como chamar cada ferramenta, e um executor que trate falhas como parte esperada do fluxo, não como exceção. Observabilidade, com rastreamento completo por execução, é o que torna possível diagnosticar qual camada específica falhou quando uma resposta sai errada, em vez de atribuir toda falha genericamente ao modelo. Engenharia de confiabilidade para esse tipo de sistema lida com uma característica que sistemas tradicionais não têm: a mesma entrada pode, ocasionalmente, produzir resultados diferentes, o que exige retry criterioso, limites explícitos de iteração, e validação de saída em cada etapa do loop.
