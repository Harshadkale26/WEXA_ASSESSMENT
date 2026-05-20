from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.dependencies import get_db
from app.models.auth import Role, User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import ROLE_HIERARCHY

security_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        claims = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if claims.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user_id = claims.get("sub")
    org_id = claims.get("org_id")
    if not user_id or not org_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")

    repo = UserRepository(session)
    user = await repo.get_by_id(UUID(str(user_id)))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")

    if str(user.organization_id) != str(org_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant mismatch")

    return user


def require_roles(*allowed_roles: Role) -> Callable:
    async def role_guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return role_guard


def require_minimum_role(min_role: Role) -> Callable:
    async def hierarchy_guard(current_user: User = Depends(get_current_user)) -> User:
        if ROLE_HIERARCHY[current_user.role] < ROLE_HIERARCHY[min_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role level")
        return current_user

    return hierarchy_guard

