from personal_finance_analytics_system.exceptions import (
    InvalidBudgetError,
)
from personal_finance_analytics_system.transaction import Transaction


class BudgetManager:
    """Manage budgets for spending categories"""

    def __init__(self) -> None:
        self.budgets: dict[str, float] = {}

    @staticmethod
    def normalise_category(category: str) -> str:
        """Return a consistent category name"""
        return category.strip().casefold()

    def set_budget(
        self,
        category: str,
        amount: float,
    ) -> None:
        """Set a budget for a category"""
        category_key = self.normalise_category(category)

        if not category_key:
            raise InvalidBudgetError(
                "Category cannot be empty"
            )

        try:
            valid_amount = float(amount)
        except (TypeError, ValueError) as error:
            raise InvalidBudgetError(
                "Budget must be a valid number"
            ) from error

        if valid_amount <= 0:
            raise InvalidBudgetError(
                "Budget must be greater than zero"
            )

        self.budgets[category_key] = valid_amount

    def get_budget(
        self,
        category: str,
    ) -> float | None:
        """Return the budget for a category"""
        category_key = self.normalise_category(category)

        return self.budgets.get(category_key)

    def get_spending(
        self,
        category: str,
        transactions: list[Transaction],
    ) -> float:
        """Return expense spending for a category"""
        category_key = self.normalise_category(category)
        total = 0.0

        for transaction in transactions:
            transaction_category = self.normalise_category(
                transaction.category
            )

            if (
                transaction.transaction_type == "expense"
                and transaction_category == category_key
            ):
                total += transaction.amount

        return total

    def get_remaining_budget(
        self,
        category: str,
        transactions: list[Transaction],
    ) -> float | None:
        """Return the remaining category budget"""
        budget = self.get_budget(category)

        if budget is None:
            return None

        spending = self.get_spending(
            category,
            transactions,
        )

        return budget - spending

    def get_budget_percentage(
        self,
        category: str,
        transactions: list[Transaction],
    ) -> float | None:
        """Return the used budget percentage"""
        budget = self.get_budget(category)

        if budget is None:
            return None

        spending = self.get_spending(
            category,
            transactions,
        )

        return spending / budget * 100

    def get_budget_status(
        self,
        category: str,
        transactions: list[Transaction],
    ) -> str:
        """Return the category budget status"""
        percentage = self.get_budget_percentage(
            category,
            transactions,
        )

        if percentage is None:
            return "not set"

        if percentage >= 100:
            return "exceeded"

        if percentage >= 80:
            return "warning"

        return "healthy"

    def get_all_budgets(self) -> dict[str, float]:
        """Return all category budgets"""
        return self.budgets.copy()

    def load_budgets(
        self,
        budgets: dict[str, float],
    ) -> None:
        """Load saved category budgets"""
        loaded_budgets = {}

        for category, amount in budgets.items():
            category_key = self.normalise_category(category)

            try:
                valid_amount = float(amount)
            except (TypeError, ValueError) as error:
                raise InvalidBudgetError(
                    "Stored budget must be a valid number"
                ) from error

            if not category_key or valid_amount <= 0:
                raise InvalidBudgetError(
                    "Stored budget data is invalid"
                )

            loaded_budgets[category_key] = valid_amount

        self.budgets = loaded_budgets