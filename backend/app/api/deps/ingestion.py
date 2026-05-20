"""API-key authenticated ingestion context (multi-tenant)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api_key_hash import hash_api_key
from app.dependencies import get_db
from app.models.auth import Organization
from app.models.ingestion import OrganizationApiKey
from app.repositories.organization_api_key_repository import OrganizationApiKeyRepository


@dataclass(frozen=True)
class IngestionContext:
    organization_id: UUID
    api_key: OrganizationApiKey


async def get_ingestion_context(
    session: AsyncSession = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> IngestionContext:
    """
    Resolve organization from `X-API-Key` (preferred) or `Authorization: Bearer <api-key>`.
    """
    token = x_api_key
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Send X-API-Key header.",
        )

    key_hash = hash_api_key(token)
    repo = OrganizationApiKeyRepository(session)
    row = await repo.get_active_by_hash(key_hash)
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    org = await session.get(Organization, row.organization_id)
    if org is None or not org.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization inactive")

    return IngestionContext(organization_id=row.organization_id, api_key=row)
