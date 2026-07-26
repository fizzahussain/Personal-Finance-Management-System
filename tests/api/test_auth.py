from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from personal_finance_analytics_system.api.app import app
from personal_finance_analytics_system.api.routers import auth


@pytest.fixture
def client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    """Provide an API client with temporary user storage"""
    monkeypatch.setattr(
        auth,
        "DATABASE_PATH",
        tmp_path / "finance.db",
    )

    with TestClient(app) as test_client:
        yield test_client


def test_register_user(
    client: TestClient,
) -> None:
    """Register a new user"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Person@Example.com",
            "password": "secure-password",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "user_id": 1,
        "email": "person@example.com",
    }


def test_reject_duplicate_registration(
    client: TestClient,
) -> None:
    """Reject duplicate user registration"""
    payload = {
        "email": "person@example.com",
        "password": "secure-password",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )
    second_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_user(
    client: TestClient,
) -> None:
    """Login and return a bearer token"""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "person@example.com",
            "password": "secure-password",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "person@example.com",
            "password": "secure-password",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_reject_incorrect_password(
    client: TestClient,
) -> None:
    """Reject login with an incorrect password"""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "person@example.com",
            "password": "secure-password",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "person@example.com",
            "password": "incorrect-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Email or password is incorrect",
    }


def test_reject_unknown_user(
    client: TestClient,
) -> None:
    """Reject login for an unknown user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing@example.com",
            "password": "secure-password",
        },
    )

    assert response.status_code == 401


def test_reject_short_registration_password(
    client: TestClient,
) -> None:
    """Reject a short registration password"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "person@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422