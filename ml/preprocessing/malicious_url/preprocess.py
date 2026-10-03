"""
Preprocessing pipeline for the CyberGuard malicious URL detector.

Source:
    PhiUSIIL Phishing URL Dataset

The raw dataset is never modified.

Pipeline:
    raw URL + label
        -> URL validation
        -> duplicate removal
        -> canonical 18 URL features
        -> stratified train/validation/test split
        -> processed CSV files
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from ml.preprocessing.malicious_url.feature_extractor import (
    URL_FEATURES,
    extract_url_features_dataframe,
)


RANDOM_STATE = 42

TRAIN_SIZE = 0.70
VALIDATION_SIZE = 0.15
TEST_SIZE = 0.15

LABEL_COLUMN = "label"
URL_COLUMN = "URL"


def load_raw_dataset(zip_path: Path) -> pd.DataFrame:
    """Load URL and label columns from the PhiUSIIL ZIP archive."""
    with zipfile.ZipFile(zip_path) as archive:
        csv_files = [
            name
            for name in archive.namelist()
            if name.lower().endswith(".csv")
        ]

        if len(csv_files) != 1:
            raise ValueError(
                f"Expected exactly one CSV file, found: {csv_files}"
            )

        with archive.open(csv_files[0]) as file:
            return pd.read_csv(
                file,
                usecols=[URL_COLUMN, LABEL_COLUMN],
            )


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Validate labels/URLs and remove duplicate URLs."""
    required_columns = {URL_COLUMN, LABEL_COLUMN}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    result = df.copy()

    result[URL_COLUMN] = result[URL_COLUMN].astype(str).str.strip()

    result = result[result[URL_COLUMN] != ""].copy()

    result = result.dropna(subset=[LABEL_COLUMN])

    result[LABEL_COLUMN] = result[LABEL_COLUMN].astype(int)

    invalid_labels = set(result[LABEL_COLUMN].unique()) - {0, 1}

    if invalid_labels:
        raise ValueError(
            f"Unexpected labels found: {sorted(invalid_labels)}"
        )

    conflicting_labels = (
        result.groupby(URL_COLUMN)[LABEL_COLUMN]
        .nunique()
        .gt(1)
        .sum()
    )

    if conflicting_labels:
        raise ValueError(
            f"Found {conflicting_labels} URLs with conflicting labels."
        )

    result = result.drop_duplicates(
        subset=[URL_COLUMN],
        keep="first",
    )

    return result.reset_index(drop=True)


def build_feature_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Convert URLs into the canonical 18-feature representation."""
    features = extract_url_features_dataframe(df[URL_COLUMN])

    features[LABEL_COLUMN] = df[LABEL_COLUMN].to_numpy()

    return features[
        URL_FEATURES + [LABEL_COLUMN]
    ]


def split_dataset(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create reproducible stratified train/validation/test splits."""
    train_df, temp_df = train_test_split(
        df,
        test_size=VALIDATION_SIZE + TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df[LABEL_COLUMN],
    )

    relative_test_size = TEST_SIZE / (
        VALIDATION_SIZE + TEST_SIZE
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=relative_test_size,
        random_state=RANDOM_STATE,
        stratify=temp_df[LABEL_COLUMN],
    )

    return (
        train_df.reset_index(drop=True),
        validation_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


def save_outputs(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
    output_dir: Path,
    metadata: dict,
) -> None:
    """Save processed datasets and preprocessing metadata."""
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_df.to_csv(
        output_dir / "train.csv",
        index=False,
    )

    validation_df.to_csv(
        output_dir / "validation.csv",
        index=False,
    )

    test_df.to_csv(
        output_dir / "test.csv",
        index=False,
    )

    with open(
        output_dir / "preprocessing_metadata.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
        )


def run_preprocessing(
    raw_zip_path: Path,
    output_dir: Path,
) -> None:
    """Run the complete preprocessing pipeline."""
    print("=" * 60)
    print("CYBERGUARD - MALICIOUS URL PREPROCESSING")
    print("=" * 60)

    print("\n[1/5] Loading raw dataset...")
    raw_df = load_raw_dataset(raw_zip_path)

    print(f"Raw rows: {len(raw_df):,}")

    print("\n[2/5] Cleaning dataset...")
    clean_df = clean_dataset(raw_df)

    print(f"Rows after cleaning: {len(clean_df):,}")
    print(
        "Label distribution:",
        clean_df[LABEL_COLUMN].value_counts().sort_index().to_dict(),
    )

    print("\n[3/5] Extracting canonical URL features...")
    feature_df = build_feature_dataset(clean_df)

    print(f"Feature matrix shape: {feature_df.shape}")
    print(f"Feature count: {len(URL_FEATURES)}")

    print("\n[4/5] Creating stratified splits...")
    train_df, validation_df, test_df = split_dataset(feature_df)

    print(f"Train rows:      {len(train_df):,}")
    print(f"Validation rows: {len(validation_df):,}")
    print(f"Test rows:       {len(test_df):,}")

    print("\n[5/5] Saving processed datasets...")

    metadata = {
        "dataset": "PhiUSIIL Phishing URL Dataset",
        "source_file": raw_zip_path.name,
        "url_column": URL_COLUMN,
        "label_column": LABEL_COLUMN,
        "label_mapping": {
            "0": "phishing_malicious",
            "1": "legitimate_benign",
        },
        "feature_count": len(URL_FEATURES),
        "features": URL_FEATURES,
        "random_state": RANDOM_STATE,
        "split_ratio": {
            "train": TRAIN_SIZE,
            "validation": VALIDATION_SIZE,
            "test": TEST_SIZE,
        },
        "raw_rows": len(raw_df),
        "clean_rows": len(clean_df),
        "train_rows": len(train_df),
        "validation_rows": len(validation_df),
        "test_rows": len(test_df),
    }

    save_outputs(
        train_df,
        validation_df,
        test_df,
        output_dir,
        metadata,
    )

    print("\nPreprocessing completed successfully.")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]

    raw_zip = (
        project_root
        / "ml"
        / "datasets"
        / "malicious_url"
        / "raw"
        / "PhiUSIIL_Phishing_URL_Dataset.zip"
    )

    processed_dir = (
        project_root
        / "ml"
        / "datasets"
        / "malicious_url"
        / "processed"
    )

    run_preprocessing(
        raw_zip_path=raw_zip,
        output_dir=processed_dir,
    )
