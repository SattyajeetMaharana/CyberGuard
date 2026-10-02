from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScoreEvent:
    user_id: str
    change: int
    reason: str
    timestamp: datetime


@dataclass
class CyberScore:
    user_id: str
    score: int
    timestamp: datetime