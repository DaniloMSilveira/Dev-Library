# 3. Redes neurais, aprendizado não supervisionado, transformers e LLMs

Este documento conecta os conceitos clássicos de Machine Learning com abordagens mais modernas baseadas em redes neurais, arquitetura de atenção e modelos de linguagem.

## 3.1 Aprendizado supervisionado e não supervisionado

Os modelos podem ser treinados de maneiras diferentes, dependendo da disponibilidade de rótulos e do tipo de problema.

- Supervisionado: há rótulos no conjunto de dados. O modelo aprende a associar entradas a saídas conhecidas.
- Não supervisionado: não há rótulos. O objetivo é descobrir padrões, grupos ou estruturas escondidas nos dados.
- Semi-supervisionado: mistura exemplos rotulados e não rotulados, o que pode ser útil quando rotular todos os dados é caro.
- Reforço: o modelo aprende por tentativa e erro, recebendo recompensas ou penalidades conforme suas ações.

Essas categorias refletem diferentes formas de aprender com base em dados e feedback.

## 3.2 Aprendizado não supervisionado

Esse tipo de aprendizado é útil quando não existe uma resposta correta previamente definida.

### Clusterização

Agrupa dados semelhantes com base em características comuns.

- K-Means: divide os dados em $k$ grupos, usando centros representativos.
- DBSCAN: identifica grupos com base em densidade e pode encontrar outliers.
- Clusterização hierárquica: organiza os dados em uma estrutura em árvore, permitindo analisar relações entre grupos.

Exemplo: segmentar clientes por comportamento de compra para criar campanhas específicas.

### Redução de dimensionalidade

Ajuda a simplificar dados complexos e manter apenas as informações mais relevantes.

- PCA: reduz a dimensionalidade preservando a maior parte da variância presente nos dados.
- t-SNE: é mais voltado para visualização e ajuda a representar dados em duas ou três dimensões.

Essas técnicas são úteis quando há muitas variáveis e é necessário reduzir ruído ou facilitar a interpretação.

## 3.3 Redes neurais

As redes neurais são modelos inspirados no cérebro artificial. Elas são compostas por camadas de neurônios artificiais que aprendem representações internas dos dados.

### Perceptron e redes feedforward

O perceptron é a unidade básica de uma rede neural. Quando várias unidades são organizadas em camadas, formam redes feedforward.

- A informação passa da entrada para as camadas intermediárias e, em seguida, para a saída.
- Esse tipo de rede é usado em problemas simples de classificação e regressão.

### CNNs

As redes convolucionais são muito usadas em visão computacional.

- Extraem padrões visuais como bordas, formas e texturas.
- São amplamente utilizadas em reconhecimento de imagens, diagnóstico médico e análise visual.

### RNNs, LSTMs e GRUs

Essas arquiteturas são indicadas para dados sequenciais, como texto, áudio e séries temporais.

- RNNs processam sequências em ordem, mas têm dificuldade com dependências longas.
- LSTMs e GRUs foram criadas para lidar melhor com esse problema, preservando informações relevantes por mais tempo.

Essas redes foram muito importantes antes do surgimento dos Transformers.

## 3.4 Transformers

Os Transformers revolucionaram o processamento de linguagem e outras áreas por causa do mecanismo de atenção.

- Diferente das RNNs, eles processam sequências de forma mais paralela.
- O mecanismo de atenção permite que o modelo identifique quais partes da entrada são mais relevantes para cada ponto da saída.
- Isso os torna muito eficazes para tarefas como tradução, sumarização, classificação de textos e geração de conteúdo.

Componentes importantes:

- Encoder: representa a entrada.
- Decoder: gera a saída.
- Self-attention: mede relações entre partes diferentes da mesma sequência.

## 3.5 LLMs

Large Language Models são modelos baseados em Transformers treinados com grandes volumes de texto.

Eles são usados para:

- responder perguntas;
- resumir documentos;
- traduzir idiomas;
- gerar código e documentação;
- atuar como assistentes de conversa.

Uma característica importante dos LLMs é a capacidade de realizar tarefas com poucas instruções, o que fez com que eles se tornassem ferramentas muito úteis em produtos e fluxos de trabalho modernos.

## 3.6 Relação entre esses conceitos

A evolução da IA passou por etapas sucessivas:

1. Algoritmos clássicos de regressão e classificação
2. Redes neurais tradicionais
3. Aprendizado não supervisionado
4. Arquiteturas modernas como Transformers
5. LLMs e modelos generativos

Cada etapa acrescentou novas capacidades ao campo e abriu espaço para soluções mais robustas e flexíveis.

## 3.7 Resumo

O aprendizado moderno une conceitos clássicos e arquiteturas profundas. Enquanto técnicas mais simples resolvem problemas bem definidos, redes neurais, Transformers e LLMs expandem a capacidade de lidar com linguagem, imagens, sequência e outros tipos complexos de dados.
