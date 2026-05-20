"""
Backward-compatible analytics query builder (dashboard widgets).

Delegates to the reusable AnalyticsQueryEngine.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.dashboard import TimeRangeConfig, TimeRangePreset, WidgetQueryConfig
from app.services.analytics_service import AnalyticsService


def resolve_time_range(config: TimeRangeConfig) -> tuple[Any, Any]:
    """Legacy helper used by dashboard service."""
    from app.schemas.analytics import AnalyticsTimeRange
    from app.services.analytics.time_range import resolve_time_window

    if config.preset == TimeRangePreset.CUSTOM and config.start and config.end:
        return resolve_time_window(
            AnalyticsTimeRange(start=config.start, end=config.end, preset=None)
        )
    preset = config.preset.value if config.preset else "7d"
    return resolve_time_window(preset)


class AnalyticsQueryBuilder:
    """Thin wrapper — prefer AnalyticsQueryEngine / AnalyticsRepository for new code."""

    def __init__(self, session: AsyncSession, organization_id: UUID) -> None:
        self.session = session
        self.organization_id = organization_id
        self._service = AnalyticsService(session)

    async def execute(self, config: WidgetQueryConfig) -> list[dict[str, Any]]:
        request = AnalyticsService.widget_config_to_request(config)
        result = await self._service.query_for_organization(self.organization_id, request)
        return [{"label": p.label, "value": p.value} for p in result.data]
