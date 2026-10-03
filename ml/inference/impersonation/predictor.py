from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(
    "ml/models/trained/impersonation/"
    "impersonation-xgboost-v1.joblib"
)

MODEL_VERSION = "impersonation-xgboost-v1"


FEATURES = [
    "urgency_level",
    "requests_wire_transfer",
    "requests_gift_cards",
    "requests_sensitive_data",
    "dkim_pass",
    "spf_pass",
    "dmarc_pass",
    "reply_to_mismatch",
    "is_end_of_month",
    "is_friday",
    "sent_outside_hours",
    "requested_amount_usd",
    "auth_failure",
    "partial_auth",
    "full_auth_bypass",
    "payroll_timing",
    "weekend_timing",
    "after_hours",
]


class ImpersonationPredictor:
    """Inference wrapper for the CyberGuard impersonation model."""

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Impersonation model not found: {model_path}"
            )

        self.model = joblib.load(model_path)
        self.model_path = model_path

    def predict(self, features: dict) -> dict:
        """Predict whether the supplied event is impersonation/BEC."""

        if not isinstance(features, dict):
            raise TypeError("features must be a dictionary")

        missing = [
            feature
            for feature in FEATURES
            if feature not in features
        ]

        if missing:
            raise ValueError(
                f"Missing required features: {missing}"
            )

        values = {
            feature: features[feature]
            for feature in FEATURES
        }

        frame = pd.DataFrame([values], columns=FEATURES)

        probability_impersonation = float(
            self.model.predict_proba(frame)[0][1]
        )

        probability_benign = float(
            self.model.predict_proba(frame)[0][0]
        )

        prediction = (
            "impersonation"
            if probability_impersonation >= 0.5
            else "benign"
        )

        confidence = max(
            probability_impersonation,
            probability_benign,
        )

        return {
            "prediction": prediction,
            "probability_impersonation": probability_impersonation,
            "probability_benign": probability_benign,
            "confidence": confidence,
            "model_version": MODEL_VERSION,
            "features": values,
        }