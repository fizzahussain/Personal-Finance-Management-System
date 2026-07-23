from pathlib import Path

import pytest

from personal_finance_analytics_system.csv_storage import CsvStorage
from personal_finance_analytics_system.json_storage import JsonStorage
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction


@pytest.fixture
def first_transactions() -> list[Transaction]:
    """Create the first transaction list"""
    return [
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


@pytest.fixture
def replacement_transactions() -> list[Transaction]:
    """Create the replacement transaction list"""
    return [
        Transaction(
            200,
            "expense",
            "Transport",
            "",
            "2026-07-03",
        ),
    ]


@pytest.mark.parametrize(
    ("storage_class", "filename"),
    [
        (JsonStorage, "transactions.json"),
        (CsvStorage, "transactions.csv"),
        (SqliteStorage, "transactions.db"),
    ],
)
def test_save_replaces_existing_transactions(
    tmp_path: Path,
    storage_class,
    filename: str,
    first_transactions: list[Transaction],
    replacement_transactions: list[Transaction],
) -> None:
    """Replace existing stored transactions"""
    storage = storage_class(
        str(tmp_path / filename)
    )

    storage.save_transactions(first_transactions)
    storage.save_transactions(
        replacement_transactions
    )

    loaded = storage.load_transactions()

    assert len(loaded) == 1
    assert loaded[0].category == "Transport"
    assert loaded[0].amount == 200