# 001 - Quote Card: requirements

## Objetivo

Exibir uma citação aleatória, com texto e autor, e permitir que a pessoa solicite outra citação.

## Requisitos funcionais

- RF01. Ao abrir a tela, a aplicação deve buscar uma citação.
- RF02. A tela deve exibir o texto e o autor da citação recebida.
- RF03. Deve existir uma ação clara para buscar outra citação.
- RF04. Durante a busca, a tela deve exibir um estado de loading.
- RF05. Em caso de erro, a tela deve exibir uma mensagem clara e permitir retry.

## Requisitos não funcionais

- RNF01. A feature deve ter testes automatizados para service e container.
- RNF02. Estados de loading e erro devem ser visíveis e compreensíveis.
- RNF03. O componente de apresentação não deve conhecer o service HTTP.
- RNF04. A solução deve evitar dependências novas sem justificativa.

## Contrato ilustrativo da API

O exemplo usa um contrato local e fictício para tornar a implementação reproduzível. A base URL deve ser configurada pelo projeto; o caminho é `GET /api/quotes/random`.

Resposta de sucesso (`200`):

```json
{
	"quote": "Uma frase de exemplo.",
	"author": "Autora de exemplo"
}
```

O service deve mapear `quote` para `text` no modelo interno `Quote`. Respostas sem `quote` ou `author` válidos devem ser tratadas como erro. Falhas de rede e respostas HTTP fora de `2xx` devem chegar ao container para exibição e retry.

## Critérios de aceite

- CA01. Ao iniciar, loading é exibido antes do resultado.
- CA02. Após sucesso, texto e autor aparecem.
- CA03. Ao acionar refresh, uma nova busca é iniciada.
- CA04. Em erro, a mensagem aparece e refresh continua disponível.
- CA05. O comportamento do service e do container possui testes.

## Fora do escopo

- Persistência de citações.
- Login e personalização.
- Design system completo.
- Cache ou modo offline.
