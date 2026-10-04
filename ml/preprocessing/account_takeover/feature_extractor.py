"""
CyberGuard — Account Takeover Feature Extraction

Leakage-safe feature extraction for the RBA Account Takeover dataset.

Features:
- Time/context features
- Training-only global frequency features
- User history features
- User-specific novelty features

Important:
- Global frequency statistics are fitted ONLY on training data.
- History features use ONLY events before the current event.
- The current event is never included in its own history.
- Target labels are never used as model features.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

import numpy as np
import pandas as pd


FEATURE_COLUMNS: List[str] = [
    "login_hour",
    "login_day_of_week",
    "is_weekend",
    "is_outside_hours",
    "login_successful",
    "country_frequency",
    "region_frequency",
    "city_frequency",
    "asn_frequency",
    "browser_frequency",
    "os_frequency",
    "device_frequency",
    "user_login_count",
    "user_failure_count",
    "user_failure_rate",
    "user_unique_countries",
    "user_unique_devices",
    "time_since_previous_login_seconds",
    "is_new_country",
    "is_new_region",
    "is_new_city",
    "is_new_asn",
    "is_new_browser",
    "is_new_os",
    "is_new_device",
]


REQUIRED_COLUMNS = [
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


CATEGORICAL_COLUMNS = [
    "Country",
    "Region",
    "City",
    "ASN",
    "Browser Name and Version",
    "OS Name and Version",
    "Device Type",
]


NOVELTY_FEATURE_MAP = {
    "Country": "is_new_country",
    "Region": "is_new_region",
    "City": "is_new_city",
    "ASN": "is_new_asn",
    "Browser Name and Version": "is_new_browser",
    "OS Name and Version": "is_new_os",
    "Device Type": "is_new_device",
}


MISSING_CATEGORY = "__MISSING__"
MISSING_USER = "__MISSING_USER__"


def _validate_input(df: pd.DataFrame) -> None:
    """Validate required raw columns."""

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )


def _normalise_categories(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Normalize user IDs and categorical values."""

    result = df.copy()

    result["User ID"] = (
        result["User ID"]
        .fillna(MISSING_USER)
        .astype(str)
    )

    for column in CATEGORICAL_COLUMNS:
        result[column] = (
            result[column]
            .fillna(MISSING_CATEGORY)
            .astype(str)
        )

    return result


