import pytest

from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.exceptions import (
    InvalidBudgetError,
    InvalidTransactionError,
)
from personal_finance_analytics_system.transaction import Transaction


def test_reject_zero_transaction_amount() -> None:
    """Reject a zero transaction amount"""
    with pytest.raises(InvalidTransactionError):
        Transaction(
            0,
            "expense",
            "Food",
        )


def test_reject_invalid_transaction_type() -> None:
    """Reject an invalid transaction type"""
    with pytest.raises(InvalidTransactionError):
        Transaction(
            100,
            "payment",
            "Food",
        )


def test_reject_empty_transaction_category() -> None:
    """Reject an empty transaction category"""
    with pytest.raises(InvalidTransactionError):
        Transaction(
            100,
            "expense",
            "",
        )


def test_reject_invalid_transaction_date() -> None:
    """Reject an invalid transaction date"""
    with pytest.raises(InvalidTransactionError):
        Transaction(
            100,
            "expense",
            "Food",
            transaction_date="30-07-2026",
        )


def test_reject_invalid_budget_amount() -> None:
    """Reject an invalid budget amount"""
    budget_manager = BudgetManager()

    with pytest.raises(InvalidBudgetError):
        budget_manager.set_budget(
            "Food",
            -100,
        )


def test_reject_empty_budget_category() -> None:
    """Reject an empty budget category"""
    budget_manager = BudgetManager()

    with pytest.raises(InvalidBudgetError):
        budget_manager.set_budget(
            "",
            100,
        )