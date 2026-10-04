# Projeto Desenvolvido na Data Science Academy

"""Página de Produtos — Catálogo com filtros, grid e navegação para detalhes."""

import logging
import httpx
import streamlit as st
from components.product_card import dsa_render_product_card, dsa_render_product_details
from config import MAX_PRODUCT_PRICE, http

logger = logging.getLogger(__name__)


def dsa_render_products():
    """Renderiza a página de catálogo de produtos.

    Responsabilidades:
    - Aplicar filtros (categoria, preço, busca)
    - Integrar com API de produtos
    - Ordenar resultados no frontend
    - Exibir produtos em grid
    - Gerenciar paginação
    - Navegar entre lista e detalhe de produto
    """

    st.markdown("## Produtos")

    # Filtros organizados em layout horizontal
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        # Filtro por categoria
        category = st.selectbox(
            "Categoria",
            ["Todas", "smartphones", "notebooks", "tablets", "acessorios", "smart_home"],
        )

    with col_f2:
        # Filtro de faixa de preço (range)
        price_range = st.slider(
            "Faixa de preço (R$)",
            0,
            MAX_PRODUCT_PRICE,
            (0, MAX_PRODUCT_PRICE),
            step=100
        )

    with col_f3:
        # Ordenação aplicada no frontend
        # Evita nova chamada à API a cada mudança
        sort_by = st.selectbox(
            "Ordenar por",
            ["Nome A-Z", "Menor Preço", "Maior Preço", "Melhor Avaliação"],
        )

    with col_f4:
        # Busca textual por nome
        search = st.text_input("Buscar por nome")

    # Página atual armazenada no estado da sessão
    page = st.session_state.get("products_page", 1)

    # Montagem dinâmica dos parâmetros da API
    params = {"page": page, "per_page": 12}

    if category != "Todas":
        params["category"] = category

    if price_range[0] > 0:
        params["min_price"] = price_range[0]

    if price_range[1] < MAX_PRODUCT_PRICE:
        params["max_price"] = price_range[1]

    if search:
        params["search"] = search

    try:
        # Chamada à API de produtos
        response = http.get("/api/v1/products", params=params)
        response.raise_for_status()

        data = response.json()

        # Suporte a resposta paginada
        products = data.get("items", [])
        total = data.get("total", 0)

    except httpx.TimeoutException:
        st.warning("O servidor está demorando. Tente novamente.")
        return

    except httpx.ConnectError:
        st.error("Erro ao conectar ao servidor. Verifique se a API está rodando.")
        return

    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao carregar produtos: {e.response.status_code}")
        st.error("Erro ao carregar produtos.")
        return

    # Ordenação local (client-side)
    # Trade-off: menor latência vs inconsistência com backend
    if sort_by == "Menor Preço":
        products.sort(key=lambda p: p.get("price", 0))

    elif sort_by == "Maior Preço":
        products.sort(key=lambda p: p.get("price", 0), reverse=True)

    elif sort_by == "Melhor Avaliação":
        products.sort(key=lambda p: p.get("rating", 0), reverse=True)

    # Informação de contexto para o usuário
    st.caption(f"{total} produtos encontrados")
    st.markdown("---")

    # Caso não haja resultados
    if total == 0:
        st.info("Nenhum produto encontrado com esses critérios. Tente ajustar os filtros.")
        return

    # Controle de navegação entre lista e detalhe
    selected = st.session_state.get("selected_product")

    if selected:
        # Renderiza página de detalhe do produto
        dsa_render_product_details(selected)

        # Botão de retorno ao catálogo
        if st.button("← Voltar ao catálogo"):
            st.session_state.pop("selected_product")
            st.rerun()

        return

    # Renderização do grid de produtos (3 colunas)
    for i in range(0, len(products), 3):

        cols = st.columns(3)

        for j, col in enumerate(cols):
            idx = i + j

            if idx < len(products):
                # Renderiza card do produto
                clicked = dsa_render_product_card(products[idx], col)

                # Se clicar, salva no estado e navega para detalhe
                if clicked:
                    st.session_state["selected_product"] = products[idx]
                    st.rerun()

    # Paginação (somente se houver mais de uma página)
    if total > 12:

        # Cálculo do número total de páginas
        total_pages = (total + 11) // 12  # ceil(total / 12)

        col_prev, col_info, col_next = st.columns([1, 2, 1])

        with col_info:
            st.caption(f"Página {page} de {total_pages}")

        with col_prev:
            # Navegação para página anterior
            if page > 1 and st.button("← Anterior"):
                st.session_state["products_page"] = page - 1
                st.rerun()

        with col_next:
            # Navegação para próxima página
            if page < total_pages and st.button("Próximo →"):
                st.session_state["products_page"] = page + 1
                st.rerun()


