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
        amount = float(amount)

        if not category_key:
            raise ValueError("Category cannot be empty")

        if amount <= 0:
            raise ValueError(
                "Budget must be greater than zero"
            )

        self.budgets[category_key] = amount

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

    def get_all_budgets(self) -> dict[str, float]:
        """Return all category budgets"""
        return self.budgets.copy()