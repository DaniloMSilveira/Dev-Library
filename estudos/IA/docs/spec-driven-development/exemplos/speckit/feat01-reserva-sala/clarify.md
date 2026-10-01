# Clarify

Gerado conceitualmente por `speckit.clarify`. Registra as perguntas levantadas sobre spec.md e as respostas que passam a valer como parte da especificação.

## Sessão de esclarecimento

**Pergunta 1:** sobreposição no instante exato, uma reserva terminando às 15h00 e outra começando às 15h00 na mesma sala, conta como conflito?

**Resposta:** não. Horários adjacentes (fim de uma igual ao início da outra) não são conflito. A condição de sobreposição é estritamente `inicio_A < fim_B E inicio_B < fim_A`, sem igualdade nas bordas.

**Impacto:** atualiza spec.md, cenário de comportamento esperado, para deixar explícito que `OverlapsWith` deve usar `<` estrito, não `<=`.

**Pergunta 2:** qual a frequência aceitável para a transição automática de "Confirmada" para "Concluída"?

**Resposta:** 5 minutos é aceitável para a primeira versão. Não há requisito de tempo real para essa transição específica.

**Impacto:** remove a marcação de decisão aberta em spec.md; a frequência de 5 minutos passa a ser parte do requisito, não mais uma suposição de implementação.

**Pergunta 3:** o que acontece se o aprovador cancelar uma reserva que já está em "Confirmada", e não apenas em "Rascunho"? RF06 menciona apenas confirmar ou cancelar uma reserva em "Rascunho".

**Resposta:** o aprovador também pode cancelar uma reserva já "Confirmada" da sala sob sua aprovação, sujeita à mesma regra de prazo de 2 horas que vale para o solicitante (RF07). RF09 já cobria isso implicitamente ("aprovador pode cancelar qualquer reserva da sala sob sua aprovação", sem restringir a estado), mas RF06 estava redigido de forma mais restrita e gerava a aparência de contradição.

**Impacto:** RF06 é reescrito para remover a restrição implícita a "Rascunho", eliminando a inconsistência com RF09.

## Spec atualizada após clarify

As três respostas acima são incorporadas a `spec.md` e passam a valer como requisito, não mais como suposição de quem implementa. Esta é a diferença central entre o fluxo com Spec Kit e o fluxo vanilla para este mesmo ponto: na versão vanilla, a mesma decisão (bordas não contam como conflito) foi tomada por quem escreveu o design e apenas registrada como nota; aqui, ela é levantada como pergunta explícita antes do plano técnico ser escrito, e a resposta vira parte da spec, não do design.
