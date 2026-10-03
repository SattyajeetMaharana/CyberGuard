"""
CyberGuard malicious URL model evaluation.

Evaluates the trained XGBoost model on the held-out test set.
No training or parameter tuning is performed here.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

from ml.evaluation.common.confusion_matrix import calculate_confusion_matrix
from ml.evaluation.common.metrics import calculate_metrics
from ml.preprocessing.malicious_url.feature_extractor import URL_FEATURES


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_test_data(
    path: Path,
    target_column: str,
) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(path)

    expected_columns = URL_FEATURES + [target_column]

    if list(df.columns) != expected_columns:
        raise ValueError(
            f"Unexpected columns in {path}.\n"
            f"Expected: {expected_columns}\n"
            f"Found: {list(df.columns)}"
        )

    if df.isna().any().any():
        raise ValueError(f"Missing values detected in {path}.")

    X = df[URL_FEATURES].copy()
    y = df[target_column].astype(int).copy()

    invalid_labels = set(y.unique()) - {0, 1}
    if invalid_labels:
        raise ValueError(f"Invalid labels found: {invalid_labels}")

    return X, y


def main() -> None:
    root = project_root()

    config_path = root / "ml" / "configs" / "malicious_url" / "config.yaml"
    config = load_config(config_path)

    target_column = config["data"]["target_column"]

    test_path = root / config["data"]["test"]
    model_path = root / config["output"]["model"]

    report_path = (
        root
        / "ml"
        / "evaluation"
        / "malicious_url"
        / "evaluation_report.json"
    )

    print("=" * 70)
    print("CYBERGUARD - MALICIOUS URL MODEL EVALUATION")
    print("=" * 70)

    print("\nLoading test dataset...")
    X_test, y_test = load_test_data(test_path, target_column)

    print(f"Test samples: {len(X_test):,}")
    print(f"Features: {len(URL_FEATURES)}")

    print("\nLoading trained model...")
    model = XGBClassifier()
    model.load_model(model_path)

    print("Model loaded successfully.")

    print("\nGenerating predictions...")

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    metrics = calculate_metrics(
        y_test.to_numpy(),
        predictions,
        probabilities,
    )

    confusion = calculate_confusion_matrix(
        y_test.to_numpy(),
        predictions,
    )

    classification = classification_report(
        y_test,
        predictions,
        target_names=["malicious", "benign"],
        output_dict=True,
        zero_division=0,
    )

    importance = model.feature_importances_

    feature_importance = {
        feature: float(score)
        for feature, score in sorted(
            zip(URL_FEATURES, importance),
            key=lambda item: item[1],
            reverse=True,
        )
    }

    report = {
        "model": {
            "name": "cyberguard-malicious-url-xgboost",
            "version": "malicious-url-xgboost-v1",
            "model_path": str(model_path.relative_to(root)),
        },
        "dataset": {
            "name": "PhiUSIIL",
            "split": "test",
            "samples": len(X_test),
            "features": URL_FEATURES,
        },
        "label_mapping": {
            "0": "malicious",
            "1": "benign",
        },
        "threshold": 0.5,
        "metrics": metrics,
        "confusion_matrix": confusion,
        "classification_report": classification,
        "feature_importance": feature_importance,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\nTest metrics:")
    for name, value in metrics.items():
        if isinstance(value, float):
            print(f"  {name.upper():20s}: {value:.6f}")
        else:
            print(f"  {name.upper():20s}: {value}")

    print("\nFeature importance:")
    for feature, score in feature_importance.items():
        print(f"  {feature:30s}: {score:.6f}")

    print("\nEvaluation report saved:")
    print(f"  {report_path}")

    print("\nEvaluation completed successfully.")


if __name__ == "__main__":
    main()
