# 2. Feature engineering e hiperparâmetros

Antes de escolher um algoritmo, é preciso entender e preparar os dados que serão usados. Este documento cobre a engenharia de atributos e, na sequência, os hiperparâmetros que controlam como um modelo aprende, dois temas que na prática acontecem em paralelo com a escolha e o ajuste do algoritmo, não depois dela.

## 2.1 O que é feature engineering

Feature engineering é o processo de criar, transformar e selecionar variáveis (features) que serão usadas pelo modelo.

O objetivo é tornar os dados mais representativos do problema e facilitar o aprendizado. Em muitos projetos, esse processo tem impacto tão grande quanto a escolha do algoritmo, em vários casos maior.

Uma feature bem construída pode ajudar o modelo a aprender padrões mais úteis, enquanto uma feature fraca pode dificultar a performance mesmo com um algoritmo sofisticado.

## 2.2 Por que isso é importante

Em problemas reais, os dados brutos raramente chegam prontos para o treino. Eles podem conter valores ausentes, escalas muito diferentes, dados categóricos sem representação numérica, colunas redundantes e sinais pouco relevantes para o problema.

A engenharia de atributos busca transformar esses dados em uma forma mais útil para o modelo. Como será visto no próximo documento, alguns algoritmos (K-NN, SVM, regressão regularizada) são sensíveis à escala das variáveis, enquanto outros (árvores de decisão, Random Forest) não são, o que significa que a preparação necessária dos dados muda de acordo com o algoritmo escolhido.

## 2.3 Tipos de transformação

Algumas transformações comuns incluem criação de novas variáveis, normalização e padronização, transformação logarítmica, codificação de variáveis categóricas, imputação de valores ausentes e seleção de atributos mais relevantes.

**Exemplos:** normalizar idade e salário para uma mesma escala quando o modelo é sensível a magnitude, transformar uma variável de preço com distribuição muito assimétrica usando log, converter categorias como cidade, segmento ou tipo de produto em valores numéricos para entrada do modelo.

## 2.4 Codificação de variáveis categóricas

Converter categorias em números não é uma operação única, a técnica certa depende da natureza da variável e do algoritmo que vai consumi-la. Escolher mal aqui é um erro comum e caro.

**One-hot encoding:** cria uma coluna binária para cada categoria possível. Indicado para variáveis categóricas sem ordem (nominais), como cidade ou cor. Vantagem: não introduz uma relação de ordem inexistente entre categorias. Limitação: em variáveis de alta cardinalidade, com muitas categorias distintas como CEP ou SKU de produto, gera um número explosivo de colunas, problema conhecido como maldição da dimensionalidade.

**Ordinal encoding:** atribui um número inteiro a cada categoria, respeitando uma ordem. Indicado quando a variável tem uma ordem natural, como nível de escolaridade (fundamental, médio, superior) ou avaliação (ruim, regular, bom, ótimo). Usar ordinal encoding em uma variável sem ordem real, como cidade, introduz uma relação numérica falsa que pode confundir o modelo.

**Target encoding:** substitui cada categoria pela média (ou outra estatística) da variável alvo para aquela categoria. Útil para variáveis de alta cardinalidade, onde one-hot geraria colunas demais. Exemplo: em bairro com centenas de valores possíveis, substituir cada bairro pela taxa média de churn observada naquele bairro. Risco importante: se calculado usando todo o dataset, incluindo os dados que depois vão para teste ou validação, o target encoding vaza informação do alvo para as features, o que caracteriza data leakage (seção 2.6). Deve ser calculado apenas com os dados de treino, de preferência com técnicas de regularização, como suavização ou cálculo via cross-validation, para reduzir overfitting em categorias raras.

**Embeddings para variáveis categóricas:** em problemas com variáveis de cardinalidade muito alta, como ID de produto em um catálogo com milhões de itens, redes neurais costumam usar embeddings, onde cada categoria é mapeada para um vetor denso de números reais aprendido durante o treinamento. É a mesma ideia usada para representar palavras e tokens em modelos de linguagem.

## 2.5 Tratamento de valores ausentes

Valores ausentes não podem simplesmente ser ignorados, a forma como são tratados afeta diretamente o resultado do modelo.

**Remoção:** descartar linhas ou colunas com muitos valores ausentes. Só é seguro quando a ausência é pequena e aleatória.

**Imputação por estatística simples:** substituir pela média, mediana (para variáveis numéricas) ou moda (para categóricas).

**Imputação por modelo:** prever o valor ausente com base em outras variáveis, usando por exemplo KNN Imputer ou um modelo de regressão auxiliar.

**Indicador de ausência:** criar uma coluna binária extra indicando se o valor estava ausente, preservando o sinal de que a ausência em si pode ser informativa. Renda não informada, por exemplo, pode ser um padrão relevante para o problema.

## 2.6 Data leakage em feature engineering

Data leakage, ou vazamento de dados, acontece quando uma feature carrega, direta ou indiretamente, informação que não estaria disponível no momento real da previsão, geralmente porque foi calculada usando dados de validação, teste ou até informação futura. É um dos erros mais silenciosos em ML: o modelo parece ter desempenho excelente na avaliação e falha completamente em produção.

**Estatísticas calculadas com o dataset inteiro:** normalizar, imputar ou calcular target encoding usando média ou desvio-padrão de todo o dataset, incluindo teste, antes de dividir em treino e teste. O correto é calcular essas estatísticas somente com o conjunto de treino e aplicá-las depois aos conjuntos de validação e teste.

**Features que usam informação futura:** em um problema de previsão de churn, por exemplo, usar data de cancelamento (ou qualquer variável derivada dela) como feature. Essa informação só existe depois que o evento que se quer prever já aconteceu.

