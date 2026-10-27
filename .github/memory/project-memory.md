# Memoria persistida do Dev-Library

## Proposito

O Dev-Library registra aprendizados tecnicos para consulta futura e funciona como portfolio pessoal. A documentacao deve ensinar o assunto e deixar claro como os conceitos se conectam a sistemas e praticas reais.

## Mapa atual

| Area | Local | Papel |
|---|---|---|
| FinOps | `estudos/FinOps/` | Guia conceitual sobre gestao de custos em nuvem e projetos de IA. |
| IA | `estudos/IA/docs/` | Trilhas de Machine Learning e Context Engineering, organizadas por topicos numerados. |
| Terraform | `estudos/Terraform/docs/` | Guias de Terraform, Ansible e AWS. |
| Terraform | `estudos/Terraform/examples/` | Exemplos praticos de AWS EC2, ECS e EKS, separados por infraestrutura e ambiente. |
| Site | `.vitepress/`, `estudos/index.md`, `.github/workflows/pages.yml` | Publica `estudos/` no GitHub Pages com VitePress. |

## Padrao editorial observado

- Titulos usam Markdown e, nas trilhas de IA, o prefixo numerico identifica a ordem do assunto.
- As paginas de IA usam secoes numeradas, definicoes progressivas, exemplos de dominio, tabelas e formulas quando necessario (o site ainda nao renderiza math; ver Site publicado). Secoes de encerramento e fontes sao opcionais e dependem do objetivo da pagina.
- FinOps usa capitulos extensos, listas, tabelas, exemplos de custos e uma abordagem de guia de referencia.
- Terraform combina explicacao conceitual, arvore de arquivos, pre-requisitos, comandos, workflow e analise de arquivos.
- O nivel esperado e introdutorio a intermediario, com aprofundamento tecnico suficiente para conectar teoria, implementacao e operacao.

## Convencoes de organizacao

- Documentacoes ficam em `estudos/<area>/docs/`.
- Exemplos de codigo ficam em `estudos/<area>/examples/` quando houver mais de um arquivo ou uma estrutura executavel.
- Use nomes em minusculas, com palavras separadas por hifens e prefixo numerico apenas quando a pasta representar uma trilha ordenada.
- Links internos devem ser relativos e apontar para arquivos existentes.
- READMEs de area devem explicar navegacao, pre-requisitos e exemplos relevantes.

## Site publicado

- Todo Markdown dentro de `estudos/` vira pagina em https://danilomsilveira.github.io/Dev-Library/; o menu e gerado pela estrutura de pastas em `.vitepress/navigation.mts` (a pasta `docs/` nao aparece como nivel no menu).
- O primeiro titulo `#` de cada arquivo e o nome da pagina no menu; mantenha um unico H1 por arquivo.
- Ao criar uma area ou trilha nova, adicione um card em `features` de `estudos/index.md`.
- Cada subpasta de `exemplos/` ou `examples/` com codigo vira um exemplo no site: uma pagina com a arvore de arquivos e uma pagina por arquivo de codigo, geradas por `.vitepress/codigo.mts` em `estudos/codigo/` (ignorada pelo git; nao edite nem crie uma area chamada `codigo`).
- So arquivos versionados ou nao ignorados pelo git entram no site; notebooks, CSVs e arquivos acima de 100 KB abrem no GitHub.
- Links relativos para pastas ou arquivos de codigo apontam para essas paginas; links para `.md` inexistentes quebram o build (`npm run docs:build`).
- Arquivos em `exemplos/*/data/` ficam fora do site.
- Formulas math e diagramas Mermaid nao estao habilitados; exigiriam plugins no VitePress. Para math, cuidado com `R$` em valores, que o parser confundiria com delimitadores.
- Texto fora de blocos de codigo e interpretado como template Vue: `{{ }}` e tags HTML soltas podem quebrar o build; coloque-os entre crases.
