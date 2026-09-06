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
