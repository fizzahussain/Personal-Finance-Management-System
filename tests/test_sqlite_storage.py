import sqlite3
from pathlib import Path

from personal_finance_analytics_system.transaction import Transaction


class SqliteStorage:
    """Manage transaction data in a SQLite database"""

    def __init__(
        self,
        file_path: str = "data/transactions.db",
    ) -> None:
        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.create_table()

    def create_table(self) -> None:
        """Create the transactions table if it does not exist"""
        with sqlite3.connect(self.file_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL
                )
                """
            )

            connection.commit()

    def save_transactions(
        self,
        transactions: list[Transaction],
    ) -> None:
        """Replace stored transactions with the current list"""
        with sqlite3.connect(self.file_path) as connection:
            connection.execute(
                "DELETE FROM transactions"
            )

            for transaction in transactions:
                connection.execute(
                    """
                    INSERT INTO transactions (
                        amount,
                        transaction_type,
                        category,
                        description
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        transaction.amount,
                        transaction.transaction_type,
                        transaction.category,
                        transaction.description,
                    ),
                )

            connection.commit()

    def load_transactions(self) -> list[Transaction]:
        """Load all transactions from the database"""
        with sqlite3.connect(self.file_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    amount,
                    transaction_type,
                    category,
                    description
                FROM transactions
                ORDER BY id
                """
            ).fetchall()

        transactions = []

        for row in rows:
            transaction = Transaction(
                amount=float(row[0]),
                transaction_type=row[1],
                category=row[2],
                description=row[3],
            )

            transactions.append(transaction)

        return transactions


#second test

def test_save_replaces_existing_transactions(tmp_path) -> None:
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))

    first_transactions = [
        Transaction(
            1000,
            "income",
            "Salary",
            "",
        ),
    ]

    storage.save_transactions(first_transactions)

    second_transactions = [
        Transaction(
            200,
            "expense",
            "Transport",
            "Bus pass",
        ),
    ]

    storage.save_transactions(second_transactions)

    loaded_transactions = storage.load_transactions()

    assert len(loaded_transactions) == 1
    assert loaded_transactions[0].amount == 200
    assert loaded_transactions[0].category == "Transport"