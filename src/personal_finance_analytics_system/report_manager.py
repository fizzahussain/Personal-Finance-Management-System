from datetime import datetime

from personal_finance_analytics_system.transaction import Transaction


class ReportManager:
    """Create monthly financial reports"""

    @staticmethod
    def validate_month(month: str) -> str:
        """Validate and return the month"""
        try:
            parsed_month = datetime.strptime(
                month,
                "%Y-%m",
            )
        except ValueError as error:
            raise ValueError(
                "Month must use YYYY-MM format"
            ) from error

        return parsed_month.strftime("%Y-%m")

    def get_monthly_transactions(
        self,
        transactions: list[Transaction],
        month: str,
    ) -> list[Transaction]:
        """Return transactions for one month"""
        valid_month = self.validate_month(month)

        return [
            transaction
            for transaction in transactions
            if transaction.transaction_date.startswith(
                valid_month
            )
        ]

    def get_monthly_income(
        self,
        transactions: list[Transaction],
        month: str,
    ) -> float:
        """Return monthly income"""
        monthly_transactions = (
            self.get_monthly_transactions(
                transactions,
                month,
            )
        )

        return sum(
            transaction.amount
            for transaction in monthly_transactions
            if transaction.transaction_type == "income"
        )

    def get_monthly_expenses(
        self,
        transactions: list[Transaction],
        month: str,
    ) -> float:
        """Return monthly expenses"""
        monthly_transactions = (
            self.get_monthly_transactions(
                transactions,
                month,
            )
        )

        return sum(
            transaction.amount
            for transaction in monthly_transactions
            if transaction.transaction_type == "expense"
        )

    def get_monthly_balance(
        self,
        transactions: list[Transaction],
        month: str,
    ) -> float:
        """Return monthly balance"""
        income = self.get_monthly_income(
            transactions,
            month,
        )

        expenses = self.get_monthly_expenses(
            transactions,
            month,
        )

        return income - expenses

    def get_savings_rate(
        self,
        transactions: list[Transaction],
        month: str,
    ) -> float:
        """Return monthly savings rate"""
        income = self.get_monthly_income(
            transactions,
            month,
        )

        if income == 0:
            return 0.0

        balance = self.get_monthly_balance(
            transactions,
            month,
        )

        return balance / income * 100

    def get_spending_by_category(
        self,
        transactions: list[Transaction],
        month: str,
    ) -> dict[str, float]:
        """Return monthly spending by category"""
        monthly_transactions = (
            self.get_monthly_transactions(
                transactions,
                month,
            )
        )

        spending: dict[str, float] = {}

        for transaction in monthly_transactions:
            if transaction.transaction_type != "expense":
                continue

            category = transaction.category.strip()

            spending[category] = (
                spending.get(category, 0.0)
                + transaction.amount
            )

        return spending