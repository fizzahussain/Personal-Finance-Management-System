import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.exceptions import (
    InvalidBudgetError,
    StorageError,
)
from personal_finance_analytics_system.sqlite_budget_storage import (
    SqliteBudgetStorage,
)


def test_save_and_load_budgets(
    tmp_path: Path,
) -> None:
    """Save and load category budgets"""
    storage = SqliteBudgetStorage(
        str(tmp_path / "finance.db"),
        user_id=1,
    )

    storage.save_budgets(
        {
            "food": 500,
            "transport": 300,
        }
    )

    assert storage.load_budgets() == {
        "food": 500.0,
        "transport": 300.0,
    }


def test_rejects_non_finite_stored_budget(
    tmp_path: Path,
) -> None:
    """Reject a non-finite budget when loading it into the manager"""
    file_path = tmp_path / "finance.db"
    storage = SqliteBudgetStorage(str(file_path))
    storage.save_budgets(
        {
            "food": float("inf"),
        }
    )

    manager = BudgetManager()

    with pytest.raises(
        InvalidBudgetError,
        match="Stored budget data is invalid",
    ):
        manager.load_budgets(storage.load_budgets())


def test_save_replaces_current_user_budgets(
    tmp_path: Path,
) -> None:
    """Replace budgets for the current user"""
    storage = SqliteBudgetStorage(
        str(tmp_path / "finance.db"),
        user_id=1,
    )

    storage.save_budgets(
        {
            "food": 500,
            "transport": 300,
        }
    )

    storage.save_budgets(
        {
            "housing": 1200,
        }
    )

    assert storage.load_budgets() == {
        "housing": 1200.0,
    }


def test_budgets_are_isolated_by_user(
    tmp_path: Path,
) -> None:
    """Keep each user's budgets separate"""
    file_path = tmp_path / "finance.db"

    first_user_storage = SqliteBudgetStorage(
        str(file_path),
        user_id=1,
    )
    second_user_storage = SqliteBudgetStorage(
        str(file_path),
        user_id=2,
    )

    first_user_storage.save_budgets(
        {
            "food": 500,
        }
    )

    second_user_storage.save_budgets(
        {
            "transport": 300,
        }
    )

    assert first_user_storage.load_budgets() == {
        "food": 500.0,
    }

    assert second_user_storage.load_budgets() == {
        "transport": 300.0,
    }


def test_replacing_budgets_does_not_delete_other_users(
    tmp_path: Path,
) -> None:
    """Preserve budgets belonging to other users"""
    file_path = tmp_path / "finance.db"

    first_user_storage = SqliteBudgetStorage(
        str(file_path),
        user_id=1,
    )
    second_user_storage = SqliteBudgetStorage(
        str(file_path),
        user_id=2,
    )

    first_user_storage.save_budgets(
        {
            "food": 500,
        }
    )

    second_user_storage.save_budgets(
        {
            "transport": 300,
        }
    )

    first_user_storage.save_budgets(
        {
            "housing": 1200,
        }
    )

    assert second_user_storage.load_budgets() == {
        "transport": 300.0,
    }


def test_database_contains_user_budget_rows(
    tmp_path: Path,
) -> None:
    """Store user budget rows in SQLite"""
    file_path = tmp_path / "finance.db"

    storage = SqliteBudgetStorage(
        str(file_path),
        user_id=2,
    )

    storage.save_budgets(
        {
            "Food": 500,
        }
    )

    with closing(
        sqlite3.connect(file_path)
    ) as connection:
        rows = connection.execute(
            """
            SELECT
                user_id,
                category,
                amount
            FROM budgets
            """
        ).fetchall()

    assert rows == [
        (
            2,
            "food",
            500.0,
        )
    ]


def test_rejects_invalid_user_id(
    tmp_path: Path,
) -> None:
    """Reject a nonpositive budget user ID"""
    with pytest.raises(
        StorageError,
        match="greater than zero",
    ):
        SqliteBudgetStorage(
            str(tmp_path / "finance.db"),
            user_id=0,
        )