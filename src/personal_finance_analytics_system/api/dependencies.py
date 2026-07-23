from pathlib import Path

from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)

DATABASE_PATH = Path("data/transactions.db")


def get_transaction_service() -> TransactionService:
    """Provide the transaction service"""
    storage = SqliteStorage(str(DATABASE_PATH))

    return TransactionService(storage)