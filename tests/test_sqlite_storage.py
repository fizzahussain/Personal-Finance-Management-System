import sqlite3
from contextlib import closing
from pathlib import Path

from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction


def test_save_and_load_transactions(
    tmp_path: Path,
) -> None:
    """Save and load transactions"""
    file_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(file_path))

    transactions = [
        Transaction(
            5000,
            "income",
            "Salary",
            "Monthly salary",
            "2026-07-01",
        ),
        Transaction(
            500,
            "expense",
            "Food",
            "Groceries",
            "2026-07-02",
        ),
    ]

    storage.save_transactions(transactions)

    loaded_transactions = storage.load_transactions()

    assert len(loaded_transactions) == 2

    assert loaded_transactions[0].amount == 5000
    assert loaded_transactions[0].transaction_type == "income"
    assert loaded_transactions[0].category == "Salary"
    assert loaded_transactions[0].description == "Monthly salary"
    assert (
        loaded_transactions[0].transaction_date
        == "2026-07-01"
    )

    assert loaded_transactions[1].amount == 500
    assert loaded_transactions[1].transaction_type == "expense"
    assert loaded_transactions[1].category == "Food"
    assert loaded_transactions[1].description == "Groceries"
    assert (
        loaded_transactions[1].transaction_date
        == "2026-07-02"
    )


def test_save_replaces_existing_transactions(
    tmp_path: Path,
) -> None:
    """Replace existing transactions"""
    file_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(file_path))

    first_transactions = [
        Transaction(
            1000,
            "income",
            "Salary",
            "",
            "2026-07-01",
        ),
        Transaction(
            100,
            "expense",
            "Food",
            "",
            "2026-07-02",
        ),
    ]

    replacement_transactions = [
        Transaction(
            200,
            "expense",
            "Transport",
            "Bus pass",
            "2026-07-03",
        ),
    ]

    storage.save_transactions(first_transactions)
    storage.save_transactions(
        replacement_transactions
    )

    loaded_transactions = storage.load_transactions()

    assert len(loaded_transactions) == 1
    assert loaded_transactions[0].amount == 200
    assert loaded_transactions[0].category == "Transport"
    assert loaded_transactions[0].description == "Bus pass"
    assert (
        loaded_transactions[0].transaction_date
        == "2026-07-03"
    )


def test_adds_date_column_to_older_database(
    tmp_path: Path,
) -> None:
    """Add the date column to an older database"""
    file_path = tmp_path / "transactions.db"

    with closing(
        sqlite3.connect(file_path)
    ) as connection:
        connection.execute(
            """
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL
            )
            """
        )

        connection.commit()

    SqliteStorage(str(file_path))

    with closing(
        sqlite3.connect(file_path)
    ) as connection:
        columns = connection.execute(
            "PRAGMA table_info(transactions)"
        ).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    assert "transaction_date" in column_names


def test_database_contains_saved_rows(
    tmp_path: Path,
) -> None:
    """Store transaction rows in the database"""
    file_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(file_path))

    transactions = [
        Transaction(
            300,
            "expense",
            "Food",
            "Dinner",
            "2026-07-04",
        ),
    ]

    storage.save_transactions(transactions)

    with closing(
        sqlite3.connect(file_path)
    ) as connection:
        rows = connection.execute(
            """
            SELECT
                amount,
                transaction_type,
                category,
                description,
                transaction_date
            FROM transactions
            """
        ).fetchall()

    assert rows == [
        (
            300.0,
            "expense",
            "Food",
            "Dinner",
            "2026-07-04",
        )
    ]