# 3. Memória e estado

Um LLM, por si só, não tem memória: cada chamada é processada de forma independente, sem nenhum traço do que aconteceu em chamadas anteriores, a menos que essa informação seja reenviada explicitamente dentro do prompt. Tudo que parece "memória" em um sistema com IA é, na verdade, uma camada construída fora do modelo, que decide o que persistir, onde persistir, e o que reinserir no contexto a cada nova chamada. Este documento cobre essa camada: os tipos de memória, como cada um é armazenado na prática, a diferença entre memória e estado, e como isso se complica quando mais de um agente está envolvido.

## 3.1 Memória não é um conceito único

É comum tratar "memória de um agente" como uma coisa só, mas na prática ela se divide em tipos com propósitos, formas de armazenamento e tempos de vida diferentes. Confundir esses tipos é uma causa comum de sistemas que ou esquecem informação importante, ou carregam contexto irrelevante em toda chamada.

**Memória de curto prazo:** o histórico da conversa ou da sessão atual. Vive enquanto a sessão está ativa e, na forma mais simples, é apenas a lista de mensagens trocadas até agora, reenviada a cada nova chamada ao modelo.

**Memória de longo prazo:** informação que precisa sobreviver entre sessões diferentes, por exemplo, uma preferência que o usuário mencionou semana passada e que deveria continuar valendo hoje, mesmo em uma conversa nova.

**Memória semântica:** fatos e conhecimento geral sobre o mundo ou sobre o domínio, organizados de forma que permita busca por significado, não por chave exata. Normalmente armazenada como embeddings em um banco vetorial (documento 2), o que permite recuperar um fato relevante mesmo que a pergunta atual não use as mesmas palavras usadas quando o fato foi registrado.

**Memória episódica:** o registro de eventos específicos que aconteceram, com seu contexto (quando, em que situação, com que resultado). Diferente da memória semântica (que generaliza um fato), a memória episódica preserva o episódio concreto: "na conversa de terça-feira, o usuário pediu para cancelar o pedido X e o cancelamento foi recusado por estar fora do prazo" é uma memória episódica; "o prazo de cancelamento é de 7 dias" é uma memória semântica extraída (ou generalizada) a partir de episódios como esse.

A tabela abaixo resume como cada tipo costuma ser armazenado na prática, já que a forma de armazenamento é o que torna cada tipo de memória útil para seu propósito específico:

| Tipo | Tempo de vida | Armazenamento típico | Forma de busca |
|---|---|---|---|
| Curto prazo | Sessão atual | Lista em memória do processo, ou cache (Redis) | Sequencial, por ordem cronológica |
| Longo prazo | Entre sessões | Banco relacional ou key-value, por usuário | Busca exata por chave (ex.: ID do usuário) |
| Semântica | Indefinido, até ser invalidada | Banco vetorial (embeddings) | Busca por similaridade |
| Episódica | Indefinido, geralmente com expiração | Banco vetorial ou documento estruturado, com metadados de data/contexto | Busca por similaridade, filtrada por metadados |

## 3.2 Memória de curto prazo na prática

A forma mais direta de memória de curto prazo é simplesmente reenviar o histórico de mensagens a cada chamada:

```python
class ConversaComMemoriaCurta:
    def __init__(self, llm_client, limite_mensagens: int = 20):
        self.llm_client = llm_client
        self.historico: list[dict] = []
        self.limite_mensagens = limite_mensagens

    def enviar(self, mensagem_usuario: str) -> str:
        self.historico.append({"role": "user", "content": mensagem_usuario})

        # Trunca o histórico para não estourar a janela de contexto (documento 2)
        historico_truncado = self.historico[-self.limite_mensagens:]

        resposta = self.llm_client.generate(messages=historico_truncado)
        self.historico.append({"role": "assistant", "content": resposta})

        return resposta
```

O truncamento por número fixo de mensagens (`limite_mensagens`) é a forma mais simples de lidar com o limite da janela de contexto, mas é também a mais ingênua: ela descarta as mensagens mais antigas, mesmo que uma delas contenha uma informação ainda relevante para a conversa atual. Estratégias mais refinadas de gerenciar esse corte, incluindo resumir em vez de simplesmente descartar, são tratadas no documento 4, na seção sobre pruning de contexto.

## 3.3 Memória de longo prazo e memória semântica na prática

