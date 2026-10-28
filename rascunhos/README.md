# Rascunhos

Caixa de entrada do que você está aprendendo e ainda não virou documentação. Esta pasta **não é publicada no site**, mas é versionada no git. Como o repositório é público, não coloque aqui nada que não possa ficar público.

## Como usar

1. **Registre o aprendizado** de um destes jeitos:
   - copie `_modelo.md` para `AAAA-MM-DD-tema.md` e escreva com as suas palavras; ou
   - cole o material no Claude Code e use `/registrar-aprendizado` (ou peça *"registra isso"*).
2. **Peça a documentação** com `/documentar-aprendizado` (todos os pendentes) ou `/documentar-aprendizado rascunhos/<arquivo>.md`. O Claude:
   - decide se o tema entra em uma página existente, em uma trilha, em uma trilha nova ou em uma área nova;
   - pede a sua confirmação antes de criar trilhas ou áreas;
   - escreve, cria o exemplo prático quando fizer sentido, revisa com um subagente independente e roda `npm run verificar`.
3. **Revise e faça o commit.** O rascunho fica com `status: documentado` e a lista das páginas geradas.

Para ver o que está pendente: `npm run estudos:catalogo`.

## Status

| Status | Significado |
|---|---|
| `novo` | Registrado, ainda não documentado. |
| `em-andamento` | O Claude está documentando. |
| `documentado` | Virou página; `documentado-em` lista os arquivos. |
