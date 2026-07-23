import sqlite3
from contextlib import closing
from pathlib import Path

from personal_finance_analytics_system.exceptions import (
    FinanceError,
    StorageError,
)
from personal_finance_analytics_system.transaction import Transaction


class SqliteStorage:
    """Manage transactions in a SQLite database"""

    def __init__(
        self,
        file_path: str = "data/transactions.db",
    ) -> None:
        self.file_path = Path(file_path)

        try:
            self.file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
        except OSError as error:
            raise StorageError(
                "Unable to prepare SQLite storage"
            ) from error

        self.create_table()
        self.add_date_column()

    def create_table(self) -> None:
        """Create the transactions table"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
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

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to create SQLite table"
            ) from error

    def add_date_column(self) -> None:
        """Add the date column to older databases"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
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

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to update SQLite table"
            ) from error

    def insert_transaction(
        self,
        transaction: Transaction,
    ) -> Transaction:
        """Insert one transaction"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                cursor = connection.execute(
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

                transaction.transaction_id = cursor.lastrowid

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to insert SQLite transaction"
            ) from error

        return transaction

    def get_transaction(
        self,
        transaction_id: int,
    ) -> Transaction | None:
        """Return one transaction by ID"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                row = connection.execute(
                    """
                    SELECT
                        id,
                        amount,
                        transaction_type,
                        category,
                        description,
                        transaction_date
                    FROM transactions
                    WHERE id = ?
                    """,
                    (transaction_id,),
                ).fetchone()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to load SQLite transaction"
            ) from error

        if row is None:
            return None

        try:
            return Transaction(
                transaction_id=int(row[0]),
                amount=float(row[1]),
                transaction_type=row[2],
                category=row[3],
                description=row[4],
                transaction_date=row[5] or None,
            )
        except FinanceError as error:
            raise StorageError(
                "SQLite transaction data is invalid"
            ) from error

    def delete_transaction(
        self,
        transaction_id: int,
    ) -> bool:
        """Delete one transaction by ID"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                cursor = connection.execute(
                    """
                    DELETE FROM transactions
                    WHERE id = ?
                    """,
                    (transaction_id,),
                )

                connection.commit()

                return cursor.rowcount > 0

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to delete SQLite transaction"
            ) from error

    def save_transactions(
        self,
        transactions: list[Transaction],
    ) -> None:
        """Replace stored transactions"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                connection.execute(
                    "DELETE FROM transactions"
                )

                for transaction in transactions:
                    if transaction.transaction_id is None:
                        cursor = connection.execute(
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

                        transaction.transaction_id = (
                            cursor.lastrowid
                        )
                    else:
                        connection.execute(
                            """
                            INSERT INTO transactions (
                                id,
                                amount,
                                transaction_type,
                                category,
                                description,
                                transaction_date
                            )
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                transaction.transaction_id,
                                transaction.amount,
                                transaction.transaction_type,
                                transaction.category,
                                transaction.description,
                                transaction.transaction_date,
                            ),
                        )

                connection.commit()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to save SQLite transactions"
            ) from error

    def load_transactions(self) -> list[Transaction]:
        """Load stored transactions"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        amount,
                        transaction_type,
                        category,
                        description,
                        transaction_date
                    FROM transactions
                    ORDER BY id
                    """
                ).fetchall()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to load SQLite transactions"
            ) from error

        transactions = []

        try:
            for row in rows:
                transaction = Transaction(
                    transaction_id=int(row[0]),
                    amount=float(row[1]),
                    transaction_type=row[2],
                    category=row[3],
                    description=row[4],
                    transaction_date=row[5] or None,
                )

                transactions.append(transaction)

        except FinanceError as error:
            raise StorageError(
                "SQLite transaction data is invalid"
            ) from error

        return transactions