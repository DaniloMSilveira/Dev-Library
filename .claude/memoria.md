# Memória do projeto

Convenções do Dev Library que não estão evidentes no código. Atualize este arquivo quando uma convenção mudar; o acervo atual é listado por `npm run estudos:catalogo` e não deve ser copiado para cá.

Este arquivo é público. Registre apenas como o projeto funciona hoje: nada de histórico de mudanças, lacunas, pendências ou justificativas de decisões passadas.

## Propósito

O Dev Library registra aprendizados técnicos para consulta futura e funciona como portfólio pessoal. O dono escreve rascunhos do que aprendeu em `rascunhos/` e os agentes transformam esse material em documentação publicada em `estudos/`.

## Estrutura canônica para conteúdo novo

| Tipo | Local | Observações |
|---|---|---|
| Área | `estudos/<Area>/` | Nome legível, no estilo das existentes (`FinOps`, `IA`, `Terraform`). Precisa de card em `estudos/index.md` e, de preferência, um `README.md`. |
| Trilha | `estudos/<Area>/docs/<trilha>/N-slug.md` | Pasta em minúsculas com hífens. Páginas numeradas a partir de 1, título `# N. Título`. |
| Página avulsa | `estudos/<Area>/docs/<slug>.md` | Para temas que cabem em uma página. |
| Exemplo | `estudos/<Area>/docs/<trilha>/exemplos/<nome>/` | Um README por exemplo. Código executável, `.env.example` no lugar de segredos. |

Estruturas legadas, que não devem ser reorganizadas sem pedido explícito:

- `estudos/FinOps/finops-cloud-ia.md` fica na raiz da área, sem `docs/`.
- `estudos/Terraform/` guarda os exemplos em `Terraform/examples/<nome>/`, fora da pasta `docs/`, e os guias não são numerados.
- `IA/docs/spec-driven-development/exemplos/` agrupa os exemplos por abordagem (`speckit/`, `vanilla/`) em vez de um exemplo por pasta.

Quando uma trilha crescer, atualize o README da área ou crie um índice antes de duplicar navegação em várias páginas.

## Padrão editorial observado

- **IA:** trilhas numeradas, seções numeradas (`## 1.1`), definições progressivas, exemplos de domínio e tabelas. Encerramento e fontes são opcionais.
- **FinOps:** capítulos extensos, listas, tabelas e exemplos de custos, no formato de guia de referência.
- **Terraform:** explicação conceitual, árvore de arquivos, pré-requisitos, comandos, workflow e análise dos arquivos do exemplo.

## Site

- Publicado em https://danilomsilveira.github.io/Dev-Library/ pelo workflow `.github/workflows/pages.yml` a cada push na `main` que altere o site ou o acervo.
- O menu é gerado pela estrutura de pastas (`.vitepress/navigation.mts`). A pasta `docs/` não aparece como nível no menu.
- Os exemplos ganham páginas de código e de árvore de arquivos, geradas por `.vitepress/codigo.mts` em `estudos/codigo/`. Não crie uma área chamada `codigo`.
- Pastas `exemplos/<nome>/data/` ficam fora do site.
- O VitePress ignora pastas ocultas: Markdown dentro delas (ex.: `.claude/` dos exemplos de harness) não vira página e é exibido como código pelo `codigo.mts`, inclusive nos links relativos dos READMEs.
- Math e Mermaid não estão habilitados (exigiriam plugins). Para math, `R$` nos textos de FinOps seria confundido com delimitador.

## Agentes de IA

- As instruções são escritas apenas para o Claude Code: `CLAUDE.md`, `.claude/memoria.md` (importada pelo `CLAUDE.md`), `.claude/rules/`, `.claude/skills/` e `.claude/agents/`.
- `.claude/rules/guia-de-estilo.md` tem `paths: estudos/**/*.md` e só entra no contexto quando o Claude trabalha nessas páginas.
- `/documentar-aprendizado` e `/registrar-aprendizado` injetam a saída de `node scripts/catalogo.mjs` ao serem invocadas. O comando é somente leitura; se o Claude Code pedir permissão para ele, pode ser liberado permanentemente.
- `/revisar-documentacao` roda no subagente `revisor-documentacao` (`context: fork`), só com leitura.
- Os exemplos em `estudos/IA/docs/harness-engineering/exemplos/` têm `CLAUDE.md`, `.claude/rules/` e skills de um projeto fictício. Para não entrarem nas sessões deste repositório, o `.claude/settings.json` os exclui com `claudeMdExcludes` e nega as skills deles (`Skill(nova-feature)`, `Skill(revisar)`, `Skill(registrar-incidente)`). Ao criar exemplos novos com arquivos do Claude Code, atualize essas listas. O fluxo de documentar fica na conversa principal porque subagentes não conseguem fazer perguntas ao usuário.
- Rascunhos são do usuário: o agente organiza, mas não reescreve o sentido nem apaga. Depois de documentado, o rascunho fica com `status: documentado` como registro de origem.
