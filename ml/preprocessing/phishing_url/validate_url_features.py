import pandas as pd

from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    extract_url_features,
)


RAW_PATH = "ml/datasets/phishing_url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"


def main():
    print("=" * 70)
    print("PHIUSIIL URL FEATURE EXTRACTOR VALIDATION")
    print("=" * 70)

    df = pd.read_csv(RAW_PATH)

    # Test a representative sample.
    sample = df.sample(
        n=1000,
        random_state=42,
    )

    print(f"\nRows checked: {len(sample)}")

    results = []

    for _, row in sample.iterrows():
        extracted = extract_url_features(row["URL"])

        for feature in FEATURE_NAMES:
            dataset_value = row[feature]
            extracted_value = extracted[feature]

            results.append(
                {
                    "URL": row["URL"],
                    "feature": feature,
                    "dataset_value": dataset_value,
                    "extracted_value": extracted_value,
                    "match": dataset_value == extracted_value,
                }
            )

    result_df = pd.DataFrame(results)

    print("\nFeature comparison:")
    print("-" * 70)

    for feature in FEATURE_NAMES:
        feature_df = result_df[
            result_df["feature"] == feature
        ]

        matches = feature_df["match"].sum()
        total = len(feature_df)
        accuracy = matches / total * 100

        print(
            f"{feature:30s} "
            f"{matches:4d}/{total:<4d} "
            f"({accuracy:6.2f}% match)"
        )

    print("\nOverall comparison:")

    total_comparisons = len(result_df)
    total_matches = result_df["match"].sum()

    print(
        f"Matching values: "
        f"{total_matches}/{total_comparisons}"
    )

    print(
        f"Overall match rate: "
        f"{total_matches / total_comparisons * 100:.2f}%"
    )

    mismatches = result_df[
        ~result_df["match"]
    ]

    print(
        f"\nTotal mismatches: {len(mismatches)}"
    )

    if len(mismatches) > 0:
        print("\nFirst 30 mismatches:")
        print(
            mismatches.head(30).to_string(index=False)
        )

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()