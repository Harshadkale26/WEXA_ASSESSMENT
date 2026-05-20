"""Celery tasks: async event processing pipeline with retries."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from app.celery_app.celery import celery_app
from app.database import async_session_factory
from app.services.event_processing_service import process_event_by_id

log = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="events.process_event",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=900,
    retry_jitter=True,
    max_retries=5,
)
def process_event_task(self, event_id: str) -> str:
    """
    Process a single ingested event asynchronously.
    Retries with exponential backoff on transient failures (DB, JSON, etc.).
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
    except Exception:
        log.exception("event_processing_failed", extra={"event_id": event_id})
        raise
    return event_id
