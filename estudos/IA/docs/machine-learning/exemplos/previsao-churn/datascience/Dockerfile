# Projeto Desenvolvido na Data Science Academy
#
# Dockerfile — Container Jupyter Notebook para EDA e Modelagem
#
# Este container disponibiliza o Jupyter Notebook na porta 8888 para
# execução interativa do notebook de Análise Exploratória de Dados (EDA)
# e modelagem. Reutiliza os módulos de pré-processamento e feature
# engineering do ml-model.

FROM python:3.11-slim

WORKDIR /app

# Instala dependências Python (mesmas do ml-model + jupyter)
COPY datascience/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os módulos fonte do ml-model (pré-processamento, feature engineering, avaliação)
COPY ml-model/src/ src/

# Copia os dados e o notebook
COPY ml-model/data/ data/
COPY ml-model/notebooks/ notebooks/

# Segurança: cria usuário não-root
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8888

# Inicia o Jupyter Notebook sem autenticação (ambiente local/demonstração)
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--NotebookApp.token=''", "--NotebookApp.password=''", "--notebook-dir=/app/notebooks"]
