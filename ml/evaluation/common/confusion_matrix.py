"""Confusion matrix utilities for CyberGuard ML evaluation."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import confusion_matrix


def calculate_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict[str, int]:
    """Return a named binary confusion matrix."""

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    return {
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    }
