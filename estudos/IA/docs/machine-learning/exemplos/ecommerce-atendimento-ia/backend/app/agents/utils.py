# Projeto Desenvolvido na Data Science Academy

"""Utilitários compartilhados entre agentes."""

import logging
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from app.config import settings
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def dsa_create_llm() -> ChatOpenAI:
    """Cria uma instância ChatOpenAI com os padrões do projeto."""
    return ChatOpenAI(model = settings.MODEL_NAME, temperature = 1)


def dsa_get_last_message(state: AgentState) -> str:
    """Extrai o conteúdo da última mensagem do estado."""
    messages = state["messages"]
    
    return messages[-1].content if messages else ""


async def dsa_run_tools_and_respond(
    tools: list,
    system_prompt: str,
    user_message: str,
    agent_name: str,
    context_label: str = "Informações encontradas",
) -> dict:
    """Executa tools via LLM e gera resposta final (padrão de 2 chamadas)."""
    try:
        llm = dsa_create_llm()

        response = await llm.bind_tools(tools).ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ])

        if response.tool_calls:
            tool_map = {t.name: t for t in tools}
            tool_results = []

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                logger.info(f"{agent_name} chamando tool: {tool_name}({tool_args})")
                if tool_name in tool_map:
                    try:
                        result = await tool_map[tool_name].ainvoke(tool_args)
                        tool_results.append(result)
                    except Exception:
                        logger.exception(f"Erro ao executar tool {tool_name}")
                        tool_results.append(f"Erro ao executar {tool_name}")
                else:
                    logger.warning(f"Tool '{tool_name}' não encontrada no mapa")

            context = "\n\n".join(str(r) for r in tool_results)
            final_response = await llm.ainvoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": f"{context_label}:\n{context}"},
                {"role": "user", "content": "Com base nas informações acima, responda ao cliente."},
            ])
            answer = final_response.content
        else:
            # LLM não chamou tools — usa resposta direta (pergunta genérica ou já sabida)
            answer = response.content

    except Exception:
        logger.exception(f"Erro no agente {agent_name}")
        answer = (
            "Desculpe, estou com dificuldades técnicas no momento. "
            "Por favor, tente novamente em instantes."
        )

    return {
        "messages": [AIMessage(content = answer)],
        "agent_used": agent_name,
        "sources": [],
    }


def dsa_create_tool_agent(tools: list, system_prompt: str, agent_name: str, context_label: str):
    """Cria uma função de agente com chamada de tools para o workflow LangGraph."""

    async def agent(state: AgentState) -> dict:
        return await dsa_run_tools_and_respond(
            tools = tools,
            system_prompt = system_prompt,
            user_message = dsa_get_last_message(state),
            agent_name = agent_name,
            context_label = context_label,
        )

    return agent


