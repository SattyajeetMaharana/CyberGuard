import pandas as pd

path = "ml/datasets/phishing_url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"

df = pd.read_csv(path)

print("=" * 70)
print("PHIUSIIL DATASET QUALITY CHECK")
print("=" * 70)

print("\nShape:")
print(df.shape)

print("\nLabel distribution:")
print(df["label"].value_counts().sort_index())

print("\nLabel percentages:")
print((df["label"].value_counts(normalize=True).sort_index() * 100).round(2))

print("\nUnique label values:")
print(sorted(df["label"].unique()))

print("\nDuplicate complete rows:")
print(df.duplicated().sum())

print("\nDuplicate URLs:")
print(df["URL"].duplicated().sum())

print("\nUnique URLs:")
print(df["URL"].nunique())

print("\nLabel grouped by URL:")
print(df.groupby("URL")["label"].nunique().value_counts())

print("\nSample label=0:")
print(df[df["label"] == 0][["URL", "label"]].head(10).to_string(index=False))

print("\nSample label=1:")
print(df[df["label"] == 1][["URL", "label"]].head(10).to_string(index=False))
