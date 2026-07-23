from personal_finance_analytics_system.budget_storage import (
    BudgetStorage,
)
from personal_finance_analytics_system.transaction_filter import (
    TransactionFilter,
)
from datetime import date, datetime

from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.storage_selection import (
    create_storage,
)
from personal_finance_analytics_system.transaction import Transaction
from personal_finance_analytics_system.transaction_manager import (
    TransactionManager,
)
from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.report_exporter import (
    ReportExporter,
)
from personal_finance_analytics_system.chart_manager import (
    ChartManager,
)

storage = None
manager = TransactionManager()
budget_manager = BudgetManager()
budget_storage = BudgetStorage()
report_manager = ReportManager()
report_exporter = ReportExporter(report_manager)
chart_manager = ChartManager(report_manager)
monthly_budget = 0.0


def choose_storage():
    """Ask the user to choose storage"""
    while True:
        print("\nChoose storage")
        print("1 JSON")
        print("2 CSV")
        print("3 SQLite")

        choice = input("Choose an option: ").strip()

        try:
            return create_storage(choice)
        except ValueError:
            print("Invalid option")

def show_menu() -> None:
    """Show menu"""
    print("\nPersonal Finance System")
    print("1 Add income")
    print("2 Add expense")
    print("3 Set monthly budget")
    print("4 Set category budget")
    print("5 View financial summary")
    print("6 View transactions")
    print("7 View category budgets")
    print("8 Filter transactions")
    print("9 View monthly report")
    print("10 Export monthly report")
    print("11 Create category spending chart")
    print("12 Create monthly summary chart")
    print("13 Exit")


def get_amount(message: str) -> float:
    """Get valid amount"""
    while True:
        try:
            amount = float(input(message).strip())

            if amount <= 0:
                print("Amount must be greater than zero")
                continue

            return amount

        except ValueError:
            print("Enter a valid number")


def get_transaction_date() -> str:
    """Get a valid transaction date"""
    while True:
        transaction_date = input(
            "Enter date YYYY-MM-DD or press Enter for today: "
        ).strip()

        if not transaction_date:
            return date.today().isoformat()

        try:
            parsed_date = datetime.strptime(
                transaction_date,
                "%Y-%m-%d",
            )
        except ValueError:
            print("Date must use YYYY-MM-DD format")
            continue

        return parsed_date.date().isoformat()


def add_transaction(transaction_type: str) -> None:
    """Add transaction"""
    amount = get_amount("Enter amount: ")
    category = input("Enter category: ").strip()

    while not category:
        print("Category cannot be empty")
        category = input("Enter category: ").strip()

    description = input(
        "Enter description or press Enter to skip: "
    ).strip()

    transaction_date = get_transaction_date()

    transaction = Transaction(
        amount=amount,
        transaction_type=transaction_type,
        category=category,
        description=description,
        transaction_date=transaction_date,
    )

    manager.add_transaction(transaction)
    storage.save_transactions(manager.transactions)

    print(
        f"{transaction_type.title()} added successfully"
    )


def set_budget() -> None:
    """Set monthly budget"""
    global monthly_budget

    monthly_budget = get_amount("Enter monthly expense budget: ")

    print(f"Monthly budget set to {monthly_budget:.2f}")


def show_summary() -> None:
    """Show financial summary"""
    income = manager.get_total_income()
    expenses = manager.get_total_expenses()
    balance = manager.get_balance()

    print("\nFinancial Summary")
    print(f"Total income: {income:.2f}")
    print(f"Total expenses: {expenses:.2f}")
    print(f"Current balance: {balance:.2f}")

    if income > 0:
        savings_rate = balance / income * 100
        print(f"Savings rate: {savings_rate:.1f}%")
    else:
        print("Savings rate: unavailable")

    if balance < 0:
        print("Status: expenses are greater than income")
    elif balance == 0:
        print("Status: no money remaining")
    else:
        print("Status: positive balance")

    show_budget_status(expenses)


