# Projeto Desenvolvido na Data Science Academy
"""Testes unitários para os módulos de pré-processamento e feature engineering.

Organização dos testes:
- Cada classe de teste agrupa testes para uma função ou módulo específico.
- Fixtures (@pytest.fixture) criam dados reutilizáveis entre os testes.
- Testes de integração (TestFullPipeline) validam o fluxo completo.

Convenção de nomenclatura:
- Classe: Test<NomeDaFuncao>
- Método: test_<comportamento_esperado>
"""

import os
import sys

import joblib
import numpy as np
import pandas as pd
import pytest

# Adiciona diretório raiz ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_preprocessing import (
    dsa_encode_target,
    dsa_handle_missing_values,
    dsa_load_data,
    dsa_prepare_features,
)
from src.feature_engineering import (
    dsa_build_preprocessor,
    dsa_get_feature_names,
    dsa_identify_feature_types,
)

# ---------------------------------------------------------------------------
# Fixtures: dados de teste reutilizáveis
# Fixtures do pytest são executadas antes de cada teste que as solicita.
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Cria DataFrame de exemplo com 3 registros para testes unitários.

    Inclui variação em todas as colunas para cobrir diferentes cenários.
    """
    return pd.DataFrame(
        {
            "customerID": ["0001-ABC", "0002-DEF", "0003-GHI"],
            "gender": ["Male", "Female", "Male"],
            "SeniorCitizen": [0, 1, 0],
            "Partner": ["Yes", "No", "Yes"],
            "Dependents": ["No", "No", "Yes"],
            "tenure": [12, 1, 60],
            "PhoneService": ["Yes", "Yes", "No"],
            "MultipleLines": ["No", "Yes", "No phone service"],
            "InternetService": ["DSL", "Fiber optic", "No"],
            "OnlineSecurity": ["Yes", "No", "No internet service"],
            "OnlineBackup": ["No", "Yes", "No internet service"],
            "DeviceProtection": ["No", "No", "No internet service"],
            "TechSupport": ["Yes", "No", "No internet service"],
            "StreamingTV": ["No", "Yes", "No internet service"],
            "StreamingMovies": ["No", "No", "No internet service"],
            "Contract": ["Month-to-month", "One year", "Two year"],
            "PaperlessBilling": ["Yes", "No", "Yes"],
            "PaymentMethod": [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
            ],
            "MonthlyCharges": [29.85, 56.95, 42.30],
            "TotalCharges": ["358.2", "56.95", "2538.0"],
            "Churn": ["No", "Yes", "No"],
        }
    )


@pytest.fixture
def integration_df() -> pd.DataFrame:
    """Carrega o dataset real para testes de integração."""
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "raw",
        "WA_Fn-UseC_-Telco-Customer-Churn.csv",
    )
    return pd.read_csv(data_path)


# ---------------------------------------------------------------------------
# Testes unitários: carregamento de dados
# ---------------------------------------------------------------------------


class TestLoadData:
    """Testes para a função load_data."""

    def test_load_data_valid_csv(self, tmp_path: object, sample_df: pd.DataFrame) -> None:
        """Testa carregamento de CSV válido."""
        filepath = str(tmp_path / "test.csv")
        sample_df.to_csv(filepath, index=False)
        result = dsa_load_data(filepath)
        assert len(result) == 3
        assert "customerID" in result.columns

    def test_load_data_file_not_found(self) -> None:
        """Testa que FileNotFoundError é lançado para arquivo inexistente."""
        with pytest.raises(FileNotFoundError):
            dsa_load_data("arquivo_inexistente.csv")

    def test_load_data_removes_duplicates(
        self, tmp_path: object, sample_df: pd.DataFrame
    ) -> None:
        """Testa remoção de duplicatas por customerID."""
        # Adiciona registro duplicado e verifica que é removido no carregamento
        df_dup = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
        filepath = str(tmp_path / "test_dup.csv")
        df_dup.to_csv(filepath, index=False)
        result = dsa_load_data(filepath)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# Testes unitários: tratamento de valores ausentes
# ---------------------------------------------------------------------------


class TestHandleMissingValues:
    """Testes para a função handle_missing_values."""

    def test_handle_total_charges_spaces(self, sample_df: pd.DataFrame) -> None:
        """Testa tratamento de espaços em TotalCharges (caso real do dataset)."""
        sample_df.loc[0, "TotalCharges"] = " "
        result = dsa_handle_missing_values(sample_df)
        assert pd.notna(result["TotalCharges"].iloc[0])
        assert isinstance(result["TotalCharges"].iloc[0], float)

    def test_handle_missing_categorical(self, sample_df: pd.DataFrame) -> None:
        """Testa preenchimento de valores ausentes em categóricas com a moda."""
        sample_df.loc[0, "gender"] = np.nan
        result = dsa_handle_missing_values(sample_df)
        assert pd.notna(result["gender"].iloc[0])

    def test_no_missing_after_treatment(self, sample_df: pd.DataFrame) -> None:
        """Testa que não restam valores ausentes após tratamento completo."""
        sample_df.loc[0, "TotalCharges"] = " "
        sample_df.loc[1, "gender"] = np.nan
        result = dsa_handle_missing_values(sample_df)
        assert result.isna().sum().sum() == 0


# ---------------------------------------------------------------------------
# Testes unitários: encoding da variável alvo
# ---------------------------------------------------------------------------


class TestEncodeTarget:
    """Testes para a função encode_target."""

    def test_encode_yes_no(self, sample_df: pd.DataFrame) -> None:
        """Testa conversão de Yes/No para 1/0."""
        result = dsa_encode_target(sample_df)
        assert set(result["Churn"].unique()) == {0, 1}

    def test_encode_missing_column(self, sample_df: pd.DataFrame) -> None:
        """Testa que KeyError é lançado quando a coluna alvo não existe."""
        with pytest.raises(KeyError):
            dsa_encode_target(sample_df, target_col="NonExistent")

    def test_encode_preserves_other_columns(self, sample_df: pd.DataFrame) -> None:
        """Testa que o encoding não altera outras colunas do DataFrame."""
        result = dsa_encode_target(sample_df)
        assert result["gender"].tolist() == sample_df["gender"].tolist()


# ---------------------------------------------------------------------------
# Testes unitários: separação de features
# ---------------------------------------------------------------------------


class TestPrepareFeatures:
    """Testes para a função prepare_features."""

    def test_removes_id_column(self, sample_df: pd.DataFrame) -> None:
        """Testa que a coluna customerID é removida das features."""
        sample_df = dsa_encode_target(sample_df)
        X, y = dsa_prepare_features(sample_df)
        assert "customerID" not in X.columns

    def test_target_separated(self, sample_df: pd.DataFrame) -> None:
        """Testa que X não contém a coluna alvo e y tem o mesmo tamanho."""
        sample_df = dsa_encode_target(sample_df)
        X, y = dsa_prepare_features(sample_df)
        assert "Churn" not in X.columns
        assert len(y) == len(X)


# ---------------------------------------------------------------------------
# Testes unitários: feature engineering
# ---------------------------------------------------------------------------


class TestFeatureEngineering:
    """Testes para funções de feature engineering (ColumnTransformer)."""

    def test_dsa_build_preprocessor(self) -> None:
        """Testa que o ColumnTransformer é criado sem erros."""
        preprocessor = dsa_build_preprocessor(
            numeric_features=["tenure", "MonthlyCharges"],
            categorical_features=["gender", "Contract"],
        )
        assert preprocessor is not None

    def test_preprocessor_transforms_data(self, sample_df: pd.DataFrame) -> None:
        """Testa que o preprocessor transforma dados mantendo o número de linhas."""
        sample_df = dsa_handle_missing_values(sample_df)
        sample_df = dsa_encode_target(sample_df)
        X, y = dsa_prepare_features(sample_df)

        numeric_features = ["tenure", "MonthlyCharges", "TotalCharges"]
        categorical_features = [
            c for c in X.columns if c not in numeric_features
        ]

        preprocessor = dsa_build_preprocessor(numeric_features, categorical_features)
        X_transformed = preprocessor.fit_transform(X)
        assert X_transformed.shape[0] == len(X)

    def test_dsa_get_feature_names(self, sample_df: pd.DataFrame) -> None:
        """Testa que os nomes das features transformadas são recuperados."""
        sample_df = dsa_handle_missing_values(sample_df)
        sample_df = dsa_encode_target(sample_df)
        X, y = dsa_prepare_features(sample_df)

        numeric_features = ["tenure", "MonthlyCharges", "TotalCharges"]
        categorical_features = [
            c for c in X.columns if c not in numeric_features
        ]

        preprocessor = dsa_build_preprocessor(numeric_features, categorical_features)
        preprocessor.fit(X)
        names = dsa_get_feature_names(preprocessor, X)
        assert len(names) > 0
        assert "tenure" in names

    def test_dsa_identify_feature_types(self, sample_df: pd.DataFrame) -> None:
        """Testa identificação automática de tipos de features."""
        sample_df = dsa_handle_missing_values(sample_df)
        sample_df = dsa_encode_target(sample_df)
        X, y = dsa_prepare_features(sample_df)

        numeric, categorical = dsa_identify_feature_types(X)
        assert "tenure" in numeric or "tenure" in categorical
        assert len(numeric) + len(categorical) > 0


# ---------------------------------------------------------------------------
# Testes de integração: pipeline completo (treino → avaliação → serialização)
# ---------------------------------------------------------------------------


class TestFullPipeline:
    """Testes de integração do pipeline completo de ML.

    Estes testes validam que todas as etapas funcionam juntas:
    pré-processamento → feature engineering → treinamento → predição.
    """

    def test_full_pipeline_trains(self, integration_df: pd.DataFrame) -> None:
        """Testa que o pipeline completo treina e atinge accuracy > 50%."""
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline

        df = dsa_handle_missing_values(integration_df)
        df = dsa_encode_target(df)
        X, y = dsa_prepare_features(df)

        numeric_features = ["tenure", "MonthlyCharges", "TotalCharges"]
        categorical_features = [
            c for c in X.columns if c not in numeric_features
        ]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        preprocessor = dsa_build_preprocessor(numeric_features, categorical_features)
        pipeline = Pipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    GradientBoostingClassifier(
                        n_estimators=50, random_state=42
                    ),
                ),
            ]
        )

        pipeline.fit(X_train, y_train)
        score = pipeline.score(X_test, y_test)
        # Modelo deve ser melhor que classificação aleatória (50%)
        assert score > 0.5

    def test_model_serialization(
        self, tmp_path: object, integration_df: pd.DataFrame
    ) -> None:
        """Testa ciclo completo: treino → serialização → carregamento → predição."""
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline

        df = dsa_handle_missing_values(integration_df)
        df = dsa_encode_target(df)
        X, y = dsa_prepare_features(df)

        numeric_features = ["tenure", "MonthlyCharges", "TotalCharges"]
        categorical_features = [
            c for c in X.columns if c not in numeric_features
        ]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        preprocessor = dsa_build_preprocessor(numeric_features, categorical_features)
        pipeline = Pipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    GradientBoostingClassifier(
                        n_estimators=50, random_state=42
                    ),
                ),
            ]
        )

        pipeline.fit(X_train, y_train)

        # Serializa o pipeline treinado com joblib
        model_path = str(tmp_path / "model.joblib")
        joblib.dump(pipeline, model_path)

        # Carrega o modelo serializado e verifica que as predições são válidas
        loaded_model = joblib.load(model_path)
        predictions = loaded_model.predict(X_test)
        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})


