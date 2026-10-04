# Projeto Desenvolvido na Data Science Academy
"""Página de Pedidos — Interface para consulta e acompanhamento de pedidos."""

import logging
import httpx
import streamlit as st
from config import http

logger = logging.getLogger(__name__)

# Configuração visual e semântica dos status de pedidos.
# Cada status possui:
# - emoji: representação visual
# - label: descrição amigável
# - progress: percentual usado na barra de progresso
STATUS_CONFIG = {
    "confirmed": {"emoji": "🔵", "label": "Confirmado", "progress": 25},
    "processing": {"emoji": "🟡", "label": "Em preparação", "progress": 50},
    "shipped": {"emoji": "🟠", "label": "Enviado", "progress": 75},
    "delivered": {"emoji": "🟢", "label": "Entregue", "progress": 100},
    "cancelled": {"emoji": "🔴", "label": "Cancelado", "progress": 0},
}


def dsa_render_orders():
    """Renderiza a página de pedidos.

    Responsabilidades:
    - Buscar pedidos automaticamente (se usuário identificado)
    - Permitir busca manual por ID, e-mail ou código de rastreio
    - Exibir status, progresso e itens do pedido
    - Integrar com chat para dúvidas contextuais
    """

    st.markdown("## Meus Pedidos")

    # Recupera o customer_id do estado da sessão.
    # Esse valor é definido no checkout e permite auto-load dos pedidos.
    customer_id = st.session_state.get("customer_id")

    orders = []

    # Carregamento automático dos pedidos do cliente
    if customer_id:
        try:
            resp = http.get(f"/api/v1/orders/customer/{customer_id}")

            if resp.is_success:
                data = resp.json()

                # Suporta dois formatos:
                # - lista direta
                # - objeto com chave "items" (padrão paginado)
                orders = data.get("items", data) if isinstance(data, dict) else data

        except httpx.TimeoutException:
            st.warning("O servidor está demorando. Tente buscar manualmente.")

        except httpx.ConnectError:
            st.warning("Não foi possível conectar ao servidor.")

        except httpx.HTTPError:
            logger.warning(f"Falha ao carregar pedidos do cliente {customer_id}")

    # Seção de busca manual
    st.markdown("### Buscar Pedido")

    search_input = st.text_input("Informe seu e-mail ou número do pedido")

    # Dispara busca manual
    if st.button("Buscar") and search_input:
        orders = []

        # Sanitização básica de input
        search_input = search_input.strip()

        try:
            # Estratégia 1: busca por ID do pedido (ex: ORD-XXXX)
            if search_input.upper().startswith("ORD"):
                resp = http.get(f"/api/v1/orders/{search_input.upper()}")

                if resp.is_success:
                    orders = [resp.json()]

            # Estratégia 2: busca por e-mail
            if not orders and "@" in search_input:
                customer_resp = http.get(f"/api/v1/customers/email/{search_input}")

                if customer_resp.is_success:
                    customer = customer_resp.json()

                    orders_resp = http.get(
                        f"/api/v1/orders/customer/{customer['id']}"
                    )

                    if orders_resp.is_success:
                        data = orders_resp.json()
                        orders = (
                            data.get("items", data)
                            if isinstance(data, dict)
                            else data
                        )

            # Estratégia 3: busca por código de rastreio
            if not orders:
                resp = http.get(f"/api/v1/orders/tracking/{search_input}")

                if resp.is_success:
                    orders = [resp.json()]

        except httpx.TimeoutException:
            st.error("O servidor está demorando para responder. Tente novamente.")
            return

        except httpx.ConnectError:
            st.error("Erro de conexão com o servidor.")
            return

        except httpx.HTTPError as e:
            logger.error(f"Erro ao buscar pedidos: {e}")
            st.error("Erro ao buscar pedidos. Tente novamente.")
            return

    # Caso nenhum pedido seja encontrado
    if not orders:
        st.info(
            "Nenhum pedido encontrado. Faça uma compra ou busque pelo e-mail/número do pedido."
        )
        return

    st.markdown(f"**{len(orders)} pedido(s) encontrado(s)**")
    st.markdown("---")

    # Renderização de cada pedido
    for order in orders:

        # Recupera status e configuração associada
        status = order.get("status", "confirmed")
        config = STATUS_CONFIG.get(status, STATUS_CONFIG["confirmed"])

        # Cada pedido é exibido em um expander (accordion)
        with st.expander(
            f"{config['emoji']} Pedido {order['id']} — {config['label']} "
            f"| R$ {order['total']:,.2f}"
        ):

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Status:** {config['emoji']} {config['label']}")

                # Data simplificada (YYYY-MM-DD)
                st.markdown(f"**Data:** {order['created_at'][:10]}")

                # Código de rastreio pode não existir em fases iniciais
                tracking = order.get("tracking_code") or "Ainda não disponível"
                st.markdown(f"**Rastreamento:** {tracking}")

            with col2:
                st.markdown(f"**Total:** R$ {order['total']:,.2f}")

            # Exibe progresso apenas se não estiver cancelado
            if status != "cancelled":

                # Barra de progresso baseada no status
                st.progress(config["progress"] / 100)

                # Representação visual das etapas do pedido
                steps = ["Confirmado", "Preparação", "Enviado", "Entregue"]
                step_cols = st.columns(4)

                for i, step in enumerate(steps):
                    with step_cols[i]:
                        progress_pct = (i + 1) * 25

                        # Marca etapas concluídas
                        if config["progress"] >= progress_pct:
                            st.markdown(f"✅ {step}")
                        else:
                            st.markdown(f"⬜ {step}")

            # Lista de itens do pedido
            st.markdown("**Itens:**")

            for item in order.get("items", []):
                name = item.get("product_name", item["product_id"])

                st.markdown(
                    f"- {name} (x{item['quantity']}) — R$ {item['unit_price']:,.2f}"
                )

            # Integração com chat contextual
            # Permite continuar a jornada com IA usando contexto do pedido
            if st.button("Perguntar ao assistente", key=f"ask-order-{order['id']}"):

                st.session_state["chat_initial_message"] = (
                    f"Qual o status do meu pedido {order['id']}?"
                )

                st.session_state["navigate_to"] = "Chat com IA"

                st.rerun()


