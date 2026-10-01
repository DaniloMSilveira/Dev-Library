# 6. SDD para agentes de IA

Um agente de IA pode acelerar cada fase do fluxo descrito no documento 3, mas também pode ampliar o dano de uma decisão errada, mudar arquivos fora do escopo ou inventar contexto que não existe no repositório. Este documento cobre como estruturar prompts, skills, permissões e revisão para que o agente opere dentro da spec, não ao lado dela.

## 6.1 Por que SDD muda o uso de agentes

Sem spec, um agente recebe uma instrução solta e precisa inferir requisitos, arquitetura e limites a partir do prompt e do que conseguir observar no código. Com uma spec, essas três coisas já estão explícitas em um artefato versionado, e o papel do agente muda de "decidir o que fazer" para "executar o que foi decidido, dentro dos limites definidos".

Isso não elimina a necessidade de boas instruções. Pelo contrário: um agente ainda precisa de um prompt que diga **qual** artefato ler, **em que ordem**, e **o que fazer com a informação encontrada**. A spec dá o conteúdo; o prompt dá o comportamento.

## 6.2 Contexto como insumo, não como garantia

Entregar os artefatos certos a um agente não garante que ele os use corretamente. Um modelo de linguagem processa todo o conteúdo do prompt, incluindo a spec, como uma sequência de tokens, sem uma distinção estrutural automática entre "isso é uma regra inviolável" e "isso é uma sugestão". Por isso, uma constituição ou um limite de escopo precisa ser reforçado de forma explícita e repetida nos prompts de cada fase, não apenas citado uma vez no início da sessão e assumido como lembrado depois.

Essa limitação é a mesma discutida com mais profundidade na série de engenharia de contexto deste repositório, especialmente no que se refere a como a posição e a repetição de uma instrução dentro do prompt afetam o quanto o modelo de fato a segue.

## 6.3 Prompts por intenção

Cada fase do fluxo (documento 3) tem uma intenção diferente, e o prompt deve refletir isso explicitamente, em vez de pedir tudo de uma vez.

**Investigar:** pedir ao agente que leia o código relevante e resuma o comportamento atual, sem propor solução ainda.

```
Leia os arquivos em src/app/payment/.
Resuma o comportamento atual, sem propor mudanças.
Liste suposições que você precisou fazer para entender o fluxo.
```

**Especificar:** pedir que o agente ajude a redigir requirements ou design, com base no contexto já reunido.

```
Com base no resumo anterior, elabore um rascunho de requirements.md
seguindo a estrutura do documento 2 desta trilha.
Marque com [DECISÃO ABERTA] qualquer ponto que precise de confirmação minha.
```

**Planejar:** pedir um plano de tasks, sem ainda tocar em código.

```
A partir do requirements.md e design.md aprovados, gere tasks.md
seguindo a estrutura do documento 2. Não implemente nada ainda.
```

**Implementar:** pedir uma task por vez, nunca o conjunto inteiro.

```
Implemente somente a task T03.
Não inicie T04 nem refatore código fora do escopo de T03.
Ao final, liste arquivos alterados e o comando para rodar os testes afetados.
```

**Verificar:** pedir que o agente confronte o resultado com os critérios de aceite, sem ele mesmo decidir se passou.

```
Compare a implementação atual com os critérios de aceite CA01 a CA05
do requirements.md. Para cada um, responda apenas: atendido, não atendido,
ou não verificável sem execução manual. Não corrija nada ainda.
```

Separar essas intenções evita o padrão mais comum de falha: pedir "implemente a feature X" em um único prompt e o agente preencher todas as decisões não especificadas com a opção mais genérica possível, que raramente é a certa para o seu contexto específico.

## 6.4 Permissões e segurança

Um agente com acesso de escrita ao repositório, ou com capacidade de executar comandos, precisa operar sob limites explícitos, não apenas sob boas intenções no prompt.

Limites recomendados:

- restringir quais pastas o agente pode modificar na task atual;
- proibir alterações em arquivos de configuração de infraestrutura, segredos ou pipelines sem revisão humana explícita;
- exigir que o agente rode testes e linters antes de reportar uma task como concluída, mas não permitir que ele faça commit ou deploy sem confirmação;
- nunca colar segredos, chaves de API ou tokens em specs, prompts ou logs que o agente lê, mesmo temporariamente;
- revisar o diff gerado antes de aceitar, mesmo quando os testes passam, porque teste verde não significa escopo correto.

