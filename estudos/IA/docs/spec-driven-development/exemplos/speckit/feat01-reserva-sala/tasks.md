# Tasks

Gerado conceitualmente por `speckit.tasks`, a partir de plan.md.

A lista de tasks é equivalente à da versão vanilla (`examples/003-room-booking-vanilla/tasks.md`, T01 a T10), com dois ajustes decorrentes de clarify.md:

```
T01. Criar entidade Booking e máquina de estados
     Ajuste: OverlapsWith usa comparação estrita nas bordas (resposta 1 de clarify.md).

T02. Testes de unidade de Booking
     Ajuste: incluir caso de teste explícito para horários adjacentes (fim de uma reserva
     igual ao início de outra), confirmando que isso NÃO é tratado como conflito.

T03. Implementar BookingRepository
T04. Implementar CreateBookingHandler
T05. Implementar ConfirmBookingHandler
T06. Implementar CancelBookingHandler
     Ajuste: cobrir explicitamente o caso de aprovador cancelando reserva "Confirmada"
     (RF06 revisado, resposta 3 de clarify.md), não apenas "Rascunho".

T07. Implementar BookingCompletionJob
     Ajuste: frequência de 5 minutos documentada como requisito confirmado, não suposição.

T08. Expor endpoints em BookingsController
T09. Implementar auditoria de transição
T10. Verificação integrada
```

Os identificadores de arquivo, dependências, critérios de aceite e comandos de validação de cada task são os mesmos descritos em `examples/003-room-booking-vanilla/tasks.md`, para evitar duplicar aqui o conteúdo completo de forma idêntica. Consulte aquele arquivo para o detalhamento de cada task; esta lista existe para registrar apenas o que muda em função das respostas de clarify.md.
