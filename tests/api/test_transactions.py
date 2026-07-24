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
        "transaction_id": 1,
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
            "transaction_id": 1,
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


def test_rejects_missing_transaction_type(
    client: TestClient,
) -> None:
    """Reject a missing transaction type"""
    response = client.post(
        "/transactions",
        json={
            "amount": 100,
            "category": "Food",
            "description": "",
            "transaction_date": "2026-07-23",
        },
    )

    assert response.status_code == 422


def test_rejects_null_transaction_type(
    client: TestClient,
) -> None:
    """Reject a null transaction type"""
    response = client.post(
        "/transactions",
        json={
            "amount": 100,
            "transaction_type": None,
            "category": "Food",
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


def create_test_transaction(
    client: TestClient,
    amount: float,
    transaction_type: str,
    category: str,
    transaction_date: str,
) -> None:
    """Create a transaction through the API"""
    response = client.post(
        "/transactions",
        json={
            "amount": amount,
            "transaction_type": transaction_type,
            "category": category,
            "description": "",
            "transaction_date": transaction_date,
        },
    )

    assert response.status_code == 201


def test_filter_transactions_by_category(
    client: TestClient,
) -> None:
    """Filter transactions by category"""
    create_test_transaction(
        client,
        500,
        "expense",
        "Food",
        "2026-07-02",
    )
    create_test_transaction(
        client,
        250,
        "expense",
        "Transport",
        "2026-07-03",
    )

    response = client.get(
        "/transactions",
        params={"category": "Food"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "Food"


def test_filter_transactions_by_type(
    client: TestClient,
) -> None:
    """Filter transactions by type"""
    create_test_transaction(
        client,
        5000,
        "income",
        "Salary",
        "2026-07-01",
    )
    create_test_transaction(
        client,
        500,
        "expense",
        "Food",
        "2026-07-02",
    )

    response = client.get(
        "/transactions",
        params={"transaction_type": "expense"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert (
        response.json()[0]["transaction_type"]
        == "expense"
    )


def test_filter_transactions_by_date(
    client: TestClient,
) -> None:
    """Filter transactions by date"""
    create_test_transaction(
        client,
        500,
        "expense",
        "Food",
        "2026-07-02",
    )

    response = client.get(
        "/transactions",
        params={
            "transaction_date": "2026-07-02",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_transactions_by_amount_range(
    client: TestClient,
) -> None:
    """Filter transactions by amount range"""
    create_test_transaction(
        client,
        100,
        "expense",
        "Food",
        "2026-07-01",
    )
    create_test_transaction(
        client,
        500,
        "expense",
        "Transport",
        "2026-07-02",
    )
    create_test_transaction(
        client,
        1000,
        "income",
        "Salary",
        "2026-07-03",
    )

    response = client.get(
        "/transactions",
        params={
            "minimum_amount": 200,
            "maximum_amount": 700,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["amount"] == 500.0


def test_rejects_reversed_amount_range(
    client: TestClient,
) -> None:
    """Reject a reversed amount range"""
    response = client.get(
        "/transactions",
        params={
            "minimum_amount": 500,
            "maximum_amount": 100,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Minimum amount cannot exceed maximum amount"
    )


def test_rejects_invalid_filter_type(
    client: TestClient,
) -> None:
    """Reject an invalid transaction type filter"""
    response = client.get(
        "/transactions",
        params={
            "transaction_type": "transfer",
        },
    )

    assert response.status_code == 422


def test_rejects_invalid_filter_date(
    client: TestClient,
) -> None:
    """Reject an invalid transaction date filter"""
    response = client.get(
        "/transactions",
        params={
            "transaction_date": "02-07-2026",
        },
    )

    assert response.status_code == 422


def test_get_transaction_by_id(
    client: TestClient,
) -> None:
    """Return one transaction by ID"""
    created_response = client.post(
        "/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": "2026-07-23",
        },
    )

    transaction_id = created_response.json()[
        "transaction_id"
    ]

    response = client.get(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "transaction_id": transaction_id,
        "amount": 500.0,
        "transaction_type": "expense",
        "category": "Food",
        "description": "Groceries",
        "transaction_date": "2026-07-23",
    }


def test_get_missing_transaction(
    client: TestClient,
) -> None:
    """Return not found for a missing transaction"""
    response = client.get("/transactions/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Transaction not found",
    }


def test_update_transaction_is_not_allowed(
    client: TestClient,
) -> None:
    """Reject transaction updates"""
    created_response = client.post(
        "/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": "2026-07-23",
        },
    )

    transaction_id = created_response.json()[
        "transaction_id"
    ]

    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "amount": 750,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Updated",
            "transaction_date": "2026-07-24",
        },
    )

    assert response.status_code == 405


def test_delete_transaction_is_not_allowed(
    client: TestClient,
) -> None:
    """Reject transaction deletion"""
    created_response = client.post(
        "/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
            "category": "Food",
            "description": "Groceries",
            "transaction_date": "2026-07-23",
        },
    )

    transaction_id = created_response.json()[
        "transaction_id"
    ]

    response = client.delete(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 405