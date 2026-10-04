from ml.common.detection import Detection
from ml.common.risk import risk_level_from_score
from ml.inference.account_takeover.predictor import AccountTakeoverPredictor
from ml.xai.account_takeover.explainer import AccountTakeoverSHAPExplainer


class AccountTakeoverDetector:
    """Production-facing detector wrapping the ATO model."""

    category = "account_takeover"

    def __init__(self):
        self.predictor = AccountTakeoverPredictor()
        self.explainer = AccountTakeoverSHAPExplainer()

    def analyze(self, event: dict) -> Detection:
        if not isinstance(event, dict):
            raise TypeError("event must be a dictionary")

        history = event.get("history", [])

        if not isinstance(history, list):
            raise TypeError("event 'history' must be a list")

        result = self.predictor.analyze(
            event,
            history,
        )

        probability = result.risk_score / 100.0
        risk_score = result.risk_score
        risk_level = risk_level_from_score(risk_score)

        features = self.predictor._build_features(
            event,
            history,
        )

        feature_dict = features.iloc[0].to_dict()

        shap_explanation = self.explainer.explain(
            feature_dict,
            top_k=5,
        )

        indicators = self._build_indicators(
            feature_dict,
            probability,
        )

        explanation = self._build_explanation(
            result,
            shap_explanation,
        )

        recommended_actions = self._recommended_actions(
            result.prediction,
            risk_level.value,
        )

        return Detection(
            category=self.category,
            prediction=result.prediction,
            risk_score=risk_score,
            risk_level=risk_level.value,
            confidence=result.confidence,
            indicators=indicators,
            explanation=explanation,
            recommended_actions=recommended_actions,
            model_version=result.model_version,
        )

    @staticmethod
    def _build_indicators(
        features: dict,
        probability: float,
    ) -> list[str]:
        indicators = []

        if features.get("is_new_country") == 1:
            indicators.append(
                "Login originated from a new country"
            )

        if features.get("is_new_region") == 1:
            indicators.append(
                "Login originated from a new region"
            )

        if features.get("is_new_city") == 1:
            indicators.append(
                "Login originated from a new city"
            )

        if features.get("is_new_asn") == 1:
            indicators.append(
                "Login originated from a new ASN"
            )

        if features.get("is_new_browser") == 1:
            indicators.append(
                "Login used a new browser"
            )

        if features.get("is_new_os") == 1:
            indicators.append(
                "Login used a new operating system"
            )

        if features.get("is_new_device") == 1:
            indicators.append(
                "Login used a new device"
            )

        if features.get("is_outside_hours") == 1:
            indicators.append(
                "Login occurred outside normal hours"
            )

        if features.get("user_failure_rate", 0.0) > 0.5:
            indicators.append(
                "User has a high recent login failure rate"
            )

        # -1 means there is no previous login.
        # Only report rapid-login behavior when an actual
        # previous login exists.
        time_since_previous_login = features.get(
            "time_since_previous_login_seconds",
            -1.0,
        )

        if 0 <= time_since_previous_login < 300:
            indicators.append(
                "Login occurred shortly after the previous login"
            )

        if probability >= 0.5:
            indicators.append(
                "Model probability meets or exceeds the ATO operating threshold"
            )

        if not indicators:
            indicators.append(
                "No strong account takeover behavioral indicators detected"
            )

        return indicators

    @staticmethod
    def _build_explanation(
        result: Detection,
        shap_explanation: dict,
    ) -> str:
        parts = [
            f"Model predicted {result.prediction} "
            f"with {result.risk_score / 100.0:.2%} "
            f"account takeover probability."
        ]

        top_features = shap_explanation.get(
            "top_features",
            [],
        )

        feature_values = shap_explanation.get(
            "feature_values",
            {},
        )

        contributions = shap_explanation.get(
            "contributions",
            {},
        )

        if top_features:
            feature_text = ", ".join(
                f"{feature}={feature_values[feature]} "
                f"(contribution {contributions[feature]:+.3f})"
                for feature in top_features
            )

            parts.append(
                f"Top SHAP contributors were: {feature_text}."
            )

        return " ".join(parts)

    @staticmethod
    def _recommended_actions(
        prediction: str,
        risk_level: str,
    ) -> list[str]:
        if prediction == "ACCOUNT_TAKEOVER":
            if risk_level == "CRITICAL":
                return [
                    "Block the login",
                    "Require strong step-up authentication",
                    "Review recent account activity",
                    "Verify the user's identity",
                ]

            if risk_level in {"HIGH", "MEDIUM"}:
                return [
                    "Require step-up authentication",
                    "Review recent account activity",
                    "Verify the user's identity",
                ]

            return [
                "Apply additional login verification",
                "Continue monitoring account activity",
            ]

        return [
            "Allow normal login processing",
            "Continue monitoring account activity",
        ]