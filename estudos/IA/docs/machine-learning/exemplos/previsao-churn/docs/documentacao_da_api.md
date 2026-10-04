<!-- Projeto Desenvolvido na Data Science Academy -->
# 7. Documentacao da API

## Visao Geral

A API REST de previsao de churn e construida com FastAPI e fornece endpoints para predicao individual e em lote de cancelamento de clientes de telecomunicacoes.

| Atributo | Valor |
|----------|-------|
| Base URL | `http://localhost:8000` |
| Prefixo | `/api/v1` |
| Documentacao interativa | `http://localhost:8000/docs` (Swagger) |
| Documentacao alternativa | `http://localhost:8000/redoc` (ReDoc) |
| Formato | JSON |
| Autenticacao | Nao requerida (versao atual) |

---

## Endpoints

### 1. Predicao Individual

**`POST /api/v1/predict`**

Realiza predicao de churn para um unico cliente.

**Request Body:**

```json
{
  "gender": "Male",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 3,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "OnlineBackup": "No",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "No",
  "StreamingMovies": "No",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 85.50,
  "TotalCharges": 256.50
}
```

**Response (200):**

```json
{
  "prediction": "Sim",
  "probability": 0.7899,
  "feature_importance": [
    {"feature": "TotalCharges", "importance": 0.222972},
    {"feature": "Contract_Two year", "importance": 0.19726},
    {"feature": "MonthlyCharges", "importance": 0.194702},
    {"feature": "tenure", "importance": 0.106601},
    {"feature": "Contract_One year", "importance": 0.077742}
  ]
}
```

**Exemplo com curl:**

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Male", "SeniorCitizen": 0, "Partner": "Yes",
    "Dependents": "No", "tenure": 3, "PhoneService": "Yes",
    "MultipleLines": "No", "InternetService": "Fiber optic",
    "OnlineSecurity": "No", "OnlineBackup": "No",
    "DeviceProtection": "No", "TechSupport": "No",
    "StreamingTV": "No", "StreamingMovies": "No",
    "Contract": "Month-to-month", "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 85.50, "TotalCharges": 256.50
  }'
