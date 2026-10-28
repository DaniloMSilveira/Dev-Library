# 📚 Dev Library

🌐 **Site:** https://danilomsilveira.github.io/Dev-Library/

Este repositório reúne anotações, exemplos e materiais de estudo organizados por tema. A ideia é servir como um espaço prático para registrar aprendizados em áreas como Terraform, infraestrutura, automação e IA.

## Objetivo

Organizar os conteúdos estudados de forma simples e acessível, permitindo encontrar exemplos e referências com facilidade.

## Como navegar

- A pasta estudos é o ponto central do repositório.
- Cada subpasta representa um tema ou área de estudo.
- Consulte os arquivos Markdown para acompanhar as anotações e os exemplos práticos.
- Explore as pastas de exemplos para ver aplicações reais de cada assunto.

## Estrutura geral

- Terraform: exemplos de infraestrutura e automação.
- IA: documentos e notas sobre conceitos e aprendizados.
- FinOps: documentos e notas sobre boas práticas da cultura finops (cloud e IA)
- Outros temas: conteúdos adicionais que forem sendo adicionados ao longo do estudo.

Este repositório está em constante evolução e pode ser usado como referência pessoal de estudos.

## Site

O conteúdo de `estudos/` é publicado como site no GitHub Pages com [VitePress](https://vitepress.dev/). A cada push na branch `main` que altere `estudos/` ou a configuração do site, o workflow `.github/workflows/pages.yml` gera e publica o site.

- A navegação segue a estrutura de pastas; o primeiro título (`#`) de cada arquivo vira o nome da página no menu.
- A página inicial do site é `estudos/index.md`; a configuração fica em `.vitepress/`.
- Os arquivos de código das pastas `exemplos/` e `examples/` também aparecem no site: cada exemplo ganha uma página com a árvore de arquivos e cada arquivo de código ganha uma página com realce de sintaxe. Essas páginas são geradas em `estudos/codigo/` (ignorada pelo git) a cada build.
- Links relativos para pastas ou arquivos de código abrem essas páginas; notebooks, CSVs e arquivos grandes abrem no GitHub.

Para visualizar localmente (requer Node.js 18 ou superior):

```bash
npm install
npm run docs:dev
```

O site fica disponível em http://localhost:5173/Dev-Library/ e atualiza a cada arquivo salvo. Antes de publicar, rode `npm run verificar`: ele confere a estrutura do acervo e o build, que acusa links quebrados.

## Do aprendizado à documentação com o Claude Code

O repositório tem um fluxo para transformar o que estou aprendendo em documentação publicada usando o [Claude Code](https://code.claude.com):

1. Registro o aprendizado em `rascunhos/`, escrevendo a partir de `rascunhos/_modelo.md` ou colando o material e usando `/registrar-aprendizado`.
2. Uso `/documentar-aprendizado`. O Claude decide onde o tema entra no acervo, pede confirmação para trilhas ou áreas novas, escreve, cria exemplos, revisa com um subagente independente e roda `npm run verificar`.
3. Reviso e faço o commit. O push publica o site.

| Arquivo | Conteúdo |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Instruções gerais do projeto |
| [.claude/memoria.md](.claude/memoria.md) | Convenções, decisões, lacunas e histórico |
| [.claude/rules/guia-de-estilo.md](.claude/rules/guia-de-estilo.md) | Padrão editorial, carregado ao editar `estudos/` |
| [.claude/skills/](.claude/skills/) | Fluxos: registrar, documentar, planejar, escrever e revisar |
| [.claude/agents/revisor-documentacao.md](.claude/agents/revisor-documentacao.md) | Subagente que revisa sem editar |
