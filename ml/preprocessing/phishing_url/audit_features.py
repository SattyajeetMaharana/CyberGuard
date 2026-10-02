import pandas as pd

RAW_PATH = "ml/datasets/phishing_url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"

df = pd.read_csv(RAW_PATH)

print("=" * 80)
print("PHIUSIIL FEATURE LEAKAGE / INFERENCE AUDIT")
print("=" * 80)

print(f"\nDataset shape: {df.shape}")

print("\nAll features:")

for i, column in enumerate(df.columns, start=1):
    print(f"{i:02d}. {column}")

# Features that can reasonably be derived directly from a URL.
URL_DERIVABLE = {
    "URL",
    "URLLength",
    "Domain",
    "DomainLength",
    "IsDomainIP",
    "TLD",
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
}

# Features that depend on external knowledge,
# webpage fetching, page content, or dataset-specific calculations.
NON_URL_DERIVABLE = {
    "URLSimilarityIndex",
    "CharContinuationRate",
    "TLDLegitimateProb",
    "URLCharProb",
    "LineOfCode",
    "LargestLineLength",
    "HasTitle",
    "Title",
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
}

print("\n" + "=" * 80)
print("URL-DERIVABLE FEATURES")
print("=" * 80)

for feature in sorted(URL_DERIVABLE):
    print(feature)

print(f"\nCount: {len(URL_DERIVABLE)}")

print("\n" + "=" * 80)
print("NON-URL-DERIVABLE / EXTERNAL FEATURES")
print("=" * 80)

for feature in sorted(NON_URL_DERIVABLE):
    print(feature)

print(f"\nCount: {len(NON_URL_DERIVABLE)}")

print("\n" + "=" * 80)
print("FEATURE COVERAGE CHECK")
print("=" * 80)

known_features = URL_DERIVABLE | NON_URL_DERIVABLE | {"label"}

missing = set(df.columns) - known_features
extra = known_features - set(df.columns)

print(f"Unclassified dataset columns: {sorted(missing)}")
print(f"Unknown audit features: {sorted(extra)}")

assert not missing, f"Unclassified columns found: {missing}"

print("\nSUCCESS: Every dataset column has been classified for the audit.")