import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models.auth import Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _create_token(
    *,
    subject: str,
    org_id: str,
    role: Role,
    token_type: str,
    expires_delta: timedelta,
    jti: str,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "org_id": org_id,
        "role": role.value,
        "type": token_type,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(*, user_id: UUID, org_id: UUID, role: Role) -> tuple[str, int]:
    expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = _create_token(
        subject=str(user_id),
        org_id=str(org_id),
        role=role,
        token_type="access",
        expires_delta=expires,
        jti=secrets.token_hex(16),
    )
    return token, int(expires.total_seconds())


def create_refresh_token(*, user_id: UUID, org_id: UUID, role: Role) -> tuple[str, str, datetime]:
    expires = timedelta(days=settings.refresh_token_expire_days)
    jti = secrets.token_hex(24)
    token = _create_token(
        subject=str(user_id),
        org_id=str(org_id),
        role=role,
        token_type="refresh",
        expires_delta=expires,
        jti=jti,
    )
    return token, jti, datetime.now(UTC) + expires


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

