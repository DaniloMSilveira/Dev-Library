# 1. Conceitos fundamentais de Context Engineering

Context Engineering é a prática de organizar, priorizar e entregar o contexto certo ao modelo de IA para que ele responda com mais precisão, relevância e consistência.

## 1.1 O que é contexto?

No contexto de sistemas com IA, contexto é o conjunto de informações que o modelo recebe antes de gerar uma resposta. Isso pode incluir:

- instruções do sistema;
- histórico da conversa;
- documentos relevantes;
- dados do usuário;
- estado da tarefa;
- restrições de negócio.

O objetivo não é enviar o máximo de informação possível, mas sim enviar a informação mais útil para a tarefa atual.

## 1.2 Por que isso importa?

Um modelo de linguagem pode responder de forma ruim se o contexto estiver:

- incompleto;
- desorganizado;
- irrelevante;
- excessivamente longo;
- contraditório.

Em sistemas reais, a qualidade da resposta depende muito da qualidade do contexto fornecido ao modelo.

## 1.3 Diferença entre prompt e contexto

Embora os dois termos estejam relacionados, eles não são exatamente iguais.

- Prompt é a instrução ou solicitação feita ao modelo.
- Contexto é o conjunto de informações que dá suporte à resposta.

Exemplo:

- Prompt: "Explique o processo de aprovação de crédito."
- Contexto: políticas internas, regras de negócio, exemplos anteriores e histórico da conversa.

## 1.4 Elementos comuns de contexto

Um bom contexto costuma incluir alguns destes blocos:

1. Instruções
   - Definem como o modelo deve agir.

2. Histórico
   - Mantém a continuidade da conversa.

3. Memória
   - Guarda informações importantes para interações futuras.

4. Documentos recuperados
   - São trazidos por técnicas como RAG.

5. Estado da tarefa
   - Informa o que já foi feito e o que falta.

## 1.5 Exemplo prático

Imagine um assistente que responde perguntas sobre políticas internas de uma empresa.

Se o contexto incluir apenas uma instrução genérica, a resposta poderá ser vaga. Mas se o contexto incluir:

- a pergunta do usuário;
- os documentos relevantes;
- a política específica do setor;
- os dados recentes da conversa;

então a resposta tende a ser muito mais útil.

## 1.6 Resumo

Context Engineering é a camada que transforma informações dispersas em um contexto estruturado e útil para o modelo. Sua função é melhorar a qualidade, a precisão e a consistência das respostas.
