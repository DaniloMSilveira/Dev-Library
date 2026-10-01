# 5. Exemplo com Angular e .NET: consulta de status de pagamento

Este laboratório ilustra uma feature mais próxima do que aparece em sistemas reais: integração com um provedor externo e persistência de dados de domínio. O backend é .NET, o frontend é Angular. O objetivo é mostrar como requirements, design e tasks reduzem decisões implícitas em um cenário com mais fronteiras do que uma tela isolada: consistência entre consulta externa e estado salvo, idempotência e tratamento de falha de integração.

## 5.1 O que será construído

A feature consulta o status de um pagamento em um provedor externo e persiste esse status no domínio da aplicação:

- `PaymentStatusService` (frontend): chama o endpoint interno e expõe o resultado para a tela;
- `PaymentStatusComponent` (frontend): exibe status, loading, erro e permite nova consulta;
- `GetPaymentStatusEndpoint` (backend): orquestra a consulta ao provedor externo e a persistência;
- `PaymentGatewayClient` (backend): encapsula a chamada HTTP ao provedor externo e mapeia o DTO externo;
- `Payment` (domínio): entidade persistida, com seu próprio status, independente do status retornado pelo provedor a cada consulta;
- `PaymentRepository` (backend): persiste e recupera o estado do pagamento.

A implementação completa dos artefatos deste exemplo (requirements.md, design.md e tasks.md) está em [`examples/002-payment-status-vanilla`](./examples/002-payment-status-vanilla/). Um segundo exemplo do mesmo domínio usando Spec Kit está em [`examples/002-payment-status-speckit`](./examples/002-payment-status-speckit/), útil para comparar o fluxo manual com o assistido por ferramenta.

## 5.2 Requisitos e critérios

A funcionalidade precisa:

- consultar o status de um pagamento existente por identificador interno;
- buscar o status atual no provedor externo quando o status local estiver desatualizado ou pendente;
- persistir o novo status quando o provedor retornar um status final (aprovado, recusado, estornado);
- não persistir uma mudança de status quando a consulta ao provedor falhar;
- expor ao frontend o status salvo, não o status bruto do provedor, para manter o domínio como fonte de verdade da aplicação;
- permitir nova tentativa de consulta pela interface, sem duplicar efeitos no domínio quando repetida.

Exemplos de requisitos funcionais:

```
RF01. Dado um pagamento com status "pendente", o sistema deve consultar o provedor externo ao abrir a tela de detalhe.
RF02. Quando o provedor retornar um status final, o sistema deve persistir esse status no domínio.
RF03. Quando o provedor estiver indisponível, o sistema deve manter o último status salvo e sinalizar a falha de consulta.
RF04. O usuário deve poder forçar uma nova consulta pelo botão "Atualizar status".
RF05. Consultas repetidas para o mesmo pagamento não devem gerar registros de histórico duplicados.
```

Fora de escopo, para deixar explícito desde o início: processar o pagamento em si, cancelar ou estornar um pagamento, e qualquer webhook assíncrono do provedor (esta feature cobre apenas a consulta sob demanda, iniciada pelo usuário).

Exemplos de critérios testáveis:

- com status local "aprovado", abrir a tela não dispara chamada ao provedor;
- com status local "pendente", abrir a tela dispara exatamente uma chamada ao provedor;
- quando o provedor retorna "aprovado", o domínio passa a refletir "aprovado" e a tela exibe esse status;
- quando o provedor está indisponível, o status local não muda e a tela exibe uma mensagem de falha de consulta, distinta de "pagamento recusado";
- duas chamadas consecutivas de "Atualizar status" para o mesmo pagamento não criam duas entradas de histórico, apenas atualizam a existente.

## 5.3 Design

A fronteira central deste exemplo é a diferença entre o status retornado pelo provedor a cada chamada e o status persistido no domínio, que só muda quando o provedor confirma um estado final.

```
backend/
├── Domain/
│   ├── Payment.cs
│   └── PaymentStatus.cs
├── Application/
│   └── GetPaymentStatusHandler.cs
├── Infrastructure/
│   ├── PaymentGatewayClient.cs
│   └── PaymentRepository.cs
└── Api/
    └── PaymentsController.cs

frontend/src/app/payment/
├── data/
│   ├── payment-status.model.ts
│   └── payment-status.service.ts
└── feature/
    └── payment-status.component.ts
```

