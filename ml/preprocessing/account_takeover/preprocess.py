"""
CyberGuard — Account Takeover Preprocessing

Preprocesses the sampled RBA train/validation/test datasets.

Important:
- Feature statistics are fitted ONLY on training data.
- Validation and test data reuse training statistics.
- User-history features are calculated independently per split.
- The target column is never used as a model feature.
- Training feature statistics are persisted for inference reuse.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ml.preprocessing.account_takeover.feature_extractor import (
    fit_feature_statistics,
    transform_features,
    get_feature_schema,
)


DATASET_DIR = Path(
    "ml/datasets/account_takeover/processed"
)

OUTPUT_DIR = Path(
    "ml/datasets/account_takeover/processed/features"
)

STATISTICS_PATH = (
    DATASET_DIR
    / "ato_feature_statistics.json"
)

SPLITS = (
    "train",
    "validation",
    "test",
)

TARGET_COLUMN = "Is Account Takeover"


def preprocess_datasets() -> None:
    """Preprocess all ATO dataset splits."""

    print("=" * 70)
    print("CYBERGUARD — ATO PREPROCESSING")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("Loading training data...")

    train = pd.read_csv(
        DATASET_DIR / "train.csv"
    )

    print(
        f"Training rows: {len(train):,}"
    )

    print()
    print("Fitting training-only feature statistics...")

    statistics = fit_feature_statistics(
        train
    )

    print("Training statistics fitted.")

    # Persist ONLY training-derived statistics.
    # These are reused during inference so the model sees
    # the same global frequency representation used during training.
    with STATISTICS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            statistics,
            file,
            indent=2,
            sort_keys=True,
        )

    print(
        f"Saved training statistics: "
        f"{STATISTICS_PATH}"
    )

    for split_name in SPLITS:

        print()
        print(
            f"Processing {split_name}..."
        )

        df = pd.read_csv(
            DATASET_DIR
            / f"{split_name}.csv"
        )

        features = transform_features(
            df,
            statistics,
        )

        target = (
            df[TARGET_COLUMN]
            .astype(bool)
            .astype(int)
        )

        output = features.copy()
        output["target"] = target.values

        output_path = (
            OUTPUT_DIR
            / f"{split_name}.csv"
        )

        output.to_csv(
            output_path,
            index=False,
        )

        print(
            f"Rows: {len(output):,}"
        )

        print(
            f"Features: {features.shape[1]}"
        )

        print(
            f"ATO positives: {int(target.sum()):,}"
        )

        print(
            f"Benign negatives: "
            f"{int((target == 0).sum()):,}"
        )

        print(
            f"Saved: {output_path}"
        )

    print()
    print(
        "Feature schema:"
    )

    for feature in get_feature_schema():
        print(
            f"  - {feature}"
        )

    print()
    print("=" * 70)
    print("ATO PREPROCESSING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    preprocess_datasets()