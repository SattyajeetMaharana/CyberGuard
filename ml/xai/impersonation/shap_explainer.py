from pathlib import Path

import joblib
import pandas as pd
import shap


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


class ImpersonationSHAPExplainer:
    """SHAP explanation generator for the impersonation model."""

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Impersonation model not found: {model_path}"
            )

        self.model = joblib.load(model_path)
        self.explainer = shap.TreeExplainer(self.model)

    def explain(self, features: dict, top_k: int = 5) -> dict:
        """Generate a SHAP explanation for one prediction."""

        if not isinstance(features, dict):
            raise TypeError("features must be a dictionary")

        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")

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

        frame = pd.DataFrame(
            [values],
            columns=FEATURES,
        )

        shap_values = self.explainer.shap_values(frame)

        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        contributions = shap_values[0]

        ranked = sorted(
            zip(
                FEATURES,
                frame.iloc[0].tolist(),
                contributions,
            ),
            key=lambda item: abs(float(item[2])),
            reverse=True,
        )

        top_features = []
        feature_values = {}
        contribution_values = {}

        for feature, value, contribution in ranked[:top_k]:
            contribution = float(contribution)

            top_features.append(feature)
            feature_values[feature] = value
            contribution_values[feature] = contribution

        prediction_probability = float(
            self.model.predict_proba(frame)[0][1]
        )

        prediction = (
            "impersonation"
            if prediction_probability >= 0.5
            else "benign"
        )

        human_readable = self._build_explanation(
            prediction,
            prediction_probability,
            ranked[:top_k],
        )

        return {
            "method": "SHAP TreeExplainer",
            "model_version": MODEL_VERSION,
            "prediction": prediction,
            "probability_impersonation": prediction_probability,
            "top_features": top_features,
            "feature_values": feature_values,
            "contributions": contribution_values,
            "human_readable_explanation": human_readable,
        }

    @staticmethod
    def _build_explanation(
        prediction: str,
        probability: float,
        ranked_features: list,
    ) -> str:
        parts = []

        for feature, value, contribution in ranked_features:
            contribution = float(contribution)

            if contribution > 0:
                effect = "increased"
                direction = "toward impersonation"
            elif contribution < 0:
                effect = "decreased"
                direction = "toward benign"
            else:
                effect = "had no meaningful effect on"
                direction = "the model score"

            if contribution == 0:
                parts.append(
                    f"{feature}={value} {effect} "
                    f"{direction} (SHAP {contribution:+.3f})"
                )
            else:
                parts.append(
                    f"{feature}={value} {effect} the model score "
                    f"{direction} (SHAP {contribution:+.3f})"
                )

        probability_percent = probability * 100

        return (
            f"The model predicted {prediction} with "
            f"{probability_percent:.2f}% impersonation probability. "
            + "; ".join(parts)
            + "."
        )