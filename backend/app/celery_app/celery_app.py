"""
Production Celery application factory.

Usage:
  Worker: celery -A app.celery_app.celery_app worker --loglevel=info
  Beat:   celery -A app.celery_app.celery_app beat --loglevel=info
"""

from __future__ import annotations

from celery import Celery

from app.celery_app.beat_schedule import build_beat_schedule
from app.celery_app.config import build_celery_config
from app.celery_app.signals import (  # noqa: F401 — register signal handlers
    on_task_failure,
    on_task_postrun,
    on_task_prerun,
    on_task_retry,
    on_worker_ready,
)
from app.celery_app.tasks.base import BaseTask
from app.logging import configure_logging

configure_logging()

celery_app = Celery("analytics")
celery_app.Task = BaseTask

celery_app.conf.update(build_celery_config())
celery_app.conf.beat_schedule = build_beat_schedule()

# Register task modules after celery_app is fully initialized (avoids circular imports)
celery_app.conf.imports = (
    "app.celery_app.tasks.events",
    "app.celery_app.tasks.health",
)

__all__ = ["celery_app"]
