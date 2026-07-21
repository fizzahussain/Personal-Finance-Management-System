"""Tests for the transaction model."""
import pytest
from personal_finance_analytics_system.transaction import Transaction


def test_income_transaction() -> None:
    transaction = Transaction(
        5000,
        "income",
        "Salary",
        "Monthly salary",
    )

    assert transaction.amount == 5000
    assert transaction.get_signed_amount() == 5000


def test_expense_transaction() -> None:
    transaction = Transaction(
        200,
        "expense",
        "Food",
        "Lunch",
    )

    assert transaction.get_signed_amount() == -200


def test_invalid_amount() -> None:
    with pytest.raises(ValueError):
        Transaction(
            0,
            "expense",
            "Food",
            "Lunch",
        )