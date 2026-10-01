# 6. Transformers e LLMs

As RNNs, LSTMs e GRUs vistas no documento anterior processam sequências elemento por elemento, o que limita paralelização e dificulta capturar dependências entre elementos muito distantes na sequência. Este documento cobre a arquitetura Transformer, que resolve esses dois problemas, e como ela sustenta os LLMs (Large Language Models) atuais.

## 6.1 O problema que o Transformer resolve

Em uma RNN, para processar a palavra na posição 50 de uma frase, o modelo precisa primeiro processar sequencialmente as 49 anteriores, carregando a informação relevante através do estado interno a cada passo. Isso tem dois custos.

O primeiro é de desempenho: o processamento sequencial impede paralelização durante o treino, tornando-o lento em sequências longas. O segundo é de qualidade: mesmo com LSTM e GRU, informação de elementos muito distantes tende a se diluir ao longo da sequência.

O Transformer, apresentado no artigo "Attention Is All You Need" (2017), resolve os dois problemas com um mecanismo chamado self-attention, que permite que cada posição da sequência olhe diretamente para todas as outras posições, em paralelo, sem depender de um estado sequencial acumulado.

## 6.2 Tokenização

Antes de qualquer processamento, o texto precisa ser convertido em unidades discretas chamadas tokens. Um token pode ser uma palavra inteira, parte de uma palavra, ou até um único caractere, dependendo do esquema de tokenização usado.

A maioria dos LLMs atuais usa tokenização por subpalavra, com algoritmos como BPE (Byte Pair Encoding) ou WordPiece. A ideia central é balancear dois extremos: tokenizar por caractere gera sequências muito longas, e tokenizar por palavra inteira gera um vocabulário enorme e não lida bem com palavras nunca vistas. Tokenização por subpalavra parte de caracteres e vai mesclando os pares mais frequentes no corpus de treino, até formar um vocabulário de tamanho fixo (tipicamente dezenas de milhares de tokens) que consegue representar qualquer palavra, mesmo as raras, combinando pedaços menores.

Por exemplo, uma palavra incomum pode ser dividida em dois ou três tokens, enquanto uma palavra comum vira um único token. Isso explica por que a contagem de tokens de um texto raramente coincide com sua contagem de palavras, algo relevante inclusive para o dimensionamento da janela de contexto discutido na série de engenharia de contexto deste repositório.

## 6.3 Embeddings

Cada token é convertido em um vetor denso de números reais, chamado embedding, antes de entrar no modelo. Esse vetor é aprendido durante o treinamento, não definido manualmente, e captura relações semânticas: tokens usados em contextos parecidos tendem a ter embeddings próximos no espaço vetorial.

Esse é o mesmo princípio mencionado no documento [2. Feature engineering e hiperparâmetros](./2-feature-engineering-e-hiperparametros.md) para representar variáveis categóricas de alta cardinalidade, aplicado aqui a um vocabulário de dezenas de milhares de tokens.

## 6.4 Positional encoding

O mecanismo de self-attention, descrito a seguir, trata a sequência como um conjunto: sozinho, ele não tem noção de ordem entre os tokens. Isso é um problema, já que "o cão mordeu o homem" e "o homem mordeu o cão" têm os mesmos tokens em ordens diferentes e significados opostos.

Para resolver isso, o Transformer soma a cada embedding de token um vetor de positional encoding, que codifica a posição daquele token na sequência. Na formulação original, esses vetores são gerados por funções seno e cosseno de frequências diferentes, o que permite ao modelo distinguir posições e também generalizar razoavelmente para sequências mais longas do que as vistas no treino. Implementações mais recentes usam variantes aprendidas ou esquemas como RoPE (Rotary Position Embedding), mas o objetivo é sempre o mesmo: injetar informação de ordem que o mecanismo de atenção não captura sozinho.

## 6.5 Self-attention: Query, Key e Value

Este é o mecanismo central do Transformer. Para cada token da sequência, o modelo gera três vetores derivados do embedding daquele token, por meio de três matrizes de pesos aprendidas: Query (Q), Key (K) e Value (V).

De forma intuitiva, o Query representa o que aquele token está "procurando" no restante da sequência. O Key representa o que cada token "oferece" como informação. O Value representa o conteúdo real que será passado adiante se a atenção recair sobre aquele token.

O cálculo acontece em três passos. Primeiro, o Query de um token é comparado (via produto escalar) com o Key de todos os outros tokens, gerando um score de compatibilidade para cada par. Segundo, esses scores passam por uma função softmax, que os transforma em pesos que somam 1, os pesos de atenção. Terceiro, o vetor de saída para aquele token é a soma ponderada dos Values de todos os tokens, usando esses pesos de atenção.

Na prática, isso significa que, ao processar a palavra "banco" em uma frase, o mecanismo de atenção pode aprender a dar peso alto para palavras próximas como "rio" ou "dinheiro" para determinar qual sentido da palavra está em jogo naquele contexto específico, e esse cálculo acontece para todos os tokens da sequência simultaneamente, não um de cada vez.