Memória de longo prazo estruturada (fatos específicos e bem definidos sobre um usuário, como preferências ou dados de cadastro) costuma ser armazenada de forma convencional, em um banco relacional ou key-value, indexada pelo identificador do usuário:

```python
class MemoriaLongoPrazo:
    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def salvar_fato(self, usuario_id: str, chave: str, valor: str) -> None:
        self.conexao.execute(
            "INSERT INTO memoria_usuario (usuario_id, chave, valor, atualizado_em) "
            "VALUES (%s, %s, %s, NOW()) "
            "ON CONFLICT (usuario_id, chave) DO UPDATE SET valor = %s, atualizado_em = NOW()",
            (usuario_id, chave, valor, valor),
        )

    def carregar_fatos(self, usuario_id: str) -> dict:
        linhas = self.conexao.execute(
            "SELECT chave, valor FROM memoria_usuario WHERE usuario_id = %s",
            (usuario_id,),
        )
        return {chave: valor for chave, valor in linhas}
```

Já memória semântica, por precisar de busca por significado (não por chave exata), usa o mesmo mecanismo de embeddings e banco vetorial já visto no documento 2, aplicado agora a fatos sobre o usuário ou sobre interações passadas, em vez de documentos de uma base de conhecimento:

```python
class MemoriaSemantica:
    def __init__(self, colecao_vetorial, modelo_embedding):
        self.colecao = colecao_vetorial
        self.modelo = modelo_embedding

    def registrar(self, usuario_id: str, fato: str) -> None:
        embedding = self.modelo.encode([fato])[0]
        self.colecao.add(
            documents=[fato],
            embeddings=[embedding.tolist()],
            metadatas=[{"usuario_id": usuario_id}],
            ids=[f"{usuario_id}_{hash(fato)}"],
        )

    def buscar_relevante(self, usuario_id: str, consulta: str, n_resultados: int = 3) -> list[str]:
        embedding_consulta = self.modelo.encode([consulta])[0]
        resultado = self.colecao.query(
            query_embeddings=[embedding_consulta.tolist()],
            n_results=n_resultados,
            where={"usuario_id": usuario_id},
        )
        return resultado["documents"][0]
```

O parâmetro `where={"usuario_id": usuario_id}` é importante: ele restringe a busca por similaridade aos fatos daquele usuário específico, evitando que a memória semântica de uma pessoa vaze para a conversa de outra, um requisito básico de isolamento que fica fácil de esquecer quando se está focado apenas em fazer a busca por similaridade funcionar.

## 3.4 Diferença entre memória e estado

Memória e estado são frequentemente confundidos, mas respondem perguntas diferentes.

**Memória** responde "o que eu sei", geralmente de forma persistente e reutilizável entre tarefas diferentes. Uma preferência do usuário, um fato sobre o domínio, um evento passado relevante.

**Estado** responde "onde estou agora nesta tarefa específica". É tipicamente efêmero, relevante apenas durante a execução de uma tarefa ou de um loop de agente, e descartado (ou arquivado, não mais consultado ativamente) quando a tarefa termina.

Exemplo: em um agente que processa um pedido de reembolso, "o cliente já pediu reembolso duas vezes este mês" é memória (um fato que persiste e pode influenciar decisões futuras). Já "neste pedido específico, já validei o prazo, ainda falta validar o motivo da devolução" é estado (relevante apenas enquanto esse pedido específico está sendo processado, sem sentido fora desse contexto).

```python
class EstadoDaTarefa:
    def __init__(self, tarefa_id: str):
        self.tarefa_id = tarefa_id
        self.passos_concluidos: list[str] = []
        self.proximo_passo: str | None = None
        self.dados_coletados: dict = {}

    def marcar_concluido(self, passo: str) -> None:
        self.passos_concluidos.append(passo)

    def esta_completo(self, passos_necessarios: list[str]) -> bool:
        return all(passo in self.passos_concluidos for passo in passos_necessarios)
```

Um erro comum é persistir estado como se fosse memória (acumulando, para sempre, o detalhe de cada passo de cada tarefa já concluída), o que infla desnecessariamente o volume de dados armazenados sem agregar valor real: ninguém precisa saber, daqui a um ano, que passo 3 de uma tarefa já finalizada foi concluído às 14h32 de uma terça-feira específica. O oposto também é um erro: tratar memória como estado (descartando um fato relevante assim que a tarefa atual termina), perdendo informação que deveria ter persistido para interações futuras.

