from typing import Protocol

from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)


class BudgetStorageProtocol(Protocol):
    """Define category budget storage operations"""

    def load_budgets(self) -> dict[str, float]:
        """Return stored budgets"""

    def save_budgets(
        self,
        budgets: dict[str, float],
    ) -> None:
        """Save category budgets"""


class BudgetService:
    """Manage category budget workflows"""

    def __init__(
        self,
        manager: BudgetManager,
        storage: BudgetStorageProtocol,
        transaction_service: TransactionService,
    ) -> None:
        self.manager = manager
        self.storage = storage
        self.transaction_service = transaction_service

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

    def get_budget_statuses(
        self,
    ) -> list[dict[str, float | str]]:
        """Return status details for all budgets"""
        transactions = (
            self.transaction_service.list_transactions()
        )

        statuses: list[dict[str, float | str]] = []

        for category, budget in self.list_budgets().items():
            spending = self.manager.get_spending(
                category,
                transactions,
            )

            remaining = self.manager.get_remaining_budget(
                category,
                transactions,
            )

            percentage = self.manager.get_budget_percentage(
                category,
                transactions,
            )

            budget_status = self.manager.get_budget_status(
                category,
                transactions,
            )

            statuses.append(
                {
                    "category": category,
                    "budget": budget,
                    "spending": spending,
                    "remaining": (
                        remaining
                        if remaining is not None
                        else budget
                    ),
                    "percentage_used": (
                        percentage
                        if percentage is not None
                        else 0.0
                    ),
                    "status": budget_status,
                }
            )

        return statuses