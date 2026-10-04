# Projeto Desenvolvido na Data Science Academy
"""Componente de sidebar compartilhado entre as páginas do webapp.

Exibe informações de status da API e métricas do modelo na barra lateral.

Este componente é importado por todas as páginas (pages/*.py) e garante
que a sidebar tenha conteúdo consistente em toda a aplicação. Também
retorna a instância do APIClient configurada, que as páginas usam para
comunicação com a API REST.

O header "Menu de Operações" é renderizado via CSS (style.css) usando
um pseudo-elemento ::before no seletor da navegação do Streamlit,
pois o Streamlit gera a navegação automaticamente e não permite
inserir conteúdo acima dela via Python.
"""

import streamlit as st

from utils.api_client import APIClient


def render_sidebar() -> APIClient:
    """Renderiza a sidebar com status da API e informações do modelo.

    Returns:
        Instância configurada do APIClient para uso nas páginas.
    """
    api_client = APIClient()

    with st.sidebar:
        # --- Seção 1: Status da API (health check) ---
        st.subheader("Status da API")
        try:
            health = api_client.health_check()
            if health.get("status") == "healthy":
                st.success("API Online", icon="\u2705")
                if health.get("model_loaded"):
                    st.info("Modelo carregado", icon="\U0001f916")
                else:
                    st.warning("Modelo não carregado", icon="\u26a0\ufe0f")
            else:
                st.error("API com problemas", icon="\u274c")
        except Exception:
            st.error("API Offline", icon="\u274c")
            st.caption("Verifique se a API está rodando.")

        st.divider()

        # --- Seção 2: Métricas do modelo (obtidas via GET /api/v1/model/info) ---
        st.subheader("Modelo")
        try:
            info = api_client.model_info()
            st.metric("Versão", info.get("model_version", "N/A"))

            metrics = info.get("metrics", {})
            if metrics:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
                    st.metric("Recall", f"{metrics.get('recall', 0):.2%}")
                with col2:
                    st.metric("Precision", f"{metrics.get('precision', 0):.2%}")
                    st.metric("F1", f"{metrics.get('f1', 0):.2%}")
        except Exception:
            st.caption("Informações indisponíveis.")

        st.divider()

        # --- Seção 3: Informações de suporte ---
        st.info(
            "No caso de dúvidas entre em contato com o Suporte DSA: "
            "suporte@datascienceacademy.com.br"
        )

    return api_client
