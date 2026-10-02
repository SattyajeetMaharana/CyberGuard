from pathlib import Path
from datetime import datetime, timezone
import json

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    FEATURE_VERSION,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path("ml/datasets/phishing_url")
FEATURE_DIR = BASE_DIR / "processed" / "features"

MODEL_DIR = Path("ml/models/trained/phishing_url")

TRAIN_PATH = FEATURE_DIR / "train_features.csv"
VALIDATION_PATH = FEATURE_DIR / "validation_features.csv"
TEST_PATH = FEATURE_DIR / "test_features.csv"

MODEL_PATH = MODEL_DIR / "url_xgboost_v1.joblib"
METADATA_PATH = MODEL_DIR / "metadata.json"


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "cyberguard-url-xgboost"
MODEL_VERSION = "url-xgb-v1"

RANDOM_STATE = 42


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset(path: Path):
    print(f"\nLoading: {path}")

    df = pd.read_csv(path)

    X = df[FEATURE_NAMES]
    y = df["label"]

    print(f"Rows: {len(df)}")
    print(f"Features: {X.shape[1]}")

    return X, y


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(model, X, y, dataset_name: str):
    print("\n" + "=" * 70)
    print(f"EVALUATION: {dataset_name.upper()}")
    print("=" * 70)

    probabilities = model.predict_proba(X)[:, 1]

    predictions = (probabilities >= 0.5).astype(int)

    accuracy = accuracy_score(y, predictions)

    precision = precision_score(
        y,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y,
        probabilities,
    )

    matrix = confusion_matrix(
        y,
        predictions,
    )

    print(f"Accuracy:   {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(matrix)

    print("\nClassification Report:")
    print(
        classification_report(
            y,
            predictions,
            target_names=[
                "Phishing",
                "Legitimate",
            ],
            zero_division=0,
        )
    )

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "confusion_matrix": matrix.tolist(),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("CYBERGUARD URL XGBOOST TRAINING")
    print("=" * 70)

    print(f"\nModel: {MODEL_NAME}")
    print(f"Model version: {MODEL_VERSION}")
    print(f"Feature version: {FEATURE_VERSION}")
    print(f"Feature count: {len(FEATURE_NAMES)}")
    print(f"Random state: {RANDOM_STATE}")

    # --------------------------------------------------------
    # Create model directory
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    X_train, y_train = load_dataset(TRAIN_PATH)

    X_validation, y_validation = load_dataset(
        VALIDATION_PATH
    )

    X_test, y_test = load_dataset(TEST_PATH)

    # --------------------------------------------------------
    # Print label distributions
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LABEL DISTRIBUTIONS")
    print("=" * 70)

    print("\nTrain:")
    print(y_train.value_counts().sort_index())

    print("\nValidation:")
    print(y_validation.value_counts().sort_index())

    print("\nTest:")
    print(y_test.value_counts().sort_index())

    # --------------------------------------------------------
    # Create XGBoost model
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CREATING XGBOOST MODEL")
    print("=" * 70)

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method="hist",
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    print("\nStarting training...")

    model.fit(
        X_train,
        y_train,
        eval_set=[
            (X_train, y_train),
            (X_validation, y_validation),
        ],
        verbose=False,
    )

    print("Training complete.")

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    train_metrics = evaluate_model(
        model,
        X_train,
        y_train,
        "train",
    )

    validation_metrics = evaluate_model(
        model,
        X_validation,
        y_validation,
        "validation",
    )

    test_metrics = evaluate_model(
        model,
        X_test,
        y_test,
        "test",
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print("\n" + "=" * 70)
    print("MODEL SAVED")
    print("=" * 70)

    print(f"Model: {MODEL_PATH}")

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "feature_version": FEATURE_VERSION,
        "dataset": "PhiUSIIL Phishing URL Dataset",
        "dataset_source": "UCI Machine Learning Repository",
        "dataset_split": "70/15/15",
        "feature_count": len(FEATURE_NAMES),
        "features": FEATURE_NAMES,
        "target": "label",
        "label_mapping": {
            "0": "phishing",
            "1": "legitimate",
        },
        "random_state": RANDOM_STATE,
        "training_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "xgboost_parameters": {
            "n_estimators": 300,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "binary:logistic",
            "eval_metric": "logloss",
        },
        "metrics": {
            "train": train_metrics,
            "validation": validation_metrics,
            "test": test_metrics,
        },
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=4,
        )

    print(f"Metadata: {METADATA_PATH}")

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FEATURE IMPORTANCE")
    print("=" * 70)

    importance = pd.DataFrame(
        {
            "feature": FEATURE_NAMES,
            "importance": model.feature_importances_,
        }
    ).sort_values(
        "importance",
        ascending=False,
    )

    print(importance.to_string(index=False))

    print("\n" + "=" * 70)
    print("XGBOOST TRAINING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()