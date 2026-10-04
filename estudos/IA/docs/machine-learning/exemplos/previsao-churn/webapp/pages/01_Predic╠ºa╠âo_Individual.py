# Projeto Desenvolvido na Data Science Academy
"""Página de predição individual de churn.

Exibe um formulário com os 19 campos do dataset para entrada de dados
de um cliente e mostra o resultado da predição com:
- Classe predita (Sim/Não)
- Probabilidade de churn (0% a 100%)
- Nível de risco (Alto/Médio/Baixo)
- Gráfico de feature importance (top 10 features)

No Streamlit, st.form() agrupa widgets e só envia os dados quando o
botão submit é clicado. Isso evita reruns desnecessários da página.
"""

import plotly.graph_objects as go
import streamlit as st

from components.sidebar import render_sidebar

# Configuração da página (obrigatório ser a primeira chamada Streamlit)
st.set_page_config(page_title="Predição Individual", page_icon="\U0001f464", layout="wide")

# Renderiza a sidebar e obtém o cliente da API
api_client = render_sidebar()

st.title("\U0001f464 Predição Individual de Churn")
st.markdown("Preencha os dados do cliente para obter a predição de churn.")

# Inicializa session_state para compartilhar histórico com o dashboard
if "predictions_history" not in st.session_state:
    st.session_state.predictions_history = []

# ---------------------------------------------------------------------------
# Formulário de entrada de dados
# st.form() agrupa todos os widgets e só envia quando o botão é clicado.
# Os valores dos campos correspondem exatamente aos Literal types
# definidos no schema CustomerData da API (validação Pydantic).
# ---------------------------------------------------------------------------

with st.form("prediction_form"):

    # --- Dados Pessoais ---
    st.subheader("Dados Pessoais")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        gender = st.selectbox("Gênero", ["Male", "Female"])
    with col2:
        senior_citizen = st.selectbox("Idoso", [0, 1], format_func=lambda x: "Sim" if x == 1 else "Não")
    with col3:
        partner = st.selectbox("Parceiro(a)", ["Yes", "No"])
    with col4:
        dependents = st.selectbox("Dependentes", ["Yes", "No"])

    # --- Serviços Contratados ---
    st.subheader("Serviços Contratados")
    col1, col2, col3 = st.columns(3)

    with col1:
        phone_service = st.selectbox("Serviço Telefônico", ["Yes", "No"])
        multiple_lines = st.selectbox(
            "Múltiplas Linhas", ["Yes", "No", "No phone service"]
        )
    with col2:
        internet_service = st.selectbox(
            "Serviço de Internet", ["DSL", "Fiber optic", "No"]
        )
        online_security = st.selectbox(
            "Segurança Online", ["Yes", "No", "No internet service"]
        )
        online_backup = st.selectbox(
            "Backup Online", ["Yes", "No", "No internet service"]
        )
    with col3:
        device_protection = st.selectbox(
            "Proteção de Dispositivo", ["Yes", "No", "No internet service"]
        )
        tech_support = st.selectbox(
            "Suporte Técnico", ["Yes", "No", "No internet service"]
        )
        streaming_tv = st.selectbox(
            "Streaming TV", ["Yes", "No", "No internet service"]
        )

    streaming_movies = st.selectbox(
        "Streaming Filmes", ["Yes", "No", "No internet service"]
    )

    # --- Informações de Contrato ---
    st.subheader("Informações de Contrato")
    col1, col2, col3 = st.columns(3)

    with col1:
        contract = st.selectbox(
            "Tipo de Contrato",
            ["Month-to-month", "One year", "Two year"],
        )
        paperless_billing = st.selectbox("Faturamento Digital", ["Yes", "No"])
    with col2:
        payment_method = st.selectbox(
            "Método de Pagamento",
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
        )
        tenure = st.number_input(
            "Meses de Permanência", min_value=0, max_value=72, value=12
        )
    with col3:
        monthly_charges = st.number_input(
            "Cobranças Mensais (USD)",
            min_value=0.0,
            max_value=200.0,
            value=50.0,
            step=0.05,
        )
        total_charges = st.number_input(
            "Cobranças Totais (USD)",
            min_value=0.0,
            max_value=10000.0,
            value=600.0,
            step=0.05,
        )

    submitted = st.form_submit_button(
        "Prever Churn", type="primary", use_container_width=True
    )

# ---------------------------------------------------------------------------
# Processamento da predição (executado ao clicar no botão)
# ---------------------------------------------------------------------------

if submitted:
    # Monta o dicionário com os 19 campos no formato esperado pela API
    customer_data = {
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
    }

    with st.spinner("Realizando predição..."):
        try:
            # Chama a API REST via POST /api/v1/predict
            result = api_client.predict(customer_data)

            # Salva no histórico para exibição no dashboard
            st.session_state.predictions_history.append(result)

            st.divider()
            st.subheader("Resultado da Predição")

            # --- Indicadores principais em 3 colunas ---
            col1, col2, col3 = st.columns(3)

            is_churn = result["prediction"] == "Sim"
            probability = result["probability"]

            with col1:
                if is_churn:
                    st.error(f"### \u26a0\ufe0f CHURN: {result['prediction']}")
                else:
                    st.success(f"### \u2705 CHURN: {result['prediction']}")

            with col2:
                st.metric(
                    "Probabilidade de Churn",
                    f"{probability:.1%}",
                )

            # Classificação de risco baseada na probabilidade
            with col3:
                if probability >= 0.7:
                    st.error("Risco: **ALTO**")
                    st.caption("Ação urgente de retenção recomendada.")
                elif probability >= 0.4:
                    st.warning("Risco: **MÉDIO**")
                    st.caption("Monitorar e oferecer incentivos.")
                else:
                    st.success("Risco: **BAIXO**")
                    st.caption("Cliente com boa retenção.")

            # Barra visual de probabilidade
            st.progress(probability, text=f"Probabilidade: {probability:.1%}")

            # --- Gráfico de Feature Importance (Plotly) ---
            feature_imp = result.get("feature_importance", [])
            if feature_imp:
                st.subheader("Features Mais Importantes")

                names = [f["feature"] for f in feature_imp[:10]]
                values = [f["importance"] for f in feature_imp[:10]]

                fig = go.Figure(
                    go.Bar(
                        x=values,
                        y=names,
                        orientation="h",
                        marker_color="#3498db",
                    )
                )
                fig.update_layout(
                    title="Top 10 Features para esta Predição",
                    xaxis_title="Importância",
                    yaxis={"autorange": "reversed"},
                    height=400,
                    margin={"l": 200},
                )
                st.plotly_chart(fig, use_container_width=True)

        except ConnectionError:
            st.error(
                "Não foi possível conectar à API. "
                "Verifique se o serviço está rodando."
            )
        except Exception as e:
            st.error(f"Erro ao realizar predição: {e}")
