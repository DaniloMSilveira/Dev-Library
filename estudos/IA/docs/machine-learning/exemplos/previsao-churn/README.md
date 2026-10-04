<!-- Projeto Desenvolvido na Data Science Academy -->
# Previsão de Churn — Telecomunicações

Aplicação web integrada a Machine Learning via API REST para previsão de churn (cancelamento) de clientes de uma empresa de telecomunicações.

## Visão Geral

O sistema utiliza um modelo de Gradient Boosting treinado no dataset Telco Customer Churn (Kaggle/IBM) para classificar clientes com alta probabilidade de cancelamento, permitindo ações preventivas de retenção.

### Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Modelo ML │────>│  API REST   │<────│   App Web   │
│ scikit-learn│     │   FastAPI   │     │  Streamlit  │
│  (treino)   │     │  (predição) │     │ (interface) │
└─────────────┘     └─────────────┘     └─────────────┘
     Docker              Docker              Docker

┌─────────────┐
│ Data Science│
│  Jupyter    │
│   (EDA)     │
└─────────────┘
     Docker
         └─────── Docker Compose (dsaprojeto1) ───────┘
```

O projeto segue uma arquitetura de camadas independentes, cada uma containerizada via Docker:

1. **Modelo ML** (`ml-model/`) — Treinamento e serialização do modelo
2. **API REST** (`api/`) — FastAPI com endpoints de predição
3. **App Web** (`webapp/`) — Interface Streamlit para interação com o modelo
4. **Data Science** (`datascience/`) — Jupyter Notebook para EDA e modelagem

---

## Como Reproduzir o Projeto

### Passo 1 — Pre-requisitos

Antes de comecar, certifique-se de ter instalado:

| Requisito | Versao Minima | Verificação |
|-----------|:------------:|-------------|
| Docker | 24+ | `docker --version` |
| Docker Compose | v2 | `docker compose version` |
| RAM disponivel | 4 GB | — |
| Portas livres | 8000, 8501 e 8888 | — |

> **Nota:** No Windows, utilize o Docker Desktop com WSL2. No macOS, utilize o Docker Desktop. No Linux, instale o Docker Engine e o plugin Compose v2.

### Passo 2 — Acessar o Projeto

Abra o terminal ou prompt de comando, navegue até a pasta com os arquivos:

```bash
cd caminho_pasta_projeto1
```

### Passo 3 — Configurar Variáveis de Ambiente (Opcional)

O arquivo `.env` contem os valores padrão e não precisa de alteração para execução local:

```env
MODEL_PATH=/app/models/churn_model.joblib
API_HOST=0.0.0.0
API_PORT=8000
API_URL=http://api:8000
LOG_LEVEL=INFO
```

### Passo 4 — Verificar os Dados

O dataset `WA_Fn-UseC_-Telco-Customer-Churn.csv` deve estar presente em `ml-model/data/raw/`. Ele já está incluído no projeto.

Caso precise baixá-lo novamente: https://www.kaggle.com/datasets/blastchar/telco-customer-churn

### Passo 5 — Subir a Stack Completa

Execute o comando abaixo na raiz do projeto (Lembre-se de abrir a janela do Docker Desktop):

```bash
docker compose up --build -d
```

O Docker Compose irá executar os quatro serviços:

1. **ml-model** — Treina o modelo de ML e salva o artefato serializado (`churn_model.joblib`). Encerra após conclusão.
2. **api** — Aguarda o modelo ser treinado, carrega o artefato e inicia a API REST na porta 8000. Executa health check automático.
3. **webapp** — Aguarda a API estar saudável e inicia a aplicação Streamlit na porta 8501.
4. **datascience** — Inicia o Jupyter Notebook na porta 8888 para EDA e modelagem interativa.

> **Tempo estimado do primeiro build:** 2-5 minutos (download das imagens Docker e instalação das dependências).

### Passo 6 — Verificar se os Servicos Estão Rodando

Em outro terminal, verifique o status dos containers:

```bash
docker compose ps -a
```

Saída esperada:

```
NAME           SERVICE       STATUS
ml-model       ml-model      exited (0)      ← Encerrou apos treinar o modelo
api            api           running (healthy)
webapp         webapp        running (healthy)
datascience    datascience   running
```

Você também pode verificar a saúde da API diretamente:

```bash
curl http://localhost:8000/api/v1/health
```

Resposta esperada:

```json
{"status": "healthy", "timestamp": "...", "model_loaded": true}
```

### Passo 7 — Acessar a Aplicação

| Servico | URL | Descrição |
|---------|-----|-----------|
| Jupyter Notebook | http://localhost:8888 | EDA e modelagem interativa |
| App Web | http://localhost:8501 | Interface principal para o usuário |
| Swagger (API) | http://localhost:8000/docs | Documentação interativa da API |
| ReDoc (API) | http://localhost:8000/redoc | Documentação alternativa da API |

### Passo 8 — Testar a API via Terminal (Opcional)

Predição individual (sem usar a app web):

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

Informações do modelo:

```bash
curl http://localhost:8000/api/v1/model/info
```

### Passo 9 — Executar os Testes

```bash
# Testes do modelo ML
docker compose run --rm ml-model pytest tests/ -v

