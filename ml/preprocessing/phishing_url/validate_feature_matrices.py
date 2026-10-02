from pathlib import Path

import numpy as np
import pandas as pd

from ml.preprocessing.phishing_url.url_features import FEATURE_NAMES


BASE_DIR = Path("ml/datasets/phishing_url")
FEATURE_DIR = BASE_DIR / "processed" / "features"


FILES = {
    "train": FEATURE_DIR / "train_features.csv",
    "validation": FEATURE_DIR / "validation_features.csv",
    "test": FEATURE_DIR / "test_features.csv",
}


EXPECTED_COLUMNS = ["URL"] + FEATURE_NAMES + ["label"]


def validate_split(name: str, path: Path):
    print(f"\n{'=' * 70}")
    print(f"VALIDATING {name.upper()}")
    print(f"{'=' * 70}")

    df = pd.read_csv(path)

    print(f"File: {path}")
    print(f"Shape: {df.shape}")

    # ---------------------------------------------------------
    # 1. Column validation
    # ---------------------------------------------------------
    assert list(df.columns) == EXPECTED_COLUMNS, (
        f"Column mismatch in {name}"
    )

    print("✓ Columns: correct")

    # ---------------------------------------------------------
    # 2. Row validation
    # ---------------------------------------------------------
    assert len(df) > 0

    print("✓ Rows: non-empty")

    # ---------------------------------------------------------
    # 3. Missing-value validation
    # ---------------------------------------------------------
    missing = df[FEATURE_NAMES].isna().sum().sum()

    print(f"Missing feature values: {missing}")

    assert missing == 0

    print("✓ Missing values: 0")

    # ---------------------------------------------------------
    # 4. Numeric validation
    # ---------------------------------------------------------
    non_numeric = []

    for feature in FEATURE_NAMES:
        if not pd.api.types.is_numeric_dtype(df[feature]):
            non_numeric.append(feature)

    assert not non_numeric, (
        f"Non-numeric features: {non_numeric}"
    )

    print("✓ Feature types: numeric")

    # ---------------------------------------------------------
    # 5. Infinite-value validation
    # ---------------------------------------------------------
    feature_values = df[FEATURE_NAMES].to_numpy(dtype=float)

    infinite_count = np.isinf(feature_values).sum()

    print(f"Infinite feature values: {infinite_count}")

    assert infinite_count == 0

    print("✓ Infinite values: 0")

    # ---------------------------------------------------------
    # 6. Label validation
    # ---------------------------------------------------------
    labels = set(df["label"].unique())

    print(f"Labels found: {sorted(labels)}")

    assert labels == {0, 1}

    print("✓ Labels: only 0 and 1")

    # ---------------------------------------------------------
    # 7. URL validation
    # ---------------------------------------------------------
    assert df["URL"].notna().all()

    print("✓ URLs: no missing values")

    # ---------------------------------------------------------
    # 8. Duplicate URL validation
    # ---------------------------------------------------------
    duplicate_urls = df["URL"].duplicated().sum()

    print(f"Duplicate URLs: {duplicate_urls}")

    assert duplicate_urls == 0

    print("✓ Duplicate URLs: 0")

    return df


def main():
    print("=" * 70)
    print("CYBERGUARD FEATURE MATRIX VALIDATION")
    print("=" * 70)

    datasets = {}

    for name, path in FILES.items():
        datasets[name] = validate_split(name, path)

    # ---------------------------------------------------------
    # Cross-split URL leakage check
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("CROSS-SPLIT URL LEAKAGE CHECK")
    print("=" * 70)

    train_urls = set(datasets["train"]["URL"])
    validation_urls = set(datasets["validation"]["URL"])
    test_urls = set(datasets["test"]["URL"])

    train_validation = train_urls & validation_urls
    train_test = train_urls & test_urls
    validation_test = validation_urls & test_urls

    print(f"Train ∩ Validation: {len(train_validation)}")
    print(f"Train ∩ Test:       {len(train_test)}")
    print(f"Validation ∩ Test:  {len(validation_test)}")

    assert len(train_validation) == 0
    assert len(train_test) == 0
    assert len(validation_test) == 0

    print("\n✓ No URL leakage between splits")

    # ---------------------------------------------------------
    # Feature schema consistency
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("FEATURE SCHEMA CHECK")
    print("=" * 70)

    train_features = datasets["train"][FEATURE_NAMES].columns.tolist()
    validation_features = datasets["validation"][FEATURE_NAMES].columns.tolist()
    test_features = datasets["test"][FEATURE_NAMES].columns.tolist()

    assert train_features == validation_features
    assert train_features == test_features

    print(f"Feature count: {len(FEATURE_NAMES)}")
    print("✓ Train/validation/test schemas identical")

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("VALIDATION SUCCESSFUL")
    print("=" * 70)

    print("\nAll checks passed:")
    print("✓ Columns")
    print("✓ Rows")
    print("✓ Missing values")
    print("✓ Numeric features")
    print("✓ Infinite values")
    print("✓ Labels")
    print("✓ URLs")
    print("✓ Duplicate URLs")
    print("✓ Cross-split leakage")
    print("✓ Feature schema")


if __name__ == "__main__":
    main()