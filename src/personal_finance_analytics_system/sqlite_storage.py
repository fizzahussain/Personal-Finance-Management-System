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
        user_id: int = 1,
    ) -> None:
        self.file_path = Path(file_path)
        self.user_id = self.validate_user_id(user_id)

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
        self.add_user_id_column()

    @staticmethod
    def validate_user_id(user_id: int) -> int:
        """Validate and return the user ID"""
        try:
            valid_user_id = int(user_id)
        except (TypeError, ValueError) as error:
            raise StorageError(
                "User ID must be a valid integer"
            ) from error

        if valid_user_id <= 0:
            raise StorageError(
                "User ID must be greater than zero"
            )

        return valid_user_id

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
                        user_id INTEGER NOT NULL DEFAULT 1,
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

    def add_user_id_column(self) -> None:
        """Add the user ID column to older databases"""
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

                if "user_id" not in column_names:
                    connection.execute(
                        """
                        ALTER TABLE transactions
                        ADD COLUMN user_id INTEGER
                        NOT NULL DEFAULT 1
                        """
                    )

                    connection.commit()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to add transaction user ID"
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
                        user_id,
                        amount,
                        transaction_type,
                        category,
                        description,
                        transaction_date
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.user_id,
                        transaction.amount,
                        transaction.transaction_type,
                        transaction.category,
                        transaction.description,
                        transaction.transaction_date,
                    ),
                )

                connection.commit()

                transaction.transaction_id = cursor.lastrowid
                transaction.user_id = self.user_id

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
                        user_id,
                        amount,
                        transaction_type,
                        category,
                        description,
                        transaction_date
                    FROM transactions
                    WHERE id = ?
                    AND user_id = ?
                    """,
                    (
                        transaction_id,
                        self.user_id,
                    ),
                ).fetchone()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to load SQLite transaction"
            ) from error

        if row is None:
            return None

        return self.row_to_transaction(row)

    def save_transactions(
        self,
        transactions: list[Transaction],
    ) -> None:
        """Replace stored transactions for one user"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                connection.execute(
                    """
                    DELETE FROM transactions
                    WHERE user_id = ?
                    """,
                    (self.user_id,),
                )

                for transaction in transactions:
                    if transaction.transaction_id is None:
                        cursor = connection.execute(
                            """
                            INSERT INTO transactions (
                                user_id,
                                amount,
                                transaction_type,
                                category,
                                description,
                                transaction_date
                            )
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                self.user_id,
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
                        transaction.user_id = self.user_id
                    else:
                        connection.execute(
                            """
                            INSERT INTO transactions (
                                id,
                                user_id,
                                amount,
                                transaction_type,
                                category,
                                description,
                                transaction_date
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                transaction.transaction_id,
                                self.user_id,
                                transaction.amount,
                                transaction.transaction_type,
                                transaction.category,
                                transaction.description,
                                transaction.transaction_date,
                            ),
                        )

                        transaction.user_id = self.user_id

                connection.commit()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to save SQLite transactions"
            ) from error

    def load_transactions(self) -> list[Transaction]:
        """Load stored transactions for one user"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        user_id,
                        amount,
                        transaction_type,
                        category,
                        description,
                        transaction_date
                    FROM transactions
                    WHERE user_id = ?
                    ORDER BY id
                    """,
                    (self.user_id,),
                ).fetchall()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to load SQLite transactions"
            ) from error

        return [
            self.row_to_transaction(row)
            for row in rows
        ]

    @staticmethod
    def row_to_transaction(
        row: sqlite3.Row | tuple[object, ...],
    ) -> Transaction:
        """Convert a SQLite row into a transaction"""
        try:
            return Transaction(
                transaction_id=int(row[0]),
                user_id=int(row[1]),
                amount=float(row[2]),
                transaction_type=str(row[3]),
                category=str(row[4]),
                description=str(row[5]),
                transaction_date=str(row[6]) or None,
            )
        except FinanceError as error:
            raise StorageError(
                "SQLite transaction data is invalid"
            ) from error