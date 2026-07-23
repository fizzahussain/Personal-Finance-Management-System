from fastapi.testclient import TestClient

from personal_finance_analytics_system.api.app import app

client = TestClient(app)


def test_root_endpoint() -> None:
    """Return basic API information"""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Personal Finance Analytics API",
        "status": "running",
    }


def test_health_endpoint() -> None:
    """Return a healthy API status"""
    response = client.get("/health")

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
    assert "/" in schema["paths"]
    assert "/health" in schema["paths"]