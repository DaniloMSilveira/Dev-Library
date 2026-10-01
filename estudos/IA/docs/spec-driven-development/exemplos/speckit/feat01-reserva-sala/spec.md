# Spec: Reserva de sala com detecção de conflito

Gerado conceitualmente por `speckit.specify`. Descreve o quê e por quê; decisões técnicas de como ficam em plan.md.

## Problema

Reservas de sala são hoje combinadas por mensagem em canal interno, sem verificação automática de conflito, o que já causou duas reuniões diferentes marcadas na mesma sala no mesmo horário.

## Intenção

Permitir que usuários reservem uma sala para um intervalo de tempo, com o sistema impedindo que duas reservas confirmadas se sobreponham para a mesma sala, incluindo sobreposição parcial.

## Atores

Solicitante, aprovador (apenas para salas que exigem aprovação), e o próprio sistema, responsável por aplicar as regras de transição de estado.

## Comportamento esperado (dado/quando/então)

```
Dado que a sala "Sala A" tem aprovação automática,
Quando o solicitante cria uma reserva das 14h às 15h,
Então a reserva é criada diretamente no estado "Confirmada".

Dado que a sala "Sala B" exige aprovação,
Quando o solicitante cria uma reserva das 14h às 15h,
Então a reserva é criada no estado "Rascunho".

Dado que existe uma reserva "Confirmada" das 14h às 15h na "Sala A",
Quando qualquer usuário tenta confirmar outra reserva das 14h30 às 15h30 na mesma sala,
Então a confirmação é recusada por conflito, e a segunda reserva permanece em "Rascunho".

Dado que uma reserva "Confirmada" começa às 14h,
Quando o solicitante tenta cancelá-la às 12h30 do mesmo dia,
Então o cancelamento é recusado, por estar a menos de 2 horas do início.

Dado que uma reserva "Confirmada" terminou às 15h,
Quando o horário atual passa das 15h,
Então a reserva muda automaticamente para "Concluída", sem ação do usuário.
```

## Requisitos funcionais

Ver `requirements.md` da versão vanilla deste mesmo domínio, em `examples/003-room-booking-vanilla/requirements.md`, para a lista completa de RF01 a RF09, RNF01 a RNF03 e CA01 a CA09. Este spec.md do Spec Kit reaproveita exatamente os mesmos requisitos, já que o domínio é idêntico; o que muda entre as duas versões é o processo de chegar à implementação, não a regra de negócio em si.

## Fora de escopo

Recorrência de reservas, notificação por e-mail, integração com calendário externo, limite de reservas simultâneas por usuário.

## Decisões abertas

```
[DECISÃO ABERTA] Qual a frequência de verificação para marcar reservas como "Concluída" automaticamente?
[DECISÃO ABERTA] Sobreposição no instante exato (uma reserva termina 15h00, outra começa 15h00) conta como conflito ou não?
```

Essas duas decisões abertas são, propositalmente, as mesmas lacunas que a versão vanilla já havia resolvido com suposições registradas em design.md (5 minutos de frequência, e horários adjacentes não contam como conflito). Aqui elas ficam marcadas explicitamente para serem resolvidas na fase seguinte, `clarify`, ilustrando a diferença de fluxo entre as duas abordagens.
