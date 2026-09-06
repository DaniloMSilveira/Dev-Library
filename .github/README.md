# Governanca de agentes

Esta pasta concentra as instrucoes versionadas para agentes de IA que trabalham no Dev-Library.

## Primeiros passos

Para tarefas de documentacao, selecione o agente `documentador` no seletor de agentes do Copilot. Ele e um agente especializado do repositorio e deve ser escolhido manualmente em cada novo chat quando esse fluxo for necessario.

O agente padrao do VS Code tambem recebe as instrucoes gerais do repositorio e pode carregar skills relevantes, mas a existencia deste arquivo nao substitui automaticamente o agente ativo.

## Estrutura

- `copilot-instructions.md`: regras gerais carregadas como contexto do repositorio.
- `memory/project-memory.md`: memoria persistida com mapa, convencoes, decisoes e lacunas conhecidas.
- `instructions/documentacao.instructions.md`: regras aplicadas a arquivos Markdown.
- `agents/documentador.agent.md`: agente especializado para planejar, criar e revisar documentacao.
- `skills/`: workflows sob demanda para tarefas de documentacao.

## Fluxo recomendado

1. Selecione o agente `documentador` para uma tarefa completa ou quando o escopo ainda nao estiver definido.
2. Use `/planejar-documentacao` antes de abrir uma nova trilha ou dividir um tema grande.
3. Use `/escrever-documentacao` para produzir uma pagina seguindo o plano e os padroes locais.
4. Use `/revisar-documentacao` antes de considerar uma pagina pronta.

As skills tambem podem ser carregadas automaticamente pelo Copilot quando a descricao da tarefa for compatível. O uso do comando `/skill` e preferivel quando voce quiser controlar explicitamente o workflow.

## O que e aplicado automaticamente

- `copilot-instructions.md` e carregado em todos os chats do workspace.
- `instructions/documentacao.instructions.md` e aplicado ao trabalhar com arquivos Markdown.
- Os arquivos em `agents/` definem agentes selecionaveis, mas nao trocam o agente ativo sozinhos.
- Os arquivos em `skills/` definem workflows reutilizaveis e sob demanda.

As instrucoes sao orientacao para o agente, nao substituem validacao humana. Conteudo tecnico, custos, versoes e referencias devem ser conferidos quando forem relevantes para a decisao.