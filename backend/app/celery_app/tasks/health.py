"""Celery health monitoring tasks (Beat + manual checks)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.celery_app.celery_app import celery_app
from app.logging import get_logger

log = get_logger(__name__)


@celery_app.task(name="health.worker_ping", bind=True)
def worker_ping(self) -> dict:
    """Periodic heartbeat — confirms workers are consuming from the broker."""
    payload = {
        "status": "ok",
        "worker": self.request.hostname,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    log.info("worker_ping", **payload)
    return payload
