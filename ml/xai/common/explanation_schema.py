"""
Common schema for CyberGuard ML explanations.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class FeatureContribution:
    feature: str
    value: float
    contribution: float


@dataclass
class Explanation:
    method: str
    model_version: str
    prediction: str
    probability_malicious: float
    probability_benign: float
    base_value: float
    feature_contributions: list[FeatureContribution]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
