"""
CyberGuard — Account Takeover Error Analysis

Analyzes the held-out ATO test set using the already-trained model.

Important:
- Does NOT retrain the model.
- Does NOT modify the test set.
- Does NOT use test data for model selection.
- Reports false positives and false negatives.
- Helps identify which features distinguish errors.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix

from ml.preprocessing.account_takeover.feature_extractor import (
    FEATURE_COLUMNS,
)


TEST_FEATURES_PATH = Path(
    "ml/datasets/account_takeover/processed/features/test.csv"
)

MODEL_PATH = Path(
    "ml/models/trained/account_takeover/"
    "account-takeover-xgboost-v1.joblib"
)

OUTPUT_PATH = Path(
    "ml/models/metadata/account-takeover-error-analysis.json"
)

TARGET_COLUMN = "target"

DEFAULT_THRESHOLD = 0.50


def main() -> None:
    print("=" * 70)
    print("CYBERGUARD — ATO ERROR ANALYSIS")
    print("=" * 70)

    if not TEST_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Test features not found: {TEST_FEATURES_PATH}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    print()
    print("Loading test features...")

    test_df = pd.read_csv(
        TEST_FEATURES_PATH
    )

    print(
        f"Test samples: {len(test_df):,}"
    )

    if TARGET_COLUMN not in test_df.columns:
        raise ValueError(
            f"Missing target column: {TARGET_COLUMN}"
        )

    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in test_df.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing model features: "
            + ", ".join(missing_features)
        )

    X_test = test_df[FEATURE_COLUMNS]

    y_test = (
        test_df[TARGET_COLUMN]
        .astype(int)
    )

    print()
    print("Loading trained model...")

    model = joblib.load(
        MODEL_PATH
    )

    probabilities = (
        model.predict_proba(X_test)[:, 1]
    )

    predictions = (
        probabilities >= DEFAULT_THRESHOLD
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    ).ravel()

    # ---------------------------------------------------------------
    # Confusion matrix
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("CONFUSION MATRIX")
    print("=" * 70)

    print()
    print(f"True negatives : {tn:,}")
    print(f"False positives: {fp:,}")
    print(f"False negatives: {fn:,}")
    print(f"True positives : {tp:,}")

    # ---------------------------------------------------------------
    # Attach predictions
    # ---------------------------------------------------------------

    analysis_df = test_df.copy()

    analysis_df["prediction_probability"] = (
        probabilities
    )

    analysis_df["prediction"] = (
        predictions
    )

    analysis_df["error_type"] = "correct"

    analysis_df.loc[
        (y_test == 1) & (predictions == 0),
        "error_type",
    ] = "false_negative"

    analysis_df.loc[
        (y_test == 0) & (predictions == 1),
        "error_type",
    ] = "false_positive"

    # ---------------------------------------------------------------
    # False negatives
    # ---------------------------------------------------------------

    false_negatives = analysis_df[
        analysis_df["error_type"]
        == "false_negative"
    ].copy()

    false_negatives = false_negatives.sort_values(
        "prediction_probability"
    )

    print()
    print("=" * 70)
    print("FALSE NEGATIVES — MISSED ATO EVENTS")
    print("=" * 70)

    print()
    print(
        f"Missed ATO events: "
        f"{len(false_negatives):,}"
    )

    if not false_negatives.empty:
        print()

        print(
            false_negatives[
                FEATURE_COLUMNS
                + ["prediction_probability"]
            ].to_string(
                index=False
            )
        )

    # ---------------------------------------------------------------
    # False positives
    # ---------------------------------------------------------------

    false_positives = analysis_df[
        analysis_df["error_type"]
        == "false_positive"
    ].copy()

    false_positives = false_positives.sort_values(
        "prediction_probability",
        ascending=False,
    )

    print()
    print("=" * 70)
    print("FALSE POSITIVES — FALSE ATO ALERTS")
    print("=" * 70)

    print()
    print(
        f"False positive events: "
        f"{len(false_positives):,}"
    )

    if not false_positives.empty:
        print()

        print(
            false_positives[
                FEATURE_COLUMNS
                + ["prediction_probability"]
            ]
            .head(20)
            .to_string(
                index=False
            )
        )

        if len(false_positives) > 20:
            print()
            print(
                "Only the top 20 false positives "
                "are displayed."
            )

    # ---------------------------------------------------------------
    # Probability distribution
    # ---------------------------------------------------------------

    positive_probabilities = (
        probabilities[
            y_test.to_numpy() == 1
        ]
    )

    negative_probabilities = (
        probabilities[
            y_test.to_numpy() == 0
        ]
    )

    print()
    print("=" * 70)
    print("PREDICTION PROBABILITY DISTRIBUTION")
    print("=" * 70)

    print()
    print("ATO events:")

    print(
        f"  Min : "
        f"{positive_probabilities.min():.6f}"
    )

    print(
        f"  Mean: "
        f"{positive_probabilities.mean():.6f}"
    )

    print(
        f"  Max : "
        f"{positive_probabilities.max():.6f}"
    )

    print()
    print("Benign events:")

    print(
        f"  Min : "
        f"{negative_probabilities.min():.6f}"
    )

    print(
        f"  Mean: "
        f"{negative_probabilities.mean():.6f}"
    )

    print(
        f"  Max : "
        f"{negative_probabilities.max():.6f}"
    )

    # ---------------------------------------------------------------
    # Feature means by error type
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("FEATURE MEANS BY GROUP")
    print("=" * 70)

    group_means = (
        analysis_df
        .groupby("error_type")[FEATURE_COLUMNS]
        .mean()
    )

    print()

    print(
        group_means.to_string()
    )

    # ---------------------------------------------------------------
    # Save diagnostic report
    # ---------------------------------------------------------------

    report = {
        "model": str(MODEL_PATH),
        "test_features": str(
            TEST_FEATURES_PATH
        ),
        "threshold": DEFAULT_THRESHOLD,
        "test_samples": int(
            len(test_df)
        ),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "ato_probability": {
            "min": float(
                positive_probabilities.min()
            ),
            "mean": float(
                positive_probabilities.mean()
            ),
            "max": float(
                positive_probabilities.max()
            ),
        },
        "benign_probability": {
            "min": float(
                negative_probabilities.min()
            ),
            "mean": float(
                negative_probabilities.mean()
            ),
            "max": float(
                negative_probabilities.max()
            ),
        },
        "feature_means_by_group": (
            group_means.to_dict()
        ),
        "false_negative_count": int(
            len(false_negatives)
        ),
        "false_positive_count": int(
            len(false_positives)
        ),
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("ERROR ANALYSIS COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Diagnostic report saved: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()