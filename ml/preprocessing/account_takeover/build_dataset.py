"""
CyberGuard — Account Takeover Dataset Builder

Memory-safe RBA dataset construction.

Design:
- Raw ZIP remains untouched.
- CSV is streamed directly from the ZIP.
- User-level split prevents user leakage.
- ATO-positive users/events are retained.
- Benign users are selected deterministically.
- Selected users retain their available event history.
- Historical features can therefore be calculated consistently.
- No target/IP/Is Attack IP fields are model features.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from ml.preprocessing.account_takeover.dataset_builder import (
    DatasetBuilderConfig,
    TARGET_COLUMN,
    validate_config,
)
from ml.preprocessing.account_takeover.split_dataset import (
    USER_COLUMN,
    split_by_user,
)


OUTPUT_COLUMNS = [
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
    "Is Account Takeover",
]


# Keep histories bounded so an unusually active user
# cannot consume excessive memory.
MAX_EVENTS_PER_USER = 100

NEGATIVE_TO_POSITIVE_RATIO = 20


def _read_user_target_map(
    config: DatasetBuilderConfig,
) -> pd.DataFrame:
    """Read only User ID and target for user splitting."""

    parts: list[pd.DataFrame] = []

    with ZipFile(config.zip_path) as archive:
        with archive.open(config.csv_name) as csv_file:

            for chunk in pd.read_csv(
                csv_file,
                chunksize=config.chunk_size,
                usecols=[
                    USER_COLUMN,
                    TARGET_COLUMN,
                ],
                low_memory=False,
            ):
                chunk[USER_COLUMN] = (
                    chunk[USER_COLUMN]
                    .fillna("__MISSING_USER__")
                    .astype(str)
                )

                parts.append(chunk)

    return pd.concat(
        parts,
        ignore_index=True,
    )


def _create_user_split_map(
    user_target: pd.DataFrame,
    random_state: int,
) -> dict[str, str]:
    """Assign every user to exactly one split."""

    split = split_by_user(
        user_target,
        random_state=random_state,
    )

    split_map: dict[str, str] = {}

    for user in split.train[USER_COLUMN].astype(str):
        split_map[user] = "train"

    for user in split.validation[
        USER_COLUMN
    ].astype(str):
        split_map[user] = "validation"

    for user in split.test[USER_COLUMN].astype(str):
        split_map[user] = "test"

    return split_map


def _get_positive_users_by_split(
    user_target: pd.DataFrame,
    split_map: dict[str, str],
) -> dict[str, set[str]]:
    """
    Identify ATO-positive users by split.

    Uses a normal Python loop instead of pandas.map() against
    the 4.3M-entry split dictionary.
    """

    positive_users = {
        "train": set(),
        "validation": set(),
        "test": set(),
    }

    positive_rows = user_target[
        user_target[TARGET_COLUMN].astype(bool)
    ]

    for user in positive_rows[
        USER_COLUMN
    ].astype(str).unique():

        split_name = split_map.get(user)

        if split_name in positive_users:
            positive_users[split_name].add(user)

    return positive_users


def _select_benign_users(
    user_target: pd.DataFrame,
    split_map: dict[str, str],
    positive_users_by_split: dict[str, set[str]],
    random_state: int,
) -> dict[str, set[str]]:
    """
    Select deterministic benign users.

    We select a fixed number of benign users rather than attempting
    to count every user's full event history.

    The final collection pass will preserve up to
    MAX_EVENTS_PER_USER events for each selected user.
    """

    rng = random.Random(random_state)

    # Number of ATO-positive users in each split.
    #
    # Because the original dataset contains extremely few ATO users,
    # use a generous benign-user pool while keeping the final dataset
    # manageable.
    benign_users_per_positive_user = 20

    selected: dict[str, set[str]] = {
        "train": set(),
        "validation": set(),
        "test": set(),
    }

    # Build candidate users directly from the already-loaded
    # user-level table.
    all_users = set(
        user_target[USER_COLUMN]
        .astype(str)
        .unique()
    )

    for split_name in (
        "train",
        "validation",
        "test",
    ):

        positive_users = positive_users_by_split[
            split_name
        ]

        candidates = [
            user
            for user in all_users
            if split_map.get(user) == split_name
            and user not in positive_users
        ]

        rng.shuffle(candidates)

        target_count = max(
            len(positive_users)
            * benign_users_per_positive_user,
            100,
        )

        selected[
            split_name
        ] = set(
            candidates[:target_count]
        )

    print()
    print("Selected benign users:")

    for split_name in (
        "train",
        "validation",
        "test",
    ):
        print(
            f"  {split_name}: "
            f"{len(selected[split_name]):,}"
        )

    return selected


def _collect_selected_users(
    config: DatasetBuilderConfig,
    selected_users: dict[str, set[str]],
) -> dict[str, list[dict]]:
    """
    Collect events for selected users.

    The raw RBA dataset is streamed once.
    """

    selected_union = (
        selected_users["train"]
        | selected_users["validation"]
        | selected_users["test"]
    )

    user_events: dict[
        str,
        list[dict],
    ] = {}

    total_rows = 0

    with ZipFile(config.zip_path) as archive:
        with archive.open(config.csv_name) as csv_file:

            for chunk in pd.read_csv(
                csv_file,
                chunksize=config.chunk_size,
                usecols=OUTPUT_COLUMNS,
                low_memory=False,
            ):

                total_rows += len(chunk)

                chunk[USER_COLUMN] = (
                    chunk[USER_COLUMN]
                    .fillna("__MISSING_USER__")
                    .astype(str)
                )

                selected_chunk = chunk[
                    chunk[USER_COLUMN].isin(
                        selected_union
                    )
                ]

                if selected_chunk.empty:
                    continue

                for user, group in selected_chunk.groupby(
                    USER_COLUMN,
                    sort=False,
                ):

                    user = str(user)

                    existing = user_events.setdefault(
                        user,
                        [],
                    )

                    remaining = (
                        MAX_EVENTS_PER_USER
                        - len(existing)
                    )

                    if remaining <= 0:
                        continue

                    records = group[
                        OUTPUT_COLUMNS
                    ].to_dict("records")

                    existing.extend(
                        records[:remaining]
                    )

                if (
                    total_rows
                    % (
                        config.chunk_size * 10
                    )
                    == 0
                ):
                    print(
                        f"  Processed "
                        f"~{total_rows:,} rows..."
                    )

    print()
    print(
        f"Total raw rows scanned: "
        f"{total_rows:,}"
    )

    return {
        "events": user_events,
        "total_rows": total_rows,
    }


def build_dataset(
    config: DatasetBuilderConfig | None = None,
) -> dict[str, dict[str, int]]:
    """Build the user-disjoint ATO datasets."""

    if config is None:
        config = DatasetBuilderConfig()

    validate_config(config)

    output_dir = Path(
        config.output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print(
        "CYBERGUARD — ATO DATASET BUILDER"
    )
    print("=" * 70)

    # ---------------------------------------------------------------
    # Phase 1 — User split
    # ---------------------------------------------------------------

    print()
    print(
        "Phase 1/3: building user split map..."
    )

    user_target = _read_user_target_map(
        config
    )

    user_count = user_target[
        USER_COLUMN
    ].nunique()

    print(
        f"Users discovered: "
        f"{user_count:,}"
    )

    split_map = _create_user_split_map(
        user_target,
        config.random_state,
    )

    positive_users_by_split = (
        _get_positive_users_by_split(
            user_target,
            split_map,
        )
    )

    print()
    print("ATO-positive users:")

    for split_name in (
        "train",
        "validation",
        "test",
    ):
        print(
            f"  {split_name}: "
            f"{len(positive_users_by_split[split_name])}"
        )

    # ---------------------------------------------------------------
    # Phase 2 — Select users
    # ---------------------------------------------------------------

    print()
    print(
        "Phase 2/3: selecting users..."
    )

    benign_users_by_split = (
        _select_benign_users(
            user_target=user_target,
            split_map=split_map,
            positive_users_by_split=(
                positive_users_by_split
            ),
            random_state=config.random_state,
        )
    )

    selected_users: dict[
        str,
        set[str],
    ] = {
        "train": set(),
        "validation": set(),
        "test": set(),
    }

    for split_name in (
        "train",
        "validation",
        "test",
    ):
        selected_users[split_name] = (
            positive_users_by_split[
                split_name
            ]
            | benign_users_by_split[
                split_name
            ]
        )

    print()
    print("Total selected users:")

    for split_name in (
        "train",
        "validation",
        "test",
    ):
        print(
            f"  {split_name}: "
            f"{len(selected_users[split_name]):,}"
        )

    # ---------------------------------------------------------------
    # Phase 3 — Collect and write
    # ---------------------------------------------------------------

    print()
    print(
        "Phase 3/3: collecting selected user histories..."
    )

    collection = _collect_selected_users(
        config,
        selected_users,
    )

    user_events = collection["events"]
    total_rows = collection["total_rows"]

    statistics: dict[
        str,
        dict[str, int],
    ] = {}

    for split_name in (
        "train",
        "validation",
        "test",
    ):

        rows: list[dict] = []

        for user in selected_users[
            split_name
        ]:
            rows.extend(
                user_events.get(
                    user,
                    [],
                )
            )

        final_data = pd.DataFrame(
            rows,
            columns=OUTPUT_COLUMNS,
        )

        if final_data.empty:
            raise RuntimeError(
                f"No data collected for "
                f"{split_name}."
            )

        # Shuffle only for storage.
        # feature_extractor.py will restore chronological
        # order per user before calculating history.
        final_data = final_data.sample(
            frac=1.0,
            random_state=config.random_state,
        ).reset_index(drop=True)

        output_path = (
            output_dir
            / f"{split_name}.csv"
        )

        final_data.to_csv(
            output_path,
            index=False,
        )

        positive_count = int(
            final_data[
                TARGET_COLUMN
            ]
            .astype(bool)
            .sum()
        )

        negative_count = (
            len(final_data)
            - positive_count
        )

        unique_users = int(
            final_data[
                USER_COLUMN
            ].nunique()
        )

        statistics[split_name] = {
            "rows": int(
                len(final_data)
            ),
            "unique_users": unique_users,
            "positive_ato": positive_count,
            "negative_benign": negative_count,
        }

        print()
        print(
            split_name.upper()
        )
        print("-" * 50)
        print(
            f"Rows: "
            f"{len(final_data):,}"
        )
        print(
            f"Unique users: "
            f"{unique_users:,}"
        )
        print(
            f"ATO positives: "
            f"{positive_count:,}"
        )
        print(
            f"Benign negatives: "
            f"{negative_count:,}"
        )
        print(
            f"Saved: "
            f"{output_path}"
        )

    # ---------------------------------------------------------------
    # Verify user disjointness
    # ---------------------------------------------------------------

    print()
    print(
        "Verifying user-disjoint splits..."
    )

    split_users: dict[
        str,
        set[str],
    ] = {}

    for split_name in (
        "train",
        "validation",
        "test",
    ):

        path = (
            output_dir
            / f"{split_name}.csv"
        )

        split_df = pd.read_csv(
            path,
            usecols=[USER_COLUMN],
        )

        split_users[split_name] = set(
            split_df[
                USER_COLUMN
            ]
            .astype(str)
        )

    train_validation_overlap = (
        split_users["train"]
        & split_users["validation"]
    )

    train_test_overlap = (
        split_users["train"]
        & split_users["test"]
    )

    validation_test_overlap = (
        split_users["validation"]
        & split_users["test"]
    )

    print(
        "Train ∩ Validation: "
        f"{len(train_validation_overlap)}"
    )

    print(
        "Train ∩ Test: "
        f"{len(train_test_overlap)}"
    )

    print(
        "Validation ∩ Test: "
        f"{len(validation_test_overlap)}"
    )

    if (
        train_validation_overlap
        or train_test_overlap
        or validation_test_overlap
    ):
        raise RuntimeError(
            "User leakage detected."
        )

    print(
        "User-disjoint verification PASSED."
    )

    # ---------------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------------

    metadata = {
        "dataset": "RBA Account Takeover",

        "source_archive": str(
            config.zip_path
        ),

        "random_state": (
            config.random_state
        ),

        "chunk_size": (
            config.chunk_size
        ),

        "split_strategy": (
            "user_disjoint"
        ),

        "sampling_strategy": (
            "user_level_selection_with_bounded_history"
        ),

        "max_events_per_user": (
            MAX_EVENTS_PER_USER
        ),

        "negative_user_selection": {
            "method": (
                "deterministic_random_user_sampling"
            ),
            "target_benign_users_per_positive_user": 20,
        },

        "raw_rows_scanned": (
            total_rows
        ),

        "splits": statistics,

        "output_columns": OUTPUT_COLUMNS,

        "leakage_policy": {
            "user_overlap": False,
            "target_as_feature": False,
            "ip_as_feature": False,
            "is_attack_ip_as_feature": False,
            "future_events_used_for_history": False,
        },
    }

    metadata_path = (
        output_dir
        / "dataset_metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print(
        "DATASET BUILD COMPLETE"
    )
    print("=" * 70)

    print(
        f"Metadata: {metadata_path}"
    )

    return statistics


if __name__ == "__main__":
    build_dataset()