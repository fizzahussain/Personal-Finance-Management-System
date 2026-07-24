from datetime import timedelta

import pytest

from personal_finance_analytics_system.auth import (
    AuthenticationError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hashes_and_verifies_password() -> None:
    """Hash and verify a password"""
    password = "secure-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(
        password,
        hashed_password,
    )


def test_rejects_incorrect_password() -> None:
    """Reject an incorrect password"""
    hashed_password = hash_password(
        "secure-password"
    )

    assert not verify_password(
        "incorrect-password",
        hashed_password,
    )


def test_rejects_short_password() -> None:
    """Reject a password shorter than eight characters"""
    with pytest.raises(
        AuthenticationError,
        match="at least 8 characters",
    ):
        hash_password("short")


def test_creates_and_decodes_access_token() -> None:
    """Create and decode an access token"""
    token = create_access_token(user_id=42)

    assert decode_access_token(token) == 42


def test_rejects_invalid_access_token() -> None:
    """Reject an invalid access token"""
    with pytest.raises(
        AuthenticationError,
        match="invalid or expired",
    ):
        decode_access_token("invalid-token")


def test_rejects_expired_access_token() -> None:
    """Reject an expired access token"""
    token = create_access_token(
        user_id=42,
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(
        AuthenticationError,
        match="invalid or expired",
    ):
        decode_access_token(token)


def test_rejects_nonpositive_token_user_id() -> None:
    """Reject a nonpositive token user ID"""
    with pytest.raises(
        AuthenticationError,
        match="greater than zero",
    ):
        create_access_token(user_id=0)