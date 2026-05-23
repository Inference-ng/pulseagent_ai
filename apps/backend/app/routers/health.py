"""Health Check Router — API Status"""

from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="", tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict with status, version, and database connection status
    """
    return {
        "status": "ok",
        "version": settings.app_version,
        "app_name": settings.app_name,
        "environment": settings.environment,
        "database": "disabled",
        "tasks": ["A", "B"],
    }
