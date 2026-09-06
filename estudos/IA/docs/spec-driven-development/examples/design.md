# 001 - Quote Card: design

## Estrutura

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

## Responsabilidades

### QuoteService

- Realizar a chamada HTTP para o provedor de citações.
- Converter o DTO externo para o modelo interno `Quote`.
- Propagar erros para o componente de orquestração.

### QuoteContainerComponent

- Injetar `QuoteService`.
- Controlar estados de loading, sucesso e erro.
- Buscar a citação inicial.
- Reagir ao evento de refresh.
- Não expor o DTO externo diretamente à UI.

### QuoteCardComponent

- Receber texto, autor, loading e mensagem de erro.
- Renderizar os estados recebidos.
- Emitir refresh.
- Não fazer HTTP nem injetar services.

## Decisões técnicas

- Consumir `GET /api/quotes/random`, conforme o contrato ilustrativo dos requisitos.
- Mapear o DTO `{ quote, author }` para o modelo interno `{ text, author }`.
- Tratar resposta inválida, falha de rede e status HTTP fora de `2xx` como erro do fluxo.

- Usar componentes standalone, conforme a versão Angular adotada pelo projeto.
- Preferir Signals para estado local e RxJS para chamadas HTTP.
- Usar `OnPush` no componente de apresentação quando compatível com a estratégia do projeto.
- Usar mock HTTP nos testes do service.
- Testar loading, sucesso, erro e retry no container.

## Limites

Este design não define persistência, autenticação, cache ou uma biblioteca visual. Essas decisões exigiriam requisitos próprios.
