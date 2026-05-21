from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import User
from app.models.dashboard import WidgetType
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.widget_repository import WidgetRepository
from app.schemas.dashboard import (
    AggregationType,
    DashboardCreate,
    DashboardDetailResponse,
    DashboardResponse,
    DashboardUpdate,
    TimeBucket,
    TimeRangeConfig,
    TimeRangePreset,
    WidgetCreate,
    WidgetDataPoint,
    WidgetDataQueryOverride,
    WidgetDataResponse,
    WidgetDataSeries,
    WidgetLayout,
    WidgetQueryConfig,
    WidgetResponse,
    WidgetUpdate,
)

DEFAULT_BOOTSTRAP_WIDGETS: list[WidgetCreate] = [
    WidgetCreate(
        title="Total events",
        widget_type=WidgetType.KPI_CARD,
        query_config=WidgetQueryConfig(
            metric="*",
            aggregation=AggregationType.COUNT,
            time_range=TimeRangeConfig(preset=TimeRangePreset.LAST_7D),
        ),
        layout=WidgetLayout(x=0, y=0, w=3, h=2),
        sort_order=0,
    ),
    WidgetCreate(
        title="Events over time",
        widget_type=WidgetType.LINE_CHART,
        query_config=WidgetQueryConfig(
            metric="*",
            aggregation=AggregationType.COUNT,
            group_by="timestamp",
            time_bucket=TimeBucket.HOUR,
            time_range=TimeRangeConfig(preset=TimeRangePreset.LAST_7D),
        ),
        layout=WidgetLayout(x=3, y=0, w=6, h=3),
        sort_order=1,
    ),
    WidgetCreate(
        title="By event type",
        widget_type=WidgetType.BAR_CHART,
        query_config=WidgetQueryConfig(
            metric="*",
            aggregation=AggregationType.COUNT,
            group_by="event_type",
            time_range=TimeRangeConfig(preset=TimeRangePreset.LAST_7D),
        ),
        layout=WidgetLayout(x=0, y=3, w=6, h=3),
        sort_order=2,
    ),
    WidgetCreate(
        title="By source",
        widget_type=WidgetType.PIE_CHART,
        query_config=WidgetQueryConfig(
            metric="*",
            aggregation=AggregationType.COUNT,
            group_by="source",
            time_range=TimeRangeConfig(preset=TimeRangePreset.LAST_7D),
        ),
        layout=WidgetLayout(x=6, y=3, w=6, h=3),
        sort_order=3,
    ),
]
from app.services.analytics_query_builder import AnalyticsQueryBuilder, resolve_time_range
from app.services.base import BaseService


