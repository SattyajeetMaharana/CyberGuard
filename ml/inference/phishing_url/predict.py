from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import shap

from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    FEATURE_VERSION,
    extract_url_features,
)
from ml.common.risk import risk_level_from_score


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = Path(
    "ml/models/trained/phishing_url/url_xgboost_v1.joblib"
)

MODEL_VERSION = "url-xgb-v1"
CATEGORY = "phishing_url"


# ============================================================
# LOAD MODEL
# ============================================================

_model = None
_explainer = None


def _load_model():
    """
    Load the trained XGBoost model once and reuse it.
    """

    global _model

    if _model is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

    return _model


# ============================================================
# LOAD SHAP EXPLAINER
# ============================================================

def _load_explainer():
    """
    Create the SHAP TreeExplainer once and reuse it.
    """

    global _explainer

    if _explainer is None:

        model = _load_model()

        _explainer = shap.TreeExplainer(model)

    return _explainer


# ============================================================
# SHAP EXPLANATION
# ============================================================

def _generate_shap_explanation(
    X: pd.DataFrame,
    feature_vector: list[float],
    top_k: int = 5,
) -> dict:
    """
    Generate model-based SHAP explanation.

    SHAP values represent the contribution of each feature
    to the model output. They are not probabilities.
    """

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than 0"
        )

    explainer = _load_explainer()

    shap_output = explainer.shap_values(X)

    # Current SHAP + XGBoost returns:
    # numpy.ndarray with shape (1, number_of_features)
    if isinstance(shap_output, list):

        shap_values = shap_output[0][0]

    else:

        shap_values = shap_output[0]

    shap_values = [
        float(value)
        for value in shap_values
    ]

    explanation_rows = []

    for feature, value, contribution in zip(
        FEATURE_NAMES,
        feature_vector,
        shap_values,
    ):

        if contribution > 0:

            direction = "increases_phishing_risk"

        elif contribution < 0:

            direction = "decreases_phishing_risk"

        else:

            direction = "neutral"

        explanation_rows.append(
            {
                "feature": feature,
                "value": value,
                "shap_value": contribution,
                "direction": direction,
            }
        )

    # Sort by absolute contribution.
    # This gives the most influential features first.
    explanation_rows.sort(
        key=lambda item: abs(item["shap_value"]),
        reverse=True,
    )

    return {
        "top_features": explanation_rows[:top_k],
        "all_features": explanation_rows,
    }


# ============================================================
# URL PREDICTION
# ============================================================

