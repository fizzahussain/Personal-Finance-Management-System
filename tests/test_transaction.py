import pytest

from personal_finance_analytics_system.exceptions import (
    InvalidTransactionError,
)
from personal_finance_analytics_system.transaction import Transaction


def test_income_transaction() -> None:
    """Create an income transaction"""
    transaction = Transaction(
        5000,
        "income",
        "Salary",
        "Monthly salary",
    )

    assert transaction.amount == 5000
    assert transaction.get_signed_amount() == 5000


def test_expense_transaction() -> None:
    """Create an expense transaction"""
    transaction = Transaction(
        200,
        "expense",
        "Food",
        "Lunch",
    )

    assert transaction.get_signed_amount() == -200


def test_invalid_amount() -> None:
    """Reject an invalid amount"""
    with pytest.raises(
        InvalidTransactionError,
        match="Amount must be greater than zero",
    ):
        Transaction(
            0,
            "expense",
            "Food",
            "Lunch",
        )