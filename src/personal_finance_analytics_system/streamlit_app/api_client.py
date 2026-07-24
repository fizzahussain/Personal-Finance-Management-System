from typing import Any

import httpx

API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 10.0


class ApiClientError(Exception):
    """Represent an API communication error"""


def request(
    method: str,
    path: str,
    **kwargs: Any,
) -> Any:
    """Send a request to the finance API"""
    try:
        response = httpx.request(
            method=method,
            url=f"{API_BASE_URL}{path}",
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except httpx.RequestError as error:
        raise ApiClientError(
            "Unable to connect to the finance API"
        ) from error

    if response.status_code >= 400:
        try:
            response_data = response.json()
            detail = response_data.get(
                "detail",
                "The API request failed",
            )
        except ValueError:
            detail = "The API request failed"

        raise ApiClientError(str(detail))

    if response.status_code == 204:
        return None

    return response.json()


def get_transactions(
    params: dict[str, str | float] | None = None,
) -> list[dict[str, Any]]:
    """Return transactions"""
    return request(
        "GET",
        "/transactions",
        params=params,
    )


def get_transaction(
    transaction_id: int,
) -> dict[str, Any]:
    """Return one transaction"""
    return request(
        "GET",
        f"/transactions/{transaction_id}",
    )


def create_transaction(
    transaction: dict[str, Any],
) -> dict[str, Any]:
    """Create a transaction"""
    return request(
        "POST",
        "/transactions",
        json=transaction,
    )


def update_transaction(
    transaction_id: int,
    transaction: dict[str, Any],
) -> dict[str, Any]:
    """Update one transaction"""
    return request(
        "PUT",
        f"/transactions/{transaction_id}",
        json=transaction,
    )


def delete_transaction(
    transaction_id: int,
) -> None:
    """Delete one transaction"""
    request(
        "DELETE",
        f"/transactions/{transaction_id}",
    )


def get_summary() -> dict[str, Any]:
    """Return transaction totals"""
    return request(
        "GET",
        "/transactions/summary",
    )


def get_budgets() -> list[dict[str, Any]]:
    """Return category budgets"""
    return request(
        "GET",
        "/budgets",
    )


def set_budget(
    category: str,
    amount: float,
) -> dict[str, Any]:
    """Create or update a category budget"""
    return request(
        "PUT",
        f"/budgets/categories/{category}",
        json={
            "amount": amount,
        },
    )


def get_budget_statuses() -> list[dict[str, Any]]:
    """Return budget analytics"""
    return request(
        "GET",
        "/budgets/status",
    )


def get_monthly_report(
    month: str,
) -> dict[str, Any]:
    """Return a monthly report"""
    return request(
        "GET",
        f"/reports/monthly/{month}",
    )