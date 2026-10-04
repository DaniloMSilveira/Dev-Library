# 2. Contexto, janela e recuperação

Depois de entender o que é contexto (documento 1), o próximo passo é entender os dois problemas práticos que toda aplicação com LLM enfrenta: o contexto cabe em um espaço limitado, e a informação certa precisa ser encontrada antes de poder ser incluída nesse espaço. Este documento cobre a janela de contexto, tokenização, embeddings, métricas de similaridade, chunking e o fluxo completo de RAG.

## 2.1 Tokens e janela de contexto

Um modelo de linguagem não processa texto diretamente, ele processa tokens. Um token pode ser uma palavra inteira, parte de uma palavra, ou um caractere, dependendo do esquema de tokenização usado pelo modelo. A contagem de tokens de um texto quase nunca coincide com a contagem de palavras: uma palavra comum costuma virar um único token, enquanto uma palavra rara ou um termo técnico pode ser dividido em dois ou três tokens.

A janela de contexto é o número máximo de tokens que um modelo consegue processar em uma única chamada, somando prompt de entrada e resposta gerada. Um modelo com janela de 128 mil tokens, por exemplo, não enxerga nada além disso: qualquer informação que não caiba dentro desse limite simplesmente não está disponível para gerar a resposta.

Em Python, para a família de modelos da OpenAI, a biblioteca `tiktoken` permite contar tokens antes de enviar uma requisição, o que é essencial para não estourar o limite:

```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o")

texto = "Context engineering é a prática de organizar contexto para um LLM."
tokens = encoding.encode(texto)

print(f"Número de tokens: {len(tokens)}")
print(f"Tokens: {tokens[:10]}...")
```

Modelos diferentes usam tokenizadores diferentes. Um texto de 100 tokens em um modelo pode ter uma contagem diferente em outro. Ao trabalhar com múltiplos modelos, é um erro comum assumir que a contagem de tokens é universal.

Ter uma janela maior não resolve o problema de qualidade do contexto. Pesquisas sobre o comportamento de modelos longos mostram um efeito chamado "lost in the middle": o modelo tende a dar mais atenção a informações no início e no fim do contexto do que a informações no meio, mesmo quando toda a informação cabe dentro da janela. Isso significa que simplesmente aumentar o tamanho do contexto enviado não é equivalente a melhorar a qualidade da resposta, e pode até piorá-la se informação irrelevante empurrar o dado importante para o meio do prompt.

## 2.2 Embeddings

Um embedding é a representação de um texto como um vetor de números reais, de dimensão fixa, gerado por um modelo treinado especificamente para isso. A ideia central é que textos com significado semântico parecido geram vetores próximos nesse espaço, enquanto textos com significados diferentes geram vetores distantes.

Essa proximidade não é definida manualmente, é aprendida durante o treinamento do modelo de embedding, tipicamente a partir de pares de textos que humanos (ou outros modelos) classificaram como semelhantes ou diferentes.

Um ponto importante: embedding de busca semântica e embedding usado dentro de um Transformer (como visto na camada de atenção de um LLM) são o mesmo conceito matemático, um vetor denso, mas servem a propósitos diferentes. Aqui, o interesse é gerar um vetor para um texto inteiro (uma frase, um parágrafo, um documento), de forma que vetores de textos parecidos fiquem próximos no espaço vetorial, para viabilizar busca por similaridade.

Exemplo gerando embeddings localmente com a biblioteca `sentence-transformers`, que roda sem depender de uma API externa:

```python
from sentence_transformers import SentenceTransformer

modelo = SentenceTransformer("all-MiniLM-L6-v2")

textos = [
    "Qual é a política de reembolso para pedidos cancelados?",
    "Como funciona o processo de devolução de um produto?",
    "Qual é a previsão do tempo para amanhã?",
]

embeddings = modelo.encode(textos)

print(f"Formato de cada embedding: {embeddings[0].shape}")
print(f"Primeiros 5 valores do primeiro embedding: {embeddings[0][:5]}")
```

O modelo `all-MiniLM-L6-v2` gera vetores de 384 dimensões. Modelos maiores, como os da família `text-embedding-3` da OpenAI, geram vetores de 1536 ou 3072 dimensões. Mais dimensões geralmente capturam mais nuance semântica, ao custo de mais espaço de armazenamento e mais tempo de cálculo na busca.

