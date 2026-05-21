"""Application service for dynamic analytics queries."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import User
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsQueryResponse
from app.schemas.dashboard import WidgetQueryConfig
from app.services.analytics.query_engine import AnalyticsQueryEngine
from app.services.base import BaseService


class AnalyticsService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def query(self, user: User, request: AnalyticsQueryRequest) -> AnalyticsQueryResponse:
        repo = AnalyticsRepository(self.session, user.organization_id)
        return await repo.run_query(request)

    async def query_for_organization(
        self,
        organization_id: UUID,
        request: AnalyticsQueryRequest,
    ) -> AnalyticsQueryResponse:
        repo = AnalyticsRepository(self.session, organization_id)
        return await repo.run_query(request)

    @staticmethod
    def widget_config_to_request(config: WidgetQueryConfig) -> AnalyticsQueryRequest:
        """Bridge dashboard widget config to analytics engine request."""
        from app.schemas.dashboard import AggregationType as WidgetAgg
        from app.schemas.dashboard import TimeRangeConfig

        agg_map = {
            WidgetAgg.COUNT: "count",
            WidgetAgg.SUM: "sum",
            WidgetAgg.AVERAGE: "avg",
        }
        group_by = config.group_by
        if group_by == "timestamp" and config.time_bucket:
            group_by = config.time_bucket.value

        tr = config.time_range
        if isinstance(tr, TimeRangeConfig):
            time_range = tr.preset.value if tr.preset else "7d"
        else:
            time_range = "7d"

        metric_field = None
        if config.metric.startswith("payload."):
            metric_field = config.metric
        elif config.metric in ("event_name", "event_type", "source"):
            # COUNT + dimension name means "all events" (or group on that column), not filter=value
            if config.aggregation != WidgetAgg.COUNT:
                metric_field = config.metric
            elif config.group_by and config.group_by not in ("timestamp",):
                metric_field = config.metric

        from app.schemas.analytics import AggregationType, AnalyticsFilter, FilterOperator

        return AnalyticsQueryRequest(
            metric=config.metric,
            metric_field=metric_field,
            aggregation=AggregationType(agg_map[config.aggregation]),
            group_by=group_by,
            time_range=time_range,
            filters=[
                AnalyticsFilter(
                    field=f.field,
                    operator=FilterOperator(f.operator.value),
                    value=f.value,
                )
                for f in config.filters
            ],
            page=1,
            page_size=1000,
        )
