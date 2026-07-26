from pathlib import Path

from personal_finance_analytics_system.services.transaction_service import (
    TransactionService,
)
from personal_finance_analytics_system.sqlite_storage import (
    SqliteStorage,
)
from personal_finance_analytics_system.transaction import Transaction


def test_create_and_list_transactions(
    tmp_path: Path,
) -> None:
    """Create and return stored transactions"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    service = TransactionService(storage)

    transaction = Transaction(
        amount=250,
        transaction_type="expense",
        category="Food",
        description="Groceries",
        transaction_date="2026-07-23",
    )

    created_transaction = service.create_transaction(
        transaction
    )

    transactions = service.list_transactions()

    assert created_transaction is transaction
    assert len(transactions) == 1
    assert transactions[0].amount == 250
    assert transactions[0].transaction_type == "expense"
    assert transactions[0].category == "Food"
    assert transactions[0].description == "Groceries"
    assert (
        transactions[0].transaction_date
        == "2026-07-23"
    )


def test_get_transaction_summary(
    tmp_path: Path,
) -> None:
    """Calculate transaction totals"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    service = TransactionService(storage)

    service.create_transaction(
        Transaction(
            amount=5000,
            transaction_type="income",
            category="Salary",
            description="Monthly salary",
            transaction_date="2026-07-01",
        )
    )

    service.create_transaction(
        Transaction(
            amount=500,
            transaction_type="expense",
            category="Food",
            description="Groceries",
            transaction_date="2026-07-02",
        )
    )

    service.create_transaction(
        Transaction(
            amount=250,
            transaction_type="expense",
            category="Transport",
            description="Travel",
            transaction_date="2026-07-03",
        )
    )

    summary = service.get_summary()

    assert summary == {
        "total_income": 5000,
        "total_expenses": 750,
        "balance": 4250,
        "transaction_count": 3,
    }


def test_get_empty_transaction_summary(
    tmp_path: Path,
) -> None:
    """Return zero totals without transactions"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    service = TransactionService(storage)

    summary = service.get_summary()

    assert summary == {
        "total_income": 0,
        "total_expenses": 0,
        "balance": 0,
        "transaction_count": 0,
    }


def create_service_with_transactions(
    tmp_path: Path,
) -> TransactionService:
    """Create a service containing test transactions"""
    database_path = tmp_path / "transactions.db"
    storage = SqliteStorage(str(database_path))
    service = TransactionService(storage)

    transactions = [
        Transaction(
            amount=5000,
            transaction_type="income",
            category="Salary",
            description="Monthly salary",
            transaction_date="2026-07-01",
        ),
        Transaction(
            amount=500,
            transaction_type="expense",
            category="Food",
            description="Groceries",
            transaction_date="2026-07-02",
        ),
        Transaction(
            amount=250,
            transaction_type="expense",
            category="Transport",
            description="Bus pass",
            transaction_date="2026-07-03",
        ),
    ]

    for transaction in transactions:
        service.create_transaction(transaction)

    return service


def test_filter_transactions_by_category(
    tmp_path: Path,
) -> None:
    """Filter transactions by category"""
    service = create_service_with_transactions(tmp_path)

    transactions = service.list_transactions(
        category="Food",
    )

    assert len(transactions) == 1
    assert transactions[0].category == "Food"


def test_filter_transactions_by_type(
    tmp_path: Path,
) -> None:
    """Filter transactions by transaction type"""
    service = create_service_with_transactions(tmp_path)

    transactions = service.list_transactions(
        transaction_type="expense",
    )

    assert len(transactions) == 2
    assert all(
        transaction.transaction_type == "expense"
        for transaction in transactions
    )


def test_filter_transactions_by_date(
    tmp_path: Path,
) -> None:
    """Filter transactions by date"""
    service = create_service_with_transactions(tmp_path)

    transactions = service.list_transactions(
        transaction_date="2026-07-03",
    )

    assert len(transactions) == 1
    assert transactions[0].category == "Transport"


def test_filter_transactions_by_amount_range(
    tmp_path: Path,
) -> None:
    """Filter transactions by amount range"""
    service = create_service_with_transactions(tmp_path)

    transactions = service.list_transactions(
        minimum_amount=300,
        maximum_amount=1000,
    )

    assert len(transactions) == 1
    assert transactions[0].amount == 500


def test_combine_transaction_filters(
    tmp_path: Path,
) -> None:
    """Combine multiple transaction filters"""
    service = create_service_with_transactions(tmp_path)

    transactions = service.list_transactions(
        transaction_type="expense",
        minimum_amount=300,
    )

    assert len(transactions) == 1
    assert transactions[0].category == "Food"


def test_get_transaction_by_id(
    tmp_path: Path,
) -> None:
    """Return one stored transaction by ID"""
    storage = SqliteStorage(
        str(tmp_path / "transactions.db")
    )
    service = TransactionService(storage)

    created = service.create_transaction(
        Transaction(
            amount=500,
            transaction_type="expense",
            category="Food",
            description="Groceries",
            transaction_date="2026-07-23",
        )
    )

    assert created.transaction_id is not None

    transaction = service.get_transaction(
        created.transaction_id
    )

    assert transaction is not None
    assert (
        transaction.transaction_id
        == created.transaction_id
    )
    assert transaction.amount == 500


def test_get_missing_transaction_by_id(
    tmp_path: Path,
) -> None:
    """Return none for a missing transaction"""
    storage = SqliteStorage(
        str(tmp_path / "transactions.db")
    )
    service = TransactionService(storage)

    transaction = service.get_transaction(999)

    assert transaction is None