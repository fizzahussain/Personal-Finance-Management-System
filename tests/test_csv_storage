from personal_finance_analytics_system.csv_storage import CsvStorage
from personal_finance_analytics_system.transaction import Transaction


def test_save_and_load_transactions(tmp_path) -> None:
    file_path = tmp_path / "transactions.csv"
    storage = CsvStorage(str(file_path))

    transactions = [
        Transaction(
            5000,
            "income",
            "Salary",
            "Monthly salary",
        ),
        Transaction(
            500,
            "expense",
            "Food",
            "",
        ),
    ]

    storage.save_transactions(transactions)

    loaded_transactions = storage.load_transactions()

    assert len(loaded_transactions) == 2
    assert loaded_transactions[0].amount == 5000
    assert loaded_transactions[1].category == "Food"