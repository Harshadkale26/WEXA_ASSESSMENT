"""Normalize raw ingestion payloads for downstream analytics (pure functions + async-friendly)."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def normalize_event_record(
    *,
    organization_id: str,
    event_name: str,
    event_type: str,
    payload: dict[str, Any],
    timestamp: datetime,
    source: str,
) -> dict[str, Any]:
    """
    Deterministic normalization layer.
    Keeps original payload embedded and adds canonical top-level metadata.
    """
    ts = timestamp.astimezone(tz=timestamp.tzinfo) if timestamp.tzinfo else timestamp
    return {
        "organization_id": organization_id,
        "event_name": event_name.strip(),
        "event_type": event_type.strip().lower(),
        "source": source.strip(),
        "occurred_at": ts.isoformat(),
        "payload": payload,
    }
