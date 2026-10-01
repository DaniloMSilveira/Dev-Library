# 1. Ciclo de vida de projetos de Machine Learning

Este documento reúne os conceitos fundamentais para entender como um projeto de Machine Learning é conduzido, desde a definição do problema até a entrega e o monitoramento do modelo em produção.

## 1.1 Engenharia de software e Machine Learning

Embora ambos sejam áreas de engenharia, há diferenças importantes entre desenvolvimento tradicional e projetos com Machine Learning.

Em software tradicional, a lógica é implementada explicitamente pelo desenvolvedor por meio de regras e instruções. Em Machine Learning, parte do comportamento emerge a partir de padrões aprendidos com dados.

Tanto sistemas tradicionais quanto sistemas de ML podem ser determinísticos ou conter aleatoriedade, dependendo da implementação e da configuração. Em ML, o comportamento aprendido depende da qualidade dos dados, do algoritmo, do treinamento e do limiar de decisão usado.

Em termos práticos, um sistema tradicional resolve problemas com regras claras. Um sistema com ML tenta aprender relações que nem sempre são totalmente conhecidas antes do desenvolvimento.

## 1.2 Ciclo de vida de software

Um projeto de software costuma seguir etapas bem conhecidas. Cada etapa tem um papel importante na construção de um sistema confiável.

**1. Levantamento de requisitos:** Momento em que se identifica o problema, as necessidades do usuário e o escopo do sistema. Exemplo: em um sistema de e-commerce, definir que o cliente precisa cadastrar produtos, adicionar itens ao carrinho e finalizar a compra.

**2. Análise e especificação:** A equipe transforma as necessidades em requisitos mais detalhados, muitas vezes com histórias de usuário e cenários. Exemplo: "Como cliente, quero adicionar produtos ao carrinho para concluir minha compra sem repetir passos."

**3. Arquitetura e design**: Define-se como o sistema será estruturado, quais componentes participarão e como eles se comunicam. Exemplo: separar o backend em módulos de catálogo, carrinho, pagamentos e autenticação.

**4. Implementação**: Fase em que o código é escrito seguindo padrões de projeto, boas práticas e critérios de qualidade. Exemplo: criar endpoints de API para cadastro de usuário e consulta de produtos.

**5. Testes**: O objetivo é validar se o sistema atende aos requisitos e se não há falhas críticas. Exemplo: testar se o checkout funciona corretamente com diferentes formas de pagamento.

**6. Deploy**: O sistema é disponibilizado para uso em produção, normalmente por meio de pipelines de integração e entrega contínua. Exemplo: publicar uma aplicação web em nuvem com automação de deploy.

**7. Manutenção**: Após o lançamento, o sistema passa por ajustes, correções e melhorias contínuas. Exemplo: corrigir um bug em uma funcionalidade de login ou adicionar uma nova regra de negócio.

## 1.3 Ciclo de vida de um projeto de Machine Learning

Em Machine Learning, o ciclo é semelhante em termos de disciplina, mas com foco maior em dados e aprendizado.

**1. Definição do problema**: É preciso saber exatamente o que se quer prever, classificar ou encontrar. Exemplo: prever se um cliente provavelmente deixará de usar o serviço em um mês.

**2. Coleta e preparação de dados**: Os dados são reunidos a partir de fontes diversas, como bancos, arquivos, logs ou APIs. Nesta etapa também ocorre limpeza, tratamento de valores ausentes, remoção de ruídos e organização do conjunto de dados. Exemplo: consolidar histórico de compras, frequência de acesso e dados demográficos.

**3. Exploração e análise dos dados**: O objetivo é entender melhor as características dos dados antes do treinamento, verificando distribuições, correlações, valores extremos e possíveis enviesamentos. Exemplo: descobrir que muitos clientes ativos são do mesmo segmento demográfico.

**4. Engenharia de atributos**: Criação, transformação e seleção das variáveis que o modelo vai efetivamente usar. Este tema é tratado em detalhe no documento [2. Feature engineering e hiperparâmetros](./2-feature-engineering-e-hiperparametros.md), já que normalmente acontece antes e em paralelo à escolha do algoritmo, não depois dela.

**5. Treinamento do modelo**: Escolhe-se um algoritmo adequado ao problema e treinam-se os parâmetros do modelo com os dados disponíveis. Em muitos casos, várias abordagens são testadas antes de escolher a mais adequada. Exemplo: comparar regressão logística, árvores de decisão e modelos baseados em redes neurais.

**6. Validação e avaliação**: O modelo é avaliado com dados que não foram usados durante o treino, para verificar se ele generaliza bem. Aqui entram métricas como precisão, recall, acurácia, erro médio e F1-score. Exemplo: verificar se o modelo detecta corretamente clientes em risco sem gerar muitos falsos positivos. Um resultado ruim aqui frequentemente manda o projeto de volta para a etapa de features ou até para a definição do problema.

