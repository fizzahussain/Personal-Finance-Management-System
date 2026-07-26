import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from personal_finance_analytics_system.exceptions import (
    FinanceError,
)

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_SECRET_KEY = os.getenv(
    "FINANCE_JWT_SECRET_KEY",
    "development-secret-change-before-production",
)

password_hash = PasswordHash.recommended()


class AuthenticationError(FinanceError):
    """Represent an authentication failure"""


def hash_password(password: str) -> str:
    """Hash a plain-text password"""
    if not isinstance(password, str):
        raise AuthenticationError(
            "Password must be text"
        )

    if len(password) < 8:
        raise AuthenticationError(
            "Password must contain at least 8 characters"
        )

    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its stored hash"""
    try:
        return password_hash.verify(
            password,
            hashed_password,
        )
    except (TypeError, ValueError):
        return False


def create_access_token(
    user_id: int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed access token"""
    if user_id <= 0:
        raise AuthenticationError(
            "User ID must be greater than zero"
        )

    expires_at = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
        "iat": datetime.now(UTC),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> int:
    """Return the user ID stored in an access token"""
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        subject = payload.get("sub")

        if subject is None:
            raise AuthenticationError(
                "Access token is invalid"
            )

        user_id = int(subject)

        if user_id <= 0:
            raise AuthenticationError(
                "Access token is invalid"
            )

        return user_id

    except (
        InvalidTokenError,
        TypeError,
        ValueError,
    ) as error:
        raise AuthenticationError(
            "Access token is invalid or expired"
        ) from error