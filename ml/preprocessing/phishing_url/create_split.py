import pandas as pd
from sklearn.model_selection import train_test_split

RAW_PATH = "ml/datasets/phishing_url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"
OUTPUT_DIR = "ml/datasets/phishing_url/processed"

df = pd.read_csv(RAW_PATH)

print("=" * 70)
print("PHIUSIIL LEAKAGE-SAFE DATASET SPLIT")
print("=" * 70)

print(f"\nOriginal rows: {len(df)}")

# Remove duplicate URLs.
# The quality check confirmed that duplicate URLs do not have conflicting labels.
df = df.drop_duplicates(subset=["URL"], keep="first").reset_index(drop=True)

print(f"Rows after URL deduplication: {len(df)}")

# First split:
# 70% train
# 30% temporary
train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    stratify=df["label"],
    random_state=42,
)

# Split temporary 50/50:
# 15% validation
# 15% test
val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    stratify=temp_df["label"],
    random_state=42,
)

print("\nSplit sizes:")
print(f"Train:      {len(train_df)}")
print(f"Validation: {len(val_df)}")
print(f"Test:       {len(test_df)}")

print("\nSplit percentages:")
total = len(df)
print(f"Train:      {len(train_df) / total * 100:.2f}%")
print(f"Validation: {len(val_df) / total * 100:.2f}%")
print(f"Test:       {len(test_df) / total * 100:.2f}%")

print("\nLabel distribution:")
print("\nTrain:")
print(train_df["label"].value_counts(normalize=True).sort_index().round(4))

print("\nValidation:")
print(val_df["label"].value_counts(normalize=True).sort_index().round(4))

print("\nTest:")
print(test_df["label"].value_counts(normalize=True).sort_index().round(4))

# Verify no URL leakage between splits.
train_urls = set(train_df["URL"])
val_urls = set(val_df["URL"])
test_urls = set(test_df["URL"])

print("\nURL leakage check:")
print(f"Train n Validation: {len(train_urls & val_urls)}")
print(f"Train n Test:       {len(train_urls & test_urls)}")
print(f"Validation n Test:  {len(val_urls & test_urls)}")

assert len(train_urls & val_urls) == 0
assert len(train_urls & test_urls) == 0
assert len(val_urls & test_urls) == 0

# Save processed splits.
train_df.to_csv(f"{OUTPUT_DIR}/train.csv", index=False)
val_df.to_csv(f"{OUTPUT_DIR}/validation.csv", index=False)
test_df.to_csv(f"{OUTPUT_DIR}/test.csv", index=False)

print("\nSaved:")
print(f"{OUTPUT_DIR}/train.csv")
print(f"{OUTPUT_DIR}/validation.csv")
print(f"{OUTPUT_DIR}/test.csv")

print("\nSUCCESS: Leakage-safe 70/15/15 split created.")
