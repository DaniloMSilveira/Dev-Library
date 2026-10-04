# Projeto Desenvolvido na Data Science Academy
"""Entry point da API FastAPI de previsão de churn.

Configura a aplicação FastAPI, incluindo:
- Ciclo de vida (lifespan): carrega o modelo de ML no startup
- Middleware CORS: controla quais origens podem acessar a API
- Error handlers: padroniza respostas de erro (422, 500)
- Rotas: registra os endpoints de predição sob o prefixo /api/v1

O FastAPI gera automaticamente documentação interativa (Swagger e ReDoc)
a partir dos schemas Pydantic e das docstrings dos endpoints.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.error_handler import register_error_handlers
from app.routes.prediction import router as prediction_router
from app.services.model_service import ModelService
from app.utils.logger import setup_logger

logger = setup_logger("main")


# ---------------------------------------------------------------------------
# Lifespan: gerencia startup e shutdown da aplicação
# O lifespan substitui os eventos @app.on_event("startup") e "shutdown"
# (deprecados no FastAPI moderno) por um context manager assíncrono.
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação.

    Carrega o modelo de ML no startup e realiza cleanup no shutdown.

    Args:
        app: Instância da aplicação FastAPI.
    """
    # Código executado no STARTUP (antes de aceitar requisições)
    logger.info("Iniciando aplicação...")

    try:
        model_service = ModelService()
        model_service.load_model()
        logger.info("Modelo carregado com sucesso no startup")
    except Exception as e:
        logger.error(
            "Erro ao carregar modelo no startup",
            extra={"error": str(e)},
        )

    # yield separa startup de shutdown — a aplicação roda entre os dois
    yield

    # Código executado no SHUTDOWN (ao encerrar a aplicação)
    logger.info("Encerrando aplicação...")


# ---------------------------------------------------------------------------
# Criação da instância FastAPI
# Os parâmetros title, description e version são usados na documentação
# gerada automaticamente em /docs (Swagger) e /redoc (ReDoc).
# ---------------------------------------------------------------------------

app = FastAPI(
    title="API de Previsão de Churn",
    description=(
        "API REST para previsão de churn de clientes de telecomunicações "
        "utilizando modelo de Machine Learning (Gradient Boosting)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware CORS (Cross-Origin Resource Sharing)
# Controla quais domínios externos podem fazer requisições para esta API.
# Sem CORS, o navegador bloqueia requisições do webapp (porta 8501)
# para a API (porta 8000) por serem origens diferentes.
# As origens permitidas são configuráveis via variável de ambiente.
# ---------------------------------------------------------------------------

_default_origins = "http://localhost:8501,http://webapp:8501"
_allowed_origins = os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Apenas métodos necessários (princípio do menor privilégio)
    allow_headers=["*"],
)

# Registra handlers globais de erro (422 e 500)
register_error_handlers(app)

# Registra as rotas de predição sob o prefixo /api/v1 (versionamento da API)
app.include_router(prediction_router, prefix="/api/v1", tags=["Predição"])


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Endpoint raiz com informações básicas da API.

    Returns:
        Mensagem de boas-vindas e links para documentação e health check.
    """
    return {
        "message": "API de Previsão de Churn",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
