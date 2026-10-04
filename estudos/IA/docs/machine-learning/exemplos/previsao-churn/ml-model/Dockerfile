# Projeto Desenvolvido na Data Science Academy
#
# Dockerfile — Container de treinamento do modelo de Machine Learning
#
# Este container executa o pipeline de treinamento do modelo de previsão
# de churn e salva o artefato serializado (.joblib) no diretório /app/models.
# Após o treinamento, o container encerra automaticamente.
#
# A imagem base python:3.11-slim é uma versão enxuta do Debian com Python,
# sem pacotes extras desnecessários, o que reduz o tamanho da imagem.

FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala as dependências Python primeiro (otimização de cache Docker).
# Como o requirements.txt muda com pouca frequência, o Docker reutiliza
# esta camada em builds subsequentes, acelerando o processo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte, configurações e dados para o container
COPY src/ src/
COPY configs/ configs/
COPY data/ data/
COPY tests/ tests/

# Cria o diretório de saída onde o modelo treinado será salvo.
# Este diretório é montado como volume no docker-compose.yml
# para compartilhar o artefato com o serviço da API.
RUN mkdir -p models

# Segurança: cria um usuário não-root para executar o container.
# Executar containers como root é uma má prática de segurança,
# pois um eventual exploit teria acesso privilegiado ao sistema.
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

# Comando executado ao iniciar o container: treina o modelo
CMD ["python", "src/train.py"]