def _prepare_base(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create basic time and login-context features."""

    result = _normalise_categories(df)

    result["Login Timestamp"] = pd.to_datetime(
        result["Login Timestamp"],
        errors="coerce",
        utc=True,
    )

    if result["Login Timestamp"].isna().any():
        raise ValueError(
            "Invalid or missing Login Timestamp values found."
        )

    result["login_hour"] = (
        result["Login Timestamp"]
        .dt.hour
        .astype(np.int8)
    )

    result["login_day_of_week"] = (
        result["Login Timestamp"]
        .dt.dayofweek
        .astype(np.int8)
    )

    result["is_weekend"] = (
        result["login_day_of_week"] >= 5
    ).astype(np.int8)

    result["is_outside_hours"] = (
        (result["login_hour"] < 7)
        | (result["login_hour"] >= 22)
    ).astype(np.int8)

    result["login_successful"] = (
        pd.to_numeric(
            result["Login Successful"],
            errors="coerce",
        )
        .fillna(0)
        .astype(np.int8)
    )

    return result


def fit_feature_statistics(
    train_df: pd.DataFrame,
) -> Dict[str, Dict[str, float]]:
    """
    Fit categorical frequency statistics using training data ONLY.
    """

    _validate_input(train_df)

    prepared = _prepare_base(train_df)

    if len(prepared) == 0:
        raise ValueError(
            "Training dataframe is empty."
        )

    total_rows = len(prepared)

    statistics: Dict[str, Dict[str, float]] = {}

    for column in CATEGORICAL_COLUMNS:
        frequencies = (
            prepared[column]
            .value_counts(dropna=False)
            .div(total_rows)
            .to_dict()
        )

        statistics[column] = frequencies

    return statistics


def _apply_frequency_features(
    df: pd.DataFrame,
    statistics: Dict[str, Dict[str, float]],
) -> pd.DataFrame:
    """Apply training-derived global frequency statistics."""

    result = df.copy()

    feature_name_map = {
        "Country": "country_frequency",
        "Region": "region_frequency",
        "City": "city_frequency",
        "ASN": "asn_frequency",
        "Browser Name and Version": "browser_frequency",
        "OS Name and Version": "os_frequency",
        "Device Type": "device_frequency",
    }

    for source_column, feature_column in feature_name_map.items():

        if source_column not in statistics:
            raise ValueError(
                f"Missing frequency statistics for "
                f"{source_column}."
            )

        frequency_map = statistics[source_column]

        result[feature_column] = (
            result[source_column]
            .map(frequency_map)
            .fillna(0.0)
            .astype(np.float32)
        )

    return result


def _build_user_history_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build leakage-safe user-history features.

    Only events before the current event are used.
    """

    result = df.copy()

    result["_original_order"] = np.arange(
        len(result)
    )

    result = result.sort_values(
        [
            "User ID",
            "Login Timestamp",
            "_original_order",
        ],
        kind="mergesort",
    ).reset_index(drop=True)

    result["user_login_count"] = (
        result.groupby(
            "User ID",
            sort=False,
        )
        .cumcount()
        .astype(np.float32)
    )

    current_failed = (
        result["login_successful"] == 0
    ).astype(np.int8)

    cumulative_failures = (
        current_failed.groupby(
            result["User ID"],
            sort=False,
        )
        .cumsum()
    )

    result["user_failure_count"] = (
        cumulative_failures
        - current_failed
    ).astype(np.float32)

    result["user_failure_rate"] = (
        result["user_failure_count"]
        / result["user_login_count"].replace(
            0,
            np.nan,
        )
    ).fillna(0.0).astype(np.float32)

    # -1.0 means there is no previous login.
    result["time_since_previous_login_seconds"] = (
        result.groupby(
            "User ID",
            sort=False,
        )["Login Timestamp"]
        .diff()
        .dt.total_seconds()
        .fillna(-1.0)
        .astype(np.float32)
    )

    novelty_columns = list(
        NOVELTY_FEATURE_MAP.values()
    )

    for feature_name in novelty_columns:
        result[feature_name] = 0

    result["user_unique_countries"] = 0.0
    result["user_unique_devices"] = 0.0

    user_history = defaultdict(
        lambda: {
            column: set()
            for column in CATEGORICAL_COLUMNS
        }
    )

    for row_index, row in result.iterrows():

        user_id = row["User ID"]
        history = user_history[user_id]

        for (
            source_column,
            feature_column,
        ) in NOVELTY_FEATURE_MAP.items():

            current_value = row[source_column]

            result.at[
                row_index,
                feature_column,
            ] = int(
                current_value
                not in history[source_column]
            )

        result.at[
            row_index,
            "user_unique_countries",
        ] = len(
            history["Country"]
        )

        result.at[
            row_index,
            "user_unique_devices",
        ] = len(
            history["Device Type"]
        )

        for source_column in CATEGORICAL_COLUMNS:
            history[source_column].add(
                row[source_column]
            )

    result["user_unique_countries"] = (
        result["user_unique_countries"]
        .astype(np.float32)
    )

    result["user_unique_devices"] = (
        result["user_unique_devices"]
        .astype(np.float32)
    )

    for feature_name in novelty_columns:
        result[feature_name] = (
            result[feature_name]
            .astype(np.int8)
        )

    result = result.sort_values(
        "_original_order",
        kind="mergesort",
    )

    result = result.drop(
        columns=["_original_order"]
    )

    return result


def transform_features(
    df: pd.DataFrame,
    statistics: Dict[str, Dict[str, float]],
) -> pd.DataFrame:
    """
    Transform raw login data into the final 25-feature representation.
    """

    _validate_input(df)

    prepared = _prepare_base(df)

    prepared = _apply_frequency_features(
        prepared,
        statistics,
    )

    prepared = _build_user_history_features(
        prepared
    )

    features = prepared[
        FEATURE_COLUMNS
    ].copy()

    for column in FEATURE_COLUMNS:
        features[column] = pd.to_numeric(
            features[column],
            errors="coerce",
        )

    features = features.replace(
        [np.inf, -np.inf],
        np.nan,
    ).fillna(0.0)

    return features.astype(
        np.float32
    )


def get_feature_schema() -> List[str]:
    """Return the ordered 25-feature schema."""

    return FEATURE_COLUMNS.copy()