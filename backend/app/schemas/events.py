from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
