from personal_finance_analytics_system.transaction import Transaction
from personal_finance_analytics_system.transaction_manager import (
    TransactionManager,
)


def show_menu() -> None:
    """Show menu"""
    print("\nPersonal Finance System")
    print("1 Add income")
    print("2 Add expense")
    print("3 View summary")
    print("4 Exit")


def add_transaction(
    manager: TransactionManager,
    transaction_type: str,
) -> None:
    """Add transaction"""
    try:
        # get input
        amount = float(input("Enter amount "))
        category = input("Enter category ")
        description = input("Enter description ")

        # create transaction
        transaction = Transaction(
            amount,
            transaction_type,
            category,
            description,
        )

        manager.add_transaction(transaction)

        print("Transaction added successfully")

    except ValueError as error:
        print(f"Error {error}")


def show_summary(manager: TransactionManager) -> None:
    """Show summary"""
    print("\nFinancial Summary")
    print(f"Total income {manager.get_total_income()}")
    print(f"Total expenses {manager.get_total_expenses()}")
    print(f"Balance {manager.get_balance()}")


def run_cli() -> None:
    """Run cli"""
    manager = TransactionManager()
    while True:
        show_menu()

        # get choice
        choice = input("Choose an option ")

        if choice == "1":
            add_transaction(manager, "income")
        elif choice == "2":
            add_transaction(manager, "expense")

        elif choice == "3":
            show_summary(manager)
        elif choice == "4":
            print("Goodbye")
            break
        else:
            print("Invalid option")


run_cli()