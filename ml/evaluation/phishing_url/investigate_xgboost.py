from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier

from ml.preprocessing.phishing_url.url_features import FEATURE_NAMES


# ============================================================
# PATHS
# ============================================================

FEATURE_DIR = Path(
    "ml/datasets/phishing_url/processed/features"
)

MODEL_PATH = Path(
    "ml/models/trained/phishing_url/url_xgboost_v1.joblib"
)

TRAIN_PATH = FEATURE_DIR / "train_features.csv"
TEST_PATH = FEATURE_DIR / "test_features.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data(path: Path):
    df = pd.read_csv(path)

    X = df[FEATURE_NAMES]
    y = df["label"]

    return X, y


# ============================================================
# FEATURE / LABEL ASSOCIATION
# ============================================================

def feature_label_analysis(df: pd.DataFrame):

    print("\n" + "=" * 70)
    print("FEATURE / LABEL ANALYSIS")
    print("=" * 70)

    rows = []

    for feature in FEATURE_NAMES:

        phishing_mean = df.loc[
            df["label"] == 0,
            feature
        ].mean()

        legitimate_mean = df.loc[
            df["label"] == 1,
            feature
        ].mean()

        rows.append(
            {
                "feature": feature,
                "phishing_mean": phishing_mean,
                "legitimate_mean": legitimate_mean,
                "absolute_difference": abs(
                    phishing_mean - legitimate_mean
                ),
            }
        )

    result = pd.DataFrame(rows)

    result = result.sort_values(
        "absolute_difference",
        ascending=False,
    )

    print(
        result.to_string(index=False)
    )

    return result


# ============================================================
# SINGLE-FEATURE AUC
# ============================================================

def single_feature_auc(df: pd.DataFrame):

    print("\n" + "=" * 70)
    print("SINGLE-FEATURE ROC-AUC ANALYSIS")
    print("=" * 70)

    results = []

    y = df["label"].to_numpy()

    for feature in FEATURE_NAMES:

        values = df[feature].to_numpy()

        try:
            auc = roc_auc_score(
                y,
                values,
            )

            # A feature can have inverse direction.
            adjusted_auc = max(
                auc,
                1 - auc,
            )

        except ValueError:
            auc = np.nan
            adjusted_auc = np.nan

        results.append(
            {
                "feature": feature,
                "auc": auc,
                "adjusted_auc": adjusted_auc,
            }
        )

    result = pd.DataFrame(results)

    result = result.sort_values(
        "adjusted_auc",
        ascending=False,
    )

    print(
        result.to_string(index=False)
    )

    return result


# ============================================================
# FEATURE DISTRIBUTION
# ============================================================

def feature_distribution(df: pd.DataFrame):

    print("\n" + "=" * 70)
    print("FEATURE DISTRIBUTION CHECK")
    print("=" * 70)

    for feature in FEATURE_NAMES:

        values = df[feature]

        print(f"\n{feature}")

        print(
            f"  min:    {values.min():.6f}"
        )

        print(
            f"  max:    {values.max():.6f}"
        )

        print(
            f"  mean:   {values.mean():.6f}"
        )

        print(
            f"  unique: {values.nunique()}"
        )


# ============================================================
# DECISION-TREE BASELINE
# ============================================================

def decision_tree_baseline(
    X_train,
    y_train,
    X_test,
    y_test,
):

    print("\n" + "=" * 70)
    print("SIMPLE DECISION-TREE BASELINE")
    print("=" * 70)

    model = DecisionTreeClassifier(
        max_depth=3,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    auc = roc_auc_score(
        y_test,
        probabilities,
    )

    accuracy = model.score(
        X_test,
        y_test,
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print(
        f"ROC-AUC:  {auc:.4f}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("CYBERGUARD XGBOOST LEAKAGE INVESTIGATION")
    print("=" * 70)

    print(
        "\nPurpose:"
        "\nInvestigate why the URL-only model achieves"
        "\nvery high test performance."
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    train_df = pd.read_csv(
        TRAIN_PATH
    )

    test_df = pd.read_csv(
        TEST_PATH
    )

    X_train = train_df[FEATURE_NAMES]
    y_train = train_df["label"]

    X_test = test_df[FEATURE_NAMES]
    y_test = test_df["label"]

    print(
        f"\nTrain rows: {len(train_df)}"
    )

    print(
        f"Test rows:  {len(test_df)}"
    )

    # --------------------------------------------------------
    # 1. Feature-label analysis
    # --------------------------------------------------------

    feature_label_analysis(
        train_df
    )

    # --------------------------------------------------------
    # 2. Single-feature AUC
    # --------------------------------------------------------

    single_feature_auc(
        train_df
    )

    # --------------------------------------------------------
    # 3. Distribution analysis
    # --------------------------------------------------------

    feature_distribution(
        train_df
    )

    # --------------------------------------------------------
    # 4. Simple baseline
    # --------------------------------------------------------

    decision_tree_baseline(
        X_train,
        y_train,
        X_test,
        y_test,
    )

    # --------------------------------------------------------
    # 5. XGBoost importance
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("SAVED XGBOOST FEATURE IMPORTANCE")
    print("=" * 70)

    model = joblib.load(
        MODEL_PATH
    )

    importance = pd.DataFrame(
        {
            "feature": FEATURE_NAMES,
            "importance": model.feature_importances_,
        }
    ).sort_values(
        "importance",
        ascending=False,
    )

    print(
        importance.to_string(index=False)
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LEAKAGE INVESTIGATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()