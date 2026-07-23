from personal_finance_analytics_system.csv_storage import CsvStorage
from personal_finance_analytics_system.json_storage import JsonStorage
from personal_finance_analytics_system.sqlite_storage import SqliteStorage


def create_storage(storage_choice: str):
    """Create storage from user choice"""
    if storage_choice == "1":
        return JsonStorage()

    if storage_choice == "2":
        return CsvStorage()

    if storage_choice == "3":
        return SqliteStorage()

    raise ValueError("Invalid storage choice")