"""
Run async DB work inside Celery prefork workers.

Celery tasks call asyncio.run() per invocation; the FastAPI-global async engine
must not be reused across loops (asyncpg: "Future attached to a different loop").
Each task gets a fresh engine + session, disposed when done.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import create_engine

T = TypeVar("T")


async def _with_fresh_session(fn: Callable[[AsyncSession], Awaitable[T]]) -> T:
    engine = create_engine()
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    try:
        async with session_factory() as session:
            return await fn(session)
    finally:
        await engine.dispose()


def run_async(fn: Callable[[AsyncSession], Awaitable[T]]) -> T:
    """Execute async DB callback in an isolated event loop and session."""
    return asyncio.run(_with_fresh_session(fn))
