---
name: documentacao-dev-library
description: "Aplica o padrao editorial do Dev-Library ao criar ou revisar documentacao Markdown, READMEs, trilhas de estudo e guias tecnicos."
applyTo: "**/*.md"
---

# Instrucao para documentacao

Ao trabalhar em um Markdown do Dev-Library:

- identifique primeiro a area, a trilha e o papel da pagina;
- preserve a numeracao e o vocabulario das paginas vizinhas;
- comece com uma definicao direta e explique por que o assunto importa;
- avance do simples para o tecnico, separando conceito, funcionamento, exemplo e limites;
- use analogias curtas para intuicao e deixe claro onde a analogia deixa de valer;
- use tabelas para comparacoes e listas para propriedades, etapas ou verificacoes;
- use blocos de codigo completos o bastante para serem entendidos, com linguagem indicada;
- explique cada exemplo pratico: contexto, entradas, saida esperada, riscos e limpeza;
- use uma secao de encerramento somente quando ela trouxer valor para a pagina; ela nao e obrigatoria;
- inclua fontes externas somente quando forem necessarias para sustentar afirmacoes, citacoes, numeros, precos, versoes ou regras legais;
- revise links, acentuacao, numeracao, nomes de arquivos e coerencia entre texto e codigo.

Para documentacoes praticas ou que descrevam mudancas tecnicas:

- registre escopo, limites, dependencias e criterios de aceite quando forem relevantes;
- relacione arquivos, comandos e evidencias de validacao sem inventar caminhos ou resultados;
- separe documentos longos em partes coesas e conecte-as por links relativos;
- mantenha exemplos, instrucoes e estrutura real do repositorio coerentes;
- ao descrever ferramentas ou comandos, informe quando versoes e requisitos precisam ser confirmados na fonte oficial;
- quando houver automacao, defina limites de alteracao, aprovacao e validacao executavel.

Nao transforme uma pagina de estudo em publicidade, nao use afirmacoes absolutas sem evidencia e nao apresente uma analogia como se fosse uma especificacao tecnica.