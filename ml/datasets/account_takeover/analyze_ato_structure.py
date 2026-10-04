"""
CyberGuard — RBA ATO Structure Analysis

Analyzes where the very rare ATO events occur by user and time.
This is used to design a leakage-resistant train/validation/test split.

The full CSV remains inside the ZIP archive and is processed in chunks.
"""

from __future__ import annotations

from collections import Counter
from zipfile import ZipFile

import pandas as pd


ZIP_PATH = "ml/datasets/account_takeover/raw/rba-dataset.zip"
CSV_NAME = "rba-dataset.csv"
CHUNK_SIZE = 250_000


def main() -> None:
    print("=" * 70)
    print("CYBERGUARD — ATO STRUCTURE ANALYSIS")
    print("=" * 70)

    total_rows = 0
    ato_rows = 0

    ato_users: set[str] = set()
    all_users: set[str] = set()

    ato_dates = Counter()
    ato_months = Counter()

    first_ato_by_user: dict[str, pd.Timestamp] = {}

    with ZipFile(ZIP_PATH) as archive:
        with archive.open(CSV_NAME) as csv_file:
            for chunk in pd.read_csv(
                csv_file,
                chunksize=CHUNK_SIZE,
                low_memory=False,
            ):
                total_rows += len(chunk)

                chunk["Login Timestamp"] = pd.to_datetime(
                    chunk["Login Timestamp"],
                    errors="coerce",
                    utc=True,
                )

                chunk["User ID"] = (
                    chunk["User ID"]
                    .astype(str)
                )

                all_users.update(chunk["User ID"].unique())

                ato_mask = chunk["Is Account Takeover"].astype(bool)
                ato_chunk = chunk.loc[ato_mask]

                if not ato_chunk.empty:
                    ato_rows += len(ato_chunk)

                    ato_users.update(
                        ato_chunk["User ID"].unique()
                    )

                    dates = ato_chunk["Login Timestamp"].dt.date
                    months = ato_chunk["Login Timestamp"].dt.to_period(
                        "M"
                    ).astype(str)

                    ato_dates.update(dates)
                    ato_months.update(months)

                    for user, timestamp in zip(
                        ato_chunk["User ID"],
                        ato_chunk["Login Timestamp"],
                    ):
                        previous = first_ato_by_user.get(user)

                        if previous is None or timestamp < previous:
                            first_ato_by_user[user] = timestamp

                if total_rows % (CHUNK_SIZE * 10) == 0:
                    print(
                        f"  Processed ~{total_rows:,} rows..."
                    )

    print()
    print("=" * 70)
    print("ATO STRUCTURE SUMMARY")
    print("=" * 70)

    print(f"Total rows: {total_rows:,}")
    print(f"Total ATO rows: {ato_rows:,}")
    print(f"ATO users: {len(ato_users):,}")
    print(f"All users: {len(all_users):,}")

    print()
    print("ATO events by month:")
    for month, count in sorted(ato_months.items()):
        print(f"  {month}: {count}")

    print()
    print("ATO events by date:")
    for date, count in sorted(ato_dates.items()):
        print(f"  {date}: {count}")

    print()
    print(
        "ATO events per affected user:"
    )

    user_ato_counts = Counter()

    with ZipFile(ZIP_PATH) as archive:
        with archive.open(CSV_NAME) as csv_file:
            for chunk in pd.read_csv(
                csv_file,
                chunksize=CHUNK_SIZE,
                low_memory=False,
                usecols=[
                    "User ID",
                    "Is Account Takeover",
                ],
            ):
                ato_mask = chunk["Is Account Takeover"].astype(bool)

                for user in chunk.loc[
                    ato_mask,
                    "User ID",
                ].astype(str):
                    user_ato_counts[user] += 1

    distribution = Counter(user_ato_counts.values())

    for ato_count, user_count in sorted(distribution.items()):
        print(
            f"  {ato_count} ATO event(s): "
            f"{user_count} user(s)"
        )

    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()