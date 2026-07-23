from fastapi import FastAPI
from fastapi.testclient import TestClient

from personal_finance_analytics_system.api.error_handlers import (
    register_error_handlers,
)
from personal_finance_analytics_system.exceptions import (
    InvalidTransactionError,
    StorageError,
)

test_app = FastAPI()
register_error_handlers(test_app)


@test_app.get("/finance-error")
def raise_finance_error() -> None:
    """Raise a finance error"""
    raise InvalidTransactionError(
        "Transaction data is invalid"
    )


@test_app.get("/storage-error")
def raise_storage_error() -> None:
    """Raise a storage error"""
    raise StorageError(
        "Storage is unavailable"
    )


client = TestClient(
    test_app,
    raise_server_exceptions=False,
)


def test_handles_finance_error() -> None:
    """Return a client error for finance errors"""
    response = client.get("/finance-error")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Transaction data is invalid",
    }


def test_handles_storage_error() -> None:
    """Return a server error for storage errors"""
    response = client.get("/storage-error")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Storage is unavailable",
    }