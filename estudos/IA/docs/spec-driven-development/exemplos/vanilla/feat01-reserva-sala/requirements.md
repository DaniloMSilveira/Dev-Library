# Requirements: Reserva de sala com detecção de conflito

## Objetivo e motivação

Permitir que usuários reservem salas de reunião para um intervalo de tempo específico, impedindo que duas reservas confirmadas ocupem o mesmo recurso no mesmo horário. Hoje a marcação é feita por mensagem em um canal interno, sem nenhuma verificação automática, o que já gerou reuniões duplicadas na mesma sala mais de uma vez.

## Atores

**Solicitante:** usuário autenticado que cria, visualiza e cancela suas próprias reservas.

**Aprovador:** usuário com permissão para confirmar ou recusar uma reserva em rascunho, quando a sala exigir aprovação.

**Sistema:** responsável por detectar conflito de horário e aplicar as transições de estado válidas.

## Estados da reserva

Uma reserva existe sempre em um destes estados, e nenhuma transição fora da lista abaixo é permitida:

```
Rascunho -> Confirmada
Rascunho -> Cancelada
Confirmada -> Cancelada
Confirmada -> Concluída
```

Não existe transição que saia de `Cancelada` ou de `Concluída`. Esses dois são estados finais.

## Fluxos principais

**Criar reserva (rascunho):** o solicitante escolhe sala, data, horário de início e fim. O sistema verifica conflito com reservas já `Confirmada` para a mesma sala e cria a reserva no estado `Rascunho` se não houver conflito bloqueante (ver RF03).

**Confirmar reserva:** depende de a sala exigir aprovação ou não (ver RF02). Quando confirmada, a reserva passa de `Rascunho` para `Confirmada`, e esse é o momento em que ela passa a bloquear outras reservas para o mesmo horário.

**Cancelar reserva:** o solicitante cancela uma reserva própria em `Rascunho` ou `Confirmada`. O sistema aplica a regra de prazo mínimo de cancelamento (RF07) apenas para reservas `Confirmada`.

**Concluir reserva:** o sistema marca automaticamente uma reserva `Confirmada` como `Concluída` após o horário de término ter passado, sem ação do usuário.

## Requisitos funcionais

```
RF01. O solicitante deve poder criar uma reserva informando sala, data, horário de início e horário de término.
RF02. Uma sala pode ser configurada como "requer aprovação" ou "aprovação automática". Para salas de aprovação automática, a reserva é criada diretamente em "Confirmada", sem passar por "Rascunho".
RF03. O sistema deve impedir a confirmação de uma reserva quando houver qualquer sobreposição de horário, mesmo parcial, com outra reserva já "Confirmada" para a mesma sala.
RF04. Duas reservas em "Rascunho" para a mesma sala e mesmo horário podem coexistir, pois ainda não bloqueiam o recurso.
RF05. Ao confirmar uma reserva em "Rascunho", se o horário já tiver sido ocupado por outra reserva confirmada nesse meio tempo, o sistema deve recusar a confirmação e informar o conflito, em vez de confirmar silenciosamente.
RF06. O aprovador deve poder confirmar ou cancelar uma reserva em "Rascunho" de uma sala que exige aprovação.
RF07. O solicitante não pode cancelar uma reserva "Confirmada" com menos de 2 horas de antecedência do horário de início.
RF08. O sistema deve marcar automaticamente como "Concluída" toda reserva "Confirmada" cujo horário de término já tenha passado.
RF09. O solicitante só pode cancelar as próprias reservas; o aprovador pode cancelar qualquer reserva da sala sob sua aprovação.
```

## Requisitos não funcionais

```
RNF01. A verificação de conflito de horário deve considerar apenas reservas no estado "Confirmada"; reservas em "Rascunho", "Cancelada" ou "Concluída" nunca bloqueiam uma nova reserva.
RNF02. A operação de confirmar uma reserva deve ser seguranca contra condição de corrida: duas confirmações simultâneas para horários conflitantes não podem resultar em duas reservas "Confirmada" sobrepostas.
RNF03. O histórico de mudança de estado de uma reserva deve ser auditável (quem mudou, de qual estado para qual estado, e quando).
```

## Critérios de aceitação

```
CA01. Criar uma reserva para uma sala de aprovação automática resulta em estado "Confirmada" imediatamente.
CA02. Criar uma reserva para uma sala que exige aprovação resulta em estado "Rascunho".
CA03. Tentar confirmar uma reserva cujo horário sobrepõe, mesmo parcialmente, uma reserva já "Confirmada" da mesma sala, resulta em erro de conflito, e a reserva permanece em "Rascunho".
CA04. Duas reservas em "Rascunho" para a mesma sala e horário podem ser criadas sem erro.
CA05. Cancelar uma reserva "Confirmada" com menos de 2 horas de antecedência é bloqueado com uma mensagem informando o prazo mínimo.
CA06. Cancelar a mesma reserva com mais de 2 horas de antecedência é permitido e muda o estado para "Cancelada".
CA07. Uma reserva "Confirmada" cujo horário de término já passou aparece como "Concluída" sem exigir nenhuma ação do usuário.
CA08. Um solicitante não consegue cancelar uma reserva de outro solicitante.
CA09. Duas tentativas de confirmação simultâneas para horários conflitantes resultam em exatamente uma reserva confirmada e uma recusada por conflito, nunca duas confirmadas.
```

## Casos de erro e limites

- tentar transição de estado fora da lista definida (ex.: de "Cancelada" para "Confirmada") deve ser rejeitada com erro explícito, não ignorada silenciosamente;
- horário de término anterior ou igual ao horário de início deve ser rejeitado na criação da reserva;
- reserva para uma sala inexistente ou inativa deve ser rejeitada antes de qualquer verificação de conflito;
- duas reservas idênticas (mesma sala, mesmo horário, mesmo solicitante) enviadas em sequência rápida não devem gerar duas reservas em rascunho idênticas sem que o usuário perceba.

## Fora de escopo

- recorrência de reservas (reservar a mesma sala toda semana);
- notificação por e-mail ou push de confirmação e lembrete, tratada como melhoria futura;
- integração com calendário externo (Google Calendar, Outlook);
- política de limite de reservas simultâneas por usuário.