## 3.5 Estado e memória compartilhada entre agentes

Em um sistema com mais de um agente trabalhando na mesma tarefa, surge um problema que não existe com um único agente: como cada agente sabe o que os outros já fizeram, decidiram ou descobriram.

Duas abordagens comuns:

**Estado compartilhado centralizado:** todos os agentes leem e escrevem em um mesmo armazenamento (um banco de dados, uma estrutura em memória compartilhada, um blackboard), e cada um consulta esse estado antes de agir. Isso simplifica a coordenação, mas introduz a necessidade de controlar concorrência: dois agentes atualizando o mesmo estado ao mesmo tempo podem causar uma condição de corrida, da mesma forma que duas requisições concorrentes podem causar inconsistência em qualquer sistema distribuído tradicional.

```python
import threading

class EstadoCompartilhado:
    def __init__(self):
        self._lock = threading.Lock()
        self._dados: dict = {}

    def atualizar(self, chave: str, valor) -> None:
        with self._lock:
            self._dados[chave] = valor

    def ler(self, chave: str):
        with self._lock:
            return self._dados.get(chave)
```

**Mensagens entre agentes:** em vez de um estado compartilhado único, cada agente mantém seu próprio estado interno e se comunica com os outros por meio de mensagens explícitas (uma pergunta, uma resposta, uma notificação de que um passo foi concluído). Essa abordagem evita o problema de concorrência de escrita direta, mas exige que cada agente saiba explicitamente para quem enviar cada mensagem, e pode gerar lentidão se a coordenação exigir muitas idas e vindas.

Na prática, sistemas multi-agente maduros costumam combinar as duas abordagens: um estado compartilhado para fatos que todos precisam consultar (por exemplo, o status geral da tarefa), e mensagens diretas para coordenação pontual entre dois agentes específicos (por exemplo, um agente pedindo a outro que refaça uma etapa).

A escolha entre as duas abordagens é, no fundo, o mesmo tipo de decisão de arquitetura que já existe em sistemas distribuídos tradicionais, sem IA envolvida: consistência forte com um estado centralizado, com o custo de contenção em alta concorrência, versus desacoplamento por mensagens, com o custo de complexidade de coordenação. O fato de os "processos" envolvidos serem agentes de IA, em vez de microsserviços tradicionais, não elimina esse trade-off, apenas o reapresenta em um contexto novo.

## 3.6 Políticas de memória

Decisões de governança sobre memória não são um detalhe de implementação, são decisões de produto e de conformidade que precisam ser tomadas de forma explícita:

**Privacidade:** qual informação pode ser armazenada como memória de longo prazo, e qual deve ser mantida apenas como memória de curto prazo (descartada ao fim da sessão)? Dados sensíveis exigem cuidado redobrado antes de virarem memória persistente.

**Retenção:** por quanto tempo uma memória permanece válida? Um fato registrado há dois anos pode estar desatualizado; a política de memória deve prever expiração ou revalidação periódica, não assumir que tudo que foi registrado uma vez continua verdadeiro para sempre.

**Proveniência:** de onde veio cada memória, quem ou o que a registrou, e quando? Isso é essencial para poder auditar e, se necessário, corrigir ou remover uma memória específica sem precisar apagar tudo.

**Consentimento e controle do usuário:** o usuário sabe o que está sendo lembrado sobre ele, e tem como consultar, corrigir ou apagar essa memória? Isso vale tanto por boa prática quanto, dependendo da jurisdição, por exigência legal.

## 3.7 Resumo

Memória não é um conceito único: curto prazo, longo prazo, semântica e episódica têm propósitos e formas de armazenamento diferentes, e escolher a estrutura errada para o tipo de informação (por exemplo, tentar fazer busca por significado em um banco relacional simples) é uma fonte comum de sistemas que não encontram informação que, tecnicamente, já foi registrada. Memória (o que se sabe) e estado (onde se está em uma tarefa específica) são conceitos diferentes, e tratá-los como a mesma coisa leva tanto a excesso de dados irrelevantes quanto à perda de informação que deveria persistir. Em sistemas multi-agente, a coordenação de estado compartilhado reintroduz, no contexto de IA, os mesmos trade-offs clássicos de sistemas distribuídos entre consistência centralizada e comunicação por mensagens.
