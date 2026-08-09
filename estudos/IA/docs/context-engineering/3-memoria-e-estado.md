# 3. Memória, estado e manutenção de contexto

Em sistemas com IA, nem todo contexto precisa ser reprocessado a cada interação. Parte dele pode ser guardada para melhorar a continuidade e a personalização.

## 3.1 O que é memória em IA?

Memória é a capacidade de guardar informações relevantes para uso futuro.

Ela pode ser:

- curta: usada durante uma conversa atual;
- longa: persistida entre interações;
- semântica: baseada em conhecimento e fatos relevantes;
- episódica: ligada a eventos específicos.

## 3.2 Por que a memória é importante?

Sem memória, o sistema tende a tratar cada interação como se fosse isolada. Isso pode causar:

- repetição de perguntas;
- perda de informação importante;
- respostas menos personalizadas.

Com memória bem construída, o sistema consegue manter uma visão mais consistente da tarefa.

## 3.3 Estado da tarefa

Estado é a representação do que já aconteceu e do que ainda precisa acontecer em uma execução.

Exemplo:

- um agente que está preenchendo uma planilha;
- um fluxo de aprovação;
- um processo de análise de incidentes.

O estado permite que o sistema saiba onde está e qual próximo passo deve tomar.

## 3.4 Diferença entre memória e estado

Embora estejam relacionados, eles não são exatamente os mesmos.

- Memória guarda conhecimento ou histórico útil.
- Estado descreve a situação atual da execução.

Exemplo:

- memória: "o usuário prefere respostas curtas";
- estado: "a tarefa de revisão ainda está em andamento".

## 3.5 Boas práticas de memória

- armazenar apenas informações realmente úteis;
- evitar excesso de dados irrelevantes;
- respeitar privacidade e segurança;
- atualizar a memória quando o contexto mudar.

## 3.6 Exemplo prático

Um assistente de suporte pode lembrar que o usuário está em uma campanha de migração de sistema. Com isso, ele pode adaptar a resposta e evitar repetir informações básicas já fornecidas.

## 3.7 Resumo

Memória e estado ajudam a manter coerência, continuidade e contexto de longo prazo. Eles são fundamentais para construir sistemas mais inteligentes e mais úteis.
