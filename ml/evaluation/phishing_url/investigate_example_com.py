from pathlib import Path

import joblib
import pandas as pd

from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    extract_url_features,
)

MODEL_PATH = Path(
    "ml/models/trained/phishing_url/url_xgboost_v1.joblib"
)

URL = "https://example.com"


def main():
    print("=" * 70)
    print("CYBERGUARD - EXAMPLE.COM INVESTIGATION")
    print("=" * 70)

    print("\nURL:")
    print(URL)

    # ---------------------------------------------------------
    # 1. Extract features
    # ---------------------------------------------------------
    features = extract_url_features(URL)

    print("\n" + "=" * 70)
    print("EXTRACTED FEATURES")
    print("=" * 70)

    for name in FEATURE_NAMES:
        print(f"{name:30s}: {features[name]}")

    # ---------------------------------------------------------
    # 2. Load model
    # ---------------------------------------------------------
    model = joblib.load(MODEL_PATH)

    X = pd.DataFrame(
        [[float(features[name]) for name in FEATURE_NAMES]],
        columns=FEATURE_NAMES,
    )

    # ---------------------------------------------------------
    # 3. Prediction
    # ---------------------------------------------------------
    probabilities = model.predict_proba(X)[0]

    phishing_probability = float(probabilities[0])
    legitimate_probability = float(probabilities[1])

    print("\n" + "=" * 70)
    print("MODEL PREDICTION")
    print("=" * 70)

    print(f"Phishing probability:    {phishing_probability:.6f}")
    print(f"Legitimate probability: {legitimate_probability:.6f}")

    # ---------------------------------------------------------
    # 4. Feature importance contribution
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("XGBOOST FEATURE IMPORTANCE")
    print("=" * 70)

    importance = model.feature_importances_

    importance_df = pd.DataFrame(
        {
            "feature": FEATURE_NAMES,
            "importance": importance,
            "value": [
                features[name]
                for name in FEATURE_NAMES
            ],
        }
    )

    importance_df = importance_df.sort_values(
        "importance",
        ascending=False,
    )

    print(importance_df.to_string(index=False))

    # ---------------------------------------------------------
    # 5. Compare with training data
    # ---------------------------------------------------------
    train_path = Path(
        "ml/datasets/phishing_url/processed/features/train_features.csv"
    )

    train_df = pd.read_csv(train_path)

    print("\n" + "=" * 70)
    print("COMPARISON WITH TRAINING DATA")
    print("=" * 70)

    rows = []

    for feature in FEATURE_NAMES:
        value = float(features[feature])

        train_min = float(train_df[feature].min())
        train_max = float(train_df[feature].max())
        train_mean = float(train_df[feature].mean())

        inside_range = train_min <= value <= train_max

        rows.append(
            {
                "feature": feature,
                "example_value": value,
                "train_min": train_min,
                "train_mean": train_mean,
                "train_max": train_max,
                "inside_train_range": inside_range,
            }
        )

    comparison_df = pd.DataFrame(rows)

    print(comparison_df.to_string(index=False))

    print("\n" + "=" * 70)
    print("INVESTIGATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()