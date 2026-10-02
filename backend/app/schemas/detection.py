from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class DetectionCreate(BaseModel):
    event_id: UUID

    category: str = Field(..., min_length=1, max_length=100)
    risk_level: str = Field(..., min_length=1, max_length=50)

    risk_score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)

    xai_information: dict | None = None
    indicators: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)

    status: str = Field(..., min_length=1, max_length=50)

    detector_version: str | None = Field(
        default=None,
        max_length=50,
    )

    model_version: str | None = Field(
        default=None,
        max_length=50,
    )


class DetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    detection_id: UUID
    event_id: UUID

    category: str
    risk_level: str

    risk_score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)

    xai_information: dict | None = None
    indicators: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)

    status: str

    detector_version: str | None = None
    model_version: str | None = None