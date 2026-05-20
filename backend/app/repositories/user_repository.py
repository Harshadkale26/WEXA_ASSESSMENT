from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import Role, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email_for_org(self, *, organization_id: UUID, email: str) -> User | None:
        stmt = select(User).where(
            User.organization_id == organization_id,
            User.email == email.lower(),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        organization_id: UUID,
        email: str,
        full_name: str,
        hashed_password: str,
        role: Role,
        is_active: bool = True,
    ) -> User:
        user = User(
            organization_id=organization_id,
            email=email.lower(),
            full_name=full_name,
            hashed_password=hashed_password,
            role=role,
            is_active=is_active,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

