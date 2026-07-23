from fastapi import APIRouter

router = APIRouter(
    tags=["system"],
)


@router.get("/")
def read_root() -> dict[str, str]:
    """Return basic API information"""
    return {
        "name": "Personal Finance Analytics API",
        "status": "running",
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status"""
    return {"status": "healthy"}