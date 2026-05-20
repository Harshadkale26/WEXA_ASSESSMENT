"""Per-organization fixed-window rate limiting using Redis INCR."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.core.config import settings


async def enforce_ingestion_rate_limit(redis: Redis, *, organization_id: UUID) -> None:
    limit = settings.ingestion_rate_limit_per_minute
    if limit <= 0:
        return

    minute_bucket = datetime.now(UTC).strftime("%Y%m%d%H%M")
    key = f"ingest:rl:{organization_id}:{minute_bucket}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 120)

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Organization ingestion rate limit exceeded. Retry after one minute.",
        )
