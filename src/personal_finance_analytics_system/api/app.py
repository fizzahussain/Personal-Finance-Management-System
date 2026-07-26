import time

from fastapi import FastAPI, Request
from fastapi.responses import Response

from personal_finance_analytics_system.api.error_handlers import (
    register_error_handlers,
)
from personal_finance_analytics_system.api.routers.auth import (
    router as auth_router,
)
from personal_finance_analytics_system.api.routers.budgets import (
    router as budgets_router,
)
from personal_finance_analytics_system.api.routers.reports import (
    router as reports_router,
)
from personal_finance_analytics_system.api.routers.system import (
    router as system_router,
)
from personal_finance_analytics_system.api.routers.transactions import (
    router as transactions_router,
)
from personal_finance_analytics_system.logging_config import (
    configure_logging,
    get_logger,
)

API_PREFIX = "/api/v1"

configure_logging()

logger = get_logger(__name__)

app = FastAPI(
    title="Personal Finance Analytics API",
    description=(
        "Backend API for managing personal finance data, "
        "including transactions, budgets, summaries, and reports"
    ),
    version="1.3.0",
)


@app.middleware("http")
async def log_http_request(
    request: Request,
    call_next,
) -> Response:
    """Log API requests and responses"""
    started_at = time.perf_counter()

    logger.debug(
        "Request started method=%s path=%s",
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (
            time.perf_counter() - started_at
        ) * 1000

        logger.exception(
            "Unhandled request error method=%s "
            "path=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (
        time.perf_counter() - started_at
    ) * 1000

    if response.status_code >= 500:
        logger.error(
            "Request failed method=%s path=%s "
            "status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
    elif response.status_code >= 400:
        logger.warning(
            "Request rejected method=%s path=%s "
            "status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
    else:
        logger.info(
            "Request completed method=%s path=%s "
            "status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

    return response

'''
@app.get("/test-error")
def test_error() -> None:
    """Raise a temporary test error"""
    raise RuntimeError("Temporary logging test")
'''

register_error_handlers(app)

app.include_router(
    system_router,
    prefix=API_PREFIX,
)
app.include_router(
    auth_router,
    prefix=API_PREFIX,
)
app.include_router(
    transactions_router,
    prefix=API_PREFIX,
)
app.include_router(
    budgets_router,
    prefix=API_PREFIX,
)
app.include_router(
    reports_router,
    prefix=API_PREFIX,
)


def run() -> None:
    """Run the API development server"""
    import uvicorn

    logger.info(
        "Starting API host=%s port=%s",
        "127.0.0.1",
        8000,
    )

    uvicorn.run(
    "personal_finance_analytics_system.api.app:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    reload_dirs=[
        "src",
    ],
    reload_excludes=[
        "logs",
        "logs/*",
        "*.log",
    ],
)


if __name__ == "__main__":
    run()