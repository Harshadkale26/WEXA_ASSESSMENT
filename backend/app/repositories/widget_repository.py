from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import Widget, WidgetType


class WidgetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, widget_id: UUID, *, organization_id: UUID) -> Widget | None:
        stmt = select(Widget).where(
            Widget.id == widget_id,
            Widget.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_dashboard(
        self,
        dashboard_id: UUID,
        *,
        organization_id: UUID,
    ) -> list[Widget]:
        stmt = (
            select(Widget)
            .where(
                Widget.dashboard_id == dashboard_id,
                Widget.organization_id == organization_id,
            )
            .order_by(Widget.sort_order.asc(), Widget.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        organization_id: UUID,
        dashboard_id: UUID,
        title: str,
        widget_type: WidgetType,
        query_config: dict,
        layout: dict | None,
        sort_order: int,
    ) -> Widget:
        row = Widget(
            organization_id=organization_id,
            dashboard_id=dashboard_id,
            title=title.strip(),
            widget_type=widget_type,
            query_config=query_config,
            layout=layout,
            sort_order=sort_order,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return row

    async def update(self, widget: Widget, **fields) -> Widget:
        for key, value in fields.items():
            if value is not None:
                setattr(widget, key, value)
        await self.session.flush()
        await self.session.refresh(widget)
        return widget

    async def delete(self, widget: Widget) -> None:
        await self.session.delete(widget)
        await self.session.flush()

    async def count_for_dashboard(self, dashboard_id: UUID) -> int:
        stmt = select(func.count()).select_from(Widget).where(Widget.dashboard_id == dashboard_id)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
