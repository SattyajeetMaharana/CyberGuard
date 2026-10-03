from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class URLAnalysisRequest(BaseModel):
    url: HttpUrl
    device_id: UUID | None = None


class AnalysisResponse(BaseModel):
    event_id: UUID
    detection_id: UUID
    category: str
    prediction: str
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str
    confidence: float = Field(..., ge=0, le=1)
    indicators: list[str] = Field(default_factory=list)
    explanation: str = ""
    recommended_actions: list[str] = Field(default_factory=list)
    incident: dict | None = None
    cyber_score: int | None = None
    recommended_action: str | None = None
