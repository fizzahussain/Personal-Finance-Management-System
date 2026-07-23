import pytest

from personal_finance_analytics_system.csv_storage import CsvStorage
from personal_finance_analytics_system.json_storage import JsonStorage
from personal_finance_analytics_system.sqlite_storage import SqliteStorage
from personal_finance_analytics_system.storage_selection import (
    create_storage,
)


def test_create_json_storage() -> None:
    """Create json storage"""
    storage = create_storage("1")

    assert isinstance(storage, JsonStorage)


def test_create_csv_storage() -> None:
    """Create csv storage"""
    storage = create_storage("2")

    assert isinstance(storage, CsvStorage)


def test_create_sqlite_storage() -> None:
    """Create sqlite storage"""
    storage = create_storage("3")

    assert isinstance(storage, SqliteStorage)


def test_invalid_storage_choice() -> None:
    """Reject invalid storage choice"""
    with pytest.raises(ValueError):
        create_storage("9")