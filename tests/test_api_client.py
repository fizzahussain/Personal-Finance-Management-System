import httpx
import pytest

from personal_finance_analytics_system.streamlit_app.api_client import (
    ApiClientError,
    request,
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

    assert request("DELETE", "/transactions/1") is None


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