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

    async def create(
        self,
        *,
        organization_id: UUID,
        name: str,
        key_hash: str,
        key_prefix: str,
    ) -> OrganizationApiKey:
        row = OrganizationApiKey(
            organization_id=organization_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            is_active=True,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return row

    async def touch_last_used(self, key: OrganizationApiKey) -> None:
        key.last_used_at = datetime.now(UTC)
        await self.session.flush()
