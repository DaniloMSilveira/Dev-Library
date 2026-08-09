# 4. Princípios e boas práticas de Context Engineering

Construir um bom contexto é tanto uma questão técnica quanto de design. A qualidade da resposta depende de como o contexto é estruturado, filtrado e atualizado.

## 4.1 Princípio da relevância

Enviar apenas informações relevantes para a tarefa atual costuma ser melhor do que enviar tudo.

Isso reduz ruído e melhora a eficiência do modelo.

## 4.2 Princípio da organização

Contexto bem organizado facilita a leitura e a interpretação.

É melhor separar:

- instruções;
- dados de entrada;
- documentos recuperados;
- histórico;
- estado da tarefa.

## 4.3 Princípio da clareza

Se o modelo não entender o problema, ele não conseguirá responder bem.

Por isso, é importante deixar explícito:

- o objetivo da tarefa;
- os limites do problema;
- as regras de resposta;
- o formato esperado.

## 4.4 Princípio da economia de tokens

Tokens custam tempo e dinheiro. Portanto, é recomendável evitar contextos excessivamente longos quando uma versão mais enxuta já resolve.

Boas práticas incluem:

- resumir interações antigas;
- evitar redundâncias;
- recuperar apenas trechos importantes;
- não repetir instruções longas quando elas já foram fornecidas.

## 4.5 Boas práticas de implementação

1. Defina claramente o objetivo da tarefa.
2. Separe contexto estático de contexto dinâmico.
3. Use recuperação para adicionar apenas informação relevante.
4. Monitore se o modelo está usando o contexto corretamente.
5. Ajuste o contexto com base no resultado observado.

## 4.6 Exemplo prático

Um agente de atendimento pode ser instruído a responder com tom profissional e em no máximo 5 parágrafos. Se o contexto incluir também uma descrição do histórico do cliente, o modelo consegue responder melhor e com mais precisão.

## 4.7 Resumo

Context Engineering não é apenas colocar mais texto no prompt. Trata-se de construir um contexto útil, claro, relevante e bem organizado para a tarefa em execução.
