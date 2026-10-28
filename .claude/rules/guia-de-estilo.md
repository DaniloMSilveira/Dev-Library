---
paths:
  - "estudos/**/*.md"
---

# Guia de estilo da documentação

Padrão editorial do Dev Library. Vale para toda página em `estudos/`, inclusive READMEs de área e de exemplos. Os procedimentos (como planejar, escrever e revisar) ficam nas skills em `.claude/skills/`; este guia define como o resultado deve ser.

## 1. Objetivo de uma página

Uma pessoa com os pré-requisitos declarados deve conseguir entender o conceito, saber por que ele importa e qual é o próximo passo. A documentação ensina o assunto e mostra como ele se conecta a sistemas e práticas reais.

O nível esperado é introdutório a intermediário, com aprofundamento técnico suficiente para ligar teoria, implementação e operação.

## 2. Estrutura de uma página

### Página conceitual

Quando fizer sentido, nesta ordem:

1. título claro e contextualizado;
2. introdução com o problema que o conceito resolve e o que a pessoa vai entender ao final;
3. definição dos termos técnicos e de como se relacionam;
4. funcionamento, do simples para o técnico;
5. analogia ou exemplo concreto para formar intuição;
6. tabela, fluxo ou código quando ajudarem a comparar ou aplicar;
7. limites, trade-offs, riscos e quando usar;
8. encerramento e fontes, somente quando ajudarem o objetivo da página.

### Página prática ou guia

Acrescente: objetivo e escopo, pré-requisitos, estrutura de arquivos, comandos seguros com o resultado esperado, verificação, custos e riscos, e limpeza ou reversão.

Os modelos ficam em `.claude/skills/escrever-documentacao/modelos/`.

## 3. Escrita

- Português do Brasil claro, mantendo os termos técnicos consagrados.
- Comece com uma definição direta e explique por que o assunto importa.
- Explique uma ideia antes de introduzir sua sigla ou abreviação.
- Use analogias curtas para intuição, deixe claro onde a analogia deixa de valer e nunca apresente uma analogia como especificação técnica.
- Não esconda complexidade relevante atrás de analogias nem use afirmações absolutas sem evidência.
- Mantenha cada página focada em uma pergunta ou em um conjunto coeso de conceitos.
- Não transforme uma página de estudo em publicidade de ferramenta.

## 4. Elementos

- **Tabelas** para comparações; **listas** para propriedades, etapas ou verificações.
- **Blocos de código** completos o bastante para serem entendidos, sempre com a linguagem indicada (` ```python `, ` ```bash `, ` ```hcl `).
- **Exemplos ilustrativos** marcados como tal. Nunca invente a saída de um comando: mostre a saída real ou descreva o resultado esperado.
- **Fontes externas** somente para sustentar citações, números, preços, versões, regras legais ou comportamento de ferramentas. Para fatos que mudam com o tempo, registre a data de verificação.

## 5. Organização do acervo

- Uma trilha é uma sequência numerada de páginas sobre um tema amplo. Divida documentações extensas em páginas coesas e conecte-as por links relativos.
- Separe conceito, processo, exemplo e referência operacional quando isso reduzir repetição.
- Exemplos com mais de um arquivo ou executáveis vão para uma pasta de exemplo com README próprio (ver a estrutura canônica em `.claude/memoria.md`).
- Mantenha documentos, exemplos e comandos coerentes entre si quando uma alteração afetar mais de um artefato.

## 6. Regras impostas pelo site

O VitePress gera o site a partir de `estudos/`. Estas regras são verificadas por `npm run verificar`:

| Regra | Motivo |
|---|---|
| Exatamente um título `#` por página (fora de pastas de exemplos). | O `#` vira o nome da página no menu. |
| Trilhas numeradas de 1 a n, sem buracos, com arquivo `N-slug.md` e título `# N. Título`. | O menu e os botões anterior/próxima seguem a numeração. |
| `{{` e `}}` só dentro de código (crases ou bloco). | Fora de código, o VitePress interpreta como template Vue e o build quebra. |
| Links internos relativos apontando para o arquivo `.md`. | Links quebrados fazem o build falhar. |
| Cada área de `estudos/` com um card em `estudos/index.md`. | É a porta de entrada do site. |

Também vale saber:

- Links relativos para pastas ou arquivos de código de exemplos abrem a página de código gerada pelo site; notebooks, CSVs e arquivos acima de 100 KB abrem no GitHub.
- Fórmulas (math) e diagramas Mermaid **não** estão habilitados. Prefira tabelas, listas ou blocos de texto. Para valores em reais, `R$` é seguro enquanto math estiver desligado.
- Seções numeradas (`## 1.1`, `## 1.2`) são o padrão das trilhas de IA. Siga o padrão da trilha em que a página entra.

## 7. Infraestrutura, custos e segurança

- Exemplos de infraestrutura deixam claros custo, permissões necessárias, riscos e como desfazer.
- Nunca inclua segredos, chaves, tokens ou dados pessoais. Use `.env.example` com valores fictícios.
- Comandos destrutivos ou que geram custo precisam de aviso explícito antes do bloco de código.

## 8. Direitos autorais

O repositório é público. Todo conteúdo precisa ser próprio:

- Escreva sempre com palavras próprias. Não reproduza trechos de cursos, livros, artigos, PDFs ou documentação, nem como citação entre aspas.
- Material de cursos (código, notebooks, slides, apostilas, projetos prontos) não entra no repositório. Exemplos práticos são sempre implementações próprias.
- Datasets de terceiros não são versionados: documente o link de download e a licença declarada pela fonte.
- Conceitos e fatos podem ser explicados livremente. Estatísticas e números de terceiros só entram com link para uma fonte pública; sem fonte, ficam fora.
- Dar crédito é permitido e recomendado: cite pelo nome a organização ou o autor de um framework, sem copiar o texto dele.

`npm run verificar` acusa marcas de material de curso como erro e citações em bloco entre aspas como aviso.
