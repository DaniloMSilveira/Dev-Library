# Analyze

Gerado conceitualmente por `speckit.analyze`, antes de `speckit.implement`. Confronta spec.md, plan.md e tasks.md em busca de inconsistência, usando a mesma lógica da matriz de rastreabilidade descrita na trilha de spec-driven-development, documento 2.

## Checagem de rastreabilidade

```
RF01 -> CA01, CA02 -> T04                         OK
RF02 -> CA01, CA02 -> T04                         OK
RF03 -> CA03, CA09 -> T01, T05                    OK
RF04 -> CA04 -> T01                               OK
RF05 -> CA03 -> T05                               OK
RF06 (revisado) -> nenhum CA dedicado -> T06      ATENÇÃO
RF07 -> CA05, CA06 -> T06                         OK
RF08 -> CA07 -> T07                               OK
RF09 -> CA08 -> T06                               OK
RNF01 -> (não observável por CA direto) -> T03    ATENÇÃO
RNF02 -> CA09 -> T05                              OK
RNF03 -> (não observável por CA direto) -> T09    ATENÇÃO
```

## Divergências encontradas

**RF06 sem critério de aceite dedicado:** depois da revisão em clarify.md, RF06 passou a cobrir também o cancelamento de reserva "Confirmada" pelo aprovador, mas nenhum CA em spec.md verifica esse caso especificamente, apenas CA08, que testa a permissão do solicitante, não a do aprovador. Ação: adicionar um CA10 cobrindo aprovador cancelando reserva "Confirmada" de outro usuário, antes de prosseguir para implementação.

**RNF01 e RNF03 sem critério de aceite observável pelo usuário final:** ambos são requisitos não funcionais verificáveis apenas por inspeção técnica (consulta ao banco, revisão de query), não por um comportamento visível na interface. Isso não é um erro, é esperado para requisitos não funcionais, mas fica registrado aqui para que a task de verificação integrada (T10) inclua explicitamente a checagem manual desses dois pontos, já que nenhum CA vai cobri-los automaticamente.

## Conflito com a constituição

Nenhum conflito encontrado com P01 a P05.

## Conclusão

Uma divergência real (RF06 sem CA) e duas observações de cobertura (RNF01, RNF03). Antes de `speckit.implement`, adicionar CA10 a spec.md e atualizar tasks.md (T06) referenciando o novo critério.

Este é o tipo de inconsistência que, no fluxo vanilla, dependeria de quem está escrevendo requirements.md e tasks.md perceber manualmente ao preencher a matriz de rastreabilidade do documento 2 da trilha de SDD. Aqui, a fase `analyze` formaliza essa checagem como uma etapa própria do fluxo, o que é a principal diferença prática entre as duas abordagens neste exemplo: não é que o fluxo vanilla não pudesse pegar o mesmo erro, é que ele depende de disciplina manual para isso, enquanto o Spec Kit reserva uma fase dedicada à checagem.
