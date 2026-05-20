"""Event ingestion processing tasks — async DB pipeline with retries."""

from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy import select

from app.celery_app.celery_app import celery_app
from app.celery_app.config import ingestion_queue_name
from app.core.config import settings
from app.database import async_session_factory
from app.logging import get_logger
from app.models.ingestion import Event, EventProcessingStatus
from app.services.event_processing_service import process_event_by_id

log = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="events.process_event",
    queue=ingestion_queue_name(),
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=settings.celery_task_retry_backoff_max,
    retry_jitter=True,
    max_retries=settings.celery_task_default_max_retries,
)
def process_event_task(self, event_id: str) -> str:
    """
    Normalize and persist a single ingested event.
    Retries with exponential backoff on transient DB / processing errors.
    """

    async def _run() -> None:
        async with async_session_factory() as session:
            await process_event_by_id(
                session,
                UUID(event_id),
                celery_task_id=self.request.id,
            )

    try:
        asyncio.run(_run())
    except Exception as exc:
        log.exception("event_processing_failed", event_id=event_id, error=str(exc))
        raise

    log.info("event_processing_completed", event_id=event_id, task_id=self.request.id)
    return event_id


@celery_app.task(
    bind=True,
    name="events.retry_failed_events",
    queue=ingestion_queue_name(),
)
def retry_failed_events(self, batch_size: int | None = None) -> dict:
    """
    Beat-scheduled sweep: re-enqueue failed events under max retry attempts.
    """
    limit = batch_size or settings.celery_failed_event_retry_batch_size

    async def _fetch_failed_ids() -> list[str]:
        async with async_session_factory() as session:
            stmt = (
                select(Event.id)
                .where(
                    Event.processing_status == EventProcessingStatus.FAILED,
                    Event.processing_attempts < settings.celery_task_default_max_retries,
                )
                .order_by(Event.updated_at.asc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return [str(row[0]) for row in result.all()]

    failed_ids = asyncio.run(_fetch_failed_ids())
    for event_id in failed_ids:
        process_event_task.apply_async(args=[event_id], queue=ingestion_queue_name())

    log.info("retry_failed_events_enqueued", count=len(failed_ids))
    return {"requeued": len(failed_ids)}
