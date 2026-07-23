import pytest

from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.transaction import Transaction


def create_transactions() -> list[Transaction]:
    """Create transactions for report tests"""
    return [
        Transaction(
            5000,
            "income",
            "Salary",
            "Monthly salary",
            "2026-07-01",
        ),
        Transaction(
            500,
            "expense",
            "Food",
            "Groceries",
            "2026-07-03",
        ),
        Transaction(
            200,
            "expense",
            "Transport",
            "Bus pass",
            "2026-07-05",
        ),
        Transaction(
            100,
            "expense",
            "Food",
            "Lunch",
            "2026-07-10",
        ),
        Transaction(
            4000,
            "income",
            "Salary",
            "Monthly salary",
            "2026-08-01",
        ),
    ]


def test_get_monthly_transactions() -> None:
    """Return transactions for one month"""
    report_manager = ReportManager()

    transactions = report_manager.get_monthly_transactions(
        create_transactions(),
        "2026-07",
    )

    assert len(transactions) == 4


def test_get_monthly_income() -> None:
    """Calculate monthly income"""
    report_manager = ReportManager()

    income = report_manager.get_monthly_income(
        create_transactions(),
        "2026-07",
    )

    assert income == 5000


def test_get_monthly_expenses() -> None:
    """Calculate monthly expenses"""
    report_manager = ReportManager()

    expenses = report_manager.get_monthly_expenses(
        create_transactions(),
        "2026-07",
    )

    assert expenses == 800


def test_get_monthly_balance() -> None:
    """Calculate monthly balance"""
    report_manager = ReportManager()

    balance = report_manager.get_monthly_balance(
        create_transactions(),
        "2026-07",
    )

    assert balance == 4200


def test_get_savings_rate() -> None:
    """Calculate monthly savings rate"""
    report_manager = ReportManager()

    savings_rate = report_manager.get_savings_rate(
        create_transactions(),
        "2026-07",
    )

    assert savings_rate == 84


def test_get_spending_by_category() -> None:
    """Calculate spending by category"""
    report_manager = ReportManager()

    spending = report_manager.get_spending_by_category(
        create_transactions(),
        "2026-07",
    )

    assert spending["Food"] == 600
    assert spending["Transport"] == 200


def test_invalid_month() -> None:
    """Reject an invalid month"""
    report_manager = ReportManager()

    with pytest.raises(
        ValueError,
        match="Month must use YYYY-MM format",
    ):
        report_manager.get_monthly_income(
            create_transactions(),
            "07-2026",
        )