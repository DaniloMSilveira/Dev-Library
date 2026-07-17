# 🧠 Janela de Contexto em LLMs

## O que é?
A **janela de contexto** é a quantidade máxima de informação (tokens) que um modelo de linguagem consegue processar em uma única interação.  
- **Tokens ≠ palavras**: uma palavra pode ser dividida em vários tokens.  
- Exemplo: "inteligência artificial" → pode virar 3 tokens.

---

## 📏 Limite de Informação
- Modelos pequenos: 2k–4k tokens (~2–3 páginas de texto).  
- Modelos médios: 8k–32k tokens (~20–80 páginas).  
- Modelos avançados: até 1M tokens (capazes de lidar com livros inteiros).

---

## ⚡ Diferenças entre Modelos
| Modelo | Janela de Contexto | Velocidade | Custo |
|--------|--------------------|------------|-------|
| 4k tokens | Rápido | Mais barato |
| 32k tokens | Médio | Moderado |
| 1M tokens | Mais lento | Muito caro |

- **Quanto maior a janela**, mais caro e lento tende a ser o processamento.  
- **Modelos menores** são ideais para tarefas rápidas e curtas.  
- **Modelos maiores** são úteis para análise de documentos extensos.

---

## 🛠️ Estratégias de Otimização
1. **Chunking inteligente**  
   - Dividir textos longos em partes menores e coerentes.  
   - Exemplo: separar capítulos de um livro ou seções de um relatório.

2. **Ranking de relevância**  
   - Selecionar apenas os trechos mais importantes para enviar ao modelo.  
   - Exemplo: usar busca semântica para priorizar parágrafos relacionados à pergunta.

3. **Resumo de histórico**  
   - Condensar interações anteriores em um resumo curto.  
   - Exemplo: em um chat longo, gerar "notas" do que já foi discutido.

4. **Compressão de contexto**  
   - Reescrever ou simplificar trechos mantendo apenas a essência.  
   - Exemplo: transformar 5 páginas em 1 página de pontos-chave.

---

## 🎯 Exemplo Prático
- Pergunta: "Explique o capítulo 3 do relatório de 200 páginas."  
- Estratégia:
  1. Dividir o relatório em chunks de 5 páginas.  
  2. Usar ranking para encontrar apenas os chunks do capítulo 3.  
  3. Resumir esses chunks.  
  4. Enviar o resumo ao modelo para análise.

---

## 📚 Chunking em LLMs

### 🔎 Motivação
- A janela de contexto de um LLM é limitada.  
- Textos longos (livros, relatórios, bases de conhecimento) não cabem inteiros.  
- **Chunking** resolve isso ao **dividir o conteúdo em pedaços menores e coerentes**.  
- Objetivo: manter cada pedaço compreensível e útil sem ultrapassar o limite de tokens.

---

### ⚙️ Como funciona
- **Divisão semântica**: separar por parágrafos, seções ou capítulos.  
- **Granularidade ajustada**: chunks muito grandes podem estourar o limite; muito pequenos perdem contexto.  
- Exemplo prático:
  - Documento de 100 páginas → dividido em chunks de 500 palavras.  
  - Cada chunk é indexado e recuperado conforme a necessidade.

---

### 📌 Chunking em RAG (Retrieval-Augmented Generation)
- No **RAG**, o modelo busca informações relevantes em uma base antes de responder.  
- Chunking garante que os documentos sejam **facilmente pesquisáveis**.  
- Processo típico:
  1. Dividir documentos em chunks.  
  2. Gerar embeddings para cada chunk.  
  3. Armazenar em um índice vetorial.  
  4. Recuperar apenas os chunks mais relevantes para a pergunta.  
- Benefício: respostas mais precisas e custo menor, pois só os trechos relevantes entram no contexto.

---

### 🧩 Chunking em Modelos de Embedding
- Embeddings transformam texto em vetores numéricos.  
- Chunking é essencial porque embeddings de textos muito longos:
  - Podem perder granularidade.  
  - Ficam menos úteis para busca semântica.  
- Exemplo:
  - Pergunta: "Quais são os sintomas da diabetes tipo 2?"  
  - Em vez de comparar com um artigo inteiro, compara-se com chunks específicos sobre sintomas.

---

