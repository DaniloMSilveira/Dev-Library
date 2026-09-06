# 3. Fluxo operacional e checkpoints

O valor do SDD aparece no processo de revisão e implementação, não apenas na existência dos arquivos. O fluxo abaixo combina a coleta de contexto, a construção da spec, o planejamento, a execução incremental e a atualização contínua dos artefatos.

## 3.1 Fase 0: coletar contexto

Antes de escrever a spec, responda perguntas direcionadas:

1. O que precisa ser corrigido ou implementado?
2. Por que isso importa e qual é o impacto de não fazer?
3. Quais arquivos, módulos ou interfaces já foram identificados?
4. Quais decisões, restrições ou tecnologias já estão definidas?
5. O que está explicitamente fora do escopo?
6. Quais evidências existem: bug, requisito, protótipo, log ou teste?

A coleta deve consultar o repositório real. Uma especificação genérica que inventa nomes de arquivos, funções ou interfaces cria um contexto enganoso para a IA.

## 3.2 Fase 1: gerar e revisar a spec

O documento deve explicar o estado atual, a intenção e o resultado esperado. Antes de apresentá-lo para implementação, faça uma auto-revisão:

- os arquivos citados existem ou foram marcados como novos;
- os critérios são objetivos;
- o escopo está limitado a um problema;
- os snippets são compatíveis com a stack;
- erros, casos limite, segurança e operação foram considerados;
- as decisões abertas estão identificadas.

O checkpoint desta fase é a aprovação da spec. Sem essa aprovação, a IA pode ajudar a fazer perguntas e apontar lacunas, mas não deveria iniciar uma implementação ampla.

## 3.3 Fase 2: esclarecer ambiguidades

Uma etapa explícita de esclarecimento evita que o agente escolha defaults importantes sem autorização. Pergunte, por exemplo:

- o estado de erro permite retry?
- o campo é obrigatório ou opcional?
- o comportamento precisa ser compatível com versões anteriores?
- a autenticação ocorre neste componente ou em uma camada existente?
- o que acontece quando o serviço externo está indisponível?

Registre a decisão na spec quando ela alterar o comportamento. Não esconda uma escolha importante apenas dentro do prompt.

## 3.4 Fase 3: gerar o plano

O plano conecta os requisitos à arquitetura e às tarefas. Ele deve mostrar:

- componentes e responsabilidades;
- contratos e fluxo de dados;
- dependências;
- estratégia de testes;
- comandos de validação;
- riscos e alternativas;
- tarefas que podem ser executadas em paralelo.

O plano deve ser revisado antes de ser convertido em tasks. Um plano detalhado para a solução errada apenas acelera o erro.

## 3.5 Fase 4: gerar e executar tasks

Quebre o trabalho em passos pequenos. Uma sequência possível é:

1. criar ou ajustar o modelo de dados;
2. implementar a integração ou service;
3. implementar o componente de apresentação;
4. implementar o componente de orquestração;
5. adicionar testes unitários;
6. executar a verificação integrada.

Cada task deve alterar o mínimo necessário. Após cada etapa, execute o teste mais próximo do comportamento alterado e revise o diff antes de continuar.

## 3.6 Fase 5: analisar e implementar

Antes de implementar tudo, analise a consistência entre requisitos, design e tasks. Procure:

- requisito sem task;
- task sem requisito;
- dependência circular;
- conflito de contrato;
- regra da constituição violada;
- teste ausente para critério de aceite.

Somente então implemente seguindo a ordem das tasks. O agente deve relatar arquivos alterados e comandos de validação, e não expandir o escopo silenciosamente.

## 3.7 Fase 6: corrigir divergências

Quando algo falhar, classifique a divergência:

| Situação | Ação principal |
|---|---|
| Código não atende à spec aprovada | Corrigir código e testes; manter a spec |
| Spec está incompleta ou incorreta | Alterar a spec e regenerar design/tasks afetados |
| Ambiente ou ferramenta impediu a validação | Registrar a limitação e criar uma verificação alternativa |
| Requisito novo apareceu | Criar ou atualizar uma spec com escopo explícito |

Não corrija uma divergência apenas com prompt solto. Preserve a evidência, atualize o artefato responsável e repita os checkpoints necessários.

## 3.8 Fase 7: manter a spec ancorada

Depois do merge ou deploy:

- mantenha a spec próxima da feature;
- atualize a documentação quando o comportamento mudar;
- crie testes de regressão para bugs corrigidos;
- registre decisões aprendidas na constituição ou no design;
- revise segurança e operação quando a arquitetura evoluir.

Uma feature nova deve ter uma nova spec ou uma alteração explícita na spec existente. Isso evita que mudanças importantes desapareçam em uma sequência de prompts.
