import pandas as pd
import numpy as np

RAW_PATH = "ml/datasets/phishing_url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"

df = pd.read_csv(RAW_PATH)

print("=" * 80)
print("PHIUSIIL FEATURE LEAKAGE ANALYSIS")
print("=" * 80)

# Features that can be calculated directly from a URL.
URL_FEATURES = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
]

EXTERNAL_FEATURES = [
    "URLSimilarityIndex",
    "CharContinuationRate",
    "TLDLegitimateProb",
    "URLCharProb",
    "LineOfCode",
    "LargestLineLength",
    "HasTitle",
    "DomainTitleMatchScore",
    "URLTitleMatchScore",
    "HasFavicon",
    "Robots",
    "IsResponsive",
    "NoOfURLRedirect",
    "NoOfSelfRedirect",
    "HasDescription",
    "NoOfPopup",
    "NoOfiFrame",
    "HasExternalFormSubmit",
    "HasSocialNet",
    "HasSubmitButton",
    "HasHiddenFields",
    "HasPasswordField",
    "Bank",
    "Pay",
    "Crypto",
    "HasCopyrightInfo",
    "NoOfImage",
    "NoOfCSS",
    "NoOfJS",
    "NoOfSelfRef",
    "NoOfEmptyRef",
    "NoOfExternalRef",
]

print("\nDataset shape:")
print(df.shape)

print("\n" + "=" * 80)
print("LABEL MEANS")
print("=" * 80)

for label in sorted(df["label"].unique()):
    subset = df[df["label"] == label]
    print(f"\nLabel {label}: {len(subset)} rows")

print("\n" + "=" * 80)
print("FEATURE-LEVEL LABEL ASSOCIATION")
print("=" * 80)

numeric_features = [
    col for col in URL_FEATURES + EXTERNAL_FEATURES
    if col in df.columns and pd.api.types.is_numeric_dtype(df[col])
]

results = []

for feature in numeric_features:
    group = df.groupby("label")[feature].mean()

    mean_0 = group.get(0, np.nan)
    mean_1 = group.get(1, np.nan)

    if mean_0 == 0:
        difference_pct = np.nan
    else:
        difference_pct = abs(mean_1 - mean_0) / abs(mean_0) * 100

    results.append(
        (
            feature,
            mean_0,
            mean_1,
            difference_pct,
        )
    )

results.sort(key=lambda x: (
    -1 if pd.isna(x[3]) else -x[3]
))

print(
    f"{'Feature':35} "
    f"{'Label 0 Mean':>15} "
    f"{'Label 1 Mean':>15} "
    f"{'Difference %':>15}"
)

for feature, mean_0, mean_1, difference_pct in results:
    print(
        f"{feature:35} "
        f"{mean_0:15.4f} "
        f"{mean_1:15.4f} "
        f"{difference_pct:15.2f}"
    )

print("\n" + "=" * 80)
print("URL FEATURE SUMMARY")
print("=" * 80)

for feature in URL_FEATURES:
    if feature in df.columns:
        print(
            f"{feature:35} "
            f"unique={df[feature].nunique():6} "
            f"missing={df[feature].isna().sum():6}"
        )

print("\n" + "=" * 80)
print("EXTERNAL FEATURE SUMMARY")
print("=" * 80)

for feature in EXTERNAL_FEATURES:
    if feature in df.columns:
        print(
            f"{feature:35} "
            f"unique={df[feature].nunique():6} "
            f"missing={df[feature].isna().sum():6}"
        )

print("\n" + "=" * 80)
print("SUSPICIOUSLY DISCRIMINATIVE FEATURES")
print("=" * 80)

# Print features with very large difference between class means.
for feature, mean_0, mean_1, difference_pct in results:
    if not pd.isna(difference_pct) and difference_pct >= 100:
        print(
            f"{feature}: "
            f"label0={mean_0:.4f}, "
            f"label1={mean_1:.4f}, "
            f"difference={difference_pct:.2f}%"
        )

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)