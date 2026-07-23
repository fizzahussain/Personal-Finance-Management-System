from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.budget_storage import (
    BudgetStorage,
)


class BudgetService:
    """Manage category budget workflows"""

    def __init__(
        self,
        manager: BudgetManager,
        storage: BudgetStorage,
    ) -> None:
        self.manager = manager
        self.storage = storage

        saved_budgets = self.storage.load_budgets()
        self.manager.load_budgets(saved_budgets)

    def list_budgets(self) -> dict[str, float]:
        """Return all category budgets"""
        return self.manager.get_all_budgets()

    def set_category_budget(
        self,
        category: str,
        amount: float,
    ) -> float:
        """Create or update a category budget"""
        cleaned_category = category.strip()

        self.manager.set_budget(
            cleaned_category,
            amount,
        )

        self.storage.save_budgets(
            self.manager.get_all_budgets()
        )

        return amount