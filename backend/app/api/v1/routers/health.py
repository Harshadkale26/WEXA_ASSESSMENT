from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app.health import get_registered_tasks, inspect_celery_workers
from app.core.config import settings
from app.core.dependencies import get_db, get_redis

router = APIRouter()


@router.get("")
async def api_health(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    db_status = "ok"
    redis_status = "ok"

    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        await redis.ping()
    except Exception:
        redis_status = "error"

    celery = inspect_celery_workers()
    celery_status = celery.get("status", "unavailable")

    components_ok = db_status == redis_status == "ok"
    workers_ok = celery_status == "ok" and celery.get("worker_count", 0) > 0

    if components_ok and workers_ok:
        overall = "ok"
    elif components_ok:
        overall = "degraded"
    else:
        overall = "degraded" if db_status == "ok" or redis_status == "ok" else "error"

    return {
        "status": overall,
        "environment": settings.environment,
        "database": db_status,
        "redis": redis_status,
        "celery": {
            "status": celery_status,
            "worker_count": celery.get("worker_count", 0),
            "workers": celery.get("workers", {}),
        },
    }


@router.get("/celery")
async def celery_health_detail():
    """Detailed Celery worker and registered task inspection."""
    workers = inspect_celery_workers(timeout=5.0)
    return {
        **workers,
        "registered_tasks": get_registered_tasks(timeout=5.0),
        "broker_url": settings.celery_broker_url.split("@")[-1],  # omit credentials if any
    }
