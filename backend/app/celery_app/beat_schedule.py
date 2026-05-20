"""Celery Beat periodic task schedule."""

from __future__ import annotations

from celery.schedules import crontab

from app.core.config import settings


def build_beat_schedule() -> dict:
    if not settings.celery_beat_enabled:
        return {}

    return {
        "worker-health-ping": {
            "task": "health.worker_ping",
            "schedule": settings.celery_beat_health_interval_seconds,
            "options": {"queue": "analytics.default"},
        },
        "retry-failed-events": {
            "task": "events.retry_failed_events",
            "schedule": crontab(minute=f"*/{settings.celery_beat_retry_failed_minutes}"),
            "options": {"queue": "analytics.ingestion"},
        },
    }
