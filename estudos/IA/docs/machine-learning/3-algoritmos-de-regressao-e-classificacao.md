# 3. Algoritmos de regressão e classificação

Depois de preparar os dados, é hora de escolher um algoritmo. Este documento cobre os principais algoritmos de regressão (previsão de valores contínuos) e classificação (previsão de categorias), com a intuição matemática mínima necessária para entender como cada um toma decisões.

## 3.1 Regressão linear

Modela a relação entre variáveis de entrada e uma saída contínua por meio de uma combinação linear dos atributos.

A previsão é dada por uma soma ponderada das variáveis de entrada mais um termo de intercepto: y = w1x1 + w2x2 + ... + wnxn + b. O treinamento encontra os pesos w que minimizam o erro quadrático médio entre a previsão e o valor real.

**Exemplo:** prever o preço de um imóvel a partir de área, número de quartos e localização.

**Quando usar:** quando a relação entre entrada e saída é aproximadamente linear e a interpretabilidade dos coeficientes importa.

## 3.2 Regressão logística

Apesar do nome, é usada para classificação, geralmente binária. Em vez de prever um valor contínuo diretamente, estima a probabilidade de uma observação pertencer a uma classe.

A combinação linear das entradas passa por uma função sigmoide, que comprime o resultado para o intervalo entre 0 e 1, interpretado como probabilidade. Um limiar de decisão (tipicamente 0,5) converte essa probabilidade em classe. Para problemas com mais de duas classes, existe a variante multinomial (softmax regression), que generaliza a mesma ideia usando uma função softmax no lugar da sigmoide.

**Exemplo:** prever se um cliente vai cancelar um serviço (sim ou não) com base em uso, tempo de contrato e histórico de pagamento.

**Quando usar:** como baseline em problemas de classificação, especialmente quando a interpretabilidade dos coeficientes é importante para o negócio.

## 3.3 K-Nearest Neighbors (K-NN)

Classifica ou prevê um valor com base nos exemplos mais próximos no conjunto de treino.

A distância entre pontos é calculada geralmente pela distância euclidiana. Para classificação, a classe prevista é a mais frequente entre os K vizinhos mais próximos. Para regressão, a previsão é a média dos valores dos K vizinhos.

Por depender diretamente de distância, o K-NN é sensível à escala das variáveis: uma variável com valores na casa dos milhares (como salário) domina o cálculo da distância sobre uma variável na casa das unidades (como número de filhos), a menos que os dados sejam normalizados antes do treino.

**Exemplo:** recomendar produtos parecidos com base em características de compras anteriores.

**Quando usar:** datasets pequenos ou médios, com poucas variáveis e necessidade de decisão baseada em similaridade.

## 3.4 Árvore de decisão

Divide os dados em subconjuntos com base em condições sobre as variáveis, formando uma estrutura em árvore.

A cada divisão (split), o algoritmo escolhe a variável e o ponto de corte que melhor separam as classes. Os critérios mais comuns são o índice Gini e a entropia (usada no cálculo do ganho de informação), ambos medidas de quão "misturadas" as classes estão em um nó. Para regressão, o critério costuma ser a redução da variância.

Árvores não são sensíveis à escala das variáveis, já que cada split avalia uma variável de cada vez, sem calcular distâncias entre pontos.

**Exemplo:** decidir se um cliente é elegível para crédito com base em renda, histórico e idade.

**Quando usar:** quando a interpretabilidade é essencial e as regras de decisão precisam ser explicáveis para o negócio.

## 3.5 Naive Bayes

Classificador probabilístico baseado no teorema de Bayes, com a suposição simplificadora (naive) de que as variáveis de entrada são independentes entre si dado a classe.

Calcula, para cada classe possível, a probabilidade de observar aquele conjunto de atributos, e escolhe a classe com maior probabilidade. Apesar da suposição de independência raramente ser verdadeira na prática, o algoritmo costuma funcionar bem em problemas com muitas variáveis, como classificação de texto.

**Exemplo:** classificar e-mails como spam ou não spam com base na frequência de palavras.

**Quando usar:** problemas com muitas features, especialmente texto, e quando é necessário um baseline rápido de treinar.

## 3.6 Support Vector Machine (SVM)

Busca o hiperplano que melhor separa as classes, maximizando a margem entre elas.

O hiperplano é a fronteira de decisão no espaço das variáveis. A margem é a distância entre o hiperplano e os pontos mais próximos de cada classe (os vetores de suporte). Quanto maior a margem, mais o modelo tende a generalizar bem. Quando os dados não são linearmente separáveis, o SVM pode usar funções de kernel (como o kernel RBF) para projetar os dados em um espaço de maior dimensão, onde a separação linear se torna possível.

