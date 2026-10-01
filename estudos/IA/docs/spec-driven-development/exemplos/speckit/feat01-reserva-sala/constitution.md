# Constitution

Gerado conceitualmente por `speckit.constitution`. Regras estáveis do repositório, não específicas desta feature.

## Princípios

**P01. Testes antes de merge:** nenhuma mudança em `Domain/` ou `Application/` é aceita sem teste de unidade cobrindo o comportamento alterado.

**P02. Regra de negócio vive no domínio:** validações de estado, transição e invariantes ficam na camada `Domain/`, nunca espalhadas em controllers ou handlers.

**P03. Mudança de comportamento exige spec atualizada:** nenhuma alteração de regra de negócio é mesclada sem a spec correspondente refletir a mudança, conforme o princípio de manter a spec ancorada (ver trilha de spec-driven-development, documento 1).

**P04. Concorrência é responsabilidade explícita:** qualquer operação que possa ser chamada simultaneamente para o mesmo recurso deve declarar, no design, como a corrida é tratada. Ausência dessa seção é motivo de bloqueio em revisão.

**P05. Sem segredo em spec ou prompt:** nenhuma credencial, chave ou dado sensível de ambiente é colado em arquivos de spec, prompts de agente ou logs versionados.

Esta constituição é reaproveitada de outras features do repositório; apenas P04 foi destacada aqui por ser diretamente relevante ao domínio de reserva com conflito de horário.