def show_budget_status(expenses: float) -> None:
    """Show budget status"""
    if monthly_budget == 0:
        print("Monthly budget: not set")
        return

    budget_remaining = monthly_budget - expenses
    budget_used = expenses / monthly_budget * 100

    print(f"Monthly budget: {monthly_budget:.2f}")
    print(f"Budget used: {budget_used:.1f}%")

    if budget_remaining < 0:
        print(
            f"Budget exceeded by: {abs(budget_remaining):.2f}"
        )
    else:
        print(f"Budget remaining: {budget_remaining:.2f}")

    if budget_used >= 100:
        print("Budget status: exceeded")
    elif budget_used >= 80:
        print("Budget status: warning")
    else:
        print("Budget status: healthy")


def show_monthly_report() -> None:
    """Show a monthly financial report"""
    month = input(
        "Enter month YYYY-MM: "
    ).strip()

    try:
        income = report_manager.get_monthly_income(
            manager.transactions,
            month,
        )

        expenses = report_manager.get_monthly_expenses(
            manager.transactions,
            month,
        )

        balance = report_manager.get_monthly_balance(
            manager.transactions,
            month,
        )

        savings_rate = report_manager.get_savings_rate(
            manager.transactions,
            month,
        )

        spending = report_manager.get_spending_by_category(
            manager.transactions,
            month,
        )

    except ValueError as error:
        print(error)
        return

    print(f"\nMonthly Report {month}")
    print(f"Income: {income:.2f}")
    print(f"Expenses: {expenses:.2f}")
    print(f"Balance: {balance:.2f}")
    print(f"Savings rate: {savings_rate:.1f}%")

    print("\nSpending by category")

    if not spending:
        print("No expense transactions found")
        return

    for category, amount in spending.items():
        print(f"{category}: {amount:.2f}")





def show_transactions() -> None:
    """Show transactions"""
    if not manager.transactions:
        print("\nNo transactions found")
        return

    print("\nTransactions")

    for number, transaction in enumerate(
        manager.transactions,
        start=1,
    ):
        description = transaction.description or "No description"

        print(
        f"{number} "
        f"{transaction.transaction_date} "
        f"{transaction.transaction_type.title()} "
        f"{transaction.category} "
        f"{transaction.amount:.2f} "
        f"{description}"
    )

def set_category_budget() -> None:
    """Set a budget for a category"""
    category = input("Enter category: ").strip()

    while not category:
        print("Category cannot be empty")
        category = input("Enter category: ").strip()

    amount = get_amount("Enter category budget: ")

    budget_manager.set_budget(
        category,
        amount,
    )

    budget_storage.save_budgets(
        budget_manager.get_all_budgets()
    )

    print(
        f"Budget for {category} set to {amount:.2f}"
    )


def show_category_budgets() -> None:
    """Show all category budgets"""
    budgets = budget_manager.get_all_budgets()

    if not budgets:
        print("\nNo category budgets found")
        return

    print("\nCategory Budgets")

    for category, budget in budgets.items():
        spending = budget_manager.get_spending(
            category,
            manager.transactions,
        )

        remaining = budget_manager.get_remaining_budget(
            category,
            manager.transactions,
        )


        percentage = budget_manager.get_budget_percentage(
            category,
            manager.transactions,
        )

        status = budget_manager.get_budget_status(
            category,
            manager.transactions,
        )

        if percentage is not None:
            print(f"Budget used: {percentage:.1f}%")

        print(f"Status: {status.title()}")
        
        print(f"\nCategory: {category.title()}")
        print(f"Budget: {budget:.2f}")
        print(f"Spent: {spending:.2f}")

        if remaining is not None and remaining < 0:
            print(
                f"Exceeded by: {abs(remaining):.2f}"
            )
        elif remaining is not None:
            print(f"Remaining: {remaining:.2f}")