Assim como o K-NN, o SVM é sensível à escala das variáveis, já que a definição de margem depende de distância.

**Exemplo:** detectar fraudes em transações financeiras com base em padrões de uso.

**Quando usar:** datasets de porte pequeno a médio, com fronteira de decisão complexa e necessidade de boa capacidade de generalização.

## 3.7 Random Forest

Ensemble de múltiplas árvores de decisão treinadas em subconjuntos diferentes dos dados e das variáveis, cujas previsões são combinadas.

Cada árvore é treinada com uma amostra aleatória dos dados (bagging) e considera apenas um subconjunto aleatório das variáveis em cada split. Para classificação, a previsão final é a classe mais votada entre as árvores. Para regressão, é a média das previsões. Essa combinação reduz a variância em relação a uma única árvore, atacando diretamente o overfitting.

Assim como árvores individuais, o Random Forest não é sensível à escala das variáveis, e funciona tanto para regressão quanto para classificação.

**Exemplo:** prever inadimplência combinando várias árvores treinadas com diferentes amostras de clientes.

**Quando usar:** quando se precisa de robustez e boa performance sem muito ajuste fino, e a interpretabilidade individual das árvores é menos importante que o desempenho.

## 3.8 Boosting (Gradient Boosting, XGBoost, LightGBM)

Constrói uma sequência de modelos fracos, geralmente árvores rasas, em que cada novo modelo corrige os erros do anterior.

Diferente do Random Forest, que treina árvores em paralelo e de forma independente, o boosting treina árvores sequencialmente: cada nova árvore foca nos exemplos que o conjunto de árvores anteriores errou mais. Implementações populares como XGBoost e LightGBM otimizam esse processo para velocidade e desempenho.

Também não é sensível à escala das variáveis e funciona para regressão e classificação, mas costuma exigir mais cuidado no ajuste de hiperparâmetros para evitar overfitting do que o Random Forest.

**Exemplo:** prever risco de crédito com alta precisão em competições e problemas reais complexos.

**Quando usar:** quando se busca o melhor desempenho possível e há tempo para ajuste cuidadoso de hiperparâmetros.

## 3.9 Sensibilidade a escala e necessidade de pré-processamento

A tabela abaixo resume, para cada algoritmo, se ele exige normalização ou padronização das variáveis antes do treino, e se serve para regressão, classificação, ou ambos. Ver documento [2. Feature engineering e hiperparâmetros](./2-feature-engineering-e-hiperparametros.md) para as técnicas de normalização.

| Algoritmo | Sensível a escala | Regressão | Classificação |
|---|---|---|---|
| Regressão linear | Não exige, mas recomendada | Sim | Não |
| Regressão logística | Não exige, mas recomendada | Não | Sim |
| K-NN | Sim, exige normalização | Sim | Sim |
| Árvore de decisão | Não | Sim | Sim |
| Naive Bayes | Não | Não | Sim |
| SVM | Sim, exige normalização | Sim | Sim |
| Random Forest | Não | Sim | Sim |
| Boosting | Não | Sim | Sim |

## 3.10 Como escolher um algoritmo

Não existe um algoritmo universalmente melhor. A escolha depende do tipo de problema, do volume de dados, da necessidade de interpretabilidade e do tempo disponível para ajuste.

Como ponto de partida, modelos lineares (regressão linear, regressão logística) servem como baseline rápido e interpretável. Árvores e ensembles (Random Forest, Boosting) costumam performar melhor em dados tabulares reais, à custa de menor interpretabilidade direta. K-NN e SVM funcionam bem em datasets menores, mas exigem atenção ao pré-processamento. Naive Bayes é uma escolha eficiente quando há muitas variáveis, como em classificação de texto.

Na prática, é comum testar mais de um algoritmo e comparar o desempenho usando as métricas e técnicas de validação descritas no próximo documento, [4. Avaliação e generalização de modelos](./4-avaliacao-e-generalizacao-de-modelos.md).

## 3.11 Resumo

Cada algoritmo tem suposições diferentes sobre os dados e formas diferentes de tomar decisões: uns dependem de distância, outros de divisões sucessivas, outros de probabilidade. Entender essas suposições, e não apenas o nome do algoritmo, é o que permite escolher a ferramenta certa para cada problema e evitar erros comuns, como aplicar K-NN ou SVM sem normalizar os dados antes.
