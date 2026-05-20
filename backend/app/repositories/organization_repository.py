from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import Organization


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_slug(self, slug: str) -> Organization | None:
        stmt = select(Organization).where(Organization.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, *, name: str, slug: str) -> Organization:
        organization = Organization(name=name, slug=slug, is_active=True)
        self.session.add(organization)
        await self.session.flush()
        await self.session.refresh(organization)
        return organization

