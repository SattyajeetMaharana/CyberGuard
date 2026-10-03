"""
CyberGuard malicious URL model training.

Trains an XGBoost binary classifier using the canonical URL-only
feature representation produced by the preprocessing pipeline.

Label mapping:
    0 -> malicious
    1 -> benign
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier

from ml.preprocessing.malicious_url.feature_extractor import URL_FEATURES


RANDOM_STATE = 42


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_split(path: Path, target_column: str) -> tuple[pd.DataFrame, pd.Series]:
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
        raise ValueError(f"Invalid labels found in {path}: {invalid_labels}")

    return X, y


def evaluate_model(
    model: XGBClassifier,
    X: pd.DataFrame,
    y: pd.Series,
) -> dict[str, float]:
    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    return {
        "accuracy": float(accuracy_score(y, predictions)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, probabilities)),
    }


def main() -> None:
    root = project_root()
    config_path = root / "ml" / "configs" / "malicious_url" / "config.yaml"

    config = load_config(config_path)

    target_column = config["data"]["target_column"]

    train_path = root / config["data"]["train"]
    validation_path = root / config["data"]["validation"]
    test_path = root / config["data"]["test"]

    print("=" * 70)
    print("CYBERGUARD - MALICIOUS URL MODEL TRAINING")
    print("=" * 70)

    print("\nLoading datasets...")
    X_train, y_train = load_split(train_path, target_column)
    X_validation, y_validation = load_split(validation_path, target_column)
    X_test, y_test = load_split(test_path, target_column)

    print(f"Training samples:   {len(X_train):,}")
    print(f"Validation samples: {len(X_validation):,}")
    print(f"Test samples:       {len(X_test):,}")
    print(f"Features:           {len(URL_FEATURES)}")
    print(f"Feature columns:    {URL_FEATURES}")

    model_config = config["model"]

    model = XGBClassifier(
        objective=model_config["objective"],
        eval_metric=model_config["eval_metric"],
        n_estimators=model_config["n_estimators"],
        max_depth=model_config["max_depth"],
        learning_rate=model_config["learning_rate"],
        subsample=model_config["subsample"],
        colsample_bytree=model_config["colsample_bytree"],
        random_state=model_config["random_state"],
        n_jobs=model_config["n_jobs"],
        tree_method=model_config["tree_method"],
    )

    print("\nTraining XGBoost model...")
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_validation, y_validation)],
        verbose=False,
    )

    print("Training completed.")

    print("\nEvaluating validation set...")
    validation_metrics = evaluate_model(
        model,
        X_validation,
        y_validation,
    )

    print("\nEvaluating test set...")
    test_metrics = evaluate_model(
        model,
        X_test,
        y_test,
    )

    print("\nValidation metrics:")
    for name, value in validation_metrics.items():
        print(f"  {name.upper():10s}: {value:.4f}")

    print("\nTest metrics:")
    for name, value in test_metrics.items():
        print(f"  {name.upper():10s}: {value:.4f}")

    model_path = root / config["output"]["model"]
    metadata_path = root / config["output"]["metadata"]

    model_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    model.save_model(model_path)

    metadata = {
        "model_name": "cyberguard-malicious-url-xgboost",
        "model_type": "XGBClassifier",
        "model_version": "malicious-url-xgboost-v1",
        "dataset": "PhiUSIIL",
        "feature_version": "malicious-url-url-only-v1",
        "features": URL_FEATURES,
        "label_mapping": {
            "0": "malicious",
            "1": "benign",
        },
        "random_state": RANDOM_STATE,
        "model_parameters": model.get_params(),
        "dataset_sizes": {
            "train": len(X_train),
            "validation": len(X_validation),
            "test": len(X_test),
        },
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "model_path": str(model_path.relative_to(root)),
    }

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print("\nArtifacts saved:")
    print(f"  Model:    {model_path}")
    print(f"  Metadata: {metadata_path}")
    print("\nTraining pipeline completed successfully.")


if __name__ == "__main__":
    main()