Esses limites valem tanto para uma skill (seção 6.6) quanto para o uso direto do agente em um editor ou terminal. A pergunta a fazer antes de dar uma permissão nova não é "isso ajuda o agente a ser mais autônomo", é "o que acontece se o agente errar com essa permissão".

## 6.5 Context window e sessões longas

Specs, design e código real podem ultrapassar o que cabe confortavelmente na janela de contexto do modelo em uma única sessão. Sintomas comuns de estouro de contexto incluem o agente esquecer uma decisão tomada no início da sessão, repetir uma pergunta já respondida, ou perder a referência a um arquivo lido há muitas mensagens.

Estratégias práticas:

- dividir uma sessão longa em sessões menores por task, recarregando apenas a spec e os arquivos relevantes àquela task específica, em vez de manter uma sessão única do início ao fim da feature;
- resumir decisões já tomadas em um bloco curto no início de uma nova sessão, em vez de confiar que o modelo "lembra" de uma sessão anterior;
- preferir referenciar um arquivo pelo caminho e deixar o agente lê-lo, em vez de colar o conteúdo inteiro no prompt quando o arquivo for grande e só uma parte for relevante.

O gerenciamento de janela de contexto, recuperação de informação relevante e estratégias de memória entre sessões são tratados com profundidade técnica na série de engenharia de contexto deste repositório. Este documento cobre apenas a aplicação direta desses conceitos ao fluxo de SDD: a spec e as tasks são, na prática, a principal fonte de contexto estruturado que se decide o que entra ou não em uma sessão com o agente.

## 6.6 Skills como SDD operacionalizado

Uma skill, no sentido usado no documento 4, é uma forma de fixar o fluxo de fases (investigar, especificar, planejar, implementar, verificar) como comportamento padrão do agente dentro de um projeto, em vez de reconstruir esse fluxo manualmente em cada prompt.

Uma skill bem desenhada para SDD deve declarar:

- em qual pasta procurar a spec da feature atual;
- qual estrutura de artefato é esperada (requirements/design/tasks separados, ou SDD.md único, conforme a seção 2.1);
- a obrigação de aguardar aprovação explícita antes de avançar da fase de especificação para a de planejamento, e desta para a de implementação;
- o limite de implementar uma task por vez, nunca o plano inteiro de uma vez;
- o comando de validação (teste, build, lint) que deve rodar antes de reportar uma task como concluída.

Uma skill não deve, no entanto, dar ao agente permissão para pular a aprovação humana nos checkpoints do documento 3 "para ser mais rápida". Automatizar o fluxo é diferente de automatizar a decisão sobre o fluxo.

## 6.7 O que não automatizar cegamente

Algumas decisões se beneficiam de assistência de IA, mas não deveriam ser delegadas inteiramente a um agente sem revisão humana direta:

- a decisão de que um requisito está completo e pode avançar para design;
- a aprovação final da spec antes da implementação começar;
- decisões de segurança, como forma de autenticação, exposição de dados sensíveis ou política de acesso;
- a interpretação de uma ambiguidade de negócio que afeta usuários reais;
- a decisão de que uma divergência entre spec e código (fase 6 do documento 3) deve ser resolvida mudando o código ou mudando a spec.

A IA pode preparar essas decisões, levantando opções e trade-offs, mas a responsabilidade final continua sendo de quem está revisando. Um agente que relata "implementado e testado com sucesso" não substitui a revisão humana do que de fato foi implementado, especialmente quando o teste em si pode ter sido escrito para validar a interpretação equivocada do agente sobre o requisito.

## 6.8 Resumo

Usar um agente de IA dentro de um fluxo de SDD muda o que se pede a ele: não "resolva o problema", mas "execute esta fase específica, dentro destes limites, usando esta spec como fonte de verdade". Isso exige prompts separados por intenção, permissões explícitas e revisadas, atenção ao tamanho de contexto em sessões longas, e uma linha clara entre o que pode ser automatizado e o que exige aprovação humana em cada checkpoint do fluxo descrito no documento 3.
