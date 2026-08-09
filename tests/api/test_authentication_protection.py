from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from personal_finance_analytics_system.api import dependencies
from personal_finance_analytics_system.api.app import app
from personal_finance_analytics_system.api.routers import auth


@pytest.fixture
def client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    """Provide an API client with temporary storage"""
    database_path = tmp_path / "finance.db"

    monkeypatch.setattr(
        dependencies,
        "DATABASE_PATH",
        database_path,
    )
    monkeypatch.setattr(
        auth,
        "DATABASE_PATH",
        database_path,
    )

    with TestClient(app) as test_client:
        yield test_client


def register_and_login(
    client: TestClient,
    email: str,
) -> str:
    """Register a user and return an access token"""
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secure-password",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "secure-password",
        },
    )

    assert login_response.status_code == 200

    return str(
        login_response.json()["access_token"]
    )


def authorization_headers(
    token: str,
) -> dict[str, str]:
    """Return bearer authorization headers"""
    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/transactions",
        "/api/v1/transactions/summary",
        "/api/v1/budgets",
        "/api/v1/budgets/status",
        (
            "/api/v1/reports"
            "?start_date=2026-06-01"
            "&end_date=2026-06-23"
        ),
    ],
)
def test_protected_endpoints_require_authentication(
    client: TestClient,
    path: str,
) -> None:
    """Require authentication for finance endpoints"""
    response = client.get(path)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication is required",
    }


def test_rejects_invalid_bearer_token(
    client: TestClient,
) -> None:
    """Reject an invalid bearer token"""
    response = client.get(
        "/api/v1/transactions",
        headers=authorization_headers(
            "invalid-token"
        ),
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Access token is invalid or expired",
    }


def test_returns_authenticated_user(
    client: TestClient,
) -> None:
    """Return the user represented by the token"""
    token = register_and_login(
        client,
        "person@example.com",
    )

    response = client.get(
        "/api/v1/auth/me",
        headers=authorization_headers(token),
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "email": "person@example.com",
    }


def test_users_cannot_see_each_others_transactions(
    client: TestClient,
) -> None:
    """Keep transaction data isolated by user"""
    first_token = register_and_login(
        client,
        "first@example.com",
    )
    second_token = register_and_login(
        client,
        "second@example.com",
    )

    create_response = client.post(
        "/api/v1/transactions",
        headers=authorization_headers(
            first_token
        ),
        json={
            "amount": 500,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": "2026-06-10",
        },
    )

    assert create_response.status_code == 201

    first_response = client.get(
        "/api/v1/transactions",
        headers=authorization_headers(
            first_token
        ),
    )
    second_response = client.get(
        "/api/v1/transactions",
        headers=authorization_headers(
            second_token
        ),
    )

    assert len(first_response.json()) == 1
    assert second_response.json() == []


def test_users_cannot_see_each_others_budgets(
    client: TestClient,
) -> None:
    """Keep budget data isolated by user"""
    first_token = register_and_login(
        client,
        "first@example.com",
    )
    second_token = register_and_login(
        client,
        "second@example.com",
    )

    create_response = client.put(
        "/api/v1/budgets/categories/Food",
        headers=authorization_headers(
            first_token
        ),
        json={
            "amount": 500,
        },
    )

    assert create_response.status_code == 200

    first_response = client.get(
        "/api/v1/budgets",
        headers=authorization_headers(
            first_token
        ),
    )
    second_response = client.get(
        "/api/v1/budgets",
        headers=authorization_headers(
            second_token
        ),
    )

    assert first_response.json() == [
        {
            "category": "food",
            "amount": 500.0,
        }
    ]
    assert second_response.json() == []