Um detalhe prático: os dois primeiros textos do exemplo acima (reembolso e devolução) tratam de temas relacionados, mesmo sem compartilhar muitas palavras exatas. Um embedding bem treinado coloca esses dois vetores relativamente próximos, enquanto o terceiro texto (previsão do tempo) fica distante dos outros dois. Essa é a propriedade que torna busca semântica possível: ela encontra textos relacionados por significado, não apenas por palavras-chave compartilhadas, o que é a limitação central de uma busca tradicional por palavra exata.

## 2.3 Métricas de similaridade

Depois de ter os embeddings, é preciso uma forma de medir o quão "próximos" dois vetores estão. As três métricas mais comuns são:

**Similaridade de cosseno:** mede o ângulo entre dois vetores, ignorando sua magnitude (tamanho). Varia de -1 (opostos) a 1 (idênticos em direção). É a métrica mais usada em busca semântica de texto, porque o que importa é a direção do vetor (o significado), não o quão "grande" ele é.

**Produto escalar (dot product):** multiplica os vetores posição a posição e soma os resultados. Diferente do cosseno, o produto escalar é sensível à magnitude dos vetores. Alguns modelos de embedding são treinados especificamente para que o produto escalar funcione bem como métrica, nesse caso ele costuma ser mais rápido de calcular que o cosseno.

**Distância euclidiana:** mede a distância "em linha reta" entre dois pontos no espaço vetorial. É mais intuitiva geometricamente, mas menos usada em busca semântica de texto, porque é mais sensível a diferenças de magnitude do vetor do que a diferenças de direção.

```python
import numpy as np

def similaridade_cosseno(vetor_a: np.ndarray, vetor_b: np.ndarray) -> float:
    produto = np.dot(vetor_a, vetor_b)
    norma_a = np.linalg.norm(vetor_a)
    norma_b = np.linalg.norm(vetor_b)
    return produto / (norma_a * norma_b)

def distancia_euclidiana(vetor_a: np.ndarray, vetor_b: np.ndarray) -> float:
    return np.linalg.norm(vetor_a - vetor_b)

# Reaproveitando os embeddings do exemplo anterior
pergunta_reembolso = embeddings[0]
pergunta_devolucao = embeddings[1]
pergunta_tempo = embeddings[2]

print(f"Cosseno (reembolso x devolução): {similaridade_cosseno(pergunta_reembolso, pergunta_devolucao):.4f}")
print(f"Cosseno (reembolso x tempo): {similaridade_cosseno(pergunta_reembolso, pergunta_tempo):.4f}")
```

Na prática, a saída esperada deste exemplo mostra um valor de similaridade bem mais alto entre "reembolso" e "devolução" do que entre "reembolso" e "tempo", confirmando numericamente o que foi descrito na seção anterior.

Qual métrica escolher não é uma decisão arbitrária: depende de como o modelo de embedding específico foi treinado. A documentação do modelo geralmente especifica qual métrica usar. Usar a métrica errada (por exemplo, distância euclidiana em um modelo otimizado para produto escalar) produz resultados de busca piores, mesmo que o embedding em si esteja correto.

## 2.4 Chunking

Documentos reais raramente cabem inteiros, de forma útil, em um único embedding. Um documento de 50 páginas gerar um único vetor perderia granularidade: a busca não conseguiria apontar para a seção específica relevante, só para o documento inteiro. Por isso, documentos são divididos em pedaços menores, chamados chunks, cada um com seu próprio embedding.

Chunking parece simples na superfície, mas envolve decisões reais que afetam diretamente a qualidade da recuperação:

**Tamanho do chunk:** chunks muito pequenos (uma frase) carregam pouco contexto próprio, o que pode fazer um trecho relevante não ser encontrado porque, isolado, ele não tem embedding parecido o suficiente com a pergunta. Chunks muito grandes (várias páginas) diluem o foco semântico do embedding, por misturar vários assuntos em um único vetor, e desperdiçam espaço da janela de contexto quando recuperados. Um ponto de partida comum é algo entre 200 e 500 tokens por chunk, mas o tamanho ideal depende do tipo de conteúdo.

**Overlap (sobreposição) entre chunks:** dividir um documento em chunks sem sobreposição corre o risco de cortar uma frase ou uma ideia exatamente na fronteira entre dois chunks, perdendo o contexto de ambos os lados. Um overlap de 10 a 20% do tamanho do chunk (por exemplo, 50 tokens de overlap em chunks de 300 tokens) reduz esse problema, ao custo de armazenar informação duplicada.

