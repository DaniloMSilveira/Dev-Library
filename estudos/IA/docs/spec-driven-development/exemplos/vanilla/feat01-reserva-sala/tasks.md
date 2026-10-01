# Tasks: Reserva de sala com detecção de conflito

## T01. Criar entidade Booking e máquina de estados

**Arquivo:** `backend/Domain/Booking.cs`, `backend/Domain/BookingStatus.cs`

**Dependências:** nenhuma.

**Contexto:** a validade de uma transição de estado precisa estar centralizada na entidade, conforme design.md, seção "Modelagem da máquina de estados".

**O que fazer:**
- criar o enum `BookingStatus` com os 4 estados;
- criar `Booking` com o dicionário `ValidTransitions` e o método `TransitionTo`;
- implementar `OverlapsWith` para detecção de sobreposição de intervalo.

**Notas de implementação:** `TransitionTo` deve lançar `InvalidBookingTransitionException` quando a transição não estiver no dicionário, nunca falhar silenciosamente.

**Critério de aceite:** CA09 depende indiretamente desta task, mas o critério direto é: toda transição listada em requirements.md é aceita, e qualquer transição fora da lista lança exceção.

**Validação:** `dotnet test --filter Booking` cobrindo as 4 transições válidas e ao menos 2 inválidas (ex.: Cancelled -> Confirmed, Completed -> Draft).

## T02. Testes de unidade de Booking

**Arquivo:** `backend/Domain/BookingTests.cs`

**Dependências:** T01.

**Contexto:** CA09 e RNF01 dependem de `OverlapsWith` estar correto antes de qualquer handler ser escrito.

**O que fazer:**
- testar as 4 transições válidas;
- testar ao menos 3 transições inválidas, incluindo as duas saindo de estado final;
- testar `OverlapsWith` com sobreposição total, sobreposição parcial no início, sobreposição parcial no fim, e sem sobreposição (horários adjacentes, ex. um termina exatamente quando o outro começa).

**Critério de aceite:** CA03 e CA04 dependem desta lógica estar correta.

**Validação:** `dotnet test --filter Booking`, todos os casos acima passando.

## T03. Implementar BookingRepository

**Arquivo:** `backend/Infrastructure/BookingRepository.cs`

**Dependências:** T01.

**Contexto:** `FindConfirmedOverlapsAsync` é o método central para RF03, RF05 e RNF01; só deve considerar reservas `Confirmed`.

**O que fazer:**
- implementar persistência básica (get por id, save);
- implementar `FindConfirmedOverlapsAsync(roomId, start, end, excludingBookingId)`, filtrando por `Status == Confirmed`;
- implementar `BeginSerializableTransactionAsync` conforme a decisão de RNF02 em design.md;
- implementar `FindConfirmedEndedBeforeAsync(dateTime)` para uso do job de conclusão (T06).

**Critério de aceite:** uma consulta por sobreposição nunca retorna reservas em `Draft`, `Cancelled` ou `Completed`.

**Validação:** teste de integração contra o banco de desenvolvimento, inserindo reservas em diferentes estados e verificando o filtro.

## T04. Implementar CreateBookingHandler

**Arquivo:** `backend/Application/CreateBookingHandler.cs`

**Dependências:** T01, T03.

**Contexto:** RF01 e RF02 determinam o estado inicial da reserva, dependendo da configuração da sala.

**O que fazer:**
- validar horário de término posterior ao de início (ver "casos de erro e limites" em requirements.md);
- validar que a sala existe e está ativa;
- criar a reserva em `Confirmed` diretamente se a sala for de aprovação automática, ou em `Draft` caso contrário;
- quando criada diretamente em `Confirmed`, aplicar a mesma verificação de conflito de T05 antes de persistir.

**Critério de aceite:** CA01 e CA02.

**Validação:** `dotnet test --filter CreateBookingHandler`.

## T05. Implementar ConfirmBookingHandler

**Arquivo:** `backend/Application/ConfirmBookingHandler.cs`

**Dependências:** T01, T03.

**Contexto:** este é o handler mais sensível da feature, por concentrar RF03, RF05, RNF02 e CA09, conforme detalhado em design.md.

