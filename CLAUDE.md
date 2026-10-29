# Dev Library

Biblioteca pessoal de estudos e portfólio técnico do Danilo. Registra o que foi aprendido para revisão futura e para consulta de conceitos e exemplos práticos.

Todo Markdown em `estudos/` é publicado como site em https://danilomsilveira.github.io/Dev-Library/ (VitePress, configurado em `.vitepress/`). Escrever uma página é publicá-la.

## Memória do projeto

As convenções do projeto ficam em `.claude/memoria.md`, importada abaixo e versionada no repositório. Registre ali como o projeto funciona hoje, sem histórico, lacunas nem justificativas de decisões, porque o arquivo é público; a memória automática do Claude Code é pessoal e não vai para o git.

@.claude/memoria.md

## Fluxo de estudos

O usuário registra o que aprendeu em `rascunhos/` e os agentes transformam isso em páginas publicadas. Use as skills de `.claude/skills/`:

| Quando | Skill |
|---|---|
| O usuário conta o que aprendeu, cola anotações, links ou código para guardar | `/registrar-aprendizado` |
| Transformar rascunhos ou um tema estudado em documentação publicada | `/documentar-aprendizado` |
| Definir escopo, local e ordem de uma página, trilha ou área nova | `/planejar-documentacao` |
| Escrever ou expandir uma página, README ou exemplo | `/escrever-documentacao` |
| Revisar uma página antes de considerá-la pronta | `/revisar-documentacao` |

- `/revisar-documentacao` roda no subagente `revisor-documentacao` (`.claude/agents/`), em contexto separado e só com leitura, para ser uma revisão independente de quem escreveu.
- O padrão editorial está em `.claude/rules/guia-de-estilo.md`, que é carregado automaticamente ao trabalhar em `estudos/`.
- Antes de decidir onde um tema entra, rode `npm run estudos:catalogo`.

## Estrutura do repositório

| Caminho | Papel |
|---|---|
| `estudos/` | Acervo publicado no site. `estudos/index.md` é a página inicial. |
| `rascunhos/` | Entrada de aprendizados ainda não documentados. Não é publicada no site. |
| `.claude/` | Memória, regras, skills e subagente deste projeto. |
| `scripts/` | Catálogo e verificação estrutural do acervo. |
| `.vitepress/` | Configuração do site. |
| `estudos/codigo/` | Páginas de código geradas pelo site; ignorada pelo git. Não edite. |
| `.github/workflows/pages.yml` | Verifica e publica o site a cada push na `main`. |

## Comandos

| Comando | Uso |
|---|---|
| `npm install` | Instala as dependências (uma vez). |
| `npm run docs:dev` | Site local com recarga automática em http://localhost:5173/Dev-Library/. |
| `npm run estudos:catalogo` | Lista áreas, trilhas, páginas, exemplos e rascunhos pendentes. |
| `npm run verificar` | Verificação completa: estrutura do acervo e build do site (que acusa links quebrados). |

## Regras gerais

- Escreva em português do Brasil, exceto nomes técnicos, comandos, APIs e termos cuja tradução prejudique a precisão.
- Não invente dados, métricas, fontes, resultados de execução nem comportamento de ferramentas.
- Diferencie fatos, interpretações, analogias, recomendações e opiniões.
- Afirmações que dependem de versão, preço, número ou regulamentação precisam de fonte ou data de verificação.
- Nunca inclua segredos, credenciais, tokens ou dados pessoais em páginas, exemplos ou rascunhos. Exemplos usam `.env.example`.
- Nunca inclua material de cursos nem nomes de instituições de ensino ou plataformas de cursos, em nenhum arquivo nem em mensagens de commit (guia de estilo, seção 8).
- Prefira mudanças pequenas e locais. Não misture reorganização ampla com conteúdo novo, e não reorganize estruturas legadas sem pedido explícito.
- Não remova alterações existentes de outras pessoas ou sessões.
- Não faça commit nem push sem pedido explícito do usuário.

## Antes de concluir

1. `npm run verificar` precisa passar. Se não for possível rodá-lo, diga isso.
2. Atualize `.claude/memoria.md` se uma convenção mudou.
3. Resuma os arquivos alterados, as validações executadas e o que ainda depende de revisão humana.
