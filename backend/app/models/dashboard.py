"""Multi-tenant dashboards and widgets."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class WidgetType(str, enum.Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    KPI_CARD = "kpi_card"
    PIE_CHART = "pie_chart"


WIDGET_TYPE_ENUM = SAEnum(
    WidgetType,
    name="widget_type_enum",
    native_enum=True,
    values_callable=lambda obj: [e.value for e in obj],
)


class Dashboard(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dashboards"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_dashboards_organization_id_name"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    organization = relationship("Organization", back_populates="dashboards", lazy="joined")
    widgets: Mapped[list["Widget"]] = relationship(
        back_populates="dashboard",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="Widget.sort_order",
    )


class Widget(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "widgets"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dashboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    widget_type: Mapped[WidgetType] = mapped_column(WIDGET_TYPE_ENUM, nullable=False)
    query_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    layout: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    dashboard: Mapped[Dashboard] = relationship(back_populates="widgets", lazy="joined")
    organization = relationship("Organization", back_populates="widgets", lazy="joined")
