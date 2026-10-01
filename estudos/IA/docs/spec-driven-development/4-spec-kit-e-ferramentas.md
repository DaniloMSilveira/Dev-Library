# 4. Spec Kit e ferramentas para SDD

Spec-Driven Development pode ser praticado manualmente com Git, Markdown e testes. Ferramentas como Spec Kit, skills de agentes, IDEs orientadas a planos e frameworks de BDD automatizam partes do fluxo, mas não substituem decisões humanas.

## 4.1 O que é estável e o que muda com a versão

Antes de descrever o Spec Kit, vale separar duas coisas que costumam se misturar ao ler documentação de ferramentas. O conceito por trás do fluxo (uma constituição que registra regras estáveis, uma etapa de especificar, uma de esclarecer ambiguidades, uma de planejar, uma de dividir em tasks, uma de analisar consistência, uma de implementar) é estável: reflete as fases já descritas no documento anterior, e não muda com a versão da ferramenta. Já os nomes exatos dos comandos, a sintaxe do CLI, os requisitos de instalação e os detalhes de versão descritos nas seções 4.2 e 4.3 são específicos da versão consultada e devem ser tratados como referência histórica, não como verdade permanente. Ao ler este documento no futuro, revalide os detalhes de versão na documentação oficial antes de segui-los; o conceito de fluxo continua útil mesmo que os comandos mudem de nome.

## 4.2 Spec Kit como fluxo de artefatos

O Spec Kit é apresentado como um conjunto de templates, scripts e instruções que organiza um projeto em torno de uma constituição, especificações, planos e tasks. Os nomes e detalhes podem mudar conforme a versão e a integração usada. Na documentação oficial consultada em 05/09/2026, o repositório indicava a versão 1.0.4.

É importante separar duas interfaces:

- `specify` é o CLI usado para instalar, inicializar e gerenciar o projeto;
- `/speckit.*` são comandos disponibilizados ao agente pela integração escolhida, não comandos genéricos do terminal.

Confirme a versão e a integração antes de reproduzir uma instalação. A tabela abaixo resume o fluxo conceitual; a sintaxe exata deve ser consultada na [documentação oficial do Spec Kit](https://github.com/github/spec-kit).

O fluxo conceitual é:

```
constitution -> specify -> clarify -> plan -> tasks -> analyze -> implement
```

A relação entre os comandos e os artefatos costuma ser:

| Etapa | Responsabilidade | Artefato esperado | Fase equivalente (doc 3) |
|---|---|---|---|
| `speckit.constitution` | Definir princípios e regras não negociáveis | Constituição do repositório | Anterior à fase 0 |
| `speckit.specify` | Descrever o que e por quê | Spec da feature | Fase 0 e 1 |
| `speckit.clarify` | Resolver ambiguidades | Spec refinada | Fase 2 |
| `speckit.plan` | Registrar decisões técnicas | Plano de implementação | Fase 3 |
| `speckit.tasks` | Dividir o plano em passos | Lista de tasks | Fase 4 |
| `speckit.analyze` | Procurar inconsistências | Relatório de análise | Fase 5 |
| `speckit.implement` | Executar as tasks | Código, testes e documentação | Fase 5 |
| `speckit.converge` | Comparar a implementação com os artefatos e registrar pendências | Tasks de convergência e evidências | Fase 6 e 7 |

A nomenclatura exata pode ser diferente em versões futuras. O conceito importante é manter checkpoints entre intenção, design, execução e validação. No fluxo oficial consultado, `clarify` e `analyze` aparecem como etapas opcionais de refinamento e consistência, o que é coerente com a seção 3.1 do documento anterior: para uma correção pequena, essas duas etapas são candidatas naturais a serem puladas.

## 4.3 Instalação e cautelas

Os artigos consultados descrevem um fluxo com agente de IA, Git, Python 3.11+ e `uv`, incluindo um comando de instalação do CLI. Como ferramentas, versões e requisitos mudam, este material não fixa um comando como universal.

Antes de instalar:

- confirme a documentação oficial do [GitHub Spec Kit](https://github.com/github/spec-kit);
- verifique a versão do Python e do gerenciador de pacotes;
- leia o que o comando de inicialização altera no repositório;
- execute em uma branch de trabalho;
- confira templates e scripts gerados antes de aceitá-los;
- mantenha o estado do projeto recuperável com Git.

Uma instalação global também pode afetar outros projetos. Prefira ambientes isolados quando o tooling permitir.

## 4.4 Skills e comandos de agentes

Uma skill é uma instrução especializada versionada no próprio projeto. Ela pode orientar um agente por fases como:

1. coletar contexto;
2. fazer perguntas;
3. gerar a spec;
4. validar caminhos citados e critérios;
5. aguardar aprovação;
6. gerar tasks;
7. implementar uma task por vez;
8. executar verificações;
9. resumir dependências e paralelismo.

Uma skill não deve conceder liberdade ilimitada. Ela precisa definir escopo, arquivos permitidos, comandos de validação e condições para parar e perguntar.

## 4.5 Outras ferramentas

| Ferramenta ou abordagem | Papel | Observação |
|---|---|---|
| Git + Markdown | Fluxo manual e transparente | Baixo custo inicial, maior disciplina manual |
| Cucumber, Behave, SpecFlow | Cenários BDD executáveis | Bom para comportamento colaborativo; exige manutenção de steps |
| OpenAPI | Contratos de API | Define interface, não toda a regra de negócio |
| Pact | Contract testing entre consumidor e provedor | Foca nas interações acordadas |
| Kiro | Ambiente opinativo para SDD | Verifique disponibilidade, custo e recursos atuais |
| Cursor e IDEs com planos | Planejamento assistido | O plano precisa continuar versionado e revisável |
| Claude Code Skills | Instruções e especialistas do projeto | Requer controle de contexto e permissões |

## 4.6 Critérios de escolha

Escolha tooling com base no risco que precisa ser controlado, e não porque a ferramenta parece popular:

**Contrato entre serviços:** OpenAPI, Pact ou schema. Da tabela 4.5, isso aponta diretamente para OpenAPI (definição de interface) e Pact (verificação do acordo entre consumidor e provedor); nenhum dos dois resolve regra de negócio sozinho.

**Comportamento de usuário:** BDD e testes de aceitação. Cucumber, Behave e SpecFlow, da tabela 4.5, servem aqui, mas custam manutenção contínua de steps, o que só compensa quando o comportamento é revisado com frequência por pessoas não técnicas.

**Regras do repositório:** constitution ou skill. Isso é o `speckit.constitution` da seção 4.2, ou uma skill equivalente da seção 4.4, quando o projeto não usa Spec Kit.

**Implementação assistida:** Spec Kit, skill ou plano versionado. Spec Kit dá o fluxo completo de comandos; uma skill isolada (Claude Code Skills, por exemplo) dá mais controle granular sobre uma única fase; um plano versionado em uma IDE serve quando o time já confia no processo manual e só quer assistência pontual.

**Validação ampla de API:** geração e testes baseados em schema. Aponta de volta para OpenAPI como fonte de verdade do contrato, com testes gerados a partir dele.

Não adicione uma ferramenta apenas porque ela gera mais arquivos. O tooling deve reduzir ambiguidade, facilitar revisão ou produzir evidência executável. Se uma ferramenta nova não fizer nenhuma dessas três coisas melhor do que Git e Markdown já fazem, o ganho não justifica a complexidade adicional.
