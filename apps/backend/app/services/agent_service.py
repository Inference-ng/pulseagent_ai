"""Agent Service — Bridge to Emmanuel's AI Agents (Phase 6)"""

import asyncio
import sys
from typing import Any, Dict
from concurrent.futures import ThreadPoolExecutor

# Add ai-agent module to path (docker: /ai-agent, local: ../ai-agent)
local_path = "../ai-agent"
docker_path = "/ai-agent"
sys.path.insert(0, local_path)
sys.path.insert(0, docker_path)


async def run_task_a(user_persona: Dict, product: Dict) -> Dict[str, Any]:
    """
    Task A: Simulate user review for a product.
    Wraps Emmanuel's synchronous agent to run in thread pool (async-safe).
    
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
        from agents.user_modeling_agent import simulate_review

        # Run sync agent in thread pool to avoid blocking async loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, simulate_review, user_persona, product
            )
        return result
        
    except ImportError as e:
        raise Exception(f"AI agent module not found: {e}")
    except Exception as e:
        raise Exception(f"Agent error in Task A: {str(e)}")


async def run_task_b(
    user_persona: Dict, top_k: int, domain: str
) -> Dict[str, Any]:
    """
    Task B: Get personalized product recommendations.
    Wraps Emmanuel's synchronous agent to run in thread pool (async-safe).
    
    Args:
        user_persona: User profile with user_id, purchase_history, price_sensitivity, etc.
        top_k: Number of recommendations (1-50)
        domain: Product domain (fashion, electronics, books, food)
        
    Returns:
        dict with keys:
            - recommendations (list of dicts with item_id, item_name, category, score, reason)
            - is_cold_start (bool, True if user has no history)
            - total (int, number of recommendations returned)
            
    Raises:
        Exception: If agent fails or module not found
    """
    try:
        from agents.recommendation_agent import get_recommendations

        # Run sync agent in thread pool to avoid blocking async loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, get_recommendations, user_persona, top_k, domain, ""
            )
        return result
        
    except ImportError as e:
        raise Exception(f"AI agent module not found: {e}")
    except Exception as e:
        raise Exception(f"Agent error in Task B: {str(e)}")
    except ImportError as e:
        raise Exception(f"AI agent module not found: {e}")
    except Exception as e:
        raise Exception(f"Agent error in Task B: {str(e)}")
