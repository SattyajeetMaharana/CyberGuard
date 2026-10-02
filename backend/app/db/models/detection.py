from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, Float, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Detection(TimestampMixin, Base):
    __tablename__ = "detections"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    event_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    xai_information: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    indicators: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    recommended_actions: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    detector_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    model_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )