from app.celery_app.celery import celery_app
from app.celery_app.tasks.base import log_task_complete, log_task_start


@celery_app.task(name="tasks.example.ping", bind=True)
def ping_task(self) -> dict:
    """Placeholder task — replace with real workloads."""
    log_task_start("ping", task_id=self.request.id)
    result = {"status": "pong"}
    log_task_complete("ping", task_id=self.request.id)
    return result