**Duplicatas entre treino e teste:** se o mesmo cliente, transação ou registro aparecer em treino e teste, por não considerar que um cliente pode ter múltiplas linhas no dataset, o modelo pode decorar esse registro em vez de aprender um padrão generalizável.

Regra prática: qualquer transformação que dependa de estatísticas do dataset (média, desvio-padrão, contagem de categorias, target encoding) deve ser ajustada (fit) apenas nos dados de treino, e depois aplicada (transform) nos dados de validação e teste, nunca o contrário. É por isso que pipelines com fit e transform separados, como os do scikit-learn, existem: eles ajudam a evitar esse erro por construção.

## 2.7 Exemplos práticos

Em um problema de previsão de preço de imóveis, novas features podem incluir preço por metro quadrado, idade do imóvel, tempo de residência do proprietário, distância até o centro da cidade e proximidade de escolas, hospitais ou transporte público. Essas variáveis podem ter mais impacto do que os dados brutos originais, porque carregam informação mais útil para a tarefa.

Outro exemplo é um problema de churn. Em vez de usar apenas o número de acessos, pode-se criar features como frequência média de uso, tempo desde o último login, número de interações recentes e crescimento ou queda no uso ao longo do tempo.

Nesse mesmo exemplo de churn, um erro clássico de vazamento seria incluir motivo do cancelamento como feature: essa informação só existe para quem já cancelou, então não estaria disponível no momento em que a previsão precisa ser feita.

## 2.8 O que são hiperparâmetros

Hiperparâmetros são configurações definidas antes do treinamento. Eles controlam a forma como o algoritmo aprende, mas não são aprendidos automaticamente a partir dos dados.

Exemplos: profundidade máxima de uma árvore, número de árvores em um Random Forest, learning rate em redes neurais, número de vizinhos em K-NN, número de épocas de treinamento.

Enquanto os parâmetros do modelo são ajustados durante o treino, os hiperparâmetros precisam ser definidos pelo cientista ou pelo engenheiro de dados.

## 2.9 Por que otimizar hiperparâmetros

Uma configuração padrão nem sempre é a melhor para um problema específico. Ajustar hiperparâmetros pode melhorar a precisão, reduzir overfitting, acelerar o treinamento e aumentar a capacidade de generalização. Em projetos reais, essa etapa pode fazer diferença significativa no resultado final.

## 2.10 Técnicas de otimização

**Grid Search:** testa um conjunto de combinações predefinido. Vantagem: simples e fácil de interpretar. Desvantagem: pode ser caro computacionalmente quando o espaço de busca é grande.

**Random Search:** seleciona combinações aleatórias de forma mais eficiente. Vantagem: costuma encontrar boas configurações com menos testes do que grid search. Desvantagem: pode perder configurações muito boas se a busca for muito limitada.

**Bayesian Optimization:** usa resultados anteriores para escolher novas configurações com maior chance de sucesso. Vantagem: mais inteligente e geralmente mais eficiente em problemas maiores. Desvantagem: exige mais implementação e interpretação.

**Hyperband:** combina busca e parada antecipada para economizar tempo computacional. Útil quando o treinamento é caro e muitas combinações precisam ser avaliadas rapidamente.

Importante: assim como as estatísticas de feature engineering, a busca de hiperparâmetros deve usar apenas treino e validação, nunca o conjunto de teste, sob risco de gerar uma estimativa otimista demais do desempenho final.

## 2.11 Boas práticas

Entender bem o problema antes de criar features. Evitar atributos redundantes ou altamente correlacionados. Nunca calcular estatísticas de normalização, imputação ou encoding usando dados de teste. Não usar dados de teste para escolher features de forma indevida. Usar validação cruzada para avaliar as configurações escolhidas. Documentar as transformações aplicadas para garantir reprodutibilidade. Manter pipelines consistentes entre treino e produção, já que a mesma sequência de transformações aplicada no treino precisa ser aplicada exatamente da mesma forma na hora de gerar previsões reais.

## 2.12 Pipeline de treinamento

Em muitos projetos, a sequência fica assim:

**1. Coleta e limpeza de dados:** primeira etapa de preparação do conjunto de dados.

**2. Engenharia de atributos:** ajustada apenas com dados de treino.

**3. Divisão em treino, validação e teste:** ou divisão seguida de ajuste das transformações, a depender da técnica usada.

**4. Treinamento do modelo:** escolha e ajuste do algoritmo com os dados de treino.

**5. Ajuste de hiperparâmetros:** busca pela melhor configuração usando treino e validação.

**6. Avaliação final:** medição de desempenho com o conjunto de teste.

**7. Deploy e monitoramento:** disponibilização do modelo e acompanhamento contínuo.

Essa estrutura ajuda a garantir que as mesmas transformações sejam aplicadas de forma consistente em todos os ciclos. Na prática, os passos 2 e 3 costumam se entrelaçar: a divisão treino e teste geralmente acontece antes do ajuste de qualquer estatística de transformação, exatamente para evitar o vazamento descrito na seção 2.6.

## 2.13 Resumo

Feature engineering e ajuste de hiperparâmetros são parte essencial do ciclo de desenvolvimento de modelos, e acontecem antes e em paralelo à escolha do algoritmo, não depois dela. Eles podem fazer uma grande diferença no desempenho final, muitas vezes mais do que simplesmente trocar de algoritmo. O cuidado com vazamento de dados nessa etapa é tão importante quanto a criação das features em si: uma feature vazada pode mascarar completamente o verdadeiro desempenho do modelo.