Decisões de design:

- o backend nunca expõe o DTO do provedor diretamente ao frontend, sempre mapeia para um modelo de domínio ou de resposta próprio;
- a consulta ao provedor acontece apenas quando o status local não é final, evitando chamadas desnecessárias (critério ligado a RF01);
- a persistência de um novo status é feita de forma idempotente: uma função ou cláusula que atualiza o status existente, em vez de inserir um novo registro de histórico a cada consulta (critério ligado a RF05);
- falha de comunicação com o provedor é tratada como um erro de infraestrutura, distinto de um status de negócio "recusado", e não deve alterar o estado persistido (critério ligado a RF03);
- um timeout explícito é configurado na chamada HTTP ao provedor, para não deixar a requisição do usuário pendurada indefinidamente.

Essas decisões devem ser confirmadas pelas convenções do projeto real. O exemplo não autoriza copiar a arquitetura sem revisar o contexto, especialmente o mecanismo de idempotência, que pode variar bastante dependendo do banco de dados usado.

## 5.4 Domínio e persistência

A entidade de domínio mantém seu próprio ciclo de vida, independente do formato de resposta do provedor:

```csharp
// Domain/PaymentStatus.cs
public enum PaymentStatus
{
    Pending,
    Approved,
    Declined,
    Refunded
}
```

```csharp
// Domain/Payment.cs
public class Payment
{
    public Guid Id { get; private set; }
    public string ExternalReference { get; private set; }
    public PaymentStatus Status { get; private set; }
    public DateTime LastCheckedAt { get; private set; }

    private static readonly PaymentStatus[] FinalStatuses =
    {
        PaymentStatus.Approved,
        PaymentStatus.Declined,
        PaymentStatus.Refunded
    };

    public bool IsFinal => FinalStatuses.Contains(Status);

    public void UpdateStatus(PaymentStatus newStatus, DateTime checkedAt)
    {
        if (IsFinal)
        {
            // Uma vez final, o status não deve regredir nem ser sobrescrito
            // por uma nova consulta, mesmo que o provedor responda algo diferente.
            return;
        }

        Status = newStatus;
        LastCheckedAt = checkedAt;
    }
}
```

A regra `IsFinal` dentro da própria entidade é o que garante RF02 e, ao mesmo tempo, protege contra uma resposta inconsistente do provedor sobrescrever um estado já definitivo, requisito que não estava explícito na lista de RFs, mas decorre diretamente de RF02 e foi registrado aqui como decisão de design.

## 5.5 Cliente do provedor externo

O cliente HTTP isola o formato específico do provedor e nunca deixa esse formato vazar para o domínio:

```csharp
// Infrastructure/PaymentGatewayClient.cs
public class PaymentGatewayClient
{
    private readonly HttpClient _httpClient;

    public PaymentGatewayClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
        _httpClient.Timeout = TimeSpan.FromSeconds(5);
    }

    public async Task<PaymentStatus> GetStatusAsync(string externalReference)
    {
        var response = await _httpClient.GetAsync($"/v1/charges/{externalReference}");

        if (!response.IsSuccessStatusCode)
        {
            throw new PaymentGatewayUnavailableException(
                $"Provedor retornou {(int)response.StatusCode} para {externalReference}.");
        }

        var dto = await response.Content.ReadFromJsonAsync<ChargeStatusDto>();

        return dto!.Status switch
        {
            "paid" => PaymentStatus.Approved,
            "declined" => PaymentStatus.Declined,
            "refunded" => PaymentStatus.Refunded,
            _ => PaymentStatus.Pending
        };
    }

    private record ChargeStatusDto(string Status);
}

public class PaymentGatewayUnavailableException : Exception
{
    public PaymentGatewayUnavailableException(string message) : base(message) { }
}
```

O `switch` que mapeia `"paid"`, `"declined"`, `"refunded"` do provedor para o enum `PaymentStatus` do domínio é a fronteira anticorrupção da integração: se o provedor mudar o nome de um status amanhã, só este método muda, o domínio e o restante da aplicação não são afetados.

## 5.6 Handler de aplicação

