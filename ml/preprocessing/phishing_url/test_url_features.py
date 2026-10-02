from ml.preprocessing.phishing_url.url_features import (
    FEATURE_NAMES,
    FEATURE_VERSION,
    extract_feature_vector,
    extract_url_features,
)


def test_normal_url():
    features = extract_url_features(
        "https://www.example.com/login"
    )

    assert len(features) == 18
    assert features["IsHTTPS"] == 1
    assert features["IsDomainIP"] == 0


def test_ip_address_url():
    features = extract_url_features(
        "http://192.168.1.10/login"
    )

    assert features["IsDomainIP"] == 1


def test_query_url():
    features = extract_url_features(
        "https://example.com/login?id=123&user=test"
    )

    assert features["NoOfQMarkInURL"] == 1
    assert features["NoOfEqualsInURL"] == 2
    assert features["NoOfAmpersandInURL"] == 1


def test_obfuscated_url():
    features = extract_url_features(
        "https://example.com/%2Flogin%20test"
    )

    assert features["HasObfuscation"] == 1
    assert features["NoOfObfuscatedChar"] == 2


def test_long_url():
    url = "https://example.com/" + ("a" * 2000)

    features = extract_url_features(url)

    assert features["URLLength"] > 2000


def test_unicode_url():
    features = extract_url_features(
        "https://example.com/लॉगिन"
    )

    assert features["URLLength"] > 0


def test_unusual_scheme():
    features = extract_url_features(
        "ftp://example.com/file.txt"
    )

    assert features["IsHTTPS"] == 0


def test_no_scheme_url():
    features = extract_url_features(
        "example.com/login"
    )

    assert features["DomainLength"] == 11
    assert features["IsDomainIP"] == 0


def test_empty_url():
    try:
        extract_url_features("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_non_string_url():
    try:
        extract_url_features(None)
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_feature_vector_order():
    vector = extract_feature_vector(
        "https://example.com"
    )

    assert len(vector) == len(FEATURE_NAMES)
    assert all(isinstance(value, float) for value in vector)


def test_feature_version():
    assert FEATURE_VERSION == "cyberguard-url-v1"


if __name__ == "__main__":
    print("=" * 70)
    print("CYBERGUARD URL FEATURE EXTRACTOR TEST")
    print("=" * 70)

    test_normal_url()
    test_ip_address_url()
    test_query_url()
    test_obfuscated_url()
    test_long_url()
    test_unicode_url()
    test_unusual_scheme()
    test_no_scheme_url()
    test_empty_url()
    test_non_string_url()
    test_feature_vector_order()
    test_feature_version()

    print("\nALL URL FEATURE TESTS PASSED")