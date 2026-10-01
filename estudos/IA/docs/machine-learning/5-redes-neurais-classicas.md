# 5. Redes neurais clássicas

Os algoritmos vistos no documento anterior funcionam bem para muitos problemas com dados tabulares, mas têm limitações em domínios como imagem, áudio, texto e sequências temporais. Este documento cobre os fundamentos de redes neurais e as arquiteturas clássicas que antecedem os Transformers, tratados no próximo documento.

Antes disso, duas técnicas de aprendizado não supervisionado merecem menção, por completarem o quadro de algoritmos de ML fora do escopo de regressão e classificação supervisionadas.

## 5.1 Clusterização

Agrupa exemplos semelhantes sem usar rótulos (aprendizado não supervisionado). O algoritmo mais comum é o K-Means, que escolhe k centróides iniciais, atribui cada ponto ao centróide mais próximo, recalcula os centróides como a média dos pontos atribuídos, e repete esse processo até convergir.

**Exemplo:** segmentar clientes em grupos de comportamento de compra semelhante, sem definir previamente quais são esses grupos.

## 5.2 Redução de dimensionalidade

Reduz o número de variáveis mantendo o máximo possível da informação original. PCA (Principal Component Analysis) é a técnica mais comum: encontra novas variáveis (componentes principais), combinações lineares das variáveis originais, ordenadas pela quantidade de variância que capturam.

**Exemplo:** reduzir centenas de variáveis correlacionadas para um punhado de componentes antes de treinar um modelo, ou para visualizar dados de alta dimensão em duas ou três dimensões.

## 5.3 Perceptron e redes neurais feedforward

O perceptron é a unidade básica de uma rede neural: recebe entradas, aplica pesos e um viés (bias), soma tudo, e passa o resultado por uma função de ativação.

A função de ativação introduz não linearidade. Sem ela, empilhar múltiplas camadas seria matematicamente equivalente a uma única camada linear, perdendo a capacidade de aprender padrões complexos. As funções de ativação mais comuns são ReLU (que zera valores negativos e mantém positivos), sigmoide (comprime para o intervalo entre 0 e 1) e tanh (comprime para o intervalo entre -1 e 1).

Uma rede neural feedforward empilha várias camadas de perceptrons: uma camada de entrada, uma ou mais camadas ocultas, e uma camada de saída. O treinamento ajusta os pesos de todas as camadas usando o algoritmo de backpropagation, que calcula o gradiente do erro em relação a cada peso e atualiza os pesos na direção que reduz o erro (gradient descent).

**Exemplo:** prever a probabilidade de um cliente cancelar um serviço a partir de dezenas de variáveis, quando a relação entre elas é complexa demais para um modelo linear.

## 5.4 Redes neurais convolucionais (CNN)

Arquitetura especializada em dados com estrutura espacial, como imagens.

Em vez de conectar cada neurônio a todos os pixels da imagem (o que geraria um número enorme de parâmetros), uma camada convolucional aplica pequenos filtros (kernels) que percorrem a imagem, detectando padrões locais como bordas, texturas e formas. Camadas convolucionais iniciais tendem a aprender padrões simples, como bordas, enquanto camadas mais profundas combinam esses padrões em conceitos mais complexos, como partes de objetos.

Camadas de pooling (como max pooling) reduzem a dimensão espacial entre convoluções, tornando a rede mais eficiente e um pouco mais robusta a pequenas variações de posição do objeto na imagem.

**Exemplo:** classificar imagens médicas para identificar sinais de uma doença, ou detectar objetos em fotos.

## 5.5 Redes neurais recorrentes (RNN, LSTM, GRU)

Arquiteturas especializadas em dados sequenciais, como texto, áudio ou séries temporais, onde a ordem dos elementos importa.

Uma RNN processa a sequência elemento por elemento, mantendo um estado interno (memória) que é atualizado a cada passo e carrega informação dos elementos anteriores. O problema prático das RNNs simples é o desaparecimento do gradiente (vanishing gradient): em sequências longas, a influência dos primeiros elementos se dilui tanto durante o treinamento que a rede efetivamente esquece o começo da sequência.

**LSTM (Long Short-Term Memory)** resolve esse problema com um mecanismo de portões (gates), que controlam explicitamente o que é lembrado, o que é esquecido e o que é passado adiante a cada passo, permitindo reter informação relevante por sequências mais longas.

**GRU (Gated Recurrent Unit)** é uma variante mais simples da LSTM, com menos portões e portanto menos parâmetros, geralmente com desempenho comparável e treino mais rápido.

**Exemplo:** prever a próxima palavra em uma frase, ou prever a demanda futura de um produto a partir do histórico de vendas.

Essas arquiteturas foram, por muitos anos, o padrão para tarefas de linguagem, até serem amplamente substituídas por Transformers, tratados no próximo documento, que resolvem o problema de dependências longas de outra forma e permitem processamento paralelo em vez de sequencial.

## 5.6 Treinamento de redes neurais

Alguns conceitos são comuns a todas as arquiteturas de redes neurais, independentemente da estrutura específica.

**Função de perda (loss function):** mede o quão distante a previsão do modelo está do valor real. A escolha depende da tarefa: erro quadrático médio para regressão, entropia cruzada (cross-entropy) para classificação.

**Gradient descent:** algoritmo de otimização que ajusta os pesos na direção que reduz a função de perda, guiado pelo gradiente calculado via backpropagation. Variantes como SGD, Adam e RMSprop diferem na forma como ajustam a taxa de aprendizado ao longo do treino.

**Épocas e batches:** uma época é uma passada completa pelos dados de treino. Como processar todo o dataset de uma vez costuma ser inviável computacionalmente, os dados são divididos em lotes menores (batches ou mini-batches), e os pesos são atualizados após cada lote.

**Overfitting em redes neurais:** redes neurais, por terem muitos parâmetros, são particularmente propensas a overfitting. Técnicas como dropout (desativar aleatoriamente neurônios durante o treino), regularização L2 e early stopping (interromper o treino quando o desempenho na validação para de melhorar) ajudam a mitigar esse risco, complementando as práticas de validação já discutidas no documento [4. Avaliação e generalização de modelos](./4-avaliacao-e-generalizacao-de-modelos.md).

## 5.7 Quando usar redes neurais

Redes neurais tendem a superar os algoritmos clássicos do documento anterior em problemas com grande volume de dados e estrutura complexa, como imagem, áudio, texto e vídeo. Em contrapartida, exigem mais dados para treinar bem, mais poder computacional, e são mais difíceis de interpretar.

Para a maioria dos problemas com dados tabulares e volume moderado, algoritmos como Random Forest e Boosting, vistos no documento anterior, costumam entregar desempenho equivalente ou melhor, com muito menos custo de treinamento e maior interpretabilidade. Redes neurais se tornam a escolha natural principalmente quando o problema envolve dados não estruturados, como as imagens, textos e sequências descritos neste documento.

## 5.8 Resumo

Redes neurais clássicas (feedforward, CNN, RNN e suas variantes) formam a base sobre a qual os Transformers foram construídos, e continuam sendo a escolha adequada para muitos problemas, especialmente em visão computacional e séries temporais. Entender como elas processam informação (localmente, no caso das CNNs, e sequencialmente, no caso das RNNs) ajuda a entender, por contraste, o que há de diferente na arquitetura Transformer, tratada no próximo documento.
