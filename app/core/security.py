"""Security utilities — JWT token service and password hashing (Strategy pattern)."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str: ...

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool: ...


class BcryptPasswordHasher(PasswordHasher):
    """Concrete strategy for bcrypt password hashing."""

    def hash(self, plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )


class TokenService:
    """Encapsulates JWT creation and validation."""

    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm

    def create_access_token(
        self,
        subject: str,
        *,
        organization_id: int | None = None,
        role: str | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
        )
        payload: dict = {"sub": subject, "exp": expire}
        if organization_id is not None:
            payload["org_id"] = organization_id
        if role:
            payload["role"] = role
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            return None


password_hasher = BcryptPasswordHasher()
token_service = TokenService(secret_key=settings.secret_key)
