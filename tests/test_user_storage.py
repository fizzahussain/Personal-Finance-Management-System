from pathlib import Path

import pytest

from personal_finance_analytics_system.exceptions import (
    StorageError,
)
from personal_finance_analytics_system.user import User
from personal_finance_analytics_system.user_storage import (
    UserStorage,
)


def test_create_and_get_user_by_email(
    tmp_path: Path,
) -> None:
    """Create and return a user by email"""
    storage = UserStorage(
        str(tmp_path / "finance.db")
    )

    created_user = storage.create_user(
        User(
            email="person@example.com",
            password_hash="hashed-password",
        )
    )

    assert created_user.user_id == 1

    stored_user = storage.get_user_by_email(
        "person@example.com"
    )

    assert stored_user is not None
    assert stored_user.user_id == 1
    assert stored_user.email == "person@example.com"
    assert stored_user.password_hash == "hashed-password"


def test_email_lookup_is_case_insensitive(
    tmp_path: Path,
) -> None:
    """Find users regardless of email casing"""
    storage = UserStorage(
        str(tmp_path / "finance.db")
    )

    storage.create_user(
        User(
            email="Person@Example.com",
            password_hash="hashed-password",
        )
    )

    stored_user = storage.get_user_by_email(
        "PERSON@EXAMPLE.COM"
    )

    assert stored_user is not None
    assert stored_user.email == "person@example.com"


def test_get_user_by_id(
    tmp_path: Path,
) -> None:
    """Return a user by ID"""
    storage = UserStorage(
        str(tmp_path / "finance.db")
    )

    created_user = storage.create_user(
        User(
            email="person@example.com",
            password_hash="hashed-password",
        )
    )

    assert created_user.user_id is not None

    stored_user = storage.get_user(
        created_user.user_id
    )

    assert stored_user is not None
    assert stored_user.email == "person@example.com"


def test_get_missing_user(
    tmp_path: Path,
) -> None:
    """Return none for a missing user"""
    storage = UserStorage(
        str(tmp_path / "finance.db")
    )

    assert storage.get_user(999) is None
    assert (
        storage.get_user_by_email(
            "missing@example.com"
        )
        is None
    )


def test_reject_duplicate_email(
    tmp_path: Path,
) -> None:
    """Reject a duplicate user email"""
    storage = UserStorage(
        str(tmp_path / "finance.db")
    )

    storage.create_user(
        User(
            email="person@example.com",
            password_hash="first-password",
        )
    )

    with pytest.raises(
        StorageError,
        match="already exists",
    ):
        storage.create_user(
            User(
                email="PERSON@example.com",
                password_hash="second-password",
            )
        )