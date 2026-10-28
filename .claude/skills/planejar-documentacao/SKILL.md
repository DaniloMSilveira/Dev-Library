---
name: planejar-documentacao
description: Define escopo, local, ordem e estrutura de uma nova página, trilha ou área de estudos no Dev-Library, sem escrever as páginas.
when_to_use: Antes de criar uma trilha ou área nova, quando um tema for amplo ou ambíguo, ou antes de renumerar ou reorganizar uma trilha existente.
argument-hint: "[tema]"
---

# Planejar documentação

Transformar um tema em um plano coerente com o acervo, sem criar páginas redundantes nem pular pré-requisitos. Esta etapa não escreve páginas completas, a menos que o usuário peça.

Tema: $ARGUMENTS

## Procedimento

1. Consulte a estrutura canônica e os legados na memória do projeto e leia o README da área, se existir.
2. Rode `npm run estudos:catalogo` e identifique o que já foi explicado sobre o tema e sobre os pré-requisitos dele.
3. Defina o público, o nível, a pergunta central e o resultado esperado.
4. Separe fundamentos, mecanismos, aplicações, trade-offs e temas avançados.
5. Decida o formato: seção em página existente, página avulsa, trilha numerada ou página teórica acompanhada de exemplo.
6. Identifique fontes, comandos, dependências e riscos de desatualização.
7. Aponte as lacunas que exigem confirmação do usuário antes da escrita.

## Saída obrigatória

Um plano curto contendo:

- objetivo e limite do escopo (o que fica de fora);
- caminho e nome de cada arquivo, seguindo a estrutura canônica da memória;
- sequência de páginas e, em cada uma, as seções principais;
- conceitos que pedem analogia, tabela, código ou exemplo prático;
- impactos no acervo: renumerações, links a corrigir, card na página inicial, README da área;
- fontes e validações necessárias;
- perguntas em aberto e o critério de pronto.