**Estratégia de corte:** cortar por número fixo de caracteres é a abordagem mais simples, mas pode partir uma frase ao meio. Cortar por limite de sentença ou de parágrafo preserva unidades de sentido completas, mas gera chunks de tamanho variável. Para documentos estruturados (como Markdown, com cabeçalhos), cortar respeitando a estrutura (por seção) costuma produzir os melhores resultados, porque cada chunk já corresponde a uma unidade de sentido que o autor do documento definiu.

Exemplo de chunking com sobreposição, por número de tokens, usando `tiktoken` para contar de forma consistente com o modelo que vai consumir o resultado:

```python
import tiktoken

def dividir_em_chunks(texto: str, tamanho_chunk: int = 300, overlap: int = 50) -> list[str]:
    encoding = tiktoken.encoding_for_model("gpt-4o")
    tokens = encoding.encode(texto)

    chunks = []
    inicio = 0
    while inicio < len(tokens):
        fim = inicio + tamanho_chunk
        chunk_tokens = tokens[inicio:fim]
        chunks.append(encoding.decode(chunk_tokens))
        inicio += tamanho_chunk - overlap  # avança, mas reaproveita o overlap

    return chunks

documento = """
Política de reembolso: pedidos podem ser cancelados em até 7 dias
após a compra, desde que o produto não tenha sido utilizado...
(texto longo continua aqui)
"""

chunks = dividir_em_chunks(documento, tamanho_chunk=300, overlap=50)
print(f"Documento dividido em {len(chunks)} chunks.")
```

O trade-off de chunking nunca desaparece por completo, apenas muda de forma: reduzir o tamanho do chunk melhora precisão (o chunk recuperado é mais focado), mas aumenta o risco de perder contexto que estava em um chunk vizinho. Esse é exatamente o tipo de decisão que deveria ser registrado explicitamente em uma spec ou design de sistema RAG, não deixado implícito no código.

## 2.5 Indexação e banco vetorial

Depois de gerar embeddings para todos os chunks de uma base de documentos, é preciso armazená-los de uma forma que permita buscar, dado o embedding de uma pergunta, quais chunks têm os vetores mais próximos. Fazer essa busca comparando a pergunta com cada chunk um por um (busca exaustiva) funciona para poucas centenas de chunks, mas não escala para milhões.

Um banco vetorial resolve isso com estruturas de indexação especializadas (como HNSW, Hierarchical Navigable Small World) que tornam a busca aproximada por vizinhos mais próximos muito mais rápida do que a busca exaustiva, trocando uma pequena margem de precisão por grande ganho de velocidade.

Opções comuns incluem FAISS (biblioteca local, da Meta, boa para prototipagem e volumes médios), Chroma (banco vetorial open-source, fácil de rodar localmente), Pinecone e Weaviate (serviços gerenciados), e extensões vetoriais em bancos relacionais já existentes, como pgvector para PostgreSQL.

Exemplo simples de indexação e busca com Chroma, por ser fácil de rodar localmente para fins de estudo:

```python
import chromadb

cliente = chromadb.Client()
colecao = cliente.create_collection(name="politicas_internas")

colecao.add(
    documents=chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))],
)

pergunta = "Posso cancelar um pedido depois de quantos dias?"
resultado = colecao.query(query_texts=[pergunta], n_results=3)

for documento, distancia in zip(resultado["documents"][0], resultado["distances"][0]):
    print(f"Distância: {distancia:.4f} | Trecho: {documento[:100]}...")
```

O Chroma, nesse exemplo, gera os embeddings internamente usando um modelo default. Em um sistema real, normalmente se escolhe explicitamente o modelo de embedding (o mesmo usado tanto para indexar os documentos quanto para a pergunta do usuário), em vez de depender do default da ferramenta, justamente para ter controle sobre qual modelo e qual métrica de similaridade estão em uso.

## 2.6 Re-ranking

A busca vetorial inicial (chamada de busca densa) é rápida, mas usa uma aproximação: compara o embedding da pergunta contra o embedding de cada chunk, isoladamente, sem considerar os dois textos juntos. Isso funciona bem para filtrar um grande volume de documentos até um conjunto menor de candidatos, mas nem sempre coloca o chunk mais relevante no topo.

Re-ranking é uma segunda etapa, aplicada só sobre os poucos candidatos já filtrados pela busca inicial (tipicamente de 10 a 50), que usa um modelo mais caro computacionalmente, mas mais preciso: um cross-encoder. Diferente do embedding usado na busca inicial (que processa pergunta e documento separadamente), um cross-encoder recebe pergunta e documento juntos, e gera diretamente uma pontuação de relevância entre os dois.

