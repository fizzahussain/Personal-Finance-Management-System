import sqlite3
from contextlib import closing
from pathlib import Path

from personal_finance_analytics_system.exceptions import (
    StorageError,
)


class SqliteBudgetStorage:
    """Manage user budgets in a SQLite database"""

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
                "Unable to prepare budget storage"
            ) from error

        self.create_table()

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
        """Create the budgets table"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        amount REAL NOT NULL,
                        UNIQUE(user_id, category)
                    )
                    """
                )

                connection.commit()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to create budgets table"
            ) from error

    def save_budgets(
        self,
        budgets: dict[str, float],
    ) -> None:
        """Replace budgets belonging to one user"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                connection.execute(
                    """
                    DELETE FROM budgets
                    WHERE user_id = ?
                    """,
                    (self.user_id,),
                )

                for category, amount in budgets.items():
                    connection.execute(
                        """
                        INSERT INTO budgets (
                            user_id,
                            category,
                            amount
                        )
                        VALUES (?, ?, ?)
                        """,
                        (
                            self.user_id,
                            category.casefold(),
                            float(amount),
                        ),
                    )

                connection.commit()

        except (TypeError, ValueError) as error:
            raise StorageError(
                "Budget data contains invalid values"
            ) from error
        except sqlite3.Error as error:
            raise StorageError(
                "Unable to save category budgets"
            ) from error

    def load_budgets(self) -> dict[str, float]:
        """Load budgets belonging to one user"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                rows = connection.execute(
                    """
                    SELECT
                        category,
                        amount
                    FROM budgets
                    WHERE user_id = ?
                    ORDER BY category
                    """,
                    (self.user_id,),
                ).fetchall()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to load category budgets"
            ) from error

        return {
            str(category): float(amount)
            for category, amount in rows
        }