**O que fazer:**
- abrir transação serializável;
- buscar a reserva e lançar `BookingNotFoundException` se não existir;
- verificar conflito via `FindConfirmedOverlapsAsync`, excluindo a própria reserva;
- lançar `BookingConflictException` em caso de conflito, sem persistir a transição;
- confirmar a transição e persistir dentro da mesma transação.

**Critério de aceite:** CA03, CA05 (indiretamente, via mensagem de conflito) e, principalmente, CA09.

**Validação:** teste de integração com duas chamadas concorrentes reais (ex.: `Task.WhenAll` disparando duas confirmações para horários conflitantes) contra o banco de desenvolvimento, não contra um mock, conforme a nota de design.md sobre a origem da garantia de RNF02.

## T06. Implementar CancelBookingHandler

**Arquivo:** `backend/Application/CancelBookingHandler.cs`

**Dependências:** T01, T03.

**Contexto:** RF07 (prazo de 2 horas) e RF09 (permissão) são duas regras independentes, cobertas em design.md.

**O que fazer:**
- verificar permissão (dono da reserva ou aprovador) antes de qualquer outra validação;
- verificar prazo de 2 horas apenas quando o status atual for `Confirmed`;
- aplicar a transição para `Cancelled`.

**Critério de aceite:** CA05, CA06, CA08.

**Validação:** `dotnet test --filter CancelBookingHandler`, cobrindo separadamente o caso de permissão negada e o caso de prazo violado.

## T07. Implementar BookingCompletionJob

**Arquivo:** `backend/Infrastructure/BookingCompletionJob.cs`

**Dependências:** T01, T03.

**Contexto:** RF08, decisão de frequência marcada como aberta em design.md (assumido 5 minutos).

**O que fazer:**
- buscar reservas `Confirmed` com término já passado;
- transicionar cada uma para `Completed` e persistir.

**Critério de aceite:** CA07.

**Validação:** teste de unidade chamando `RunAsync` com dados simulados de reservas expiradas e não expiradas, verificando que só as expiradas mudam de estado.

## T08. Expor endpoints em BookingsController

**Arquivo:** `backend/Api/BookingsController.cs`

**Dependências:** T04, T05, T06.

**O que fazer:**
- `POST /api/bookings` chamando `CreateBookingHandler`;
- `POST /api/bookings/{id}/confirm` chamando `ConfirmBookingHandler`;
- `POST /api/bookings/{id}/cancel` chamando `CancelBookingHandler`;
- mapear `BookingConflictException`, `BookingForbiddenException` e `BookingCancellationWindowException` para códigos HTTP apropriados (409, 403, 422 respectivamente).

**Critério de aceite:** todos os CA01 a CA08 acessíveis via chamada HTTP, não apenas via chamada direta ao handler.

**Validação:** coleção de requisições HTTP (ex. arquivo `.http` ou Postman) cobrindo cada critério de aceite.

## T09. Implementar auditoria de transição

**Arquivo:** a definir junto com a migração de banco para `BookingStatusHistory`.

**Dependências:** T04, T05, T06, T07.

**Contexto:** RNF03.

**O que fazer:**
- criar a tabela/registro `BookingStatusHistory` conforme design.md;
- gravar uma entrada a cada chamada de `TransitionTo` bem-sucedida, na mesma transação da mudança de estado.

**Critério de aceite:** nenhum CA específico, mas é requisito não funcional obrigatório (RNF03); validação é a existência do registro, não um comportamento visível ao usuário final.

**Validação:** consulta manual à tabela após executar os testes de T04 a T07, confirmando uma entrada por transição realizada.

## T10. Verificação integrada

**Dependências:** todas as anteriores.

**O que fazer:**
- subir o backend com banco de desenvolvimento populado com ao menos duas salas (uma de aprovação automática, uma que exige aprovação);
- executar manualmente o fluxo completo: criar reserva em sala de aprovação automática (CA01), criar e confirmar em sala com aprovação (CA02 e depois confirmação), tentar criar conflito (CA03), cancelar dentro e fora do prazo (CA05 e CA06), disparar o job de conclusão manualmente e verificar CA07;
- executar o teste de concorrência de T05 isoladamente mais uma vez, já integrado ao endpoint HTTP, não apenas ao handler direto.

Esta é a única task que confirma, de ponta a ponta, que a combinação de todos os handlers com o banco real produz o comportamento esperado pela máquina de estados definida em requirements.md.
