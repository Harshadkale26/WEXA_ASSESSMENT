"""Celery cluster health checks for API monitoring."""

from __future__ import annotations

from typing import Any

from app.celery_app.celery_app import celery_app
from app.logging import get_logger

log = get_logger(__name__)


def inspect_celery_workers(timeout: float = 2.0) -> dict[str, Any]:
    """
    Ping active workers via Celery control inspect API.
    Returns worker names and ping responses; empty if no workers are reachable.
    """
    try:
        inspector = celery_app.control.inspect(timeout=timeout)
        ping = inspector.ping() if inspector else None
        if not ping:
            return {"status": "unavailable", "workers": {}, "worker_count": 0}

        return {
            "status": "ok",
            "workers": ping,
            "worker_count": len(ping),
        }
    except Exception as exc:  # noqa: BLE001
        log.warning("celery_health_inspect_failed", error=str(exc))
        return {"status": "error", "workers": {}, "worker_count": 0, "detail": str(exc)}


def get_registered_tasks(timeout: float = 2.0) -> list[str]:
    try:
        inspector = celery_app.control.inspect(timeout=timeout)
        registered = inspector.registered() if inspector else None
        if not registered:
            return []
        tasks: set[str] = set()
        for worker_tasks in registered.values():
            tasks.update(worker_tasks)
        return sorted(tasks)
    except Exception:  # noqa: BLE001
        return []
