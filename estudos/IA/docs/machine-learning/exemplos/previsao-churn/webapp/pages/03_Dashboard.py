# Projeto Desenvolvido na Data Science Academy
"""Página de dashboard com métricas agregadas das predições.

Exibe gráficos interativos (Plotly) e estatísticas das predições
realizadas na sessão atual, incluindo:
- Gráfico de pizza: distribuição de churn (Sim vs Não)
- Histograma: distribuição de probabilidades
- Barras horizontais: feature importance média (top 10)
- Barras verticais: classificação por nível de risco

Os dados são obtidos do session_state do Streamlit, que acumula
todas as predições feitas nas páginas Individual e Batch.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.sidebar import render_sidebar

st.set_page_config(page_title="Dashboard", page_icon="\U0001f4ca", layout="wide")

api_client = render_sidebar()

st.title("\U0001f4ca Dashboard de Predições")

# Inicializa session_state
if "predictions_history" not in st.session_state:
    st.session_state.predictions_history = []

predictions = st.session_state.predictions_history

# Exibe mensagem se não houver predições na sessão
if not predictions:
    st.info(
        "Nenhuma predição realizada nesta sessão. "
        "Utilize as páginas de **Predição Individual** ou **Predição Batch** "
        "para gerar dados para o dashboard."
    )
    st.stop()  # Interrompe a execução da página aqui

st.success(f"Total de predições na sessão: {len(predictions)}")

# Prepara DataFrame com os dados das predições
pred_data = []
for pred in predictions:
    pred_data.append(
        {
            "prediction": pred["prediction"],
            "probability": pred["probability"],
        }
    )

df = pd.DataFrame(pred_data)

# ---------------------------------------------------------------------------
# Métricas gerais (cards no topo)
# ---------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

total = len(df)
churn_count = (df["prediction"] == "Sim").sum()
no_churn_count = total - churn_count
avg_prob = df["probability"].mean()

with col1:
    st.metric("Total de Predições", total)
with col2:
    st.metric("Previsão Churn", int(churn_count))
with col3:
    st.metric("Previsão Não Churn", int(no_churn_count))
with col4:
    st.metric("Probabilidade Média", f"{avg_prob:.1%}")

st.divider()

# ---------------------------------------------------------------------------
# Gráficos: distribuição de churn e histograma de probabilidades
# ---------------------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição de Churn Predito")

    # Gráfico de rosca (donut chart) — Plotly
    churn_dist = df["prediction"].value_counts()
    fig = go.Figure(
        data=[
            go.Pie(
                labels=churn_dist.index,
                values=churn_dist.values,
                hole=0.4,  # hole > 0 cria gráfico de rosca
                marker_colors=["#2ecc71", "#e74c3c"],
            )
        ]
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribuição de Probabilidade")

    # Histograma colorido por classe predita — Plotly Express
    fig = px.histogram(
        df,
        x="probability",
        nbins=20,
        color="prediction",
        color_discrete_map={"Sim": "#e74c3c", "Não": "#2ecc71"},
        labels={"probability": "Probabilidade", "prediction": "Churn"},
    )
    fig.update_layout(
        xaxis_title="Probabilidade de Churn",
        yaxis_title="Contagem",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Feature importance agregada (média das importâncias de todas as predições)
# ---------------------------------------------------------------------------

all_features: dict[str, list[float]] = {}
for pred in predictions:
    for feat in pred.get("feature_importance", []):
        name = feat["feature"]
        if name not in all_features:
            all_features[name] = []
        all_features[name].append(feat["importance"])

if all_features:
    st.divider()
    st.subheader("Features que Mais Contribuem para Churn")

    # Calcula a média de importância de cada feature
    avg_importance = {
        name: sum(values) / len(values) for name, values in all_features.items()
    }
    sorted_features = sorted(
        avg_importance.items(), key=lambda x: x[1], reverse=True
    )[:10]

    names = [f[0] for f in sorted_features]
    values = [f[1] for f in sorted_features]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker_color="#3498db",
        )
    )
    fig.update_layout(
        title="Top 10 Features (Importância Média)",
        xaxis_title="Importância Média",
        yaxis={"autorange": "reversed"},
        height=400,
        margin={"l": 200},
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Classificação por nível de risco (ALTO / MÉDIO / BAIXO)
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Classificação por Nível de Risco")

# Classifica cada predição em faixas de risco baseadas na probabilidade
df["risk"] = df["probability"].apply(
    lambda p: "ALTO" if p >= 0.7 else "MÉDIO" if p >= 0.4 else "BAIXO"
)
risk_counts = df["risk"].value_counts().reindex(["ALTO", "MÉDIO", "BAIXO"], fill_value=0)

fig = go.Figure(
    go.Bar(
        x=risk_counts.index,
        y=risk_counts.values,
        marker_color=["#e74c3c", "#f39c12", "#2ecc71"],
    )
)
fig.update_layout(
    xaxis_title="Nível de Risco",
    yaxis_title="Contagem",
    height=350,
)
st.plotly_chart(fig, use_container_width=True)

# Botão para limpar todo o histórico de predições da sessão
st.divider()
if st.button("Limpar Histórico de Predições", type="secondary"):
    st.session_state.predictions_history = []
    st.session_state.batch_results = None
    st.rerun()  # Força recarregamento da página