Esse custo computacional maior é exatamente o motivo pelo qual o cross-encoder não é usado na busca inicial contra milhões de documentos, apenas depois, para reordenar um conjunto pequeno de candidatos.

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

pergunta = "Posso cancelar um pedido depois de quantos dias?"
candidatos = resultado["documents"][0]  # os 3 chunks já recuperados na seção anterior

pares = [[pergunta, candidato] for candidato in candidatos]
pontuacoes = reranker.predict(pares)

candidatos_ordenados = sorted(zip(candidatos, pontuacoes), key=lambda x: x[1], reverse=True)

for candidato, pontuacao in candidatos_ordenados:
    print(f"Pontuação: {pontuacao:.4f} | Trecho: {candidato[:100]}...")
```

Em sistemas de produção, serviços como o Cohere Rerank oferecem essa etapa como uma API, evitando a necessidade de hospedar o modelo de cross-encoder localmente. O princípio é o mesmo: busca densa ampla e barata primeiro, reordenação precisa e mais cara depois, apenas sobre o conjunto já reduzido.

## 2.7 RAG: o fluxo completo

RAG (Retrieval-Augmented Generation) é a combinação de tudo visto neste documento em um único fluxo, usado para responder perguntas com base em uma coleção de documentos que o modelo não viu durante seu treinamento:

1. o documento é dividido em chunks (seção 2.4);
2. cada chunk é convertido em embedding e armazenado em um banco vetorial (seções 2.2 e 2.5);
3. quando chega uma pergunta do usuário, ela também é convertida em embedding, usando o mesmo modelo usado para indexar os documentos;
4. o banco vetorial retorna os chunks com maior similaridade à pergunta (seção 2.3);
5. opcionalmente, os candidatos passam por re-ranking para refinar a ordem (seção 2.6);
6. os chunks mais relevantes são inseridos no prompt enviado ao LLM, junto com a pergunta original;
7. o LLM gera a resposta com base no contexto recuperado, não apenas no que aprendeu durante o treinamento.

```python
def responder_com_rag(pergunta: str, colecao, reranker, llm_client) -> str:
    # Passo 3 e 4: busca densa inicial
    resultado = colecao.query(query_texts=[pergunta], n_results=10)
    candidatos = resultado["documents"][0]

    # Passo 5: re-ranking sobre os candidatos
    pares = [[pergunta, candidato] for candidato in candidatos]
    pontuacoes = reranker.predict(pares)
    melhores = sorted(zip(candidatos, pontuacoes), key=lambda x: x[1], reverse=True)[:3]

    # Passo 6: montagem do prompt com o contexto recuperado
    contexto = "\n\n".join(chunk for chunk, _ in melhores)
    prompt = f"""Use apenas as informações abaixo para responder à pergunta.
Se a resposta não estiver no contexto, diga que não sabe.

Contexto:
{contexto}

Pergunta: {pergunta}
"""

    # Passo 7: geração da resposta
    return llm_client.generate(prompt)
```

A instrução explícita "se a resposta não estiver no contexto, diga que não sabe" é uma prática simples e importante: sem ela, o modelo tende a preencher lacunas com conhecimento do próprio treinamento em vez do contexto recuperado, o que reduz groundedness (tema do documento 1) e aumenta o risco de uma resposta que parece correta, mas não está de fato apoiada nos documentos fornecidos.

Cada etapa desse fluxo é um ponto de falha possível. Um chunking ruim (seção 2.4) significa que a informação certa nunca foi indexada de forma recuperável. Um modelo de embedding mal escolhido (seção 2.2) significa que perguntas e documentos relevantes não ficam próximos no espaço vetorial. Pular re-ranking (seção 2.6) em uma base de documentos grande e heterogênea pode deixar o chunk mais relevante fora do topo. Diagnosticar uma resposta ruim de um sistema RAG exige verificar cada uma dessas etapas isoladamente, não apenas o prompt final enviado ao modelo.

## 2.8 Resumo

A janela de contexto é um limite físico de tokens, não apenas um número a ser respeitado, e colocar mais contexto nem sempre melhora a resposta, por causa de efeitos como "lost in the middle". Embeddings transformam texto em vetores que capturam significado semântico, e a escolha de métrica de similaridade deve seguir o que o modelo de embedding foi treinado para usar. Chunking, indexação em banco vetorial e re-ranking são as três etapas técnicas que, juntas, formam a camada de recuperação de um sistema RAG, e cada uma delas tem decisões próprias que afetam diretamente a qualidade do contexto entregue ao modelo.
