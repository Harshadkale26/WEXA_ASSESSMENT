from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import OrganizationApiKey


class OrganizationApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active_by_hash(self, key_hash: str) -> OrganizationApiKey | None:
        stmt = select(OrganizationApiKey).where(
            OrganizationApiKey.key_hash == key_hash,
            OrganizationApiKey.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, key_id: UUID, *, organization_id: UUID) -> OrganizationApiKey | None:
        stmt = select(OrganizationApiKey).where(
            OrganizationApiKey.id == key_id,
            OrganizationApiKey.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_org(self, organization_id: UUID) -> list[OrganizationApiKey]:
        stmt = (
            select(OrganizationApiKey)
            .where(OrganizationApiKey.organization_id == organization_id)
            .order_by(OrganizationApiKey.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        organization_id: UUID,
        name: str,
        key_hash: str,
        key_prefix: str,
        webhook_signing_secret: str | None = None,
    ) -> OrganizationApiKey:
        row = OrganizationApiKey(
            organization_id=organization_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            is_active=True,
            webhook_signing_secret=webhook_signing_secret,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return row

    async def revoke(self, key: OrganizationApiKey) -> OrganizationApiKey:
        key.is_active = False
        await self.session.flush()
        await self.session.refresh(key)
        return key

    async def touch_last_used(self, key: OrganizationApiKey) -> None:
        key.last_used_at = datetime.now(UTC)
        await self.session.flush()
