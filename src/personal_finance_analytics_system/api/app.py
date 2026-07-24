from fastapi import FastAPI

from personal_finance_analytics_system.api.error_handlers import (
    register_error_handlers,
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

API_PREFIX = "/api/v1"

app = FastAPI(
    title="Personal Finance Analytics API",
    description=(
        "Backend API for managing personal finance data, "
        "including transactions, budgets, summaries, and reports"
    ),
    version="1.0.0",
)

register_error_handlers(app)

app.include_router(
    system_router,
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