# Projeto Desenvolvido na Data Science Academy
"""Script de treinamento do modelo de previsão de churn.

Executa o pipeline completo de Machine Learning:
1. Carregamento dos dados
2. Pré-processamento (limpeza e encoding)
3. Feature engineering (transformações numéricas e categóricas)
4. Treinamento (GradientBoostingClassifier com balanceamento de classes)
5. Avaliação (métricas de desempenho no conjunto de teste)
6. Serialização (modelo + metadados salvos em disco)

Este script é o entry point do container ml-model e é executado
automaticamente ao iniciar o Docker Compose.
"""

import json
import os
import sys
from datetime import datetime, timezone

import joblib
import yaml
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.utils.class_weight import compute_sample_weight

# Adiciona diretório raiz ao path para permitir imports relativos
# (necessário porque o script é executado diretamente via CMD no Docker)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_preprocessing import (
    dsa_encode_target,
    dsa_handle_missing_values,
    dsa_load_data,
    dsa_prepare_features,
)
from src.evaluate import (
    dsa_evaluate_model,
    dsa_get_feature_importance,
    dsa_print_evaluation_report,
)
from src.feature_engineering import (
    dsa_build_preprocessor,
    dsa_get_feature_names,
    dsa_identify_feature_types,
)
def dsa_load_config(config_path: str) -> dict:
    """Carrega configurações do modelo a partir de arquivo YAML.

    Usar arquivo de configuração externo permite alterar hiperparâmetros
    sem modificar o código-fonte (separação de configuração e código).

    Args:
        config_path: Caminho para o arquivo de configuração.

    Returns:
        Dicionário com as configurações.
    """
    with open(config_path) as f:
        return yaml.safe_load(f)


