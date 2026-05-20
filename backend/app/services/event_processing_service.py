"""Background processing for ingested events (Celery worker entrypoints)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import Event, EventProcessingStatus
from app.repositories.event_repository import EventRepository
from app.services.event_normalization import normalize_event_record


async def process_event_by_id(
    session: AsyncSession,
    event_id: UUID,
    *,
    celery_task_id: str | None,
) -> None:
    """
    Load event, normalize payload, mark completed.
    On failure mark failed and re-raise so Celery can retry (when configured).
    """
    repo = EventRepository(session)
    event = await repo.get_by_id_for_worker(event_id)
    if event is None:
        return

    if event.processing_status == EventProcessingStatus.COMPLETED:
        return

    try:
        event.processing_status = EventProcessingStatus.PROCESSING
        if celery_task_id:
            event.celery_task_id = celery_task_id
        event.processing_attempts = event.processing_attempts + 1
        event.error_message = None
        await session.flush()

        normalized = normalize_event_record(
            organization_id=str(event.organization_id),
            event_name=event.event_name,
            event_type=event.event_type,
            payload=dict(event.payload),
            timestamp=event.timestamp,
            source=event.source,
        )
        event.normalized_payload = normalized
        event.processing_status = EventProcessingStatus.COMPLETED
        await session.commit()
    except Exception as exc:  # noqa: BLE001
        await session.rollback()
        failed = await session.get(Event, event_id)
        if failed is not None:
            failed.processing_status = EventProcessingStatus.FAILED
            failed.error_message = str(exc)[:4000]
            await session.commit()
        raise
