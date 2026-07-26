from datetime import date
from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import Response

from personal_finance_analytics_system.api.dependencies import (
    get_report_service,
)
from personal_finance_analytics_system.api.schemas import (
    DateRangeReportResponse,
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
    "",
    response_model=DateRangeReportResponse,
)
def get_date_range_report(
    service: ReportServiceDependency,
    start_date: Annotated[
        date,
        Query(),
    ],
    end_date: Annotated[
        date,
        Query(),
    ],
) -> DateRangeReportResponse:
    """Return a financial report for a date range"""
    try:
        report = service.get_date_range_report(
            start_date,
            end_date,
        )
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

    return DateRangeReportResponse(
        start_date=report["start_date"],
        end_date=report["end_date"],
        income=float(report["income"]),
        expenses=float(report["expenses"]),
        balance=float(report["balance"]),
        savings_rate=float(report["savings_rate"]),
        spending_by_category=dict(
            report["spending_by_category"]
        ),
    )


@router.get("/download")
def download_date_range_report(
    service: ReportServiceDependency,
    start_date: Annotated[
        date,
        Query(),
    ],
    end_date: Annotated[
        date,
        Query(),
    ],
    report_format: Annotated[
        Literal["csv", "json"],
        Query(alias="format"),
    ] = "csv",
) -> Response:
    """Download a financial report"""
    try:
        if report_format == "csv":
            content = service.export_date_range_report_csv(
                start_date,
                end_date,
            )
            media_type = "text/csv"
        else:
            content = service.export_date_range_report_json(
                start_date,
                end_date,
            )
            media_type = "application/json"
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

    filename = (
        f"financial-report-"
        f"{start_date.isoformat()}-"
        f"{end_date.isoformat()}."
        f"{report_format}"
    )

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
        },
    )


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