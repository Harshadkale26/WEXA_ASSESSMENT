"""Analytics query API — dynamic event analytics requests and responses."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class AggregationType(str, Enum):
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    AVERAGE = "average"  # alias normalized to avg


class TimeRangeInput(str, Enum):
    """Shorthand presets (also accepted as plain strings)."""

    H1 = "1h"
    H24 = "24h"
    D7 = "7d"
    D30 = "30d"


class TimeBucketGroup(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class DimensionGroup(str, Enum):
    EVENT_TYPE = "event_type"
    EVENT_NAME = "event_name"
    SOURCE = "source"


class FilterOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    IN = "in"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    CONTAINS = "contains"


class AnalyticsFilter(BaseModel):
    field: str = Field(min_length=1, max_length=120)
    operator: FilterOperator
    value: str | int | float | bool | list[str] | list[int] | list[float]


class AnalyticsTimeRange(BaseModel):
    """Structured time window (alternative to preset string)."""

    preset: TimeRangeInput | None = TimeRangeInput.H24
    start: datetime | None = None
    end: datetime | None = None

    @model_validator(mode="after")
    def validate_custom(self) -> AnalyticsTimeRange:
        if self.start is not None and self.end is not None and self.start >= self.end:
            raise ValueError("start must be before end")
        return self


class AnalyticsQueryRequest(BaseModel):
    """
    Dynamic analytics query input.

    Example:
        {"metric": "page_views", "aggregation": "count", "group_by": "hour", "time_range": "24h"}
    """

    metric: str = Field(
        min_length=1,
        max_length=120,
        description="Event name shorthand, column, or payload.<key> for numeric aggregations",
    )
    aggregation: AggregationType
    group_by: str | None = Field(
        default=None,
        description="hour | day | week | month | event_type | event_name | source",
    )
    time_range: str | AnalyticsTimeRange = Field(
        default="7d",
        description='Preset: "1h", "24h", "7d", "30d" or {"preset","start","end"}',
    )
    metric_field: str | None = Field(
        default=None,
        description="Explicit field for metric (event_name, event_type, payload.amount). "
        "If omitted, metric is applied as event_name filter for count.",
    )
    filters: list[AnalyticsFilter] = Field(default_factory=list)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=100, ge=1, le=1000)

    @field_validator("aggregation", mode="before")
    @classmethod
    def normalize_avg(cls, v: str) -> str:
        if isinstance(v, str) and v.lower() == "average":
            return "avg"
        return v

    @model_validator(mode="after")
    def validate_aggregation_metric(self) -> AnalyticsQueryRequest:
        agg = self.aggregation
        if agg in (AggregationType.SUM, AggregationType.AVG, AggregationType.AVERAGE):
            if self.metric_field and self.metric_field.startswith("payload."):
                return self
            if self.metric_field in ("event_name", "event_type", "source"):
                raise ValueError("sum/avg on string columns is not supported")
            if not self.metric_field and not self.metric.startswith("payload."):
                raise ValueError("sum/avg requires metric_field or payload.<key>")
        return self


class AnalyticsDataPoint(BaseModel):
    label: str
    value: float
    bucket_start: datetime | None = None


class AnalyticsQueryMeta(BaseModel):
    organization_id: str
    metric: str
    aggregation: str
    group_by: str | None
    time_range_start: datetime
    time_range_end: datetime
    total_groups: int
    page: int
    page_size: int
    has_more: bool


class AnalyticsQueryResponse(BaseModel):
    data: list[AnalyticsDataPoint]
    meta: AnalyticsQueryMeta
