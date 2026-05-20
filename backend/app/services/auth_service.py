from dataclasses import dataclass
import secrets
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api_key_hash import hash_api_key
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.auth import Organization, RefreshToken, Role, User
from app.repositories.organization_api_key_repository import OrganizationApiKeyRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    InviteUserRequest,
    LoginRequest,
    OrganizationResponse,
    RefreshTokenRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.events import CreateApiKeyRequest, CreateApiKeyResponse


ROLE_HIERARCHY = {
    Role.OWNER: 4,
    Role.ADMIN: 3,
    Role.ANALYST: 2,
    Role.VIEWER: 1,
}


@dataclass
class TokenBundle:
    access_token: str
    refresh_token: str
    access_expires_in: int


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.org_repo = OrganizationRepository(session)
        self.user_repo = UserRepository(session)
        self.refresh_repo = RefreshTokenRepository(session)
        self.api_key_repo = OrganizationApiKeyRepository(session)

    async def signup(self, payload: SignupRequest) -> AuthResponse:
        org = await self.org_repo.get_by_slug(payload.organization_slug)
        if org:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization slug already exists")

        organization = await self.org_repo.create(
            name=payload.organization_name.strip(),
            slug=payload.organization_slug.strip().lower(),
        )

        owner = await self.user_repo.create(
            organization_id=organization.id,
            email=payload.email,
            full_name=payload.full_name.strip(),
            hashed_password=hash_password(payload.password),
            role=Role.OWNER,
            is_active=True,
        )
        tokens = await self._issue_tokens(owner)
        return self._auth_response(owner, organization, tokens)

    async def login(self, payload: LoginRequest) -> AuthResponse:
        organization = await self.org_repo.get_by_slug(payload.organization_slug.strip().lower())
        if not organization or not organization.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        user = await self.user_repo.get_by_email_for_org(organization_id=organization.id, email=payload.email)
        if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        tokens = await self._issue_tokens(user)
        return self._auth_response(user, organization, tokens)

    async def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        claims = self._decode_expected_token(payload.refresh_token, expected_type="refresh")
        jti = str(claims["jti"])
        user_id = UUID(str(claims["sub"]))
        org_id = UUID(str(claims["org_id"]))

        stored = await self.refresh_repo.get_by_jti(jti)
        if not stored or not stored.is_active or stored.user_id != user_id or stored.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        if stored.token_hash != hash_token(payload.refresh_token):
            await self.refresh_repo.revoke(stored)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        await self.refresh_repo.revoke(stored)

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        tokens = await self._issue_tokens(user)
        return TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.access_expires_in,
        )

    async def invite_user(self, *, actor: User, payload: InviteUserRequest) -> UserResponse:
        if ROLE_HIERARCHY[actor.role] <= ROLE_HIERARCHY[payload.role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot invite user with equal or higher role",
            )

        existing = await self.user_repo.get_by_email_for_org(
            organization_id=actor.organization_id,
            email=payload.email,
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

        user = await self.user_repo.create(
            organization_id=actor.organization_id,
            email=payload.email,
            full_name=payload.full_name.strip(),
            hashed_password=hash_password(payload.password),
            role=payload.role,
            is_active=True,
        )
        return UserResponse.model_validate(user)

    async def get_current_user(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def create_api_key(self, actor: User, payload: CreateApiKeyRequest) -> CreateApiKeyResponse:
        plaintext = f"wk_live_{secrets.token_urlsafe(32)}"
        key_prefix = plaintext[:12]
        row = await self.api_key_repo.create(
            organization_id=actor.organization_id,
            name=payload.name.strip(),
            key_hash=hash_api_key(plaintext),
            key_prefix=key_prefix,
        )
        return CreateApiKeyResponse(id=row.id, api_key=plaintext, key_prefix=key_prefix, name=row.name)

    def _decode_expected_token(self, token: str, *, expected_type: str) -> dict:
        try:
            claims = decode_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
        if claims.get("type") != expected_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return claims

    async def _issue_tokens(self, user: User) -> TokenBundle:
        access_token, expires_in = create_access_token(
            user_id=user.id,
            org_id=user.organization_id,
            role=user.role,
        )
        refresh_token, jti, expires_at = create_refresh_token(
            user_id=user.id,
            org_id=user.organization_id,
            role=user.role,
        )
        await self.refresh_repo.create(
            user_id=user.id,
            organization_id=user.organization_id,
            jti=jti,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )
        return TokenBundle(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_in=expires_in,
        )

    def _auth_response(self, user: User, organization: Organization, tokens: TokenBundle) -> AuthResponse:
        return AuthResponse(
            user=UserResponse.model_validate(user),
            organization=OrganizationResponse.model_validate(organization),
            tokens=TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                expires_in=tokens.access_expires_in,
            ),
        )

