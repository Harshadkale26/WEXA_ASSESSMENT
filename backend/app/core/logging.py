import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(name: Optional[str] = None) -> logging.Logger:
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(log_level)
        root.addHandler(handler)

    logger = logging.getLogger(name or "app")
    logger.setLevel(log_level)
    return logger