**7. Deploy**: O modelo é integrado a uma aplicação, serviço ou pipeline de decisão, exposto via API, usado internamente ou incorporado em um fluxo automatizado. Exemplo: aplicar o modelo em uma plataforma de atendimento para sugerir ações de retenção.

**8. Monitoramento e manutenção**: Depois de entrar em produção, o modelo precisa ser monitorado para garantir que continue performando bem. Com o tempo os dados podem mudar, exigindo re-treinamento, ajustes e atualização de regras. Exemplo: um modelo de detecção de fraude pode perder precisão se os padrões de fraude mudarem. O monitoramento pode revelar a necessidade de reiniciar o ciclo desde a coleta de dados.

## 1.4 Diferenças principais entre software e ML

| Aspecto | Desenvolvimento tradicional | Machine Learning |
|---|---|---|
| Base | Regras explícitas | Dados e aprendizado |
| Resultado | Definido por regras e componentes | Definido por parâmetros aprendidos |
| Validação | Testes funcionais e regras de negócio | Métricas de desempenho e generalização |
| Manutenção | Correções e novas features | Re-treinamento, ajuste e monitoramento |
| Foco principal | Comportamento do sistema | Padrões presentes nos dados |

## 1.5 Arquivos entregues em projetos de ML

Um projeto de Machine Learning geralmente envolve mais do que apenas o modelo final. Os principais entregáveis são:

- Código fonte para treino, avaliação e inferência: scripts, notebooks ou módulos prontos para executar as etapas do pipeline.
- Dados de treino, validação e teste: garantem que o modelo possa ser treinado e validado de forma consistente.
- Arquivos de configuração: definem hiperparâmetros, caminhos de dados, seeds e outras definições importantes.
- Relatórios de desempenho: apresentam métricas, gráficos e comparações entre modelos.
- Documentação do projeto: explica objetivos, estrutura, dependências, instruções de execução e decisões tomadas.
- Artefatos do modelo treinado: pesos, versões do modelo, metadata e arquivos de serialização.

## 1.6 Reprodutibilidade e versionamento

Um projeto de ML só é confiável se puder ser reproduzido. Dado o mesmo código, os mesmos dados e a mesma configuração, o resultado deve ser aproximadamente o mesmo. Na prática isso costuma falhar por descuido, não por limitação técnica, e é um dos maiores gargalos de projetos reais de ML.

Três frentes de versionamento costumam ser necessárias, e são independentes entre si.

Código é versionado com Git, como em qualquer projeto de software.

Dados mudam ao longo do tempo, com novos registros, correções e reprocessamentos. Sem versionar o dado usado em cada treino, é impossível saber depois qual dado gerou qual modelo. Ferramentas como DVC (Data Version Control) ou soluções de data lake com versionamento, como Delta Lake, resolvem esse problema.

Modelos e experimentos também variam entre execuções, mesmo com o mesmo código, por causa de aleatoriedade na inicialização, no shuffle dos dados ou em técnicas como dropout. Ferramentas como MLflow, Weights & Biases ou DVC permitem registrar, para cada execução, os hiperparâmetros usados, as métricas obtidas, a versão dos dados e o artefato do modelo resultante.

Boas práticas mínimas:

- fixar seeds sempre que possível, sabendo que isso reduz mas não elimina toda variabilidade (paralelismo em GPU pode introduzir não determinismo residual);
- registrar a versão exata do código, dos dados e dos hiperparâmetros usados em cada modelo publicado;
- manter um requirements.txt ou lockfile com as versões exatas das bibliotecas, já que uma mudança de versão de scikit-learn ou PyTorch pode alterar resultados;
- nunca sobrescrever um dataset de forma destrutiva, preferindo novas versões nomeadas ou controladas por ferramenta de versionamento.

## 1.7 Exemplo prático

Considere um projeto para prever inadimplência de clientes em um banco.

O problema é definido claramente: identificar clientes com maior chance de atraso no pagamento. Os dados incluem histórico de pagamentos, valor médio das faturas, renda e comportamento recente. O modelo é treinado e avaliado com métricas como recall e precisão, e o resultado pode ser usado para priorizar ações de recuperação antes que o problema se agrave.

Esse exemplo mostra que um projeto de ML não é apenas uma tarefa técnica. É uma solução orientada a decisão e impacto real, construída de forma iterativa.

## 1.8 Resumo

Um projeto de Machine Learning vai além de treinar um modelo. Envolve estratégia, dados, avaliação, implantação e monitoramento contínuo, em um ciclo iterativo. O sucesso depende de boa definição do problema, qualidade dos dados, escolhas técnicas adequadas, reprodutibilidade e acompanhamento após o deploy.
