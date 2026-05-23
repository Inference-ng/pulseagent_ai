"""Recommendation Router (Task B) — Get Personalized Recommendations"""

import asyncio
import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.request import RecommendRequest
from app.schemas.response import RecommendResponse
from app.services.agent_service import run_task_b
from app.services.db_service import log_recommendation, log_audit
from app.utils.constants import AGENT_TIMEOUT, VALID_DOMAINS

router = APIRouter(prefix="/api/v1", tags=["tasks"])


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(
    req: RecommendRequest,
    background_tasks: BackgroundTasks,
):
    """
    POST /api/v1/recommend
    
    Task B: Get personalized product recommendations for a user.
    Handles cold-start users and cross-domain recommendations.
    
    Args:
        req: RecommendRequest with user_persona, top_k, domain
        background_tasks: FastAPI background tasks for logging
        
    Returns:
        RecommendResponse with ranked list of recommendations
        
    Raises:
        HTTPException: If domain invalid, agent fails, or times out
    """
    start_time = time.time()
    status_code = 200
    error_msg = None
    
    try:
        # Validate domain
        if req.domain not in VALID_DOMAINS:
            status_code = 422
            error_msg = f"Invalid domain: {req.domain}"
            raise HTTPException(
                status_code=422,
                detail=f"Domain must be one of: {', '.join(VALID_DOMAINS)}",
            )
        
        # Call agent with timeout
        try:
            result = await asyncio.wait_for(
                run_task_b(req.user_persona, req.top_k, req.domain, req.context_query),
                timeout=AGENT_TIMEOUT,
            )
        except asyncio.TimeoutError:
            status_code = 504
            error_msg = "Agent execution timeout"
            raise HTTPException(
                status_code=504,
                detail="Agent took too long to respond (timeout)",
            )
        except Exception as e:
            status_code = 500
            error_msg = str(e)
            raise HTTPException(
                status_code=500,
                detail=f"Agent error: {str(e)}",
            )
        
        # Validate response structure
        if not all(key in result for key in [
            "recommendations",
            "is_cold_start",
            "total",
        ]):
            status_code = 500
            error_msg = "Invalid agent response structure"
            raise HTTPException(
                status_code=500,
                detail="Agent returned invalid response structure",
            )
        
        # Build response
        response = RecommendResponse(**result)
        
        # Log to database in background
        background_tasks.add_task(
            log_recommendation,
            req.user_persona.get("user_id", "unknown"),
            result.get("recommendations", []),
            req.domain,
            result.get("is_cold_start", False),
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        status_code = 500
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}",
        )
    
    finally:
        # Log audit in background
        duration = int((time.time() - start_time) * 1000)  # ms
        background_tasks.add_task(
            log_audit,
            "/api/v1/recommend",
            "POST",
            status_code,
            duration,
            error_msg,
        )
