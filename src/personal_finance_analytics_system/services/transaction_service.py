from personal_finance_analytics_system.cache import (
    TtlCache,
    application_cache,
)
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
        cache: TtlCache = application_cache,
    ) -> None:
        self.storage = storage
        self.cache = cache

    @property
    def cache_namespace(self) -> str:
        """Return the cache namespace for this user"""
        database_path = self.storage.file_path.resolve()

        return (
            f"{database_path}:"
            f"user:{self.storage.user_id}"
        )

    def invalidate_cache(self) -> None:
        """Delete cached data for the current user"""
        self.cache.delete_prefix(
            (self.cache_namespace,)
        )

    def list_transactions(
        self,
        category: str | None = None,
        transaction_type: str | None = None,
        transaction_date: str | None = None,
        minimum_amount: float | None = None,
        maximum_amount: float | None = None,
    ) -> list[Transaction]:
        """Return transactions matching the filters"""
        cache_key = (
            self.cache_namespace,
            "transactions",
            category,
            transaction_type,
            transaction_date,
            minimum_amount,
            maximum_amount,
        )

        cached_transactions = self.cache.get(
            cache_key
        )

        if cached_transactions is not None:
            return cached_transactions

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

        self.cache.set(
            cache_key,
            transactions,
        )

        return transactions

    def get_transaction(
        self,
        transaction_id: int,
    ) -> Transaction | None:
        """Return one transaction by ID"""
        cache_key = (
            self.cache_namespace,
            "transaction",
            transaction_id,
        )

        cached_transaction = self.cache.get(
            cache_key
        )

        if cached_transaction is not None:
            return cached_transaction

        transaction = self.storage.get_transaction(
            transaction_id
        )

        if transaction is not None:
            self.cache.set(
                cache_key,
                transaction,
            )

        return transaction

    def create_transaction(
        self,
        transaction: Transaction,
    ) -> Transaction:
        """Create and store a transaction"""
        created_transaction = (
            self.storage.insert_transaction(
                transaction
            )
        )

        self.invalidate_cache()

        return created_transaction

    def get_summary(self) -> dict[str, float | int]:
        """Return the transaction summary"""
        cache_key = (
            self.cache_namespace,
            "transaction-summary",
        )

        cached_summary = self.cache.get(cache_key)

        if cached_summary is not None:
            return cached_summary

        transactions = self.list_transactions()

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

        summary: dict[str, float | int] = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": total_income - total_expenses,
            "transaction_count": len(transactions),
        }

        self.cache.set(
            cache_key,
            summary,
        )

        return summary