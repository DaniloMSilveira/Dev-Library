# Projeto Desenvolvido na Data Science Academy
#
# Dockerfile — Container da API REST (FastAPI)
#
# Este container serve a API de predição de churn via FastAPI + Uvicorn.
# O modelo de ML é montado como volume externo (somente leitura) pelo
# docker-compose.yml, ou seja, este container não contém o modelo no build.
#
# O Uvicorn é um servidor ASGI (Asynchronous Server Gateway Interface)
# de alta performance, ideal para frameworks async como o FastAPI.

FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o curl, necessário para os health checks (verificação de saúde).
# O --no-install-recommends evita pacotes extras desnecessários.
# O rm -rf limpa o cache do apt para reduzir o tamanho da imagem.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python (camada cacheada pelo Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação FastAPI e os testes
COPY app/ app/
COPY tests/ tests/

# Cria o diretório onde o volume com o modelo será montado.
# O modelo (.joblib) será disponibilizado via volume Docker read-only.
RUN mkdir -p models

# Segurança: cria e utiliza um usuário não-root
RUN useradd --create-home appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check interno do Docker — verifica periodicamente se a API responde.
# Usado pelo Docker Compose para determinar quando o webapp pode iniciar.
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Documenta a porta exposta pelo container (apenas informativo)
EXPOSE 8000

# Inicia o servidor Uvicorn com 2 workers para concorrência.
# --host 0.0.0.0: aceita conexões de qualquer interface de rede
# --workers 2: cria 2 processos para atender requisições em paralelo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]




