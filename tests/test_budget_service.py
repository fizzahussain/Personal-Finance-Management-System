from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.services.budget_service import (
    BudgetService,
)


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


def test_list_budgets_is_initially_empty() -> None:
    """Return an empty budget collection"""
    storage = FakeBudgetStorage()
    service = BudgetService(
        manager=BudgetManager(),
        storage=storage,
    )

    assert service.list_budgets() == {}


def test_set_category_budget() -> None:
    """Create a category budget"""
    storage = FakeBudgetStorage()
    service = BudgetService(
        manager=BudgetManager(),
        storage=storage,
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


def test_update_category_budget() -> None:
    """Update an existing category budget"""
    storage = FakeBudgetStorage()
    service = BudgetService(
        manager=BudgetManager(),
        storage=storage,
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


def test_load_saved_budgets() -> None:
    """Load existing budgets from storage"""
    storage = FakeBudgetStorage()
    storage.budgets = {
        "Food": 500,
        "Transport": 300,
    }

    service = BudgetService(
        manager=BudgetManager(),
        storage=storage,
    )

    assert service.list_budgets() == {
        "food": 500.0,
        "transport": 300.0,
    }