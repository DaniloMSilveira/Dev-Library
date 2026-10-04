# Projeto Desenvolvido na Data Science Academy
"""Testes unitários para os schemas Pydantic da API.

Estes testes validam que os schemas de entrada e saída funcionam
corretamente, incluindo:
- Aceitação de dados válidos
- Rejeição de valores fora dos limites (ge, le)
- Rejeição de valores fora do conjunto Literal permitido
- Rejeição de campos obrigatórios ausentes

Diferente dos testes de integração (test_prediction.py), estes testes
não fazem requisições HTTP — instanciam os schemas diretamente.
"""

import pytest
from pydantic import ValidationError

from app.schemas import (
    BatchPredictionRequest,
    CustomerData,
    HealthResponse,
    ModelInfo,
    PredictionResponse,
)


def _valid_customer_data() -> dict:
    """Retorna dados válidos de um cliente para reuso entre testes."""
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


# ---------------------------------------------------------------------------
# Testes: schema CustomerData (validação de entrada)
# ---------------------------------------------------------------------------


class TestCustomerData:
    """Testes para o schema CustomerData (19 features do cliente)."""

    def test_valid_data(self) -> None:
        """Testa que dados válidos são aceitos sem erro."""
        customer = CustomerData(**_valid_customer_data())
        assert customer.gender == "Male"
        assert customer.tenure == 12

    def test_invalid_gender(self) -> None:
        """Testa que Literal rejeita valores fora do conjunto permitido."""
        data = _valid_customer_data()
        data["gender"] = "Other"  # Só aceita "Male" ou "Female"
        with pytest.raises(ValidationError):
            CustomerData(**data)

    def test_invalid_tenure_negative(self) -> None:
        """Testa que ge=0 rejeita valores negativos."""
        data = _valid_customer_data()
        data["tenure"] = -1
        with pytest.raises(ValidationError):
            CustomerData(**data)

    def test_invalid_tenure_too_high(self) -> None:
        """Testa que le=72 rejeita valores acima do limite."""
        data = _valid_customer_data()
        data["tenure"] = 100
        with pytest.raises(ValidationError):
            CustomerData(**data)

    def test_invalid_contract(self) -> None:
        """Testa que tipo de contrato inválido é rejeitado."""
        data = _valid_customer_data()
        data["Contract"] = "Three year"
        with pytest.raises(ValidationError):
            CustomerData(**data)

    def test_invalid_monthly_charges_negative(self) -> None:
        """Testa que ge=0 rejeita cobranças negativas."""
        data = _valid_customer_data()
        data["MonthlyCharges"] = -10
        with pytest.raises(ValidationError):
            CustomerData(**data)

    def test_missing_required_field(self) -> None:
        """Testa que campo obrigatório ausente gera ValidationError."""
        data = _valid_customer_data()
        del data["gender"]
        with pytest.raises(ValidationError):
            CustomerData(**data)

    def test_all_internet_service_options(self) -> None:
        """Testa que todos os valores Literal de InternetService são aceitos."""
        for option in ["DSL", "Fiber optic", "No"]:
            data = _valid_customer_data()
            data["InternetService"] = option
            customer = CustomerData(**data)
            assert customer.InternetService == option

    def test_all_payment_methods(self) -> None:
        """Testa que todos os 4 métodos de pagamento são aceitos."""
        methods = [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ]
        for method in methods:
            data = _valid_customer_data()
            data["PaymentMethod"] = method
            customer = CustomerData(**data)
            assert customer.PaymentMethod == method


# ---------------------------------------------------------------------------
# Testes: schema PredictionResponse (validação de saída)
# ---------------------------------------------------------------------------


class TestPredictionResponse:
    """Testes para o schema PredictionResponse."""

    def test_valid_response(self) -> None:
        """Testa criação com dados válidos."""
        response = PredictionResponse(
            prediction="Sim",
            probability=0.85,
            feature_importance=[
                {"feature": "tenure", "importance": 0.15}
            ],
        )
        assert response.prediction == "Sim"
        assert response.probability == 0.85

    def test_probability_bounds(self) -> None:
        """Testa que probabilidade > 1.0 é rejeitada (le=1)."""
        with pytest.raises(ValidationError):
            PredictionResponse(
                prediction="Sim",
                probability=1.5,
                feature_importance=[],
            )


# ---------------------------------------------------------------------------
# Testes: schema BatchPredictionRequest
# ---------------------------------------------------------------------------


class TestBatchPredictionRequest:
    """Testes para o schema BatchPredictionRequest."""

    def test_valid_batch(self) -> None:
        """Testa que batch com pelo menos 1 cliente é aceito."""
        batch = BatchPredictionRequest(
            customers=[CustomerData(**_valid_customer_data())]
        )
        assert len(batch.customers) == 1

    def test_empty_batch(self) -> None:
        """Testa que batch vazio é rejeitado (min_length=1)."""
        with pytest.raises(ValidationError):
            BatchPredictionRequest(customers=[])
