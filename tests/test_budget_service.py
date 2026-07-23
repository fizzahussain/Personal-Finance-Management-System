from pathlib import Path

from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.services.budget_service import (
    BudgetService,
)
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction


class FakeBudgetStorage:
    """Store budgets in memory for tests"""

    def __init__(self) -> None:
        self.budgets: dict[str, float] = {}

    def load_budgets(self) -> dict[str, float]:
        """Return stored budgets"""
        return self.budgets.copy()

    def save_budgets(
        self,
        budgets: dict[str, float],
    ) -> None:
        """Save budgets"""
        self.budgets = budgets.copy()


def create_budget_service(
    tmp_path: Path,
    storage: FakeBudgetStorage | None = None,
) -> BudgetService:
    """Create a budget service with temporary storage"""
    database_path = tmp_path / "transactions.db"

    transaction_service = TransactionService(
        SqliteStorage(str(database_path))
    )

    return BudgetService(
        manager=BudgetManager(),
        storage=storage or FakeBudgetStorage(),
        transaction_service=transaction_service,
    )


def test_list_budgets_is_initially_empty(
    tmp_path: Path,
) -> None:
    """Return an empty budget collection"""
    service = create_budget_service(tmp_path)

    assert service.list_budgets() == {}


def test_set_category_budget(
    tmp_path: Path,
) -> None:
    """Create a category budget"""
    storage = FakeBudgetStorage()
    service = create_budget_service(
        tmp_path,
        storage,
    )

    amount = service.set_category_budget(
        category="Food",
        amount=500,
    )

    assert amount == 500
    assert service.list_budgets() == {
        "food": 500.0,
    }
    assert storage.budgets == {
        "food": 500.0,
    }


def test_update_category_budget(
    tmp_path: Path,
) -> None:
    """Update an existing category budget"""
    storage = FakeBudgetStorage()
    service = create_budget_service(
        tmp_path,
        storage,
    )

    service.set_category_budget(
        category="Food",
        amount=500,
    )

    service.set_category_budget(
        category="Food",
        amount=750,
    )

    assert service.list_budgets() == {
        "food": 750.0,
    }
    assert storage.budgets == {
        "food": 750.0,
    }


def test_load_saved_budgets(
    tmp_path: Path,
) -> None:
    """Load existing budgets from storage"""
    storage = FakeBudgetStorage()
    storage.budgets = {
        "Food": 500,
        "Transport": 300,
    }

    service = create_budget_service(
        tmp_path,
        storage,
    )

    assert service.list_budgets() == {
        "food": 500.0,
        "transport": 300.0,
    }


def test_get_budget_statuses(
    tmp_path: Path,
) -> None:
    """Return spending status for category budgets"""
    service = create_budget_service(tmp_path)

    service.set_category_budget(
        category="Food",
        amount=500,
    )

    service.transaction_service.create_transaction(
        Transaction(
            amount=350,
            transaction_type="expense",
            category="Food",
            description="Groceries",
            transaction_date="2026-07-23",
        )
    )

    statuses = service.get_budget_statuses()

    assert statuses == [
        {
            "category": "food",
            "budget": 500.0,
            "spending": 350.0,
            "remaining": 150.0,
            "percentage_used": 70.0,
            "status": "healthy",
        }
    ]


def test_get_exceeded_budget_status(
    tmp_path: Path,
) -> None:
    """Return exceeded status when spending is over budget"""
    service = create_budget_service(tmp_path)

    service.set_category_budget(
        category="Food",
        amount=500,
    )

    service.transaction_service.create_transaction(
        Transaction(
            amount=600,
            transaction_type="expense",
            category="Food",
            description="Groceries",
            transaction_date="2026-07-23",
        )
    )

    statuses = service.get_budget_statuses()

    assert statuses[0]["spending"] == 600.0
    assert statuses[0]["remaining"] == -100.0
    assert statuses[0]["percentage_used"] == 120.0
    assert statuses[0]["status"] == "exceeded"