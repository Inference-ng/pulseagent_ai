"""Review Simulation Router (Task A) — Simulate User Reviews"""

import asyncio
import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.request import SimulateReviewRequest
from app.schemas.response import SimulateReviewResponse
from app.services.agent_service import run_task_a
from app.services.db_service import log_simulation, log_audit
from app.utils.constants import AGENT_TIMEOUT

router = APIRouter(prefix="/api/v1", tags=["tasks"])


@router.post("/simulate-review", response_model=SimulateReviewResponse)
async def simulate_review(
    req: SimulateReviewRequest,
    background_tasks: BackgroundTasks,
):
    """
    POST /api/v1/simulate-review
    
    Task A: Simulate a realistic user review and rating for a product.
    
    Args:
        req: SimulateReviewRequest with user_persona and product details
        background_tasks: FastAPI background tasks for logging
        
    Returns:
        SimulateReviewResponse with predicted_rating, simulated_review, confidence, reasoning
        
    Raises:
        HTTPException: If agent fails or times out
    """
    start_time = time.time()
    status_code = 200
    error_msg = None
    
    try:
        # Call agent with timeout
        try:
            result = await asyncio.wait_for(
                run_task_a(req.user_persona, req.product),
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
            "predicted_rating",
            "simulated_review",
            "confidence",
            "reasoning",
        ]):
            status_code = 500
            error_msg = "Invalid agent response structure"
            raise HTTPException(
                status_code=500,
                detail="Agent returned invalid response structure",
            )
        
        # Build response
        response = SimulateReviewResponse(**result)
        
        # Log to database in background
        background_tasks.add_task(
            log_simulation,
            req.user_persona.get("user_id", "unknown"),
            req.product,
            result,
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
            "/api/v1/simulate-review",
            "POST",
            status_code,
            duration,
            error_msg,
        )
