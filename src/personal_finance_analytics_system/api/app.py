from fastapi import FastAPI

app = FastAPI(
    title="Personal Finance Analytics API",
    description="Backend API for managing personal finance data",
    version="1.0.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Return basic API information"""
    return {
        "name": "Personal Finance Analytics API",
        "status": "running",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status"""
    return {"status": "healthy"}