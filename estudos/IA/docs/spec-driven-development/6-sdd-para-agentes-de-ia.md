# 6. SDD para agentes de IA

Agentes de IA tornam o ciclo SDD mais rápido, mas também tornam erros de escopo mais baratos de produzir e mais caros de revisar. O agente deve ser tratado como executor e colaborador técnico sob restrições explícitas, não como autoridade sobre requisitos ou arquitetura.

## 6.1 Contexto mínimo

Forneça ao agente:

- objetivo e impacto;
- spec aprovada;
- constituição e convenções do projeto;
- arquivos e interfaces relevantes;
- o que muda e o que não muda;
- critérios de aceite;
- comandos de validação;
- limites de segurança, dados e permissões.

O primeiro passo deve ser leitura do repositório e das fontes relevantes. Uma resposta genérica que não referencia o código real é um sinal de que o contexto ainda é insuficiente.

## 6.2 Fases de uma skill de SDD

Uma skill versionada pode seguir este fluxo:

### Fase 0: perguntas

Coleta contexto sobre problema, impacto, arquivos afetados e restrições. Deve interromper o processo se houver uma decisão bloqueadora.

### Fase 1: SDD

Gera um documento com contexto, escopo, design, fluxo, arquivos, critérios de aceite e considerações adicionais. Os caminhos devem ser reais ou explicitamente novos.

### Fase 2: validação

Revisa caminhos citados, compatibilidade, critérios e escopo. Apresenta o resultado da validação e aguarda aprovação.

### Fase 3: tasks

Cria tarefas individuais com dependências, contexto, notas de implementação e critérios verificáveis. A última task deve cuidar da verificação integrada.

### Fase 4: execução

Implementa uma task por vez, executa validações e informa arquivos alterados. O agente não deve começar a próxima task sem que o checkpoint anterior esteja aceitável.

## 6.3 Prompts por intenção

Para explorar:

```text
Leia a spec e o código relevante. Não edite arquivos.
Liste o comportamento atual, o esperado, as ambiguidades e os riscos.
Cite os caminhos reais usados na análise.
```

Para planejar:

```text
Com base na spec aprovada, proponha tasks pequenas e ordenadas.
Para cada task, informe arquivos, dependências, critério de aceite e comando de validação.
Não implemente.
```

Para implementar:

```text
Implemente somente TASK-2.
Respeite o que não muda e não crie funcionalidades novas.
Execute os testes relacionados e relate qualquer divergência da spec.
```

Para revisar:

```text
Compare a implementação com a spec e os critérios de aceite.
Liste primeiro violações, regressões, riscos e testes ausentes.
Não altere arquivos até a aprovação das correções.
```

## 6.4 Permissões e segurança

Comece com permissões restritas e leitura do projeto. A aprovação automática de escritas pode ser aceitável em tarefas de baixo risco, mas não deve ser confundida com revisão de segurança.

Não envie ao agente:

- credenciais;
- tokens ou chaves privadas;
- dados pessoais desnecessários;
- arquivos de produção sem necessidade;
- contexto maior do que a tarefa exige.

Em infraestrutura, defina cedo autenticação, autorização, segredos, logging e rollback. Adiar segurança pode obrigar substituição de recursos ou reimplantação de toda a stack.

## 6.5 Context window e sessões longas

Contexto finito influencia o processo. Para reduzir perda de informação:

- mantenha specs compactas e referenciáveis;
- registre decisões fora da conversa;
- divida trabalho em fases e tasks;
- resuma estado ao trocar de sessão;
- não dependa apenas do histórico do chat;
- valide o que o agente realmente leu.

Ferramentas podem compactar ou resumir conversas, mas isso não garante preservação de todos os detalhes. Artefatos versionados são uma memória mais auditável.

## 6.6 Feedback e correção

Quando o resultado divergir, preserve a evidência:

- comportamento esperado;
- comportamento observado;
- passos para reproduzir;
- mensagem de erro;
- arquivos envolvidos;
- hipótese sobre a causa.

Depois classifique o caso: código incorreto, spec incorreta, ambiente bloqueado ou requisito novo. Atualize o artefato responsável e regenere somente o que depende dele.

## 6.7 O que não automatizar cegamente

Não delegue sem revisão:

- decisões de segurança e privacidade;
- mudanças irreversíveis em infraestrutura;
- migrações sem estratégia de rollback;
- requisitos legais ou financeiros;
- aprovação final de critérios de negócio;
- alterações amplas causadas por uma task pequena.
