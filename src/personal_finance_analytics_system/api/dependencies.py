from pathlib import Path

from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.budget_storage import (
    BudgetStorage,
)
from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.services.budget_service import (
    BudgetService,
)
from personal_finance_analytics_system.services.report_service import (
    ReportService,
)
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


def get_budget_service() -> BudgetService:
    """Provide the budget service"""
    manager = BudgetManager()
    storage = BudgetStorage()

    return BudgetService(
        manager=manager,
        storage=storage,
    )

def get_report_service() -> ReportService:
    """Provide the report service"""
    transaction_service = get_transaction_service()

    return ReportService(
        report_manager=ReportManager(),
        transaction_service=transaction_service,
    )