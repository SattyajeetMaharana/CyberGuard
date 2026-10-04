from pathlib import Path

import joblib
import pandas as pd
import shap


MODEL_PATH = Path(
    "ml/models/trained/account_takeover/"
    "account-takeover-xgboost-v1.joblib"
)

MODEL_VERSION = "account-takeover-xgboost-v1"


FEATURES = [
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


class AccountTakeoverSHAPExplainer:
    """SHAP explanation generator for the account takeover model."""

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Account takeover model not found: {model_path}"
            )

        self.model = joblib.load(model_path)
        self.explainer = shap.TreeExplainer(self.model)

    def explain(self, features: dict, top_k: int = 5) -> dict:
        """Generate a SHAP explanation for one ATO prediction."""

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
            "account_takeover"
            if prediction_probability >= 0.5
            else "no_account_takeover"
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
            "probability_account_takeover": prediction_probability,
            "probability_no_account_takeover": (
                1.0 - prediction_probability
            ),
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
                direction = "toward account takeover"
            elif contribution < 0:
                effect = "decreased"
                direction = "toward no account takeover"
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
            f"{probability_percent:.2f}% account takeover probability. "
            + "; ".join(parts)
            + "."
        )