"""Health Check Router — Placeholder for Phase 3"""

from fastapi import APIRouter

router = APIRouter(prefix="", tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint — to be implemented in Phase 3"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "database": "connected",
    }
