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

## Padrao editorial observado

- Titulos usam Markdown e, nas trilhas de IA, o prefixo numerico identifica a ordem do assunto.
- As paginas de IA usam secoes numeradas, definicoes progressivas, exemplos de dominio, tabelas e formulas em KaTeX quando necessario. Secoes de encerramento e fontes sao opcionais e dependem do objetivo da pagina.
- FinOps usa capitulos extensos, listas, tabelas, exemplos de custos e uma abordagem de guia de referencia.
- Terraform combina explicacao conceitual, arvore de arquivos, pre-requisitos, comandos, workflow e analise de arquivos.
- O nivel esperado e introdutorio a intermediario, com aprofundamento tecnico suficiente para conectar teoria, implementacao e operacao.

## Convencoes de organizacao

- Documentacoes ficam em `estudos/<area>/docs/`.
- Exemplos de codigo ficam em `estudos/<area>/examples/` quando houver mais de um arquivo ou uma estrutura executavel.
- Use nomes em minusculas, com palavras separadas por hifens e prefixo numerico apenas quando a pasta representar uma trilha ordenada.
- Links internos devem ser relativos e apontar para arquivos existentes.
- READMEs de area devem explicar navegacao, pre-requisitos e exemplos relevantes.

## Decisoes para futuras alteracoes

- Priorizar clareza e rastreabilidade em vez de densidade artificial.
- Usar analogias para formar intuicao, sem substituir definicoes tecnicas.
- Preferir exemplos pequenos e seguros; indicar explicitamente o que e ilustrativo.
- Registrar fontes externas para fatos que mudam com o tempo.
- Manter uma pagina focada em uma pergunta ou conjunto coeso de conceitos.
- Quando uma trilha crescer, atualizar o README da area ou criar um indice antes de duplicar navegacao em varias paginas.
- Separar conceito, processo, exemplo e operacao quando isso melhorar a revisao; manter escopo, limites e evidencias rastreaveis em conteudos praticos.

## Lacunas conhecidas

- Ainda nao ha README proprio para `estudos/IA/` ou `estudos/FinOps/`.
- As trilhas de IA podem ganhar indices de navegacao e fontes externas quando isso trouxer valor ao conteudo.
- Alguns exemplos Terraform e textos existentes podem conter nomes, versoes ou descricoes que merecem revisao antes de serem tratados como normativos.
- Nao existe pipeline automatizado de validacao de Markdown, links ou exemplos.