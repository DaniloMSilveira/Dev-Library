# 5. Exemplo com Angular: Quote Card

Este laboratório adapta o exemplo de uma aplicação Angular pequena que exibe uma citação de uma API externa. O objetivo não é construir uma aplicação completa, mas demonstrar como requirements, design e tasks reduzem decisões implícitas antes do código.

## 5.1 O que será construído

A feature terá três responsabilidades:

- `QuoteService`: realiza a chamada HTTP e converte o DTO externo para um modelo interno;
- `QuoteContainerComponent`: coordena carregamento, sucesso, erro e retry;
- `QuoteCardComponent`: apresenta a citação e emite a ação de refresh.

A implementação pode consultar os artefatos do exemplo em [`examples/spec-driven-development/001-quote-card`](../../examples/spec-driven-development/001-quote-card/).

## 5.2 Requisitos e critérios

A funcionalidade precisa:

- buscar uma citação ao abrir a tela;
- exibir texto e autor;
- mostrar loading durante a chamada;
- permitir nova tentativa por um botão claro;
- exibir erro compreensível;
- manter estados visíveis e acessíveis;
- possuir testes para service e componente de orquestração;
- evitar novas bibliotecas e alterações fora do escopo.

Exemplos de critérios testáveis:

- ao iniciar, loading aparece antes do resultado;
- após sucesso, texto e autor são exibidos;
- ao clicar em refresh, uma nova chamada é feita;
- em erro, a mensagem aparece e o retry continua disponível;
- o botão fica desabilitado durante loading, se essa for a decisão aprovada no design.

## 5.3 Design

A separação smart/dumb é uma decisão de fronteira, não uma regra universal:

```text
src/app/quote/
├── data/
│   ├── quote.model.ts
│   └── quote.service.ts
├── feature/
│   └── quote-container.component.ts
└── ui/
    └── quote-card.component.ts
```

O componente de apresentação recebe dados e emite eventos. O container injeta o service, controla o estado e decide quando buscar novamente. A camada de dados conhece o contrato externo e protege o restante da aplicação contra mudanças no DTO.

Decisões possíveis do design:

- componentes standalone;
- `OnPush` no componente de apresentação;
- `input()` e `output()` para comunicação explícita;
- Signals para estado local;
- RxJS para a chamada HTTP;
- testes unitários para service e container;
- proxy de desenvolvimento para lidar com CORS, quando necessário.

Essas decisões devem ser confirmadas pela versão Angular e pelas convenções do projeto. O exemplo não autoriza copiar a arquitetura sem revisar o contexto.

## 5.4 Tasks

1. Criar o modelo interno `Quote`.
2. Implementar `QuoteService` e mapear o DTO da API.
3. Criar `QuoteCardComponent` com estados de loading e erro.
4. Criar `QuoteContainerComponent` e orquestrar o fluxo.
5. Escrever testes do service com mock HTTP.
6. Escrever testes do container para sucesso, erro e retry.
7. Executar build, testes e revisão visual/acessível.

Cada task deve ser executada isoladamente, validada e marcada antes da próxima. A task 7 é uma verificação integrada, não um detalhe opcional.

## 5.5 Prompt inicial para um agente

```text
Leia os arquivos:
- examples/requirements.md
- examples/design.md
- examples/tasks.md

Antes de alterar qualquer arquivo:
1. resuma os requisitos e critérios de aceite;
2. liste ambiguidades e proponha defaults explícitos;
3. confira se os caminhos citados existem;
4. apresente um plano seguindo a ordem das tasks;
5. informe os comandos de build, teste e lint.

Não implemente ainda e não adicione funcionalidades fora da spec.
```

Após a revisão humana do plano, o agente pode receber uma task por vez:

```text
Implemente somente a task T01.
Faça a menor mudança possível.
Não execute T02 ou tarefas posteriores.
Ao final, liste arquivos alterados e comandos de validação.
```

## 5.6 Limitações do laboratório

- a API externa pode mudar ou ficar indisponível;
- CORS e autenticação dependem do serviço escolhido;
- o exemplo não define persistência;
- requisitos visuais precisam de protótipo e validação reais;
- não há garantia de que uma versão futura do Angular aceite exatamente as mesmas APIs;
- conteúdo de terceiros deve ser usado respeitando as políticas e limites do serviço.
