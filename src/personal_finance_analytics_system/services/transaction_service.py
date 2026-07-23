from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction


class TransactionService:
    """Manage transaction workflows"""

    def __init__(
        self,
        storage: SqliteStorage,
    ) -> None:
        self.storage = storage

    def list_transactions(
        self,
    ) -> list[Transaction]:
        """Return all stored transactions"""
        return self.storage.load_transactions()

    def create_transaction(
        self,
        transaction: Transaction,
    ) -> Transaction:
        """Create and store a transaction"""
        transactions = self.storage.load_transactions()
        transactions.append(transaction)

        self.storage.save_transactions(transactions)

        return transaction