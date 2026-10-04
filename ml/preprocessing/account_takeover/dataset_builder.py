"""
CyberGuard — Account Takeover Dataset Builder

Configuration and helpers for building leakage-safe RBA datasets.

The raw RBA ZIP is never modified or extracted permanently.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


RBA_ZIP_PATH = Path(
    "ml/datasets/account_takeover/raw/rba-dataset.zip"
)

RBA_CSV_NAME = "rba-dataset.csv"

OUTPUT_DIR = Path(
    "ml/datasets/account_takeover/processed"
)

RANDOM_STATE = 42

# Keep all positive ATO events.
# The negative class will be sampled after splitting.
NEGATIVE_TO_POSITIVE_RATIO = 20

CHUNK_SIZE = 250_000


# Raw columns required to construct the model features.
RAW_FEATURE_COLUMNS = [
    "Login Timestamp",
    "User ID",
    "Country",
    "Region",
    "City",
    "ASN",
    "Browser Name and Version",
    "OS Name and Version",
    "Device Type",
    "Login Successful",
]

TARGET_COLUMN = "Is Account Takeover"

# Explicitly excluded from model inputs.
EXCLUDED_COLUMNS = [
    "index",
    "IP Address",
    "User Agent String",
    "Is Attack IP",
    "Is Account Takeover",
]


@dataclass(frozen=True)
class DatasetBuilderConfig:
    """Immutable configuration for the ATO dataset builder."""

    zip_path: Path = RBA_ZIP_PATH
    csv_name: str = RBA_CSV_NAME
    output_dir: Path = OUTPUT_DIR
    chunk_size: int = CHUNK_SIZE
    negative_to_positive_ratio: int = NEGATIVE_TO_POSITIVE_RATIO
    random_state: int = RANDOM_STATE


def validate_config(config: DatasetBuilderConfig) -> None:
    """Validate dataset-builder configuration."""

    if not config.zip_path.exists():
        raise FileNotFoundError(
            f"RBA dataset not found: {config.zip_path}"
        )

    if config.chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero"
        )

    if config.negative_to_positive_ratio <= 0:
        raise ValueError(
            "negative_to_positive_ratio must be greater than zero"
        )

    if config.random_state < 0:
        raise ValueError(
            "random_state must be non-negative"
        )


def print_config(config: DatasetBuilderConfig) -> None:
    """Print the active dataset-builder configuration."""

    print("=" * 70)
    print("CYBERGUARD — ATO DATASET BUILDER CONFIGURATION")
    print("=" * 70)

    print(f"RBA ZIP: {config.zip_path}")
    print(f"CSV: {config.csv_name}")
    print(f"Output directory: {config.output_dir}")
    print(f"Chunk size: {config.chunk_size:,}")
    print(
        "Negative/positive ratio: "
        f"{config.negative_to_positive_ratio}:1"
    )
    print(f"Random state: {config.random_state}")

    print()
    print("Model input columns:")
    for column in RAW_FEATURE_COLUMNS:
        print(f"  - {column}")

    print()
    print("Excluded columns:")
    for column in EXCLUDED_COLUMNS:
        print(f"  - {column}")


if __name__ == "__main__":
    config = DatasetBuilderConfig()

    validate_config(config)
    print_config(config)

    print()
    print("CONFIGURATION VALID")