O handler decide quando consultar o provedor e quando apenas devolver o status já salvo, aplicando diretamente RF01:

```csharp
// Application/GetPaymentStatusHandler.cs
public class GetPaymentStatusHandler
{
    private readonly PaymentRepository _repository;
    private readonly PaymentGatewayClient _gatewayClient;

    public GetPaymentStatusHandler(PaymentRepository repository, PaymentGatewayClient gatewayClient)
    {
        _repository = repository;
        _gatewayClient = gatewayClient;
    }

    public async Task<PaymentStatusResult> HandleAsync(Guid paymentId)
    {
        var payment = await _repository.GetByIdAsync(paymentId)
            ?? throw new PaymentNotFoundException(paymentId);

        if (payment.IsFinal)
        {
            return PaymentStatusResult.FromDomain(payment, queriedProvider: false);
        }

        try
        {
            var providerStatus = await _gatewayClient.GetStatusAsync(payment.ExternalReference);
            payment.UpdateStatus(providerStatus, DateTime.UtcNow);
            await _repository.SaveAsync(payment);

            return PaymentStatusResult.FromDomain(payment, queriedProvider: true);
        }
        catch (PaymentGatewayUnavailableException)
        {
            // Falha de infraestrutura: devolve o último status salvo,
            // sinalizando que a consulta ao provedor falhou, sem alterar o domínio.
            return PaymentStatusResult.FromDomain(payment, queriedProvider: true, providerFailed: true);
        }
    }
}

public record PaymentStatusResult(PaymentStatus Status, bool QueriedProvider, bool ProviderFailed)
{
    public static PaymentStatusResult FromDomain(Payment payment, bool queriedProvider, bool providerFailed = false)
        => new(payment.Status, queriedProvider, providerFailed);
}
```

O `try/catch` em torno apenas da chamada ao provedor, e não em torno do `SaveAsync`, é deliberado: uma falha ao persistir deve propagar como erro real (RF02 não foi cumprido), enquanto uma falha ao consultar o provedor é um caso de negócio esperado (RF03) e tem uma resposta própria.

## 5.7 Frontend: service e componente

O service do frontend consome apenas o endpoint interno, nunca o provedor externo diretamente:

```typescript
// frontend/src/app/payment/data/payment-status.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PaymentStatusResult } from './payment-status.model';

@Injectable({ providedIn: 'root' })
export class PaymentStatusService {
  private http = inject(HttpClient);

  getStatus(paymentId: string): Observable<PaymentStatusResult> {
    return this.http.get<PaymentStatusResult>(`/api/payments/${paymentId}/status`);
  }
}
```

```typescript
// frontend/src/app/payment/data/payment-status.model.ts
export type PaymentStatus = 'Pending' | 'Approved' | 'Declined' | 'Refunded';

export interface PaymentStatusResult {
  status: PaymentStatus;
  queriedProvider: boolean;
  providerFailed: boolean;
}
```

O componente distingue, na interface, um status de negócio de uma falha de consulta, exatamente o que o critério de RF03 exige:

```typescript
// frontend/src/app/payment/feature/payment-status.component.ts
import { Component, inject, input, signal } from '@angular/core';
import { PaymentStatusService } from '../data/payment-status.service';
import { PaymentStatusResult } from '../data/payment-status.model';

@Component({
  selector: 'app-payment-status',
  standalone: true,
  template: `
    @if (loading()) {
      <p>Consultando status...</p>
    } @else if (result(); as result) {
      <p>Status: {{ result.status }}</p>
      @if (result.providerFailed) {
        <p role="alert">Não foi possível confirmar o status mais recente com o provedor.</p>
      }
    }
    <button (click)="refresh()" [disabled]="loading()">Atualizar status</button>
  `,
})
export class PaymentStatusComponent {
  paymentId = input.required<string>();

  private service = inject(PaymentStatusService);
  result = signal<PaymentStatusResult | null>(null);
  loading = signal(false);

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.service.getStatus(this.paymentId()).subscribe({
      next: (result) => {
        this.result.set(result);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }
}
```

## 5.8 Testes

Teste do domínio, cobrindo a regra de não regressão de status final:

