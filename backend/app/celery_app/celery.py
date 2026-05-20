from celery import Celery

from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

celery_app = Celery(
    "analytics",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.celery_app.tasks.example", "app.celery_app.tasks.events"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
