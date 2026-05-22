"""Health Check Router — Database & API Health Status"""

from fastapi import APIRouter, HTTPException
from app.database import prisma
from app.config import settings

router = APIRouter(prefix="", tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict with status, version, and database connection status
    """
    try:
        # Test database connection with a simple query
        await prisma.user.count()
        database_status = "connected"
    except Exception as e:
        database_status = f"error: {str(e)}"
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
    
    return {
        "status": "ok",
        "version": settings.app_version,
        "app_name": settings.app_name,
        "environment": settings.environment,
        "database": database_status,
        "tasks": ["A", "B"],
    }
