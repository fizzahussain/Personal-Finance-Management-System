from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from personal_finance_analytics_system.api.app import app
from personal_finance_analytics_system.api.dependencies import (
    get_transaction_service,
)
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)


@pytest.fixture
def client(
    tmp_path: Path,
) -> Iterator[TestClient]:
    """Provide an API client with temporary storage"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    service = TransactionService(storage)

    app.dependency_overrides[
        get_transaction_service
    ] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_list_transactions_is_initially_empty(
    client: TestClient,
) -> None:
    """Return an empty transaction list"""
    response = client.get("/transactions")

    assert response.status_code == 200
    assert response.json() == []


def test_create_transaction(
    client: TestClient,
) -> None:
    """Create a transaction"""
    response = client.post(
        "/transactions",
        json={
            "amount": 250,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": "2026-07-23",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "amount": 250.0,
        "transaction_type": "expense",
        "category": "Food",
        "description": "Groceries",
        "transaction_date": "2026-07-23",
    }


def test_created_transaction_is_returned(
    client: TestClient,
) -> None:
    """Return a previously created transaction"""
    client.post(
        "/transactions",
        json={
            "amount": 5000,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": "2026-07-01",
        },
    )

    response = client.get("/transactions")

    assert response.status_code == 200
    assert response.json() == [
        {
            "amount": 5000.0,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": "2026-07-01",
        }
    ]


def test_rejects_invalid_amount(
    client: TestClient,
) -> None:
    """Reject a non-positive amount"""
    response = client.post(
        "/transactions",
        json={
            "amount": 0,
            "transaction_type": "expense",
            "category": "Food",
            "description": "",
            "transaction_date": "2026-07-23",
        },
    )

    assert response.status_code == 422


def test_rejects_invalid_transaction_type(
    client: TestClient,
) -> None:
    """Reject an invalid transaction type"""
    response = client.post(
        "/transactions",
        json={
            "amount": 100,
            "transaction_type": "transfer",
            "category": "Other",
            "description": "",
            "transaction_date": "2026-07-23",
        },
    )

    assert response.status_code == 422


def test_rejects_empty_category(
    client: TestClient,
) -> None:
    """Reject an empty category"""
    response = client.post(
        "/transactions",
        json={
            "amount": 100,
            "transaction_type": "expense",
            "category": "   ",
            "description": "",
            "transaction_date": "2026-07-23",
        },
    )

    assert response.status_code == 422


def test_rejects_invalid_date(
    client: TestClient,
) -> None:
    """Reject an invalid transaction date"""
    response = client.post(
        "/transactions",
        json={
            "amount": 100,
            "transaction_type": "expense",
            "category": "Food",
            "description": "",
            "transaction_date": "23-07-2026",
        },
    )

    assert response.status_code == 422

def test_get_empty_transaction_summary(
    client: TestClient,
) -> None:
    """Return an empty transaction summary"""
    response = client.get("/transactions/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_income": 0.0,
        "total_expenses": 0.0,
        "balance": 0.0,
        "transaction_count": 0,
    }

def test_get_transaction_summary(
    client: TestClient,
) -> None:
    """Return calculated transaction totals"""
    client.post(
        "/transactions",
        json={
            "amount": 5000,
            "transaction_type": "income",
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": "2026-07-01",
        },
    )

    client.post(
        "/transactions",
        json={
            "amount": 750,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": "2026-07-02",
        },
    )

    response = client.get("/transactions/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_income": 5000.0,
        "total_expenses": 750.0,
        "balance": 4250.0,
        "transaction_count": 2,
    }