def display_transactions(
    transactions: list[Transaction],
) -> None:
    """Display a transaction list"""
    if not transactions:
        print("\nNo transactions found")
        return

    print("\nTransactions")

    for number, transaction in enumerate(
        transactions,
        start=1,
    ):
        description = transaction.description or "No description"

        print(
            f"{number} "
            f"{transaction.transaction_date} "
            f"{transaction.transaction_type.title()} "
            f"{transaction.category} "
            f"{transaction.amount:.2f} "
            f"{description}"
        )

def show_filter_menu() -> None:
    """Show transaction filters"""
    print("\nFilter Transactions")
    print("1 Category")
    print("2 Transaction type")
    print("3 Date")
    print("4 Amount range")
    print("5 Back")


def filter_transactions() -> None:
    """Filter and display transactions"""
    while True:
        show_filter_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            category = input("Enter category: ").strip()

            filtered = TransactionFilter.by_category(
                manager.transactions,
                category,
            )

            display_transactions(filtered)

        elif choice == "2":
            transaction_type = input(
                "Enter income or expense: "
            ).strip()

            filtered = TransactionFilter.by_type(
                manager.transactions,
                transaction_type,
            )

            display_transactions(filtered)

        elif choice == "3":
            transaction_date = input(
                "Enter date YYYY-MM-DD: "
            ).strip()

            filtered = TransactionFilter.by_date(
                manager.transactions,
                transaction_date,
            )

            display_transactions(filtered)

        elif choice == "4":
            minimum_text = input(
                "Enter minimum amount or press Enter: "
            ).strip()

            maximum_text = input(
                "Enter maximum amount or press Enter: "
            ).strip()

            minimum_amount = (
                float(minimum_text)
                if minimum_text
                else None
            )

            maximum_amount = (
                float(maximum_text)
                if maximum_text
                else None
            )

            filtered = TransactionFilter.by_amount_range(
                manager.transactions,
                minimum_amount,
                maximum_amount,
            )

            display_transactions(filtered)

        elif choice == "5":
            break

        else:
            print("Invalid option")

def export_monthly_report() -> None:
    """Export a monthly report"""
    month = input(
        "Enter month YYYY-MM: "
    ).strip()

    try:
        file_path = report_exporter.export_monthly_report(
            manager.transactions,
            month,
        )
    except ValueError as error:
        print(error)
        return

    print(
        f"Report exported to {file_path}"
    )


def create_category_chart() -> None:
    """Create a category spending chart"""
    month = input(
        "Enter month YYYY-MM: "
    ).strip()

    try:
        file_path = (
            chart_manager.create_category_spending_chart(
                manager.transactions,
                month,
            )
        )
    except ValueError as error:
        print(error)
        return

    print(
        f"Chart saved to {file_path}"
    )


def create_summary_chart() -> None:
    """Create a monthly summary chart"""
    month = input(
        "Enter month YYYY-MM: "
    ).strip()

    try:
        file_path = (
            chart_manager.create_monthly_summary_chart(
                manager.transactions,
                month,
            )
        )
    except ValueError as error:
        print(error)
        return

    print(
        f"Chart saved to {file_path}"
    )


def run_cli() -> None:
    """Run cli"""
    global storage
    global manager

    storage = choose_storage()
    manager = TransactionManager()
    manager.transactions = storage.load_transactions()
    saved_budgets = budget_storage.load_budgets()
    budget_manager.load_budgets(saved_budgets)

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_transaction("income")

        elif choice == "2":
            add_transaction("expense")

        elif choice == "3":
            set_budget()

        elif choice == "4":
            set_category_budget()

        elif choice == "5":
            show_summary()

        elif choice == "6":
            show_transactions()

        elif choice == "7":
            show_category_budgets()

        elif choice == "8":
            filter_transactions()

        elif choice == "9":
            show_monthly_report()

        elif choice == "10":
            export_monthly_report()

        elif choice == "11":
            create_category_chart()

        elif choice == "12":
            create_summary_chart()

        elif choice == "13":
            print("Goodbye")
            break

        else:
            print("Invalid option")

run_cli()