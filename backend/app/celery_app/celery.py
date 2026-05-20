"""Backward-compatible Celery app entrypoint (docker-compose / legacy imports)."""

from app.celery_app.celery_app import celery_app

__all__ = ["celery_app"]
