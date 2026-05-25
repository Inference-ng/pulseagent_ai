"""Database Service — Prisma Wrapper Methods"""

import json
from app.database import prisma
from typing import Any, Dict, List


async def _get_or_create_user(user_id: str) -> str:
    """
    Upsert a User record and return its internal primary-key id (cuid).

    The Simulation and Recommendation models relate via User.id (cuid),
    NOT the human-readable User.user_id string.
    """
    user = await prisma.user.upsert(
        where={"user_id": user_id},
        data={"create": {"user_id": user_id}, "update": {}},
    )
    return user.id  # cuid — the actual FK expected by child models


async def log_simulation(
    user_id: str, product: Dict, result: Dict
) -> None:
    try:
        if not prisma.is_connected():
            return

        pk = await _get_or_create_user(user_id)

        await prisma.simulation.create(
            data={
                "userId":          pk,
                "productName":     product.get("name", ""),
                "productData":     json.dumps(product),
                "predictedRating": result.get("predicted_rating", 0),
                "simulatedReview": result.get("simulated_review", ""),
                "confidence":      result.get("confidence", 0),
                "reasoning":       result.get("reasoning", ""),
            }
        )
    except Exception as e:
        print(f"Error logging simulation: {e}")


async def log_recommendation(
    user_id: str, recommendations: List, domain: str, is_cold_start: bool
) -> None:
    try:
        if not prisma.is_connected():
            return

        pk = await _get_or_create_user(user_id)

        await prisma.recommendation.create(
            data={
                "userId":              pk,
                "recommendationsJson": json.dumps(recommendations),
                "domain":              domain,
                "isColdStart":         is_cold_start,
            }
        )
    except Exception as e:
        print(f"Error logging recommendation: {e}")


async def log_audit(
    endpoint: str,
    method: str,
    status: int,
    duration: int,
    error: str = None,
) -> None:
    try:
        if not prisma.is_connected():
            return
        await prisma.auditlog.create(
            data={
                "endpoint": endpoint,
                "method":   method,
                "status":   status,
                "duration": duration,
                "error":    error,
            }
        )
    except Exception as e:
        print(f"Error logging audit: {e}")