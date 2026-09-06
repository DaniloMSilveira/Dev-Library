# 4. Spec Kit e ferramentas para SDD

Spec-Driven Development pode ser praticado manualmente com Git, Markdown e testes. Ferramentas como Spec Kit, skills de agentes, IDEs orientadas a planos e frameworks de BDD automatizam partes do fluxo, mas não substituem decisões humanas.

## 4.1 Spec Kit como fluxo de artefatos

O Spec Kit é apresentado como um conjunto de templates, scripts e instruções que organiza um projeto em torno de uma constituição, especificações, planos e tasks. Os nomes e detalhes podem mudar conforme a versão e a integração usada. Na documentação oficial consultada em 05/09/2026, o repositório indicava a versão 1.0.4.

É importante separar duas interfaces:

- `specify` é o CLI usado para instalar, inicializar e gerenciar o projeto;
- `/speckit.*` são comandos disponibilizados ao agente pela integração escolhida, não comandos genéricos do terminal.

Confirme a versão e a integração antes de reproduzir uma instalação. A tabela abaixo resume o fluxo conceitual; a sintaxe exata deve ser consultada na [documentação oficial do Spec Kit](https://github.com/github/spec-kit).

O fluxo conceitual é:

```text
constitution -> specify -> clarify -> plan -> tasks -> analyze -> implement
```

A relação entre os comandos e os artefatos costuma ser:

| Etapa | Responsabilidade | Artefato esperado |
|---|---|---|
| `speckit.constitution` | Definir princípios e regras não negociáveis | Constituição do repositório |
| `speckit.specify` | Descrever o que e por quê | Spec da feature |
| `speckit.clarify` | Resolver ambiguidades | Spec refinada |
| `speckit.plan` | Registrar decisões técnicas | Plano de implementação |
| `speckit.tasks` | Dividir o plano em passos | Lista de tasks |
| `speckit.analyze` | Procurar inconsistências | Relatório de análise |
| `speckit.implement` | Executar as tasks | Código, testes e documentação |
| `speckit.converge` | Comparar a implementação com os artefatos e registrar pendências | Tasks de convergência e evidências |

A nomenclatura exata pode ser diferente em versões futuras. O conceito importante é manter checkpoints entre intenção, design, execução e validação. No fluxo oficial consultado, `clarify` e `analyze` aparecem como etapas opcionais de refinamento e consistência.

## 4.2 Instalação e cautelas

Os artigos consultados descrevem um fluxo com agente de IA, Git, Python 3.11+ e `uv`, incluindo um comando de instalação do CLI. Como ferramentas, versões e requisitos mudam, este material não fixa um comando como universal.

Antes de instalar:

- confirme a documentação oficial do [GitHub Spec Kit](https://github.com/github/spec-kit);
- verifique a versão do Python e do gerenciador de pacotes;
- leia o que o comando de inicialização altera no repositório;
- execute em uma branch de trabalho;
- confira templates e scripts gerados antes de aceitá-los;
- mantenha o estado do projeto recuperável com Git.

Uma instalação global também pode afetar outros projetos. Prefira ambientes isolados quando o tooling permitir.

## 4.3 Skills e comandos de agentes

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

## 4.4 Outras ferramentas

| Ferramenta ou abordagem | Papel | Observação |
|---|---|---|
| Git + Markdown | Fluxo manual e transparente | Baixo custo inicial, maior disciplina manual |
| Cucumber, Behave, SpecFlow | Cenários BDD executáveis | Bom para comportamento colaborativo; exige manutenção de steps |
| OpenAPI | Contratos de API | Define interface, não toda a regra de negócio |
| Pact | Contract testing entre consumidor e provedor | Foca nas interações acordadas |
| Kiro | Ambiente opinativo para SDD | Verifique disponibilidade, custo e recursos atuais |
| Cursor e IDEs com planos | Planejamento assistido | O plano precisa continuar versionado e revisável |
| Claude Code Skills | Instruções e especialistas do projeto | Requer controle de contexto e permissões |

## 4.5 Critérios de escolha

Escolha tooling com base no risco que precisa ser controlado:

- contrato entre serviços: OpenAPI, Pact ou schema;
- comportamento de usuário: BDD e testes de aceitação;
- regras do repositório: constitution ou skill;
- implementação assistida: Spec Kit, skill ou plano versionado;
- validação ampla de API: geração e testes baseados em schema.

Não adicione uma ferramenta apenas porque ela gera mais arquivos. O tooling deve reduzir ambiguidade, facilitar revisão ou produzir evidência executável.
