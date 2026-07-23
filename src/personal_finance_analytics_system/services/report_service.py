from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)


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