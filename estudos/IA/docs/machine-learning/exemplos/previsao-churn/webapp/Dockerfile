# Projeto Desenvolvido na Data Science Academy
#
# Dockerfile — Container da Aplicação Web (Streamlit)
#
# Este container serve a interface web para o usuário final.
# A aplicação NÃO acessa o modelo de ML diretamente — toda comunicação
# é feita via chamadas HTTP para a API REST (container "api").
#
# O Streamlit é um framework Python para criação rápida de interfaces
# de dados, sem necessidade de HTML, CSS ou JavaScript.

FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o curl para health checks do Docker
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python (camada cacheada pelo Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação Streamlit.
# A estrutura é: entry point (app.py), páginas, componentes, utilitários e assets.
COPY App.py .
COPY pages/ pages/
COPY components/ components/
COPY utils/ utils/
COPY assets/ assets/
COPY tests/ tests/

# Segurança: cria e utiliza um usuário não-root
RUN useradd --create-home appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check usando o endpoint nativo de saúde do Streamlit
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Documenta a porta exposta pelo container
EXPOSE 8501

# Inicia o Streamlit em modo headless (sem navegador).
# --server.address=0.0.0.0: aceita conexões externas (necessário no Docker)
# --server.headless=true: não tenta abrir navegador automaticamente
CMD ["streamlit", "run", "App.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
