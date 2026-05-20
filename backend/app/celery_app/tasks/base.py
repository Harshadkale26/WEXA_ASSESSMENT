"""Base Celery task with production defaults: retries, backoff, structured logging."""

from __future__ import annotations

from celery import Task

from app.core.config import settings
from app.logging import get_logger

log = get_logger(__name__)


class BaseTask(Task):
    """Shared task base — exponential backoff retries and structured lifecycle logs."""

    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = settings.celery_task_retry_backoff_max
    retry_jitter = True
    max_retries = settings.celery_task_default_max_retries
    acks_late = True
    reject_on_worker_lost = True

    def on_failure(self, exc, task_id, args, kwargs, einfo) -> None:
        log.error(
            "task_on_failure",
            task_name=self.name,
            task_id=task_id,
            error=str(exc),
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo) -> None:
        log.warning(
            "task_on_retry",
            task_name=self.name,
            task_id=task_id,
            retries=self.request.retries,
            error=str(exc),
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs) -> None:
        log.info(
            "task_on_success",
            task_name=self.name,
            task_id=task_id,
        )
        super().on_success(retval, task_id, args, kwargs)
