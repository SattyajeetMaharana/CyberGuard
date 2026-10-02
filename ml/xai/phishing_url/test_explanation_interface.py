from ml.xai.phishing_url.shap_explainer import explain_url


def main():
    url = "https://example.com"

    result = explain_url(url, top_k=5)

    print("=" * 70)
    print("CYBERGUARD - XAI INTERFACE TEST")
    print("=" * 70)

    print("\nURL:")
    print(result["url"])

    print("\nModel:")
    print(result["model_version"])

    print("\nPhishing probability:")
    print(result["phishing_probability"])

    print("\nLegitimate probability:")
    print(result["legitimate_probability"])

    print("\nTop SHAP features:")

    for item in result["top_features"]:
        print(
            f"  {item['feature']:30s} "
            f"value={item['value']:<10} "
            f"SHAP={item['shap_value']:+.6f} "
            f"{item['direction']}"
        )

    print("\n" + "=" * 70)
    print("XAI INTERFACE TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()