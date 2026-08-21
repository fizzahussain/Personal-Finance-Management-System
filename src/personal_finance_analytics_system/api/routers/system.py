import os

from fastapi import APIRouter

router = APIRouter(
    prefix="",
    tags=["system"],
)


@router.get("/")
def read_root() -> dict[str, str]:
    """Return basic API information"""
    return {"message": "Personal Finance Analytics API"}


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status"""
    return {"status": "healthy"}


@router.get("/version")
def get_version() -> dict[str, str]:
    """Return the API version"""
    return {"version": "1.3.0"}


@router.get("/config")
def get_public_config() -> dict[str, str]:
    """Return safe application configuration"""
    return {
        "api_prefix": "/api/v1",
        "environment": "production" if os.getenv("VERCEL") else "development",
    }
