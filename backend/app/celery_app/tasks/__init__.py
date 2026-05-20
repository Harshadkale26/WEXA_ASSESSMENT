"""Celery task modules — import tasks here for autodiscovery."""

import app.celery_app.tasks.events  # noqa: F401
import app.celery_app.tasks.example  # noqa: F401
