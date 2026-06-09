"""Agent Service — Bridge to Emmanuel's AI Agents (Phase 6)"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Dict

# ---------------------------------------------------------------------------
# PATH SETUP — add the ai-agent package to sys.path so that
# `from agents.xxx import yyy` works at runtime.
# ---------------------------------------------------------------------------
_current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 3 levels:  services → app → backend → apps, then into ai-agent
_local_path = os.path.abspath(os.path.join(_current_dir, "../../../ai-agent"))
_docker_path = "/ai-agent"

if _local_path not in sys.path:
    sys.path.insert(0, _local_path)
if _docker_path not in sys.path:
    sys.path.insert(0, _docker_path)



async def run_task_a(user_persona: Dict, product: Dict) -> Dict[str, Any]:
    """
    Task A: Simulate user review for a product.
    Wraps Emmanuel's synchronous agent to run in a thread (async-safe).

    Args:
        user_persona: User profile with user_id, purchase_history, price_sensitivity, etc.
        product: Product details with name, category, price, brand, description

    Returns:
        dict with keys:
            - predicted_rating (float 1.0-5.0)
            - simulated_review (str, 3-5 sentences)
            - confidence (float 0.0-1.0)
            - reasoning (str, brief explanation)

    Raises:
        Exception: If agent fails or module not found
    """
    try:
        from agents.user_modeling_agent import simulate_review  # type: ignore[import]

        # Run sync agent in a separate thread to avoid blocking the async loop
        result = await asyncio.to_thread(simulate_review, user_persona, product)
        return result

    except ImportError as e:
        raise Exception(f"AI agent module not found: {e}")
    except Exception as e:
        raise Exception(f"Agent error in Task A: {str(e)}")


async def run_task_b(
    user_persona: Dict, top_k: int, domain: str, context_query: str = ""
) -> Dict[str, Any]:
    try:
        from agents.recommendation_agent import get_recommendations  # type: ignore[import]

        result = await asyncio.to_thread(
            get_recommendations, user_persona, top_k, domain, context_query
        )
        
        # Ensure result has required keys
        if not result or "recommendations" not in result:
            return {
                "recommendations": [],
                "is_cold_start": True,
                "total": 0
            }
        
        return result

    except ImportError as e:
        raise Exception(f"AI agent module not found: {e}")
    except Exception as e:
        raise Exception(f"Agent error in Task B: {str(e)}")