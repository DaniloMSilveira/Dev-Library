# 2. Contexto, janela de contexto e recuperação de informação

Gerir contexto de forma eficiente é essencial para obter respostas melhores sem desperdiçar tokens ou reduzir a precisão do modelo.

## 2.1 Janela de contexto

A janela de contexto é a quantidade de informação que um modelo consegue processar em uma interação.

Ela limita:

- quanto texto pode ser enviado;
- quanto histórico pode ser mantido;
- quanto conteúdo pode ser analisado de uma vez.

Se o contexto for muito grande, pode haver custo maior e pior aproveitamento do modelo. Se for muito pequeno, a resposta pode ficar incompleta.

## 2.2 Por que isso é importante?

Modelos diferentes têm limites diferentes. Alguns aceitam poucos tokens, outros aceitam milhares ou até milhões.

Isso significa que é preciso:

- filtrar o que é realmente relevante;
- evitar excesso de informações redundantes;
- resumir ou compactar partes do contexto quando necessário.

## 2.3 Estratégias para lidar com limites de contexto

### Chunking

Chunking é a prática de dividir textos longos em partes menores e mais coerentes.

Exemplo:

- um documento grande pode ser dividido em capítulos ou seções;
- cada parte pode ser indexada e recuperada separadamente.

Isso melhora a organização e ajuda na busca de informações relevantes.

### Ranking de relevância

Nem tudo que existe no contexto precisa ser enviado ao modelo. Em vez disso, é possível priorizar os trechos mais importantes.

Exemplo:

- uma pergunta sobre políticas de reembolso pode recuperar apenas trechos relacionados a esse tema.

### Resumo de histórico

Em conversas longas, o histórico pode ser condensado em uma versão mais curta e objetiva.

Isso mantém a continuidade sem sobrecarregar o modelo.

## 2.4 Recuperação de informação

Em muitos sistemas, o contexto é montado a partir de documentos externos. Isso é comum em arquiteturas como RAG.

O fluxo costuma ser:

1. o usuário faz uma pergunta;
2. o sistema busca documentos relevantes;
3. esses documentos são enviados ao modelo;
4. o modelo responde com base no contexto recuperado.

## 2.5 Exemplo prático

Imagine um chatbot corporativo que responde dúvidas sobre procedimentos internos.

Em vez de enviar todo o manual para o modelo, o sistema pode:

- localizar apenas as páginas relevantes;
- resumir o conteúdo;
- incluir só o trecho mais útil na resposta final.

## 2.6 Resumo

A janela de contexto define o limite do que o modelo consegue considerar de uma vez. A recuperação de informação ajuda a selecionar os trechos mais úteis, tornando o contexto mais eficiente e mais preciso.
