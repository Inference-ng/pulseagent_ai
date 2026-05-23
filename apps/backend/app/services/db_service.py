"""Database Service — Prisma Wrapper Methods (Phase 5)"""

import json
from app.database import prisma
from typing import Any, Dict, List


async def log_simulation(
    user_id: str, product: Dict, result: Dict
) -> None:
    """
    Store a simulation result in the database.
    
    Args:
        user_id: User identifier
        product: Product data
        result: Simulation result from agent
    """
    try:
        if not prisma.is_connected():
            return
        # Ensure user exists
        await prisma.user.upsert(
            where={"user_id": user_id},
            data={"create": {"user_id": user_id}, "update": {}},
        )

        # Store simulation
        await prisma.simulation.create(
            data={
                "userId": user_id,
                "productName": product.get("name", ""),
                "productData": json.dumps(product),
                "predictedRating": result.get("predicted_rating", 0),
                "simulatedReview": result.get("simulated_review", ""),
                "confidence": result.get("confidence", 0),
                "reasoning": result.get("reasoning", ""),
            }
        )
    except Exception as e:
        print(f"Error logging simulation: {e}")


async def log_recommendation(
    user_id: str, recommendations: List, domain: str, is_cold_start: bool
) -> None:
    """
    Store recommendation results in the database.
    
    Args:
        user_id: User identifier
        recommendations: List of recommendation items
        domain: Product domain
        is_cold_start: Whether this was a cold-start recommendation
    """
    try:
        if not prisma.is_connected():
            return
        # Ensure user exists
        await prisma.user.upsert(
            where={"user_id": user_id},
            data={"create": {"user_id": user_id}, "update": {}},
        )

        # Store recommendations
        await prisma.recommendation.create(
            data={
                "userId": user_id,
                "recommendationsJson": json.dumps(recommendations),
                "domain": domain,
                "isColdStart": is_cold_start,
            }
        )
    except Exception as e:
        print(f"Error logging recommendation: {e}")


async def log_audit(
    endpoint: str, method: str, status: int, duration: int, error: str = None
) -> None:
    """
    Log API request to audit log.
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        status: HTTP status code
        duration: Request duration in milliseconds
        error: Error message if any
    """
    try:
        if not prisma.is_connected():
            return
        await prisma.auditlog.create(
            data={
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "duration": duration,
                "error": error,
            }
        )
    except Exception as e:
        print(f"Error logging audit: {e}")
