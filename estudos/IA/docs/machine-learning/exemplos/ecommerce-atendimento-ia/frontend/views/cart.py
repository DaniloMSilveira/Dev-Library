# Projeto Desenvolvido na Data Science Academy

"""Página do Carrinho — Responsável por exibir itens, calcular totais e orquestrar o checkout."""

import logging
import httpx
import streamlit as st
from config import FREE_SHIPPING_THRESHOLD, STANDARD_SHIPPING_COST, http

logger = logging.getLogger(__name__)


def dsa_render_cart():
    """Renderiza a página do carrinho.

    Responsabilidades:
    - Exibir itens adicionados ao carrinho
    - Permitir edição de quantidade e remoção
    - Calcular subtotal, frete e total
    - Realizar fluxo de checkout (cliente + pedido)
    - Exibir confirmação de pedido concluído

    Toda a persistência de estado é feita via st.session_state.
    """

    st.markdown("## Carrinho de Compras")

    # Recupera e remove (pop) o último pedido concluído do session_state.
    # Isso garante que o resumo seja exibido apenas uma vez após o checkout.
    last_order = st.session_state.pop("last_order", None)

    if last_order:
        # Feedback de sucesso após finalização da compra
        st.success("Pedido realizado com sucesso!")

        # Exibição de informações principais do pedido
        st.markdown(f"**Número do pedido:** {last_order['id']}")
        st.markdown(
            f"**Código de rastreamento:** {last_order.get('tracking_code', 'Em breve')}"
        )
        st.markdown(f"**Total:** R$ {last_order['total']:,.2f}")

        # Navegação assistida para tela de pedidos
        if st.button("Acompanhar Pedido"):
            st.session_state["navigate_to"] = "Meus Pedidos"
            st.rerun()

        # Interrompe renderização do restante da página
        return

    # Recupera carrinho atual do estado da sessão
    cart = st.session_state.get("cart", [])

    # Caso não haja itens no carrinho
    if not cart:
        st.info("Seu carrinho está vazio.")

        # CTA para voltar à navegação de produtos
        if st.button("Explorar Produtos"):
            st.session_state["navigate_to"] = "Produtos"
            st.rerun()

        return

    subtotal = 0.0

    # Lista de índices a serem removidos após iteração
    # Evita modificar lista enquanto está sendo percorrida
    items_to_remove = []

    # Itera sobre itens do carrinho
    for i, item in enumerate(cart):
        product = item["product"]

        # Layout em colunas para estrutura de linha de item
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 0.5])

        with col1:
            # Nome do produto
            st.markdown(f"**{product['name']}**")

        with col2:
            # Preço unitário
            st.markdown(f"R$ {product['price']:,.2f}")

        with col3:
            # Input de quantidade com persistência por key única
            new_qty = st.number_input(
                "Qtd",
                min_value=1,
                max_value=10,
                value=item["quantity"],
                key=f"cart-qty-{i}",
                label_visibility="collapsed",
            )

            # Atualiza quantidade diretamente no estado
            cart[i]["quantity"] = new_qty

        with col4:
            # Cálculo do total por item
            item_total = product["price"] * new_qty
            subtotal += item_total

            st.markdown(f"R$ {item_total:,.2f}")

        with col5:
            # Botão de remoção do item
            if st.button("🗑️ Remover", key=f"remove-{i}"):
                items_to_remove.append(i)

    # Remoção segura dos itens (de trás para frente)
    # Evita deslocamento de índices durante pop()
    for idx in sorted(items_to_remove, reverse=True):
        cart.pop(idx)

    # Atualiza estado global do carrinho
    st.session_state["cart"] = cart

    # Força rerun para refletir remoção imediatamente
    if items_to_remove:
        st.rerun()

    st.markdown("---")

    # Regra de negócio: frete grátis acima de um valor mínimo
    shipping = 0.0 if subtotal >= FREE_SHIPPING_THRESHOLD else STANDARD_SHIPPING_COST

    # Cálculo do total final
    total = subtotal + shipping

    # Layout do resumo do pedido
    col_r1, col_r2 = st.columns(2)

    with col_r2:
        st.markdown("### Resumo do Pedido")
        st.markdown(f"Subtotal: **R$ {subtotal:,.2f}**")

        # Exibição condicional do frete
        if shipping == 0:
            st.markdown("Frete: **Grátis** ✅")
        else:
            st.markdown(f"Frete estimado: **R$ {shipping:,.2f}**")

        st.markdown(f"### Total: R$ {total:,.2f}")

    st.markdown("---")

    # Seção de checkout
    st.markdown("### Finalizar Compra")

    # Coleta de dados básicos do cliente
    email = st.text_input("Seu e-mail")
    name = st.text_input("Seu nome")

    # Botão principal de ação
    if st.button("Finalizar Compra", type="primary"):

        # Validação simples de input
        if not email or not name:
            st.error("Preencha seu nome e e-mail.")
            return

        if "@" not in email:
            st.error("E-mail inválido. Informe um e-mail válido.")
            return

        try:
            # Criação/registro do cliente na API
            customer_resp = http.post(
                "/api/v1/customers",
                json={"name": name, "email": email},
            )
            customer_resp.raise_for_status()
            customer = customer_resp.json()

            # Montagem dos itens do pedido no formato esperado pela API
            order_items = []
            for item in cart:
                order_items.append({
                    "product_id": item["product"]["id"],
                    "quantity": item["quantity"],
                })

            # Criação do pedido
            order_resp = http.post(
                "/api/v1/orders",
                json={
                    "customer_id": customer["id"],
                    "items": order_items,
                },
            )
            order_resp.raise_for_status()
            order = order_resp.json()

            # Limpa carrinho após sucesso
            st.session_state["cart"] = []

            # Armazena contexto do cliente e último pedido
            st.session_state["customer_id"] = customer["id"]
            st.session_state["last_order"] = order

            # Reexecuta app para mostrar tela de sucesso
            st.rerun()

        except httpx.HTTPStatusError as e:
            # Erros retornados pela API (4xx, 5xx)
            error_detail = ""
            try:
                error_detail = e.response.json().get("detail", "")
            except (ValueError, AttributeError):
                error_detail = str(e)

            st.error(f"Erro ao finalizar compra: {error_detail or str(e)}")

        except httpx.TimeoutException:
            # Timeout de comunicação com backend
            st.error("O servidor está demorando. Tente novamente.")

        except httpx.ConnectError:
            # Falha de conexão (API fora do ar, rede, etc)
            st.error("Erro de conexão. Verifique se a API está rodando.")


            