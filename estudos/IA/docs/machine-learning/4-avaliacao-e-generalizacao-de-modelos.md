# 4. Avaliação de modelos e generalização

Avaliar um modelo é essencial para verificar se ele realmente aprende padrões úteis e não apenas memoriza os dados usados no treinamento.

## 4.1 Por que avaliar?

A avaliação ajuda a responder perguntas importantes antes de colocar um modelo em produção.

- O modelo acertou o suficiente?
- Ele generaliza bem para novos dados?
- Há risco de overfitting ou underfitting?
- O desempenho é bom o bastante para a decisão de negócio?

Sem avaliação adequada, um modelo pode parecer útil em teoria, mas falhar em cenários reais.

## 4.2 Divisão de dados

Um fluxo comum é dividir os dados em:

- treino: usado para ajustar os pesos e aprender os padrões
- validação: usado para escolher configurações e comparar modelos
- teste: usado para medir o desempenho final em dados não vistos

Esse procedimento evita que o modelo seja avaliado com os mesmos dados usados para aprender. Isso gera uma estimativa mais honesta de sua capacidade de generalização.

## 4.3 Métricas para classificação

Para problemas com respostas categóricas, algumas métricas comuns são:

- Accuracy: proporção de acertos no geral
- Precision: quanto das previsões positivas foram realmente corretas
- Recall: quanto dos casos positivos reais foram identificados
- F1-score: equilíbrio entre precision e recall
- AUC-ROC: capacidade do modelo de ordenar corretamente as classes

Essas métricas ajudam a comparar modelos em problemas com classes diferentes, como fraude, churn, diagnóstico ou recomendação.

## 4.4 Métricas para regressão

Para problemas de previsão numérica, podem ser usadas:

- MAE: erro médio absoluto
- MSE: erro quadrático médio
- RMSE: raiz do erro quadrático médio
- $R^2$: quanto da variação dos dados é explicada pelo modelo

Essas métricas medem o erro entre os valores previstos e os valores reais.

## 4.5 Validação cruzada

A validação cruzada divide os dados em várias partes e avalia o modelo em diferentes combinações.

- Em um esquema $k$-fold, os dados são divididos em $k$ partes.
- O modelo é treinado $k$ vezes, cada vez deixando uma parte para validação.
- Isso reduz o risco de uma avaliação muito favorável por causa de uma divisão específica.

Essa técnica é especialmente útil quando o conjunto de dados é pequeno ou quando a estabilidade do modelo é importante.

## 4.6 Overfitting e underfitting

### Underfitting

O modelo é muito simples para capturar os padrões importantes presentes nos dados.

Sinais comuns:

- desempenho ruim tanto no treino quanto na validação
- alta taxa de erro em todas as etapas
- dificuldade de aprender relações relevantes

### Overfitting

O modelo aprende demais os dados de treino e perde capacidade de generalizar.

Sinais comuns:

- excelente desempenho no treino
- desempenho ruim em dados novos
- memorização de detalhes específicos e ruídos do conjunto de treinamento

## 4.7 Bias e variance

Esses conceitos ajudam a entender o equilíbrio entre simplicidade e complexidade.

- Bias alto está associado a underfitting.
- Variance alta está associada a overfitting.
- O objetivo é encontrar um ponto intermediário em que o modelo aprenda padrões úteis sem memorizar excessivamente os dados.

Em muitos casos, reduzir o overfitting exige regularização, mais dados ou simplificação do modelo.

## 4.8 Interpretabilidade e monitoramento

Em alguns cenários, não basta saber que o modelo acertou. Também é importante entender por que ele tomou determinada decisão.

Técnicas como SHAP e LIME ajudam a explicar previsões. Isso é especialmente relevante em áreas como saúde, finanças e crédito, onde transparência e rastreabilidade são importantes.

Em produção, é essencial monitorar:

- desempenho ao longo do tempo;
- mudança nos dados, conhecida como data drift;
- degradação de precisão;
- comportamento em diferentes segmentos de clientes ou usuários.

## 4.9 Avaliação em produção

A avaliação não termina quando o modelo é treinado. Em ambientes reais, a performance precisa ser acompanhada continuamente.

Exemplo prático:

- um modelo de detecção de fraude pode começar a falhar se os padrões de fraude mudarem;
- um modelo de recomendação pode perder eficácia se o comportamento dos usuários mudar.

Por isso, re-treinamento, testes periódicos e análise de métricas de produção são parte essencial do ciclo de vida do modelo.

## 4.10 Resumo

Uma boa avaliação não se resume a uma única métrica. Ela deve considerar robustez, capacidade de generalização, qualidade das previsões e comportamento do modelo em cenários reais.
