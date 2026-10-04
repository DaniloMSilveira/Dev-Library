# Projeto Desenvolvido na Data Science Academy

"""Product Card — Componente reutilizável de exibição de produto."""

import streamlit as st

# Mapeia categorias de produto para ícones visuais.
# Isso melhora a experiência no frontend, tornando a identificação
# dos produtos mais rápida e amigável para o usuário.
CATEGORY_ICONS = {
    "smartphones": "📱",
    "notebooks": "💻",
    "tablets": "📟",
    "acessorios": "🎧",
    "smart_home": "🏠",
}


def dsa_render_product_card(product: dict, col) -> bool:
    """Renderiza um card resumido de produto dentro de uma coluna do Streamlit.

    Retorna:
        bool: True se o botão "Ver Detalhes" for clicado, caso contrário False.
    """

    # Recupera o ícone com base na categoria do produto.
    # Caso a categoria não esteja mapeada, usa um ícone genérico.
    icon = CATEGORY_ICONS.get(product.get("category", ""), "📦")

    # O "with col" garante que todo o conteúdo abaixo seja renderizado
    # dentro da coluna recebida como argumento.
    with col:
        # Exibe nome do produto, truncando para evitar quebra visual excessiva no layout.
        st.markdown(f"### {icon} {product['name'][:40]}")

        # Exibe a marca em formato secundário, com menos destaque visual.
        st.caption(product.get("brand", ""))

        # Exibe o preço formatado em moeda brasileira.
        price = product.get("price", 0)
        st.markdown(f"**R$ {price:,.2f}**")

        # Exibe avaliação média e número de reviews.
        # As estrelas são calculadas de forma simples, usando apenas a parte inteira da nota.
        rating = product.get("rating", 0)
        reviews = product.get("reviews_count", 0)
        stars = "⭐" * int(rating)
        st.caption(f"{stars} ({rating}) — {reviews} avaliações")

        # Exibe status de disponibilidade com base no estoque.
        stock = product.get("stock", 0)
        if stock > 0:
            st.caption(f"✅ Em estoque ({stock} un.)")
        else:
            st.caption("❌ Indisponível")

        # Botão para abrir ou navegar para a visualização detalhada do produto.
        # A key única evita conflito entre botões renderizados em loops/listas.
        return st.button("Ver Detalhes", key=f"detail-{product['id']}")


def dsa_render_product_details(product: dict):
    """Renderiza a visualização detalhada de um produto."""

    # Cabeçalho principal com nome do produto.
    st.markdown(f"## {product['name']}")

    # Informações básicas do produto.
    st.markdown(f"**Marca:** {product.get('brand', '')}")
    st.markdown(f"**Categoria:** {product.get('category', '')}")

    # Descrição livre do produto.
    st.markdown(product.get("description", ""))

    # Preço com mais destaque visual na tela de detalhes.
    st.markdown(f"### R$ {product.get('price', 0):,.2f}")

    # Especificações técnicas do produto.
    # Espera um dicionário no formato chave: valor.
    specs = product.get("specs", {})
    if specs:
        st.markdown("#### Especificações")
        for key, value in specs.items():
            st.markdown(f"- **{key}:** {value}")

    # Divide a área em duas colunas para separar ações do usuário.
    col1, col2 = st.columns(2)

    with col1:
        # Permite ao usuário selecionar a quantidade desejada.
        # O limite máximo é fixado em 10 por simplicidade de interface.
        qty = st.number_input(
            "Quantidade",
            min_value=1,
            max_value=10,
            value=1,
            key=f"qty-{product['id']}"
        )

        # Adiciona o produto ao carrinho armazenado em session_state.
        # session_state permite manter dados entre reruns do Streamlit.
        if st.button("Adicionar ao Carrinho", key=f"add-{product['id']}"):
            cart = st.session_state.get("cart", [])
            cart.append({"product": product, "quantity": qty})
            st.session_state["cart"] = cart

            # Feedback visual imediato para o usuário.
            st.success(f"{product['name']} adicionado ao carrinho!")

    with col2:
        # Prepara uma mensagem inicial para o chat com IA sobre o produto atual.
        # Também define a navegação desejada e força rerun da aplicação,
        # permitindo redirecionamento interno baseado no estado.
        if st.button("Perguntar ao assistente", key=f"ask-{product['id']}"):
            st.session_state["chat_initial_message"] = (
                f"Me fale sobre o produto {product['name']} (ID: {product['id']})"
            )
            st.session_state["navigate_to"] = "Chat com IA"

            # Reexecuta o app para que a navegação/estado atualizado seja refletido na interface.
            st.rerun()


            