class DashboardService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.dashboards = DashboardRepository(session)
        self.widgets = WidgetRepository(session)

    async def list_dashboards(self, user: User) -> list[DashboardResponse]:
        rows = await self.dashboards.list_for_org(user.organization_id)
        return [DashboardResponse.model_validate(r) for r in rows]

    async def get_dashboard(self, user: User, dashboard_id: UUID) -> DashboardDetailResponse:
        row = await self._get_dashboard_or_404(dashboard_id, user.organization_id)
        widgets = await self.widgets.list_for_dashboard(dashboard_id, organization_id=user.organization_id)
        return DashboardDetailResponse(
            **DashboardResponse.model_validate(row).model_dump(),
            widgets=[WidgetResponse.model_validate(w) for w in widgets],
        )

    async def create_dashboard(self, user: User, payload: DashboardCreate) -> DashboardResponse:
        row = await self.dashboards.create(
            organization_id=user.organization_id,
            name=payload.name,
            description=payload.description,
            is_default=payload.is_default,
            created_by_id=user.id,
        )
        return DashboardResponse.model_validate(row)

    async def bootstrap_default(self, user: User) -> DashboardDetailResponse:
        """
        Ensure the org has a default dashboard with sample widgets (idempotent).
        Creates dashboard and/or widgets if missing.
        """
        rows = await self.dashboards.list_for_org(user.organization_id)
        dashboard = next((d for d in rows if d.is_default), None)
        if dashboard is None and rows:
            dashboard = rows[0]
        if dashboard is None:
            dashboard = await self.dashboards.create(
                organization_id=user.organization_id,
                name="Overview",
                description="Auto-generated analytics overview",
                is_default=True,
                created_by_id=user.id,
            )

        widgets = await self.widgets.list_for_dashboard(
            dashboard.id,
            organization_id=user.organization_id,
        )
        if not widgets:
            for spec in DEFAULT_BOOTSTRAP_WIDGETS:
                await self.create_widget(user, dashboard.id, spec)

        return await self.get_dashboard(user, dashboard.id)

    async def update_dashboard(
        self,
        user: User,
        dashboard_id: UUID,
        payload: DashboardUpdate,
    ) -> DashboardResponse:
        row = await self._get_dashboard_or_404(dashboard_id, user.organization_id)
        data = payload.model_dump(exclude_unset=True)
        updated = await self.dashboards.update(row, **data)
        return DashboardResponse.model_validate(updated)

    async def delete_dashboard(self, user: User, dashboard_id: UUID) -> None:
        row = await self._get_dashboard_or_404(dashboard_id, user.organization_id)
        await self.dashboards.delete(row)

    async def list_widgets(self, user: User, dashboard_id: UUID) -> list[WidgetResponse]:
        await self._get_dashboard_or_404(dashboard_id, user.organization_id)
        rows = await self.widgets.list_for_dashboard(dashboard_id, organization_id=user.organization_id)
        return [WidgetResponse.model_validate(r) for r in rows]

    async def create_widget(
        self,
        user: User,
        dashboard_id: UUID,
        payload: WidgetCreate,
    ) -> WidgetResponse:
        await self._get_dashboard_or_404(dashboard_id, user.organization_id)
        row = await self.widgets.create(
            organization_id=user.organization_id,
            dashboard_id=dashboard_id,
            title=payload.title,
            widget_type=payload.widget_type,
            query_config=payload.query_config.model_dump(mode="json"),
            layout=payload.layout.model_dump() if payload.layout else None,
            sort_order=payload.sort_order,
        )
        return WidgetResponse.model_validate(row)

    async def get_widget(self, user: User, widget_id: UUID) -> WidgetResponse:
        row = await self._get_widget_or_404(widget_id, user.organization_id)
        return WidgetResponse.model_validate(row)

    async def update_widget(
        self,
        user: User,
        widget_id: UUID,
        payload: WidgetUpdate,
    ) -> WidgetResponse:
        row = await self._get_widget_or_404(widget_id, user.organization_id)
        data = payload.model_dump(exclude_unset=True)
        if "query_config" in data and data["query_config"] is not None:
            data["query_config"] = WidgetQueryConfig.model_validate(data["query_config"]).model_dump(
                mode="json"
            )
        if "layout" in data and data["layout"] is not None:
            data["layout"] = dict(data["layout"])
        updated = await self.widgets.update(row, **data)
        return WidgetResponse.model_validate(updated)

    async def delete_widget(self, user: User, widget_id: UUID) -> None:
        row = await self._get_widget_or_404(widget_id, user.organization_id)
        await self.widgets.delete(row)

    async def get_widget_data(
        self,
        user: User,
        widget_id: UUID,
        override: WidgetDataQueryOverride | None = None,
    ) -> WidgetDataResponse:
        row = await self._get_widget_or_404(widget_id, user.organization_id)
        config = WidgetQueryConfig.model_validate(row.query_config)

        if override:
            if override.time_range:
                config.time_range = override.time_range
            if override.filters is not None:
                config.filters = override.filters

        builder = AnalyticsQueryBuilder(self.session, user.organization_id)
        raw_rows = await builder.execute(config)

        start, end = resolve_time_range(config.time_range)
        response = WidgetDataResponse(
            widget_id=row.id,
            widget_type=row.widget_type,
            aggregation=config.aggregation,
            metric=config.metric,
            time_range={"start": start.isoformat(), "end": end.isoformat()},
        )

        if row.widget_type == WidgetType.KPI_CARD:
            response.value = raw_rows[0]["value"] if raw_rows else 0.0
            return response

        points = [WidgetDataPoint(label=r["label"], value=r["value"]) for r in raw_rows]
        response.points = points
        response.labels = [p.label for p in points]
        response.series = [
            WidgetDataSeries(name=config.metric, points=points),
        ]
        response.meta = {"group_by": config.group_by, "row_count": len(points)}
        return response

    async def _get_dashboard_or_404(self, dashboard_id: UUID, organization_id: UUID):
        row = await self.dashboards.get_by_id(dashboard_id, organization_id=organization_id)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
        return row

    async def _get_widget_or_404(self, widget_id: UUID, organization_id: UUID):
        row = await self.widgets.get_by_id(widget_id, organization_id=organization_id)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
        return row
