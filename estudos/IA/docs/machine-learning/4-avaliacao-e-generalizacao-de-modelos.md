# 4. Avaliação e generalização de modelos

Treinar um modelo não é suficiente. É preciso avaliar se ele realmente aprendeu padrões úteis, e não apenas decorou os dados de treino. Este documento cobre as métricas e técnicas usadas para medir desempenho e generalização.

## 4.1 Divisão treino, validação e teste

Antes de qualquer avaliação, os dados precisam ser divididos em conjuntos separados.

O conjunto de **treino** é usado para ajustar os parâmetros do modelo. O conjunto de **validação** é usado para comparar configurações e ajustar hiperparâmetros durante o desenvolvimento. O conjunto de **teste** é usado apenas uma vez, ao final, para estimar como o modelo se comportará em dados nunca vistos.

Um erro comum é usar o conjunto de teste repetidamente durante o desenvolvimento, como se fosse validação. Isso contamina a estimativa final: o modelo acaba indiretamente ajustado ao teste, e o número reportado deixa de refletir o desempenho real em produção.

## 4.2 Overfitting e underfitting

**Overfitting** acontece quando o modelo aprende padrões específicos demais dos dados de treino, incluindo ruído, e perde capacidade de generalizar para dados novos. O sintoma típico é desempenho muito bom no treino e desempenho ruim na validação ou no teste.

**Underfitting** acontece quando o modelo é simples demais para capturar os padrões reais dos dados, resultando em desempenho ruim tanto no treino quanto na validação.

O objetivo é encontrar um meio-termo, um modelo complexo o suficiente para capturar os padrões reais do problema, mas não tão complexo a ponto de memorizar ruído.

## 4.3 Validação cruzada

Validação cruzada (cross-validation) é uma técnica para obter uma estimativa mais robusta de desempenho, especialmente útil quando o dataset é pequeno.

Na variante mais comum, k-fold cross-validation, os dados de treino são divididos em k partes (folds). O modelo é treinado k vezes, cada vez usando k-1 folds para treino e o fold restante para validação. A métrica final é a média dos resultados nas k execuções, o que reduz a dependência de uma única divisão treino e validação ter sido "sortuda" ou "azarada".

**Nested cross-validation** é usada quando também se quer ajustar hiperparâmetros de forma robusta: um loop externo de cross-validation avalia o desempenho geral, enquanto um loop interno, dentro de cada fold externo, faz a busca de hiperparâmetros. Isso evita que a escolha de hiperparâmetros seja indiretamente ajustada ao mesmo dado usado na avaliação final, um problema sutil de vazamento de informação entre a etapa de tuning e a etapa de avaliação.

## 4.4 Matriz de confusão

Antes de falar em precisão, recall ou F1-score, vale entender a matriz de confusão, de onde essas métricas derivam. Para um problema de classificação binária, a matriz organiza as previsões em quatro categorias:

| | Previsto positivo | Previsto negativo |
|---|---|---|
| Real positivo | Verdadeiro positivo (VP) | Falso negativo (FN) |
| Real negativo | Falso positivo (FP) | Verdadeiro negativo (VN) |

**Verdadeiro positivo:** o modelo previu positivo e a classe real era positiva.

**Falso positivo:** o modelo previu positivo, mas a classe real era negativa. Também chamado de erro tipo I.

**Falso negativo:** o modelo previu negativo, mas a classe real era positiva. Também chamado de erro tipo II.

**Verdadeiro negativo:** o modelo previu negativo e a classe real era negativa.

Cada métrica de classificação é, no fundo, uma forma diferente de combinar esses quatro números, dando peso diferente ao custo de cada tipo de erro.

## 4.5 Métricas de classificação

**Acurácia:** proporção de previsões corretas sobre o total. É a métrica mais intuitiva, mas enganosa em datasets desbalanceados. Em um problema onde 95% dos casos são da classe negativa, um modelo que sempre prevê negativo atinge 95% de acurácia sem aprender nada útil.

**Precisão (precision):** entre os casos que o modelo previu como positivos, quantos realmente eram positivos. Calculada como VP / (VP + FP). Importa quando o custo de um falso positivo é alto, como marcar um e-mail legítimo como spam.

