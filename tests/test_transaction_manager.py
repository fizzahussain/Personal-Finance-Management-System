from personal_finance_analytics_system.transaction import Transaction
from personal_finance_analytics_system.transaction_manager import (
    TransactionManager,
)


def test_transaction_manager_summary() -> None:
    manager = TransactionManager()

    income = Transaction(
        5000,
        "income",
        "Salary",
        "Monthly salary",
        "2026-07-22",
    )

    expense = Transaction(
        500,
        "expense",
        "Food",
        "Groceries",
    )

    manager.add_transaction(income)
    manager.add_transaction(expense)

    assert manager.get_total_income() == 5000
    assert manager.get_total_expenses() == 500
    assert manager.get_balance() == 4500