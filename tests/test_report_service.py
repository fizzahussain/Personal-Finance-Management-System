from datetime import date
from pathlib import Path

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


def create_report_service(
    tmp_path: Path,
) -> ReportService:
    """Create a report service with temporary storage"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    transaction_service = TransactionService(storage)

    return ReportService(
        report_manager=ReportManager(),
        transaction_service=transaction_service,
    )


def test_get_empty_monthly_report(
    tmp_path: Path,
) -> None:
    """Return an empty monthly report"""
    service = create_report_service(tmp_path)

    report = service.get_monthly_report("2026-07")

    assert report == {
        "month": "2026-07",
        "income": 0,
        "expenses": 0,
        "balance": 0,
        "savings_rate": 0,
        "spending_by_category": {},
    }


def test_get_monthly_report(
    tmp_path: Path,
) -> None:
    """Return calculated monthly report values"""
    service = create_report_service(tmp_path)

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

    service.transaction_service.create_transaction(
        Transaction(
            amount=1000,
            transaction_type="income",
            category="Bonus",
            description="Previous month bonus",
            transaction_date="2026-06-30",
        )
    )

    report = service.get_monthly_report("2026-07")

    assert report == {
        "month": "2026-07",
        "income": 5000,
        "expenses": 750,
        "balance": 4250,
        "savings_rate": 85,
        "spending_by_category": {
            "Food": 500,
            "Transport": 250,
        },
    }


def test_rejects_invalid_report_month(
    tmp_path: Path,
) -> None:
    """Reject an invalid month"""
    service = create_report_service(tmp_path)

    try:
        service.get_monthly_report("July 2026")
    except ValueError as error:
        assert str(error)
    else:
        raise AssertionError("ValueError was not raised")

def test_get_latest_report_end_date() -> None:
    """Return the latest permitted report date"""
    result = ReportService.get_latest_report_end_date(
        date(2026, 7, 24)
    )

    assert result == date(2026, 6, 23)


def test_get_latest_report_end_date_in_january() -> None:
    """Return a permitted date in the previous December"""
    result = ReportService.get_latest_report_end_date(
        date(2026, 1, 10)
    )

    assert result == date(2025, 12, 9)

