# Projeto Desenvolvido na Data Science Academy
"""Schemas Pydantic para validação de dados de entrada e saída da API.

Define os modelos de request e response para os endpoints de predição
de churn, health check e informações do modelo.

O Pydantic v2 realiza validação automática dos dados:
- Tipos incorretos são rejeitados (ex: string onde se espera int)
- Literal types restringem valores a um conjunto fixo (ex: "Male" ou "Female")
- Field com ge/le define limites numéricos (ge = greater or equal, le = less or equal)
- Campos com ... (Ellipsis) são obrigatórios

Quando a validação falha, o FastAPI retorna automaticamente HTTP 422
com detalhes dos campos que falharam.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Schema de entrada: dados do cliente para predição
# Os nomes dos campos seguem o padrão do dataset original (camelCase/PascalCase)
# para manter compatibilidade com os dados de treinamento.
# ---------------------------------------------------------------------------


class CustomerData(BaseModel):
    """Dados de entrada para predição de churn de um cliente.

    Todos os 19 campos são obrigatórios e correspondem às features
    do dataset Telco Customer Churn. O Literal type restringe cada
    campo categórico aos valores aceitos pelo modelo.
    """

    # --- Dados demográficos ---
    gender: Literal["Male", "Female"] = Field(
        ..., description="Gênero do cliente"
    )
    SeniorCitizen: Literal[0, 1] = Field(
        ..., description="Se o cliente é idoso (1) ou não (0)"
    )
    Partner: Literal["Yes", "No"] = Field(
        ..., description="Se o cliente possui parceiro(a)"
    )
    Dependents: Literal["Yes", "No"] = Field(
        ..., description="Se o cliente possui dependentes"
    )

    # --- Serviços contratados ---
    tenure: int = Field(
        ..., ge=0, le=72, description="Meses de permanência como cliente"
    )
    PhoneService: Literal["Yes", "No"] = Field(
        ..., description="Se possui serviço telefônico"
    )
    MultipleLines: Literal["Yes", "No", "No phone service"] = Field(
        ..., description="Se possui múltiplas linhas"
    )
    InternetService: Literal["DSL", "Fiber optic", "No"] = Field(
        ..., description="Tipo de serviço de internet"
    )
    OnlineSecurity: Literal["Yes", "No", "No internet service"] = Field(
        ..., description="Se possui segurança online"
    )
    OnlineBackup: Literal["Yes", "No", "No internet service"] = Field(
        ..., description="Se possui backup online"
    )
    DeviceProtection: Literal["Yes", "No", "No internet service"] = Field(
        ..., description="Se possui proteção de dispositivo"
    )
    TechSupport: Literal["Yes", "No", "No internet service"] = Field(
        ..., description="Se possui suporte técnico"
    )
    StreamingTV: Literal["Yes", "No", "No internet service"] = Field(
        ..., description="Se possui streaming de TV"
    )
    StreamingMovies: Literal["Yes", "No", "No internet service"] = Field(
        ..., description="Se possui streaming de filmes"
    )

    # --- Informações de contrato e pagamento ---
    Contract: Literal["Month-to-month", "One year", "Two year"] = Field(
        ..., description="Tipo de contrato"
    )
    PaperlessBilling: Literal["Yes", "No"] = Field(
        ..., description="Se possui faturamento sem papel"
    )
    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ] = Field(..., description="Método de pagamento")

    # --- Valores financeiros (ge/le = limites de validação) ---
    MonthlyCharges: float = Field(
        ..., ge=0, le=200, description="Cobranças mensais em USD"
    )
    TotalCharges: float = Field(
        ..., ge=0, le=10000, description="Cobranças totais em USD"
    )


# ---------------------------------------------------------------------------
# Schemas de resposta: resultados de predição
# ---------------------------------------------------------------------------


class FeatureImportance(BaseModel):
    """Importância de uma feature na predição do modelo."""

    feature: str = Field(..., description="Nome da feature")
    importance: float = Field(..., description="Valor da importância")


class PredictionResponse(BaseModel):
    """Resposta de uma predição individual de churn."""

    prediction: str = Field(
        ..., description="Classe predita: 'Sim' ou 'Não'"
    )
    probability: float = Field(
        ..., ge=0, le=1, description="Probabilidade de churn (0 a 1)"
    )
    feature_importance: list[FeatureImportance] = Field(
        default_factory=list,
        description="Top features mais importantes para esta predição",
    )


# ---------------------------------------------------------------------------
# Schemas de predição em lote (batch)
# ---------------------------------------------------------------------------


class BatchPredictionRequest(BaseModel):
    """Request para predição em lote (múltiplos clientes)."""

    customers: list[CustomerData] = Field(
        ..., min_length=1, description="Lista de clientes para predição"
    )


class BatchSummary(BaseModel):
    """Resumo estatístico das predições em lote."""

    total: int = Field(..., description="Total de clientes processados")
    churn_count: int = Field(..., description="Quantidade prevista como churn")
    churn_rate: float = Field(
        ..., description="Percentual de churn previsto"
    )


class BatchPredictionResponse(BaseModel):
    """Resposta completa de predição em lote."""

    predictions: list[PredictionResponse] = Field(
        ..., description="Lista de predições individuais"
    )
    summary: BatchSummary = Field(
        ..., description="Resumo estatístico das predições"
    )


# ---------------------------------------------------------------------------
# Schemas auxiliares: health check, info do modelo, erro
# ---------------------------------------------------------------------------


class ModelInfo(BaseModel):
    """Informações e metadados do modelo carregado."""

    model_version: str = Field(..., description="Versão do modelo")
    trained_at: str = Field(..., description="Data/hora do treinamento")
    metrics: dict[str, float] = Field(
        ..., description="Métricas de avaliação do modelo"
    )
    feature_names: list[str] = Field(
        ..., description="Nomes das features de entrada"
    )


class HealthResponse(BaseModel):
    """Resposta do endpoint de health check."""

    status: str = Field(..., description="Status do serviço")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    model_loaded: bool = Field(
        ..., description="Se o modelo está carregado em memória"
    )


class ErrorResponse(BaseModel):
    """Resposta padronizada de erro da API."""

    detail: str = Field(..., description="Mensagem de erro")
    status_code: int = Field(..., description="Código HTTP do erro")
