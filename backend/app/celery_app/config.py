"""Celery worker, broker, and task defaults — driven by application settings."""

from __future__ import annotations

from kombu import Exchange, Queue

from app.core.config import settings


def default_queue_name() -> str:
    return "analytics.default"


def priority_queue_name() -> str:
    return "analytics.priority"


def ingestion_queue_name() -> str:
    return "analytics.ingestion"


def build_celery_config() -> dict:
    """Return Celery `conf.update(...)` dict for worker and beat processes."""
    default_q = default_queue_name()
    ingestion_q = ingestion_queue_name()

    return {
        # Broker / backend (Redis)
        "broker_url": settings.celery_broker_url,
        "result_backend": settings.celery_result_backend,
        "broker_connection_retry_on_startup": True,
        "broker_transport_options": {
            "visibility_timeout": settings.celery_visibility_timeout,
            "socket_timeout": 30,
            "socket_connect_timeout": 30,
        },
        "redis_backend_health_check_interval": 30,
        # Serialization
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "result_extended": True,
        "result_expires": settings.celery_result_expires,
        # Timezone
        "timezone": "UTC",
        "enable_utc": True,
        # Worker reliability
        "task_track_started": True,
        "task_acks_late": True,
        "task_reject_on_worker_lost": True,
        "worker_prefetch_multiplier": settings.celery_worker_prefetch_multiplier,
        "worker_concurrency": settings.celery_worker_concurrency,
        "worker_max_tasks_per_child": settings.celery_worker_max_tasks_per_child,
        "worker_send_task_events": True,
        "task_send_sent_event": True,
        # Default retry policy (overridable per task)
        "task_default_retry_delay": settings.celery_task_default_retry_delay,
        "task_annotations": {
            "*": {
                "rate_limit": None,
            },
        },
        # Queues & routing
        "task_default_queue": default_q,
        "task_queues": (
            Queue(default_q, Exchange(default_q), routing_key=default_q),
            Queue(
                ingestion_q,
                Exchange(ingestion_q),
                routing_key=ingestion_q,
            ),
            Queue(
                priority_queue_name(),
                Exchange(priority_queue_name()),
                routing_key=priority_queue_name(),
            ),
        ),
        "task_routes": {
            "events.*": {"queue": ingestion_q},
            "health.*": {"queue": default_q},
        },
        # Beat (imported from beat_schedule module)
        "beat_schedule": {},
        "beat_scheduler": "celery.beat:PersistentScheduler",
        # Monitoring
        "worker_hijack_root_logger": False,
    }
