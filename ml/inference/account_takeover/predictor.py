from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from ml.common.detection import Detection
from ml.common.risk import risk_level_from_score
from ml.preprocessing.account_takeover.feature_extractor import (
    transform_features,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "trained"
    / "account_takeover"
    / "account-takeover-xgboost-v1.joblib"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "metadata"
    / "account-takeover-xgboost-v1.json"
)

STATISTICS_PATH = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "account_takeover"
    / "processed"
    / "ato_feature_statistics.json"
)


class AccountTakeoverPredictor:
    """
    Inference wrapper for the Account Takeover Detection model.

    Uses:
    - trained XGBoost model
    - training-time model metadata
    - training-only feature statistics
    - 25-feature ATO feature extractor
    - optional previous login history
    """

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        metadata_path: Path = METADATA_PATH,
        statistics_path: Path = STATISTICS_PATH,
    ) -> None:

        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.statistics_path = Path(statistics_path)

        self._validate_paths()

        # Load trained model
        self.model = joblib.load(self.model_path)

        # Load metadata
        with self.metadata_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            self.metadata = json.load(file)

        # Load training-only feature statistics
        with self.statistics_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            self.statistics = json.load(file)

        # IMPORTANT:
        # Metadata uses "features", not "feature_names".
        self.feature_names = list(
            self.metadata["features"]
        )

        # IMPORTANT:
        # Threshold is stored inside operating_threshold.
        self.threshold = float(
            self.metadata["operating_threshold"][
                "selected_threshold"
            ]
        )

        self.model_version = self.metadata.get(
            "model_version",
            "account-takeover-xgboost-v1",
        )

        self._validate_model_configuration()

    # ================================================================
    # VALIDATION
    # ================================================================

    def _validate_paths(self) -> None:

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"ATO model not found: {self.model_path}"
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"ATO metadata not found: {self.metadata_path}"
            )

        if not self.statistics_path.exists():
            raise FileNotFoundError(
                "ATO feature statistics not found: "
                f"{self.statistics_path}"
            )

    def _validate_model_configuration(self) -> None:

        if len(self.feature_names) != 25:
            raise ValueError(
                "ATO model must use exactly 25 features. "
                f"Found {len(self.feature_names)}."
            )

        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError(
                "ATO operating threshold must be between 0 and 1. "
                f"Found {self.threshold}."
            )

    # ================================================================
    # EVENT VALIDATION
    # ================================================================

    @staticmethod
    def _validate_event(
        event: dict[str, Any],
    ) -> None:

        if not isinstance(event, dict):
            raise TypeError(
                "event must be a dictionary."
            )

    @staticmethod
    def _validate_history(
        event: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> None:

        if not isinstance(history, list):
            raise TypeError(
                "history must be a list."
            )

        current_user = event.get("User ID")

        current_timestamp = pd.to_datetime(
            event.get("Login Timestamp"),
            errors="coerce",
        )

        if pd.isna(current_timestamp):
            raise ValueError(
                "event contains an invalid Login Timestamp."
            )

        for index, previous_event in enumerate(history):

            if not isinstance(previous_event, dict):
                raise TypeError(
                    f"history[{index}] must be a dictionary."
                )

            previous_user = previous_event.get(
                "User ID"
            )

            if previous_user != current_user:
                raise ValueError(
                    "All history events must belong to "
                    "the same User ID as the current event."
                )

            previous_timestamp = pd.to_datetime(
                previous_event.get("Login Timestamp"),
                errors="coerce",
            )

            if pd.isna(previous_timestamp):
                raise ValueError(
                    f"history[{index}] contains an invalid "
                    "Login Timestamp."
                )

            if previous_timestamp >= current_timestamp:
                raise ValueError(
                    "All history events must occur strictly "
                    "before the current event."
                )

    # ================================================================
    # FEATURE BUILDING
    # ================================================================

    def _build_features(
        self,
        event: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> pd.DataFrame:

        self._validate_event(event)

        self._validate_history(
            event,
            history,
        )

        current_df = pd.DataFrame([event])

        if history:

            history_df = pd.DataFrame(history)

            combined_df = pd.concat(
                [
                    history_df,
                    current_df,
                ],
                ignore_index=True,
            )

        else:
            combined_df = current_df

        combined_df["Login Timestamp"] = pd.to_datetime(
            combined_df["Login Timestamp"],
            errors="raise",
        )

        # Ensure chronological ordering.
        combined_df = combined_df.sort_values(
            by=[
                "User ID",
                "Login Timestamp",
            ],
            kind="stable",
        ).reset_index(drop=True)

        # IMPORTANT:
        # Uses saved training statistics.
        # Does NOT refit statistics during inference.
        transformed = transform_features(
            combined_df,
            self.statistics,
        )

        if transformed.empty:
            raise ValueError(
                "Feature extraction produced no rows."
            )

        # The last row corresponds to the current event
        # after chronological sorting.
        current_features = transformed.iloc[
            [-1]
        ].copy()

        missing_features = [
            feature
            for feature in self.feature_names
            if feature not in current_features.columns
        ]

        if missing_features:
            raise ValueError(
                "Missing model features: "
                + ", ".join(missing_features)
            )

        # Force exact training feature order.
        current_features = current_features[
            self.feature_names
        ]

        if current_features.shape[1] != 25:
            raise ValueError(
                "ATO inference must produce exactly "
                f"25 features. Found "
                f"{current_features.shape[1]}."
            )

        return current_features

    # ================================================================
    # PROBABILITY
    # ================================================================

    def predict_probability(
        self,
        event: dict[str, Any],
        history: list[dict[str, Any]] | None = None,
    ) -> float:

        if history is None:
            history = []

        features = self._build_features(
            event,
            history,
        )

        probability = float(
            self.model.predict_proba(
                features
            )[0][1]
        )

        # Numerical safety.
        probability = max(
            0.0,
            min(1.0, probability),
        )

        return probability

    # ================================================================
    # DETECTION
    # ================================================================

    def analyze(
        self,
        event: dict[str, Any],
        history: list[dict[str, Any]] | None = None,
    ) -> Detection:

        if history is None:
            history = []

        probability = self.predict_probability(
            event,
            history,
        )

        risk_score = probability * 100.0

        risk_level = risk_level_from_score(
            risk_score
        )

        is_account_takeover = (
            probability >= self.threshold
        )

        if is_account_takeover:
            prediction = "ACCOUNT_TAKEOVER"
            confidence = probability
        else:
            prediction = "NO_ACCOUNT_TAKEOVER"
            confidence = 1.0 - probability

        probability_percent = (
            f"{probability:.2%}"
        )

        threshold_percent = (
            f"{self.threshold:.2%}"
        )

        indicators = [
            f"ATO probability: {probability_percent}",
            f"Risk score: {risk_score:.2f}/100",
            f"Operating threshold: {threshold_percent}",
        ]

        if is_account_takeover:

            explanation = (
                f"The login event has an ATO probability "
                f"of {probability_percent}, which meets or "
                f"exceeds the operating threshold of "
                f"{threshold_percent}."
            )

            recommended_actions = [
                "Block or step-up authenticate the login.",
                "Review recent account activity.",
                "Verify the user's identity.",
            ]

        else:

            explanation = (
                f"The login event has an ATO probability "
                f"of {probability_percent}, which is below "
                f"the operating threshold of "
                f"{threshold_percent}."
            )

            recommended_actions = [
                "Allow normal processing.",
                "Continue monitoring account activity.",
            ]

        return Detection(
            category="account_takeover",
            prediction=prediction,
            risk_score=round(
                risk_score,
                2,
            ),
            risk_level=risk_level.value,
            confidence=round(
                confidence,
                4,
            ),
            indicators=indicators,
            explanation=explanation,
            recommended_actions=recommended_actions,
            model_version=self.model_version,
        )

    # ================================================================
    # CONVENIENCE METHOD
    # ================================================================

    def predict_account_takeover(
        self,
        event: dict[str, Any],
        history: list[dict[str, Any]] | None = None,
    ) -> Detection:

        return self.analyze(
            event=event,
            history=history,
        )