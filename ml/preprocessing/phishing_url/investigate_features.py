import pandas as pd


RAW_PATH = "ml/datasets/phishing_url/raw/PhiUSIIL_Phishing_URL_Dataset.csv"


def main():
    df = pd.read_csv(RAW_PATH)

    sample = df.sample(
        n=20,
        random_state=42,
    )

    print("=" * 80)
    print("PHIUSIIL FEATURE FORMULA INVESTIGATION")
    print("=" * 80)

    for _, row in sample.iterrows():
        url = row["URL"]

        print("\nURL:")
        print(repr(url))

        print("\nLengths:")
        print("Python len(url):", len(url))
        print("Dataset URLLength:", row["URLLength"])

        print("\nCharacter counts:")
        print("isalpha:", sum(c.isalpha() for c in url))
        print("isascii alpha:", sum(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in url))
        print("isdigit:", sum(c.isdigit() for c in url))
        print("non-alphanumeric:", sum(not c.isalnum() for c in url))

        print("\nDataset:")
        print(
            row[
                [
                    "URLLength",
                    "NoOfLettersInURL",
                    "LetterRatioInURL",
                    "NoOfDegitsInURL",
                    "DegitRatioInURL",
                    "NoOfOtherSpecialCharsInURL",
                    "SpacialCharRatioInURL",
                ]
            ].to_dict()
        )

        print("-" * 80)


if __name__ == "__main__":
    main()