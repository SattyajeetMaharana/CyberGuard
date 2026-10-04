from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd


ZIP_PATH = Path(
    "ml/datasets/account_takeover/raw/rba-dataset.zip"
)

CSV_NAME = "rba-dataset.csv"
CHUNK_SIZE = 250_000


def main() -> None:
    print("=" * 70)
    print("CYBERGUARD — RBA ACCOUNT TAKEOVER DATASET INSPECTION")
    print("=" * 70)

    with ZipFile(ZIP_PATH, "r") as archive:
        info = archive.getinfo(CSV_NAME)

        print(f"\nCSV: {CSV_NAME}")
        print(f"Compressed size: {info.compress_size / (1024**2):.2f} MB")
        print(f"Uncompressed size: {info.file_size / (1024**3):.2f} GB")

        with archive.open(CSV_NAME) as csv_file:
            chunks = pd.read_csv(
                csv_file,
                chunksize=CHUNK_SIZE,
                low_memory=False,
            )

            total_rows = 0
            target_counts = {False: 0, True: 0}

            unique_users = set()

            missing_counts = None
            duplicate_rows = 0

            min_timestamp = None
            max_timestamp = None

            categorical_values = {
                "Country": set(),
                "Region": set(),
                "City": set(),
                "ASN": set(),
                "Browser Name and Version": set(),
                "OS Name and Version": set(),
                "Device Type": set(),
            }

            attack_ip_counts = {
                False: {False: 0, True: 0},
                True: {False: 0, True: 0},
            }

            previous_chunk = None

            print("\nProcessing dataset in chunks...")

            for chunk_number, chunk in enumerate(chunks, start=1):
                rows = len(chunk)
                total_rows += rows

                # ------------------------------------------------------
                # Target distribution
                # ------------------------------------------------------
                target = chunk["Is Account Takeover"]

                counts = target.value_counts(dropna=False)

                for value, count in counts.items():
                    if pd.isna(value):
                        continue

                    bool_value = bool(value)
                    target_counts[bool_value] += int(count)

                # ------------------------------------------------------
                # User statistics
                # ------------------------------------------------------
                unique_users.update(
                    chunk["User ID"].dropna().unique().tolist()
                )

                # ------------------------------------------------------
                # Missing values
                # ------------------------------------------------------
                current_missing = chunk.isna().sum()

                if missing_counts is None:
                    missing_counts = current_missing
                else:
                    missing_counts += current_missing

                # ------------------------------------------------------
                # Duplicate rows
                # ------------------------------------------------------
                duplicate_rows += int(chunk.duplicated().sum())

                # ------------------------------------------------------
                # Temporal coverage
                # ------------------------------------------------------
                timestamps = pd.to_numeric(
                    chunk["Login Timestamp"],
                    errors="coerce",
                )

                chunk_min = timestamps.min()
                chunk_max = timestamps.max()

                if pd.notna(chunk_min):
                    if min_timestamp is None or chunk_min < min_timestamp:
                        min_timestamp = chunk_min

                if pd.notna(chunk_max):
                    if max_timestamp is None or chunk_max > max_timestamp:
                        max_timestamp = chunk_max

                # ------------------------------------------------------
                # Categorical cardinality
                # ------------------------------------------------------
                for column in categorical_values:
                    values = chunk[column].dropna().unique()
                    categorical_values[column].update(values.tolist())

                # ------------------------------------------------------
                # Is Attack IP × ATO relationship
                # ------------------------------------------------------
                attack_ip = chunk["Is Attack IP"]

                cross = pd.crosstab(
                    attack_ip,
                    target,
                )

                for attack_value in [False, True]:
                    for ato_value in [False, True]:
                        if (
                            attack_value in cross.index
                            and ato_value in cross.columns
                        ):
                            attack_ip_counts[attack_value][ato_value] += int(
                                cross.loc[attack_value, ato_value]
                            )

                if chunk_number % 10 == 0:
                    print(
                        f"  Processed ~{total_rows:,} rows..."
                    )

    print("\n" + "=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)

    print(f"\nTotal rows: {total_rows:,}")
    print(f"Unique users: {len(unique_users):,}")

    print("\nTarget distribution:")
    for label, count in target_counts.items():
        percentage = (
            count / total_rows * 100
            if total_rows
            else 0
        )

        print(
            f"  Is Account Takeover={label}: "
            f"{count:,} ({percentage:.4f}%)"
        )

    print("\nDuplicate rows within individual chunks:")
    print(f"  {duplicate_rows:,}")

    print("\nMissing values:")
    if missing_counts is not None:
        for column, count in missing_counts.items():
            if count > 0:
                percentage = count / total_rows * 100
                print(
                    f"  {column}: "
                    f"{count:,} ({percentage:.4f}%)"
                )

    print("\nCategorical cardinality:")
    for column, values in categorical_values.items():
        print(
            f"  {column}: {len(values):,} unique values"
        )

    print("\nIs Attack IP × Is Account Takeover:")
    print(
        "                  ATO=False       ATO=True"
    )

    print(
        f"Attack IP=False   "
        f"{attack_ip_counts[False][False]:>12,}   "
        f"{attack_ip_counts[False][True]:>12,}"
    )

    print(
        f"Attack IP=True    "
        f"{attack_ip_counts[True][False]:>12,}   "
        f"{attack_ip_counts[True][True]:>12,}"
    )

    print("\nTimestamp range:")

    if min_timestamp is not None and max_timestamp is not None:
        print(f"  Minimum raw timestamp: {int(min_timestamp)}")
        print(f"  Maximum raw timestamp: {int(max_timestamp)}")

        try:
            print(
                "  Minimum datetime:",
                pd.to_datetime(
                    min_timestamp,
                    unit="ms",
                    errors="coerce",
                ),
            )
            print(
                "  Maximum datetime:",
                pd.to_datetime(
                    max_timestamp,
                    unit="ms",
                    errors="coerce",
                ),
            )
        except Exception as exc:
            print(f"  Datetime conversion failed: {exc}")

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()