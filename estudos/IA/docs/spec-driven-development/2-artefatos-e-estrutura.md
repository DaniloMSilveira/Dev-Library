# 2. Artefatos e estrutura de uma feature

Uma feature orientada por especificação precisa separar intenção, decisões técnicas e execução. Essa separação evita que um único documento misture requisitos com detalhes de implementação e permite revisar cada tipo de decisão no momento adequado.

## 2.1 Estrutura recomendada

Uma estrutura simples para uma feature pode ser:

```text
specs/
└── 001-quote-card/
    ├── requirements.md
    ├── design.md
    └── tasks.md
```

Em projetos que usam uma especificação mais ampla para uma correção, uma alternativa é:

```text
docs/
└── recuperar-acesso/
    ├── SDD.md
    └── tasks/
        ├── TASK-1-validar-token.md
        ├── TASK-2-atualizar-servico.md
        └── TASK-3-verificacao-e2e.md
```

As duas estruturas são compatíveis. A primeira separa os artefatos principais da feature; a segunda detalha contexto, impacto e tarefas em documentos independentes.

## 2.2 Requirements: o que e por quê

O arquivo de requisitos deve explicar o problema sem prender a solução a uma biblioteca específica.

Inclua:

- objetivo e motivação;
- atores e fluxos principais;
- requisitos funcionais;
- requisitos não funcionais;
- critérios de aceitação;
- casos de erro e limites;
- o que não faz parte do escopo.

Exemplo de requisito funcional:

```markdown
RF01. Ao abrir a tela, a aplicação deve solicitar uma citação.
RF02. O usuário deve poder solicitar outra citação.
RF03. Enquanto a solicitação estiver em andamento, o estado de loading deve ser visível.
RF04. Em caso de erro, a interface deve mostrar uma mensagem e permitir nova tentativa.
```

Um requisito como "a interface deve ser moderna" é uma intenção vaga. Transforme-o em critérios observáveis de design, acessibilidade e comportamento, quando esses aspectos forem realmente necessários.

## 2.3 Design: como

O design traduz requisitos em decisões técnicas. Deve explicar somente o necessário para que a implementação seja consistente:

- estrutura de pastas;
- responsabilidades de módulos e componentes;
- contratos de dados;
- gerenciamento de estado;
- dependências e integrações;
- estratégia de testes;
- decisões de segurança e operação;
- alternativas descartadas, quando relevantes.

Não transforme o design em uma reprodução de cada linha do código. Ele deve preservar a intenção arquitetural e as fronteiras que não podem ser quebradas.

## 2.4 Tasks: ordem e verificação

Tasks são unidades pequenas de trabalho, com dependências e critérios verificáveis.

Uma task útil registra:

- identificador e descrição;
- arquivo ou área afetada;
- dependências;
- contexto;
- o que fazer;
- notas de implementação;
- critério de aceite;
- comando ou evidência de validação.

A task final deve ser dedicada à verificação integrada quando a feature exigir mais de um componente. Isso evita terminar após a implementação sem testar o fluxo completo.

## 2.5 Constitution: regras estáveis do projeto

Uma constituição registra princípios que valem para várias features. Exemplos:

- componentes de apresentação não fazem chamadas HTTP;
- funcionalidades com lógica de dados exigem testes;
- mudanças de comportamento atualizam a spec correspondente;
- mensagens de erro devem ser claras e acessíveis;
- alterações devem ser pequenas e rastreáveis;
- segredos não podem aparecer em specs, prompts ou logs.

A constituição não deve repetir cada requisito de cada feature. Ela contém regras duradouras do repositório.

## 2.6 SDD.md para correções

Para corrigir uma funcionalidade existente, um `SDD.md` pode usar sete seções:

1. **Contexto e problema:** estado atual e risco.
2. **Escopo da correção:** o que muda e o que não muda.
3. **Design da solução:** módulos, interfaces e snippets necessários.
4. **Fluxo após a correção:** sequência de dados ou usuário.
5. **Arquivos a modificar ou criar:** impacto concreto.
6. **Critérios de aceite:** afirmações verificáveis.
7. **Considerações adicionais:** segurança, performance e débito técnico.

A seção "o que não muda" é particularmente importante quando um agente participa da implementação. Ela funciona como um limite explícito contra refatorações e funcionalidades não solicitadas.

## 2.7 Qualidade dos artefatos

Antes de aprovar os documentos, confira:

- arquivos citados existem ou estão marcados como novos;
- snippets correspondem às versões usadas no projeto;
- cada critério pode ser marcado como verdadeiro ou falso;
- dependências entre tasks estão explícitas;
- escopo e fora de escopo não se contradizem;
- riscos relevantes têm uma forma de validação;
- a linguagem deixa claro o que é fato, decisão e hipótese.
