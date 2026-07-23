from fastapi import FastAPI

from personal_finance_analytics_system.api.routers.system import (
    router as system_router,
)

app = FastAPI(
    title="Personal Finance Analytics API",
    description="Backend API for managing personal finance data",
    version="1.0.0",
)

app.include_router(system_router)