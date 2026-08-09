import httpx
import pytest

from personal_finance_analytics_system.streamlit_app.api_client import (
    ApiClientError,
    create_transaction,
    download_report,
    get_authorization_headers,
    get_budgets,
    get_current_user,
    get_date_range_report,
    get_summary,
    get_transactions,
    login_user,
    register_user,
    request,
    set_budget,
)


def test_request_returns_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return JSON from a successful request"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "status": "ok",
            },
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    result = request(
        "GET",
        "/health",
    )

    assert result == {
        "status": "ok",
    }


def test_request_handles_no_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return none for a no-content response"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=204,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    assert request(
        "GET",
        "/empty",
    ) is None


def test_request_raises_api_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise an API error for failed responses"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=400,
            json={
                "detail": "Invalid request",
            },
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    with pytest.raises(
        ApiClientError,
        match="Invalid request",
    ):
        request(
            "GET",
            "/transactions",
        )


def test_request_uses_default_error_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use a default message for a non-JSON error"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            text="Server error",
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    with pytest.raises(
        ApiClientError,
        match="The API request failed",
    ):
        request(
            "GET",
            "/transactions",
        )


def test_request_handles_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise an API error when the backend is unavailable"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        raise httpx.ConnectError(
            "Connection failed"
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    with pytest.raises(
        ApiClientError,
        match="Unable to connect",
    ):
        request(
            "GET",
            "/health",
        )


def test_authorization_headers_without_token() -> None:
    """Return no authorization header without a token"""
    assert get_authorization_headers(None) == {}


def test_authorization_headers_with_token() -> None:
    """Return a bearer authorization header"""
    assert get_authorization_headers(
        "test-token"
    ) == {
        "Authorization": "Bearer test-token",
    }


def test_request_sends_bearer_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Send the bearer token with an API request"""
    captured_headers: dict[str, str] = {}

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        headers = kwargs["headers"]

        assert isinstance(headers, dict)

        captured_headers.update(headers)

        return httpx.Response(
            status_code=200,
            json=[],
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    request(
        "GET",
        "/transactions",
        access_token="test-token",
    )

    assert captured_headers == {
        "Authorization": "Bearer test-token",
    }


def test_request_preserves_supplied_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preserve custom headers alongside authorization"""
    captured_headers: dict[str, str] = {}

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        headers = kwargs["headers"]

        assert isinstance(headers, dict)

        captured_headers.update(headers)

        return httpx.Response(
            status_code=200,
            json={},
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    request(
        "GET",
        "/auth/me",
        access_token="test-token",
        headers={
            "X-Test": "value",
        },
    )

    assert captured_headers == {
        "X-Test": "value",
        "Authorization": "Bearer test-token",
    }


def test_register_user_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Send registration details to the API"""
    captured: dict[str, object] = {}

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        captured["method"] = method
        captured["url"] = url
        captured["json"] = kwargs["json"]

        return httpx.Response(
            status_code=201,
            json={
                "user_id": 1,
                "email": "person@example.com",
            },
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    result = register_user(
        "person@example.com",
        "secure-password",
    )

    assert captured["method"] == "POST"
    assert str(captured["url"]).endswith(
        "/api/v1/auth/register"
    )
    assert captured["json"] == {
        "email": "person@example.com",
        "password": "secure-password",
    }
    assert result["user_id"] == 1


def test_login_user_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Send login details to the API"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        assert method == "POST"
        assert url.endswith(
            "/api/v1/auth/login"
        )
        assert kwargs["json"] == {
            "email": "person@example.com",
            "password": "secure-password",
        }

        return httpx.Response(
            status_code=200,
            json={
                "access_token": "test-token",
                "token_type": "bearer",
            },
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    result = login_user(
        "person@example.com",
        "secure-password",
    )

    assert result["access_token"] == "test-token"


def test_get_current_user_sends_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Request the authenticated user with a token"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        assert method == "GET"
        assert url.endswith("/api/v1/auth/me")
        assert kwargs["headers"] == {
            "Authorization": "Bearer test-token",
        }

        return httpx.Response(
            status_code=200,
            json={
                "user_id": 1,
                "email": "person@example.com",
            },
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    result = get_current_user(
        "test-token"
    )

    assert result["email"] == "person@example.com"


@pytest.mark.parametrize(
    ("function_call", "expected_path"),
    [
        (
            lambda: get_transactions(
                access_token="test-token"
            ),
            "/api/v1/transactions",
        ),
        (
            lambda: get_summary(
                "test-token"
            ),
            "/api/v1/transactions/summary",
        ),
        (
            lambda: get_budgets(
                "test-token"
            ),
            "/api/v1/budgets",
        ),
        (
            lambda: get_date_range_report(
                "2026-06-01",
                "2026-06-23",
                "test-token",
            ),
            "/api/v1/reports",
        ),
    ],
)
def test_protected_get_requests_send_token(
    monkeypatch: pytest.MonkeyPatch,
    function_call: object,
    expected_path: str,
) -> None:
    """Send authorization for protected GET requests"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        assert method == "GET"
        assert url.endswith(expected_path)
        assert kwargs["headers"] == {
            "Authorization": "Bearer test-token",
        }

        return httpx.Response(
            status_code=200,
            json=[],
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    assert callable(function_call)
    function_call()


def test_create_transaction_sends_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Send authorization when creating a transaction"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        assert method == "POST"
        assert kwargs["headers"] == {
            "Authorization": "Bearer test-token",
        }

        return httpx.Response(
            status_code=201,
            json={
                "transaction_id": 1,
            },
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    result = create_transaction(
        {
            "amount": 100,
            "transaction_type": "expense",
            "category": "Food",
            "description": "",
            "transaction_date": "2026-06-10",
        },
        access_token="test-token",
    )

    assert result["transaction_id"] == 1


def test_set_budget_sends_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Send authorization when setting a budget"""

    def fake_request(
        method: str,
        url: str,
        timeout: float,
        **kwargs: object,
    ) -> httpx.Response:
        assert method == "PUT"
        assert kwargs["headers"] == {
            "Authorization": "Bearer test-token",
        }

        return httpx.Response(
            status_code=200,
            json={
                "category": "food",
                "amount": 500,
            },
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    result = set_budget(
        "Food",
        500,
        access_token="test-token",
    )

    assert result["amount"] == 500


def test_download_report_sends_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Send authorization when downloading a report"""

    def fake_get(
        url: str,
        headers: dict[str, str],
        params: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        assert url.endswith(
            "/api/v1/reports/download"
        )
        assert headers == {
            "Authorization": "Bearer test-token",
        }
        assert params == {
            "start_date": "2026-06-01",
            "end_date": "2026-06-23",
            "format": "csv",
        }

        return httpx.Response(
            status_code=200,
            content=b"report-content",
        )

    monkeypatch.setattr(
        httpx,
        "get",
        fake_get,
    )

    result = download_report(
        "2026-06-01",
        "2026-06-23",
        "csv",
        access_token="test-token",
    )

    assert result == b"report-content"


def test_download_report_raises_api_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise an error for a failed report download"""

    def fake_get(
        url: str,
        headers: dict[str, str],
        params: dict[str, str],
        timeout: float,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=401,
            json={
                "detail": (
                    "Access token is invalid or expired"
                ),
            },
        )

    monkeypatch.setattr(
        httpx,
        "get",
        fake_get,
    )

    with pytest.raises(
        ApiClientError,
        match="invalid or expired",
    ):
        download_report(
            "2026-06-01",
            "2026-06-23",
            "csv",
            access_token="expired-token",
        )
        