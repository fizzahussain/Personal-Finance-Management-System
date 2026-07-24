from typing import Any

import httpx

API_BASE_URL = "http://127.0.0.1:8000/api/v1"
REQUEST_TIMEOUT = 10.0


class ApiClientError(Exception):
    """Represent an API communication error"""


def get_authorization_headers(
    access_token: str | None,
) -> dict[str, str]:
    """Return bearer authorization headers"""
    if not access_token:
        return {}

    return {
        "Authorization": f"Bearer {access_token}",
    }


def request(
    method: str,
    path: str,
    access_token: str | None = None,
    **kwargs: Any,
) -> Any:
    """Send a request to the finance API"""
    supplied_headers = kwargs.pop("headers", {})

    headers = {
        **supplied_headers,
        **get_authorization_headers(access_token),
    }

    try:
        response = httpx.request(
            method=method,
            url=f"{API_BASE_URL}{path}",
            headers=headers,
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


def register_user(
    email: str,
    password: str,
) -> dict[str, Any]:
    """Register a user"""
    return request(
        "POST",
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )


def login_user(
    email: str,
    password: str,
) -> dict[str, Any]:
    """Login and return an access token"""
    return request(
        "POST",
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


def get_current_user(
    access_token: str,
) -> dict[str, Any]:
    """Return the authenticated user"""
    return request(
        "GET",
        "/auth/me",
        access_token=access_token,
    )


def get_transactions(
    params: dict[str, str | float] | None = None,
    access_token: str | None = None,
) -> list[dict[str, Any]]:
    """Return transactions"""
    return request(
        "GET",
        "/transactions",
        access_token=access_token,
        params=params,
    )


def get_transaction(
    transaction_id: int,
    access_token: str | None = None,
) -> dict[str, Any]:
    """Return one transaction"""
    return request(
        "GET",
        f"/transactions/{transaction_id}",
        access_token=access_token,
    )


def create_transaction(
    transaction: dict[str, Any],
    access_token: str | None = None,
) -> dict[str, Any]:
    """Create a transaction"""
    return request(
        "POST",
        "/transactions",
        access_token=access_token,
        json=transaction,
    )


def get_summary(
    access_token: str | None = None,
) -> dict[str, Any]:
    """Return transaction totals"""
    return request(
        "GET",
        "/transactions/summary",
        access_token=access_token,
    )


def get_budgets(
    access_token: str | None = None,
) -> list[dict[str, Any]]:
    """Return category budgets"""
    return request(
        "GET",
        "/budgets",
        access_token=access_token,
    )


def set_budget(
    category: str,
    amount: float,
    access_token: str | None = None,
) -> dict[str, Any]:
    """Create or update a category budget"""
    return request(
        "PUT",
        f"/budgets/categories/{category}",
        access_token=access_token,
        json={
            "amount": amount,
        },
    )


def get_budget_statuses(
    access_token: str | None = None,
) -> list[dict[str, Any]]:
    """Return budget analytics"""
    return request(
        "GET",
        "/budgets/status",
        access_token=access_token,
    )


def get_date_range_report(
    start_date: str,
    end_date: str,
    access_token: str | None = None,
) -> dict[str, Any]:
    """Return a report for a date range"""
    return request(
        "GET",
        "/reports",
        access_token=access_token,
        params={
            "start_date": start_date,
            "end_date": end_date,
        },
    )


def download_report(
    start_date: str,
    end_date: str,
    report_format: str,
    access_token: str | None = None,
) -> bytes:
    """Download a report file"""
    try:
        response = httpx.get(
            f"{API_BASE_URL}/reports/download",
            headers=get_authorization_headers(
                access_token
            ),
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