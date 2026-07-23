import pytest

from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.transaction import Transaction


def test_set_and_get_budget() -> None:
    """Set and get a category budget"""
    budget_manager = BudgetManager()

    budget_manager.set_budget("Food", 500)

    assert budget_manager.get_budget("Food") == 500


def test_category_matching_ignores_case() -> None:
    """Match categories without case differences"""
    budget_manager = BudgetManager()

    budget_manager.set_budget("Food", 500)

    assert budget_manager.get_budget("food") == 500
    assert budget_manager.get_budget("FOOD") == 500


def test_get_category_spending() -> None:
    """Calculate category spending"""
    budget_manager = BudgetManager()

    transactions = [
        Transaction(
            200,
            "expense",
            "Food",
            "Groceries",
        ),
        Transaction(
            50,
            "expense",
            "food",
            "Lunch",
        ),
        Transaction(
            1000,
            "income",
            "Salary",
            "",
        ),
        Transaction(
            100,
            "expense",
            "Transport",
            "Bus pass",
        ),
    ]

    spending = budget_manager.get_spending(
        "Food",
        transactions,
    )

    assert spending == 250


def test_get_remaining_budget() -> None:
    """Calculate remaining category budget"""
    budget_manager = BudgetManager()
    budget_manager.set_budget("Food", 500)

    transactions = [
        Transaction(
            200,
            "expense",
            "Food",
            "Groceries",
        ),
        Transaction(
            50,
            "expense",
            "Food",
            "Lunch",
        ),
    ]

    remaining = budget_manager.get_remaining_budget(
        "Food",
        transactions,
    )

    assert remaining == 250


def test_remaining_budget_can_be_negative() -> None:
    """Show when a category budget is exceeded"""
    budget_manager = BudgetManager()
    budget_manager.set_budget("Food", 100)

    transactions = [
        Transaction(
            150,
            "expense",
            "Food",
            "Groceries",
        ),
    ]

    remaining = budget_manager.get_remaining_budget(
        "Food",
        transactions,
    )

    assert remaining == -50


def test_missing_budget_returns_none() -> None:
    """Return none when no budget exists"""
    budget_manager = BudgetManager()

    remaining = budget_manager.get_remaining_budget(
        "Food",
        [],
    )

    assert remaining is None


def test_reject_invalid_budget_amount() -> None:
    """Reject an invalid budget amount"""
    budget_manager = BudgetManager()

    with pytest.raises(
        ValueError,
        match="Budget must be greater than zero",
    ):
        budget_manager.set_budget("Food", 0)


def test_reject_empty_category() -> None:
    """Reject an empty category"""
    budget_manager = BudgetManager()

    with pytest.raises(
        ValueError,
        match="Category cannot be empty",
    ):
        budget_manager.set_budget("", 500)