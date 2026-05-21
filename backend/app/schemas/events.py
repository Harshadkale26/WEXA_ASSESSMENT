from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class IngestionEventIn(BaseModel):
    """Single event payload (validated before JSONB persistence)."""

    event_name: str = Field(min_length=1, max_length=255)
    event_type: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any]
    timestamp: datetime
    source: str = Field(min_length=1, max_length=255)

    @field_validator("event_name", "event_type", "source")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        return v.strip()


class IngestionBatchIn(BaseModel):
    events: list[IngestionEventIn] = Field(min_length=1)


class EventAcceptedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    event_name: str
    event_type: str
    processing_status: str


class BatchIngestionResponse(BaseModel):
    accepted: list[EventAcceptedOut]
    enqueued_tasks: int


class CsvRowError(BaseModel):
    row_number: int
    detail: str


class CsvIngestionResponse(BaseModel):
    accepted: int
    rejected: list[CsvRowError]
    enqueued_tasks: int


class CreateApiKeyRequest(BaseModel):
    name: str = Field(default="default", min_length=1, max_length=120)


class CreateApiKeyResponse(BaseModel):
    """Plaintext key is returned once; store it securely on the client."""

    id: UUID
    api_key: str = Field(description="Use as X-API-Key header value")
    key_prefix: str
    name: str
    webhook_signing_secret: str | None = Field(
        default=None,
        description="Use for X-Webhook-Signature on POST /ingestion/webhooks/events",
    )


class ApiKeyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime
    has_webhook_signing_secret: bool = False


class WebhookIngestionPayload(BaseModel):
    """Webhook receiver body — single event or batch."""

    events: list[IngestionEventIn] | None = None
    event_name: str | None = Field(default=None, min_length=1, max_length=255)
    event_type: str | None = Field(default=None, min_length=1, max_length=120)
    payload: dict[str, Any] | None = None
    timestamp: datetime | None = None
    source: str | None = Field(default=None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def validate_shape(self) -> "WebhookIngestionPayload":
        if self.events:
            return self
        required = [self.event_name, self.event_type, self.payload, self.timestamp, self.source]
        if all(v is not None for v in required):
            return self
        raise ValueError(
            "Provide either 'events' array or all of: event_name, event_type, payload, timestamp, source"
        )

    def to_batch(self) -> IngestionBatchIn:
        if self.events:
            return IngestionBatchIn(events=self.events)
        return IngestionBatchIn(
            events=[
                IngestionEventIn(
                    event_name=self.event_name,  # type: ignore[arg-type]
                    event_type=self.event_type,  # type: ignore[arg-type]
                    payload=self.payload,  # type: ignore[arg-type]
                    timestamp=self.timestamp,  # type: ignore[arg-type]
                    source=self.source,  # type: ignore[arg-type]
                )
            ]
        )
