# 1. Ciclo de vida de projetos de Machine Learning

Este documento reúne os conceitos fundamentais para entender como um projeto de Machine Learning é conduzido, desde a definição do problema até a entrega e o monitoramento do modelo em produção.

## 1.1 Engenharia de software e Machine Learning

Embora ambos sejam áreas de engenharia, há diferenças importantes entre desenvolvimento tradicional e projetos com Machine Learning.

- Em software tradicional, a lógica é implementada explicitamente pelo desenvolvedor por meio de regras e instruções.
- Em Machine Learning, parte do comportamento emerge a partir de padrões aprendidos com dados.
- No software clássico, o comportamento costuma ser determinístico: para uma mesma entrada, a saída tende a ser previsível.
- Em ML, o resultado pode ser probabilístico e depender da qualidade dos dados, da escolha do algoritmo e da forma como o modelo foi treinado.

Em termos práticos, um sistema tradicional resolve problemas com regras claras. Um sistema com ML tenta aprender relações que nem sempre são totalmente conhecidas antes do desenvolvimento.

## 1.2 Ciclo de vida de software

Um projeto de software costuma seguir etapas bem conhecidas. Cada etapa tem um papel importante na construção de um sistema confiável.

1. Levantamento de requisitos
   - É o momento em que se identifica o problema, as necessidades do usuário e o escopo do sistema.
   - Exemplo: em um sistema de e-commerce, pode-se definir que o cliente precisa cadastrar produtos, adicionar itens ao carrinho e finalizar a compra.

2. Análise e especificação
   - A equipe transforma as necessidades em requisitos mais detalhados, muitas vezes com histórias de usuário e cenários.
   - Exemplo: "Como cliente, quero adicionar produtos ao carrinho para concluir minha compra sem repetir passos."

3. Arquitetura e design
   - Define-se como o sistema será estruturado, quais componentes participarão e como eles se comunicam.
   - Exemplo: separar o backend em módulos de catálogo, carrinho, pagamentos e autenticação.

4. Implementação
   - É a fase em que o código é escrito seguindo padrões de projeto, boas práticas e critérios de qualidade.
   - Exemplo: criar endpoints de API para cadastro de usuário e consulta de produtos.

5. Testes
   - O objetivo é validar se o sistema atende aos requisitos e se não há falhas críticas.
   - Exemplo: testar se o checkout funciona corretamente quando o cliente escolhe diferentes formas de pagamento.

6. Deploy
   - O sistema é disponibilizado para uso em produção, normalmente por meio de pipelines de integração e entrega contínua.
   - Exemplo: publicar uma aplicação web em uma plataforma de nuvem com automação de deploy.

7. Manutenção
   - Após o lançamento, o sistema passa por ajustes, correções e melhorias contínuas.
   - Exemplo: corrigir um bug identificado em uma funcionalidade de login ou adicionar uma nova regra de negócio.

## 1.3 Ciclo de vida de um projeto de Machine Learning

Em Machine Learning, o ciclo é semelhante em termos de disciplina, mas com foco maior em dados e aprendizado.

1. Definição do problema
   - É preciso saber exatamente o que se quer prever, classificar ou encontrar.
   - Exemplo: prever se um cliente provavelmente deixará de usar o serviço em um mês.

2. Coleta e preparação de dados
   - Os dados são reunidos a partir de fontes diversas, como bancos, arquivos, logs ou APIs.
   - Nesta etapa, também ocorre limpeza, tratamento de valores ausentes, remoção de ruídos e organização do conjunto de dados.
   - Exemplo: consolidar histórico de compras, frequência de acesso e dados demográficos.

3. Exploração e análise dos dados
   - O objetivo é entender melhor as características dos dados antes do treinamento.
   - Pode-se verificar distribuições, correlações, valores extremos e possíveis enviesamentos.
   - Exemplo: descobrir que muitos clientes ativos são do mesmo segmento demográfico.

4. Treinamento do modelo
   - Escolhe-se um algoritmo adequado ao problema e treinam-se os parâmetros do modelo com os dados disponíveis.
   - Em muitos casos, várias abordagens são testadas antes de escolher a mais adequada.
   - Exemplo: comparar regressão logística, árvores de decisão e modelos baseados em redes neurais.

5. Validação e avaliação
   - O modelo é avaliado com dados que não foram usados durante o treino para verificar se ele generaliza bem.
   - Aqui entram métricas como precisão, recall, acurácia, erro médio e F1-score.
   - Exemplo: verificar se o modelo consegue detectar corretamente clientes em risco sem gerar muitos falsos positivos.

6. Deploy
   - O modelo é integrado a uma aplicação, serviço ou pipeline de decisão.
   - Pode ser exposto via API, usado em um sistema interno ou incorporado em um fluxo automatizado.
   - Exemplo: aplicar o modelo em uma plataforma de atendimento para sugerir ações de retenção.

7. Monitoramento e manutenção
   - Depois de entrar em produção, o modelo precisa ser monitorado para garantir que continue performando bem.
   - Com o tempo, os dados podem mudar, o que exige re-treinamento, ajustes e atualização de regras.
   - Exemplo: um modelo de detecção de fraude pode perder precisão se os padrões de fraude mudarem.

## 1.4 Diferenças principais entre software e ML

| Aspecto | Desenvolvimento tradicional | Machine Learning |
|---|---|---|
| Base | Regras explícitas | Dados e aprendizado |
| Resultado | Determinístico | Probabilístico |
| Validação | Testes funcionais e regras de negócio | Métricas de desempenho e generalização |
| Manutenção | Correções e novas features | Re-treinamento, ajuste e monitoramento |
| Foco principal | Comportamento do sistema | Padrões presentes nos dados |

## 1.5 Arquivos entregues em projetos de ML

Um projeto de Machine Learning geralmente envolve mais do que apenas o modelo final. Os principais entregáveis são:

- Código fonte para treino, avaliação e inferência
  - Inclui scripts, notebooks ou módulos prontos para executar as etapas do pipeline.

- Dados de treino, validação e teste
  - Garantem que o modelo possa ser treinado e validado de forma consistente.

- Arquivos de configuração
  - Definem hiperparâmetros, caminhos de dados, seeds e outras definições importantes.

- Relatórios de desempenho
  - Apresentam métricas, gráficos e comparações entre modelos.

- Documentação do projeto
  - Explica objetivos, estrutura, dependências, instruções de execução e decisões tomadas.

- Artefatos do modelo treinado
  - Podem incluir pesos, versões do modelo, metadata e arquivos de serialização.

## 1.6 Exemplo prático

Considere um projeto para prever inadimplência de clientes em um banco.

- O problema é definido claramente: identificar clientes com maior chance de atraso no pagamento.
- Os dados incluem histórico de pagamentos, valor médio das faturas, renda e comportamento recente.
- O modelo é treinado e avaliado com métricas como recall e precisão.
- O resultado pode ser usado para priorizar ações de recuperação antes que o problema se agrave.

Esse exemplo mostra que um projeto de ML não é apenas uma tarefa técnica. Ele é uma solução orientada a decisão e impacto real.

## 1.7 Resumo

Um projeto de Machine Learning vai além de “treinar um modelo”. Ele envolve estratégia, dados, avaliação, implantação e monitoramento contínuo. O sucesso depende de boa definição do problema, qualidade dos dados, escolhas técnicas adequadas e acompanhamento após o deploy.
