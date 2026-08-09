import csv
from pathlib import Path

from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.transaction import Transaction


class ReportExporter:
    """Export monthly reports to CSV"""

    def __init__(
        self,
        report_manager: ReportManager,
    ) -> None:
        self.report_manager = report_manager

    def export_monthly_report(
        self,
        transactions: list[Transaction],
        month: str,
        file_path: str | None = None,
    ) -> Path:
        """Export one monthly report"""
        valid_month = self.report_manager.validate_month(
            month
        )

        if file_path is None:
            path = Path(
                f"reports/monthly_report_{valid_month}.csv"
            )
        else:
            path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        income = self.report_manager.get_monthly_income(
            transactions,
            valid_month,
        )

        expenses = self.report_manager.get_monthly_expenses(
            transactions,
            valid_month,
        )

        balance = self.report_manager.get_monthly_balance(
            transactions,
            valid_month,
        )

        savings_rate = self.report_manager.get_savings_rate(
            transactions,
            valid_month,
        )

        spending = (
            self.report_manager.get_spending_by_category(
                transactions,
                valid_month,
            )
        )

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)

            writer.writerow(
                [
                    "metric",
                    "value",
                ]
            )

            writer.writerow(
                [
                    "income",
                    income,
                ]
            )

            writer.writerow(
                [
                    "expenses",
                    expenses,
                ]
            )

            writer.writerow(
                [
                    "balance",
                    balance,
                ]
            )

            writer.writerow(
                [
                    "savings_rate",
                    savings_rate,
                ]
            )

            writer.writerow([])

            writer.writerow(
                [
                    "category",
                    "amount",
                ]
            )

            for category, amount in spending.items():
                writer.writerow(
                    [
                        category,
                        amount,
                    ]
                )

        return path