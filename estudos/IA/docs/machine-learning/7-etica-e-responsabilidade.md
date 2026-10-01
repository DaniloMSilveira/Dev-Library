# 7. Ética e responsabilidade

Construir modelos tecnicamente sólidos não é suficiente. Este documento cobre os principais princípios éticos, riscos e obrigações legais envolvidos no desenvolvimento e uso de sistemas de Machine Learning e IA.

## 7.1 Por que ética importa em ML

Modelos de ML tomam ou influenciam decisões que afetam pessoas reais: aprovação de crédito, triagem de currículos, diagnóstico médico, moderação de conteúdo. Diferente de um bug de software, um problema ético em um modelo pode ser sistemático e afetar milhares de pessoas da mesma forma, de forma silenciosa, sem gerar um erro visível que chame atenção para o problema.

## 7.2 Princípios éticos centrais

**Justiça (fairness):** o modelo não deve gerar resultados sistematicamente piores para determinados grupos, como raça, gênero ou idade, sem justificativa legítima relacionada ao problema.

**Transparência:** deve ser possível entender, em algum grau, como o modelo chega às suas decisões, especialmente em contextos de alto impacto. As técnicas de interpretabilidade vistas no documento [4. Avaliação e generalização de modelos](./4-avaliacao-e-generalizacao-de-modelos.md), como SHAP e LIME, são ferramentas práticas para isso.

**Responsabilização (accountability):** deve estar claro quem responde pelas decisões do modelo, incluindo mecanismos de correção quando algo dá errado.

**Privacidade:** dados pessoais usados no treinamento e na operação do modelo devem ser protegidos, com coleta e uso limitados ao necessário para o propósito declarado.

**Segurança e robustez:** o modelo deve se comportar de forma previsível e segura, inclusive diante de entradas inesperadas, adversariais ou fora da distribuição de treino.

**Consentimento informado:** pessoas cujos dados são usados devem saber disso e, na maioria dos casos, ter concordado explicitamente. Isso vale tanto para a coleta dos dados quanto para o uso que o modelo faz deles, e é uma exigência tanto ética quanto legal, retomada na seção 7.5 sobre LGPD.

**Não maleficência:** o sistema não deve, no seu funcionamento normal, causar dano a pessoas ou grupos, o que exige considerar não apenas o uso pretendido, mas também usos indevidos previsíveis.

**Sustentabilidade:** modelos muito grandes, especialmente LLMs, têm custo computacional e ambiental relevante, algo que também pesa na escolha entre um modelo mais simples e um mais complexo quando ambos atendem ao problema.

## 7.3 Viés em Machine Learning

Viés (bias) é uma distorção sistemática nas previsões do modelo, geralmente desfavorável a um grupo específico. Diferente de erro aleatório, viés tem uma direção consistente.

Três origens comuns:

**Viés nos dados de treino:** se os dados históricos refletem discriminação passada, o modelo aprende e reproduz esse padrão. Um exemplo clássico é um modelo de triagem de currículos treinado em contratações históricas de uma empresa que, no passado, contratou predominantemente um perfil demográfico específico.

**Viés de amostragem:** quando certos grupos estão sub-representados nos dados de treino, o modelo tende a performar pior para eles, simplesmente por ter visto poucos exemplos daquele grupo durante o aprendizado.

**Viés de medição:** quando a forma como uma variável é medida ou definida já embute uma distorção, como usar "número de prisões" como proxy para "criminalidade", quando o primeiro também reflete padrões de policiamento desigual, não apenas o comportamento em si.

**Mitigação:** passa por auditar os dados de treino antes do treinamento, calcular métricas de desempenho separadamente por subgrupo relevante (como já descrito na seção 4.9), e, quando necessário, aplicar técnicas de correção como reponderação de exemplos ou ajuste de limiar de decisão por grupo.

## 7.4 Explicabilidade na prática

