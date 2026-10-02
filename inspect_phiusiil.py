import pandas as pd

path = "ml/datasets/phishing_url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"

df = pd.read_csv(path)

print("=" * 70)
print("PHIUSIIL DATASET INSPECTION")
print("=" * 70)

print("\nShape:")
print(df.shape)

print("\nColumns:")
for i, column in enumerate(df.columns, start=1):
    print(f"{i:02d}. {column}")

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nLabel column candidates:")
for column in df.columns:
    if column.lower() in ["label", "status", "class", "target"]:
        print(f"Found: {column}")

print("\nFirst 5 rows:")
print(df.head().to_string())

print("\nDataset information:")
df.info()