```csharp
// Domain/PaymentTests.cs
public class PaymentTests
{
    [Fact]
    public void UpdateStatus_quando_status_atual_e_final_nao_deve_alterar()
    {
        var payment = PaymentTestFactory.WithStatus(PaymentStatus.Approved);

        payment.UpdateStatus(PaymentStatus.Declined, DateTime.UtcNow);

        Assert.Equal(PaymentStatus.Approved, payment.Status);
    }

    [Fact]
    public void UpdateStatus_quando_status_atual_e_pendente_deve_atualizar()
    {
        var payment = PaymentTestFactory.WithStatus(PaymentStatus.Pending);

        payment.UpdateStatus(PaymentStatus.Approved, DateTime.UtcNow);

        Assert.Equal(PaymentStatus.Approved, payment.Status);
    }
}
```

Teste do handler, cobrindo o caso de falha do provedor sem alteração de domínio, que é o critério mais fácil de implementar errado nesta feature:

```csharp
// Application/GetPaymentStatusHandlerTests.cs
public class GetPaymentStatusHandlerTests
{
    [Fact]
    public async Task HandleAsync_quando_provedor_falha_mantem_status_salvo()
    {
        var payment = PaymentTestFactory.WithStatus(PaymentStatus.Pending);
        var repository = Substitute.For<PaymentRepository>();
        repository.GetByIdAsync(payment.Id).Returns(payment);

        var gatewayClient = Substitute.For<PaymentGatewayClient>();
        gatewayClient.GetStatusAsync(payment.ExternalReference)
            .Returns<Task<PaymentStatus>>(_ => throw new PaymentGatewayUnavailableException("timeout"));

        var handler = new GetPaymentStatusHandler(repository, gatewayClient);

        var result = await handler.HandleAsync(payment.Id);

        Assert.True(result.ProviderFailed);
        Assert.Equal(PaymentStatus.Pending, payment.Status);
        await repository.DidNotReceive().SaveAsync(Arg.Any<Payment>());
    }

    [Fact]
    public async Task HandleAsync_quando_status_ja_e_final_nao_consulta_provedor()
    {
        var payment = PaymentTestFactory.WithStatus(PaymentStatus.Approved);
        var repository = Substitute.For<PaymentRepository>();
        repository.GetByIdAsync(payment.Id).Returns(payment);
        var gatewayClient = Substitute.For<PaymentGatewayClient>();

        var handler = new GetPaymentStatusHandler(repository, gatewayClient);
        await handler.HandleAsync(payment.Id);

        await gatewayClient.DidNotReceive().GetStatusAsync(Arg.Any<string>());
    }
}
```

## 5.9 Tasks

1. Criar `PaymentStatus` e `Payment`, com a regra de não regressão de status final.
2. Implementar `PaymentGatewayClient`, incluindo timeout e mapeamento de DTO externo.
3. Implementar `PaymentRepository` com atualização idempotente de status.
4. Implementar `GetPaymentStatusHandler`, cobrindo os três caminhos: status final, sucesso de consulta e falha de provedor.
5. Expor o endpoint em `PaymentsController`.
6. Implementar `PaymentStatusService` e `PaymentStatusComponent` no frontend.
7. Escrever testes de domínio e de handler cobrindo os critérios de RF02, RF03 e RF05.
8. Executar verificação integrada: subir backend e frontend, simular indisponibilidade do provedor e confirmar que o status local não muda.

A task 8 é a mais importante deste exemplo: é a única forma de confirmar, de ponta a ponta, que RF03 (não persistir mudança quando a consulta falha) realmente funciona, já que esse comportamento depende da integração entre handler, repositório e cliente HTTP, não de uma única unidade isolada.

## 5.10 Limitações do laboratório

- o provedor de pagamento real pode ter um formato de resposta diferente do DTO simplificado usado aqui;
- idempotência de persistência foi tratada apenas no nível do método, uma aplicação real pode precisar de controle adicional em nível de banco de dados sob concorrência;
- autenticação com o provedor (API key, OAuth) foi omitida para focar no fluxo de domínio e integração;
- cenários de reconciliação (webhook assíncrono do provedor avisando mudança de status) ficam fora deste exemplo, conforme definido em "fora de escopo" na seção 5.2;
- dados sensíveis de pagamento devem seguir as exigências de conformidade aplicáveis (como PCI DSS), que não são o foco deste material.
