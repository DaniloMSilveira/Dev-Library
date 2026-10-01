# Plan

Gerado conceitualmente por `speckit.plan`, a partir de spec.md já refinado por clarify.md.

## Arquitetura

Idêntica à decisão técnica da versão vanilla, já que a mudança de processo entre as duas abordagens não implica mudança de arquitetura para este domínio:

```
backend/
├── Domain/
│   ├── Booking.cs
│   ├── BookingStatus.cs
│   └── BookingConflictException.cs
├── Application/
│   ├── CreateBookingHandler.cs
│   ├── ConfirmBookingHandler.cs
│   └── CancelBookingHandler.cs
├── Infrastructure/
│   ├── BookingRepository.cs
│   └── BookingCompletionJob.cs
└── Api/
    └── BookingsController.cs
```

## Decisões técnicas

**Máquina de estados:** tabela de transições válidas dentro da entidade `Booking`, igual ao design vanilla. Ver `examples/003-room-booking-vanilla/design.md`, seção "Modelagem da máquina de estados", para o código de referência; a decisão técnica não muda entre as duas versões.

**Detecção de sobreposição:** `OverlapsWith` usando comparação estrita (`<`, não `<=`) nas duas bordas, conforme resposta 1 de clarify.md. Esta é a única diferença de código em relação à versão vanilla original, que já havia chegado à mesma conclusão, mas sem o registro formal de pergunta e resposta.

**Concorrência (P04 da constituição):** transação serializável no banco para `ConfirmBookingHandler`, pelo mesmo motivo descrito na versão vanilla: a garantia de RNF02 precisa valer entre múltiplas instâncias do backend, não apenas em memória de um processo.

**Job de conclusão automática:** frequência de 5 minutos, agora como requisito confirmado (resposta 2 de clarify.md), não mais como suposição a ser validada.

**Permissão de cancelamento:** verificada no handler antes de qualquer transição de estado, incluindo o caso de aprovador cancelando reserva já "Confirmada" (RF06 revisado, resposta 3 de clarify.md).

## Estratégia de testes

Igual à versão vanilla: testes de unidade em `Booking` para transições e sobreposição, teste de integração com concorrência real para `ConfirmBookingHandler`, testes de unidade para `CancelBookingHandler` cobrindo prazo e permissão separadamente, teste do job de conclusão.

## Risco e alternativa considerada

Mesmo risco identificado na versão vanilla sobre lock otimista versus transação serializável para RNF02. Decisão mantida: transação serializável para a primeira versão, por simplicidade de raciocínio sobre um caso de uso pontual e de baixo volume.

## Checagem contra a constituição

```
P01 (testes antes de merge): plano inclui testes para cada handler e para a entidade.
P02 (regra de negócio no domínio): transições e sobreposição ficam em Booking.cs, não em controllers.
P03 (spec atualizada): spec.md já reflete as decisões de clarify.md antes deste plano ser escrito.
P04 (concorrência explícita): seção "Concorrência" acima cobre isso diretamente.
P05 (sem segredo em spec): não aplicável a este domínio, nenhum segredo envolvido.
```
