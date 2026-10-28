---
name: documentar-aprendizado
description: Transforma rascunhos de rascunhos/ ou um tema estudado em documentação publicada em estudos/, conduzindo o fluxo completo de classificar, planejar, escrever, criar exemplo, revisar, validar e registrar.
when_to_use: Quando o usuário pedir "documenta os rascunhos", "documenta o rascunho de X", "processa o que aprendi" ou "cria a documentação de X".
argument-hint: "[caminho do rascunho ou tema]"
---

# Documentar aprendizado

Fluxo de ponta a ponta que leva um aprendizado do rascunho até uma página publicada. Siga as etapas em ordem. As etapas 7 e 8 nunca são opcionais.

Rascunho ou tema indicado (se vazio, use os rascunhos pendentes abaixo): $ARGUMENTS

## Acervo e rascunhos atuais

!`node scripts/catalogo.mjs`

## 1. Reunir o material

- Identifique o rascunho:
  - se o usuário indicou um, use-o;
  - se pediu "os rascunhos pendentes", processe um tema por vez, na ordem da lista acima;
  - se trouxe o tema direto no chat, registre-o antes com `/registrar-aprendizado`, para manter o registro de origem.
- Leia o rascunho inteiro e as fontes citadas que estiverem acessíveis.
- Mude o rascunho para `status: em-andamento`.

## 2. Classificar

Decida o destino com base no acervo e registre o motivo:

| Situação | Destino |
|---|---|
| Aprofunda ou corrige uma página existente | Nova seção na página existente |
| Tema novo dentro de uma trilha existente | Nova página numerada no fim da trilha |
| Tema amplo, novo dentro de uma área | Nova trilha em `docs/<trilha>/` |
| Tema de uma área que ainda não existe | Nova área em `estudos/<Area>/` |

Inserir uma página no meio de uma trilha exige renumerar as seguintes e corrigir os links que apontam para elas. Faça isso só com confirmação do usuário.

## 3. Planejar

- **Seção nova ou página nova em trilha existente:** faça um plano curto e siga em frente.
- **Trilha nova, área nova, renumeração ou rascunho ambíguo:** aplique `/planejar-documentacao`, apresente o plano ao usuário e espere a confirmação antes de escrever.

## 4. Escrever

Aplique `/escrever-documentacao`, partindo dos modelos dela.

- O rascunho é a base: a experiência, os exemplos e as conclusões do usuário têm prioridade.
- O que você acrescentar para completar a explicação precisa ser correto e, quando depender de versão, preço, número ou comportamento de ferramenta, ter fonte.
- Resolva os pontos marcados em "Dúvidas e pontos a confirmar" ou leve-os ao relatório final.
- Escreva com palavras próprias, sem trechos ou código de cursos, livros, PDFs ou artigos (guia de estilo, seção 8).

## 5. Criar um exemplo prático

Quando o rascunho tiver código ou o tema pedir prática:

- crie `docs/<trilha>/exemplos/<nome>/` com um README baseado em `.claude/skills/escrever-documentacao/modelos/exemplo-readme.md`;
- use `.env.example` com valores fictícios, nunca segredos;
- rode o exemplo ou os testes quando for possível; se não for, declare no README e no relatório que ele não foi executado.

## 6. Integrar ao acervo

- Adicione links "veja também" entre páginas relacionadas quando ajudarem. Anterior e próxima já são gerados pelo site.
- **Área nova:** crie o `README.md` da área (modelo `readme-area.md`) e um card em `features` de `estudos/index.md`.
- **Trilha nova:** cite-a no README da área, se ele existir.

## 7. Revisar e validar

- Rode `/revisar-documentacao` passando os caminhos das páginas criadas ou alteradas. A revisão roda em um subagente independente; corrija todos os achados críticos e importantes que ela trouxer.
- Rode `npm run verificar` e corrija até passar.

## 8. Registrar

- No rascunho, defina `status: documentado` e preencha `documentado-em` com os caminhos das páginas. Não apague o rascunho.
- Atualize `.claude/memoria.md` somente se surgiu uma convenção, decisão ou lacuna nova, e registre-a no histórico com a data.

## Relatório final

Informe ao usuário:

- as páginas e os exemplos criados ou alterados, com links;
- a classificação escolhida e o motivo;
- as validações executadas e o resultado;
- o que você acrescentou além do rascunho e merece revisão humana;
- as dúvidas que ficaram em aberto.

Não faça commit nem push sem pedido explícito.
