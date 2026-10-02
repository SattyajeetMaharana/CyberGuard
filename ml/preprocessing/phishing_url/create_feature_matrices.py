from pathlib import Path

import pandas as pd

from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    FEATURE_VERSION,
    extract_url_features,
)


BASE_DIR = Path("ml/datasets/phishing_url")
INPUT_DIR = BASE_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "processed/features"


def create_features(input_file: Path, output_file: Path) -> None:
    print(f"\nProcessing: {input_file}")

    df = pd.read_csv(input_file)

    if "URL" not in df.columns:
        raise ValueError(f"'URL' column missing in {input_file}")

    if "label" not in df.columns:
        raise ValueError(f"'label' column missing in {input_file}")

    print(f"Rows: {len(df)}")

    feature_rows = []

    for url in df["URL"]:
        features = extract_url_features(url)
        feature_rows.append(features)

    feature_df = pd.DataFrame(
        feature_rows,
        columns=FEATURE_NAMES,
    )

    # Keep the original label.
    feature_df["label"] = df["label"].to_numpy()

    # Keep URL separately for traceability/debugging.
    feature_df.insert(0, "URL", df["URL"].to_numpy())

    output_file.parent.mkdir(parents=True, exist_ok=True)

    feature_df.to_csv(output_file, index=False)

    print(f"Saved: {output_file}")
    print(f"Shape: {feature_df.shape}")

    print("\nLabel distribution:")
    print(feature_df["label"].value_counts().sort_index())

    print("\nFeature count:")
    print(len(FEATURE_NAMES))


def main():
    print("=" * 70)
    print("CYBERGUARD URL FEATURE MATRIX GENERATION")
    print("=" * 70)

    print(f"\nFeature version: {FEATURE_VERSION}")
    print(f"Feature count: {len(FEATURE_NAMES)}")

    splits = {
        "train": (
            INPUT_DIR / "train.csv",
            OUTPUT_DIR / "train_features.csv",
        ),
        "validation": (
            INPUT_DIR / "validation.csv",
            OUTPUT_DIR / "validation_features.csv",
        ),
        "test": (
            INPUT_DIR / "test.csv",
            OUTPUT_DIR / "test_features.csv",
        ),
    }

    for split_name, (input_file, output_file) in splits.items():
        print(f"\n{'=' * 70}")
        print(f"PROCESSING {split_name.upper()}")
        print(f"{'=' * 70}")

        create_features(input_file, output_file)

    print("\n" + "=" * 70)
    print("FEATURE MATRIX GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()