```

---

### 2. Predicao em Lote

**`POST /api/v1/predict/batch`**

Realiza predicao de churn para multiplos clientes em uma unica requisicao (inferencia vetorizada).

**Request Body:**

```json
{
  "customers": [
    {
      "gender": "Male", "SeniorCitizen": 0, "Partner": "Yes",
      "Dependents": "No", "tenure": 3, "PhoneService": "Yes",
      "MultipleLines": "No", "InternetService": "Fiber optic",
      "OnlineSecurity": "No", "OnlineBackup": "No",
      "DeviceProtection": "No", "TechSupport": "No",
      "StreamingTV": "No", "StreamingMovies": "No",
      "Contract": "Month-to-month", "PaperlessBilling": "Yes",
      "PaymentMethod": "Electronic check",
      "MonthlyCharges": 85.50, "TotalCharges": 256.50
    },
    {
      "gender": "Female", "SeniorCitizen": 0, "Partner": "Yes",
      "Dependents": "Yes", "tenure": 60, "PhoneService": "Yes",
      "MultipleLines": "Yes", "InternetService": "DSL",
      "OnlineSecurity": "Yes", "OnlineBackup": "Yes",
      "DeviceProtection": "Yes", "TechSupport": "Yes",
      "StreamingTV": "Yes", "StreamingMovies": "Yes",
      "Contract": "Two year", "PaperlessBilling": "No",
      "PaymentMethod": "Bank transfer (automatic)",
      "MonthlyCharges": 75.00, "TotalCharges": 4500.00
    }
  ]
}
```

**Response (200):**

```json
{
  "predictions": [
    {
      "prediction": "Sim",
      "probability": 0.7899,
      "feature_importance": [...]
    },
    {
      "prediction": "Nao",
      "probability": 0.0131,
      "feature_importance": [...]
    }
  ],
  "summary": {
    "total": 2,
    "churn_count": 1,
    "churn_rate": 0.5
  }
}
```

---

### 3. Health Check

**`GET /api/v1/health`**

Verifica o estado de saude da API e se o modelo esta carregado.

**Response (200):**

```json
{
  "status": "healthy",
  "timestamp": "2026-03-02T18:00:00.000000Z",
  "model_loaded": true
}
```

---

### 4. Informacoes do Modelo

**`GET /api/v1/model/info`**

Retorna metadados e metricas do modelo carregado.

**Response (200):**

```json
{
  "model_version": "1.0.0",
  "trained_at": "2026-03-02T17:59:57.259349+00:00",
  "metrics": {
    "accuracy": 0.665,
    "precision": 0.4426,
    "recall": 0.6485,
    "f1": 0.5261,
    "auc_roc": 0.7222
  },
  "feature_names": [
    "gender", "SeniorCitizen", "Partner", "Dependents",
    "tenure", "PhoneService", "MultipleLines", "InternetService",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
    "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
    "PaymentMethod", "MonthlyCharges", "TotalCharges"
  ]
}
```

---

## Campos de Entrada (CustomerData)

Todos os 19 campos sao obrigatorios. A validacao e feita via Pydantic v2 com `Literal` types.

| Campo | Tipo | Valores Permitidos |
|-------|------|--------------------|
| `gender` | string | `"Male"`, `"Female"` |
| `SeniorCitizen` | integer | `0`, `1` |
| `Partner` | string | `"Yes"`, `"No"` |
| `Dependents` | string | `"Yes"`, `"No"` |
| `tenure` | integer | 0 a 72 |
| `PhoneService` | string | `"Yes"`, `"No"` |
| `MultipleLines` | string | `"Yes"`, `"No"`, `"No phone service"` |
| `InternetService` | string | `"DSL"`, `"Fiber optic"`, `"No"` |
| `OnlineSecurity` | string | `"Yes"`, `"No"`, `"No internet service"` |
| `OnlineBackup` | string | `"Yes"`, `"No"`, `"No internet service"` |
| `DeviceProtection` | string | `"Yes"`, `"No"`, `"No internet service"` |
| `TechSupport` | string | `"Yes"`, `"No"`, `"No internet service"` |
| `StreamingTV` | string | `"Yes"`, `"No"`, `"No internet service"` |
| `StreamingMovies` | string | `"Yes"`, `"No"`, `"No internet service"` |
| `Contract` | string | `"Month-to-month"`, `"One year"`, `"Two year"` |
| `PaperlessBilling` | string | `"Yes"`, `"No"` |
| `PaymentMethod` | string | `"Electronic check"`, `"Mailed check"`, `"Bank transfer (automatic)"`, `"Credit card (automatic)"` |
| `MonthlyCharges` | float | 0 a 200 |
| `TotalCharges` | float | 0 a 10000 |

---

## Campos de Resposta

### PredictionResponse

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `prediction` | string | Classe predita: `"Sim"` (churn) ou `"Nao"` (nao-churn) |
| `probability` | float | Probabilidade de churn (0.0 a 1.0), arredondada em 4 decimais |
| `feature_importance` | array | Top 10 features com `feature` (nome) e `importance` (peso) |

### BatchPredictionResponse

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `predictions` | array | Lista de `PredictionResponse` |
| `summary.total` | integer | Total de clientes processados |
| `summary.churn_count` | integer | Quantidade prevista como churn |
| `summary.churn_rate` | float | Taxa de churn no lote |

### HealthResponse

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `status` | string | `"healthy"` |
| `timestamp` | string (ISO 8601) | Momento da verificacao (UTC) |
| `model_loaded` | boolean | Se o modelo esta carregado em memoria |

### ModelInfo

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `model_version` | string | Versao do modelo (ex: `"1.0.0"`) |
| `trained_at` | string (ISO 8601) | Data/hora do treinamento |
| `metrics` | object | Metricas: `accuracy`, `precision`, `recall`, `f1`, `auc_roc` |
| `feature_names` | array | Lista das 19 features de entrada |

---

## Codigos de Resposta

| Codigo | Descricao | Quando ocorre |
|:------:|-----------|---------------|
| 200 | Sucesso | Predicao realizada, health check OK, model info OK |
| 422 | Erro de validacao | Campo ausente, tipo incorreto, valor fora do range, batch vazio |
| 500 | Erro interno | Falha no modelo, erro nao tratado |

### Exemplo de erro 422

```json
{
  "detail": "Erro de validação nos dados de entrada",
  "status_code": 422,
  "errors": [
    {"field": "body -> tenure", "message": "Input should be less than or equal to 72"},
    {"field": "body -> gender", "message": "Input should be 'Male' or 'Female'"}
  ]
}
```

### Exemplo de erro 500

```json
{
  "detail": "Erro interno do servidor",
  "status_code": 500
}
```