def dsa_train_model() -> None:
    """Executa o pipeline completo de treinamento do modelo."""

    # Determina caminhos base a partir da localização deste script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "configs", "model_config.yaml")

    print("=" * 60)
    print("TREINAMENTO DO MODELO DE PREVISÃO DE CHURN")
    print("=" * 60)

    # -------------------------------------------------------------------------
    # Etapa 1: Carregamento dos dados
    # -------------------------------------------------------------------------
    config = dsa_load_config(config_path)
    print(f"\nConfiguração carregada de: {config_path}")

    data_path = os.path.join(base_dir, config["data"]["raw_path"])
    print(f"Carregando dados de: {data_path}")
    df = dsa_load_data(data_path)

    print(f"Shape dos dados: {df.shape}")

    # -------------------------------------------------------------------------
    # Etapa 2: Pré-processamento
    # Trata valores ausentes e converte a variável alvo para formato numérico.
    # -------------------------------------------------------------------------
    print("\n--- Pré-processamento ---")
    df = dsa_handle_missing_values(df)
    df = dsa_encode_target(df, config["data"]["target_column"])

    # Separa features (X) e variável alvo (y)
    X, y = dsa_prepare_features(
        df,
        target_col=config["data"]["target_column"],
        id_col=config["features"]["id_column"],
    )

    print(f"Features: {X.shape[1]} | Amostras: {X.shape[0]}")
    print(f"Distribuição do target: {y.value_counts().to_dict()}")

    # -------------------------------------------------------------------------
    # Etapa 3: Feature engineering
    # Identifica tipos de features e prepara o ColumnTransformer.
    # -------------------------------------------------------------------------
    numeric_features, categorical_features = dsa_identify_feature_types(
        X,
        numeric_features=config["features"]["numeric"],
        categorical_features=config["features"]["categorical"],
    )

    print(f"Features numéricas ({len(numeric_features)}): {numeric_features}")
    print(f"Features categóricas ({len(categorical_features)}): {len(categorical_features)} colunas")

    # -------------------------------------------------------------------------
    # Etapa 4: Split treino/teste
    # Divide os dados em treino (80%) e teste (20%) com estratificação.
    # stratify=y garante que a proporção de churn seja mantida em ambos os
    # conjuntos, o que é essencial quando as classes são desbalanceadas.
    # -------------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config["data"]["test_size"],
        random_state=config["data"]["random_state"],
        stratify=y,
    )

    print(f"\nTreino: {X_train.shape[0]} | Teste: {X_test.shape[0]}")

    # -------------------------------------------------------------------------
    # Etapa 5: Construção e treinamento do pipeline
    # O Pipeline do scikit-learn encadeia preprocessor + classificador em um
    # único objeto. Isso garante que o mesmo pré-processamento é aplicado
    # tanto no treino quanto na inferência (evita data leakage).
    # -------------------------------------------------------------------------
    print("\n--- Treinamento ---")
    preprocessor = dsa_build_preprocessor(numeric_features, categorical_features)
    model_params = config["model"]["params"]

    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", GradientBoostingClassifier(**model_params)),
        ]
    )

    # compute_sample_weight("balanced") atribui pesos inversamente proporcionais
    # à frequência de cada classe. Isso compensa o desbalanceamento do dataset
    # (~26% churn vs ~74% não-churn), fazendo o modelo dar mais atenção à
    # classe minoritária (churn).
    sample_weights = compute_sample_weight("balanced", y_train)

    print(f"Algoritmo: {config['model']['algorithm']}")
    print(f"Parâmetros: {model_params}")
    print(f"Balanceamento: sample_weight='balanced'")

    # O prefixo "classifier__" indica que sample_weight é passado ao
    # passo "classifier" do Pipeline (notação de duplo underscore do scikit-learn)
    pipeline.fit(X_train, y_train, classifier__sample_weight=sample_weights)
    print("Treinamento concluído!")

    # -------------------------------------------------------------------------
    # Etapa 6: Avaliação do modelo no conjunto de teste
    # O conjunto de teste nunca foi visto durante o treinamento, portanto as
    # métricas refletem a capacidade de generalização do modelo.
    # -------------------------------------------------------------------------
    print("\n--- Avaliação ---")
    metrics = dsa_evaluate_model(pipeline, X_test, y_test)

    # Extrai feature importance do modelo treinado
    fitted_preprocessor = pipeline.named_steps["preprocessor"]
    feature_names = dsa_get_feature_names(fitted_preprocessor, X_train)
    feature_importance = dsa_get_feature_importance(pipeline, feature_names)

    y_pred = pipeline.predict(X_test)
    dsa_print_evaluation_report(metrics, feature_importance, y_test, y_pred)

    # -------------------------------------------------------------------------
    # Etapa 7: Serialização do modelo (persistência)
    # joblib salva o Pipeline completo (preprocessor + classifier) em um
    # único arquivo .joblib. Na API, basta carregar este arquivo para
    # realizar predições com todas as transformações incluídas.
    # -------------------------------------------------------------------------
    print("\n--- Serialização ---")
    models_dir = os.path.join(base_dir, os.path.dirname(config["output"]["model_path"]))
    os.makedirs(models_dir, exist_ok=True)

    model_path = os.path.join(base_dir, config["output"]["model_path"])
    joblib.dump(pipeline, model_path)
    print(f"Modelo salvo em: {model_path}")

    # Salva metadados em JSON separado para consulta pela API
    # (versão, métricas, features, hiperparâmetros)
    metadata = {
        "model_version": "1.0.0",
        "algorithm": config["model"]["algorithm"],
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "feature_names": list(X.columns),
        "feature_importance": feature_importance[:10],
        "n_training_samples": int(X_train.shape[0]),
        "n_test_samples": int(X_test.shape[0]),
        "params": model_params,
    }

    metadata_path = os.path.join(base_dir, config["output"]["metadata_path"])
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Metadados salvos em: {metadata_path}")

    print("\n" + "=" * 60)
    print("TREINAMENTO FINALIZADO COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    dsa_train_model()
