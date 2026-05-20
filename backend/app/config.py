"""
Convenience module to expose settings at app root.
Keeps clean-architecture config implementation in `app/core/config.py`.
"""

from app.core.config import Settings, settings

__all__ = ["Settings", "settings"]

