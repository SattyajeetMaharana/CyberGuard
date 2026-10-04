"""
CyberGuard — Account Takeover Dataset Splitting

Creates leakage-resistant train/validation/test splits for the RBA dataset.

Primary rule:
The same User ID must never appear in more than one split.

The split is performed at USER level rather than individual-event level.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split


TARGET_COLUMN = "Is Account Takeover"
USER_COLUMN = "User ID"

RANDOM_STATE = 42

TRAIN_SIZE = 0.70
VALIDATION_SIZE = 0.15
TEST_SIZE = 0.15


@dataclass
class DatasetSplit:
    """Container for train/validation/test datasets."""

    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def _validate_split_sizes() -> None:
    if abs(
        TRAIN_SIZE + VALIDATION_SIZE + TEST_SIZE - 1.0
    ) > 1e-9:
        raise ValueError(
            "TRAIN_SIZE + VALIDATION_SIZE + TEST_SIZE must equal 1"
        )


def split_by_user(
    df: pd.DataFrame,
    random_state: int = RANDOM_STATE,
) -> DatasetSplit:
    """
    Split authentication events by User ID.

    Every user is assigned to exactly one split.
    Therefore, no user's historical behavior can leak between
    training, validation, and test sets.
    """
    _validate_split_sizes()

    required = {
        USER_COLUMN,
        TARGET_COLUMN,
    }

    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if df.empty:
        raise ValueError("Cannot split an empty dataframe")

    user_labels = (
        df.groupby(USER_COLUMN)[TARGET_COLUMN]
        .max()
        .reset_index()
    )

    users = user_labels[USER_COLUMN].astype(str)
    labels = user_labels[TARGET_COLUMN].astype(int)

    # Stratification is attempted only when every class has enough
    # users to support the requested split.
    label_counts = labels.value_counts()

    can_stratify = (
        len(label_counts) == 2
        and label_counts.min() >= 3
    )

    if can_stratify:
        train_users, temp_users = train_test_split(
            users,
            test_size=VALIDATION_SIZE + TEST_SIZE,
            random_state=random_state,
            stratify=labels,
        )
    else:
        train_users, temp_users = train_test_split(
            users,
            test_size=VALIDATION_SIZE + TEST_SIZE,
            random_state=random_state,
        )

    temp_labels = (
        user_labels.set_index(USER_COLUMN)
        .loc[temp_users, TARGET_COLUMN]
        .astype(int)
    )

    temp_test_fraction = (
        TEST_SIZE / (VALIDATION_SIZE + TEST_SIZE)
    )

    temp_label_counts = temp_labels.value_counts()

    can_stratify_temp = (
        len(temp_label_counts) == 2
        and temp_label_counts.min() >= 2
    )

    if can_stratify_temp:
        validation_users, test_users = train_test_split(
            temp_users,
            test_size=temp_test_fraction,
            random_state=random_state,
            stratify=temp_labels,
        )
    else:
        validation_users, test_users = train_test_split(
            temp_users,
            test_size=temp_test_fraction,
            random_state=random_state,
        )

    train_user_set = set(train_users)
    validation_user_set = set(validation_users)
    test_user_set = set(test_users)

    if train_user_set & validation_user_set:
        raise RuntimeError("Train/validation user overlap detected")

    if train_user_set & test_user_set:
        raise RuntimeError("Train/test user overlap detected")

    if validation_user_set & test_user_set:
        raise RuntimeError("Validation/test user overlap detected")

    train = df[
        df[USER_COLUMN].astype(str).isin(train_user_set)
    ].copy()

    validation = df[
        df[USER_COLUMN].astype(str).isin(validation_user_set)
    ].copy()

    test = df[
        df[USER_COLUMN].astype(str).isin(test_user_set)
    ].copy()

    return DatasetSplit(
        train=train,
        validation=validation,
        test=test,
    )


def print_split_summary(split: DatasetSplit) -> None:
    """Print event/user/target statistics for each split."""

    for name, data in [
        ("TRAIN", split.train),
        ("VALIDATION", split.validation),
        ("TEST", split.test),
    ]:
        users = data[USER_COLUMN].nunique()
        events = len(data)
        positives = int(data[TARGET_COLUMN].astype(bool).sum())

        print()
        print(f"{name}")
        print("-" * 50)
        print(f"Events: {events:,}")
        print(f"Users: {users:,}")
        print(f"ATO events: {positives:,}")

        if events:
            print(
                f"ATO rate: "
                f"{positives / events:.6%}"
            )


def verify_no_user_overlap(split: DatasetSplit) -> None:
    """Raise an error if any user occurs in multiple splits."""

    train_users = set(
        split.train[USER_COLUMN].astype(str)
    )
    validation_users = set(
        split.validation[USER_COLUMN].astype(str)
    )
    test_users = set(
        split.test[USER_COLUMN].astype(str)
    )

    assert not train_users & validation_users
    assert not train_users & test_users
    assert not validation_users & test_users