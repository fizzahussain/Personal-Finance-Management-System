from fastapi import APIRouter

API_NAME = "Personal Finance Analytics API"
API_VERSION = "1.0.0"
API_ROUTE_VERSION = "v1"

router = APIRouter(
    tags=["system"],
)


@router.get("/")
def read_root() -> dict[str, str]:
    """Return basic API information"""
    return {
        "name": API_NAME,
        "status": "running",
        "api_version": API_ROUTE_VERSION,
    }


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status"""
    return {
        "status": "healthy",
    }


@router.get("/version")
def get_version() -> dict[str, str]:
    """Return application version information"""
    return {
        "name": API_NAME,
        "version": API_VERSION,
        "api_version": API_ROUTE_VERSION,
    }


@router.get("/config")
def get_public_config() -> dict[str, object]:
    """Return safe public configuration"""
    return {
        "currency": "USD",
        "available_report_formats": [
            "csv",
            "json",
        ],
        "minimum_report_date": "2020-01-01",
    }