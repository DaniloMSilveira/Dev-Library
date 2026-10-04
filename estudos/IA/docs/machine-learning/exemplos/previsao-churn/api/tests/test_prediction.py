# Projeto Desenvolvido na Data Science Academy
"""Testes de integração para os endpoints de predição da API.

Utiliza o TestClient do FastAPI, que simula requisições HTTP sem
precisar subir um servidor real. Isso permite testar os endpoints
como se fossem chamadas HTTP reais, mas em memória.

Os testes de predição usam @patch para substituir o ModelService por
um mock, isolando os testes da disponibilidade do modelo de ML.
Testes de validação (422) não precisam de mock, pois o erro ocorre
antes de chegar ao serviço.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

# TestClient simula requisições HTTP para a aplicação FastAPI
client = TestClient(app)


# ---------------------------------------------------------------------------
# Funções auxiliares: dados de teste e resultados mock
# ---------------------------------------------------------------------------


def _valid_customer_data() -> dict:
    """Retorna dados válidos de um cliente para testes."""
    return {
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 12,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "DSL",
        "OnlineSecurity": "Yes",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "Yes",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 29.85,
        "TotalCharges": 358.2,
    }


def _mock_predict_result() -> dict:
    """Retorna resultado mock de predição (substitui o modelo real)."""
    return {
        "prediction": "Não",
        "probability": 0.25,
        "feature_importance": [
            {"feature": "tenure", "importance": 0.15},
            {"feature": "MonthlyCharges", "importance": 0.12},
        ],
    }


# ---------------------------------------------------------------------------
# Testes: Health Check (não precisa de mock — endpoint simples)
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """Testes para o endpoint GET /api/v1/health."""

    def test_health_check(self) -> None:
        """Testa que o health check retorna status 200 com campos esperados."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "model_loaded" in data


# ---------------------------------------------------------------------------
# Testes: Informações do Modelo (usa mock para simular modelo carregado)
# ---------------------------------------------------------------------------


class TestModelInfo:
    """Testes para o endpoint GET /api/v1/model/info."""

    @patch("app.routes.prediction.ModelService")
    def test_model_info(self, mock_service_class: MagicMock) -> None:
        """Testa que retorna metadados do modelo com status 200."""
        # Configura o mock para retornar dados simulados
        mock_instance = MagicMock()
        mock_instance.get_model_info.return_value = {
            "model_version": "1.0.0",
            "trained_at": "2024-01-01T00:00:00",
            "metrics": {"accuracy": 0.85},
            "feature_names": ["tenure", "MonthlyCharges"],
        }
        mock_instance.is_loaded = True
        mock_service_class.return_value = mock_instance

        response = client.get("/api/v1/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "model_version" in data
        assert "metrics" in data


# ---------------------------------------------------------------------------
# Testes: Predição Individual (POST /api/v1/predict)
# ---------------------------------------------------------------------------


class TestPredictEndpoint:
    """Testes para o endpoint POST /api/v1/predict."""

    @patch("app.routes.prediction.ModelService")
    def test_predict_valid_data(self, mock_service_class: MagicMock) -> None:
        """Testa predição com dados válidos retorna 200 com resultado."""
        mock_instance = MagicMock()
        mock_instance.predict.return_value = _mock_predict_result()
        mock_service_class.return_value = mock_instance

        response = client.post("/api/v1/predict", json=_valid_customer_data())
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "feature_importance" in data

    def test_predict_invalid_data(self) -> None:
        """Testa que dados com valores inválidos retornam 422."""
        invalid_data = {"gender": "Invalid", "tenure": -5}
        response = client.post("/api/v1/predict", json=invalid_data)
        assert response.status_code == 422

    def test_predict_missing_fields(self) -> None:
        """Testa que campos obrigatórios ausentes retornam 422."""
        response = client.post("/api/v1/predict", json={"gender": "Male"})
        assert response.status_code == 422

    def test_predict_empty_body(self) -> None:
        """Testa que body vazio retorna 422."""
        response = client.post("/api/v1/predict", json={})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Testes: Predição em Lote (POST /api/v1/predict/batch)
# ---------------------------------------------------------------------------


class TestBatchPredictEndpoint:
    """Testes para o endpoint POST /api/v1/predict/batch."""

    @patch("app.routes.prediction.ModelService")
    def test_predict_batch_valid(self, mock_service_class: MagicMock) -> None:
        """Testa predição em lote com dados válidos retorna 200 com resumo."""
        mock_instance = MagicMock()
        mock_instance.predict_batch.return_value = [
            _mock_predict_result(),
            _mock_predict_result(),
        ]
        mock_service_class.return_value = mock_instance

        response = client.post(
            "/api/v1/predict/batch",
            json={"customers": [_valid_customer_data(), _valid_customer_data()]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "summary" in data
        assert data["summary"]["total"] == 2

    def test_predict_batch_empty(self) -> None:
        """Testa que batch vazio retorna 422 (min_length=1 no schema)."""
        response = client.post(
            "/api/v1/predict/batch", json={"customers": []}
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Testes: Endpoint Raiz
# ---------------------------------------------------------------------------


class TestRootEndpoint:
    """Testes para o endpoint GET /."""

    def test_root(self) -> None:
        """Testa que o endpoint raiz retorna mensagem e links."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
