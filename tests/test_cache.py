from pathlib import Path

from personal_finance_analytics_system.cache import (
    TtlCache,
)
from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction


def test_cache_stores_and_returns_value() -> None:
    """Store and return a cached value"""
    cache = TtlCache(ttl_seconds=30)

    cache.set(
        ("user:1", "summary"),
        {
            "balance": 100,
        },
    )

    assert cache.get(
        ("user:1", "summary")
    ) == {
        "balance": 100,
    }


def test_cache_returns_copies() -> None:
    """Prevent callers from changing cached values"""
    cache = TtlCache(ttl_seconds=30)
    key = ("user:1", "items")

    cache.set(
        key,
        [1, 2],
    )

    first_result = cache.get(key)
    assert isinstance(first_result, list)

    first_result.append(3)

    assert cache.get(key) == [1, 2]


def test_delete_prefix_only_removes_matching_values() -> None:
    """Delete one user's cached values"""
    cache = TtlCache(ttl_seconds=30)

    cache.set(
        ("user:1", "summary"),
        100,
    )
    cache.set(
        ("user:2", "summary"),
        200,
    )

    cache.delete_prefix(("user:1",))

    assert cache.get(
        ("user:1", "summary")
    ) is None
    assert cache.get(
        ("user:2", "summary")
    ) == 200


def test_transaction_creation_invalidates_summary(
    tmp_path: Path,
) -> None:
    """Refresh cached totals after a transaction"""
    cache = TtlCache(ttl_seconds=30)

    service = TransactionService(
        SqliteStorage(
            str(tmp_path / "finance.db"),
            user_id=1,
        ),
        cache=cache,
    )

    assert service.get_summary()["transaction_count"] == 0

    service.create_transaction(
        Transaction(
            amount=100,
            transaction_type="income",
            category="Salary",
            transaction_date="2026-06-01",
        )
    )

    summary = service.get_summary()

    assert summary["transaction_count"] == 1
    assert summary["total_income"] == 100


def test_cache_isolated_by_user(
    tmp_path: Path,
) -> None:
    """Keep cached transaction data separate by user"""
    cache = TtlCache(ttl_seconds=30)
    database_path = tmp_path / "finance.db"

    first_service = TransactionService(
        SqliteStorage(
            str(database_path),
            user_id=1,
        ),
        cache=cache,
    )

    second_service = TransactionService(
        SqliteStorage(
            str(database_path),
            user_id=2,
        ),
        cache=cache,
    )

    first_service.create_transaction(
        Transaction(
            amount=500,
            transaction_type="income",
            category="Salary",
            transaction_date="2026-06-01",
        )
    )

    assert (
        first_service.get_summary()["total_income"]
        == 500
    )
    assert (
        second_service.get_summary()["total_income"]
        == 0
    )