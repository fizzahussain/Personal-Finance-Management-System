from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction
from personal_finance_analytics_system.transaction_filter import (
    TransactionFilter,
)


class TransactionService:
    """Manage transaction workflows"""

    def __init__(
        self,
        storage: SqliteStorage,
    ) -> None:
        self.storage = storage

    def list_transactions(
        self,
        category: str | None = None,
        transaction_type: str | None = None,
        transaction_date: str | None = None,
        minimum_amount: float | None = None,
        maximum_amount: float | None = None,
    ) -> list[Transaction]:
        """Return transactions matching the filters"""
        transactions = self.storage.load_transactions()

        if category is not None:
            transactions = TransactionFilter.by_category(
                transactions,
                category,
            )

        if transaction_type is not None:
            transactions = TransactionFilter.by_type(
                transactions,
                transaction_type,
            )

        if transaction_date is not None:
            transactions = TransactionFilter.by_date(
                transactions,
                transaction_date,
            )

        if (
            minimum_amount is not None
            or maximum_amount is not None
        ):
            transactions = TransactionFilter.by_amount_range(
                transactions,
                minimum_amount,
                maximum_amount,
            )

        return transactions

    def get_transaction(
        self,
        transaction_id: int,
    ) -> Transaction | None:
        """Return one transaction by ID"""
        return self.storage.get_transaction(transaction_id)

    def create_transaction(
        self,
        transaction: Transaction,
    ) -> Transaction:
        """Create and store a transaction"""
        return self.storage.insert_transaction(transaction)

    

    def get_summary(self) -> dict[str, float | int]:
        """Return the transaction summary"""
        transactions = self.storage.load_transactions()

        total_income = sum(
            transaction.amount
            for transaction in transactions
            if transaction.transaction_type == "income"
        )

        total_expenses = sum(
            transaction.amount
            for transaction in transactions
            if transaction.transaction_type == "expense"
        )

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": total_income - total_expenses,
            "transaction_count": len(transactions),
        }