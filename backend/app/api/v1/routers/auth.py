from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user, require_minimum_role
from app.dependencies import get_db
from app.models.auth import Role, User
from app.schemas.auth import (
    AuthResponse,
    InviteUserRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    SignupRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, session: AsyncSession = Depends(get_db)) -> AuthResponse:
    service = AuthService(session)
    return await service.signup(payload)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)) -> AuthResponse:
    service = AuthService(session)
    return await service.login(payload)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    service = AuthService(session)
    return await service.refresh(payload)


@router.post("/invite", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    payload: InviteUserRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_minimum_role(Role.ADMIN)),
) -> UserResponse:
    service = AuthService(session)
    return await service.invite_user(actor=current_user, payload=payload)


@router.get("/me", response_model=UserResponse)
async def get_me(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    service = AuthService(session)
    return await service.get_current_user(current_user)

