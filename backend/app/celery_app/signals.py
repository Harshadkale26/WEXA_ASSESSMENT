"""Celery signal handlers — structlog integration for task lifecycle."""

from __future__ import annotations

from celery.signals import task_failure, task_postrun, task_prerun, task_retry, worker_ready

from app.logging import configure_logging, get_logger

log = get_logger(__name__)


@worker_ready.connect
def on_worker_ready(sender=None, **kwargs) -> None:
    configure_logging()
    log.info("celery_worker_ready", worker=str(sender))


@task_prerun.connect
def on_task_prerun(task_id=None, task=None, args=None, kwargs=None, **extra) -> None:
    log.info(
        "celery_task_started",
        task_id=task_id,
        task_name=task.name if task else None,
    )


@task_postrun.connect
def on_task_postrun(task_id=None, task=None, retval=None, state=None, **extra) -> None:
    log.info(
        "celery_task_finished",
        task_id=task_id,
        task_name=task.name if task else None,
        state=state,
    )


@task_retry.connect
def on_task_retry(request=None, reason=None, einfo=None, **extra) -> None:
    log.warning(
        "celery_task_retry",
        task_id=request.id if request else None,
        task_name=request.task if request else None,
        reason=str(reason) if reason else None,
        retries=request.retries if request else None,
    )


@task_failure.connect
def on_task_failure(task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra) -> None:
    log.error(
        "celery_task_failed",
        task_id=task_id,
        exception=str(exception) if exception else None,
    )
