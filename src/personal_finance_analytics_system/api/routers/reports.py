from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from personal_finance_analytics_system.api.dependencies import (
    get_report_service,
)
from personal_finance_analytics_system.api.schemas import (
    MonthlyReportResponse,
)
from personal_finance_analytics_system.exceptions import FinanceError
from personal_finance_analytics_system.services.report_service import (
    ReportService,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

ReportServiceDependency = Annotated[
    ReportService,
    Depends(get_report_service),
]


@router.get(
    "/monthly/{month}",
    response_model=MonthlyReportResponse,
)
def get_monthly_report(
    month: str,
    service: ReportServiceDependency,
) -> MonthlyReportResponse:
    """Return a monthly financial report"""
    try:
        report = service.get_monthly_report(month)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except FinanceError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    return MonthlyReportResponse(
        month=str(report["month"]),
        income=float(report["income"]),
        expenses=float(report["expenses"]),
        balance=float(report["balance"]),
        savings_rate=float(report["savings_rate"]),
        spending_by_category=dict(
            report["spending_by_category"]
        ),
    )