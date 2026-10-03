"""
CyberGuard malicious URL inference.

Loads the trained XGBoost model and applies the exact same
18-feature URL representation used during training.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from xgboost import XGBClassifier

from ml.preprocessing.malicious_url.feature_extractor import (
    URL_FEATURES,
    extract_url_features,
)


class MaliciousURLPredictor:
    """Predict whether a URL is malicious or benign."""

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

    def predict(self, url: str) -> dict:
        """Predict the security class for one URL."""

        features = extract_url_features(url)

        feature_values = [[
            features[name]
            for name in URL_FEATURES
        ]]

        probability_benign = float(
            self.model.predict_proba(feature_values)[0][1]
        )

        probability_malicious = 1.0 - probability_benign

        prediction = (
            "benign"
            if probability_benign >= 0.5
            else "malicious"
        )

        confidence = max(
            probability_benign,
            probability_malicious,
        )

        return {
            "url": url,
            "prediction": prediction,
            "probability_malicious": probability_malicious,
            "probability_benign": probability_benign,
            "confidence": confidence,
            "model_version": "malicious-url-xgboost-v1",
            "feature_version": "malicious-url-url-only-v1",
            "features": features,
        }


def predict_url(url: str) -> dict:
    """Convenience function for one URL prediction."""

    predictor = MaliciousURLPredictor()
    return predictor.predict(url)


if __name__ == "__main__":
    predictor = MaliciousURLPredictor()

    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/login?verify=123456",
    ]

    for url in test_urls:
        result = predictor.predict(url)

        print("\n" + "=" * 70)
        print(f"URL: {result['url']}")
        print(f"Prediction: {result['prediction']}")
        print(
            f"Malicious probability: "
            f"{result['probability_malicious']:.4f}"
        )
        print(
            f"Benign probability: "
            f"{result['probability_benign']:.4f}"
        )
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Model: {result['model_version']}")
