---
name: revisar-documentacao
description: "Use quando for necessario revisar uma documentacao do Dev-Library quanto a clareza, rigor tecnico, estrutura, links, exemplos, fontes e consistencia editorial."
---

# Revisar documentacao

## Ordem da revisao

1. Compare a pagina com a memoria persistida e com os documentos vizinhos.
2. Verifique se o titulo, o escopo e o nivel correspondem ao conteudo.
3. Procure erros factuais, termos indefinidos, generalizacoes e afirmacoes sem fonte.
4. Confira numeracao, links relativos, nomes de arquivos, comandos e exemplos.
5. Avalie se a progressao vai de intuicao para mecanismo e aplicacao.
6. Verifique se limites, trade-offs, riscos, custos e versoes foram tratados quando relevantes.
7. Confira se formulas, tabelas e codigo sao necessarios, legiveis e coerentes.

## Classificacao dos achados

- **Critico**: pode induzir uma pratica insegura, quebrar um exemplo ou ensinar algo incorreto.
- **Importante**: reduz a compreensao, a reprodutibilidade ou a confiabilidade.
- **Melhoria**: ajuste editorial, navegacao ou aprofundamento opcional.

## Formato da resposta

Liste primeiro os achados por severidade, com arquivo e referencia de secao. Para cada um, explique o impacto e proponha uma correcao objetiva. Depois informe os pontos fortes, os testes feitos e as lacunas que permanecem. Se nao houver achados, diga isso claramente e registre os riscos residuais.