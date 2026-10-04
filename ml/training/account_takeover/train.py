"""
CyberGuard — Account Takeover Model Training

Training principles:
- Train/validation/test remain strictly separated.
- Validation data is used for early stopping and threshold selection.
- Test data is used only for final evaluation.
- Conservative XGBoost regularization is used to reduce overfitting.
- Class imbalance is handled with scale_pos_weight.
- Training and validation metrics are compared explicitly.
- PR-AUC is emphasized because ATO data is highly imbalanced.
- Operating threshold is selected using validation data only.
- No test data is used for training or model selection.
- Feature importance is recorded for model analysis.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
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

from ml.training.account_takeover.hyperparameters import (
    MODEL_NAME,
    MODEL_VERSION,
    XGBOOST_PARAMS,
)


# -------------------------------------------------------------------
# Paths and configuration
# -------------------------------------------------------------------

FEATURE_DIR = Path(
    "ml/datasets/account_takeover/processed/features"
)

MODEL_DIR = Path(
    "ml/models/trained/account_takeover"
)

METADATA_DIR = Path(
    "ml/models/metadata"
)

TARGET_COLUMN = "target"

EARLY_STOPPING_ROUNDS = 30

# Warning thresholds.
# These are diagnostic thresholds, not automatic proof of overfitting.
OVERFITTING_F1_GAP_WARNING = 0.10
OVERFITTING_PR_AUC_GAP_WARNING = 0.10

# Candidate operating thresholds.
# These are evaluated on validation data only.
THRESHOLD_CANDIDATES = [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
]


# -------------------------------------------------------------------
# Dataset loading
# -------------------------------------------------------------------

def load_split(
    split_name: str,
) -> tuple[pd.DataFrame, pd.Series]:
    """Load one preprocessed dataset split."""

    path = FEATURE_DIR / f"{split_name}.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset split not found: {path}"
        )

    df = pd.read_csv(path)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Missing target column: {TARGET_COLUMN}"
        )

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN].astype(int)

    if X.empty:
        raise ValueError(
            f"No model features found in {path}"
        )

    if X.isnull().any().any():
        raise ValueError(
            f"Missing values found in {path}"
        )

    if y.nunique() < 2:
        raise ValueError(
            f"Split {split_name} contains only one class."
        )

    return X, y


# -------------------------------------------------------------------
# Metrics
# -------------------------------------------------------------------

def calculate_metrics(
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> dict:
    """Calculate classification metrics."""

    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "threshold must be between 0 and 1."
        )

    predictions = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "threshold": float(threshold),

        "accuracy": float(
            accuracy_score(
                y_true,
                predictions,
            )
        ),

        "precision": float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        "recall": float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        "f1": float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        "roc_auc": float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),

        "pr_auc": float(
            average_precision_score(
                y_true,
                probabilities,
            )
        ),

        "confusion_matrix": [
            [int(tn), int(fp)],
            [int(fn), int(tp)],
        ],

        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),

        "false_positive_rate": float(
            fp / (fp + tn)
            if (fp + tn)
            else 0.0
        ),

        "false_negative_rate": float(
            fn / (fn + tp)
            if (fn + tp)
            else 0.0
        ),
    }


# -------------------------------------------------------------------
# Validation threshold selection
# -------------------------------------------------------------------

def select_validation_threshold(
    y_validation: pd.Series,
    validation_probabilities: np.ndarray,
) -> tuple[float, list[dict]]:
    """
    Select an operating threshold using validation data only.

    Selection priority:
    1. Highest validation F1.
    2. If F1 ties, higher recall.
    3. If recall also ties, higher precision.

    The test set is never used for threshold selection.
    """

    results: list[dict] = []

    for threshold in THRESHOLD_CANDIDATES:
        metrics = calculate_metrics(
            y_validation,
            validation_probabilities,
            threshold=threshold,
        )

        results.append(metrics)

    best = max(
        results,
        key=lambda item: (
            item["f1"],
            item["recall"],
            item["precision"],
        ),
    )

    return (
        float(best["threshold"]),
        results,
    )


# -------------------------------------------------------------------
# Feature importance
# -------------------------------------------------------------------

def calculate_feature_importance(
    model: XGBClassifier,
    feature_names: list[str],
) -> pd.DataFrame:
    """
    Calculate XGBoost gain-based feature importance.

    XGBoost's feature_importances_ represents the importance
    values associated with the trained tree ensemble.
    """

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": model.feature_importances_,
        }
    )

    importance = importance.sort_values(
        "importance",
        ascending=False,
    ).reset_index(drop=True)

    return importance


# -------------------------------------------------------------------
# Main training pipeline
# -------------------------------------------------------------------

def main() -> None:
    """Train and evaluate the ATO model."""

    print("=" * 70)
    print(
        "CYBERGUARD — ACCOUNT TAKEOVER MODEL TRAINING"
    )
    print("=" * 70)

    # ---------------------------------------------------------------
    # 1. Load datasets
    # ---------------------------------------------------------------

    X_train, y_train = load_split("train")

    X_validation, y_validation = load_split(
        "validation"
    )

    X_test, y_test = load_split("test")

    # ---------------------------------------------------------------
    # 2. Verify feature schemas
    # ---------------------------------------------------------------

    if list(X_train.columns) != list(
        X_validation.columns
    ):
        raise ValueError(
            "Train and validation feature schemas differ."
        )

    if list(X_train.columns) != list(
        X_test.columns
    ):
        raise ValueError(
            "Train and test feature schemas differ."
        )

    print()
    print("Dataset sizes:")
    print(
        f"  Train:      {len(X_train):,}"
    )
    print(
        f"  Validation: {len(X_validation):,}"
    )
    print(
        f"  Test:       {len(X_test):,}"
    )

    print()
    print(
        f"Number of features: "
        f"{X_train.shape[1]}"
    )

    # ---------------------------------------------------------------
    # 3. Calculate class weighting
    # ---------------------------------------------------------------

    positive_count = int(
        y_train.sum()
    )

    negative_count = int(
        len(y_train) - positive_count
    )

    if positive_count == 0:
        raise ValueError(
            "Training data contains no ATO-positive samples."
        )

    scale_pos_weight = (
        negative_count / positive_count
    )

    print()
    print("Class distribution:")
    print(
        f"  Positive ATO:    "
        f"{positive_count:,}"
    )
    print(
        f"  Negative benign: "
        f"{negative_count:,}"
    )
    print(
        f"  scale_pos_weight: "
        f"{scale_pos_weight:.4f}"
    )

    # ---------------------------------------------------------------
    # 4. Prepare model parameters
    # ---------------------------------------------------------------

    params = dict(XGBOOST_PARAMS)

    params["scale_pos_weight"] = (
        scale_pos_weight
    )

    model = XGBClassifier(
        **params,
        early_stopping_rounds=EARLY_STOPPING_ROUNDS,
    )

    print()
    print("Model configuration:")
    print(
        f"  max_depth: "
        f"{params['max_depth']}"
    )
    print(
        f"  learning_rate: "
        f"{params['learning_rate']}"
    )
    print(
        f"  n_estimators: "
        f"{params['n_estimators']}"
    )
    print(
        f"  subsample: "
        f"{params['subsample']}"
    )
    print(
        f"  colsample_bytree: "
        f"{params['colsample_bytree']}"
    )
    print(
        f"  min_child_weight: "
        f"{params['min_child_weight']}"
    )
    print(
        f"  gamma: "
        f"{params['gamma']}"
    )
    print(
        f"  reg_alpha: "
        f"{params['reg_alpha']}"
    )
    print(
        f"  reg_lambda: "
        f"{params['reg_lambda']}"
    )
    print(
        f"  early_stopping_rounds: "
        f"{EARLY_STOPPING_ROUNDS}"
    )

    # ---------------------------------------------------------------
    # 5. Train
    # ---------------------------------------------------------------

    print()
    print("Training model...")
    print(
        "Validation set is used for early stopping."
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[
            (
                X_validation,
                y_validation,
            )
        ],
        verbose=False,
    )

    booster = model.get_booster()

    trees_used = (
        booster.num_boosted_rounds()
    )

    best_iteration = getattr(
        model,
        "best_iteration",
        None,
    )

    best_score = getattr(
        model,
        "best_score",
        None,
    )

    print()
    print(
        f"Trees used: {trees_used}"
    )

    if best_iteration is not None:
        print(
            f"Best iteration: "
            f"{best_iteration}"
        )

    if best_score is not None:
        print(
            f"Best validation score "
            f"(logloss): {best_score:.6f}"
        )

    # ---------------------------------------------------------------
    # 6. Generate probabilities
    # ---------------------------------------------------------------

    train_probabilities = (
        model.predict_proba(X_train)[:, 1]
    )

    validation_probabilities = (
        model.predict_proba(X_validation)[:, 1]
    )

    # Test probabilities are generated only after
    # training is complete and before final evaluation.
    # They are NOT used for threshold selection.
    test_probabilities = (
        model.predict_proba(X_test)[:, 1]
    )

    # ---------------------------------------------------------------
    # 7. Select operating threshold using validation only
    # ---------------------------------------------------------------

    selected_threshold, threshold_results = (
        select_validation_threshold(
            y_validation,
            validation_probabilities,
        )
    )

    print()
    print("=" * 70)
    print(
        "VALIDATION THRESHOLD ANALYSIS"
    )
    print("=" * 70)

    print(
        "Threshold | Precision | Recall | F1 | PR-AUC"
    )
    print("-" * 70)

    for result in threshold_results:
        print(
            f"{result['threshold']:9.2f} | "
            f"{result['precision']:9.4f} | "
            f"{result['recall']:6.4f} | "
            f"{result['f1']:6.4f} | "
            f"{result['pr_auc']:7.4f}"
        )

    print()
    print(
        f"Selected validation threshold: "
        f"{selected_threshold:.2f}"
    )

    # ---------------------------------------------------------------
    # 8. Calculate metrics at selected threshold
    # ---------------------------------------------------------------

    train_metrics = calculate_metrics(
        y_train,
        train_probabilities,
        threshold=selected_threshold,
    )

    validation_metrics = calculate_metrics(
        y_validation,
        validation_probabilities,
        threshold=selected_threshold,
    )

    test_metrics = calculate_metrics(
        y_test,
        test_probabilities,
        threshold=selected_threshold,
    )

    metric_names = (
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "pr_auc",
        "false_positive_rate",
        "false_negative_rate",
    )

    # ---------------------------------------------------------------
    # 9. Print train metrics
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("TRAIN METRICS")
    print("=" * 70)

    for key in metric_names:
        print(
            f"{key}: "
            f"{train_metrics[key]:.6f}"
        )

    # ---------------------------------------------------------------
    # 10. Print validation metrics
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("VALIDATION METRICS")
    print("=" * 70)

    for key in metric_names:
        print(
            f"{key}: "
            f"{validation_metrics[key]:.6f}"
        )

    # ---------------------------------------------------------------
    # 11. Print test metrics
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("TEST METRICS")
    print("=" * 70)

    for key in metric_names:
        print(
            f"{key}: "
            f"{test_metrics[key]:.6f}"
        )

    print()
    print(
        "Test confusion matrix:"
    )
    print(
        np.array(
            test_metrics[
                "confusion_matrix"
            ]
        )
    )

    # ---------------------------------------------------------------
    # 12. Feature importance
    # ---------------------------------------------------------------

    feature_importance = (
        calculate_feature_importance(
            model,
            list(X_train.columns),
        )
    )

    print()
    print("=" * 70)
    print("FEATURE IMPORTANCE")
    print("=" * 70)

    for _, row in feature_importance.iterrows():
        print(
            f"{row['feature']}: "
            f"{row['importance']:.6f}"
        )

    # ---------------------------------------------------------------
    # 13. Overfitting check
    # ---------------------------------------------------------------

    train_f1 = train_metrics["f1"]

    validation_f1 = (
        validation_metrics["f1"]
    )

    train_pr_auc = (
        train_metrics["pr_auc"]
    )

    validation_pr_auc = (
        validation_metrics["pr_auc"]
    )

    f1_gap = (
        train_f1 - validation_f1
    )

    pr_auc_gap = (
        train_pr_auc - validation_pr_auc
    )

    print()
    print("=" * 70)
    print("OVERFITTING CHECK")
    print("=" * 70)

    print(
        f"Train F1:          "
        f"{train_f1:.6f}"
    )

    print(
        f"Validation F1:     "
        f"{validation_f1:.6f}"
    )

    print(
        f"F1 gap:             "
        f"{f1_gap:.6f}"
    )

    print(
        f"Train PR-AUC:      "
        f"{train_pr_auc:.6f}"
    )

    print(
        f"Validation PR-AUC: "
        f"{validation_pr_auc:.6f}"
    )

    print(
        f"PR-AUC gap:         "
        f"{pr_auc_gap:.6f}"
    )

    f1_overfit_warning = (
        f1_gap >
        OVERFITTING_F1_GAP_WARNING
    )

    pr_auc_overfit_warning = (
        pr_auc_gap >
        OVERFITTING_PR_AUC_GAP_WARNING
    )

    if f1_overfit_warning:
        print(
            "WARNING: Large train/validation "
            "F1 gap detected."
        )
    else:
        print(
            "F1 gap: acceptable."
        )

    if pr_auc_overfit_warning:
        print(
            "WARNING: Large train/validation "
            "PR-AUC gap detected."
        )
    else:
        print(
            "PR-AUC gap: acceptable."
        )

    overfitting_warning = (
        f1_overfit_warning
        or pr_auc_overfit_warning
    )

    if overfitting_warning:
        print()
        print(
            "OVERFITTING STATUS: WARNING"
        )
        print(
            "Do not treat this model as "
            "production-ready without further "
            "regularization/generalization work."
        )
    else:
        print()
        print(
            "OVERFITTING STATUS: "
            "NO LARGE GAP DETECTED"
        )

    # ---------------------------------------------------------------
    # 14. Save model and metadata
    # ---------------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    METADATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
        MODEL_DIR
        / f"{MODEL_VERSION}.joblib"
    )

    joblib.dump(
        model,
        model_path,
    )

    # Save feature importance separately.
    feature_importance_path = (
        MODEL_DIR
        / f"{MODEL_VERSION}-feature-importance.csv"
    )

    feature_importance.to_csv(
        feature_importance_path,
        index=False,
    )

    # ---------------------------------------------------------------
    # 15. Build metadata
    # ---------------------------------------------------------------

    metadata = {
        "model_name": MODEL_NAME,

        "model_version": MODEL_VERSION,

        "task": (
            "binary account takeover detection"
        ),

        "features": list(
            X_train.columns
        ),

        "train_samples": int(
            len(X_train)
        ),

        "validation_samples": int(
            len(X_validation)
        ),

        "test_samples": int(
            len(X_test)
        ),

        "positive_train": (
            positive_count
        ),

        "negative_train": (
            negative_count
        ),

        "scale_pos_weight": float(
            scale_pos_weight
        ),

        "hyperparameters": params,

        "early_stopping_rounds": (
            EARLY_STOPPING_ROUNDS
        ),

        "trees_used": int(
            trees_used
        ),

        "best_iteration": (
            int(best_iteration)
            if best_iteration is not None
            else None
        ),

        "best_validation_logloss": (
            float(best_score)
            if best_score is not None
            else None
        ),

        "operating_threshold": {
            "selected_from": "validation",
            "selection_metric": "f1",
            "tie_breakers": [
                "recall",
                "precision",
            ],
            "candidate_thresholds": (
                THRESHOLD_CANDIDATES
            ),
            "selected_threshold": float(
                selected_threshold
            ),
            "validation_results": (
                threshold_results
            ),
        },

        "metrics": {
            "train": train_metrics,
            "validation": validation_metrics,
            "test": test_metrics,
        },

        "feature_importance": (
            feature_importance.to_dict(
                orient="records"
            )
        ),

        "overfitting_check": {
            "train_f1": float(
                train_f1
            ),

            "validation_f1": float(
                validation_f1
            ),

            "f1_gap": float(
                f1_gap
            ),

            "train_pr_auc": float(
                train_pr_auc
            ),

            "validation_pr_auc": float(
                validation_pr_auc
            ),

            "pr_auc_gap": float(
                pr_auc_gap
            ),

            "f1_warning_threshold": (
                OVERFITTING_F1_GAP_WARNING
            ),

            "pr_auc_warning_threshold": (
                OVERFITTING_PR_AUC_GAP_WARNING
            ),

            "warning": bool(
                overfitting_warning
            ),
        },

        "evaluation_policy": {
            "test_used_for_final_evaluation_only": True,
            "test_used_for_training": False,
            "test_used_for_model_selection": False,
            "test_used_for_threshold_selection": False,
        },
    }

    metadata_path = (
        METADATA_DIR
        / f"{MODEL_VERSION}.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    # ---------------------------------------------------------------
    # 16. Final output
    # ---------------------------------------------------------------

    print()
    print(
        f"Model saved: {model_path}"
    )

    print(
        f"Feature importance saved: "
        f"{feature_importance_path}"
    )

    print(
        f"Metadata saved: {metadata_path}"
    )

    print()
    print("=" * 70)
    print(
        "ATO MODEL TRAINING COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()