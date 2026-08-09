# 5. Feature engineering e hiperparâmetros

Além de escolher um algoritmo, o desempenho de um modelo depende muito da qualidade dos dados de entrada e da forma como o modelo é configurado.

## 5.1 O que é feature engineering

Feature engineering é o processo de criar, transformar e selecionar variáveis que serão usadas pelo modelo.

O objetivo é tornar os dados mais representativos do problema e facilitar o aprendizado. Em muitos projetos, esse processo tem impacto tão grande quanto a escolha do algoritmo.

Uma feature bem construída pode ajudar o modelo a aprender padrões mais úteis, enquanto uma feature fraca pode dificultar a performance mesmo com um algoritmo sofisticado.

## 5.2 Por que isso é importante

Em problemas reais, os dados brutos raramente chegam prontos para o treino. Eles podem conter:

- valores ausentes;
- escalas muito diferentes;
- dados categóricos sem representação numérica;
- colunas redundantes;
- sinais pouco relevantes para o problema.

A engenharia de atributos busca transformar esses dados em uma forma mais útil para o modelo.

## 5.3 Tipos de transformação

Algumas transformações comuns incluem:

- criação de novas variáveis;
- normalização e padronização;
- transformação logarítmica;
- codificação de variáveis categóricas;
- imputação de valores ausentes;
- seleção de atributos mais relevantes.

### Exemplos de transformação

- Normalizar idade e salário para uma mesma escala quando o modelo é sensível a magnitude.
- Transformar uma variável de preço com distribuição muito assimétrica usando log.
- Converter categorias como "cidade", "segmento" ou "tipo de produto" em valores numéricos para entrada do modelo.

## 5.4 Exemplos práticos

Em um problema de previsão de preço de imóveis, novas features podem incluir:

- preço por metro quadrado;
- idade do imóvel;
- tempo de residência do proprietário;
- distância até o centro da cidade;
- proximidade de escolas, hospitais ou transporte público.

Essas variáveis podem ter mais impacto do que os dados brutos originais, porque carregam informação mais útil para a tarefa.

Outro exemplo é um problema de churn. Em vez de usar apenas o número de acessos, pode-se criar features como:

- frequência média de uso;
- tempo desde o último login;
- número de interações recentes;
- crescimento ou queda no uso ao longo do tempo.

## 5.5 O que são hiperparâmetros

Hiperparâmetros são configurações definidas antes do treinamento.

Eles controlam a forma como o algoritmo aprende, mas não são aprendidos automaticamente a partir dos dados.

Exemplos:

- profundidade máxima de uma árvore;
- número de árvores em um Random Forest;
- learning rate em redes neurais;
- número de vizinhos em K-NN;
- número de épocas de treinamento.

Enquanto os parâmetros do modelo são ajustados durante o treino, os hiperparâmetros precisam ser definidos pelo cientista ou pelo engenheiro de dados.

## 5.6 Por que otimizar hiperparâmetros

Uma configuração padrão nem sempre é a melhor para um problema específico. Ajustar hiperparâmetros pode:

- melhorar a precisão;
- reduzir overfitting;
- acelerar o treinamento;
- aumentar a capacidade de generalização.

Em projetos reais, essa etapa pode fazer diferença significativa no resultado final.

## 5.7 Técnicas de otimização

### Grid Search

Testa um conjunto de combinações predefinido.

- Vantagem: simples e fácil de interpretar.
- Desvantagem: pode ser caro computacionalmente quando o espaço de busca é grande.

### Random Search

Seleciona combinações aleatórias de forma mais eficiente.

- Vantagem: costuma encontrar boas configurações com menos testes do que grid search.
- Desvantagem: pode perder configurações muito boas se a busca for muito limitada.

### Bayesian Optimization

Usa resultados anteriores para escolher novas configurações com maior chance de sucesso.

- Vantagem: é mais inteligente e geralmente mais eficiente em problemas maiores.
- Desvantagem: exige mais implementação e interpretação.

### Hyperband

Combina busca e parada antecipada para economizar tempo computacional.

- Útil quando o treinamento é caro e muitas combinações precisam ser avaliadas rapidamente.

## 5.8 Boas práticas

- Entender bem o problema antes de criar features.
- Evitar atributos redundantes ou altamente correlacionados.
- Não usar dados de teste para escolher features de forma indevida.
- Usar validação cruzada para avaliar as configurações escolhidas.
- Documentar as transformações aplicadas para garantir reprodutibilidade.
- Manter pipelines consistentes entre treino e produção.

## 5.9 Pipeline de treinamento

Em muitos projetos, a sequência fica assim:

1. Coleta e limpeza de dados
2. Engenharia de atributos
3. Divisão em treino, validação e teste
4. Treinamento do modelo
5. Ajuste de hiperparâmetros
6. Avaliação final
7. Deploy e monitoramento

Essa estrutura ajuda a garantir que as mesmas transformações sejam aplicadas de forma consistente em todos os ciclos.

## 5.10 Resumo

Feature engineering e ajuste de hiperparâmetros são parte essencial do ciclo de desenvolvimento de modelos. Eles podem fazer uma grande diferença no desempenho final, muitas vezes mais do que simplesmente trocar de algoritmo.