def predict(url: str) -> dict:
    """
    Predict whether a URL is phishing or legitimate.

    Returns a standardized CyberGuard-style detection object
    containing prediction, risk, indicators and SHAP explanation.
    """

    # --------------------------------------------------------
    # Extract URL features
    # --------------------------------------------------------

    features = extract_url_features(url)

    feature_vector = [
        float(features[name])
        for name in FEATURE_NAMES
    ]

    X = pd.DataFrame(
        [feature_vector],
        columns=FEATURE_NAMES,
    )

    # --------------------------------------------------------
    # Model inference
    # --------------------------------------------------------

    model = _load_model()

    probabilities = model.predict_proba(X)[0]

    # Model label mapping:
    #
    # 0 = phishing
    # 1 = legitimate
    #
    # Therefore:
    # phishing_probability = probability of class 0
    # legitimate_probability = probability of class 1

    phishing_probability = float(
        probabilities[0]
    )

    legitimate_probability = float(
        probabilities[1]
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    if phishing_probability >= 0.5:

        prediction = "malicious"

    else:

        prediction = "benign"

    # --------------------------------------------------------
    # Risk score
    # --------------------------------------------------------

    risk_score = phishing_probability * 100

    risk_score = max(
        0.0,
        min(100.0, risk_score),
    )

    risk_level = risk_level_from_score(
        risk_score
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = max(
        phishing_probability,
        legitimate_probability,
    )

    # --------------------------------------------------------
    # Indicators
    # --------------------------------------------------------

    indicators = []

    if features["IsHTTPS"] == 0:

        indicators.append(
            "URL does not use HTTPS"
        )

    if features["IsDomainIP"] == 1:

        indicators.append(
            "URL uses an IP address instead of a domain name"
        )

    if features["NoOfSubDomain"] >= 3:

        indicators.append(
            "URL contains multiple subdomains"
        )

    if features["NoOfDegitsInURL"] >= 5:

        indicators.append(
            "URL contains a high number of digits"
        )

    if features["NoOfQMarkInURL"] > 0:

        indicators.append(
            "URL contains query parameters"
        )

    if features["NoOfAmpersandInURL"] > 0:

        indicators.append(
            "URL contains multiple query parameters"
        )

    if features["HasObfuscation"] == 1:

        indicators.append(
            "URL contains percent-encoded characters"
        )

    if features["URLLength"] >= 100:

        indicators.append(
            "URL is unusually long"
        )

    # --------------------------------------------------------
    # Recommended actions
    # --------------------------------------------------------

    if prediction == "malicious":

        recommended_actions = [
            "Do not open the URL",
            "Verify the sender or source",
            "Report the URL if received through a suspicious message",
        ]

    else:

        recommended_actions = [
            "URL appears benign according to the model",
            "Continue to verify the source before entering sensitive information",
        ]

    # --------------------------------------------------------
    # SHAP explanation
    # --------------------------------------------------------

    shap_explanation = _generate_shap_explanation(
        X=X,
        feature_vector=feature_vector,
        top_k=5,
    )

    # --------------------------------------------------------
    # Human-readable explanation
    # --------------------------------------------------------

    top_feature_names = [
        item["feature"]
        for item in shap_explanation["top_features"]
    ]

    explanation = (
        f"Model classified the URL as {prediction} "
        f"with phishing probability "
        f"{phishing_probability:.4f}. "
        f"Top model-influencing features: "
        f"{', '.join(top_feature_names)}."
    )

    # --------------------------------------------------------
    # Standardized detection object
    # --------------------------------------------------------

    return {
        "category": CATEGORY,
        "prediction": prediction,
        "risk_score": round(
            risk_score,
            2,
        ),
        "risk_level": risk_level.value,
        "confidence": round(
            confidence,
            4,
        ),
        "indicators": indicators,
        "explanation": explanation,
        "recommended_actions": recommended_actions,
        "model_version": MODEL_VERSION,
        "feature_version": FEATURE_VERSION,
        "phishing_probability": round(
            phishing_probability,
            4,
        ),
        "legitimate_probability": round(
            legitimate_probability,
            4,
        ),
        "xai": {
            "method": "SHAP",
            "top_features": shap_explanation["top_features"],
            "all_features": shap_explanation["all_features"],
        },
    }


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    test_urls = [
        "https://www.google.com",
        "https://www.example.com/login?id=123",
        "http://192.168.1.10/login",
    ]

    print("=" * 70)
    print("CYBERGUARD URL PREDICTION TEST")
    print("=" * 70)

    for url in test_urls:

        print("\nURL:")
        print(url)

        result = predict(url)

        print("\nPrediction:")
        print(result["prediction"])

        print("\nRisk:")
        print(
            f"{result['risk_score']} "
            f"({result['risk_level']})"
        )

        print("\nConfidence:")
        print(result["confidence"])

        print("\nPhishing probability:")
        print(result["phishing_probability"])

        print("\nLegitimate probability:")
        print(result["legitimate_probability"])

        print("\nIndicators:")

        for indicator in result["indicators"]:

            print(f"  - {indicator}")

        print("\nTop SHAP features:")

        for item in result["xai"]["top_features"]:

            print(
                f"  {item['feature']:30s} "
                f"value={item['value']:<10} "
                f"SHAP={item['shap_value']:+.6f} "
                f"{item['direction']}"
            )

        print("\nExplanation:")
        print(result["explanation"])

        print("\n" + "-" * 70)