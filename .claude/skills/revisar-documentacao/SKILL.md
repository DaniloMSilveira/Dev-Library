---
name: revisar-documentacao
description: Revisa páginas ou trilhas do Dev-Library quanto a clareza, rigor técnico, estrutura, links, exemplos, fontes e consistência editorial, em um subagente independente que só lê.
when_to_use: Antes de considerar uma documentação pronta, ao final de /documentar-aprendizado, ou quando o usuário pedir uma revisão.
argument-hint: "[caminhos das páginas]"
context: fork
agent: revisor-documentacao
background: false
---

# Revisar documentação

Revise: $ARGUMENTS

Se nenhum caminho foi informado, revise as páginas de `estudos/` alteradas em relação ao último commit (`git status --short estudos/`).

## Ordem da revisão

1. Leia `.claude/rules/guia-de-estilo.md`, `.claude/memoria.md` e as páginas vizinhas de cada página revisada.
2. Verifique se o título, o escopo e o nível correspondem ao conteúdo.
3. Procure erros factuais, termos não definidos, generalizações e afirmações sem fonte.
4. Confira a numeração, os links relativos, os nomes de arquivos, os comandos e os exemplos.
5. Procure material de terceiros (guia de estilo, seção 8): trechos copiados, código de curso e nomes de instituições de ensino ou plataformas de cursos, inclusive em URLs, comentários e nomes de recursos dos exemplos.
6. Avalie se a progressão vai da intuição para o mecanismo e a aplicação.
7. Verifique se limites, trade-offs, riscos, custos e versões foram tratados quando relevantes.
8. Confira se tabelas e código são necessários, legíveis e coerentes com o texto.
9. Se a página veio de um rascunho (`rascunhos/`, campo `documentado-em`), confira se ela preserva o que o usuário escreveu e se o que foi acrescentado tem sustentação.
10. Rode `npm run verificar` e inclua o resultado.

## Classificação dos achados

- **Crítico:** pode induzir uma prática insegura, quebrar um exemplo ou o build, ou ensinar algo incorreto.
- **Importante:** reduz a compreensão, a reprodutibilidade ou a confiabilidade.
- **Melhoria:** ajuste editorial, de navegação ou aprofundamento opcional.

## Formato da resposta

Liste primeiro os achados por severidade, com arquivo e seção. Para cada um, explique o impacto e proponha uma correção objetiva. Depois informe os pontos fortes, as verificações feitas e as lacunas que permanecem. Se não houver achados, diga isso claramente e registre os riscos residuais.

Não edite arquivos: quem escreveu aplica as correções.
