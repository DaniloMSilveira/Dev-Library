# Instrucoes do Dev-Library

## Identidade do repositorio

O Dev-Library e uma biblioteca pessoal de estudos e um portfolio tecnico. Seu conteudo deve ser util para revisao futura, consulta de conceitos e entendimento de exemplos praticos.

## Uso dos agentes

- Para criar, organizar ou revisar documentacao, selecione manualmente o agente `documentador` no Chat do Copilot quando iniciar um novo chat.
- O agente padrao tambem recebe estas instrucoes, mas nao assume automaticamente o perfil nem o fluxo completo do `documentador`.
- Use as skills `planejar-documentacao`, `escrever-documentacao` e `revisar-documentacao` quando a tarefa corresponder a esses workflows; elas podem ser chamadas com `/nome-da-skill`.
- Nao considere a selecao do agente ou a execucao de uma skill como substituta da validacao humana.

Antes de criar ou alterar uma documentacao, leia:

- `.github/memory/project-memory.md` para entender o mapa e as decisoes do repositorio;
- a documentacao vizinha do mesmo assunto para preservar continuidade;
- os arquivos de exemplo relacionados, quando a pagina explicar codigo ou infraestrutura.

## Regras gerais

- Responda e escreva em portugues, exceto nomes tecnicos, comandos, APIs e termos cuja traducao prejudique a precisao.
- Preserve a organizacao existente em `estudos/<area>/docs/` e `estudos/<area>/examples/`.
- Prefira mudancas pequenas, locais e coerentes com o historico do repositorio.
- Nao invente dados, metricas, fontes, resultados de execucao ou comportamento de ferramentas.
- Diferencie fatos, interpretacoes, analogias, recomendacoes e opinioes.
- Ao usar uma afirmacao dependente de versao, custo, numero ou regulamentacao, informe a data ou indique que ela precisa ser verificada.
- Nao exponha segredos, credenciais, chaves privadas, tokens ou valores sensiveis nos exemplos.
- Nao misture uma reorganizacao ampla com a criacao de um novo topico sem necessidade.

## Padrao de uma boa documentacao

Uma pagina nova deve, quando fizer sentido:

1. apresentar o conceito e o problema que ele resolve;
2. explicar a intuicao com uma analogia ou exemplo concreto;
3. definir os termos tecnicos e suas relacoes;
4. mostrar um exemplo pratico, fluxo, tabela ou trecho de codigo;
5. discutir limites, trade-offs, riscos e quando usar;
6. fechar com uma secao de encerramento apenas quando ela ajudar a consolidar o conteudo;
7. incluir fontes externas apenas quando forem necessarias para sustentar afirmacoes, versoes, numeros ou decisoes.

Para conteudo pratico, inclua pre-requisitos, estrutura de arquivos, comandos seguros, resultado esperado e limpeza ou reversao quando aplicavel.

## Organizacao de conteudo tecnico

- Divida uma documentacao extensa em paginas coesas, preservando a ordem e a navegacao da trilha.
- Separe conceito, processo, exemplo e referencia operacional quando essa divisao reduzir repeticao.
- Mantenha exemplos executaveis em `estudos/<area>/examples/` quando envolverem mais de um arquivo.
- Registre escopo, limites, dependencias e criterios verificaveis em guias praticos quando forem relevantes.
- Mantenha documentos, exemplos e comandos coerentes entre si quando uma alteracao afetar mais de um artefato.
- Nao trate comandos, versoes ou comportamentos de ferramentas como permanentes sem verificacao na documentacao oficial.

## Qualidade antes de concluir

- Verifique titulos, numeracao, ortografia e links relativos.
- Confirme que nomes de arquivos e comandos correspondem ao repositorio.
- Valide exemplos executaveis com a ferramenta apropriada quando isso for possivel.
- Nao remova alteracoes existentes de outros autores.
- Ao terminar, resuma os arquivos alterados, as validacoes executadas e qualquer lacuna conhecida.