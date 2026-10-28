---
name: escrever-documentacao
description: Cria ou expande uma página de estudo, uma trilha, um README de área ou de exemplo, ou um guia prático no Dev-Library, partindo dos modelos do projeto.
argument-hint: "[página ou tema]"
---

# Escrever documentação

Alvo: $ARGUMENTS

## Preparação

- Leia `.claude/rules/guia-de-estilo.md` (se ainda não estiver no contexto) e as páginas vizinhas, principalmente a anterior e a seguinte na trilha.
- Confirme o caminho, o nome do arquivo e o número na trilha de acordo com a estrutura canônica da memória do projeto.
- Separe os fatos confirmados dos pontos que exigem fonte ou teste.

## Modelos

Comece pelo modelo adequado em `${CLAUDE_SKILL_DIR}/modelos/` e remova os comentários de orientação ao terminar:

| Modelo | Uso |
|---|---|
| `pagina-conceitual.md` | Página de trilha que explica um conceito |
| `guia-pratico.md` | Passo a passo com comandos e resultado esperado |
| `readme-area.md` | Visão geral de uma área nova |
| `exemplo-readme.md` | README de uma pasta de exemplo |

Se a trilha já tiver um padrão próprio (seções numeradas, ordem das seções), siga a trilha em vez do modelo.

## Regras de escrita

- Siga o guia de estilo, inclusive as regras impostas pelo site (seção 6).
- Use seções numeradas (`## N.1`) quando a trilha usar esse padrão.
- Marque exemplos ilustrativos e não invente resultados de comandos.
- Ao documentar ferramentas ou automação, inclua limites, permissões, custo e como validar.
- Quando a página vier de um rascunho, preserve as conclusões e os exemplos do usuário; o que você acrescentar precisa ser correto e, quando sensível a mudança, ter fonte.

## Verificação

Depois de editar:

- confira links relativos, numeração, blocos de código, nomes reais de arquivos e a coerência com a página anterior e a seguinte;
- rode `npm run verificar`.

Relate o que foi criado, o que foi validado e o que ainda depende de verificação externa.
