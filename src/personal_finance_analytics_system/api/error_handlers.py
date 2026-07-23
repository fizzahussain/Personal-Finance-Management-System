from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from personal_finance_analytics_system.exceptions import (
    FinanceError,
    StorageError,
)


def register_error_handlers(app: FastAPI) -> None:
    """Register application exception handlers"""

    @app.exception_handler(StorageError)
    async def handle_storage_error(
        request: Request,
        error: StorageError,
    ) -> JSONResponse:
        """Return a storage error response"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(error),
            },
        )

    @app.exception_handler(FinanceError)
    async def handle_finance_error(
        request: Request,
        error: FinanceError,
    ) -> JSONResponse:
        """Return a finance error response"""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(error),
            },
        )