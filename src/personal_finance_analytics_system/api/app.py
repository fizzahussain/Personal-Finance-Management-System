from fastapi import FastAPI

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

app = FastAPI(
    title="Personal Finance Analytics API",
    description="Backend API for managing personal finance data",
    version="1.0.0",
)

app.include_router(system_router)
app.include_router(transactions_router)
app.include_router(budgets_router)
app.include_router(reports_router)
