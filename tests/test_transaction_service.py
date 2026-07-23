from pathlib import Path

from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction


def test_create_and_list_transactions(
    tmp_path: Path,
) -> None:
    """Create and return stored transactions"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    service = TransactionService(storage)

    transaction = Transaction(
        amount=250,
        transaction_type="expense",
        category="Food",
        description="Groceries",
        transaction_date="2026-07-23",
    )

    created_transaction = service.create_transaction(
        transaction
    )

    transactions = service.list_transactions()

    assert created_transaction is transaction
    assert len(transactions) == 1
    assert transactions[0].amount == 250
    assert transactions[0].transaction_type == "expense"
    assert transactions[0].category == "Food"
    assert transactions[0].description == "Groceries"
    assert (
        transactions[0].transaction_date
        == "2026-07-23"
    )

def test_get_transaction_summary(
    tmp_path: Path,
) -> None:
    """Calculate transaction totals"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    service = TransactionService(storage)

    service.create_transaction(
        Transaction(
            amount=5000,
            transaction_type="income",
            category="Salary",
            description="Monthly salary",
            transaction_date="2026-07-01",
        )
    )

    service.create_transaction(
        Transaction(
            amount=500,
            transaction_type="expense",
            category="Food",
            description="Groceries",
            transaction_date="2026-07-02",
        )
    )

    service.create_transaction(
        Transaction(
            amount=250,
            transaction_type="expense",
            category="Transport",
            description="Travel",
            transaction_date="2026-07-03",
        )
    )

    summary = service.get_summary()

    assert summary == {
        "total_income": 5000,
        "total_expenses": 750,
        "balance": 4250,
        "transaction_count": 3,
    }

def test_get_empty_transaction_summary(
    tmp_path: Path,
) -> None:
    """Return zero totals without transactions"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    service = TransactionService(storage)

    summary = service.get_summary()

    assert summary == {
        "total_income": 0,
        "total_expenses": 0,
        "balance": 0,
        "transaction_count": 0,
    }