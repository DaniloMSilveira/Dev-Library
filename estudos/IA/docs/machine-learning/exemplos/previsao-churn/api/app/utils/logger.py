# Projeto Desenvolvido na Data Science Academy
"""Configuração de logging estruturado em JSON para a API.

Provê logger configurável via variável de ambiente LOG_LEVEL,
com saída em formato JSON para facilitar integração com ferramentas
de monitoramento (ELK Stack, Datadog, CloudWatch, etc).

Por que JSON em vez de texto plano?
- Logs JSON são parseáveis por ferramentas de agregação automaticamente
- Cada campo (timestamp, level, message) é um atributo pesquisável
- Metadados contextuais (extra) são incluídos como campos adicionais
- Facilita filtragem, busca e alertas em ambientes de produção

Exemplo de saída:
{"asctime": "2026-03-02T18:00:00", "name": "routes", "levelname": "INFO",
 "message": "Predição realizada", "prediction": "Sim", "probability": 0.78}
"""

import logging
import os
import sys

from pythonjsonlogger.json import JsonFormatter


def setup_logger(name: str = "api") -> logging.Logger:
    """Configura e retorna um logger com saída JSON estruturada.

    Cada módulo da API cria seu próprio logger com um nome identificador
    (ex: "routes", "model_service"), permitindo filtrar logs por origem.

    Args:
        name: Nome do logger (identifica o módulo de origem). Default: 'api'.

    Returns:
        Logger configurado com handler JSON em stdout.
    """
    logger = logging.getLogger(name)

    # Evita duplicação de handlers quando a função é chamada mais de uma vez
    # para o mesmo nome (o logging do Python cacheia loggers por nome)
    if logger.handlers:
        return logger

    # Nível de log configurável via variável de ambiente (padrão: INFO)
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Envia logs para stdout (padrão Docker — capturado por docker compose logs)
    handler = logging.StreamHandler(sys.stdout)

    # Formata cada entrada de log como um objeto JSON
    formatter = JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
