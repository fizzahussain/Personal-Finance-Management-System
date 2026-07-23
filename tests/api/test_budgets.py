from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from personal_finance_analytics_system.api.app import app
from personal_finance_analytics_system.api.dependencies import (
    get_budget_service,
)
from personal_finance_analytics_system.budget_manager import (
    BudgetManager,
)
from personal_finance_analytics_system.services.budget_service import (
    BudgetService,
)


class FakeBudgetStorage:
    """Store budgets in memory for API tests"""

    def __init__(self) -> None:
        self.budgets: dict[str, float] = {}

    def load_budgets(self) -> dict[str, float]:
        """Return stored budgets"""
        return self.budgets.copy()

    def save_budgets(
        self,
        budgets: dict[str, float],
    ) -> None:
        """Save budgets"""
        self.budgets = budgets.copy()


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Provide an API client with temporary budget storage"""
    service = BudgetService(
        manager=BudgetManager(),
        storage=FakeBudgetStorage(),
    )

    app.dependency_overrides[
        get_budget_service
    ] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_list_budgets_is_initially_empty(
    client: TestClient,
) -> None:
    """Return an empty budget list"""
    response = client.get("/budgets")

    assert response.status_code == 200
    assert response.json() == []


def test_create_category_budget(
    client: TestClient,
) -> None:
    """Create a category budget"""
    response = client.put(
        "/budgets/categories/Food",
        json={
            "amount": 500,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "category": "food",
        "amount": 500.0,
    }


def test_created_budget_is_returned(
    client: TestClient,
) -> None:
    """Return a previously created budget"""
    client.put(
        "/budgets/categories/Food",
        json={
            "amount": 500,
        },
    )

    response = client.get("/budgets")

    assert response.status_code == 200
    assert response.json() == [
        {
            "category": "food",
            "amount": 500.0,
        }
    ]


def test_update_category_budget(
    client: TestClient,
) -> None:
    """Update an existing category budget"""
    client.put(
        "/budgets/categories/Food",
        json={
            "amount": 500,
        },
    )

    response = client.put(
        "/budgets/categories/Food",
        json={
            "amount": 750,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "category": "food",
        "amount": 750.0,
    }


def test_rejects_non_positive_budget(
    client: TestClient,
) -> None:
    """Reject a non-positive budget"""
    response = client.put(
        "/budgets/categories/Food",
        json={
            "amount": 0,
        },
    )

    assert response.status_code == 422