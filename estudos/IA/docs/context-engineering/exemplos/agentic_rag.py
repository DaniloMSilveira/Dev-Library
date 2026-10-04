from datetime import date
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# ---------- Corpus simulado (em produção, viria do Qdrant/Chroma/Pinecone) ----------
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

# Pergunta do usuário
query = "Como funciona o algoritmo HNSW para busca vetorial?"

# ---------- Estágio 1: Recuperação por similaridade vetorial (bi-encoder) ----------
# Rápido e barato.
bi = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
q_emb = bi.encode(query)
docs_emb = bi.encode([d["texto"] for d in corpus])

# Similaridade cosseno (em produção: ANN/HNSW pelo banco vetorial)
sims = (docs_emb @ q_emb) / (np.linalg.norm(docs_emb, axis=1) * np.linalg.norm(q_emb))
top_idx = np.argsort(sims)[::-1][:5]  # top-5 candidatos
cand = [{**corpus[i], "s1": float(sims[i])} for i in top_idx]

print("=== Estágio 1: recuperação vetorial (top-5) ===")
for c in cand:
    print(f"  [{c['s1']:+.3f}] doc {c['id']}: {c['texto'][:55]}")

# ---------- Estágio 2: Reranking com cross-encoder ----------
# Lento e caro, mas muito mais preciso, pois só rodamos sobre os 5 que sobraram.
cross = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
pares = [(query, c["texto"]) for c in cand]
scores2 = cross.predict(pares)
for c, s in zip(cand, scores2):
    c["s2"] = float(s)
cand.sort(key=lambda c: c["s2"], reverse=True)

print("\n=== Estágio 2: reranking com cross-encoder ===")
for c in cand:
    print(f"  [{c['s2']:+.3f}] doc {c['id']}: {c['texto'][:55]}")

# ---------- Estágio 3: Regras de negócio (autoridade + recência) ----------
PESO_FONTE = {"doc_oficial": 1.2, "paper": 1.1, "blog_random": 0.7}
HOJE = date(2025, 5, 1)

def fator_recencia(d):
    dias = (HOJE - d).days
    return max(0.5, 1.0 - dias / 1000)  # decai com a idade, base 0.5

for c in cand:
    c["s3"] = c["s2"] * PESO_FONTE.get(c["fonte"], 1.0) * fator_recencia(c["data"])
cand.sort(key=lambda c: c["s3"], reverse=True)

print("\n=== Estágio 3: regras de negócio (autoridade + recência) ===")
for c in cand:
    print(f"  [{c['s3']:+.3f}] {c['fonte']:12s} {c['data']}  doc {c['id']}")

# ---------- Seleção final: só os 3 melhores entram no contexto do LLM ----------
selecionados = cand[:3]
print("\n=== Selecionados para o prompt da LLM ===")
for c in selecionados:
    print(f"  - {c['texto']}")

# ---------- Estágio 4: Agente de IA consome o contexto curado e gera a resposta ----------
from anthropic import Anthropic

llm = Anthropic()