# Testes da API
docker compose run --rm api pytest tests/ -v

# Testes do webapp
docker compose run --rm webapp pytest tests/ -v
```

### Passo 10 — Encerrar os Serviços

```bash
# Parar todos os servicos
docker compose down

# Parar e remover volumes (remove o modelo treinado)
docker compose down -v
```

---

## Comandos Úteis

```bash
# Subir em modo detached (background)
docker compose up --build -d

# Ver logs em tempo real
docker compose logs -f

# Ver logs de um servico especifico
docker compose logs -f api

# Rebuild de um servico especifico
docker compose up --build api

# Retreinar o modelo manualmente
docker compose run --rm ml-model python src/train.py
```

---

## Endpoints da API

| Metodo | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/predict` | Predição individual de churn |
| POST | `/api/v1/predict/batch` | Predição em lote |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/model/info` | Informacoes e metricas do modelo |

Documentação completa da API: [docs/07_documentacao_da_api.md](docs/documentacao_da_api.md)

---

## Estrutura do Projeto

```
projeto-ml-churn/
├── docker-compose.yml           # Orquestração dos 4 servicos (dsaprojeto1)
├── .env.example                 # Template de variaveis de ambiente
├── .gitignore
├── README.md
│
├── ml-model/                    # Camada 1: Modelo de Machine Learning
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── data/raw/                # Dados brutos
│   ├── notebooks/               # EDA e modelagem
│   ├── src/                     # Codigo-fonte (treino, avaliação)
│   ├── models/                  # Artefatos serializados
│   ├── tests/                   # Testes unitarios
│   └── configs/                 # Configuracoes do modelo
│
├── api/                         # Camada 2: API REST (FastAPI)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/                     # Codigo da aplicação
│   │   ├── main.py              # Entry point
│   │   ├── schemas.py           # Modelos Pydantic
│   │   ├── routes/              # Endpoints
│   │   ├── services/            # Logica de negocio
│   │   ├── middleware/          # Error handlers
│   │   └── utils/               # Logger
│   └── tests/                   # Testes
│
├── webapp/                      # Camada 3: Aplicação Web (Streamlit)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                   # Entry point
│   ├── pages/                   # Paginas (predição, batch, dashboard)
│   ├── components/              # Componentes compartilhados
│   ├── utils/                   # Cliente da API
│   └── tests/                   # Testes
│
├── datascience/                 # Camada 4: Jupyter Notebook (EDA)
│   ├── Dockerfile
│   └── requirements.txt
```

---

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Modelo ML | Python 3.11+, scikit-learn, pandas, numpy |
| API | FastAPI, Uvicorn, Pydantic v2 |
| App Web | Streamlit, Plotly, httpx |
| Data Science | Jupyter Notebook, matplotlib, seaborn |
| Infra | Docker, Docker Compose |
| Testes | pytest, httpx |

---

Obrigado
Data Science Academy
