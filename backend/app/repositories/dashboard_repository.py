from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dashboard import Dashboard


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, dashboard_id: UUID, *, organization_id: UUID) -> Dashboard | None:
        stmt = (
            select(Dashboard)
            .where(Dashboard.id == dashboard_id, Dashboard.organization_id == organization_id)
            .options(selectinload(Dashboard.widgets))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_org(
        self,
        organization_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Dashboard]:
        stmt = (
            select(Dashboard)
            .where(Dashboard.organization_id == organization_id)
            .order_by(Dashboard.is_default.desc(), Dashboard.name.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        organization_id: UUID,
        name: str,
        description: str | None,
        is_default: bool,
        created_by_id: UUID | None,
    ) -> Dashboard:
        if is_default:
            await self._clear_default(organization_id)
        row = Dashboard(
            organization_id=organization_id,
            name=name.strip(),
            description=description,
            is_default=is_default,
            created_by_id=created_by_id,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return row

    async def update(self, dashboard: Dashboard, **fields) -> Dashboard:
        if fields.get("is_default"):
            await self._clear_default(dashboard.organization_id)
        for key, value in fields.items():
            if value is not None:
                setattr(dashboard, key, value)
        await self.session.flush()
        await self.session.refresh(dashboard)
        return dashboard

    async def delete(self, dashboard: Dashboard) -> None:
        await self.session.delete(dashboard)
        await self.session.flush()

    async def _clear_default(self, organization_id: UUID) -> None:
        await self.session.execute(
            update(Dashboard)
            .where(Dashboard.organization_id == organization_id, Dashboard.is_default.is_(True))
            .values(is_default=False)
        )