**Multi-head attention** repete esse processo várias vezes em paralelo, com conjuntos diferentes de matrizes Q, K e V (as "cabeças" de atenção), permitindo que o modelo capture diferentes tipos de relação ao mesmo tempo, como relações sintáticas em uma cabeça e relações semânticas em outra. Os resultados de todas as cabeças são concatenados e combinados por mais uma camada de pesos aprendidos.

## 6.6 Arquitetura completa do Transformer

Um bloco Transformer combina a camada de multi-head attention com uma rede feedforward simples (como as vistas no documento anterior), aplicada de forma independente a cada posição, além de conexões residuais e normalização de camada (layer normalization), que ajudam a estabilizar o treinamento de redes muito profundas.

A arquitetura original tem duas partes: um encoder, que processa a sequência de entrada, e um decoder, que gera a sequência de saída token a token, usado por exemplo em tradução automática. A maioria dos LLMs atuais de geração de texto, como a família GPT, usa apenas a parte decoder, adaptada para prever o próximo token da sequência repetidamente. Modelos como o BERT usam apenas a parte encoder, voltados para tarefas de compreensão em vez de geração.

## 6.7 O que são LLMs

Um LLM (Large Language Model) é, na essência, um Transformer decoder de grande escala, treinado para prever o próximo token de uma sequência de texto, sobre um volume massivo de dados textuais.

Apesar da tarefa de treino ser simples de descrever, prever o próximo token, treinar essa tarefa em escala suficiente (bilhões de parâmetros, treinados sobre trilhões de tokens) faz o modelo aprender, implicitamente, gramática, fatos sobre o mundo presentes nos dados de treino, e padrões de raciocínio, sem que nenhuma dessas capacidades tenha sido explicitamente programada.

O treinamento de um LLM moderno costuma ter pelo menos duas etapas. O **pré-treinamento** (pretraining) é a etapa de prever o próximo token sobre um corpus massivo e geral, onde o modelo adquire conhecimento amplo mas ainda não é bom em seguir instruções. O **ajuste fino** (fine-tuning), frequentemente via instruction tuning e RLHF (Reinforcement Learning from Human Feedback), ajusta o modelo para seguir instruções e responder de forma mais alinhada às expectativas humanas, usando um volume de dados muito menor que o pré-treinamento.

## 6.8 Limitações e riscos

**Alucinação:** o modelo pode gerar informação plausível, mas factualmente incorreta, com o mesmo grau de confiança de uma informação correta. Isso decorre diretamente da forma como o modelo é treinado: prever o próximo token mais provável não é o mesmo que verificar a veracidade de uma afirmação.

**Janela de contexto limitada:** o modelo só "enxerga" uma quantidade finita de tokens de cada vez. Esse tema, junto com estratégias de recuperação de informação relevante para contornar esse limite, é tratado em detalhe na série de engenharia de contexto deste repositório.

**Viés herdado dos dados de treino:** como o modelo aprende padrões estatísticos de um corpus real, ele pode reproduzir vieses presentes nesses dados. O tema é retomado com mais profundidade no documento [7. Ética e responsabilidade](./7-etica-e-responsabilidade.md).

**Custo computacional:** o mecanismo de self-attention, na sua forma original, tem custo que cresce quadraticamente com o tamanho da sequência, o que torna processar contextos muito longos computacionalmente caro. Variantes mais recentes de atenção buscam reduzir esse custo.

## 6.9 Ponte com engenharia de contexto

Os documentos da série de context engineering deste repositório tratam de como estruturar, filtrar e gerenciar a informação que é apresentada a um LLM já treinado, no momento do uso (inference), incluindo técnicas como RAG (Retrieval-Augmented Generation), gerenciamento de janela de contexto e memória de agentes.

Este documento cobre a camada anterior: como o modelo em si é construído e treinado. Entender tokenização e embeddings, por exemplo, explica por que a contagem de tokens de um prompt não coincide com a contagem de palavras, algo relevante ao dimensionar o que cabe na janela de contexto. Entender o mecanismo de self-attention explica por que a posição da informação dentro do prompt pode afetar o quanto o modelo "presta atenção" nela, um tema prático abordado nos princípios de boas práticas da série de context engineering.

## 6.10 Resumo

O Transformer substitui o processamento sequencial das RNNs por um mecanismo de atenção que compara todos os tokens entre si em paralelo, usando Query, Key e Value. Tokenização e embeddings convertem texto em representações numéricas que o modelo consegue processar, e positional encoding reintroduz a noção de ordem que a atenção, sozinha, não captura. LLMs são Transformers decoder treinados em larga escala para prever o próximo token, capacidade da qual emergem, indiretamente, conhecimento e habilidades de linguagem, junto com limitações reais como alucinação e viés.