### 🎯 Boas práticas de Chunking
1. **Tamanho balanceado**: 200–500 palavras por chunk é comum.  
2. **Overlap inteligente**: incluir algumas frases do final de um chunk no início do próximo para não perder contexto.  
3. **Segmentação semântica**: evitar cortar no meio de uma ideia ou frase.  
4. **Pré-processamento**: remover redundâncias e normalizar texto antes de gerar embeddings.

---

## 🔗 Modelos de Embedding

### O que são?
- **Embeddings** são representações vetoriais de textos, palavras ou documentos.  
- Cada pedaço de texto é convertido em um vetor em um espaço multidimensional.  
- Objetivo: permitir comparação semântica entre textos.

### Exemplos de uso
- Busca semântica: encontrar trechos relevantes em uma base de conhecimento.  
- RAG: indexar chunks de documentos para recuperação eficiente.  
- Clustering: agrupar textos semelhantes.  
- Classificação: detectar tópicos ou intenções.

---

## 📐 Métricas de Similaridade

Para comparar embeddings, usamos métricas matemáticas que medem o quão próximos dois vetores estão em termos semânticos:

| Métrica | Como funciona | Uso comum |
|---------|---------------|-----------|
| **Similaridade do Cosseno** | Mede o ângulo entre dois vetores. Quanto menor o ângulo, maior a similaridade. | Busca semântica, ranking de relevância |
| **Produto Escalar (Dot Product)** | Calcula o produto dos valores correspondentes dos vetores. | Recomendação, modelos de ranking |
| **Distância Euclidiana** | Mede a distância geométrica direta entre dois pontos no espaço vetorial. | Clustering, agrupamento de textos semelhantes |

### Observações
- **Similaridade do Cosseno** é a mais usada em NLP, pois foca na direção do vetor (semântica) e ignora o tamanho.  
- **Produto Escalar** é útil em sistemas de recomendação, onde a magnitude também importa.  
- **Distância Euclidiana** é intuitiva para medir proximidade, mas pode ser menos eficaz em espaços de alta dimensão.

---

## 🧩 Modelos de Chunking

### 🔒 Chunking Estático
- Divide o texto em pedaços fixos (ex: 500 tokens).  
- Simples de implementar, mas pode cortar ideias no meio.  
- Bom para textos estruturados e previsíveis.

### 🔄 Chunking Dinâmico
- Divide o texto de forma adaptativa, respeitando **parágrafos, tópicos ou subtítulos**.  
- Preserva melhor o contexto e evita cortes bruscos.  
- Ideal para RAG e embeddings, pois cada chunk carrega uma ideia completa.

---

## 🎯 Exemplo Prático
- Pergunta: "Quais são os sintomas da diabetes tipo 2?"  
- Fluxo:
  1. Documento médico dividido em chunks dinâmicos (por seção).  
  2. Cada chunk convertido em embedding.  
  3. Pergunta também convertida em embedding.  
  4. Similaridade do cosseno identifica os chunks mais próximos.  
  5. LLM recebe apenas os trechos relevantes → resposta precisa e 

---

## 🗂️ Índices Vetoriais

Quando trabalhamos com embeddings em grandes bases de dados, precisamos de **estruturas de índice vetorial** para buscar rapidamente os vetores mais semelhantes.  
Os três principais métodos são:

---

### ⚡ HNSW (Hierarchical Navigable Small World)
- **Como funciona**: cria um grafo hierárquico onde cada vetor é conectado a vizinhos próximos.  
- Busca eficiente usando "atalhos" no grafo.  
- **Vantagens**:
  - Alta precisão.  
  - Muito rápido em consultas.  
- **Desvantagens**:
  - Consome mais memória.  
- **Casos de uso**:
  - Bases pequenas ou médias (até milhões de vetores).  
  - Aplicações que exigem **alta precisão** (ex: busca semântica em documentos críticos).

---

### 📊 IVF (Inverted File Index)
- **Como funciona**: divide o espaço vetorial em clusters (via k-means).  
- Cada vetor é atribuído a um cluster; busca ocorre apenas nos clusters mais relevantes.  
- **Vantagens**:
  - Escalável para bases grandes.  
  - Reduz tempo de busca.  
- **Desvantagens**:
  - Pode perder precisão se o número de clusters for mal configurado.  
