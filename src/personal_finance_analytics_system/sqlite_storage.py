import sqlite3
from pathlib import Path

from personal_finance_analytics_system.transaction import Transaction


class SqliteStorage:
    """Manage transactions in a SQLite database"""

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
        self.add_date_column()

    def create_table(self) -> None:
        """Create the transactions table"""
        with sqlite3.connect(self.file_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    transaction_date TEXT NOT NULL DEFAULT ''
                )
                """
            )

            connection.commit()

    def add_date_column(self) -> None:
        """Add the date column to older databases"""
        with sqlite3.connect(self.file_path) as connection:
            columns = connection.execute(
                "PRAGMA table_info(transactions)"
            ).fetchall()

            column_names = [
                column[1]
                for column in columns
            ]

            if "transaction_date" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE transactions
                    ADD COLUMN transaction_date TEXT
                    NOT NULL DEFAULT ''
                    """
                )

                connection.commit()

    def save_transactions(
        self,
        transactions: list[Transaction],
    ) -> None:
        """Replace stored transactions"""
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
                        description,
                        transaction_date
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        transaction.amount,
                        transaction.transaction_type,
                        transaction.category,
                        transaction.description,
                        transaction.transaction_date,
                    ),
                )

            connection.commit()

    def load_transactions(self) -> list[Transaction]:
        """Load stored transactions"""
        with sqlite3.connect(self.file_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    amount,
                    transaction_type,
                    category,
                    description,
                    transaction_date
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
                transaction_date=row[4] or None,
            )

            transactions.append(transaction)

        return transactions