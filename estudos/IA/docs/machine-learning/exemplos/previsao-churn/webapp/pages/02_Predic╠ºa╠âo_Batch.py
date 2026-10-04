# Projeto Desenvolvido na Data Science Academy
"""Página de predição em lote (batch) de churn.

Permite upload de arquivo CSV com dados de múltiplos clientes,
valida as colunas obrigatórias e exibe os resultados com:
- Resumo estatístico (total, churn count, churn rate)
- Tabela colorida por nível de risco
- Download CSV com as predições anexadas

O fluxo é:
1. Upload do CSV pelo usuário
2. Validação das 19 colunas obrigatórias
3. Envio para a API via POST /api/v1/predict/batch
4. Exibição dos resultados com estilização condicional
"""

import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar

st.set_page_config(page_title="Predição Batch", page_icon="\U0001f4c1", layout="wide")

api_client = render_sidebar()

st.title("\U0001f4c1 Predição Batch de Churn")
st.markdown("Faça upload de um arquivo CSV com dados de clientes para predição em lote.")

# Inicializa session_state para persistir resultados entre reruns
if "batch_results" not in st.session_state:
    st.session_state.batch_results = None
if "predictions_history" not in st.session_state:
    st.session_state.predictions_history = []

# As 19 colunas obrigatórias (devem corresponder ao schema CustomerData da API)
REQUIRED_COLUMNS = [
    "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
    "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges",
]

# ---------------------------------------------------------------------------
# Upload e validação do CSV
# ---------------------------------------------------------------------------

uploaded_file = st.file_uploader(
    "Selecione um arquivo CSV",
    type=["csv"],
    help="O arquivo deve conter as colunas necessárias para predição.",
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"Arquivo carregado: {len(df)} registros")

        # Preview das primeiras linhas
        st.subheader("Preview dos Dados")
        st.dataframe(df.head(), use_container_width=True)

        # Verifica se todas as colunas obrigatórias estão presentes
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing_cols:
            st.error(
                f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}"
            )
            st.info(f"Colunas necessárias: {', '.join(REQUIRED_COLUMNS)}")
        else:
            st.success("Todas as colunas obrigatórias encontradas.")

            # Seleciona apenas as colunas necessárias (ignora extras como customerID)
            predict_df = df[REQUIRED_COLUMNS].copy()

            if st.button(
                "Processar Lote", type="primary", use_container_width=True
            ):
                with st.spinner(f"Processando {len(predict_df)} clientes..."):
                    try:
                        # Converte DataFrame para lista de dicionários (formato da API)
                        customers = predict_df.to_dict(orient="records")
                        result = api_client.predict_batch(customers)

                        # Armazena resultado no session_state para persistência
                        st.session_state.batch_results = result

                        # Salva predições no histórico para o dashboard
                        for pred in result.get("predictions", []):
                            st.session_state.predictions_history.append(pred)

                    except ConnectionError:
                        st.error(
                            "Não foi possível conectar à API. "
                            "Verifique se o serviço está rodando."
                        )
                    except Exception as e:
                        st.error(f"Erro ao processar lote: {e}")

    except Exception as e:
        st.error(f"Erro ao ler arquivo CSV: {e}")

# ---------------------------------------------------------------------------
# Exibição dos resultados
# ---------------------------------------------------------------------------

if st.session_state.batch_results is not None:
    result = st.session_state.batch_results
    predictions = result.get("predictions", [])
    summary = result.get("summary", {})

    st.divider()
    st.subheader("Resultados")

    # --- Métricas resumo em 3 colunas ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Clientes", summary.get("total", 0))
    with col2:
        st.metric("Previsão de Churn", summary.get("churn_count", 0))
    with col3:
        churn_rate = summary.get("churn_rate", 0)
        st.metric("Taxa de Churn", f"{churn_rate:.1%}")

    # --- Tabela detalhada com estilização condicional por risco ---
    st.subheader("Predições Detalhadas")

    results_data = []
    for i, pred in enumerate(predictions):
        results_data.append(
            {
                "Cliente": i + 1,
                "Predição": pred["prediction"],
                "Probabilidade": f"{pred['probability']:.1%}",
                "Risco": (
                    "ALTO"
                    if pred["probability"] >= 0.7
                    else "MÉDIO"
                    if pred["probability"] >= 0.4
                    else "BAIXO"
                ),
            }
        )

    results_df = pd.DataFrame(results_data)

    # Aplica cores de fundo condicionais: vermelho (alto), amarelo (médio), verde (baixo)
    st.dataframe(
        results_df.style.apply(
            lambda row: [
                "background-color: #ffcccc"
                if row["Risco"] == "ALTO"
                else "background-color: #fff3cd"
                if row["Risco"] == "MÉDIO"
                else "background-color: #d4edda"
            ]
            * len(row),
            axis=1,
        ),
        use_container_width=True,
        hide_index=True,
    )

    # --- Download CSV com predições anexadas ao arquivo original ---
    if uploaded_file is not None:
        try:
            # Relê o arquivo original (seek(0) volta ao início do buffer)
            uploaded_file.seek(0)
            original_df = pd.read_csv(uploaded_file)

            # Adiciona colunas de predição ao DataFrame original
            original_df["Churn_Predicao"] = [
                p["prediction"] for p in predictions
            ]
            original_df["Churn_Probabilidade"] = [
                round(p["probability"], 4) for p in predictions
            ]

            csv_data = original_df.to_csv(index=False)
            st.download_button(
                label="Download CSV com Predições",
                data=csv_data,
                file_name="predicoes_churn.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception:
            pass