- **Casos de uso**:
  - Bases muito grandes (centenas de milhões de vetores).  
  - Cenários onde **velocidade** é mais importante que precisão absoluta.

---

### 🧮 PQ (Product Quantization)
- **Como funciona**: comprime vetores em representações menores, dividindo-os em subvetores e quantizando cada parte.  
- Permite armazenar embeddings de forma compacta.  
- **Vantagens**:
  - Reduz drasticamente o uso de memória.  
  - Permite buscas rápidas em bases gigantes.  
- **Desvantagens**:
  - Perda de precisão devido à compressão.  
- **Casos de uso**:
  - Bases enormes (bilhões de vetores).  
  - Cenários onde **custo e memória** são críticos (ex: motores de busca globais).

---

## 📌 Comparação Rápida

| Índice | Precisão | Velocidade | Memória | Melhor uso |
|--------|----------|------------|---------|------------|
| **HNSW** | Alta | Alta | Alta | Bases médias, alta precisão |
| **IVF** | Média | Alta | Média | Bases grandes, busca rápida |
| **PQ** | Baixa/Média | Alta | Baixa | Bases gigantes, otimização de custo |

---

## 🔀 Uso de IVF com PQ

### 🧩 Como funciona
- **IVF** organiza os vetores em clusters (via k-means).  
- Durante a busca, apenas alguns clusters relevantes são explorados.  
- **PQ** comprime os vetores dentro desses clusters em representações menores.  
- Resultado: busca rápida e eficiente em bases gigantes, com consumo reduzido de memória.

---

### ⚡ Benefícios da combinação
1. **Escalabilidade**: suporta bases com bilhões de vetores.  
2. **Eficiência**: reduz tempo de busca ao limitar clusters e usar vetores comprimidos.  
3. **Custo menor**: PQ diminui uso de memória e armazenamento.  
4. **Flexibilidade**: permite ajustar trade-off entre precisão e velocidade.

---

### 📌 Casos de uso
- **Motores de busca globais**: indexação de páginas da web em escala massiva.  
- **Recomendação de conteúdo**: plataformas de streaming ou e-commerce com milhões de itens.  
- **Bases científicas**: busca em grandes coleções de artigos ou dados biomédicos.  
- **Aplicações multimodais**: recuperação de imagens, vídeos ou áudio em catálogos enormes.

---

### ⚖️ Trade-offs
- **Precisão**: menor que HNSW puro, pois há compressão e busca parcial.  
- **Velocidade**: muito alta, ideal para consultas em tempo real.  
- **Memória**: extremamente otimizada, permitindo trabalhar com bases que não caberiam em RAM sem PQ.

---

# 🔍 Estratégias Avançadas de Recuperação em LLMs

## 🧩 Busca Híbrida (Índices Vetoriais + BM25)

### O que é?
- Combina **busca semântica** (via embeddings e índices vetoriais) com **busca lexical** (BM25).  
- **BM25**: algoritmo clássico de recuperação baseado em frequência de termos.  
- **Índices vetoriais**: permitem busca por significado, não apenas por palavras exatas.

### Benefícios
- **Cobertura completa**: BM25 garante precisão lexical, vetores garantem relevância semântica.  
- **Equilíbrio**: evita perder resultados importantes que não são semanticamente próximos, mas contêm termos-chave.  
- **Casos de uso**:
  - Pesquisa em bases jurídicas (palavras exatas importam).  
  - FAQ corporativo (semântica importa mais).  
  - Motores de busca híbridos (Google, Bing, etc. usam combinações semelhantes).

---

## 🔄 Reranking com Cross-Encoder

### Como funciona
- Após recuperar candidatos (via BM25 ou embeddings), aplica-se um **Cross-Encoder** para reavaliar pares (pergunta + documento).  
- Diferente de embeddings, o Cross-Encoder lê os dois textos juntos e gera uma pontuação de relevância.

### Benefícios
- **Alta precisão**: captura nuances que embeddings podem perder.  
- **Melhor ranking**: garante que os resultados mais relevantes fiquem no topo.  
- **Casos de uso**:
  - Chatbots de suporte que precisam respostas exatas.  
  - Pesquisa acadêmica ou científica.  
  - Sistemas de QA (Pergunta-Resposta).

---

## 🗂️ Filtragem por Metadata

