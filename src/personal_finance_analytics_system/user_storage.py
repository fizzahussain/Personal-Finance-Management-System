import sqlite3
from contextlib import closing
from pathlib import Path

from personal_finance_analytics_system.exceptions import (
    StorageError,
)
from personal_finance_analytics_system.user import User


class UserStorage:
    """Manage users in a SQLite database"""

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
                "Unable to prepare user storage"
            ) from error

        self.create_table()

    def create_table(self) -> None:
        """Create the users table"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL
                    )
                    """
                )

                connection.commit()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to create users table"
            ) from error

    def create_user(
        self,
        user: User,
    ) -> User:
        """Insert one user"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO users (
                        email,
                        password_hash
                    )
                    VALUES (?, ?)
                    """,
                    (
                        user.email.lower(),
                        user.password_hash,
                    ),
                )

                connection.commit()

                user.user_id = cursor.lastrowid

        except sqlite3.IntegrityError as error:
            raise StorageError(
                "A user with this email already exists"
            ) from error
        except sqlite3.Error as error:
            raise StorageError(
                "Unable to create user"
            ) from error

        return user

    def get_user_by_email(
        self,
        email: str,
    ) -> User | None:
        """Return one user by email"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                row = connection.execute(
                    """
                    SELECT
                        id,
                        email,
                        password_hash
                    FROM users
                    WHERE email = ?
                    """,
                    (email.lower(),),
                ).fetchone()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to load user"
            ) from error

        if row is None:
            return None

        return User(
            user_id=int(row[0]),
            email=str(row[1]),
            password_hash=str(row[2]),
        )

    def get_user(
        self,
        user_id: int,
    ) -> User | None:
        """Return one user by ID"""
        try:
            with closing(
                sqlite3.connect(self.file_path)
            ) as connection:
                row = connection.execute(
                    """
                    SELECT
                        id,
                        email,
                        password_hash
                    FROM users
                    WHERE id = ?
                    """,
                    (user_id,),
                ).fetchone()

        except sqlite3.Error as error:
            raise StorageError(
                "Unable to load user"
            ) from error

        if row is None:
            return None

        return User(
            user_id=int(row[0]),
            email=str(row[1]),
            password_hash=str(row[2]),
        )