def agente_rag(query: str, contexto: list[dict]) -> dict:
    """Recebe os documentos selecionados pelo pipeline e produz a resposta final."""

    # Numera os documentos para que o agente possa citar fontes específicas
    bloco_contexto = "\n\n".join(
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

    user = f"CONTEXTO:\n{bloco_contexto}\n\nPERGUNTA: {query}"

    resp = llm.messages.create(
        model = "claude-sonnet",
        max_tokens = 400,
        system = system,
        messages = [{"role": "user", "content": user}],
    )

    return {
        "resposta": resp.content[0].text,
        "docs_no_contexto": [c["id"] for c in contexto],
        "tokens": {
            "entrada": resp.usage.input_tokens,
            "saida": resp.usage.output_tokens,
        },
    }


# ----- Execução: usa os 3 docs selecionados pelo pipeline ----- 
saida = agente_rag(query, selecionados)

print("\n=== Resposta gerada pelo Agente ===")
print(saida["resposta"])
print(f"\nDocs disponíveis no contexto: {saida['docs_no_contexto']}")
print(f"Tokens consumidos: entrada={saida['tokens']['entrada']}, saida={saida['tokens']['saida']}")


"""
Este script implementa, de forma compacta e didática, o pipeline RAG (Retrieval-Augmented Generation) que costuma operar em sistemas com Agentes de IA 
ancorados em conhecimento externo. Ele não pretende ser eficiente nem escalável pois todo o corpus é mantido em memória, embeddings são recomputados a 
cada execução e não há persistência, mas sim tornar visível, em cerca de cem linhas, cada um dos quatro estágios pelos quais uma pergunta do usuário 
passa antes de virar uma resposta ancorada em fontes.

A entrada do pipeline é um corpus simulado de oito documentos heterogêneos, deliberadamente desenhados para ilustrar comportamentos específicos: alguns 
altamente relevantes para a query (HNSW, busca vetorial), alguns ligeiramente relacionados (bancos relacionais, embeddings em geral), alguns ruído puro 
(uma receita de bolo) e variações controladas em fonte (doc_oficial, paper, blog_random) e data (de 2020 a 2025). 

Essa diversidade permite observar como cada estágio do pipeline lida com candidatos de qualidade diferente. 

A query "Como funciona o algoritmo HNSW para busca vetorial?" foi escolhida para ser semanticamente próxima de vários documentos, forçando o sistema 
a fazer escolhas entre candidatos parecidos.

O estágio 1 executa a recuperação semântica via bi-encoder. Cada documento e a query são convertidos em vetores densos pelo modelo 
paraphrase-multilingual-MiniLM-L12-v2 (multilíngue e adequado para português) e a similaridade cosseno entre query e documentos define o ranking inicial. 
Em produção, esse cálculo seria delegado a um índice ANN dentro de um banco vetorial como Qdrant, Chroma ou Pinecone, escalando para milhões de documentos 
com latência de milissegundos. No script, é feito por multiplicação de matrizes pura justamente para que você enxergue o que ANN/HNSW está aproximando 
por baixo da abstração. O estágio retorna os top-5 candidatos.

O estágio 2 aplica reranking com cross-encoder e a diferença conceitual é fundamental: enquanto o bi-encoder gera embeddings independentes para 
query e documentos (e depois os compara), o cross-encoder processa o par (query, documento) junto, numa única passagem do modelo. Isso permite capturar 
dependências semânticas finas (saber que "vetorial" qualifica "banco" e que "banco relacional" não satisfaz a query) a um custo computacional muito maior 
por avaliação. A reordenação que ocorre aqui costuma ser dramática: documentos que pareciam relevantes pelo embedding caem e documentos diretamente 
alinhados com a intenção da query sobem.

O estágio 3 introduz uma camada qualitativamente diferente das duas anteriores. Os estágios 1 e 2 são puramente semânticos e só olham o texto. O estágio 3 
traz conhecimento sobre o mundo que não está no texto: que documentação oficial costuma ser mais confiável do que blog aleatório (codificado em PESO_FONTE), 
que conteúdo recente tende a ser mais relevante para queries técnicas (codificado em fator_recencia). Esses sinais são determinísticos, baratos de aplicar 
e frequentemente fazem mais diferença na qualidade percebida do que ajustar o modelo de embedding. O score final combina os três estágios e o pipeline 
seleciona apenas os top-3 documentos para entrar no contexto do LLM.

O estágio 4 fecha o ciclo. O Agente de IA recebe os documentos curados pelos estágios anteriores e produz a resposta final. O system prompt impõe 
três contratos explícitos: citar [N] em cada afirmação, abster-se com a frase "Informação insuficiente" quando o contexto não cobre a pergunta e 
usar APENAS o contexto fornecido. Esses contratos são o que separa um sistema RAG profissional de um sistema que alucina silenciosamente sob aparência 
de competência. A função retorna não apenas a resposta gerada, mas também os IDs dos documentos disponibilizados e os tokens consumidos, embriões de 
observabilidade que permitiriam, em produção, computar métricas como context precision e custo por requisição.

Didaticamente, o script tem três virtudes complementares. Primeiro, torna explícita a separação de responsabilidades: cada estágio tem uma única função 
(filtrar, refinar, regular, gerar) e pode ser substituído ou removido sem afetar os outros, permitindo experimentar comentando blocos e observando 
o impacto. Segundo, torna visível o efeito de cada estágio, imprimindo a ordem dos candidatos a cada passo; ao rodar, você vê com os próprios olhos 
como o ranking muda, o que é muito mais eficaz do que diagramas estáticos. Terceiro, usa stack realista: os modelos de embedding e cross-encoder são os 
mesmos usados em produção, a estrutura de dados ({id, fonte, data, texto, scores}) é compatível com schemas reais de bancos vetoriais 
e o agente usa a API real da Anthropic. 

As principais simplificações deste script: 

- Não há cache de embeddings e em produção, os embeddings dos documentos seriam computados uma única vez, persistidos no banco vetorial e reutilizados. 
- Não há tratamento de erros, retries com backoff exponencial, nem rate limiting. 
- Não há observabilidade estruturada, apenas print(). 
- Não há avaliação semântica da resposta (faithfulness, relevance), que em produção alimentaria o loop de melhoria contínua descrito no Capítulo 4 do curso na Data Science Academy.

"""




    