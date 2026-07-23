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