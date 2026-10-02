from ucimlrepo import fetch_ucirepo

dataset = fetch_ucirepo(id=967)

output_path = "ml/datasets/phishing_url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"

dataset.data.features.join(dataset.data.targets).to_csv(
    output_path,
    index=False
)

print(f"Saved dataset to: {output_path}")
print(f"Rows: {len(dataset.data.features)}")
print(f"Columns: {len(dataset.data.features.columns)}")
