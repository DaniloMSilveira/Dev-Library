# Design: Reserva de sala com detecção de conflito

## Estrutura de pastas

```
backend/
├── Domain/
│   ├── Booking.cs
│   ├── BookingStatus.cs
│   ├── Room.cs
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

## Modelagem da máquina de estados

O enum `BookingStatus` e a validação de transição vivem dentro da entidade `Booking`, não espalhados pelos handlers. Isso garante que uma transição inválida seja impossível de representar, independente de qual handler ou rota chamou o método.

```csharp
public enum BookingStatus
{
    Draft,
    Confirmed,
    Cancelled,
    Completed
}
```

```csharp
public class Booking
{
    private static readonly Dictionary<BookingStatus, BookingStatus[]> ValidTransitions = new()
    {
        [BookingStatus.Draft] = new[] { BookingStatus.Confirmed, BookingStatus.Cancelled },
        [BookingStatus.Confirmed] = new[] { BookingStatus.Cancelled, BookingStatus.Completed },
        [BookingStatus.Cancelled] = Array.Empty<BookingStatus>(),
        [BookingStatus.Completed] = Array.Empty<BookingStatus>()
    };

    public Guid Id { get; private set; }
    public Guid RoomId { get; private set; }
    public Guid RequesterId { get; private set; }
    public DateTime StartsAt { get; private set; }
    public DateTime EndsAt { get; private set; }
    public BookingStatus Status { get; private set; }

    public bool OverlapsWith(DateTime start, DateTime end)
        => StartsAt < end && start < EndsAt;

    public void TransitionTo(BookingStatus newStatus)
    {
        if (!ValidTransitions[Status].Contains(newStatus))
        {
            throw new InvalidBookingTransitionException(Status, newStatus);
        }

        Status = newStatus;
    }
}
```

O dicionário `ValidTransitions` é a representação direta da máquina de estados definida em requirements.md. Qualquer transição nova no negócio exige alterar essa tabela, nunca adicionar um `if` solto em algum handler.

A condição em `OverlapsWith` (`StartsAt < end && start < EndsAt`) é a forma padrão de detectar sobreposição de dois intervalos de tempo, incluindo sobreposição parcial, conforme RF03. Vale comentar essa linha no código real, porque a lógica de sobreposição de intervalos é um erro comum de se acertar de primeira.

## Verificação de conflito e concorrência

A verificação de conflito (RF03, RF05) só considera reservas `Confirmed` (RNF01):

```csharp
public class ConfirmBookingHandler
{
    private readonly BookingRepository _repository;

    public ConfirmBookingHandler(BookingRepository repository)
    {
        _repository = repository;
    }

    public async Task ConfirmAsync(Guid bookingId)
    {
        using var transaction = await _repository.BeginSerializableTransactionAsync();

        var booking = await _repository.GetByIdAsync(bookingId)
            ?? throw new BookingNotFoundException(bookingId);

        var conflicting = await _repository.FindConfirmedOverlapsAsync(
            booking.RoomId, booking.StartsAt, booking.EndsAt, excludingBookingId: booking.Id);

        if (conflicting.Any())
        {
            throw new BookingConflictException(booking.Id, conflicting.First().Id);
        }

        booking.TransitionTo(BookingStatus.Confirmed);
        await _repository.SaveAsync(booking);
        await transaction.CommitAsync();
    }
}
```

RNF02 (segurança contra condição de corrida) é resolvido pela transação com isolamento serializável: duas chamadas simultâneas de confirmação para horários conflitantes vão serializar no banco, e a segunda a executar vai encontrar a reserva já confirmada da primeira na checagem de `FindConfirmedOverlapsAsync`, falhando com `BookingConflictException` em vez de ambas passarem. Isso é a decisão de design para CA09, e é o motivo de essa verificação não poder ser feita apenas em memória na aplicação: duas instâncias do backend rodando em paralelo não compartilham memória, mas compartilham o banco.

## Transição automática para Completed

RF08 (marcar automaticamente como `Completed`) não é uma ação disparada por um usuário, então não tem um handler de aplicação chamado por uma rota HTTP. É um job agendado:

```csharp
public class BookingCompletionJob
{
    private readonly BookingRepository _repository;

