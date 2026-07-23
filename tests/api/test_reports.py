from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from personal_finance_analytics_system.api.app import app
from personal_finance_analytics_system.api.dependencies import (
    get_report_service,
)
from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.services.report_service import (
    ReportService,
)
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction


@pytest.fixture
def client(
    tmp_path: Path,
) -> Iterator[TestClient]:
    """Provide an API client with temporary report storage"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    transaction_service = TransactionService(storage)

    service = ReportService(
        report_manager=ReportManager(),
        transaction_service=transaction_service,
    )

    app.dependency_overrides[
        get_report_service
    ] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_get_empty_monthly_report(
    client: TestClient,
) -> None:
    """Return an empty monthly report"""
    response = client.get("/reports/monthly/2026-07")

    assert response.status_code == 200
    assert response.json() == {
        "month": "2026-07",
        "income": 0.0,
        "expenses": 0.0,
        "balance": 0.0,
        "savings_rate": 0.0,
        "spending_by_category": {},
    }


def test_get_monthly_report(
    client: TestClient,
) -> None:
    """Return monthly report calculations"""
    service = app.dependency_overrides[
        get_report_service
    ]()

    service.transaction_service.create_transaction(
        Transaction(
            amount=5000,
            transaction_type="income",
            category="Salary",
            description="Monthly salary",
            transaction_date="2026-07-01",
        )
    )

    service.transaction_service.create_transaction(
        Transaction(
            amount=500,
            transaction_type="expense",
            category="Food",
            description="Groceries",
            transaction_date="2026-07-02",
        )
    )

    service.transaction_service.create_transaction(
        Transaction(
            amount=250,
            transaction_type="expense",
            category="Transport",
            description="Bus pass",
            transaction_date="2026-07-03",
        )
    )

    response = client.get("/reports/monthly/2026-07")

    assert response.status_code == 200
    assert response.json() == {
        "month": "2026-07",
        "income": 5000.0,
        "expenses": 750.0,
        "balance": 4250.0,
        "savings_rate": 85.0,
        "spending_by_category": {
            "Food": 500.0,
            "Transport": 250.0,
        },
    }


def test_monthly_report_ignores_other_months(
    client: TestClient,
) -> None:
    """Ignore transactions from other months"""
    service = app.dependency_overrides[
        get_report_service
    ]()

    service.transaction_service.create_transaction(
        Transaction(
            amount=3000,
            transaction_type="income",
            category="Salary",
            description="June salary",
            transaction_date="2026-06-01",
        )
    )

    response = client.get("/reports/monthly/2026-07")

    assert response.status_code == 200
    assert response.json()["income"] == 0.0


def test_rejects_invalid_report_month(
    client: TestClient,
) -> None:
    """Reject an invalid report month"""
    response = client.get(
        "/reports/monthly/invalid-month"
    )

    assert response.status_code == 422