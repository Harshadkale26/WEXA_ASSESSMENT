"""Time range resolution for analytics queries."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.schemas.analytics import AnalyticsTimeRange, TimeRangeInput


def resolve_time_window(
    time_range: str | AnalyticsTimeRange,
) -> tuple[datetime, datetime]:
    """
    Resolve preset string ("24h") or structured AnalyticsTimeRange to UTC bounds.
    """
    now = datetime.now(UTC)

    if isinstance(time_range, AnalyticsTimeRange):
        if time_range.start is not None and time_range.end is not None:
            start = _ensure_utc(time_range.start)
            end = _ensure_utc(time_range.end)
            return start, end
        preset = time_range.preset or TimeRangeInput.H24
        return _preset_bounds(preset, now)

    preset_key = str(time_range).strip().lower()
    preset_map = {
        "1h": TimeRangeInput.H1,
        "24h": TimeRangeInput.H24,
        "7d": TimeRangeInput.D7,
        "30d": TimeRangeInput.D30,
    }
    preset = preset_map.get(preset_key, TimeRangeInput.D7)
    return _preset_bounds(preset, now)


def _preset_bounds(preset: TimeRangeInput, now: datetime) -> tuple[datetime, datetime]:
    deltas = {
        TimeRangeInput.H1: timedelta(hours=1),
        TimeRangeInput.H24: timedelta(hours=24),
        TimeRangeInput.D7: timedelta(days=7),
        TimeRangeInput.D30: timedelta(days=30),
    }
    delta = deltas.get(preset, timedelta(days=7))
    return now - delta, now


def _ensure_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
