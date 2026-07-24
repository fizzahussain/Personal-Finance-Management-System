import csv
import json
from calendar import monthrange
from datetime import date, timedelta
from io import StringIO

from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.transaction import Transaction


class ReportService:
    """Manage financial report workflows"""

    def __init__(
        self,
        report_manager: ReportManager,
        transaction_service: TransactionService,
    ) -> None:
        self.report_manager = report_manager
        self.transaction_service = transaction_service

    def get_monthly_report(
        self,
        month: str,
    ) -> dict[str, object]:
        """Return a monthly financial report"""
        transactions = (
            self.transaction_service.list_transactions()
        )

        return {
            "month": month,
            "income": self.report_manager.get_monthly_income(
                transactions,
                month,
            ),
            "expenses": (
                self.report_manager.get_monthly_expenses(
                    transactions,
                    month,
                )
            ),
            "balance": self.report_manager.get_monthly_balance(
                transactions,
                month,
            ),
            "savings_rate": (
                self.report_manager.get_savings_rate(
                    transactions,
                    month,
                )
            ),
            "spending_by_category": (
                self.report_manager.get_spending_by_category(
                    transactions,
                    month,
                )
            ),
        }

    def get_date_range_report(
        self,
        start_date: date,
        end_date: date,
    ) -> dict[str, object]:
        """Return a financial report for a date range"""
        if start_date > end_date:
            raise ValueError(
                "Start date cannot be after end date"
            )

        latest_end_date = self.get_latest_report_end_date()

        if end_date > latest_end_date:
            raise ValueError(
                f"End date cannot be later than "
                f"{latest_end_date.isoformat()}"
            )

        transactions = (
            self.transaction_service.list_transactions()
        )

        filtered_transactions = [
            transaction
            for transaction in transactions
            if start_date
            <= self._transaction_date(transaction)
            <= end_date
        ]

        income = sum(
            transaction.amount
            for transaction in filtered_transactions
            if transaction.transaction_type == "income"
        )

        expenses = sum(
            transaction.amount
            for transaction in filtered_transactions
            if transaction.transaction_type == "expense"
        )

        balance = income - expenses

        savings_rate = (
            balance / income * 100
            if income > 0
            else 0.0
        )

        spending_by_category: dict[str, float] = {}

        for transaction in filtered_transactions:
            if transaction.transaction_type != "expense":
                continue

            spending_by_category[transaction.category] = (
                spending_by_category.get(
                    transaction.category,
                    0.0,
                )
                + transaction.amount
            )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "income": income,
            "expenses": expenses,
            "balance": balance,
            "savings_rate": savings_rate,
            "spending_by_category": spending_by_category,
        }

    @staticmethod
    def _transaction_date(
        transaction: Transaction,
    ) -> date:
        """Return the transaction date as a date object"""
        return date.fromisoformat(
            transaction.transaction_date
        )

    @staticmethod
    def get_latest_report_end_date(
        today: date | None = None,
    ) -> date:
        """Return the latest permitted report date"""
        current_date = today or date.today()

        if current_date.month == 1:
            previous_year = current_date.year - 1
            previous_month = 12
        else:
            previous_year = current_date.year
            previous_month = current_date.month - 1

        previous_month_days = monthrange(
            previous_year,
            previous_month,
        )[1]

        matching_day = min(
            current_date.day,
            previous_month_days,
        )

        return (
            date(
                previous_year,
                previous_month,
                matching_day,
            )
            - timedelta(days=1)
        )

    def export_date_range_report_csv(
        self,
        start_date: date,
        end_date: date,
    ) -> str:
        """Return a date-range report as CSV"""
        report = self.get_date_range_report(
            start_date,
            end_date,
        )

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "start_date",
                "end_date",
                "income",
                "expenses",
                "balance",
                "savings_rate",
            ]
        )

        writer.writerow(
            [
                report["start_date"],
                report["end_date"],
                report["income"],
                report["expenses"],
                report["balance"],
                report["savings_rate"],
            ]
        )

        writer.writerow([])
        writer.writerow(
            [
                "category",
                "amount",
            ]
        )

        spending_by_category = report[
            "spending_by_category"
        ]

        for category, amount in spending_by_category.items():
            writer.writerow(
                [
                    category,
                    amount,
                ]
            )

        return output.getvalue()


    def export_date_range_report_json(
        self,
        start_date: date,
        end_date: date,
    ) -> str:
        """Return a date-range report as JSON"""
        report = self.get_date_range_report(
            start_date,
            end_date,
        )

        serializable_report = {
            "start_date": report["start_date"].isoformat(),
            "end_date": report["end_date"].isoformat(),
            "income": report["income"],
            "expenses": report["expenses"],
            "balance": report["balance"],
            "savings_rate": report["savings_rate"],
            "spending_by_category": report[
                "spending_by_category"
            ],
        }

        return json.dumps(
            serializable_report,
            indent=2,
        )