**Recall (sensibilidade):** entre os casos que realmente eram positivos, quantos o modelo conseguiu identificar. Calculado como VP / (VP + FN). Importa quando o custo de um falso negativo é alto, como deixar passar uma transação fraudulenta.

**F1-score:** média harmônica entre precisão e recall, útil quando se quer equilibrar os dois em uma única métrica, especialmente em datasets desbalanceados.

**AUC-ROC:** mede a capacidade do modelo de separar as classes em diferentes limiares de decisão, não apenas no limiar padrão de 0,5. Um valor de 1,0 indica separação perfeita, e 0,5 indica desempenho equivalente a chute aleatório.

**PR-AUC:** semelhante ao AUC-ROC, mas baseado na curva de precisão e recall em vez de taxa de verdadeiro e falso positivo. Costuma ser mais informativa que o AUC-ROC em problemas com forte desbalanceamento de classes.

## 4.6 Calibração de probabilidade

Um modelo pode ter boa capacidade de separar classes (bom AUC-ROC) sem que as probabilidades que ele produz sejam confiáveis como probabilidades reais. Um modelo bem calibrado, entre todos os casos onde ele prevê 70% de chance de churn, deveria acertar próximo de 70% das vezes.

Essa propriedade importa quando a probabilidade em si é usada para tomar decisões, como priorizar quais clientes contatar primeiro em uma campanha de retenção. Modelos como regressão logística tendem a ser bem calibrados por natureza. Modelos como Random Forest e Boosting costumam precisar de uma etapa extra de calibração (como Platt Scaling ou Isotonic Regression) se a probabilidade exata for importante para o caso de uso, não apenas o ranking relativo entre os casos.

Uma forma simples de verificar calibração é o gráfico de calibração (calibration curve), que compara a probabilidade prevista com a frequência real observada em cada faixa de probabilidade.

## 4.7 Métricas de regressão

**Erro absoluto médio (MAE):** média das diferenças absolutas entre valor previsto e valor real. Fácil de interpretar, na mesma unidade da variável prevista.

**Erro quadrático médio (MSE):** média das diferenças ao quadrado entre valor previsto e valor real. Penaliza erros grandes com mais intensidade que o MAE, por causa do quadrado.

**Raiz do erro quadrático médio (RMSE):** raiz quadrada do MSE, o que devolve a métrica para a mesma unidade da variável original, facilitando a interpretação.

**R² (coeficiente de determinação):** indica a proporção da variância da variável alvo que o modelo consegue explicar. Varia de 0 a 1 em geral, sendo 1 um ajuste perfeito, embora possa ser negativo se o modelo for pior que simplesmente prever a média.

## 4.8 Interpretabilidade de modelos

Além de medir desempenho, muitas vezes é necessário entender por que o modelo tomou determinada decisão, especialmente em domínios regulados como crédito e saúde.

**SHAP (SHapley Additive exPlanations)** e **LIME (Local Interpretable Model-agnostic Explanations)** são técnicas que estimam a contribuição de cada variável para uma previsão específica.

É importante ter clareza sobre o que essas técnicas realmente mostram: elas indicam quais variáveis mais influenciaram a previsão do modelo, mas isso não é o mesmo que provar uma relação de causa e efeito no mundo real. Uma variável pode ter alta importância no modelo por estar correlacionada com a variável alvo, sem necessariamente causá-la.

## 4.9 Métricas por grupo e generalização justa

Avaliar apenas a métrica agregada pode esconder desempenho desigual entre subgrupos da população, como diferentes faixas etárias, regiões ou perfis de cliente. Um modelo pode ter boa acurácia geral e, ainda assim, cometer muito mais falsos negativos em um subgrupo específico.

Calcular as métricas da seção 4.5 separadamente por grupo relevante ajuda a identificar esse tipo de problema antes do deploy. O tema é retomado com mais profundidade, incluindo as implicações éticas e legais, no documento [7. Ética e responsabilidade](./7-etica-e-responsabilidade.md).

## 4.10 Resumo

Avaliar um modelo vai além de calcular uma métrica única depois do treino. Envolve dividir os dados corretamente, usar validação cruzada quando necessário, entender a matriz de confusão por trás das métricas de classificação, verificar se as probabilidades produzidas são confiáveis, e checar se o desempenho se mantém consistente entre diferentes subgrupos dos dados.