Em muitos setores regulados, como crédito e saúde, explicar uma decisão automatizada não é apenas boa prática, é exigência legal. Uma decisão de negar crédito, por exemplo, pode exigir que a instituição informe ao cliente os principais fatores que levaram àquela decisão.

Isso cria uma tensão prática: modelos mais complexos, como redes neurais profundas e ensembles de árvores, costumam ter melhor desempenho, mas são mais difíceis de explicar do que um modelo linear ou uma única árvore de decisão. Técnicas como SHAP ajudam a mitigar essa tensão, mas não a eliminam completamente, e a escolha do modelo em domínios regulados precisa considerar essa troca desde o início do projeto, não apenas depois que o modelo já está pronto.

## 7.5 LGPD e proteção de dados

A Lei Geral de Proteção de Dados (LGPD) estabelece regras para coleta, armazenamento e uso de dados pessoais no Brasil, e é diretamente relevante para projetos de ML que usam dados de pessoas.

Pontos centrais para um projeto de ML:

**Finalidade específica:** os dados só podem ser usados para o propósito informado no momento da coleta. Usar uma base de dados de clientes, coletada para faturamento, para treinar um modelo de propensão de compra sem base legal adicional, é uma violação comum.

**Minimização de dados:** deve-se coletar e reter apenas os dados necessários para o propósito declarado, não tudo que estiver disponível.

**Direito à explicação:** titulares de dados têm direito a solicitar revisão de decisões tomadas unicamente por meio de processamento automatizado, o que se conecta diretamente à necessidade de explicabilidade discutida na seção 7.4.

**Anonimização e pseudonimização:** técnicas que reduzem o risco associado ao uso de dados pessoais, embora seja importante saber que dados "anonimizados" às vezes podem ser reidentificados quando cruzados com outras bases, o que exige cuidado real, não apenas nominal, no tratamento desses dados.

## 7.6 Riscos específicos de LLMs

Os riscos éticos de LLMs incluem os já discutidos para ML em geral, além de alguns específicos à forma como esses modelos são treinados e usados, complementando as limitações técnicas já descritas no documento [6. Transformers e LLMs](./6-transformers-e-llms.md).

**Viés amplificado em escala:** por serem treinados em corpora massivos coletados da internet, LLMs podem herdar e reproduzir estereótipos presentes nesses dados, e fazem isso em escala, potencialmente afetando um número muito maior de interações do que um modelo de classificação tradicional treinado para uma tarefa específica.

**Desinformação:** a capacidade de gerar texto fluente e convincente, combinada com o risco de alucinação, facilita a geração de conteúdo falso em volume, dificultando a distinção entre conteúdo gerado por humanos e por modelos.

**Uso indevido:** a mesma capacidade que permite gerar código, textos e respostas úteis pode ser direcionada para fins maliciosos, como geração de phishing ou conteúdo enganoso em massa.

## 7.7 Checklist de responsabilidade

Antes de colocar um modelo em produção, vale revisar:

**1. Dados:** a coleta teve base legal e consentimento adequado? Há representação equilibrada dos grupos relevantes ao problema?

**2. Avaliação:** o desempenho foi medido por subgrupo, não apenas de forma agregada?

**3. Explicabilidade:** é possível explicar, ao menos em linhas gerais, por que o modelo tomou uma decisão específica?

**4. Impacto:** foram considerados os usos indevidos previsíveis do sistema, não apenas o uso pretendido?

**5. Monitoramento:** existe um plano para monitorar o modelo após o deploy e agir se o comportamento mudar ou algum problema for identificado?

## 7.8 Resumo

Ética em Machine Learning não é uma etapa isolada, adicionada ao final do projeto. Justiça, transparência, privacidade e responsabilização precisam ser consideradas desde a definição do problema e a coleta de dados, atravessando a escolha do algoritmo, a avaliação por subgrupo e o monitoramento contínuo após o deploy. Em domínios regulados, essas considerações deixam de ser apenas boas práticas e passam a ser exigências legais, como no caso da LGPD.
