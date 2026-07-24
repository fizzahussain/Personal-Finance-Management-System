from typing import Any

import httpx

API_BASE_URL = "http://127.0.0.1:8000/api/v1"
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


def get_date_range_report(
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Return a report for a date range"""
    return request(
        "GET",
        "/reports",
        params={
            "start_date": start_date,
            "end_date": end_date,
        },
    )


def download_report(
    start_date: str,
    end_date: str,
    report_format: str,
) -> bytes:
    """Download a report file"""
    try:
        response = httpx.get(
            f"{API_BASE_URL}/reports/download",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "format": report_format,
            },
            timeout=REQUEST_TIMEOUT,
        )
    except httpx.RequestError as error:
        raise ApiClientError(
            "Unable to connect to the finance API"
        ) from error

    if response.status_code >= 400:
        try:
            detail = response.json().get(
                "detail",
                "The report download failed",
            )
        except ValueError:
            detail = "The report download failed"

        raise ApiClientError(str(detail))

    return response.content