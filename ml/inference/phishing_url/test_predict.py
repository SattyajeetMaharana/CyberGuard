from ml.inference.phishing_url.predict import predict
from ml.preprocessing.phishing_url.url_features import FEATURE_NAMES


def test_predict_returns_detection_object():
    result = predict("https://www.google.com")

    required_keys = {
        "category",
        "prediction",
        "risk_score",
        "risk_level",
        "confidence",
        "indicators",
        "explanation",
        "recommended_actions",
        "model_version",
        "feature_version",
        "phishing_probability",
        "legitimate_probability",
        "xai",
    }

    assert required_keys.issubset(result.keys())


def test_prediction_values_are_valid():
    result = predict("https://www.google.com")

    assert result["prediction"] in {
        "malicious",
        "benign",
    }

    assert 0 <= result["risk_score"] <= 100

    assert 0 <= result["confidence"] <= 1

    assert 0 <= result["phishing_probability"] <= 1

    assert 0 <= result["legitimate_probability"] <= 1

    assert (
        abs(
            result["phishing_probability"]
            + result["legitimate_probability"]
            - 1.0
        )
        < 1e-6
    )


def test_risk_level_is_valid():
    result = predict("https://www.google.com")

    assert result["risk_level"] in {
        "SAFE",
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }


def test_model_metadata():
    result = predict("https://www.google.com")

    assert result["category"] == "phishing_url"

    assert result["model_version"] == "url-xgb-v1"

    assert (
        result["feature_version"]
        == "cyberguard-url-v1"
    )


def test_xai_exists():
    result = predict("https://www.google.com")

    xai = result["xai"]

    assert xai["method"] == "SHAP"

    assert "top_features" in xai

    assert "all_features" in xai

    assert len(xai["top_features"]) == 5

    assert len(xai["all_features"]) == len(
        FEATURE_NAMES
    )


def test_xai_features_match_model_features():
    result = predict("https://www.google.com")

    explained_features = {
        item["feature"]
        for item in result["xai"]["all_features"]
    }

    assert explained_features == set(
        FEATURE_NAMES
    )


def test_xai_directions_are_valid():
    result = predict("https://www.google.com")

    valid_directions = {
        "increases_phishing_risk",
        "decreases_phishing_risk",
        "neutral",
    }

    for item in result["xai"]["all_features"]:

        assert item["direction"] in valid_directions

        assert isinstance(
            item["shap_value"],
            float,
        )


def test_malicious_url_returns_high_risk():
    result = predict(
        "http://192.168.1.10/login"
    )

    assert result["prediction"] == "malicious"

    assert result["risk_score"] >= 80

    assert result["risk_level"] == "CRITICAL"


def test_benign_url_sanity_check():
    result = predict(
        "https://www.google.com"
    )

    assert result["prediction"] == "benign"

    assert result["risk_level"] == "SAFE"


def test_edge_case_long_url():
    url = (
        "https://example.com/"
        + "a" * 200
    )

    result = predict(url)

    assert isinstance(result, dict)

    assert 0 <= result["risk_score"] <= 100


def test_query_parameter_url():
    result = predict(
        "https://www.example.com/login?id=123"
    )

    assert isinstance(result, dict)

    assert "URL contains query parameters" in (
        result["indicators"]
    )


def test_ip_based_url():
    result = predict(
        "http://192.168.1.10/login"
    )

    assert (
        "URL uses an IP address instead of a domain name"
        in result["indicators"]
    )


if __name__ == "__main__":
    print("=" * 70)
    print("CYBERGUARD - PREDICTION + XAI TEST")
    print("=" * 70)

    print("\nRunning automated tests...\n")

    import pytest

    exit_code = pytest.main(
        [
            __file__,
            "-v",
        ]
    )

    print("\n" + "=" * 70)

    if exit_code == 0:
        print("ALL PREDICTION + XAI TESTS PASSED")
    else:
        print("SOME TESTS FAILED")

    print("=" * 70)

    raise SystemExit(exit_code)