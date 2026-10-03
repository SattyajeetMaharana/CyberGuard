from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier

from ml.training.impersonation.hyperparameters import (
    MODEL_NAME,
    MODEL_VERSION,
    XGBOOST_PARAMS,
)


BASE_DIR = Path("ml/datasets/impersonation/processed")
MODEL_DIR = Path("ml/models/trained/impersonation")


FEATURES = [
    "urgency_level",
    "requests_wire_transfer",
    "requests_gift_cards",
    "requests_sensitive_data",
    "dkim_pass",
    "spf_pass",
    "dmarc_pass",
    "reply_to_mismatch",
    "is_end_of_month",
    "is_friday",
    "sent_outside_hours",
    "requested_amount_usd",
    "auth_failure",
    "partial_auth",
    "full_auth_bypass",
    "payroll_timing",
    "weekend_timing",
    "after_hours",
]

TARGET = "label"


def load_split(filename: str):
    df = pd.read_csv(BASE_DIR / filename)

    X = df[FEATURES]
    y = df[TARGET].astype(int)

    return X, y


def evaluate(model, X, y, split_name: str) -> dict:
    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    accuracy = accuracy_score(y, predictions)
    precision = precision_score(y, predictions, zero_division=0)
    recall = recall_score(y, predictions, zero_division=0)
    f1 = f1_score(y, predictions, zero_division=0)
    roc_auc = roc_auc_score(y, probabilities)
    pr_auc = average_precision_score(y, probabilities)

    matrix = confusion_matrix(y, predictions)

    print(f"\n=== {split_name.upper()} EVALUATION ===")
    print(f"Accuracy : {accuracy:.6f}")
    print(f"Precision: {precision:.6f}")
    print(f"Recall   : {recall:.6f}")
    print(f"F1       : {f1:.6f}")
    print(f"ROC-AUC  : {roc_auc:.6f}")
    print(f"PR-AUC   : {pr_auc:.6f}")

    print("\nConfusion Matrix:")
    print(matrix)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "confusion_matrix": matrix.tolist(),
    }


def main() -> None:
    print("=== CYBERGUARD IMPERSONATION MODEL TRAINING ===")

    X_train, y_train = load_split("train.csv")
    X_val, y_val = load_split("validation.csv")
    X_test, y_test = load_split("test.csv")

    print("\nDataset:")
    print("Train:", X_train.shape)
    print("Validation:", X_val.shape)
    print("Test:", X_test.shape)

    print("\nFeatures:", len(FEATURES))

    model = XGBClassifier(**XGBOOST_PARAMS)

    print("\nTraining XGBoost...")
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    print("Training complete.")

    validation_metrics = evaluate(
        model,
        X_val,
        y_val,
        "validation",
    )

    test_metrics = evaluate(
        model,
        X_test,
        y_test,
        "test",
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODEL_DIR / f"{MODEL_VERSION}.joblib"

    joblib.dump(model, model_path)

    print("\n=== MODEL SAVED ===")
    print(model_path)

    print("\n=== FEATURE IMPORTANCE ===")

    importances = pd.Series(
        model.feature_importances_,
        index=FEATURES,
    ).sort_values(ascending=False)

    for feature, importance in importances.items():
        print(f"{feature:30s} {importance:.6f}")

    print("\n=== TRAINING SUMMARY ===")
    print("Model:", MODEL_NAME)
    print("Version:", MODEL_VERSION)
    print("Validation metrics:", validation_metrics)
    print("Test metrics:", test_metrics)


if __name__ == "__main__":
    main()