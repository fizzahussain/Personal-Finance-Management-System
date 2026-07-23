from pathlib import Path

import pytest

from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.budget_storage import (
    BudgetStorage,
)
from personal_finance_analytics_system.csv_storage import CsvStorage
from personal_finance_analytics_system.exceptions import (
    InvalidBudgetError,
    StorageError,
)
from personal_finance_analytics_system.json_storage import JsonStorage
from personal_finance_analytics_system.report_manager import (
    ReportManager,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction
from personal_finance_analytics_system.transaction_filter import (
    TransactionFilter,
)


def create_transactions() -> list[Transaction]:
    """Create transactions for coverage tests"""
    return [
        Transaction(
            5000,
            "income",
            "Salary",
            "Monthly salary",
            "2026-07-01",
        ),
        Transaction(
            300,
            "expense",
            "Food",
            "Groceries",
            "2026-07-02",
        ),
        Transaction(
            100,
            "expense",
            "Transport",
            "Bus pass",
            "2026-08-01",
        ),
    ]


def test_missing_json_file_returns_empty_list(
    tmp_path: Path,
) -> None:
    """Return an empty list for a missing JSON file"""
    storage = JsonStorage(
        str(tmp_path / "missing.json")
    )

    assert storage.load_transactions() == []


def test_missing_csv_file_returns_empty_list(
    tmp_path: Path,
) -> None:
    """Return an empty list for a missing CSV file"""
    storage = CsvStorage(
        str(tmp_path / "missing.csv")
    )

    assert storage.load_transactions() == []


def test_missing_budget_file_returns_empty_dictionary(
    tmp_path: Path,
) -> None:
    """Return empty budgets for a missing file"""
    storage = BudgetStorage(
        str(tmp_path / "missing.json")
    )

    assert storage.load_budgets() == {}


def test_empty_sqlite_database_returns_empty_list(
    tmp_path: Path,
) -> None:
    """Return an empty list from a new database"""
    storage = SqliteStorage(
        str(tmp_path / "transactions.db")
    )

    assert storage.load_transactions() == []


def test_json_data_must_be_a_list(
    tmp_path: Path,
) -> None:
    """Reject JSON data that is not a list"""
    file_path = tmp_path / "transactions.json"
    file_path.write_text(
        '{"amount": 100}',
        encoding="utf-8",
    )

    storage = JsonStorage(str(file_path))

    with pytest.raises(
        StorageError,
        match="JSON transaction data must be a list",
    ):
        storage.load_transactions()


def test_budget_data_must_be_an_object(
    tmp_path: Path,
) -> None:
    """Reject budget data that is not an object"""
    file_path = tmp_path / "budgets.json"
    file_path.write_text(
        "[100, 200]",
        encoding="utf-8",
    )

    storage = BudgetStorage(str(file_path))

    with pytest.raises(
        StorageError,
        match="Budget data must be an object",
    ):
        storage.load_budgets()


def test_load_budgets_normalises_categories() -> None:
    """Normalise loaded budget categories"""
    budget_manager = BudgetManager()

    budget_manager.load_budgets(
        {
            " Food ": 500,
            "TRANSPORT": 200,
        }
    )

    assert budget_manager.get_budget("food") == 500
    assert budget_manager.get_budget("transport") == 200


def test_load_budgets_rejects_invalid_amount() -> None:
    """Reject an invalid stored budget amount"""
    budget_manager = BudgetManager()

    with pytest.raises(InvalidBudgetError):
        budget_manager.load_budgets(
            {
                "food": "invalid",
            }
        )


def test_missing_category_budget_returns_none() -> None:
    """Return none when a category has no budget"""
    budget_manager = BudgetManager()

    assert budget_manager.get_budget("Food") is None
    assert (
        budget_manager.get_remaining_budget(
            "Food",
            [],
        )
        is None
    )


def test_missing_budget_status_is_not_set() -> None:
    """Return not set when no budget exists"""
    budget_manager = BudgetManager()

    status = budget_manager.get_budget_status(
        "Food",
        [],
    )

    assert status == "not set"


def test_report_without_income_has_zero_savings_rate() -> None:
    """Return zero savings rate without income"""
    report_manager = ReportManager()

    transactions = [
        Transaction(
            100,
            "expense",
            "Food",
            "",
            "2026-07-01",
        ),
    ]

    savings_rate = report_manager.get_savings_rate(
        transactions,
        "2026-07",
    )

    assert savings_rate == 0


def test_report_for_empty_month() -> None:
    """Return zero values for an empty month"""
    report_manager = ReportManager()
    transactions = create_transactions()

    assert (
        report_manager.get_monthly_income(
            transactions,
            "2026-09",
        )
        == 0
    )

    assert (
        report_manager.get_monthly_expenses(
            transactions,
            "2026-09",
        )
        == 0
    )

    assert (
        report_manager.get_monthly_balance(
            transactions,
            "2026-09",
        )
        == 0
    )

    assert (
        report_manager.get_spending_by_category(
            transactions,
            "2026-09",
        )
        == {}
    )


def test_filter_returns_empty_list_for_unknown_category() -> None:
    """Return no transactions for an unknown category"""
    filtered = TransactionFilter.by_category(
        create_transactions(),
        "Entertainment",
    )

    assert filtered == []


def test_filter_amount_range_with_no_limits() -> None:
    """Return all transactions without amount limits"""
    transactions = create_transactions()

    filtered = TransactionFilter.by_amount_range(
        transactions,
    )

    assert filtered == transactions


def test_filter_amount_range_excludes_values() -> None:
    """Exclude values outside the amount range"""
    filtered = TransactionFilter.by_amount_range(
        create_transactions(),
        minimum_amount=200,
        maximum_amount=1000,
    )

    assert len(filtered) == 1
    assert filtered[0].category == "Food"