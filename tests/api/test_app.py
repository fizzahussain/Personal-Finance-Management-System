import pytest
from fastapi.testclient import TestClient

from personal_finance_analytics_system.api.app import app
from personal_finance_analytics_system.api.dependencies import (
    get_current_user,
)
from personal_finance_analytics_system.user import User


def override_current_user() -> User:
    """Return an authenticated test user"""
    return User(
        user_id=1,
        email="test@example.com",
        password_hash="test-password-hash",
    )


@pytest.fixture
def client() -> TestClient:
    """Return an authenticated API test client"""
    app.dependency_overrides[get_current_user] = (
        override_current_user
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_root_endpoint(
    client: TestClient,
) -> None:
    """Return basic API information"""
    response = client.get("/api/v1/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Personal Finance Analytics API",
    }


def test_health_endpoint(
    client: TestClient,
) -> None:
    """Return a healthy API status"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_version_endpoint(
    client: TestClient,
) -> None:
    """Return API version information"""
    response = client.get("/api/v1/version")

    assert response.status_code == 200
    assert response.json() == {
        "version": "1.0.0",
    }


def test_config_endpoint(
    client: TestClient,
) -> None:
    """Return safe application configuration"""
    response = client.get("/api/v1/config")

    assert response.status_code == 200
    assert response.json() == {
        "api_prefix": "/api/v1",
        "environment": "development",
    }


def test_openapi_documentation() -> None:
    """Expose the OpenAPI schema"""
    with TestClient(app) as test_client:
        response = test_client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert schema["info"]["title"] == (
        "Personal Finance Analytics API"
    )
    assert schema["info"]["version"] == "1.0.0"
    assert "/api/v1/" in schema["paths"]
    assert "/api/v1/health" in schema["paths"]


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/",
        "/api/v1/health",
        "/api/v1/version",
        "/api/v1/config",
    ],
)
def test_system_endpoints_require_authentication(
    path: str,
) -> None:
    """Reject unauthenticated system requests"""
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        response = test_client.get(path)

    assert response.status_code == 401