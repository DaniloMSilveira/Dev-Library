# 7. Colaboração entre múltiplos agentes

Colaboração multiagente é o nome guarda-chuva para sistemas em que vários agentes, cada um com seu papel, trabalham juntos em um mesmo objetivo. O [Supervisor](6-supervisor.md) é um caso particular, com um coordenador central. Esta página trata do caso geral: como os agentes trocam mensagens, como podem ser conectados, como usar o debate entre agentes para melhorar uma decisão e quais decisões de projeto precisam ser tomadas no início.

A mensagem principal é de cautela: cada agente a mais multiplica custo e complexidade. O padrão vale a pena quando a colaboração melhora um resultado que pode ser medido.

## 7.1 Termos e definições

**Papel:** a responsabilidade de um agente no grupo (por exemplo, propor, questionar, consolidar), definida pelo prompt de sistema, pelas ferramentas que ele recebe e pelo modelo usado.

**Mensagem:** a unidade de comunicação entre agentes. Diferente de uma conversa humana, precisa de estrutura para ser roteada e auditada.

**Topologia:** quem pode mandar mensagem para quem.

**Estado compartilhado:** dados que todos os agentes leem e escrevem, como o status geral da tarefa. É a alternativa (ou o complemento) à troca de mensagens, discutida em [3.5 Estado e memória compartilhada entre agentes](../context-engineering/3-memoria-e-estado.md#_3-5-estado-e-memoria-compartilhada-entre-agentes).

**Debate:** arranjo em que agentes com posições ou papéis diferentes argumentam em rodadas, e uma decisão final é extraída do diálogo.

## 7.2 O protocolo de mensagens

Para que vários agentes conversem de forma confiável, cada mensagem precisa carregar mais do que o texto:

| Campo | Para que serve |
|---|---|
| Remetente | Saber quem disse o quê, para auditoria e para o contexto de quem recebe |
| Destinatário | Entregar a um agente específico ou a todos (*broadcast*) |
| Tipo | Distinguir proposta, pergunta, resposta, crítica e informação |
| Conteúdo | O texto ou os dados da mensagem |
| Referência | A mensagem ou o item do estado a que ela responde |

```python
# Ilustrativo: estrutura mínima de uma mensagem entre agentes.
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Mensagem:
    remetente: str
    destinatario: str  # nome de um agente ou "todos"
    tipo: Literal["proposta", "pergunta", "resposta", "critica", "info"]
    conteudo: str
    responde_a: int | None = None  # índice da mensagem no log
```

Registrar todas as mensagens em um log único, na ordem em que foram enviadas, é o que permite reconstruir depois por que o grupo chegou a uma conclusão.

## 7.3 Topologias

| Topologia | Como funciona | Vantagens | Desvantagens |
|---|---|---|---|
| Estrela | Todos falam só com um coordenador central (o padrão Supervisor) | Simples, auditável, custo previsível | O coordenador é ponto único de falha e gargalo |
| Cadeia | Cada agente passa o resultado ao próximo, em sequência fixa | Fácil de entender e testar | Pouco flexível; um erro no início se propaga |
| Malha | Qualquer agente pode falar com qualquer outro | Flexível, sem coordenador único | O número de interações cresce rápido e o comportamento fica difícil de prever |

O custo da malha merece atenção. Se cada um dos N agentes lê e responde às falas dos outros a cada rodada, o número de mensagens processadas por rodada cresce com o quadrado de N: com N agentes e R rodadas, são da ordem de N² × R leituras de mensagem. Dobrar o número de agentes quadruplica esse volume. Antes de adotar malha, confira se uma estrela ou uma cadeia resolvem.

## 7.4 Debate entre agentes

O debate usa a divergência como ferramenta. Em vez de confiar em uma única resposta, o sistema coloca agentes com papéis diferentes para argumentar e só então consolida:

```text
rodada 1..R:   proponente ──► defende uma posição
                    ▲                │
                    └── cético ◄─────┘  aponta suposições frágeis e riscos

após R rodadas:  log do debate ──► sintetizador ──► decisão final com justificativa
```

Du et al. (2023) estudaram uma forma desse arranjo: várias instâncias de um modelo propõem respostas, leem as respostas umas das outras e revisam as próprias ao longo de rodadas até convergir. O método melhorou raciocínio matemático e estratégico e reduziu respostas factualmente incorretas nas tarefas avaliadas.

**Quando usar:** decisões caras de errar e com espaço para perspectivas diferentes, como escolha de arquitetura, análise de risco de um contrato ou priorização. Os papéis podem ser de posição (proponente, cético) ou de especialidade (segurança, custo, experiência do usuário).

**Cuidados:**

- **Divergência útil (recomendação).** O trabalho de Du et al. obteve ganhos mesmo com várias instâncias do mesmo modelo, então modelos diferentes não são obrigatórios. Ainda assim, convergência rápida não é sinal de acerto: se os agentes concordam logo na primeira rodada, o debate pode estar só repetindo a mesma resposta. Papéis bem definidos (e, quando fizer sentido, modelos diferentes) ajudam a trazer objeções que um agente sozinho não levantaria.
- **Critério de parada.** Número fixo de rodadas, convergência (ninguém muda de posição) ou um sintetizador que decide. O sintetizador é o mais previsível, porque sempre produz uma saída.
- **Concordância não é verdade.** Agentes podem convergir para a mesma resposta errada. Quando houver como verificar com dados ou testes, verifique.

## 7.5 Decisões de projeto

Estas decisões são difíceis de mudar depois que o sistema está construído, então valem ser tomadas de forma explícita no início:

| Decisão | Opções | Critério |
|---|---|---|
| Topologia | Estrela, cadeia, malha | Estrela para controle e auditoria; malha só se a flexibilidade compensar o custo |
| Comunicação | Mensagens, estado compartilhado, os dois | Estado para fatos que todos consultam; mensagens para coordenação pontual |
| Memória | Privada por agente, compartilhada | Compartilhada para colaborar; privada para isolar papéis e evitar contaminação |
| Modelos | Iguais para todos, diferentes por papel | Diferentes para ajustar custo e para aumentar a diversidade de perspectivas |
| Parada | Rodadas fixas, convergência, sintetizador | Sempre com um teto de rodadas ou mensagens |

## 7.6 Combinando os padrões da trilha

Os padrões desta trilha se encaixam. Um arranjo possível para um assistente de operações financeiras:

1. Um **router** separa pedidos simples (respondidos direto por um modelo pequeno) de pedidos de análise.
2. Pedidos de análise vão para um **supervisor**, que coordena workers de dados, contratos e redação.
3. Cada worker é um agente **ReAct** com as ferramentas da sua especialidade.
4. Quando o pedido é uma decisão de alto impacto, o supervisor aciona um **debate** entre um proponente e um cético antes do parecer.
5. O parecer passa por **reflection** contra a política da empresa antes de ser entregue.

Cada camada acrescenta custo, latência e pontos de falha. A ordem segura é a inversa da complexidade: começar com um único agente, medir onde ele falha e acrescentar o padrão que resolve aquela falha.

## 7.7 Resumo

Sistemas multiagente exigem decisões explícitas sobre protocolo de mensagens, topologia, memória, modelos e critério de parada. A estrela é a topologia mais controlável; a malha é a mais flexível e a mais cara, com volume de mensagens crescendo com o quadrado do número de agentes. O debate entre agentes com papéis distintos pode melhorar decisões difíceis, desde que haja divergência real e um sintetizador que encerre. Como em toda a trilha, mais agentes só se justificam quando melhoram um resultado medido.

## Fontes

- Du et al., [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325), 2023, consultado em 2026-10-28.
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), Anthropic, publicado em 2024-12-19, consultado em 2026-10-28.
