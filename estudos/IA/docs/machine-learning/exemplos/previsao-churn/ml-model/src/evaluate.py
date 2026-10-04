# Projeto Desenvolvido na Data Science Academy
"""Módulo de avaliação do modelo de previsão de churn.

Contém funções para cálculo de métricas de desempenho e
análise de importância de features.

Métricas utilizadas:
- Accuracy: proporção de acertos totais
- Precision: dos que o modelo disse "churn", quantos realmente são
- Recall: dos que realmente são churn, quantos o modelo identificou
- F1-Score: média harmônica entre precision e recall (equilíbrio)
- AUC-ROC: capacidade de distinguir entre as classes (independente do limiar)

Em problemas de churn, o Recall é especialmente importante porque o custo
de não identificar um cliente que vai cancelar (falso negativo) é maior
do que o custo de abordar um cliente que não ia cancelar (falso positivo).
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline


def dsa_evaluate_model(
    model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series
) -> dict[str, float]:
    """Avalia o modelo no conjunto de teste e retorna métricas.

    Args:
        model: Pipeline treinado (preprocessor + classificador).
        X_test: Features do conjunto de teste.
        y_test: Variável alvo do conjunto de teste.

    Returns:
        Dicionário com métricas: accuracy, precision, recall, f1, auc_roc.
    """
    # predict() retorna a classe (0 ou 1)
    y_pred = model.predict(X_test)

    # predict_proba() retorna probabilidades — usamos a coluna da classe 1 (churn)
    # para calcular a AUC-ROC, que avalia a qualidade do ranking de probabilidades
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "auc_roc": round(float(roc_auc_score(y_test, y_proba)), 4),
    }

    return metrics


def dsa_get_feature_importance(
    model: Pipeline, feature_names: list[str]
) -> list[dict[str, float | str]]:
    """Retorna a importância das features ordenada de forma decrescente.

    O GradientBoostingClassifier calcula a importância com base na redução
    de impureza (Gini) proporcionada por cada feature nas árvores de decisão.
    Features com maior importância tiveram maior contribuição para as predições.

    Args:
        model: Pipeline treinado com classificador que possui feature_importances_.
        feature_names: Lista de nomes das features transformadas.

    Returns:
        Lista de dicionários com 'feature' e 'importance', ordenada decrescente.
    """
    # Acessa o classificador dentro do Pipeline
    classifier = model.named_steps["classifier"]

    # Verifica se o classificador suporta feature importance
    # (nem todos os modelos do scikit-learn possuem este atributo)
    if not hasattr(classifier, "feature_importances_"):
        raise AttributeError(
            "O classificador não possui atributo 'feature_importances_'."
        )

    importances = classifier.feature_importances_

    # Combina nomes das features com seus valores de importância
    feature_importance = [
        {"feature": name, "importance": round(float(imp), 6)}
        for name, imp in zip(feature_names, importances)
    ]

    # Ordena da mais importante para a menos importante
    feature_importance.sort(key=lambda x: x["importance"], reverse=True)

    return feature_importance


def dsa_print_evaluation_report(
    metrics: dict[str, float],
    feature_importance: list[dict[str, float | str]],
    y_test: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    top_n: int = 10,
) -> None:
    """Imprime relatório formatado de avaliação do modelo.

    Args:
        metrics: Dicionário com métricas de avaliação.
        feature_importance: Lista de importância das features.
        y_test: Valores reais do conjunto de teste.
        y_pred: Valores preditos pelo modelo.
        top_n: Número de features mais importantes a exibir.
    """
    print("=" * 60)
    print("RELATÓRIO DE AVALIAÇÃO DO MODELO")
    print("=" * 60)

    print("\n--- Métricas de Desempenho ---")
    for metric, value in metrics.items():
        print(f"  {metric:>12}: {value:.4f}")

    # Matriz de Confusão:
    # TN (True Negative):  corretamente previu "não churn"
    # FP (False Positive): previu "churn" mas era "não churn" (alarme falso)
    # FN (False Negative): previu "não churn" mas era "churn" (mais custoso)
    # TP (True Positive):  corretamente previu "churn"
    print("\n--- Matriz de Confusão ---")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  TN={cm[0][0]:>5}  FP={cm[0][1]:>5}")
    print(f"  FN={cm[1][0]:>5}  TP={cm[1][1]:>5}")

    print(f"\n--- Top {top_n} Features Mais Importantes ---")
    for i, feat in enumerate(feature_importance[:top_n], 1):
        print(f"  {i:>2}. {feat['feature']:<30} {feat['importance']:.6f}")

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=["Não Churn", "Churn"]))
    print("=" * 60)
