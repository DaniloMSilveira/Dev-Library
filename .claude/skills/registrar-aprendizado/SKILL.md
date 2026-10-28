---
name: registrar-aprendizado
description: Guarda em rascunhos/ algo que o usuário aprendeu, para documentar depois, sem escrever a documentação final.
when_to_use: Quando o usuário disser "anota isso", "registra isso", "aprendi X hoje", "guarda esse material", ou colar anotações, links, trechos de código ou resumos de curso para guardar.
argument-hint: "[tema ou material]"
---

# Registrar aprendizado

Captura rápida: transformar o que o usuário trouxe em um rascunho organizado em `rascunhos/`, preservando o conteúdo dele. A documentação final é feita depois, com `/documentar-aprendizado`.

Material passado na invocação (se estiver vazio, use o que o usuário escreveu na conversa): $ARGUMENTS

## Acervo e rascunhos atuais

!`node scripts/catalogo.mjs`

## Procedimento

1. **Procure um rascunho existente do mesmo tema** em "Rascunhos pendentes" acima. Se houver um com `status: novo` ou `em-andamento`, acrescente o material a ele em vez de criar outro.
2. **Crie o rascunho**, se não houver: copie `rascunhos/_modelo.md` para `rascunhos/AAAA-MM-DD-<slug>.md`, com a data de hoje e um slug curto em minúsculas com hífens (ex.: `2026-10-27-kubernetes-probes.md`).
3. **Preencha o frontmatter:** `tema`, `criado-em` e `status: novo`. Em `area`, sugira a área mais provável a partir do acervo (uma existente ou uma nova).
4. **Organize o material nas seções do modelo**, com fidelidade:
   - mantenha as palavras, exemplos e conclusões do usuário; corrija só formatação;
   - não complete o conteúdo com conhecimento seu;
   - se notar um erro provável ou uma lacuna, registre em "Dúvidas e pontos a confirmar" com o prefixo `[agente]`;
   - links e fontes vão em "Fontes"; código vai em blocos com a linguagem indicada.
5. **Não copie material de terceiros.** O rascunho é versionado em um repositório público. Se o material vier de curso, livro, PDF ou artigo, registre um resumo com palavras próprias e a fonte em "Fontes", nunca o texto ou o código original. Anotações escritas pelo próprio usuário seguem a regra de fidelidade acima.
6. **Remova segredos.** Se o material tiver tokens, senhas, chaves ou dados pessoais, substitua por `<removido>` e avise o usuário.

## Saída

Responda com:

- o caminho do rascunho criado ou atualizado;
- a área sugerida e, em uma linha, onde o tema parece se encaixar no acervo;
- a pergunta: "Quer que eu documente agora?". Se sim, siga `/documentar-aprendizado`.

Não crie nem altere arquivos em `estudos/` nesta skill.
