# Projeto Desenvolvido na Data Science Academy
"""Serviço de carregamento e inferência do modelo de ML.

Implementa o padrão Singleton para garantir que apenas uma instância
do modelo exista em memória durante toda a vida da aplicação.

Padrões utilizados:
- Singleton (__new__): garante instância única do serviço
- Lazy Loading: o modelo só é carregado quando load_model() é chamado
- Inferência Vetorizada: predict_batch processa todo o DataFrame de uma vez

O pipeline completo do scikit-learn (preprocessor + classifier) é carregado
via joblib, incluindo todas as transformações. Isso garante que os dados
de entrada recebem o mesmo pré-processamento usado no treinamento.
"""

import json
import os
from typing import Any

import joblib
import pandas as pd

from app.utils.logger import setup_logger

logger = setup_logger("model_service")


class ModelService:
    """Serviço singleton para gerenciamento do modelo de previsão de churn.

    Realiza carregamento lazy do pipeline serializado e fornece
    métodos para predição individual e em lote.

    O padrão Singleton é implementado via __new__: qualquer chamada a
    ModelService() retorna sempre a mesma instância, compartilhando
    o modelo carregado entre todas as requisições.
    """

    # Atributos de classe (compartilhados por todas as instâncias = a única instância)
    _instance: "ModelService | None" = None  # Referência à instância singleton
    _model: Any = None                        # Pipeline scikit-learn carregado
    _metadata: dict | None = None             # Metadados do modelo (versão, métricas)

    def __new__(cls) -> "ModelService":
        """Implementa o padrão Singleton.

        Se a instância ainda não existe, cria uma nova.
        Caso contrário, retorna a instância existente.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self) -> None:
        """Carrega o pipeline de ML serializado via joblib.

        O caminho do modelo é obtido da variável de ambiente MODEL_PATH.
        Também carrega os metadados (versão, métricas) se o arquivo existir.

        Raises:
            FileNotFoundError: Se o arquivo do modelo não for encontrado.
            RuntimeError: Se houver erro ao carregar o modelo.
        """
        model_path = os.environ.get(
            "MODEL_PATH", "/app/models/churn_model.joblib"
        )
        metadata_path = model_path.replace(
            "churn_model.joblib", "model_metadata.json"
        )

        logger.info("Carregando modelo", extra={"model_path": model_path})

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Arquivo do modelo não encontrado: {model_path}"
            )

        # joblib.load() reconstrói o objeto Pipeline completo a partir do arquivo
        try:
            self._model = joblib.load(model_path)
            logger.info("Modelo carregado com sucesso")
        except Exception as e:
            logger.error("Erro ao carregar modelo", extra={"error": str(e)})
            raise RuntimeError(f"Erro ao carregar modelo: {e}") from e

        # Carrega metadados (versão, métricas, features) se disponíveis
        if os.path.exists(metadata_path):
            with open(metadata_path) as f:
                self._metadata = json.load(f)
            logger.info("Metadados carregados com sucesso")
        else:
            logger.warning(
                "Arquivo de metadados não encontrado",
                extra={"metadata_path": metadata_path},
            )
            self._metadata = {
                "model_version": "unknown",
                "trained_at": "unknown",
                "metrics": {},
                "feature_names": [],
            }

    @property
    def is_loaded(self) -> bool:
        """Verifica se o modelo está carregado em memória.

        Returns:
            True se o modelo está carregado e pronto para inferência.
        """
        return self._model is not None

    def predict(self, data: dict) -> dict:
        """Realiza predição de churn para um único cliente.

        Delega para predict_batch() com lista de um elemento,
        reutilizando a mesma lógica vetorizada.

        Args:
            data: Dicionário com os dados do cliente (19 features).

        Returns:
            Dicionário com prediction, probability e feature_importance.

        Raises:
            RuntimeError: Se o modelo não estiver carregado.
        """
        return self.predict_batch([data])[0]

    def predict_batch(self, data: list[dict]) -> list[dict]:
        """Realiza predição de churn para múltiplos clientes (inferência vetorizada).

        Inferência vetorizada: converte toda a lista em um DataFrame e chama
        predict/predict_proba uma única vez, em vez de iterar cliente por cliente.
        Isso é significativamente mais rápido graças às otimizações NumPy/scikit-learn.

        Args:
            data: Lista de dicionários com dados dos clientes.

        Returns:
            Lista de dicionários com resultados de predição.

        Raises:
            RuntimeError: Se o modelo não estiver carregado.
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo não carregado. Execute load_model().")

        # Converte lista de dicionários em DataFrame (entrada esperada pelo Pipeline)
        df = pd.DataFrame(data)

        # predict() retorna a classe (0 ou 1) para cada cliente
        predictions = self._model.predict(df)

        # predict_proba()[:, 1] retorna a probabilidade da classe 1 (churn)
        probabilities = self._model.predict_proba(df)[:, 1]

        # Feature importance é global do modelo (não varia por cliente)
        feature_importance = self._get_feature_importance()

        # Monta o resultado combinando predição, probabilidade e features
        return [
            {
                "prediction": "Sim" if int(pred) == 1 else "Não",
                "probability": round(float(prob), 4),
                "feature_importance": feature_importance,
            }
            for pred, prob in zip(predictions, probabilities)
        ]

    def _get_feature_importance(self) -> list[dict[str, Any]]:
        """Retorna as top 10 features por importância do modelo.

        Acessa o classificador dentro do Pipeline para extrair
        feature_importances_ (importância baseada na redução de impureza Gini).

        Returns:
            Lista de dicionários com feature e importance, ordenada decrescentemente.
        """
        try:
            # Acessa os passos do Pipeline pelo nome
            classifier = self._model.named_steps["classifier"]
            preprocessor = self._model.named_steps["preprocessor"]

            importances = classifier.feature_importances_

            # Reconstrói os nomes das features após transformação do ColumnTransformer
            feature_names: list[str] = []
            for name, transformer, columns in preprocessor.transformers_:
                if name == "num":
                    # Features numéricas mantêm os nomes originais
                    feature_names.extend(columns)
                elif name == "cat":
                    # OneHotEncoder cria novas colunas binárias
                    if hasattr(transformer, "get_feature_names_out"):
                        cat_names = transformer.get_feature_names_out(
                            columns
                        ).tolist()
                        feature_names.extend(cat_names)

            # Combina nomes e importâncias, ordena e retorna top 10
            feat_imp = sorted(
                [
                    {"feature": name, "importance": round(float(imp), 6)}
                    for name, imp in zip(feature_names, importances)
                ],
                key=lambda x: x["importance"],
                reverse=True,
            )

            return feat_imp[:10]

        except Exception as e:
            logger.warning(
                "Erro ao calcular feature importance",
                extra={"error": str(e)},
            )
            return []

    def get_model_info(self) -> dict:
        """Retorna metadados e informações do modelo carregado.

        Returns:
            Dicionário com versão, data de treinamento, métricas e features.
        """
        if self._metadata is None:
            return {
                "model_version": "unknown",
                "trained_at": "unknown",
                "metrics": {},
                "feature_names": [],
            }

        return {
            "model_version": self._metadata.get("model_version", "unknown"),
            "trained_at": self._metadata.get("trained_at", "unknown"),
            "metrics": self._metadata.get("metrics", {}),
            "feature_names": self._metadata.get("feature_names", []),
        }
