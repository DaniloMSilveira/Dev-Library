# Projeto Desenvolvido na Data Science Academy

"""Sidebar — Componente de navegação lateral com menu, suporte e informações da loja."""

import streamlit as st


def dsa_render_sidebar() -> str:
    """Renderiza a sidebar da aplicação e retorna a página selecionada.

    A sidebar centraliza:
    - Navegação principal entre páginas
    - Indicação dinâmica da quantidade de itens no carrinho
    - Mensagens informativas e de suporte
    - Informações institucionais da loja

    Retorno:
        str: Nome da página selecionada, já normalizado para uso no roteamento.
    """

    # Todo o bloco abaixo será renderizado dentro da barra lateral do Streamlit.
    with st.sidebar:

        # Título principal da aplicação/loja exibido no topo da sidebar.
        st.markdown("# Tech Store Brasil")

        # Separador visual para organizar melhor os blocos da interface.
        st.markdown("---")

        # Recupera o carrinho salvo no session_state.
        # Caso ainda não exista, usa lista vazia como padrão.
        cart_count = len(st.session_state.get("cart", []))

        # O rótulo do menu é dinâmico:
        # exibe a quantidade de itens quando o carrinho não está vazio.
        cart_label = f"Carrinho ({cart_count})" if cart_count > 0 else "Carrinho"

        # Componente principal de navegação.
        # O st.radio funciona como um menu de seleção única entre páginas.
        # O label fica oculto para manter a interface mais limpa.
        # A key fixa garante persistência do estado do componente entre reruns.
        page = st.radio(
            "Navegação",
            options=["Home", "Produtos", cart_label, "Meus Pedidos", "Chat com IA"],
            label_visibility="collapsed",
            key="nav_radio",
        )

        # Novo separador visual entre navegação e conteúdo informativo.
        st.markdown("---")

        # Mensagem de transparência sobre limitações da IA.
        # Isso ajuda a alinhar expectativa do usuário e reforça fallback humano.
        st.info(
            "A IA pode cometer erros. Se preferir, solicite no chat para "
            "**falar com um atendente humano**."
        )

        # Bloco colapsável para suporte.
        # Mantém a sidebar mais limpa, exibindo detalhes apenas quando necessário.
        with st.expander("Precisa de ajuda?"):
            st.markdown(
                "No caso de dúvidas entre em contato com o "
                "Suporte DSA: **suporte@datascienceacademy**"
            )

        # Rodapé visual da sidebar.
        st.markdown("---")

        # Informação institucional e promessa de disponibilidade do atendimento.
        st.markdown("*Atendimento 24h via IA*")

        # Identificação da marca/projeto.
        st.markdown("Tech Store Brasil &copy; Data Science Academy")

        # Link institucional da organização.
        st.markdown(
            "[www.datascienceacademy.com.br](https://www.datascienceacademy.com.br)"
        )

    # Normalização do valor retornado:
    # como o rótulo do carrinho é dinâmico ("Carrinho" ou "Carrinho (N)"),
    # transformamos qualquer variação contendo "Carrinho" no valor fixo "Carrinho".
    #
    # Isso simplifica o roteamento no app principal, evitando condicionais
    # dependentes da quantidade de itens.
    if "Carrinho" in page:
        return "Carrinho"

    return page


    