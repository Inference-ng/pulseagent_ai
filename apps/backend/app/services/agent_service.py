"""Agent Service — Bridge to Emmanuel's AI Agents (Phase 5)"""

import sys
from typing import Any, Dict

# Add ai-agent module to path (Docker volume mount at /ai-agent)
sys.path.insert(0, "/ai-agent")


async def run_task_a(user_persona: Dict, product: Dict) -> Dict[str, Any]:
    """
    Call Emmanuel's user modeling agent (Task A).
    
    Args:
        user_persona: User profile data
        product: Product details
        
    Returns:
        dict with predicted_rating, simulated_review, confidence, reasoning
    """
    try:
        from agents.user_modeling_agent import simulate_review

        result = await simulate_review(user_persona, product)
        return result
    except ImportError as e:
        raise Exception(f"AI agent module not found: {e}")
    except Exception as e:
        raise Exception(f"Agent error in Task A: {str(e)}")


async def run_task_b(
    user_persona: Dict, top_k: int, domain: str
) -> Dict[str, Any]:
    """
    Call Emmanuel's recommendation agent (Task B).
    
    Args:
        user_persona: User profile data
        top_k: Number of recommendations to return
        domain: Product domain (fashion, electronics, books, food)
        
    Returns:
        dict with recommendations list, is_cold_start, total
    """
    try:
        from agents.recommendation_agent import get_recommendations

        result = await get_recommendations(user_persona, top_k, domain)
        return result
    except ImportError as e:
        raise Exception(f"AI agent module not found: {e}")
    except Exception as e:
        raise Exception(f"Agent error in Task B: {str(e)}")
