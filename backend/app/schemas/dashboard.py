"""Pydantic schemas for dashboards, widgets, and analytics query configuration."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.dashboard import WidgetType


class AggregationType(str, Enum):
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"


class TimeRangePreset(str, Enum):
    LAST_1H = "1h"
    LAST_24H = "24h"
    LAST_7D = "7d"
    LAST_30D = "30d"
    CUSTOM = "custom"


class FilterOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    IN = "in"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    CONTAINS = "contains"


class TimeBucket(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class TimeRangeConfig(BaseModel):
    preset: TimeRangePreset | None = TimeRangePreset.LAST_7D
    start: datetime | None = None
    end: datetime | None = None

    @model_validator(mode="after")
    def validate_custom_range(self) -> TimeRangeConfig:
        if self.preset == TimeRangePreset.CUSTOM:
            if self.start is None or self.end is None:
                raise ValueError("Custom time_range requires start and end")
            if self.start >= self.end:
                raise ValueError("time_range.start must be before time_range.end")
        return self


class WidgetFilter(BaseModel):
    field: str = Field(min_length=1, max_length=120)
    operator: FilterOperator
    value: str | int | float | bool | list[str] | list[int] | list[float]


class WidgetQueryConfig(BaseModel):
    """Stored in widgets.query_config (JSONB)."""

    metric: str = Field(
        min_length=1,
        max_length=120,
        description="Column (event_type, event_name, source) or payload path (payload.amount)",
    )
    aggregation: AggregationType
    group_by: str | None = Field(
        default=None,
        max_length=120,
        description="Dimension: event_type, event_name, source, timestamp",
    )
    time_bucket: TimeBucket | None = Field(
        default=None,
        description="Required when group_by=timestamp (line/bar charts)",
    )
    time_range: TimeRangeConfig = Field(default_factory=TimeRangeConfig)
    filters: list[WidgetFilter] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_grouping(self) -> WidgetQueryConfig:
        if self.group_by == "timestamp" and self.time_bucket is None:
            self.time_bucket = TimeBucket.DAY
        if self.aggregation in (AggregationType.SUM, AggregationType.AVERAGE):
            if self.metric in ("*", "event_name", "event_type", "source"):
                raise ValueError("sum/average requires a numeric metric or payload.<key>")
        return self


class WidgetLayout(BaseModel):
    x: int = 0
    y: int = 0
    w: int = 4
    h: int = 3


# --- Dashboard CRUD ---


class DashboardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    is_default: bool = False


class DashboardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    is_default: bool | None = None


class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    is_default: bool
    created_by_id: UUID | None
    created_at: datetime
    updated_at: datetime


class DashboardDetailResponse(DashboardResponse):
    widgets: list["WidgetResponse"] = Field(default_factory=list)


# --- Widget CRUD ---


class WidgetCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    widget_type: WidgetType
    query_config: WidgetQueryConfig
    layout: WidgetLayout | None = None
    sort_order: int = 0

    @model_validator(mode="after")
    def validate_widget_type_rules(self) -> WidgetCreate:
        if self.widget_type == WidgetType.KPI_CARD and self.query_config.group_by:
            raise ValueError("KPI card widgets must not use group_by")
        if self.widget_type in (WidgetType.PIE_CHART, WidgetType.BAR_CHART) and not self.query_config.group_by:
            raise ValueError(f"{self.widget_type.value} requires group_by")
        if self.widget_type == WidgetType.LINE_CHART:
            if self.query_config.group_by and self.query_config.group_by != "timestamp":
                pass  # allow categorical line or time series
            elif self.query_config.group_by is None:
                self.query_config.group_by = "timestamp"
        return self


class WidgetUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    widget_type: WidgetType | None = None
    query_config: WidgetQueryConfig | None = None
    layout: WidgetLayout | None = None
    sort_order: int | None = None


class WidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    dashboard_id: UUID
    title: str
    widget_type: WidgetType
    query_config: dict[str, Any]
    layout: dict[str, Any] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime


class WidgetDataPoint(BaseModel):
    label: str
    value: float


class WidgetDataSeries(BaseModel):
    name: str
    points: list[WidgetDataPoint]


class WidgetDataResponse(BaseModel):
    widget_id: UUID
    widget_type: WidgetType
    aggregation: AggregationType
    metric: str
    time_range: dict[str, str]
    # KPI: single value
    value: float | None = None
    # Charts: series or points
    labels: list[str] = Field(default_factory=list)
    series: list[WidgetDataSeries] = Field(default_factory=list)
    points: list[WidgetDataPoint] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)


class WidgetDataQueryOverride(BaseModel):
    """Optional runtime override for widget data fetch."""

    time_range: TimeRangeConfig | None = None
    filters: list[WidgetFilter] | None = None


DashboardDetailResponse.model_rebuild()
