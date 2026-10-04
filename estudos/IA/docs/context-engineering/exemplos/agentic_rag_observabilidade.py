import uuid, time, json, logging, re
from contextlib import contextmanager
from datetime import date, datetime
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# =========================================================================
# Infraestrutura mínima de observabilidade
# =========================================================================
logging.basicConfig(level = logging.INFO, format = "%(message)s")
log = logging.getLogger("rag_obs")

# Cada execução do pipeline = 1 trace. Cada operação dentro = 1 span.
trace_id = str(uuid.uuid4())
spans: list[dict] = []

# Tabela de preços (USD por 1M tokens) — observabilidade financeira
PRECO = {"claude-sonnet": {"in": 3.0, "out": 15.0}}

@contextmanager
def span(nome: str, **atributos):
    """Cronometra um bloco, captura atributos e emite log estruturado."""
    s = {
        "trace_id": trace_id,
        "span_id": uuid.uuid4().hex[:8],
        "name": nome,
        "start": datetime.utcnow().isoformat() + "Z",
        **atributos,
    }
    inicio = time.perf_counter()
    try:
        yield s
    finally:
        s["latency_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
        spans.append(s)
        log.info(json.dumps(s, default = str, ensure_ascii = False))

# =========================================================================
# Corpus simulado
# =========================================================================
corpus = [
    {"id": 1, "fonte": "doc_oficial", "data": date(2025, 1, 15),
     "texto": "Pipelines RAG combinam recuperação semântica com geração de linguagem."},
    {"id": 2, "fonte": "paper",       "data": date(2023, 5, 12),
     "texto": "HNSW é um algoritmo de busca aproximada por vizinhos mais próximos."},
    {"id": 3, "fonte": "doc_oficial", "data": date(2024, 6, 10),
     "texto": "Bancos relacionais usam SQL para consultas estruturadas."},
    {"id": 4, "fonte": "blog_random", "data": date(2020, 3, 1),
     "texto": "Receita de bolo de fubá com 3 ovos e 1 xícara de leite."},
    {"id": 5, "fonte": "paper",       "data": date(2024, 8, 20),
     "texto": "Cross-encoders avaliam pares query-documento com mais precisão que bi-encoders."},
    {"id": 6, "fonte": "paper",       "data": date(2025, 2, 28),
     "texto": "O HNSW organiza vetores em camadas hierárquicas e acelera buscas em alta dimensão."},
    {"id": 7, "fonte": "doc_oficial", "data": date(2024, 9, 5),
     "texto": "Embedding é a representação vetorial densa de texto."},
    {"id": 8, "fonte": "blog_random", "data": date(2022, 1, 1),
     "texto": "Bancos vetoriais armazenam embeddings para busca semântica."},
]

query = "Como funciona o algoritmo HNSW para busca vetorial?"

# =========================================================================
# Estágio 1: recuperação vetorial — instrumentado
# =========================================================================
with span("retrieval.bi_encoder", query = query, corpus_size = len(corpus)) as s:
    bi = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    q_emb = bi.encode(query)
    docs_emb = bi.encode([d["texto"] for d in corpus])
    sims = (docs_emb @ q_emb) / (np.linalg.norm(docs_emb, axis=1) * np.linalg.norm(q_emb))
    top_idx = np.argsort(sims)[::-1][:5]
    cand = [{**corpus[i], "s1": float(sims[i])} for i in top_idx]

    s["top_k"] = 5
    s["top_score"] = max(c["s1"] for c in cand)
    s["min_score"] = min(c["s1"] for c in cand)
    s["doc_ids"] = [c["id"] for c in cand]

# =========================================================================
# Estágio 2: reranking — instrumentado
# =========================================================================
with span("rerank.cross_encoder", input_size = len(cand)) as s:
    cross = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
    pares = [(query, c["texto"]) for c in cand]
    scores2 = cross.predict(pares)
    for c, score in zip(cand, scores2):
        c["s2"] = float(score)
    cand.sort(key=lambda c: c["s2"], reverse=True)

    s["top_score"] = cand[0]["s2"]
    s["doc_ids_after"] = [c["id"] for c in cand]

# =========================================================================
# Estágio 3: regras de negócio — instrumentado
# =========================================================================
PESO_FONTE = {"doc_oficial": 1.2, "paper": 1.1, "blog_random": 0.7}
HOJE = date(2025, 5, 1)

def fator_recencia(d):
    return max(0.5, 1.0 - (HOJE - d).days / 1000)

with span("business_rules", pesos_fonte=PESO_FONTE) as s:
    for c in cand:
        c["s3"] = c["s2"] * PESO_FONTE.get(c["fonte"], 1.0) * fator_recencia(c["data"])
    cand.sort(key=lambda c: c["s3"], reverse=True)
    s["doc_ids_final"] = [c["id"] for c in cand]

selecionados = cand[:3]

# =========================================================================
# Estágio 4: Agente de IA — instrumentado com sinais semânticos
# =========================================================================
from anthropic import Anthropic

llm = Anthropic()
MODELO = "claude-sonnet"

def agente_rag(query: str, contexto: list[dict]) -> dict:
    bloco = "\n\n".join(
        f"[{i+1}] (fonte: {c['fonte']}, data: {c['data']})\n{c['texto']}"
        for i, c in enumerate(contexto)
    )
    
    system = (
        "Você é um agente que responde perguntas técnicas usando APENAS o contexto fornecido.\n"
        "Regras estritas:\n"
        "1. Cada afirmação deve ser ancorada com [N] indicando o documento usado.\n"
        "2. Se o contexto não cobrir a pergunta, responda 'Informação insuficiente no contexto.'\n"
        "3. Seja direto e didático: no máximo 4 frases."
    )
    user = f"CONTEXTO:\n{bloco}\n\nPERGUNTA: {query}"

    with span("llm.generate", model = MODELO, contexto_docs = len(contexto)) as s:
        resp = llm.messages.create(
            model = MODELO, 
            max_tokens = 400, 
            system = system,
            messages = [{"role": "user", "content": user}],
        )
        texto = resp.content[0].text

        # ----- Sinais quantitativos (token economics) -----
        s["input_tokens"] = resp.usage.input_tokens
        s["output_tokens"] = resp.usage.output_tokens
        s["custo_usd"] = round(
            (resp.usage.input_tokens * PRECO[MODELO]["in"] +
             resp.usage.output_tokens * PRECO[MODELO]["out"]) / 1_000_000,
            6,
        )

        # ----- Sinais semânticos (qualidade da resposta) -----
        citacoes = re.findall(r"\[(\d+)\]", texto)
        s["citacoes_total"] = len(citacoes)
        s["citacoes_unicas"] = len(set(citacoes))
        s["abstencao"] = "Informação insuficiente" in texto

    return {"resposta": texto}

saida = agente_rag(query, selecionados)

# =========================================================================
# Relatório consolidado do trace
# =========================================================================
print("\n" + "=" * 60)
print(f"TRACE {trace_id}")
print("=" * 60)

latencia_total = sum(s["latency_ms"] for s in spans)
print(f"spans executados : {len(spans)}")
print(f"latência total   : {latencia_total:.0f} ms")
print("caminho crítico  : " + " → ".join(s["name"] for s in spans))

print("\nLatência por estágio:")
for s in spans:
    pct = s["latency_ms"] / latencia_total * 100
    barra = "█" * int(pct / 2)
    print(f"  {s['name']:30s} {s['latency_ms']:7.1f} ms  {barra} {pct:5.1f}%")

# Sinais do agente
gen = next(s for s in spans if s["name"] == "llm.generate")
docs_disponiveis = set(range(1, len(selecionados) + 1))
docs_citados = set(int(x) for x in re.findall(r"\[(\d+)\]", saida["resposta"]))

print(f"\nObservabilidade do agente:")
print(f"  modelo               : {gen['model']}")
print(f"  tokens (in/out)      : {gen['input_tokens']} / {gen['output_tokens']}")
print(f"  custo (USD)          : ${gen['custo_usd']}")
print(f"  citações na resposta : {gen['citacoes_total']} ({gen['citacoes_unicas']} únicas)")
print(f"  agente abstevê-se?   : {gen['abstencao']}")
print(f"  docs disponíveis     : {sorted(docs_disponiveis)}")
print(f"  docs efetivamente usados : {sorted(docs_citados)}")
print(f"  contexto desperdiçado    : {sorted(docs_disponiveis - docs_citados)}")

print("\n" + "-" * 60)
print(saida["resposta"])


"""
A instrumentação foi pensada para cobrir as quatro camadas que discutimos sobre observabilidade. 

O span() como context manager é a peça central, ele recebe um nome, registra timestamps, calcula latência ao sair do bloco e emite um log estruturado 
em JSON. Isso atende simultaneamente aos três pilares clássicos: cada chamada gera um log estruturado (a linha JSON impressa), os atributos numéricos 
alimentariam métricas se exportados a um sistema como Prometheus ou Datadog, e a relação trace_id/span_id constrói um trace completo da requisição.

O que faz esse exemplo ser específico de Agentes de IA (e não apenas observabilidade tradicional) é a captura de sinais que só fazem sentido quando o 
sistema é semântico. 

O span do estágio 1 captura top_score, min_score e doc_ids recuperados, o que permite detectar deriva da qualidade de recuperação ao longo do tempo 
(a busca vetorial está retornando candidatos cada vez piores?). 

O span do estágio 2 registra como o reranking reordenou os documentos, sinal direto de quanto valor o cross-encoder está agregando. 

O span do llm.generate é o mais rico: além de tokens e custo, conta quantas vezes o agente citou fontes e quantas fontes únicas usou, detecta se 
ele abstém-se com a frase canônica e expõe o "contexto desperdiçado", documentos que estavam no prompt mas não foram citados na resposta. Este último é um 
sinal valioso e raramente medido: se o agente cita só 1 dos 3 documentos disponibilizados, isso sugere que o pipeline de seleção está superdimensionado, 
pagando tokens à toa.

O relatório final amarra tudo. A barra de latência por estágio permite identificar visualmente o caminho crítico. Em produção, o llm.generate quase 
sempre domina e essa visualização justifica investimentos em cache de similaridade, modelos menores ou paralelização. A linha do custo permite responder 
a pergunta operacional mais frequente em produção: "quanto custou esta resposta?". E os campos docs_disponíveis, docs_efetivamente_usados e 
contexto_desperdiçado materializam, em três linhas, a métrica de context precision que costuma exigir um framework inteiro como o RAGAS para ser computada 
e aqui aparece como inspeção direta do alinhamento entre o que foi recuperado e o que foi efetivamente referenciado.

Em produção, dois passos transformam esse exemplo em algo realmente utilizável. 

O primeiro é trocar o print() final por exportação real: emitir os spans para um backend (LangSmith, LangFuse, OTel + Jaeger, ou um simples índice 
Elasticsearch) com trace_id como chave de junção. 

O segundo é amostrar e avaliar, rodar uma LLM-as-a-judge sobre amostras dos traces para anotar qualidade semântica que regex não captura, 
como faithfulness e relevância. 

Mas o exemplo conceitual é exatamente o que está aqui: cada operação cronometrada, cada decisão registrada, cada sinal semântico capturado, 
todos amarrados ao mesmo trace_id. É essa amarração que separa um sistema observável de uma caixa-preta, exatamente o ponto que vimos no tópico 
sobre correlação de chamadas no Capítulo 4 do curso na Data Science Academy.

"""






