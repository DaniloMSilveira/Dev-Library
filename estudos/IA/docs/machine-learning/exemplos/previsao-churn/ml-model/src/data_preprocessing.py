# Projeto Desenvolvido na Data Science Academy
"""Módulo de pré-processamento de dados para o modelo de previsão de churn.

Contém funções para carregamento, limpeza e transformação dos dados brutos
do dataset Telco Customer Churn.

O pré-processamento é a primeira etapa do pipeline de ML e é responsável por
garantir que os dados estejam limpos e consistentes antes do treinamento.
Cada função segue o princípio de responsabilidade única (SRP): uma tarefa por função.
"""

import numpy as np
import pandas as pd


def dsa_load_data(filepath: str) -> pd.DataFrame:
    """Carrega o dataset CSV e realiza limpeza inicial.

    Args:
        filepath: Caminho para o arquivo CSV dos dados brutos.

    Returns:
        DataFrame com os dados carregados e limpos.

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
        ValueError: Se o arquivo estiver vazio ou com formato inválido.
    """
    df = pd.read_csv(filepath)

    if df.empty:
        raise ValueError(f"O arquivo {filepath} está vazio.")

    # Remove espaços em branco nos nomes das colunas.
    # Isso evita erros silenciosos ao acessar colunas como "tenure " vs "tenure".
    df.columns = df.columns.str.strip()

    # Remove duplicatas baseado no customerID se existir.
    # Registros duplicados distorcem o treinamento do modelo.
    if "customerID" in df.columns:
        df = df.drop_duplicates(subset=["customerID"])

    return df


def dsa_handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Trata valores ausentes no dataset.

    Estratégia de imputação:
    - TotalCharges: converte para numérico e preenche missing com a mediana.
    - Colunas categóricas: preenche com a moda (valor mais frequente).
    - Colunas numéricas: preenche com a mediana (robusta a outliers).

    A mediana é preferida à média para dados numéricos porque é menos
    sensível a valores extremos (outliers).

    Args:
        df: DataFrame com os dados brutos.

    Returns:
        DataFrame com valores ausentes tratados.
    """
    # Cria cópia para não alterar o DataFrame original (imutabilidade)
    df = df.copy()

    # Tratamento específico da coluna TotalCharges.
    # No dataset original, TotalCharges é uma string com espaços em branco
    # para clientes novos (tenure=0), por isso precisa de conversão explícita.
    if "TotalCharges" in df.columns:
        # Substitui strings vazias ou só com espaços por NaN
        df["TotalCharges"] = df["TotalCharges"].replace(r"^\s*$", np.nan, regex=True)
        # Converte para numérico — valores não-conversíveis viram NaN
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        # Preenche NaN com a mediana (imputação estatística)
        median_total = df["TotalCharges"].median()
        df["TotalCharges"] = df["TotalCharges"].fillna(median_total)

    # Preenche colunas numéricas restantes com mediana
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    # Preenche colunas categóricas com moda (valor mais frequente).
    # mode()[0] retorna o primeiro valor mais frequente caso haja empate.
    categorical_cols = df.select_dtypes(include=["object", "str"]).columns
    for col in categorical_cols:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].mode()[0])

    return df


def dsa_encode_target(df: pd.DataFrame, target_col: str = "Churn") -> pd.DataFrame:
    """Converte a coluna alvo Churn para valores binários (1/0).

    Modelos de classificação do scikit-learn esperam variáveis alvo numéricas.
    A conversão Yes→1, No→0 é o padrão para classificação binária.

    Args:
        df: DataFrame com a coluna alvo.
        target_col: Nome da coluna alvo. Default: 'Churn'.

    Returns:
        DataFrame com a coluna alvo codificada como 0/1.
    """
    df = df.copy()

    if target_col not in df.columns:
        raise KeyError(f"Coluna '{target_col}' não encontrada no DataFrame.")

    # Mapeia Yes/No para 1/0 (aceita variações de capitalização)
    mapping = {"Yes": 1, "No": 0, "yes": 1, "no": 0}
    if df[target_col].dtype == "object" or pd.api.types.is_string_dtype(df[target_col]):
        df[target_col] = df[target_col].map(mapping).fillna(0)

    # Garante que a coluna é inteira (scikit-learn espera int para classificação)
    df[target_col] = df[target_col].astype(int)

    return df


def dsa_prepare_features(
    df: pd.DataFrame, target_col: str = "Churn", id_col: str = "customerID"
) -> tuple[pd.DataFrame, pd.Series]:
    """Separa features (X) e variável alvo (y), removendo coluna de ID.

    Esta separação é fundamental em ML: o modelo aprende a relação entre
    X (features de entrada) e y (variável que queremos prever).
    A coluna de ID é removida pois não contém informação preditiva.

    Args:
        df: DataFrame preprocessado.
        target_col: Nome da coluna alvo.
        id_col: Nome da coluna de identificação do cliente.

    Returns:
        Tupla (X, y) com features e variável alvo.
    """
    df = df.copy()

    # Remove coluna de ID — não é uma feature preditiva
    if id_col in df.columns:
        df = df.drop(columns=[id_col])

    # Separa variável alvo (y) das features de entrada (X)
    y = df[target_col]
    X = df.drop(columns=[target_col])

    return X, y
