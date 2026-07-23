from personal_finance_analytics_system.transaction import Transaction
from personal_finance_analytics_system.transaction_filter import (
    TransactionFilter,
)


def create_transactions() -> list[Transaction]:
    """Create transactions for tests"""
    return [
        Transaction(
            5000,
            "income",
            "Salary",
            "Monthly salary",
            "2026-07-01",
        ),
        Transaction(
            200,
            "expense",
            "Food",
            "Groceries",
            "2026-07-02",
        ),
        Transaction(
            50,
            "expense",
            "Food",
            "Lunch",
            "2026-07-03",
        ),
        Transaction(
            100,
            "expense",
            "Transport",
            "Bus pass",
            "2026-07-04",
        ),
    ]


def test_filter_by_category() -> None:
    """Filter by category"""
    transactions = create_transactions()

    filtered = TransactionFilter.by_category(
        transactions,
        "food",
    )

    assert len(filtered) == 2
    assert all(
        transaction.category.casefold() == "food"
        for transaction in filtered
    )


def test_filter_by_type() -> None:
    """Filter by transaction type"""
    transactions = create_transactions()

    filtered = TransactionFilter.by_type(
        transactions,
        "expense",
    )

    assert len(filtered) == 3
    assert all(
        transaction.transaction_type == "expense"
        for transaction in filtered
    )


def test_filter_by_date() -> None:
    """Filter by date"""
    transactions = create_transactions()

    filtered = TransactionFilter.by_date(
        transactions,
        "2026-07-02",
    )

    assert len(filtered) == 1
    assert filtered[0].description == "Groceries"


def test_filter_by_minimum_amount() -> None:
    """Filter by minimum amount"""
    transactions = create_transactions()

    filtered = TransactionFilter.by_amount_range(
        transactions,
        minimum_amount=100,
    )

    assert len(filtered) == 3


def test_filter_by_maximum_amount() -> None:
    """Filter by maximum amount"""
    transactions = create_transactions()

    filtered = TransactionFilter.by_amount_range(
        transactions,
        maximum_amount=100,
    )

    assert len(filtered) == 2


def test_filter_by_amount_range() -> None:
    """Filter by minimum and maximum amount"""
    transactions = create_transactions()

    filtered = TransactionFilter.by_amount_range(
        transactions,
        minimum_amount=50,
        maximum_amount=200,
    )

    assert len(filtered) == 3