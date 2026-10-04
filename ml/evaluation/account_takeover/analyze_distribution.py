"""
CyberGuard — Account Takeover Distribution Analysis

Purpose:
- Compare train/validation/test feature distributions.
- Identify possible distribution shift.
- Identify features whose behavior differs strongly across splits.
- Do NOT retrain or modify the model.

This analysis is diagnostic only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


FEATURE_DIR = Path(
    "ml/datasets/account_takeover/processed/features"
)

TARGET_COLUMN = "target"

SPLITS = (
    "train",
    "validation",
    "test",
)


def load_split(
    split_name: str,
) -> pd.DataFrame:
    """Load one processed split."""

    path = FEATURE_DIR / f"{split_name}.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing split: {path}"
        )

    df = pd.read_csv(path)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Missing target column in {path}"
        )

    return df


def summarize_feature(
    feature: str,
    train: pd.Series,
    validation: pd.Series,
    test: pd.Series,
) -> dict:
    """Calculate distribution statistics."""

    result = {
        "feature": feature,

        "train_mean": float(train.mean()),
        "validation_mean": float(validation.mean()),
        "test_mean": float(test.mean()),

        "train_std": float(train.std()),
        "validation_std": float(validation.std()),
        "test_std": float(test.std()),

        "train_min": float(train.min()),
        "validation_min": float(validation.min()),
        "test_min": float(test.min()),

        "train_max": float(train.max()),
        "validation_max": float(validation.max()),
        "test_max": float(test.max()),
    }

    train_mean = result["train_mean"]

    if abs(train_mean) > 1e-9:
        result["validation_mean_relative_change"] = float(
            abs(
                result["validation_mean"]
                - train_mean
            )
            / abs(train_mean)
        )

        result["test_mean_relative_change"] = float(
            abs(
                result["test_mean"]
                - train_mean
            )
            / abs(train_mean)
        )
    else:
        result["validation_mean_relative_change"] = 0.0
        result["test_mean_relative_change"] = 0.0

    return result


def main() -> None:
    """Run train/validation/test distribution analysis."""

    print("=" * 70)
    print(
        "CYBERGUARD — ATO DISTRIBUTION SHIFT ANALYSIS"
    )
    print("=" * 70)

    train_df = load_split("train")
    validation_df = load_split("validation")
    test_df = load_split("test")

    train_X = train_df.drop(
        columns=[TARGET_COLUMN]
    )

    validation_X = validation_df.drop(
        columns=[TARGET_COLUMN]
    )

    test_X = test_df.drop(
        columns=[TARGET_COLUMN]
    )

    if list(train_X.columns) != list(
        validation_X.columns
    ):
        raise ValueError(
            "Train and validation schemas differ."
        )

    if list(train_X.columns) != list(
        test_X.columns
    ):
        raise ValueError(
            "Train and test schemas differ."
        )

    print()
    print("Dataset sizes:")
    print(
        f"  Train:      {len(train_df):,}"
    )
    print(
        f"  Validation: {len(validation_df):,}"
    )
    print(
        f"  Test:       {len(test_df):,}"
    )

    print()
    print("Class distributions:")

    for name, df in (
        ("Train", train_df),
        ("Validation", validation_df),
        ("Test", test_df),
    ):
        positives = int(
            df[TARGET_COLUMN].sum()
        )

        negatives = int(
            len(df) - positives
        )

        positive_rate = (
            positives / len(df)
        )

        print(
            f"  {name}: "
            f"positive={positives}, "
            f"negative={negatives}, "
            f"positive_rate={positive_rate:.6f}"
        )

    # ---------------------------------------------------------------
    # Feature distribution comparison
    # ---------------------------------------------------------------

    rows = []

    for feature in train_X.columns:

        row = summarize_feature(
            feature,
            train_X[feature],
            validation_X[feature],
            test_X[feature],
        )

        rows.append(row)

    summary = pd.DataFrame(rows)

    summary = summary.sort_values(
        "test_mean_relative_change",
        ascending=False,
    )

    print()
    print("=" * 70)
    print("FEATURE DISTRIBUTION SHIFT")
    print("=" * 70)

    for _, row in summary.iterrows():

        print()
        print(
            f"Feature: {row['feature']}"
        )

        print(
            f"  Train mean:      "
            f"{row['train_mean']:.6f}"
        )

        print(
            f"  Validation mean: "
            f"{row['validation_mean']:.6f}"
        )

        print(
            f"  Test mean:       "
            f"{row['test_mean']:.6f}"
        )

        print(
            f"  Train std:       "
            f"{row['train_std']:.6f}"
        )

        print(
            f"  Validation std:  "
            f"{row['validation_std']:.6f}"
        )

        print(
            f"  Test std:        "
            f"{row['test_std']:.6f}"
        )

        print(
            f"  Test mean relative "
            f"change: "
            f"{row['test_mean_relative_change']:.2%}"
        )

    # ---------------------------------------------------------------
    # Correlation with target
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("FEATURE / TARGET CORRELATION")
    print("=" * 70)

    train_correlations = (
        train_df.corr(numeric_only=True)[
            TARGET_COLUMN
        ]
        .drop(TARGET_COLUMN)
        .sort_values(
            key=lambda values: values.abs(),
            ascending=False,
        )
    )

    for feature, correlation in (
        train_correlations.items()
    ):
        print(
            f"{feature}: "
            f"{correlation:.6f}"
        )

    # ---------------------------------------------------------------
    # Save diagnostic report
    # ---------------------------------------------------------------

    output_path = Path(
        "ml/models/metadata/"
        "account-takeover-distribution-analysis.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "train_samples": int(
            len(train_df)
        ),
        "validation_samples": int(
            len(validation_df)
        ),
        "test_samples": int(
            len(test_df)
        ),
        "class_distribution": {
            "train": {
                "positive": int(
                    train_df[TARGET_COLUMN].sum()
                ),
                "negative": int(
                    len(train_df)
                    - train_df[TARGET_COLUMN].sum()
                ),
            },
            "validation": {
                "positive": int(
                    validation_df[TARGET_COLUMN].sum()
                ),
                "negative": int(
                    len(validation_df)
                    - validation_df[TARGET_COLUMN].sum()
                ),
            },
            "test": {
                "positive": int(
                    test_df[TARGET_COLUMN].sum()
                ),
                "negative": int(
                    len(test_df)
                    - test_df[TARGET_COLUMN].sum()
                ),
            },
        },
        "feature_distribution": summary.to_dict(
            orient="records"
        ),
        "train_target_correlations": {
            str(feature): float(value)
            for feature, value
            in train_correlations.items()
        },
    }

    output_path.write_text(
        pd.Series(report).to_json(
            indent=2
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"Diagnostic report saved: "
        f"{output_path}"
    )

    print()
    print("=" * 70)
    print(
        "DISTRIBUTION ANALYSIS COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()