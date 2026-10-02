from ml.inference.phishing_url.predict import predict


TEST_URLS = [
    "https://example.com",
    "https://www.ozzy.com",
    "https://www.itkf.org",
    "https://www.ihc.hr",
    "https://www.quebec.ca",
    "https://www.xfce.org",
    "https://www.twu.ca",
    "https://www.id.me",
    "https://www.ciscolive.com",
]


def main():
    print("=" * 80)
    print("CYBERGUARD - BENIGN URL GENERALIZATION TEST")
    print("=" * 80)

    for url in TEST_URLS:
        result = predict(url)

        print("\nURL:", url)
        print("Prediction:", result["prediction"])
        print("Phishing probability:", result["phishing_probability"])
        print("Legitimate probability:", result["legitimate_probability"])
        print("Risk score:", result["risk_score"])
        print("Risk level:", result["risk_level"])


if __name__ == "__main__":
    main()