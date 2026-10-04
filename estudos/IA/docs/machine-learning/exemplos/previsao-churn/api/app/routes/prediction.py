# Projeto Desenvolvido na Data Science Academy
"""Rotas de predição da API de previsão de churn.

Define os endpoints REST para predição individual, em lote,
health check e informações do modelo.

Conceitos utilizados:
- APIRouter: agrupa rotas relacionadas para organização modular
- Depends: implementa Dependency Injection do FastAPI, injetando
  o ModelService automaticamente em cada endpoint
- response_model: define o schema de resposta para validação e documentação
- async def: endpoints assíncronos (padrão FastAPI/ASGI)
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    BatchSummary,
    CustomerData,
    HealthResponse,
    ModelInfo,
    PredictionResponse,
)
from app.services.model_service import ModelService
from app.utils.logger import setup_logger

logger = setup_logger("routes")

# APIRouter permite agrupar endpoints e registrá-los no app com prefixo
router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency Injection
# O FastAPI chama get_model_service() automaticamente antes de cada endpoint
# que declara model_service: ModelService = Depends(get_model_service).
# Isso desacopla a criação do serviço da lógica do endpoint.
# ---------------------------------------------------------------------------


def get_model_service() -> ModelService:
    """Dependency injection para o ModelService.

    Returns:
        Instância singleton do ModelService.
    """
    return ModelService()


# ---------------------------------------------------------------------------
# Endpoint: Predição Individual (POST /api/v1/predict)
# ---------------------------------------------------------------------------


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    customer: CustomerData,
    model_service: ModelService = Depends(get_model_service),
) -> PredictionResponse:
    """Realiza predição de churn para um único cliente.

    O FastAPI valida automaticamente o JSON de entrada usando o schema
    CustomerData (Pydantic). Se a validação falhar, retorna HTTP 422.

    Args:
        customer: Dados do cliente validados pelo Pydantic.
        model_service: Instância do serviço de modelo (injetada via Depends).

    Returns:
        Resultado da predição com probabilidade e feature importance.
    """
    logger.info("Predição individual solicitada")

    # model_dump() converte o objeto Pydantic para dicionário Python
    data = customer.model_dump()
    result = model_service.predict(data)

    logger.info(
        "Predição realizada",
        extra={
            "prediction": result["prediction"],
            "probability": result["probability"],
        },
    )

    return PredictionResponse(
        prediction=result["prediction"],
        probability=result["probability"],
        feature_importance=result["feature_importance"],
    )


# ---------------------------------------------------------------------------
# Endpoint: Predição em Lote (POST /api/v1/predict/batch)
# ---------------------------------------------------------------------------


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    request: BatchPredictionRequest,
    model_service: ModelService = Depends(get_model_service),
) -> BatchPredictionResponse:
    """Realiza predição de churn para múltiplos clientes em uma requisição.

    A inferência é vetorizada: o modelo processa todo o DataFrame de uma vez,
    em vez de iterar cliente por cliente, o que é significativamente mais rápido.

    Args:
        request: Lista de dados de clientes validados pelo Pydantic.
        model_service: Instância do serviço de modelo (injetada via Depends).

    Returns:
        Lista de predições individuais e resumo estatístico do lote.
    """
    logger.info(
        "Predição em lote solicitada",
        extra={"n_customers": len(request.customers)},
    )

    # Converte lista de objetos Pydantic para lista de dicionários
    data = [c.model_dump() for c in request.customers]
    results = model_service.predict_batch(data)

    # Monta lista de respostas individuais
    predictions = [
        PredictionResponse(
            prediction=r["prediction"],
            probability=r["probability"],
            feature_importance=r["feature_importance"],
        )
        for r in results
    ]

    # Calcula resumo estatístico do lote
    churn_count = sum(1 for r in results if r["prediction"] == "Sim")
    total = len(results)

    summary = BatchSummary(
        total=total,
        churn_count=churn_count,
        churn_rate=round(churn_count / total, 4) if total > 0 else 0.0,
    )

    logger.info(
        "Predição em lote concluída",
        extra={
            "total": total,
            "churn_count": churn_count,
            "churn_rate": summary.churn_rate,
        },
    )

    return BatchPredictionResponse(predictions=predictions, summary=summary)


# ---------------------------------------------------------------------------
# Endpoint: Health Check (GET /api/v1/health)
# Usado pelo Docker Compose para verificar se a API está pronta para
# receber requisições (condition: service_healthy).
# ---------------------------------------------------------------------------


@router.get("/health", response_model=HealthResponse)
async def health_check(
    model_service: ModelService = Depends(get_model_service),
) -> HealthResponse:
    """Verifica o estado de saúde da API.

    Args:
        model_service: Instância do serviço de modelo.

    Returns:
        Status da API, timestamp UTC e estado do modelo em memória.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        model_loaded=model_service.is_loaded,
    )


# ---------------------------------------------------------------------------
# Endpoint: Informações do Modelo (GET /api/v1/model/info)
# ---------------------------------------------------------------------------


@router.get("/model/info", response_model=ModelInfo)
async def model_info(
    model_service: ModelService = Depends(get_model_service),
) -> ModelInfo:
    """Retorna informações e metadados do modelo carregado.

    Args:
        model_service: Instância do serviço de modelo.

    Returns:
        Versão, data de treinamento, métricas e lista de features.
    """
    info = model_service.get_model_info()

    return ModelInfo(
        model_version=info["model_version"],
        trained_at=info["trained_at"],
        metrics=info["metrics"],
        feature_names=info["feature_names"],
    )
