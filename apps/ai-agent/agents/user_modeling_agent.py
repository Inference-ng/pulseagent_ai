import os
import re
import logging
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    import warnings
    warnings.warn("GOOGLE_API_KEY not set — Gemini calls will fail!", stacklevel=2)

from langgraph.graph import StateGraph, END
from prompts.task_a_prompt import TASK_A_HUMAN_PROMPT, TASK_A_BASE_PROMPT
from prompts.nigerian_context import get_context_for_persona
from utils.gemini_client import call_gemini  # ← shared client


class AgentState(TypedDict):
    user_persona: dict
    product: dict
    history_context: str
    review_result: dict
    errors: list


def retrieve(state: AgentState) -> AgentState:
    persona = state["user_persona"]
    history = persona.get("purchase_history", [])
    if persona.get("is_cold_start", False) or not history:
        state["history_context"] = "No past purchase history available."
    else:
        state["history_context"] = f"User has previously purchased: {', '.join(history)}."
    return state


def contextualize(state: AgentState) -> AgentState:
    persona = state["user_persona"]
    history_ctx = state.get("history_context", "")
    price_sens = persona.get("price_sensitivity", "medium")
    categories = ", ".join(persona.get("preferred_categories", []))
    context_str = (
        f"This user is a {price_sens}-price-sensitive shopper interested in {categories}. "
        f"{history_ctx}"
    )
    history_count = len(persona.get("purchase_history", []))
    if 0 < history_count < 3:
        context_str += (
            " Note: sparse purchase history (fewer than 3 items) — "
            "widen rating deviation, reduce confidence."
        )
    state["history_context"] = context_str
    return state


def generate(state: AgentState) -> AgentState:
    persona = state["user_persona"]
    product = state["product"]

    nigerian_ctx = get_context_for_persona(persona)
    system_prompt = TASK_A_BASE_PROMPT.format(nigerian_context=nigerian_ctx) + """

IMPORTANT: Respond ONLY with valid JSON — no markdown, no code fences, no extra text:
{
  "predicted_rating": <float between 1.0 and 5.0>,
  "simulated_review": "<3-5 sentence review string>",
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<brief explanation of rating and review choices>"
}"""

    # Sanitise user-controlled input before injecting into prompt
    context_query = str(product.get("description", "") or "")[:500]

    user_message = TASK_A_HUMAN_PROMPT.format(
        user_id=persona.get("user_id", "unknown"),
        avg_rating_given=persona.get("avg_rating_given", "N/A"),
        price_sensitivity=persona.get("price_sensitivity", "medium"),
        preferred_categories=", ".join(persona.get("preferred_categories", [])),
        is_cold_start=persona.get("is_cold_start", False),
        history_context=state.get("history_context", ""),
        product_name=product.get("name", ""),
        product_category=product.get("category", ""),
        product_price=product.get("price", 0),
        product_brand=product.get("brand", ""),
        product_description=context_query,
    )

    try:
        result = call_gemini(system_prompt, user_message, temperature=0.7)
        for key in ["predicted_rating", "simulated_review", "confidence", "reasoning"]:
            if key not in result:
                raise ValueError(f"Missing key in LLM response: {key}")
        state["review_result"] = result
        logger.info("[TaskA] Success — rating=%.1f confidence=%.2f",
                    result["predicted_rating"], result["confidence"])
    except Exception as e:
        logger.error("[TaskA] generate() failed: %s", e)
        state["errors"].append(str(e))
        state["review_result"] = {
            "predicted_rating": persona.get("avg_rating_given") or 3.0,
            "simulated_review": (
                "This product is okay sha. Abeg, I no go lie, e fit do the work but "
                "e get better options on Jumia. The price self no too bad but delivery "
                "fees don choke me."
            ),
            "confidence": 0.0,
            "reasoning": f"Fallback due to LLM error: {e}",
        }
    return state


def validate(state: AgentState) -> AgentState:
    res = state.get("review_result", {})
    rating = res.get("predicted_rating", 3.0)
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 3.0
    res["predicted_rating"] = max(1.0, min(5.0, rating))

    review = res.get("simulated_review", "")
    sentences = [s for s in re.split(r"[.!?]", review) if s.strip()]
    if len(sentences) < 2:
        res["simulated_review"] = review + " E good o. I go recommend am."

    state["review_result"] = res
    return state


workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("contextualize", contextualize)
workflow.add_node("generate", generate)
workflow.add_node("validate", validate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "contextualize")
workflow.add_edge("contextualize", "generate")
workflow.add_edge("generate", "validate")
workflow.add_edge("validate", END)

app = workflow.compile()


def simulate_review(user_persona: dict, product: dict) -> dict:
    initial_state: AgentState = {
        "user_persona": user_persona,
        "product": product,
        "history_context": "",
        "review_result": {},
        "errors": [],
    }
    final_state = app.invoke(initial_state)
    return final_state["review_result"]
