# Projeto Desenvolvido na Data Science Academy
"""Entry point da aplicação web Streamlit de previsão de churn.

Configura a página principal com informações do projeto e instruções de uso.

No Streamlit, este arquivo é o ponto de entrada da aplicação. O framework
detecta automaticamente os arquivos na pasta pages/ e cria a navegação
no sidebar. Cada arquivo em pages/ vira uma página acessível pelo menu lateral.

A aplicação NÃO acessa o modelo de ML diretamente — toda comunicação é
feita via chamadas HTTP para a API REST usando o APIClient.
"""

import os

import streamlit as st

# ---------------------------------------------------------------------------
# Configuração global da página (deve ser a primeira chamada Streamlit)
# Estas configurações se aplicam à página principal e definem valores
# padrão para layout, ícone e estado da sidebar.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Previsão de Churn - Telecom",
    page_icon="\U0001f4c9",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Carrega CSS customizado para estilização da interface.
# O CSS é injetado via st.markdown com unsafe_allow_html=True,
# permitindo personalizar elementos visuais do Streamlit.
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main() -> None:
    """Renderiza a página principal da aplicação."""

    # Banner customizado com HTML (substitui o header padrão do Streamlit)
    st.markdown(
        '<div class="custom-banner">'
        "<h1>Data Science Academy - Projeto 1</h1>"
        "<p>Engenharia de Software Para Aplicação Web Integrada a Machine Learning via API</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    ### Bem-vindo ao Sistema de Previsão de Churn

    Esta aplicação utiliza **Machine Learning** para prever a probabilidade de
    cancelamento (churn) de clientes de telecomunicações, permitindo ações
    proativas de retenção.

    ---

    #### Como usar

    Navegue pelas páginas no menu lateral:

    1. **Predição Individual** — Insira os dados de um cliente e obtenha a
       predição de churn com probabilidade e explicabilidade.

    2. **Predição Batch** — Faça upload de um arquivo CSV com dados de múltiplos
       clientes para predição em lote.

    3. **Dashboard** — Visualize métricas agregadas e gráficos das predições
       realizadas na sessão.

    ---

    #### Sobre o Modelo

    - **Algoritmo:** Gradient Boosting Classifier (scikit-learn)
    - **Dataset:** Telco Customer Churn (Kaggle/IBM)
    - **Features:** 19 variáveis (demográficas, serviços, contrato)
    - **Variável alvo:** Churn (Sim/Não)

    #### Arquitetura

    ```
    App Web (Streamlit) → API REST (FastAPI) → Modelo ML (scikit-learn)
    ```

    Todas as predições são realizadas via API REST. A aplicação web não tem
    acesso direto ao modelo de ML.
    """)

    # Inicializa o session_state do Streamlit para armazenar dados entre páginas.
    # O session_state persiste enquanto a sessão do navegador estiver ativa,
    # permitindo que predições feitas em uma página apareçam no dashboard.
    if "predictions_history" not in st.session_state:
        st.session_state.predictions_history = []
    if "batch_results" not in st.session_state:
        st.session_state.batch_results = None


if __name__ == "__main__":
    main()
