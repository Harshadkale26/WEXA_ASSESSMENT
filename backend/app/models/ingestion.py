"""Multi-tenant event ingestion: API keys and raw events."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class EventProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


EVENT_STATUS_ENUM = SAEnum(
    EventProcessingStatus,
    name="event_processing_status_enum",
    native_enum=True,
    values_callable=lambda obj: [e.value for e in obj],
)


class OrganizationApiKey(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Server-side hashed API keys for ingestion (never store plaintext)."""

    __tablename__ = "organization_api_keys"
    __table_args__ = (
        UniqueConstraint("key_hash", name="uq_organization_api_keys_key_hash"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="default")
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    webhook_signing_secret: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="Server-side secret for X-Webhook-Signature HMAC verification.",
    )

    organization = relationship(
        "Organization",
        back_populates="api_keys",
        lazy="joined",
    )


class Event(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Ingested event row; async pipeline fills normalized_payload and status."""

    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_organization_id_timestamp", "organization_id", "timestamp"),
        Index("ix_events_organization_id_event_type", "organization_id", "event_type"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    normalized_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    processing_status: Mapped[EventProcessingStatus] = mapped_column(
        EVENT_STATUS_ENUM,
        nullable=False,
        default=EventProcessingStatus.PENDING,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_attempts: Mapped[int] = mapped_column(
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    organization = relationship(
        "Organization",
        back_populates="events",
        lazy="joined",
    )
