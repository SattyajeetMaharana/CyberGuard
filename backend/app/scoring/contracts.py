from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ScoreEvent:
    user_id: str
    previous_score: int
    delta: int
    new_score: int
    event: str
    timestamp: datetime

    @property
    def change(self) -> int:
        return self.delta

    @property
    def reason(self) -> str:
        return self.event


@dataclass(frozen=True)
class CyberScore:
    user_id: str
    score: int
    timestamp: datetime