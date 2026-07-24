from fastapi.testclient import TestClient

from personal_finance_analytics_system.api.app import app

client = TestClient(app)


def test_root_endpoint() -> None:
    """Return basic API information"""
    response = client.get("/api/v1/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Personal Finance Analytics API",
        "status": "running",
        "api_version": "v1",
    }


def test_health_endpoint() -> None:
    """Return a healthy API status"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_openapi_documentation() -> None:
    """Expose the OpenAPI schema"""
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert schema["info"]["title"] == (
        "Personal Finance Analytics API"
    )
    assert schema["info"]["version"] == "1.0.0"
    assert "/api/v1/" in schema["paths"]
    assert "/api/v1/health" in schema["paths"]


def test_version_endpoint() -> None:
    """Return API version information"""
    response = client.get("/api/v1/version")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Personal Finance Analytics API",
        "version": "1.0.0",
        "api_version": "v1",
    }


def test_config_endpoint() -> None:
    """Return safe public configuration"""
    response = client.get("/api/v1/config")

    assert response.status_code == 200
    assert response.json() == {
        "currency": "USD",
        "available_report_formats": [
            "csv",
            "json",
        ],
        "minimum_report_date": "2020-01-01",
    }