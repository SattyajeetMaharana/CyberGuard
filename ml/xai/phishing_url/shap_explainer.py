from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import shap

from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    extract_url_features,
)

MODEL_PATH = Path(
    "ml/models/trained/phishing_url/url_xgboost_v1.joblib"
)

MODEL_VERSION = "url-xgb-v1"


_model = None
_explainer = None


def _load_model():
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def _load_explainer():
    global _explainer

    if _explainer is None:
        model = _load_model()
        _explainer = shap.TreeExplainer(model)

    return _explainer


def explain_url(url: str, top_k: int = 5) -> dict:
    """
    Generate a SHAP explanation for a URL prediction.

    Returns the actual model feature contributions.
    """

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    features = extract_url_features(url)

    feature_vector = [
        float(features[name])
        for name in FEATURE_NAMES
    ]

    X = pd.DataFrame(
        [feature_vector],
        columns=FEATURE_NAMES,
    )

    model = _load_model()
    explainer = _load_explainer()

    probabilities = model.predict_proba(X)[0]

    phishing_probability = float(probabilities[0])
    legitimate_probability = float(probabilities[1])

    # ---------------------------------------------------------
    # SHAP values
    # ---------------------------------------------------------
    shap_output = explainer.shap_values(X)

    # XGBoost binary classification normally returns
    # one SHAP array for the positive class.
    if isinstance(shap_output, list):
        shap_values = shap_output[0][0]
    else:
        shap_values = shap_output[0]

    shap_values = [float(value) for value in shap_values]

    explanation_rows = []

    for feature, value, contribution in zip(
        FEATURE_NAMES,
        feature_vector,
        shap_values,
    ):
        explanation_rows.append(
            {
                "feature": feature,
                "value": value,
                "shap_value": contribution,
                "direction": (
                    "increases_phishing_risk"
                    if contribution > 0
                    else "decreases_phishing_risk"
                    if contribution < 0
                    else "neutral"
                ),
            }
        )

    # Sort by absolute SHAP contribution.
    explanation_rows.sort(
        key=lambda item: abs(item["shap_value"]),
        reverse=True,
    )

    top_features = explanation_rows[:top_k]

    return {
        "url": url,
        "model_version": MODEL_VERSION,
        "phishing_probability": round(
            phishing_probability,
            6,
        ),
        "legitimate_probability": round(
            legitimate_probability,
            6,
        ),
        "top_features": top_features,
        "all_features": explanation_rows,
    }


if __name__ == "__main__":
    test_urls = [
        "https://www.google.com",
        "https://example.com",
        "http://192.168.1.10/login",
    ]

    print("=" * 70)
    print("CYBERGUARD URL SHAP EXPLANATION TEST")
    print("=" * 70)

    for url in test_urls:
        print("\nURL:")
        print(url)

        result = explain_url(url)

        print("\nPrediction:")
        print(
            f"Phishing probability: "
            f"{result['phishing_probability']}"
        )

        print("\nTop SHAP features:")

        for item in result["top_features"]:
            print(
                f"  {item['feature']:30s} "
                f"value={item['value']:<10} "
                f"SHAP={item['shap_value']:+.6f} "
                f"{item['direction']}"
            )