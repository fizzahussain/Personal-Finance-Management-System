from collections.abc import Iterator
from datetime import date
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


def set_latest_report_date(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Set a stable latest permitted report date"""
    monkeypatch.setattr(
        ReportService,
        "get_latest_report_end_date",
        staticmethod(
            lambda today=None: date(2026, 6, 23)
        ),
    )


def test_get_empty_monthly_report(
    client: TestClient,
) -> None:
    """Return an empty monthly report"""
    response = client.get(
        "/api/v1/reports/monthly/2026-07"
    )

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

    response = client.get(
        "/api/v1/reports/monthly/2026-07"
    )

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

    response = client.get(
        "/api/v1/reports/monthly/2026-07"
    )

    assert response.status_code == 200
    assert response.json()["income"] == 0.0


def test_rejects_invalid_report_month(
    client: TestClient,
) -> None:
    """Reject an invalid report month"""
    response = client.get(
        "/api/v1/reports/monthly/invalid-month"
    )

    assert response.status_code == 422


def test_get_date_range_report(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return report calculations for a date range"""
    set_latest_report_date(monkeypatch)

    service = app.dependency_overrides[
        get_report_service
    ]()

    service.transaction_service.create_transaction(
        Transaction(
            amount=5000,
            transaction_type="income",
            category="Salary",
            description="Monthly salary",
            transaction_date="2026-06-01",
        )
    )

    service.transaction_service.create_transaction(
        Transaction(
            amount=500,
            transaction_type="expense",
            category="Food",
            description="Groceries",
            transaction_date="2026-06-10",
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

    response = client.get(
        "/api/v1/reports",
        params={
            "start_date": "2026-06-01",
            "end_date": "2026-06-23",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "start_date": "2026-06-01",
        "end_date": "2026-06-23",
        "income": 5000.0,
        "expenses": 500.0,
        "balance": 4500.0,
        "savings_rate": 90.0,
        "spending_by_category": {
            "Food": 500.0,
        },
    }


def test_date_range_report_ignores_outside_dates(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ignore transactions outside the selected date range"""
    set_latest_report_date(monkeypatch)

    service = app.dependency_overrides[
        get_report_service
    ]()

    service.transaction_service.create_transaction(
        Transaction(
            amount=1000,
            transaction_type="income",
            category="Salary",
            description="May salary",
            transaction_date="2026-05-01",
        )
    )

    response = client.get(
        "/api/v1/reports",
        params={
            "start_date": "2026-06-01",
            "end_date": "2026-06-23",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "start_date": "2026-06-01",
        "end_date": "2026-06-23",
        "income": 0.0,
        "expenses": 0.0,
        "balance": 0.0,
        "savings_rate": 0.0,
        "spending_by_category": {},
    }


def test_rejects_reversed_report_date_range(
    client: TestClient,
) -> None:
    """Reject a reversed report date range"""
    response = client.get(
        "/api/v1/reports",
        params={
            "start_date": "2026-06-23",
            "end_date": "2026-06-01",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Start date cannot be after end date",
    }


def test_rejects_missing_report_dates(
    client: TestClient,
) -> None:
    """Reject missing report date parameters"""
    response = client.get("/api/v1/reports")

    assert response.status_code == 422


def test_rejects_report_after_latest_date(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject a report ending after the latest date"""
    set_latest_report_date(monkeypatch)

    response = client.get(
        "/api/v1/reports",
        params={
            "start_date": "2026-06-01",
            "end_date": "2026-06-24",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "End date cannot be later than 2026-06-23"
        ),
    }


def test_accepts_report_through_latest_date(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Accept a report ending on the latest permitted date"""
    set_latest_report_date(monkeypatch)

    response = client.get(
        "/api/v1/reports",
        params={
            "start_date": "2026-06-01",
            "end_date": "2026-06-23",
        },
    )

    assert response.status_code == 200


def test_download_csv_report(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Download a CSV report"""
    set_latest_report_date(monkeypatch)

    response = client.get(
        "/api/v1/reports/download",
        params={
            "start_date": "2026-06-01",
            "end_date": "2026-06-23",
            "format": "csv",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/csv"
    )
    assert "attachment;" in response.headers[
        "content-disposition"
    ]
    assert (
        "financial-report-2026-06-01-2026-06-23.csv"
        in response.headers["content-disposition"]
    )
    assert "start_date,end_date" in response.text


def test_download_json_report(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Download a JSON report"""
    set_latest_report_date(monkeypatch)

    response = client.get(
        "/api/v1/reports/download",
        params={
            "start_date": "2026-06-01",
            "end_date": "2026-06-23",
            "format": "json",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/json"
    )
    assert "attachment;" in response.headers[
        "content-disposition"
    ]
    assert (
        "financial-report-2026-06-01-2026-06-23.json"
        in response.headers["content-disposition"]
    )
    assert response.json() == {
        "start_date": "2026-06-01",
        "end_date": "2026-06-23",
        "income": 0,
        "expenses": 0,
        "balance": 0,
        "savings_rate": 0.0,
        "spending_by_category": {},
    }


def test_download_rejects_late_end_date(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject a download ending after the latest date"""
    set_latest_report_date(monkeypatch)

    response = client.get(
        "/api/v1/reports/download",
        params={
            "start_date": "2026-06-01",
            "end_date": "2026-06-24",
            "format": "csv",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "End date cannot be later than 2026-06-23"
        ),
    }


def test_rejects_invalid_report_format(
    client: TestClient,
) -> None:
    """Reject an unsupported report format"""
    response = client.get(
        "/api/v1/reports/download",
        params={
            "start_date": "2026-06-01",
            "end_date": "2026-06-23",
            "format": "pdf",
        },
    )

    assert response.status_code == 422