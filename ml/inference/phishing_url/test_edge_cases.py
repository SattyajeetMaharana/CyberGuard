import pytest

from ml.inference.phishing_url.predict import predict


# ============================================================
# UNICODE URL
# ============================================================

def test_unicode_url():
    url = "https://example.com/café/login"

    result = predict(url)

    assert isinstance(result, dict)
    assert 0 <= result["risk_score"] <= 100


# ============================================================
# URL WITHOUT SCHEME
# ============================================================

def test_url_without_scheme():
    url = "example.com/login"

    result = predict(url)

    assert isinstance(result, dict)
    assert 0 <= result["risk_score"] <= 100


# ============================================================
# UNUSUAL SCHEME
# ============================================================

def test_unusual_scheme():
    url = "ftp://example.com/file.txt"

    result = predict(url)

    assert isinstance(result, dict)
    assert 0 <= result["risk_score"] <= 100


# ============================================================
# OBFUSCATED URL
# ============================================================

def test_obfuscated_url():
    url = "https://example.com/%2Flogin%3Fid%3D123"

    result = predict(url)

    assert isinstance(result, dict)
    assert 0 <= result["risk_score"] <= 100


# ============================================================
# QUERY-HEAVY URL
# ============================================================

def test_query_heavy_url():
    url = (
        "https://example.com/login"
        "?id=123"
        "&user=456"
        "&session=789"
        "&token=abc"
    )

    result = predict(url)

    assert isinstance(result, dict)
    assert 0 <= result["risk_score"] <= 100


# ============================================================
# VERY LONG URL
# ============================================================

def test_very_long_url():
    url = (
        "https://example.com/"
        + "a" * 1000
    )

    result = predict(url)

    assert isinstance(result, dict)
    assert 0 <= result["risk_score"] <= 100


# ============================================================
# EMPTY URL
# ============================================================

def test_empty_url_rejected():
    with pytest.raises(ValueError):
        predict("")


# ============================================================
# WHITESPACE URL
# ============================================================

def test_whitespace_url_rejected():
    with pytest.raises(ValueError):
        predict("   ")


# ============================================================
# NON-STRING URL
# ============================================================

def test_non_string_url_rejected():
    with pytest.raises(TypeError):
        predict(None)


# ============================================================
# NUMERIC URL
# ============================================================

def test_numeric_url_rejected():
    with pytest.raises(TypeError):
        predict(12345)


# ============================================================
# MAIN TEST RUNNER
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("CYBERGUARD - URL EDGE CASE TEST")
    print("=" * 70)

    print("\nRunning edge-case tests...\n")

    exit_code = pytest.main(
        [
            __file__,
            "-v",
        ]
    )

    print("\n" + "=" * 70)

    if exit_code == 0:
        print("ALL EDGE-CASE TESTS PASSED")
    else:
        print("SOME EDGE-CASE TESTS FAILED")

    print("=" * 70)

    raise SystemExit(exit_code)