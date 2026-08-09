# 2. Algoritmos de regressão e classificação

Nesta etapa, o foco está em alguns dos algoritmos mais importantes do aprendizado supervisionado, usados para prever valores numéricos ou categorizar exemplos em classes.

## 2.1 Aprendizado supervisionado

O aprendizado supervisionado usa dados com rótulos para aprender uma relação entre entrada e saída. O algoritmo recebe exemplos já classificados e tenta encontrar um padrão que permita fazer previsões sobre novos exemplos.

- Na regressão, a saída é um valor numérico.
- Na classificação, a saída é uma categoria ou rótulo.

Esse tipo de abordagem é muito comum em problemas onde existe um histórico com respostas corretas.

## 2.2 Regressão

A regressão é usada quando a variável alvo é quantitativa, ou seja, quando se quer prever números.

### Regressão linear simples

Modela a relação entre uma variável independente e uma variável dependente por meio de uma reta.

- Fórmula básica: $y = b_0 + b_1x$
- Exemplo: estimar o salário com base nos anos de experiência.

Essa abordagem é simples, interpretável e costuma funcionar bem quando a relação entre as variáveis é quase linear.

### Regressão linear múltipla

Usa mais de uma variável de entrada para prever um valor.

- Exemplo: prever preço de um imóvel com base em área, localização, número de quartos e idade do prédio.

Ela oferece mais flexibilidade do que a regressão simples, mas ainda depende de uma relação relativamente estruturada entre as variáveis.

### Regressão polinomial

Útil quando a relação entre as variáveis não é linear. Em vez de uma reta, o modelo utiliza termos de maior grau para ajustar curvas.

- Exemplo: prever crescimento populacional ou consumo energético em função do tempo.

Essa abordagem pode capturar padrões mais complexos, mas também aumenta o risco de overfitting se for exagerada.

### Regressão regularizada

Algumas variantes adicionam penalizações para controlar complexidade.

- Ridge: reduz o impacto de coeficientes muito grandes e ajuda a evitar overfitting.
- Lasso: além de regularizar, pode selecionar variáveis mais relevantes e zerar outras.

Essas técnicas são muito úteis quando há muitas variáveis correlacionadas.

## 2.3 Classificação

A classificação prevê categorias ou rótulos. Em vez de retornar um número, o modelo indica a qual classe um exemplo pertence.

### Regressão logística

Apesar do nome, é usada principalmente para problemas de classificação binária.

- Exemplo: prever se um e-mail é spam ou não spam.
- O modelo estima probabilidades e decide a classe com base em um limiar.

É simples, eficiente e amplamente utilizada como baseline.

### K-NN (K-Nearest Neighbors)

Classifica um ponto com base nos $k$ vizinhos mais próximos no espaço de atributos.

- Exemplo: classificar uma fruta como maçã ou laranja com base em peso e textura.
- Vantagem: é intuitivo e não exige um treinamento complexo.
- Limitação: pode ficar lento em bases muito grandes.

### Árvore de decisão

Divide os dados em regras simples e interpretáveis, formando uma estrutura em forma de árvore.

- Exemplo: decidir se um cliente terá ou não alta chance de churn com base em idade, renda e uso do serviço.
- Vantagem: é fácil de explicar.
- Limitação: pode overfitar se crescer demais.

### Random Forest

Combina várias árvores de decisão para melhorar estabilidade e precisão.

- Exemplo: prever se um paciente tem risco de doença com base em diferentes características clínicas.
- Vantagem: reduz o efeito de uma única árvore muito específica.
- Limitação: perde um pouco da interpretabilidade simples das árvores isoladas.

### SVM (Support Vector Machine)

Busca um hiperplano que melhor separa as classes no espaço de características.

- Funciona muito bem em problemas com alta dimensionalidade.
- Pode usar kernels para lidar com separações não lineares.
- Exemplo: classificar imagens ou distinguir padrões complexos em dados tabulares.

### Boosting

Técnicas como AdaBoost e Gradient Boosting combinam modelos fracos para formar um modelo mais forte.

- Exemplo: prever risco de crédito com alta precisão.
- Vantagem: costuma entregar excelente desempenho.
- Limitação: pode exigir mais cuidado na configuração.

## 2.4 Regressão x classificação

| Tipo | Saída esperada | Exemplo |
|---|---|---|
| Regressão | Valor numérico | Preço de um imóvel |
| Classificação | Classe ou rótulo | Spam ou não spam |

A principal diferença está na natureza da resposta que o modelo deve produzir.

## 2.5 Quando escolher cada abordagem

- Use regressão quando a resposta for uma quantidade, como preço, temperatura, demanda ou tempo.
- Use classificação quando a resposta for um rótulo, como aprovado/reprovado, fraude/não fraude, cliente/ não cliente.
- Em problemas mais complexos, modelos mais sofisticados podem ser necessários, principalmente quando há padrões não lineares.

## 2.6 Exemplo prático combinado

Imagine um cenário de previsão de vendas para uma loja.

- Se a tarefa for prever o valor das vendas de um mês, usa-se regressão.
- Se a tarefa for prever se um cliente fará uma compra ou não, usa-se classificação.

Esse tipo de decisão é fundamental no início de qualquer projeto, pois influencia diretamente a escolha do algoritmo e das métricas.

## 2.7 Resumo

Regressão e classificação são os blocos iniciais do aprendizado supervisionado. Eles oferecem uma base sólida para entender problemas mais avançados, como redes neurais, modelos de séries temporais e sistemas modernos baseados em linguagem.
