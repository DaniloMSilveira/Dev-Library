# Projeto Desenvolvido na Data Science Academy

"""Entrypoint FastAPI — Configuração da aplicação, middlewares e routers."""

import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.config import settings
from app.database import dsa_create_tables, engine
from app.routers import chat, customers, orders, products

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def dsa_lifespan(app: FastAPI):
    """Eventos de startup e shutdown."""
    logger.info(f"Iniciando {settings.APP_NAME} Backend API...")
    await dsa_create_tables()
    logger.info("Tabelas criadas/verificadas com sucesso.")
    yield
    await engine.dispose()
    logger.info("Backend API finalizado.")


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="API REST do e-commerce com atendimento automatizado via agentes de IA",
    version="1.0.0",
    lifespan=dsa_lifespan,
)

# CORS — origens configuráveis via variável de ambiente
allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def dsa_security_headers(request: Request, call_next):
    """Adiciona headers de segurança e request ID a cada resposta."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


app.include_router(products.router)
app.include_router(orders.router)
app.include_router(customers.router)
app.include_router(chat.router)


@app.get("/")
async def dsa_root() -> dict:
    """Informações básicas da API."""
    return {
        "name": f"{settings.APP_NAME} API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def dsa_health_check():
    """Health check — verifica conexão com o banco de dados."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        logger.exception("Health check falhou")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )
