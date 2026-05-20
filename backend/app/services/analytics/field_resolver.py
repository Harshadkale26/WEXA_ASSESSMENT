"""Safe field resolution — no user-controlled SQL, whitelist only."""

from __future__ import annotations

import re

from fastapi import HTTPException, status
from sqlalchemy import Float, String, cast
from sqlalchemy.sql.elements import ColumnElement

from app.models.ingestion import Event
from app.schemas.analytics import AnalyticsFilter, FilterOperator
from app.services.analytics.constants import (
    ALLOWED_DIMENSIONS,
    ALLOWED_METRIC_COLUMNS,
    DATE_TRUNC_MAP,
    PAYLOAD_PREFIX,
    TIME_BUCKETS,
)


class FieldResolver:
    @staticmethod
    def validate_field(field: str) -> None:
        if field in ALLOWED_DIMENSIONS:
            return
        if field.startswith(PAYLOAD_PREFIX):
            key = field[len(PAYLOAD_PREFIX) :]
            if re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", key):
                return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported field: {field}",
        )

    @staticmethod
    def is_time_bucket(group_by: str | None) -> bool:
        return group_by is not None and group_by.lower() in TIME_BUCKETS

    @staticmethod
    def dimension_column(field: str) -> ColumnElement:
        FieldResolver.validate_field(field)
        if field == "event_type":
            return Event.event_type
        if field == "event_name":
            return Event.event_name
        if field == "source":
            return Event.source
        key = field[len(PAYLOAD_PREFIX) :]
        return Event.payload[key].astext

    @staticmethod
    def time_bucket_column(bucket: str) -> ColumnElement:
        unit = DATE_TRUNC_MAP.get(bucket.lower())
        if not unit:
            raise HTTPException(status_code=400, detail=f"Invalid time bucket: {bucket}")
        from sqlalchemy import func

        return func.date_trunc(unit, Event.timestamp)

    @staticmethod
    def numeric_metric(metric: str, metric_field: str | None) -> ColumnElement:
        field = metric_field or metric
        if field.startswith(PAYLOAD_PREFIX):
            key = field[len(PAYLOAD_PREFIX) :]
            if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", key):
                raise HTTPException(status_code=400, detail=f"Invalid payload key: {key}")
            return cast(Event.payload[key].astext, Float)
        if field in ALLOWED_METRIC_COLUMNS:
            return cast(FieldResolver.dimension_column(field), Float)
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported numeric metric field: {field}",
        )

    @staticmethod
    def filter_condition(flt: AnalyticsFilter) -> ColumnElement:
        col = FieldResolver.dimension_column(flt.field)
        op, val = flt.operator, flt.value

        if op == FilterOperator.EQ:
            return col == val
        if op == FilterOperator.NE:
            return col != val
        if op == FilterOperator.IN:
            if not isinstance(val, list):
                raise HTTPException(status_code=400, detail="IN requires a list")
            return col.in_(val)
        if op in (FilterOperator.GT, FilterOperator.GTE, FilterOperator.LT, FilterOperator.LTE):
            if not flt.field.startswith(PAYLOAD_PREFIX):
                raise HTTPException(status_code=400, detail="Comparisons need payload.<key>")
            num = cast(col, Float)
            fval = float(val)  # type: ignore[arg-type]
            if op == FilterOperator.GT:
                return num > fval
            if op == FilterOperator.GTE:
                return num >= fval
            if op == FilterOperator.LT:
                return num < fval
            return num <= fval
        if op == FilterOperator.CONTAINS:
            return cast(col, String).ilike(f"%{val}%")
        raise HTTPException(status_code=400, detail=f"Unknown operator: {op}")
