import pandas as pd
import shap
import joblib

from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    extract_url_features,
)


MODEL_PATH = (
    "ml/models/trained/phishing_url/url_xgboost_v1.joblib"
)


def test_url(url):
    print("\n" + "=" * 70)
    print("URL:", url)
    print("=" * 70)

    model = joblib.load(MODEL_PATH)

    features = extract_url_features(url)

    X = pd.DataFrame(
        [[float(features[name]) for name in FEATURE_NAMES]],
        columns=FEATURE_NAMES,
    )

    probabilities = model.predict_proba(X)[0]

    print("\nMODEL PROBABILITIES")
    print("Phishing:   ", probabilities[0])
    print("Legitimate: ", probabilities[1])

    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X)

    print("\nSHAP OUTPUT TYPE:")
    print(type(shap_values))

    print("\nSHAP OUTPUT SHAPE:")
    print(getattr(shap_values, "shape", "no shape"))

    print("\nSHAP EXPECTED VALUE:")
    print(explainer.expected_value)

    print("\nRAW SHAP OUTPUT:")
    print(shap_values)

    # ---------------------------------------------------------
    # Validate feature count
    # ---------------------------------------------------------
    if hasattr(shap_values, "shape"):

        if len(shap_values.shape) != 2:
            raise AssertionError(
                f"Expected 2D SHAP array, got {shap_values.shape}"
            )

        if shap_values.shape[1] != len(FEATURE_NAMES):
            raise AssertionError(
                "SHAP feature count does not match "
                "model feature count"
            )

    print("\nFEATURE COUNT:")
    print("Model features:", len(FEATURE_NAMES))

    if hasattr(shap_values, "shape"):
        print("SHAP features:", shap_values.shape[1])

    # ---------------------------------------------------------
    # Feature contributions
    # ---------------------------------------------------------
    if isinstance(shap_values, list):
        values = shap_values[0][0]
    else:
        values = shap_values[0]

    print("\nFEATURE CONTRIBUTIONS")

    rows = []

    for feature, value, shap_value in zip(
        FEATURE_NAMES,
        X.iloc[0].tolist(),
        values,
    ):
        rows.append(
            {
                "feature": feature,
                "value": value,
                "shap_value": float(shap_value),
            }
        )

    result = pd.DataFrame(rows)

    result["abs_shap"] = result["shap_value"].abs()

    result = result.sort_values(
        "abs_shap",
        ascending=False,
    )

    print(result.to_string(index=False))


def main():

    urls = [
        "https://www.google.com",
        "https://example.com",
        "http://192.168.1.10/login",
    ]

    for url in urls:
        test_url(url)

    print("\n" + "=" * 70)
    print("SHAP VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()