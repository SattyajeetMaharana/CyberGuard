"""
SHAP explainability for the CyberGuard malicious URL model.

The explanation is generated from the actual trained XGBoost model
and the exact same 18 URL features used during inference.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import shap
import yaml
from xgboost import XGBClassifier

from ml.preprocessing.malicious_url.feature_extractor import (
    URL_FEATURES,
    extract_url_features,
)
from ml.xai.common.explanation_schema import (
    Explanation,
    FeatureContribution,
)


class MaliciousURLSHAPExplainer:
    """Generate SHAP explanations for malicious URL predictions."""

    def __init__(
        self,
        model_path: str | Path | None = None,
    ) -> None:
        root = Path(__file__).resolve().parents[3]

        if model_path is None:
            config_path = (
                root
                / "ml"
                / "configs"
                / "malicious_url"
                / "config.yaml"
            )

            with config_path.open("r", encoding="utf-8") as file:
                config = yaml.safe_load(file)

            model_path = root / config["output"]["model"]

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.model = XGBClassifier()
        self.model.load_model(self.model_path)

        self.explainer = shap.TreeExplainer(self.model)

    def explain(self, url: str) -> Explanation:
        """Explain the prediction for one URL."""

        features = extract_url_features(url)

        feature_frame = pd.DataFrame(
            [features],
            columns=URL_FEATURES,
        )

        probability_benign = float(
            self.model.predict_proba(feature_frame)[0][1]
        )

        probability_malicious = 1.0 - probability_benign

        prediction = (
            "benign"
            if probability_benign >= 0.5
            else "malicious"
        )

        shap_values = self.explainer.shap_values(feature_frame)

        if hasattr(shap_values, "values"):
            shap_values = shap_values.values

        shap_values = shap_values[0]

        expected_value = self.explainer.expected_value

        if hasattr(expected_value, "__len__"):
            base_value = float(expected_value[0])
        else:
            base_value = float(expected_value)

        contributions = [
            FeatureContribution(
                feature=feature_name,
                value=float(features[feature_name]),
                contribution=float(shap_value),
            )
            for feature_name, shap_value in zip(
                URL_FEATURES,
                shap_values,
            )
        ]

        contributions.sort(
            key=lambda item: abs(item.contribution),
            reverse=True,
        )

        return Explanation(
            method="SHAP TreeExplainer",
            model_version="malicious-url-xgboost-v1",
            prediction=prediction,
            probability_malicious=probability_malicious,
            probability_benign=probability_benign,
            base_value=base_value,
            feature_contributions=contributions,
        )


def explain_url(url: str) -> dict:
    """Convenience function for one URL explanation."""

    explainer = MaliciousURLSHAPExplainer()
    return explainer.explain(url).to_dict()


if __name__ == "__main__":
    explainer = MaliciousURLSHAPExplainer()

    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/login?verify=123456",
    ]

    for url in test_urls:
        explanation = explainer.explain(url)

        print("\n" + "=" * 70)
        print(f"URL: {url}")
        print(f"Prediction: {explanation.prediction}")
        print(
            "Malicious probability: "
            f"{explanation.probability_malicious:.6f}"
        )
        print(
            "Benign probability: "
            f"{explanation.probability_benign:.6f}"
        )
        print(f"Base value: {explanation.base_value:.6f}")
        print("\nTop feature contributions:")

        for contribution in explanation.feature_contributions[:10]:
            print(
                f"  {contribution.feature}: "
                f"value={contribution.value:.6f}, "
                f"SHAP={contribution.contribution:.6f}"
            )
