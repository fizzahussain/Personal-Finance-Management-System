from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.transaction import Transaction


class ChartManager:
    """Create monthly financial charts"""

    def __init__(
        self,
        report_manager: ReportManager,
    ) -> None:
        self.report_manager = report_manager

    @staticmethod
    def create_output_path(
        file_path: str,
    ) -> Path:
        """Create the output folder"""
        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def create_category_spending_chart(
        self,
        transactions: list[Transaction],
        month: str,
        file_path: str | None = None,
    ) -> Path:
        """Create a category spending pie chart"""
        valid_month = self.report_manager.validate_month(
            month
        )

        spending = (
            self.report_manager.get_spending_by_category(
                transactions,
                valid_month,
            )
        )

        if not spending:
            raise ValueError(
                "No expense transactions found"
            )

        if file_path is None:
            file_path = (
                "reports/"
                f"category_spending_{valid_month}.png"
            )

        path = self.create_output_path(file_path)

        categories = list(spending.keys())
        amounts = list(spending.values())

        plt.figure(
            figsize=(8, 6),
        )

        plt.pie(
            amounts,
            labels=categories,
            autopct="%1.1f%%",
        )

        plt.title(
            f"Category Spending {valid_month}"
        )

        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path

    def create_monthly_summary_chart(
        self,
        transactions: list[Transaction],
        month: str,
        file_path: str | None = None,
    ) -> Path:
        """Create an income and expense bar chart"""
        valid_month = self.report_manager.validate_month(
            month
        )

        income = self.report_manager.get_monthly_income(
            transactions,
            valid_month,
        )

        expenses = self.report_manager.get_monthly_expenses(
            transactions,
            valid_month,
        )

        if file_path is None:
            file_path = (
                "reports/"
                f"monthly_summary_{valid_month}.png"
            )

        path = self.create_output_path(file_path)

        labels = [
            "Income",
            "Expenses",
        ]

        amounts = [
            income,
            expenses,
        ]

        plt.figure(
            figsize=(8, 6),
        )

        plt.bar(
            labels,
            amounts,
        )

        plt.title(
            f"Monthly Summary {valid_month}"
        )

        plt.ylabel("Amount")

        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path