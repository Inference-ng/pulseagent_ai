import os
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
# NOTE: FAISSStore is imported lazily inside retrieve() to prevent a Windows
# segfault caused by PyTorch + FAISS native DLLs loading at the same time.


class RecoAgentState(TypedDict):
    user_persona: dict
    top_k: int
    domain: str
    context_query: str
    candidate_products: list
    final_result: dict
    errors: list


def retrieve(state: RecoAgentState) -> RecoAgentState:
    """FAISS semantic search using user preferences + context query, filtered by domain."""
    from memory.faiss_store import FAISSStore   # lazy import — avoids Windows segfault
    store = FAISSStore()
    persona = state["user_persona"]
    domain = state["domain"].strip().lower()
    query = state.get("context_query", "").strip()
    if not query:
        query = " ".join(persona.get("preferred_categories", [state["domain"]]))

    # Search broadly (top 30) then filter by domain category
    results = store.search(query, k=30)

    # Filter: keep only items whose category matches the requested domain
    filtered = [
        r for r in results
        if r.get("category", "").strip().lower() == domain
    ]

    # Relax filter if too few results — fall back to broader semantic matches
    top_k = state.get("top_k", 5)
    if len(filtered) < top_k:
        filtered = results  # use unfiltered if not enough domain-specific items

    state["candidate_products"] = filtered[:20]
    return state



def cold_start_check(state: RecoAgentState) -> RecoAgentState:
    """
    Cold-start strategy (3-step):
      Step 1: Context semantic search already done in retrieve().
      Step 2: If still empty, fall back to domain-based popular placeholder items.
      Step 3: Scores will be kept low (0.3–0.6) to reflect uncertainty.
    """
    persona = state["user_persona"]
    if not state["candidate_products"]:
        # Synthetic popular fallback items for the requested domain
        domain = state["domain"]
        fallback_items = [
            {
                "id": f"popular_{domain}_{i}",
                "name": f"Top {domain.title()} Item #{i}",
                "category": domain.title(),
                "price": 15000 + (i * 2000),
                "brand": brand,
                "description": f"Popular {domain} item on Jumia Nigeria.",
            }
            for i, brand in enumerate(
                ["Nike", "Adidas", "Puma", "H&M", "Zara", "Reebok", "New Balance", "Fila", "Converse", "Vans"], 1
            )
        ]
        state["candidate_products"] = fallback_items
    return state


