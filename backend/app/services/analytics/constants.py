"""Whitelisted fields and mappings for safe query generation."""

from __future__ import annotations

PAYLOAD_PREFIX = "payload."

# Dimensions allowed in group_by and filters
ALLOWED_DIMENSIONS = frozenset({"event_type", "event_name", "source"})

# Time buckets (time-series group_by)
TIME_BUCKETS = frozenset({"hour", "day", "week", "month"})

# Columns usable as numeric metric sources for sum/avg
ALLOWED_METRIC_COLUMNS = frozenset({"event_name", "event_type", "source"})

# SQL date_trunc units
DATE_TRUNC_MAP = {
    "hour": "hour",
    "day": "day",
    "week": "week",
    "month": "month",
}
