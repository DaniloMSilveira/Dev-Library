# Projeto Desenvolvido na Data Science Academy
"""Testes unitários para o cliente da API (APIClient).

Estratégia de teste:
- Usa unittest.mock para substituir o httpx.Client real por um mock,
  evitando chamadas HTTP reais durante os testes (testes isolados).
- Cada classe de teste agrupa testes de um método público do APIClient.
- Testa tanto cenários de sucesso quanto cenários de falha (conexão, timeout, HTTP error).

Conceitos utilizados:
- MagicMock: cria objetos "falsos" que registram como foram chamados
  e permitem configurar retornos (return_value) e efeitos colaterais (side_effect).
- @patch: decorador/context manager que substitui um objeto no módulo alvo
  durante a execução do teste, restaurando o original ao final.
- @pytest.fixture: função que prepara dados ou objetos reutilizáveis entre testes.
  O pytest injeta automaticamente a fixture via nome do parâmetro.
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from utils.api_client import APIClient


# ---------------------------------------------------------------------------
# Fixtures e helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def client() -> APIClient:
    """Cria instância do APIClient com httpx.Client mockado.

    Usa patch() como context manager para interceptar a criação do httpx.Client
    dentro do __init__ do APIClient. Depois substitui o _client interno por
    um MagicMock para controlar as respostas HTTP nos testes.

    max_retries=1 evita espera desnecessária no backoff durante os testes.
    """
    # patch impede que o httpx.Client real seja instanciado (evita conexão real)
    with patch("utils.api_client.httpx.Client"):
        api = APIClient(base_url="http://testserver:8000", timeout=5, max_retries=1)
    # Substitui o client interno para controlar respostas via MagicMock
    api._client = MagicMock()
    return api


def _mock_response(data: dict, status_code: int = 200) -> MagicMock:
    """Cria um objeto mock que simula uma resposta HTTP do httpx.

    Configura .json() para retornar os dados esperados e .raise_for_status()
    para lançar HTTPStatusError quando o status_code indica erro (>= 400).
    Isso replica o comportamento real do httpx sem fazer requisições.
    """
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = data
    response.raise_for_status = MagicMock()
    # Simula o comportamento do httpx: raise_for_status() lança exceção em 4xx/5xx
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=response
        )
    return response


# ---------------------------------------------------------------------------
# Testes: predição individual (POST /api/v1/predict)
# ---------------------------------------------------------------------------

class TestAPIClientPredict:
    """Testes para o método predict (predição individual)."""

    def test_predict_success(self, client: APIClient) -> None:
        """Testa predição bem-sucedida — verifica se retorna prediction e probability."""
        expected = {
            "prediction": "Não",
            "probability": 0.25,
            "feature_importance": [],
        }
        # Configura o mock para retornar a resposta esperada
        client._client.request.return_value = _mock_response(expected)

        result = client.predict({"tenure": 12, "MonthlyCharges": 50.0})
        assert result["prediction"] == "Não"
        assert result["probability"] == 0.25

    def test_predict_connection_error(self, client: APIClient) -> None:
        """Testa que ConnectError é convertido em ConnectionError após retries."""
        # side_effect faz o mock lançar exceção em vez de retornar valor
        client._client.request.side_effect = httpx.ConnectError("Connection refused")

        # O APIClient converte httpx.ConnectError → ConnectionError (built-in Python)
        with pytest.raises(ConnectionError):
            client.predict({"tenure": 12})

    def test_predict_timeout(self, client: APIClient) -> None:
        """Testa que TimeoutException é convertida em TimeoutError."""
        client._client.request.side_effect = httpx.TimeoutException("Timeout")

        # O APIClient converte httpx.TimeoutException → TimeoutError (built-in Python)
        with pytest.raises(TimeoutError):
            client.predict({"tenure": 12})


# ---------------------------------------------------------------------------
# Testes: predição batch (POST /api/v1/predict/batch)
# ---------------------------------------------------------------------------

class TestAPIClientBatch:
    """Testes para o método predict_batch (predição em lote)."""

    def test_batch_predict_success(self, client: APIClient) -> None:
        """Testa predição batch — verifica estrutura com predictions e summary."""
        expected = {
            "predictions": [
                {"prediction": "Sim", "probability": 0.8, "feature_importance": []},
                {"prediction": "Não", "probability": 0.2, "feature_importance": []},
            ],
            "summary": {"total": 2, "churn_count": 1, "churn_rate": 0.5},
        }
        client._client.request.return_value = _mock_response(expected)

        result = client.predict_batch([{"tenure": 12}, {"tenure": 60}])
        assert result["summary"]["total"] == 2


# ---------------------------------------------------------------------------
# Testes: health check (GET /api/v1/health)
# ---------------------------------------------------------------------------

class TestAPIClientHealth:
    """Testes para o método health_check."""

    def test_health_check_success(self, client: APIClient) -> None:
        """Testa health check — verifica status e model_loaded."""
        expected = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00",
            "model_loaded": True,
        }
        client._client.request.return_value = _mock_response(expected)

        result = client.health_check()
        assert result["status"] == "healthy"
        assert result["model_loaded"] is True


# ---------------------------------------------------------------------------
# Testes: informações do modelo (GET /api/v1/model/info)
# ---------------------------------------------------------------------------

class TestAPIClientModelInfo:
    """Testes para o método model_info."""

    def test_model_info_success(self, client: APIClient) -> None:
        """Testa obtenção de metadados do modelo — verifica model_version."""
        expected = {
            "model_version": "1.0.0",
            "trained_at": "2024-01-01T00:00:00",
            "metrics": {"accuracy": 0.85},
            "feature_names": ["tenure"],
        }
        client._client.request.return_value = _mock_response(expected)

        result = client.model_info()
        assert result["model_version"] == "1.0.0"

    def test_model_info_api_error(self, client: APIClient) -> None:
        """Testa que erros HTTP (ex: 500) são propagados sem retry.

        Erros HTTP indicam problema na API (não de conexão), então o
        APIClient propaga imediatamente sem tentar novamente.
        """
        client._client.request.return_value = _mock_response(
            {"detail": "Error"}, status_code=500
        )

        with pytest.raises(httpx.HTTPStatusError):
            client.model_info()
