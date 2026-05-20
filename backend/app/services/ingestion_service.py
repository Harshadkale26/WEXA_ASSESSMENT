"""Multi-tenant event ingestion orchestration (API key + rate limit + Celery enqueue)."""

from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app.config import ingestion_queue_name
from app.celery_app.tasks.events import process_event_task
from app.core.config import settings
from app.models.ingestion import Event, EventProcessingStatus
from app.models.ingestion import OrganizationApiKey
from app.repositories.event_repository import EventRepository
from app.repositories.organization_api_key_repository import OrganizationApiKeyRepository
from app.schemas.events import (
    BatchIngestionResponse,
    CsvIngestionResponse,
    CsvRowError,
    EventAcceptedOut,
    IngestionBatchIn,
    IngestionEventIn,
)
from app.services.ingestion_rate_limiter import enforce_ingestion_rate_limit


class IngestionService:
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
        *,
        organization_id: UUID,
        api_key_row: OrganizationApiKey,
    ) -> None:
        self.session = session
        self.redis = redis
        self.organization_id = organization_id
        self.api_key_row = api_key_row
        self.events = EventRepository(session)
        self.api_keys = OrganizationApiKeyRepository(session)

    def _build_event(self, data: IngestionEventIn) -> Event:
        return Event(
            organization_id=self.organization_id,
            event_name=data.event_name,
            event_type=data.event_type,
            payload=data.payload,
            normalized_payload=None,
            timestamp=data.timestamp,
            source=data.source,
            processing_status=EventProcessingStatus.PENDING,
            celery_task_id=None,
            error_message=None,
            processing_attempts=0,
        )

    async def _after_persist_enqueue(self, event: Event) -> None:
        result = process_event_task.apply_async(
            args=[str(event.id)],
            queue=ingestion_queue_name(),
        )
        event.celery_task_id = result.id
        await self.session.flush()

    async def ingest_single(self, data: IngestionEventIn) -> EventAcceptedOut:
        await enforce_ingestion_rate_limit(self.redis, organization_id=self.organization_id)
        event = self._build_event(data)
        await self.events.add(event)
        await self._after_persist_enqueue(event)
        await self.api_keys.touch_last_used(self.api_key_row)
        return EventAcceptedOut.model_validate(event)

    async def ingest_batch(self, data: IngestionBatchIn) -> BatchIngestionResponse:
        if len(data.events) > settings.ingestion_max_batch_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Batch exceeds max size of {settings.ingestion_max_batch_size}",
            )

        await self._enforce_bulk_rate_limit(len(data.events))

        accepted: list[Event] = []
        for item in data.events:
            accepted.append(self._build_event(item))

        await self.events.add_many(accepted)
        for ev in accepted:
            await self._after_persist_enqueue(ev)

        await self.api_keys.touch_last_used(self.api_key_row)

        return BatchIngestionResponse(
            accepted=[EventAcceptedOut.model_validate(e) for e in accepted],
            enqueued_tasks=len(accepted),
        )

    async def ingest_csv(self, upload: UploadFile) -> CsvIngestionResponse:
        raw = await upload.read()
        if len(raw) > settings.ingestion_csv_max_bytes:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="CSV file too large")

        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV has no header row")

        required = {"event_name", "event_type", "timestamp", "source", "payload"}
        fields = {h.strip() for h in reader.fieldnames if h}
        if not required.issubset(fields):
            missing = required - fields
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV missing required columns: {sorted(missing)}",
            )

        rows: list[IngestionEventIn] = []
        errors: list[CsvRowError] = []
        for i, row in enumerate(reader, start=2):
            try:
                payload_raw = row.get("payload", "")
                payload = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
                if not isinstance(payload, dict):
                    raise ValueError("payload must be a JSON object")

                ts_raw = (row.get("timestamp") or "").strip()
                ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))

                rows.append(
                    IngestionEventIn(
                        event_name=row["event_name"],
                        event_type=row["event_type"],
                        timestamp=ts,
                        source=row["source"],
                        payload=payload,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                errors.append(CsvRowError(row_number=i, detail=str(exc)))

        if not rows:
            return CsvIngestionResponse(accepted=0, rejected=errors, enqueued_tasks=0)

        if len(rows) > settings.ingestion_max_batch_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV row count exceeds max batch size {settings.ingestion_max_batch_size}",
            )

        await self._enforce_bulk_rate_limit(len(rows))

        events = [self._build_event(r) for r in rows]
        await self.events.add_many(events)
        for ev in events:
            await self._after_persist_enqueue(ev)
        await self.api_keys.touch_last_used(self.api_key_row)

        return CsvIngestionResponse(
            accepted=len(events),
            rejected=errors,
            enqueued_tasks=len(events),
        )

    async def _enforce_bulk_rate_limit(self, n: int) -> None:
        limit = settings.ingestion_rate_limit_per_minute
        if limit <= 0 or n <= 0:
            return

        minute_bucket = datetime.now(UTC).strftime("%Y%m%d%H%M")
        key = f"ingest:rl:{self.organization_id}:{minute_bucket}"

        new_val = await self.redis.incrby(key, n)
        if new_val == n:
            await self.redis.expire(key, 120)

        if new_val > limit:
            await self.redis.incrby(key, -n)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Organization ingestion rate limit exceeded. Retry after one minute.",
            )
