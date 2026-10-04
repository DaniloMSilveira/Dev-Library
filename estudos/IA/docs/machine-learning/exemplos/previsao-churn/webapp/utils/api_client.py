# Projeto Desenvolvido na Data Science Academy
"""Cliente HTTP para comunicação com a API de previsão de churn.

Centraliza todas as chamadas HTTP para a API REST, incluindo
tratamento de erros, timeout e retry com backoff exponencial.

Padrões utilizados:
- Connection Pooling: reutiliza uma única conexão HTTP (httpx.Client)
  para todas as requisições, evitando overhead de abrir/fechar conexões.
- Retry com Backoff Exponencial: em caso de falha de conexão, aguarda
  tempos crescentes (1s, 2s, 4s...) antes de tentar novamente.
- Facade: fornece métodos simples (predict, health_check) que
  encapsulam a complexidade da comunicação HTTP.
"""

import os
import time
from typing import Any

import httpx


class APIClient:
    """Cliente para interação com a API de previsão de churn.

    Reutiliza uma única conexão HTTP (connection pooling) para todas as
    requisições, com retry automático e backoff exponencial em falhas.

    Attributes:
        base_url: URL base da API.
        timeout: Timeout para requisições em segundos.
        max_retries: Número máximo de tentativas em caso de falha de conexão.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        """Inicializa o cliente da API.

        Args:
            base_url: URL base da API. Se não informado, usa API_URL do ambiente.
            timeout: Timeout para requisições em segundos. Default: 30.
            max_retries: Número máximo de retries. Default: 3.
        """
        self.base_url = (
            base_url or os.environ.get("API_URL", "http://localhost:8000")
        ).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # httpx.Client mantém um pool de conexões persistentes,
        # reutilizando-as entre requisições (mais eficiente que criar uma nova por chamada)
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def _request_with_retry(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict:
        """Executa requisição HTTP com retry e backoff exponencial.

        Estratégia de retry:
        - ConnectError: tenta novamente com espera crescente (2^attempt segundos)
        - HTTPStatusError: propaga imediatamente (erro da API, não de conexão)
        - TimeoutException: propaga imediatamente como TimeoutError

        Args:
            method: Método HTTP (GET, POST, etc).
            endpoint: Endpoint relativo (ex: /api/v1/predict).
            **kwargs: Argumentos adicionais para httpx (ex: json=...).

        Returns:
            Dicionário com a resposta JSON da API.

        Raises:
            ConnectionError: Se não conseguir conectar após todas as tentativas.
            httpx.HTTPStatusError: Se a API retornar erro HTTP (4xx, 5xx).
            TimeoutError: Se a requisição exceder o timeout.
        """
        last_exception: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                response = self._client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError as e:
                last_exception = e
                # Backoff exponencial: 1s, 2s, 4s...
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            except httpx.HTTPStatusError:
                # Erro HTTP (ex: 422, 500) — não faz retry, propaga imediatamente
                raise
            except httpx.TimeoutException as e:
                raise TimeoutError(
                    f"Timeout ao conectar com a API ({self.timeout}s)"
                ) from e

        raise ConnectionError(
            f"Não foi possível conectar à API após {self.max_retries} tentativas. "
            f"Verifique se a API está rodando em {self.base_url}"
        ) from last_exception

    # ---------------------------------------------------------------------------
    # Métodos públicos: cada um encapsula uma chamada HTTP para a API
    # ---------------------------------------------------------------------------

    def predict(self, customer_data: dict) -> dict:
        """Realiza predição de churn para um único cliente.

        Args:
            customer_data: Dicionário com os 19 campos do cliente.

        Returns:
            Dicionário com prediction, probability e feature_importance.
        """
        return self._request_with_retry(
            "POST", "/api/v1/predict", json=customer_data
        )

    def predict_batch(self, customers: list[dict]) -> dict:
        """Realiza predição de churn para múltiplos clientes.

        Args:
            customers: Lista de dicionários com dados dos clientes.

        Returns:
            Dicionário com predictions (lista) e summary (estatísticas).
        """
        return self._request_with_retry(
            "POST", "/api/v1/predict/batch", json={"customers": customers}
        )

    def health_check(self) -> dict:
        """Verifica o estado de saúde da API.

        Returns:
            Dicionário com status, timestamp e model_loaded.
        """
        return self._request_with_retry("GET", "/api/v1/health")

    def model_info(self) -> dict:
        """Obtém informações e metadados do modelo.

        Returns:
            Dicionário com model_version, trained_at, metrics e feature_names.
        """
        return self._request_with_retry("GET", "/api/v1/model/info")
