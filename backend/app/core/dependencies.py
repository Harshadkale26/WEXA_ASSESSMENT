"""
Backwards-compatible import path for earlier scaffold.
Prefer `app.dependencies` going forward.
"""

from app.dependencies import get_db, get_redis

__all__ = ["get_db", "get_redis"]
