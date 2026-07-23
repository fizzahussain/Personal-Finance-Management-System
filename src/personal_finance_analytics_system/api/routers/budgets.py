from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from personal_finance_analytics_system.api.dependencies import (
    get_budget_service,
)
from personal_finance_analytics_system.api.schemas import (
    CategoryBudgetResponse,
    CategoryBudgetStatusResponse,
    CategoryBudgetUpdate,
)
from personal_finance_analytics_system.exceptions import FinanceError
from personal_finance_analytics_system.services.budget_service import (
    BudgetService,
)

router = APIRouter(
    prefix="/budgets",
    tags=["budgets"],
)

BudgetServiceDependency = Annotated[
    BudgetService,
    Depends(get_budget_service),
]


@router.get(
    "",
    response_model=list[CategoryBudgetResponse],
)
def list_budgets(
    service: BudgetServiceDependency,
) -> list[CategoryBudgetResponse]:
    """Return all category budgets"""
    try:
        budgets = service.list_budgets()
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    return [
        CategoryBudgetResponse(
            category=category,
            amount=amount,
        )
        for category, amount in budgets.items()
    ]

@router.get(
    "/status",
    response_model=list[CategoryBudgetStatusResponse],
)
def get_budget_statuses(
    service: BudgetServiceDependency,
) -> list[CategoryBudgetStatusResponse]:
    """Return status details for all budgets"""
    try:
        budget_statuses = service.get_budget_statuses()
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    return [
        CategoryBudgetStatusResponse(
            category=str(item["category"]),
            budget=float(item["budget"]),
            spending=float(item["spending"]),
            remaining=float(item["remaining"]),
            percentage_used=float(
                item["percentage_used"]
            ),
            status=str(item["status"]),
        )
        for item in budget_statuses
    ]

@router.put(
    "/categories/{category}",
    response_model=CategoryBudgetResponse,
)
def set_category_budget(
    category: str,
    budget_data: CategoryBudgetUpdate,
    service: BudgetServiceDependency,
) -> CategoryBudgetResponse:
    """Create or update a category budget"""
    cleaned_category = category.strip()

    if not cleaned_category:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Category cannot be empty",
        )

    try:
        amount = service.set_category_budget(
            category=cleaned_category,
            amount=budget_data.amount,
        )
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return CategoryBudgetResponse(
    category=cleaned_category.lower(),
    amount=amount,
)