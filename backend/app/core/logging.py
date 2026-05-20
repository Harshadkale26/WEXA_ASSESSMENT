"""
Backwards-compatible import path for earlier scaffold.
Prefer `app.logging` going forward.
"""

from app.logging import configure_logging, get_logger


def setup_logging():  # pragma: no cover
    configure_logging()
    return get_logger("app")
