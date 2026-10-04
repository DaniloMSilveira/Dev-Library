# Projeto Desenvolvido na Data Science Academy
"""Entrypoint Streamlit — Aplicação web do e-commerce Tech Store Brasil."""

import streamlit as st

st.set_page_config(
    page_title="Tech Store Brasil - DSA Projeto 2",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("### **Data Science Academy**")
st.markdown("**Engenharia de Software Para Machine Learning — Projeto 2**")
st.markdown("##### **Engenharia de Software Para Aplicação de E-commerce com Atendimento Automatizado via Agentes de IA e RAG com Arquitetura de Microsserviços**")
st.markdown("---")

# Inicialização centralizada de session state
_defaults = {
    "cart": [],
    "customer_id": None,
    "conversation_id": None,
    "chat_history": [],
    "selected_product": None,
    "products_page": 1,
}
for key, value in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

from components.sidebar import dsa_render_sidebar

navigate_to = st.session_state.pop("navigate_to", None)
if navigate_to:
    st.session_state["nav_radio"] = navigate_to

page = dsa_render_sidebar()

if page == "Home":
    from views.home import dsa_render_home
    dsa_render_home()
elif page == "Produtos":
    from views.products import dsa_render_products
    dsa_render_products()
elif page == "Carrinho":
    from views.cart import dsa_render_cart
    dsa_render_cart()
elif page == "Meus Pedidos":
    from views.orders import dsa_render_orders
    dsa_render_orders()
elif page == "Chat com IA":
    from views.chat import dsa_render_chat
    dsa_render_chat()
