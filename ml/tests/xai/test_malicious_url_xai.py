"""Tests for malicious URL SHAP explanations."""

from ml.xai.malicious_url.shap_explainer import (
    MaliciousURLSHAPExplainer,
)


def test_malicious_url_shap_explanation():
    explainer = MaliciousURLSHAPExplainer()

    explanation = explainer.explain(
        "http://192.168.1.1/login?verify=123456"
    )

    assert explanation.method == "SHAP TreeExplainer"
    assert explanation.model_version == "malicious-url-xgboost-v1"
    assert explanation.prediction == "malicious"
    assert 0.0 <= explanation.probability_malicious <= 1.0
    assert 0.0 <= explanation.probability_benign <= 1.0
    assert len(explanation.feature_contributions) == 18


def test_malicious_url_shap_contains_expected_features():
    explainer = MaliciousURLSHAPExplainer()

    explanation = explainer.explain(
        "https://www.google.com"
    )

    feature_names = {
        contribution.feature
        for contribution in explanation.feature_contributions
    }

    assert "URLLength" in feature_names
    assert "DomainLength" in feature_names
    assert "IsHTTPS" in feature_names
    assert "NoOfDegitsInURL" in feature_names
