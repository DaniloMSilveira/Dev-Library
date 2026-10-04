# Projeto Desenvolvido na Data Science Academy
"""Middleware de tratamento global de erros da API.

Captura exceções não tratadas e retorna respostas padronizadas
em formato JSON com códigos HTTP apropriados.

O FastAPI possui tratamento padrão de erros, mas este middleware
personaliza as respostas para:
- HTTP 422: erros de validação com detalhes por campo
- HTTP 500: erros internos com mensagem genérica (sem expor detalhes ao cliente)

Hierarquia de tratamento:
1. RequestValidationError → Dados de entrada inválidos (422)
2. ValidationError → Erro de validação Pydantic interno (422)
3. Exception → Qualquer erro não tratado (500)
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.utils.logger import setup_logger

logger = setup_logger("error_handler")


def register_error_handlers(app: FastAPI) -> None:
    """Registra handlers de erro globais na aplicação FastAPI.

    Os handlers são registrados via decorator @app.exception_handler,
    que intercepta exceções específicas antes que cheguem ao handler padrão.

    Args:
        app: Instância da aplicação FastAPI.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handler para erros de validação de request (HTTP 422).

        Ocorre quando o JSON de entrada não passa na validação do schema Pydantic
        (campo ausente, tipo incorreto, valor fora do range permitido, etc).

        Args:
            request: Objeto de request HTTP.
            exc: Exceção de validação com lista de erros.

        Returns:
            JSONResponse com detalhes de cada campo que falhou na validação.
        """
        # Formata os erros para uma estrutura legível: campo + mensagem
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({"field": field, "message": error["msg"]})

        logger.warning(
            "Erro de validação",
            extra={"path": str(request.url), "errors": errors},
        )

        return JSONResponse(
            status_code=422,
            content={
                "detail": "Erro de validação nos dados de entrada",
                "status_code": 422,
                "errors": errors,
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handler para erros de validação Pydantic internos (HTTP 422).

        Diferente do RequestValidationError, este ocorre quando a validação
        falha dentro do código (não na deserialização do request).

        Args:
            request: Objeto de request HTTP.
            exc: Exceção de validação Pydantic.

        Returns:
            JSONResponse com mensagem de erro.
        """
        logger.warning(
            "Erro de validação Pydantic",
            extra={"path": str(request.url), "detail": str(exc)},
        )

        return JSONResponse(
            status_code=422,
            content={
                "detail": "Erro de validação nos dados",
                "status_code": 422,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handler para exceções genéricas não tratadas (HTTP 500).

        Captura qualquer exceção que não foi tratada pelos handlers anteriores.
        Retorna mensagem genérica ao cliente (sem expor detalhes internos por
        segurança) e registra os detalhes completos no log.

        Args:
            request: Objeto de request HTTP.
            exc: Exceção não tratada.

        Returns:
            JSONResponse com mensagem genérica de erro interno.
        """
        logger.error(
            "Erro interno do servidor",
            extra={
                "path": str(request.url),
                "error_type": type(exc).__name__,
                "detail": str(exc),
            },
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Erro interno do servidor",
                "status_code": 500,
            },
        )