    public BookingCompletionJob(BookingRepository repository)
    {
        _repository = repository;
    }

    public async Task RunAsync()
    {
        var expired = await _repository.FindConfirmedEndedBeforeAsync(DateTime.UtcNow);

        foreach (var booking in expired)
        {
            booking.TransitionTo(BookingStatus.Completed);
            await _repository.SaveAsync(booking);
        }
    }
}
```

Decisão em aberto, a ser confirmada antes da implementação: a frequência de execução deste job (a cada minuto, a cada 5 minutos) depende de quão rápido o sistema precisa refletir uma reserva como concluída, e não foi especificada em requirements.md. Assumir 5 minutos como default razoável, sujeito a confirmação.

## Permissão de cancelamento

RF09 (solicitante cancela só o próprio, aprovador cancela qualquer um da sala sob aprovação) é uma regra de autorização, não de estado. Ela é verificada no handler, antes de chamar `TransitionTo`, para manter a entidade `Booking` sem conhecimento de quem está pedindo a operação:

```csharp
public class CancelBookingHandler
{
    public async Task CancelAsync(Guid bookingId, Guid actingUserId, bool actingUserIsApprover)
    {
        var booking = await _repository.GetByIdAsync(bookingId)
            ?? throw new BookingNotFoundException(bookingId);

        var isOwner = booking.RequesterId == actingUserId;
        if (!isOwner && !actingUserIsApprover)
        {
            throw new BookingForbiddenException(bookingId, actingUserId);
        }

        if (booking.Status == BookingStatus.Confirmed)
        {
            var minutesUntilStart = (booking.StartsAt - DateTime.UtcNow).TotalMinutes;
            if (minutesUntilStart < 120)
            {
                throw new BookingCancellationWindowException(bookingId, minutesUntilStart);
            }
        }

        booking.TransitionTo(BookingStatus.Cancelled);
        await _repository.SaveAsync(booking);
    }
}
```

O prazo de 2 horas (RF07) só é verificado quando `Status == Confirmed`, nunca para `Draft`, o que está alinhado com o texto de requirements.md ("apenas para reservas Confirmada").

## Auditoria

RNF03 exige histórico de transição auditável. A decisão de design é um log de domínio simples, gravado na mesma transação da mudança de estado:

```
BookingStatusHistory
├── BookingId
├── FromStatus
├── ToStatus
├── ChangedByUserId
└── ChangedAt
```

Esse log não precisa de uma entidade de domínio rica, é um registro de escrita única (append-only), gravado por um pequeno serviço de auditoria chamado a partir de cada handler que executa uma transição.

## Estratégia de testes

- testes de unidade na entidade `Booking`: toda transição válida permitida, toda transição inválida rejeitada, `OverlapsWith` com casos de sobreposição total, parcial e ausência de sobreposição;
- teste de integração para `ConfirmBookingHandler`, incluindo o cenário de duas confirmações concorrentes para o mesmo horário (CA09), que exige um teste de integração real contra o banco, não um mock, já que a garantia vem do isolamento de transação;
- teste de unidade para `CancelBookingHandler`, cobrindo RF07 (prazo) e RF09 (permissão) separadamente;
- teste do job de conclusão automática, verificando que só reservas `Confirmed` com término passado são afetadas.

## Alternativas descartadas

Avaliou-se resolver a concorrência de RNF02 com um lock otimista (campo de versão na linha) em vez de transação serializável. Descartado para a primeira versão por ser mais simples de raciocinar sobre a transação serializável diretamente no caso de uso de confirmação, que é pontual e de baixo volume; lock otimista pode ser revisitado se a tabela de reservas crescer a ponto de transações serializáveis causarem contenção perceptível.
