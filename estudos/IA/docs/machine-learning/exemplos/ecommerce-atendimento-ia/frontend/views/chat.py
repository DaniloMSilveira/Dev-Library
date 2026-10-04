# Projeto Desenvolvido na Data Science Academy
"""Página de Chat — Interface do chatbot com agentes de IA."""

import logging
import time
import httpx
import streamlit as st
from config import CHAT_TIMEOUT, http

logger = logging.getLogger(__name__)

# Mensagem inicial exibida ao usuário quando o chat é iniciado.
# Atua como onboarding e direciona os principais casos de uso.
WELCOME_MESSAGE = (
    "Olá! Sou o assistente virtual da Tech Store Brasil. Posso ajudar com:\n\n"
    "- Consultas sobre produtos\n"
    "- Status de pedidos\n"
    "- Políticas de troca/devolução\n"
    "- Recomendações personalizadas\n\n"
    "Como posso ajudar?"
)


def dsa_render_chat():
    """Renderiza a página de chat.

    Responsabilidades:
    - Inicializar histórico de conversa
    - Exibir mensagens (user + assistant)
    - Renderizar sugestões iniciais
    - Integrar com backend via API
    - Controlar estado da conversa (conversation_id)
    """

    st.markdown("## 💬 Assistente TechStore")
    st.caption("Pergunte sobre produtos, pedidos, políticas ou qualquer dúvida!")

    # Inicializa histórico se ainda não existir
    # session_state permite persistência entre reruns do Streamlit
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Injeta mensagem de boas-vindas apenas na primeira interação
    if not st.session_state["chat_history"]:
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "agent_used": "welcome",
        })

    # Exibe sugestões rápidas apenas no início da conversa
    # (quando só existe a mensagem de boas-vindas)
    if len(st.session_state["chat_history"]) <= 1:
        st.markdown("**Sugestões:**")

        cols = st.columns(4)

        # Sugestões pré-definidas para guiar o usuário
        suggestions = [
            ("📦 Status do pedido", "Qual o status do meu pedido?"),
            ("🔍 Buscar produto", "Quero ver smartphones até R$5000"),
            ("🔄 Política de trocas", "Qual a política de troca e devolução?"),
            ("👤 Falar com atendente", "Quero falar com um atendente humano"),
        ]

        # Cada botão dispara envio direto de mensagem
        for i, (label, message) in enumerate(suggestions):
            with cols[i]:
                if st.button(label, key=f"suggestion-{i}"):
                    dsa_send_message(message)

    # Permite navegação programática para o chat a partir de outras telas
    # (ex: clicar em "Perguntar ao assistente" no produto)
    initial_msg = st.session_state.pop("chat_initial_message", None)
    if initial_msg:
        dsa_send_message(initial_msg)

    # Renderização do histórico de mensagens
    for idx, msg in enumerate(st.session_state["chat_history"]):

        # st.chat_message define o layout visual tipo chat (balões)
        with st.chat_message(msg["role"]):

            # Flag "_new" indica mensagem recém-chegada do backend
            # usada para aplicar efeito de digitação apenas uma vez
            is_new = msg.get("_new", False)

            if is_new:
                msg["_new"] = False
                _dsa_typewriter(msg["content"])
            else:
                st.markdown(msg["content"])

            # Exibe qual agente respondeu (observabilidade do sistema multi-agente)
            if msg["role"] == "assistant" and msg.get("agent_used") not in ("welcome", None):

                agent_labels = {
                    "router_agent": "Assistente Geral",
                    "product_agent": "Agente de Produtos 🛒",
                    "order_agent": "Agente de Pedidos 📦",
                    "faq_agent": "Agente FAQ 📚",
                    "escalation_agent": "Escalação 👤",
                    "error_handler": "Sistema",
                }

                agent_name = agent_labels.get(
                    msg.get("agent_used", ""),
                    msg.get("agent_used", "")
                )

                st.caption(f"Respondido por: {agent_name}")

            # Exibe fontes utilizadas pelo agente (RAG / contexto externo)
            sources = msg.get("sources", [])
            if sources:
                with st.expander("📚 Fontes consultadas"):
                    for source in sources:
                        st.caption(source.get("source", ""))

    # Botão para resetar a conversa
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Nova"):
            st.session_state["chat_history"] = []
            st.session_state["conversation_id"] = None
            st.rerun()

    # Input principal do usuário (componente nativo de chat do Streamlit)
    user_input = st.chat_input("Digite sua mensagem...")

    if user_input:
        dsa_send_message(user_input)


def dsa_send_message(message: str):
    """Envia mensagem ao backend e atualiza o histórico.

    Fluxo:
    1. Adiciona mensagem do usuário ao histórico
    2. Chama API de chat
    3. Atualiza conversation_id (contexto)
    4. Adiciona resposta do agente
    5. Trata erros de integração
    """

    # Adiciona mensagem do usuário imediatamente (UX responsiva)
    st.session_state["chat_history"].append({
        "role": "user",
        "content": message
    })

    # Spinner indica processamento assíncrono
    with st.spinner("Assistente processando sua mensagem..."):
        try:
            response = http.post(
                "/api/v1/chat",
                json={
                    "message": message,
                    "conversation_id": st.session_state.get("conversation_id"),
                },
                timeout=CHAT_TIMEOUT,
            )

            # Levanta exceção se status != 2xx
            response.raise_for_status()

            data = response.json()

            # Mantém contexto da conversa para continuidade
            st.session_state["conversation_id"] = data.get("conversation_id")

            # Adiciona resposta do agente
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": data["response"],
                "agent_used": data.get("agent_used", "unknown"),
                "sources": data.get("sources", []),

                # Marca como nova para aplicar efeito de digitação
                "_new": True,
            })

        except httpx.TimeoutException:
            # Timeout do backend
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": "Desculpe, a resposta está demorando mais que o esperado. Tente novamente.",
                "agent_used": "error_handler",
            })

        except httpx.ConnectError:
            # Falha de conexão
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": "Desculpe, não foi possível conectar ao servidor. Tente novamente.",
                "agent_used": "error_handler",
            })

        except httpx.HTTPStatusError as e:
            # Erros HTTP retornados pela API
            logger.error(f"Erro HTTP no chat: {e.response.status_code}")

            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": "Desculpe, ocorreu um erro. Tente novamente.",
                "agent_used": "error_handler",
            })

    # Força rerun para atualizar UI imediatamente
    st.rerun()


def _dsa_typewriter(text: str, speed: float = 0.015):
    """Exibe texto com efeito de digitação.

    Simula streaming de resposta token a token,
    melhorando percepção de responsividade da IA.
    """

    def _stream():
        for char in text:
            yield char
            time.sleep(speed)

    # write_stream consome gerador e renderiza progressivamente
    st.write_stream(_stream)