def rank(state: RecoAgentState) -> RecoAgentState:
    """LLM re-ranks the top-20 FAISS results to top-K with per-item reasoning."""
    persona = state["user_persona"]
    candidates = state["candidate_products"]
    top_k = state["top_k"]
    is_cold_start = persona.get("is_cold_start", False)

    if not candidates:
        state["final_result"] = {
            "recommendations": [],
            "is_cold_start": is_cold_start,
            "total": 0,
        }
        return state

    # Format candidates for LLM
    candidates_str = ""
    for i, c in enumerate(candidates[:20], 1):
        candidates_str += (
            f"{i}. Name: {c.get('name', 'Unknown')}, "
            f"Category: {c.get('category', 'N/A')}, "
            f"Price: ₦{c.get('price', 0)}, "
            f"Brand: {c.get('brand', 'N/A')}\n"
        )

    confidence_note = "Since this is a cold-start user, assign confidence scores between 0.3 and 0.6." if is_cold_start else "Assign confidence scores between 0.6 and 0.95 based on persona fit."

    system_prompt = f"""You are a product recommendation engine for a Nigerian e-commerce platform.
Given a user persona and candidate products, select and rank the top {top_k} most relevant items.
{confidence_note}
Include one cross-domain suggestion if the user's history is domain-specific.

IMPORTANT: Respond ONLY with valid JSON — no markdown, no code fences:
{{
  "recommendations": [
    {{
      "item_id": "<string>",
      "item_name": "<string>",
      "category": "<string>",
      "score": <float 0.0-1.0>,
      "reason": "<one sentence reason>"
    }}
  ],
  "is_cold_start": <true|false>,
  "total": <int>
}}
"""

    human_prompt = f"""User Persona:
- User ID: {persona.get('user_id', 'unknown')}
- Price Sensitivity: {persona.get('price_sensitivity', 'medium')}
- Preferred Categories: {', '.join(persona.get('preferred_categories', []))}
- Purchase History: {', '.join(persona.get('purchase_history', [])) or 'None'}
- Is Cold Start: {is_cold_start}

Context Query: "{state.get('context_query', '')}"
Domain: {state['domain']}
Top-K requested: {top_k}

Candidate Products:
{candidates_str}

Return the top {top_k} ranked recommendations as JSON.
"""

    from langchain_core.messages import SystemMessage, HumanMessage

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,
        google_api_key=GOOGLE_API_KEY,
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]

    chain = llm | JsonOutputParser()

    try:
        result = chain.invoke(messages)
        # Ensure required keys exist
        if "recommendations" not in result:
            raise ValueError("Missing 'recommendations' key in LLM response")
        result["is_cold_start"] = is_cold_start
        result["total"] = len(result["recommendations"])
        state["final_result"] = result
    except Exception as e:
        state["errors"].append(str(e))
        # Fallback: build recommendations from candidates directly
        items = []
        score_base = 0.4 if is_cold_start else 0.7
        for i, c in enumerate(candidates[:top_k]):
            score = max(0.3, score_base - i * 0.03)
            items.append({
                "item_id": str(c.get("id", f"item_{i}")),
                "item_name": c.get("name", f"Product {i+1}"),
                "category": c.get("category", state["domain"].title()),
                "score": round(score, 2),
                "reason": f"Matches your interest in {state['domain']}. E go work for you!",
            })
        state["final_result"] = {
            "recommendations": items,
            "is_cold_start": is_cold_start,
            "total": len(items),
        }
    return state


def cross_domain(state: RecoAgentState) -> RecoAgentState:
    """If user history is in one domain, inject one cross-domain suggestion."""
    persona = state["user_persona"]
    history = persona.get("purchase_history", [])
    recs = state["final_result"].get("recommendations", [])

    # Only inject if there are at least 3 recs and history is non-empty
    if history and len(recs) >= 3:
        existing_categories = {r.get("category", "").lower() for r in recs}
        if len(existing_categories) == 1:
            import random
            domains = ["Books & Education", "Electronics", "Food", "Fashion", "Beauty"]
            current_domain = state["domain"].title()
            other_domains = [d for d in domains if d != current_domain]
            cross_domain = random.choice(other_domains) if other_domains else "Books & Education"

            # Inject a cross-domain item
            cross_item = {
                "item_id": f"cross_domain_pick",
                "item_name": f"Surprise {cross_domain} Pick",
                "category": cross_domain,
                "score": 0.55,
                "reason": f"Based on your shopping pattern, you might also like to explore {cross_domain.lower()}. No be small thing, variety na the spice of life!",
            }
            recs.append(cross_item)
            state["final_result"]["recommendations"] = recs
            state["final_result"]["total"] = len(recs)

    return state


# Build LangGraph workflow
workflow = StateGraph(RecoAgentState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("cold_start_check", cold_start_check)
workflow.add_node("rank", rank)
workflow.add_node("cross_domain", cross_domain)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "cold_start_check")
workflow.add_edge("cold_start_check", "rank")
workflow.add_edge("rank", "cross_domain")
workflow.add_edge("cross_domain", END)

app = workflow.compile()


def get_recommendations(user_persona: dict, top_k: int = 10, domain: str = "fashion", context_query: str = "") -> dict:
    """
    Task B entry point.
    Returns: dict with keys recommendations (list), is_cold_start (bool), total (int)
    """
    initial_state: RecoAgentState = {
        "user_persona": user_persona,
        "top_k": top_k,
        "domain": domain,
        "context_query": context_query,
        "candidate_products": [],
        "final_result": {},
        "errors": [],
    }
    final_state = app.invoke(initial_state)
    return final_state["final_result"]
