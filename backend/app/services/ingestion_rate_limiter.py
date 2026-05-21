"""Per-organization and per-API-key fixed-window rate limiting using Redis INCR."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.core.config import settings


def _minute_bucket() -> str:
    return datetime.now(UTC).strftime("%Y%m%d%H%M")


async def _incr_window(redis: Redis, key: str, amount: int, *, rollback_on_fail: bool) -> int:
    new_val = await redis.incrby(key, amount)
    if new_val == amount:
        await redis.expire(key, 120)
    return new_val


async def _check_limit(
    redis: Redis,
    key: str,
    amount: int,
    limit: int,
    *,
    detail: str,
    rollback_on_fail: bool,
) -> None:
    if limit <= 0 or amount <= 0:
        return
    new_val = await _incr_window(redis, key, amount, rollback_on_fail=rollback_on_fail)
    if new_val > limit:
        if rollback_on_fail:
            await redis.incrby(key, -amount)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


async def enforce_ingestion_rate_limit(
    redis: Redis,
    *,
    organization_id: UUID,
    api_key_id: UUID,
    event_count: int = 1,
) -> None:
    """Apply org-wide and per-API-key ingestion limits for the current minute."""
    bucket = _minute_bucket()
    org_key = f"ingest:rl:org:{organization_id}:{bucket}"
    key_key = f"ingest:rl:key:{api_key_id}:{bucket}"

    await _check_limit(
        redis,
        org_key,
        event_count,
        settings.ingestion_rate_limit_per_minute,
        detail="Organization ingestion rate limit exceeded. Retry after one minute.",
        rollback_on_fail=False,
    )

    try:
        await _check_limit(
            redis,
            key_key,
            event_count,
            settings.ingestion_rate_limit_per_key_per_minute,
            detail="API key ingestion rate limit exceeded. Retry after one minute.",
            rollback_on_fail=True,
        )
    except HTTPException:
        await redis.incrby(org_key, -event_count)
        raise
