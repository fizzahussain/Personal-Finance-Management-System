import pytest

from personal_finance_analytics_system.budget_storage import (
    BudgetStorage,
)
from personal_finance_analytics_system.exceptions import (
    StorageError,
)
from personal_finance_analytics_system.json_storage import (
    JsonStorage,
)


def test_reject_damaged_transaction_json(
    tmp_path,
) -> None:
    """Reject damaged transaction JSON"""
    file_path = tmp_path / "transactions.json"
    file_path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    storage = JsonStorage(str(file_path))

    with pytest.raises(StorageError):
        storage.load_transactions()


def test_reject_damaged_budget_json(
    tmp_path,
) -> None:
    """Reject damaged budget JSON"""
    file_path = tmp_path / "budgets.json"
    file_path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    storage = BudgetStorage(str(file_path))

    with pytest.raises(StorageError):
        storage.load_budgets()