# 001 - Quote Card: tasks

## T01 - Criar modelo Quote

- Arquivo: `src/app/quote/data/quote.model.ts`
- Depende de: nenhuma.
- Critério: modelo interno contém texto e autor.

## T02 - Implementar QuoteService

- Arquivo: `src/app/quote/data/quote.service.ts`
- Depende de: T01.
- Critério: service chama `GET /api/quotes/random`, valida o DTO `{ quote, author }` e o mapeia para `Quote`.
- Validação: teste HTTP com resposta de sucesso e erro.

## T03 - Criar QuoteCardComponent

- Arquivo: `src/app/quote/ui/quote-card.component.*`
- Depende de: T01.
- Critério: componente renderiza sucesso, loading e erro e emite refresh.

## T04 - Criar QuoteContainerComponent

- Arquivo: `src/app/quote/feature/quote-container.component.*`
- Depende de: T02 e T03.
- Critério: container busca ao iniciar e ao receber refresh, controlando os estados.

## T05 - Testar QuoteService

- Arquivo: teste do service.
- Depende de: T02.
- Critério: sucesso mapeia dados e erro é propagado.

## T06 - Testar QuoteContainerComponent

- Arquivo: teste do container.
- Depende de: T04.
- Critério: loading, sucesso, erro e retry são verificados.

## T07 - Verificação integrada

- Depende de: T05 e T06.
- Executar build, testes e lint.
- Revisar acessibilidade dos estados e do botão.
- Conferir que nenhuma funcionalidade fora do escopo foi adicionada.
