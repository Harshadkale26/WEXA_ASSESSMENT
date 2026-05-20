from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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

    return {
        "status": "ok" if db_status == redis_status == "ok" else "degraded",
        "environment": settings.environment,
        "database": db_status,
        "redis": redis_status,
    }
