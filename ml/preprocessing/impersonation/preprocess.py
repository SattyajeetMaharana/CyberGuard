from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


RAW_PATH = Path(
    "ml/datasets/impersonation/raw/africa_bec/"
    "business_email_compromise_dataset.csv"
)

OUTPUT_DIR = Path("ml/datasets/impersonation/processed")


FEATURES = [
    "urgency_level",
    "requests_wire_transfer",
    "requests_gift_cards",
    "requests_sensitive_data",
    "dkim_pass",
    "spf_pass",
    "dmarc_pass",
    "reply_to_mismatch",
    "is_end_of_month",
    "is_friday",
    "sent_outside_hours",
    "requested_amount_usd",
    "auth_failure",
    "partial_auth",
    "full_auth_bypass",
    "payroll_timing",
    "weekend_timing",
    "after_hours",
]


TARGET = "label"


def main() -> None:
    df = pd.read_csv(RAW_PATH)

    required = FEATURES + [TARGET]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data = df[required].copy()

    if data.isnull().any().any():
        raise ValueError("Missing values detected in selected features.")

    X = data[FEATURES]
    y = data[TARGET].astype(int)

    # 70% train, 15% validation, 15% test.
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        stratify=y,
        random_state=42,
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=42,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pd.concat([X_train, y_train], axis=1).to_csv(
        OUTPUT_DIR / "train.csv",
        index=False,
    )

    pd.concat([X_val, y_val], axis=1).to_csv(
        OUTPUT_DIR / "validation.csv",
        index=False,
    )

    pd.concat([X_test, y_test], axis=1).to_csv(
        OUTPUT_DIR / "test.csv",
        index=False,
    )

    print("=== IMPERSONATION PREPROCESSING ===")
    print("Features:", len(FEATURES))
    print("Train:", X_train.shape)
    print("Validation:", X_val.shape)
    print("Test:", X_test.shape)

    print("\nLabel distribution:")

    print("Train:")
    print(y_train.value_counts().sort_index())

    print("Validation:")
    print(y_val.value_counts().sort_index())

    print("Test:")
    print(y_test.value_counts().sort_index())

    print("\nSaved:")
    print(OUTPUT_DIR / "train.csv")
    print(OUTPUT_DIR / "validation.csv")
    print(OUTPUT_DIR / "test.csv")


if __name__ == "__main__":
    main()