"""Common classification metrics for CyberGuard ML evaluation."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_probability: np.ndarray,
) -> dict[str, float]:
    """Calculate standard binary classification metrics."""

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    total_negatives = tn + fp
    total_positives = tp + fn

    false_positive_rate = (
        float(fp / total_negatives)
        if total_negatives
        else 0.0
    )

    false_negative_rate = (
        float(fn / total_positives)
        if total_positives
        else 0.0
    )

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(
            precision_score(y_true, y_pred, zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, y_pred, zero_division=0)
        ),
        "f1": float(
            f1_score(y_true, y_pred, zero_division=0)
        ),
        "roc_auc": float(
            roc_auc_score(y_true, y_probability)
        ),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "false_positive_rate": false_positive_rate,
        "false_negative_rate": false_negative_rate,
    }
