# Projeto Desenvolvido na Data Science Academy
"""Módulo de feature engineering para o modelo de previsão de churn.

Contém funções para construção do pipeline de pré-processamento
com transformações numéricas e categóricas usando scikit-learn.

Feature engineering é o processo de transformar dados brutos em features
que melhor representam o problema para o modelo de ML. Neste módulo,
usamos o ColumnTransformer do scikit-learn para aplicar transformações
diferentes a cada tipo de feature (numérica ou categórica).
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def dsa_build_preprocessor(
    numeric_features: list[str], categorical_features: list[str]
) -> ColumnTransformer:
    """Constrói o ColumnTransformer com transformações para features numéricas e categóricas.

    O ColumnTransformer permite aplicar transformações diferentes a subconjuntos
    de colunas do DataFrame. Isso é essencial porque features numéricas e
    categóricas requerem tratamentos distintos:

    - Numéricas (StandardScaler): normaliza para média=0 e desvio padrão=1,
      evitando que features com escalas grandes dominem o modelo.
    - Categóricas (OneHotEncoder): converte categorias em variáveis binárias
      (0/1), formato necessário para algoritmos baseados em árvore e gradiente.

    Args:
        numeric_features: Lista de nomes das features numéricas.
        categorical_features: Lista de nomes das features categóricas.

    Returns:
        ColumnTransformer configurado com StandardScaler para numéricas
        e OneHotEncoder para categóricas.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            # StandardScaler: z = (x - média) / desvio_padrão
            ("num", StandardScaler(), numeric_features),
            (
                "cat",
                OneHotEncoder(
                    drop="first",           # Remove primeira categoria para evitar multicolinearidade
                    handle_unknown="ignore", # Ignora categorias não vistas no treino (evita erro na API)
                    sparse_output=False,     # Retorna array denso em vez de matriz esparsa
                ),
                categorical_features,
            ),
        ],
        # Colunas não listadas são descartadas (segurança contra features inesperadas)
        remainder="drop",
    )

    return preprocessor


def dsa_get_feature_names(
    preprocessor: ColumnTransformer, X: pd.DataFrame
) -> list[str]:
    """Retorna os nomes das features após transformação pelo ColumnTransformer.

    Após o OneHotEncoder, as features categóricas são expandidas em múltiplas
    colunas binárias (ex: Contract → Contract_One year, Contract_Two year).
    Esta função recupera os nomes corretos para uso na feature importance.

    Args:
        preprocessor: ColumnTransformer já ajustado (fit).
        X: DataFrame original usado no fit.

    Returns:
        Lista de nomes das features transformadas.
    """
    feature_names: list[str] = []

    # Itera sobre os transformadores do ColumnTransformer
    for name, transformer, columns in preprocessor.transformers_:
        if name == "num":
            # Features numéricas mantêm os nomes originais (StandardScaler não cria colunas)
            feature_names.extend(columns)
        elif name == "cat":
            # OneHotEncoder cria novas colunas — recupera nomes via get_feature_names_out
            if hasattr(transformer, "get_feature_names_out"):
                cat_names = transformer.get_feature_names_out(columns).tolist()
                feature_names.extend(cat_names)
            else:
                feature_names.extend(columns)

    return feature_names


def dsa_identify_feature_types(
    df: pd.DataFrame,
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Identifica features numéricas e categóricas no DataFrame.

    Se as listas não forem fornecidas, identifica automaticamente
    com base nos tipos de dados das colunas (dtype).

    Args:
        df: DataFrame com as features.
        numeric_features: Lista de features numéricas (opcional).
        categorical_features: Lista de features categóricas (opcional).

    Returns:
        Tupla (numeric_features, categorical_features).
    """
    # Identificação automática com base no dtype do pandas
    if numeric_features is None:
        numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()

    if categorical_features is None:
        categorical_features = df.select_dtypes(
            include=["object", "str", "category"]
        ).columns.tolist()

    # Valida que todas as features especificadas existem no DataFrame
    for feat in numeric_features:
        if feat not in df.columns:
            raise KeyError(f"Feature numérica '{feat}' não encontrada no DataFrame.")

    for feat in categorical_features:
        if feat not in df.columns:
            raise KeyError(f"Feature categórica '{feat}' não encontrada no DataFrame.")

    return numeric_features, categorical_features