### O que é?
- Usar atributos extras (autor, data, categoria, idioma) para restringir resultados.  
- Exemplo: buscar apenas documentos publicados após 2020 ou apenas em português.

### Benefícios
- Reduz ruído.  
- Aumenta precisão em bases heterogêneas.  
- Casos de uso: bibliotecas digitais, e-commerce (filtrar por preço, marca).

---

## 🧹 Desduplicação (Dedup)

### O que é?
- Remover documentos ou chunks duplicados ou muito semelhantes.  
- Evita redundância no contexto enviado ao LLM.

### Benefícios
- Economiza tokens.  
- Melhora clareza da resposta.  
- Casos de uso: bases com versões repetidas de artigos, logs de sistemas.

---

## 💰 Orçamento de Tokens

### Estratégia
- Cada consulta ao LLM tem um limite de tokens → **precisa ser gerenciado**.  
- Técnicas:
  1. **Resumo automático**: condensar chunks antes de enviar.  
  2. **Ranking de relevância**: enviar apenas os top-N resultados.  
  3. **Compressão semântica**: reduzir redundâncias mantendo significado.  
  4. **Histórico resumido**: em chats longos, resumir interações passadas.

### Benefícios
- Reduz custo.  
- Aumenta velocidade.  
- Evita ultrapassar limites de 

---

# 🔀 RRF (Reciprocal Rank Fusion) na Busca Híbrida

## 📌 O que é RRF?
- **Reciprocal Rank Fusion (RRF)** é uma técnica de fusão de resultados de múltiplos sistemas de busca.  
- Em vez de escolher apenas um método (lexical ou semântico), o RRF combina rankings diferentes em uma lista única.  
- Fórmula simplificada:  
  

\[
  Score(d) = \sum \frac{1}{k + rank(d)}
  \]


  - Onde `rank(d)` é a posição do documento em cada ranking.  
  - `k` é um parâmetro de suavização (tipicamente 60).

---

## ⚙️ Como funciona na prática
1. Executa-se uma busca **lexical** (ex: BM25 em ElasticSearch).  
2. Executa-se uma busca **semântica** (ex: embeddings em FAISS ou Milvus).  
3. Cada resultado recebe uma pontuação baseada na sua posição em cada ranking.  
4. O RRF combina os rankings em uma lista final, equilibrando os dois mundos.

---

## 🧩 Exemplos em Ferramentas

### 🔎 ElasticSearch
- ElasticSearch suporta BM25 nativamente.  
- Pode ser combinado com plugins ou integrações de vetores (como **ElasticSearch Vector Search**).  
- O RRF é usado para fundir os resultados BM25 (palavras exatas) com embeddings (semântica).  
- Caso de uso:  
  - Busca em e-commerce → BM25 garante que "Tênis Nike" apareça, embeddings garantem que "calçado esportivo" também seja considerado.

### 🧠 FAISS / Milvus / Weaviate
- FAISS (Facebook AI Similarity Search) e Milvus/Weaviate são bancos especializados em busca vetorial.  
- Integração comum:  
  - BM25 via ElasticSearch ou PostgreSQL.  
  - Vetorial via FAISS/Milvus.  
  - RRF combina os dois rankings.  
- Caso de uso:  
  - Pesquisa acadêmica → BM25 garante termos exatos ("RNA"), embeddings capturam contexto ("ácido ribonucleico").

---

## 🎯 Benefícios do RRF
- **Equilíbrio**: evita que apenas semântica ou apenas termos exatos dominem.  
- **Robustez**: melhora recall e precisão em bases heterogêneas.  
- **Flexibilidade**: ajustável via parâmetro `k` para dar mais peso a um ranking.  
- **Aplicações**:
  - Chatbots corporativos.  
  - Motores de busca híbridos.  
  - Sistemas de suporte técnico.  
  - Pesquisa multimodal (texto + imagem).

---

## Lista de Verificação de Otimização RAG

- Limpeza dos textos desnecessários (ícones, caracteres especiais, etc)
- Seleção correta do modelo de embedding
- Chunking otimizado para seu domínio
- Seleção de métrica de similaridade apropriada
- Índice vetorial com parâmetros sintonizados
- Busca híbrida se necessário
- Reranking com cross-encoder
- Filtragem inteligente de metadados
- Orçamento de tokens final verificado


