import logging
import sys
from typing import Any

import structlog

from app.core.config import settings


def _shared_processors() -> list[Any]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def configure_logging() -> None:
    """
    Configure stdlib logging + structlog once per process.
    Safe to call multiple times (idempotent enough for local dev reload).
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers on reload.
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(handler)

    structlog.configure(
        processors=[
            *_shared_processors(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "app") -> structlog.stdlib.BoundLogger:
    configure_logging()
    return structlog.get_logger(name)

