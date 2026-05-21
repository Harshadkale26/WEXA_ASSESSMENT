"""
Reusable async analytics query engine (SQLAlchemy).

- Multi-tenant isolation on organization_id
- Safe whitelisted fields only
- count / sum / avg aggregations
- Time-series buckets (hour, day, week, month)
- Pagination on grouped results
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Float, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from app.models.ingestion import Event, EventProcessingStatus
from app.schemas.analytics import (
    AggregationType,
    AnalyticsDataPoint,
    AnalyticsFilter,
    AnalyticsQueryRequest,
    AnalyticsQueryResponse,
    AnalyticsQueryMeta,
)
from app.services.analytics.field_resolver import FieldResolver
from app.services.analytics.time_range import resolve_time_window


@dataclass(frozen=True)
class BuiltQuery:
    """Internal representation of a compiled analytics SELECT."""

    statement: Select[Any]
    group_expr: ColumnElement[Any] | None
    is_scalar: bool


class AnalyticsQueryEngine:
    """Build and execute parameterized analytics queries over events."""

    def __init__(self, session: AsyncSession, organization_id: UUID) -> None:
        self.session = session
        self.organization_id = organization_id
        self._resolver = FieldResolver()

    async def execute(self, request: AnalyticsQueryRequest) -> AnalyticsQueryResponse:
        start, end = resolve_time_window(request.time_range)
        built = self.build(request, start, end)

        total_groups = 0
        if built.group_expr is not None:
            total_groups = await self._count_groups(built, request, start, end)

        offset = (request.page - 1) * request.page_size
        stmt = built.statement.offset(offset).limit(request.page_size)

        result = await self.session.execute(stmt)
        rows = result.all()

        data = self._rows_to_points(rows, built.group_expr is not None)
        has_more = built.group_expr is not None and (offset + len(data) < total_groups)

        agg = request.aggregation.value
        if request.aggregation == AggregationType.AVERAGE:
            agg = "avg"

        return AnalyticsQueryResponse(
            data=data,
            meta=AnalyticsQueryMeta(
                organization_id=str(self.organization_id),
                metric=request.metric,
                aggregation=agg,
                group_by=request.group_by,
                time_range_start=start,
                time_range_end=end,
                total_groups=total_groups if built.group_expr is not None else 1,
                page=request.page,
                page_size=request.page_size,
                has_more=has_more,
            ),
        )

    def build(
        self,
        request: AnalyticsQueryRequest,
        start: datetime,
        end: datetime,
    ) -> BuiltQuery:
        conditions = self._base_conditions(start, end)
        conditions.extend(self._metric_conditions(request))
        for flt in request.filters:
            conditions.append(self._resolver.filter_condition(flt))

        agg_expr = self._aggregation_expr(request)
        group_expr = self._group_expr(request)

        if group_expr is not None:
            stmt = (
                select(
                    group_expr.label("label"),
                    agg_expr.label("value"),
                )
                .where(and_(*conditions))
                .group_by(group_expr)
                .order_by(group_expr)  # time-series friendly ordering
            )
            return BuiltQuery(statement=stmt, group_expr=group_expr, is_scalar=False)

        stmt = select(agg_expr.label("value")).where(and_(*conditions))
        return BuiltQuery(statement=stmt, group_expr=None, is_scalar=True)

    def _base_conditions(self, start: datetime, end: datetime) -> list[ColumnElement]:
        return [
            Event.organization_id == self.organization_id,
            Event.timestamp >= start,
            Event.timestamp <= end,
            Event.processing_status == EventProcessingStatus.COMPLETED,
        ]

    def _metric_conditions(self, request: AnalyticsQueryRequest) -> list[ColumnElement]:
        """
        Optional filters from metric shorthand.

        When widget config uses metric=event_type for a COUNT of all events, do not
        filter event_type='event_type'. Only filter when metric is a concrete value
        (e.g. metric=pageview with metric_field=event_type).
        """
        if request.metric_field:
            field = request.metric_field
            if field in ("event_name", "event_type", "source"):
                if request.metric not in (field, "*") and request.metric:
                    return [self._resolver.dimension_column(field) == request.metric]
            return []

        if request.aggregation == AggregationType.COUNT:
            if request.metric not in ("event_name", "event_type", "source", "*"):
                return [Event.event_name == request.metric]
        return []

    def _aggregation_expr(self, request: AnalyticsQueryRequest) -> ColumnElement:
        agg = request.aggregation
        if agg == AggregationType.AVERAGE:
            agg = AggregationType.AVG

        if agg == AggregationType.COUNT:
            return func.count(Event.id)

        metric_expr = self._resolver.numeric_metric(request.metric, request.metric_field)
        if agg == AggregationType.SUM:
            return func.coalesce(func.sum(metric_expr), 0.0)
        if agg == AggregationType.AVG:
            return func.coalesce(func.avg(metric_expr), 0.0)
        raise ValueError(f"Unsupported aggregation: {agg}")

    def _group_expr(self, request: AnalyticsQueryRequest) -> ColumnElement | None:
        if not request.group_by:
            return None

        gb = request.group_by.lower()
        if self._resolver.is_time_bucket(gb):
            return self._resolver.time_bucket_column(gb)

        self._resolver.validate_field(gb)
        return self._resolver.dimension_column(gb)

    async def _count_groups(
        self,
        built: BuiltQuery,
        request: AnalyticsQueryRequest,
        start: datetime,
        end: datetime,
    ) -> int:
        subq = built.statement.subquery()
        count_stmt = select(func.count()).select_from(subq)
        result = await self.session.execute(count_stmt)
        return int(result.scalar_one() or 0)

    @staticmethod
    def _rows_to_points(rows: Any, grouped: bool) -> list[AnalyticsDataPoint]:
        points: list[AnalyticsDataPoint] = []
        if not grouped:
            val = rows[0][0] if rows else 0.0
            return [AnalyticsDataPoint(label="total", value=float(val or 0))]

        for row in rows:
            label = row.label
            bucket_start = label if isinstance(label, datetime) else None
            label_str = label.isoformat() if isinstance(label, datetime) else str(label)
            points.append(
                AnalyticsDataPoint(
                    label=label_str,
                    value=float(row.value or 0),
                    bucket_start=bucket_start,
                )
            )
        return points
