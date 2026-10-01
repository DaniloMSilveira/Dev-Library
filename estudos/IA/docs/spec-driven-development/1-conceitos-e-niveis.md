# 1. Conceitos e níveis de Spec-Driven Development

Spec-Driven Development (SDD), ou desenvolvimento orientado por especificações, é uma abordagem em que especificações versionadas, revisáveis e verificáveis orientam a implementação e continuam sendo consultadas durante a evolução da funcionalidade.

O ponto central não é produzir um documento antes do código. É transformar decisões importantes em artefatos que reduzam ambiguidades, controlem escopo e permitam comparar o comportamento esperado com o comportamento implementado.

## 1.1 Por que SDD ganhou importância com IA?

Ferramentas de IA conseguem gerar código rapidamente, mas precisam inferir contexto, regras de negócio, arquitetura e limites a partir das instruções recebidas. Quando tudo é solicitado em um prompt único, surgem riscos como:

- implementação de uma interpretação diferente da necessidade;
- inclusão de funcionalidades não solicitadas;
- violação de limites arquiteturais;
- testes que verificam detalhes, mas não o comportamento;
- retrabalho causado por correções sucessivas;
- aumento de débito técnico e de consumo de contexto.

SDD desloca parte desse raciocínio para artefatos explícitos. O agente pode ajudar a escrever, revisar e implementar, mas não precisa adivinhar decisões que deveriam ter sido discutidas.

## 1.2 O que conta como especificação?

Uma spec não precisa ser um único arquivo. Ela pode ser um conjunto de artefatos versionados e relacionados:

**Requisitos:** o problema, o objetivo, os fluxos e os critérios de aceitação.

**Design:** arquitetura, componentes, interfaces, dados e decisões técnicas.

**Tasks:** passos pequenos, ordenados e verificáveis.

**Contratos:** OpenAPI, schemas, eventos ou interfaces públicas.

**Testes:** exemplos executáveis do comportamento esperado.

**Constituição:** regras permanentes de qualidade, arquitetura, segurança e manutenção.

**Documentação operacional:** validação, deploy, observabilidade e rollback.

Uma informação só deve ser tratada como contrato quando houver clareza sobre sua autoridade. Um protótipo visual, por exemplo, pode ser uma referência de design, mas não necessariamente define acessibilidade, comportamento de erro ou contrato de dados.

## 1.3 Três níveis de adoção

Os níveis abaixo são uma forma útil de avaliar a maturidade do processo. Eles não são uma classificação oficial única de todo o mercado.

| Nível | Característica | Risco principal |
|---|---|---|
| `spec-first` | A spec é criada e revisada antes da implementação | Ser abandonada assim que o código começa |
| `spec-anchored` | A spec continua sendo referência durante manutenção e evolução | Ficar desatualizada após mudanças rápidas |
| `spec-as-source` | A spec é a fonte principal e o código é derivado ou regenerado | Rigidez, custo de tooling e perda de controle sobre detalhes |

O fluxo `spec-first` já melhora o planejamento. O ganho mais duradouro costuma aparecer quando a equipe mantém a spec ancorada no comportamento real, atualizando-a quando a intenção ou o contrato mudam.

Um sinal prático para saber em qual nível o time realmente está: olhe a última mudança de comportamento relevante e pergunte se a spec foi aberta e atualizada junto com o código, ou só o código mudou. Se a spec não é tocada há várias mudanças de comportamento, o time está em `spec-once` na prática, mesmo que tenha começado em `spec-first` ou `spec-anchored`. A progressão de nível não é uma decisão única de ferramenta, é um hábito: exigir que toda mudança de comportamento venha acompanhada de uma atualização de spec, ainda que pequena, é o que sustenta `spec-anchored` ao longo do tempo.

### Spec-once: um antipadrão útil de reconhecer

Uma equipe pode escrever uma boa spec, implementá-la e nunca mais consultá-la. Esse processo parece SDD no início, mas vira `spec-once`: a especificação foi usada como lançamento do trabalho, não como instrumento de manutenção.

A correção é tratar mudanças de comportamento como mudanças coordenadas em spec, design, tasks, código e testes.

## 1.4 Relação com práticas anteriores

SDD não substitui TDD, BDD, ATDD ou contract testing. Ele organiza essas práticas em torno de uma intenção compartilhada.

**TDD:** usa testes para guiar pequenos ciclos de implementação. Encaixa bem dentro de uma task de SDD: a spec diz o que implementar, TDD guia como implementar aquele pedaço específico.

**BDD:** expressa comportamento em linguagem que produto e engenharia conseguem revisar. Os critérios de aceite de uma spec de SDD podem ser escritos diretamente no formato Given/When/Then do BDD, unindo as duas práticas em vez de escolher uma.

**Specification by Example:** transforma exemplos concretos em especificações colaborativas. Serve como técnica para escrever a seção de requisitos ou critérios de aceite de uma spec, não como alternativa a ela.

**Contract testing:** verifica o acordo entre consumidor e provedor de uma integração. Útil como forma de validar a seção de contratos de uma spec quando a feature envolve integração entre serviços.

**API-first:** define uma interface antes de implementar seus consumidores e provedores. É uma instância específica de SDD aplicada a contratos de API.

**Design by Contract:** formaliza pré-condições, pós-condições e invariantes. Pode alimentar diretamente a seção de design de uma spec quando o componente tem contrato comportamental rígido.

A diferença de ênfase do SDD contemporâneo está na combinação de especificação, tooling e agentes de IA em um fluxo iterativo e rastreável. Na prática, a escolha não costuma ser "SDD ou BDD": a pergunta mais útil é qual dessas práticas mais específicas usar dentro de cada artefato da spec.

## 1.5 Benefícios e limites

Benefícios esperados:

- menor ambiguidade antes da implementação;
- escopo mais controlado;
- revisão de arquitetura em uma etapa mais barata;
- tasks menores e checkpoints objetivos;
- onboarding facilitado;
- histórico das decisões do projeto;
- contexto mais útil para ferramentas de IA.

Limites importantes:

- uma spec errada pode produzir código consistentemente errado;
- especificações detalhadas demais podem atrasar descoberta e aprendizado;
- testes derivados de uma spec não cobrem automaticamente segurança, operação ou comportamento emergente;
- `spec-as-source` exige ferramentas maduras e disciplina de geração;
- a qualidade da saída de IA continua dependendo de revisão humana e validação executável.

## 1.6 Navegação da trilha

- [2. Artefatos e estrutura](./2-artefatos-e-estrutura.md): requisitos, design, tasks, constituição e SDD de feature.
- [3. Fluxo operacional e checkpoints](./3-fluxo-operacional-e-checkpoints.md): do contexto inicial à implementação e à manutenção.
- [4. Spec Kit e ferramentas](./4-spec-kit-e-ferramentas.md): comandos, papéis e critérios para escolher tooling.
- [5. Exemplo com Angular](./5-exemplo-com-angular.md): uma feature pequena organizada em requirements, design e tasks.
- [6. SDD para agentes de IA](./6-sdd-para-agentes-de-ia.md): prompts, skills, revisão e limites de automação.
