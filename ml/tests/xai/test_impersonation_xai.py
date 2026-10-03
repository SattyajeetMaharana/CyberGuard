from ml.xai.impersonation.shap_explainer import ImpersonationSHAPExplainer


BENIGN_FEATURES = {
    "urgency_level": 1,
    "requests_wire_transfer": 0,
    "requests_gift_cards": 0,
    "requests_sensitive_data": 0,
    "dkim_pass": 1,
    "spf_pass": 1,
    "dmarc_pass": 1,
    "reply_to_mismatch": 0,
    "is_end_of_month": 0,
    "is_friday": 0,
    "sent_outside_hours": 0,
    "requested_amount_usd": 0,
    "auth_failure": 0,
    "partial_auth": 0,
    "full_auth_bypass": 0,
    "payroll_timing": 0,
    "weekend_timing": 0,
    "after_hours": 0,
}


IMPERSONATION_FEATURES = {
    "urgency_level": 5,
    "requests_wire_transfer": 1,
    "requests_gift_cards": 0,
    "requests_sensitive_data": 1,
    "dkim_pass": 0,
    "spf_pass": 0,
    "dmarc_pass": 0,
    "reply_to_mismatch": 1,
    "is_end_of_month": 0,
    "is_friday": 0,
    "sent_outside_hours": 1,
    "requested_amount_usd": 250000,
    "auth_failure": 1,
    "partial_auth": 0,
    "full_auth_bypass": 1,
    "payroll_timing": 0,
    "weekend_timing": 0,
    "after_hours": 1,
}


def test_benign_xai_explanation():
    explainer = ImpersonationSHAPExplainer()

    result = explainer.explain(BENIGN_FEATURES)

    assert result["method"] == "SHAP TreeExplainer"
    assert result["model_version"] == "impersonation-xgboost-v1"
    assert result["prediction"] == "benign"
    assert 0 <= result["probability_impersonation"] <= 1

    assert len(result["top_features"]) == 5
    assert len(result["feature_values"]) == 5
    assert len(result["contributions"]) == 5

    assert "human_readable_explanation" in result
    assert "toward impersonation" in result["human_readable_explanation"]


def test_impersonation_xai_explanation():
    explainer = ImpersonationSHAPExplainer()

    result = explainer.explain(IMPERSONATION_FEATURES)

    assert result["method"] == "SHAP TreeExplainer"
    assert result["model_version"] == "impersonation-xgboost-v1"
    assert result["prediction"] == "impersonation"
    assert result["probability_impersonation"] > 0.5

    assert len(result["top_features"]) == 5
    assert len(result["feature_values"]) == 5
    assert len(result["contributions"]) == 5

    assert "human_readable_explanation" in result
    assert "toward impersonation" in result["human_readable_explanation"]


def test_missing_feature_rejected():
    explainer = ImpersonationSHAPExplainer()

    incomplete = dict(BENIGN_FEATURES)
    incomplete.pop("dkim_pass")

    try:
        explainer.explain(incomplete)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Missing required features" in str(exc)


def test_invalid_features_type_rejected():
    explainer = ImpersonationSHAPExplainer()

    try:
        explainer.explain([])
        assert False, "Expected TypeError"
    except TypeError as exc:
        assert "features must be a dictionary" in str(exc)