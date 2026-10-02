from pathlib import Path

import pandas as pd

from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    extract_url_features,
)


TRAIN_PATH = Path(
    "ml/datasets/phishing_url/processed/features/train_features.csv"
)


TARGET_URLS = [
    "https://example.com",
    "https://google.com",
]


def main():
    print("=" * 70)
    print("CYBERGUARD - BENIGN URL NEIGHBOR INVESTIGATION")
    print("=" * 70)

    df = pd.read_csv(TRAIN_PATH)

    print(f"\nTraining rows: {len(df)}")

    # ---------------------------------------------------------
    # 1. Search exact domains
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("EXACT DOMAIN SEARCH")
    print("=" * 70)

    for url in TARGET_URLS:
        domain = url.split("://", 1)[1].split("/", 1)[0]

        matches = df[
            df["URL"].astype(str).str.contains(
                domain,
                case=False,
                regex=False,
            )
        ]

        print(f"\nSearch: {domain}")
        print(f"Matches: {len(matches)}")

        if len(matches) > 0:
            print(
                matches[
                    ["URL", "label"] + FEATURE_NAMES
                ].head(20).to_string(index=False)
            )

    # ---------------------------------------------------------
    # 2. Find short HTTPS benign URLs
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("SHORT HTTPS BENIGN URLS")
    print("=" * 70)

    benign = df[df["label"] == 1].copy()

    short_https = benign[
        (benign["IsHTTPS"] == 1)
        & (benign["URLLength"] <= 25)
        & (benign["NoOfDegitsInURL"] == 0)
        & (benign["NoOfSubDomain"] <= 1)
    ].copy()

    print(f"Matching benign URLs: {len(short_https)}")

    if len(short_https) > 0:
        print(
            short_https[
                [
                    "URL",
                    "URLLength",
                    "DomainLength",
                    "NoOfSubDomain",
                    "NoOfDegitsInURL",
                    "IsHTTPS",
                    "label",
                ]
            ]
            .head(50)
            .to_string(index=False)
        )

    # ---------------------------------------------------------
    # 3. Feature vector similar to example.com
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("FEATURE PROFILE")
    print("=" * 70)

    example_features = extract_url_features(
        "https://example.com"
    )

    for feature in FEATURE_NAMES:
        print(
            f"{feature:30s}: "
            f"{example_features[feature]}"
        )

    # ---------------------------------------------------------
    # 4. Compare benign feature means
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("EXAMPLE.COM VS BENIGN MEANS")
    print("=" * 70)

    comparison = []

    for feature in FEATURE_NAMES:
        comparison.append(
            {
                "feature": feature,
                "example_com": example_features[feature],
                "benign_mean": benign[feature].mean(),
            }
        )

    comparison_df = pd.DataFrame(comparison)

    print(comparison_df.to_string(index=False))

    print("\n" + "=" * 70)
    print("INVESTIGATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()