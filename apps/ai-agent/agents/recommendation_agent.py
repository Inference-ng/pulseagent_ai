import os
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END

# ── Singleton FAISS store ─────────────────────────────────────────────────────
# Loaded ONCE at module import time. Loading inside retrieve() on every call
# costs 15-25 seconds per request (SentenceTransformer model load) and causes
# the 60-second backend timeout to trigger.
from memory.faiss_store import FAISSStore as _FAISSStore
_FAISS_STORE = _FAISSStore()   # loaded once, reused on every request
# ─────────────────────────────────────────────────────────────────────────────


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
    store = _FAISS_STORE   # use the singleton — already loaded at startup
    persona = state["user_persona"]
    domain = state["domain"].strip().lower()
    query = state.get("context_query", "").strip()
    if not query:
        query = " ".join(persona.get("preferred_categories", [state["domain"]]))

    # Search broadly (top 50) then filter by domain category
    results = store.search(query, k=50)

    # Filter: keep only items whose category matches the requested domain
    # Filter: keep only items whose category matches the requested domain
    filtered = [
        r for r in results
        if r.get("category", "").strip().lower() == domain
        or domain in r.get("category", "").strip().lower()
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
        stars_info   = f", Stars: {c.get('stars', 'N/A')}"   if c.get("stars")        else ""
        reviews_info = f", Reviews: {c.get('review_count')}" if c.get("review_count") else ""
        candidates_str += (
            f"{i}. Name: {c.get('name', 'Unknown')}, "
            f"Category: {c.get('category', 'N/A')}, "
            f"Price: ₦{c.get('price', 0)}, "
            f"Brand: {c.get('brand', 'N/A')}"
            f"{stars_info}{reviews_info}\n"
        )

    confidence_note = "Since this is a cold-start user, assign confidence scores between 0.3 and 0.6." if is_cold_start else "Assign confidence scores between 0.6 and 0.95 based on persona fit."

    system_prompt = f"""You are a product recommendation engine for a Nigerian e-commerce platform.
Given a user persona and candidate products, select and rank the top {top_k} most relevant items.
{confidence_note}
Include one cross-domain suggestion if the user's history is domain-specific.
Consider the product's star rating and review count as quality signals when available.

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
    """
    Cross-domain injection — ONLY when context query explicitly
    suggests interest outside the selected domain.
    A fashion platform stays fashion. A books platform stays books.
    Cross-domain is opt-in via the user's own query, not forced.
    """
    persona  = state["user_persona"]
    domain   = state["domain"].lower()
    query    = state.get("context_query", "").lower()
    recs     = state["final_result"].get("recommendations", [])

    # Keywords that suggest the user wants something OUTSIDE their domain
    CROSS_SIGNALS = {
        "fashion":     ["book", "read", "novel", "learn", "food", "eat", "restaurant", "tech", "phone", "gadget"],
        "electronics": ["book", "read", "novel", "learn", "food", "eat", "restaurant", "wear", "cloth", "fashion"],
        "books":       ["wear", "cloth", "fashion", "shoe", "food", "eat", "restaurant", "phone", "gadget"],
        "food":        ["book", "read", "wear", "cloth", "fashion", "phone", "gadget", "electronics"],
        "beauty":      ["book", "read", "food", "eat", "phone", "gadget", "electronics"],
        "restaurants": ["book", "read", "wear", "cloth", "fashion", "phone", "gadget"],
    }

    signals = CROSS_SIGNALS.get(domain, [])
    user_wants_cross_domain = any(word in query for word in signals)

    # Only inject cross-domain if the query explicitly signals it
    if not user_wants_cross_domain:
        return state

    # Also require minimum recs and purchase history
    if len(recs) < 3 or persona.get("is_cold_start", False):
        return state

    CROSS_DOMAIN_ITEMS = {
        "Books & Education": {
            "item_id":   "cd_book_001",
            "item_name": "Atomic Habits by James Clear",
            "category":  "Books & Education",
            "score":     0.55,
            "reason":    "Based on your query, this self-improvement book is highly rated among Nigerian professionals. E go add value!",
        },
        "Electronics": {
            "item_id":   "cd_elec_001",
            "item_name": "Oraimo FreePods 4 TWS Earbuds",
            "category":  "Electronics",
            "score":     0.55,
            "reason":    "Top-rated affordable earbuds on Jumia Nigeria — great value, no be lie.",
        },
        "Food": {
            "item_id":   "cd_food_001",
            "item_name": "Suya Spot Signature Combo",
            "category":  "Food",
            "score":     0.55,
            "reason":    "Nigerians wey know say you can't go wrong with suya after shopping.",
        },
        "Fashion": {
            "item_id":   "cd_fashion_001",
            "item_name": "Premium Ankara Kaftan",
            "category":  "Fashion",
            "score":     0.55,
            "reason":    "A classic Nigerian wardrobe staple — perfect for owambe or any occasion.",
        },
        "Beauty": {
            "item_id":   "cd_beauty_001",
            "item_name": "SheaMoisture African Black Soap Bundle",
            "category":  "Beauty",
            "score":     0.55,
            "reason":    "Highly rated natural skincare on Jumia — great for Nigerian skin.",
        },
        "Restaurants": {
            "item_id":   "cd_rest_001",
            "item_name": "Chicken Republic Family Meal Deal",
            "category":  "Restaurants",
            "score":     0.55,
            "reason":    "After all that shopping, you deserve a treat. Chicken Republic dey everywhere!",
        },
    }

    current_domain = domain.title()
    other_domains  = [d for d in CROSS_DOMAIN_ITEMS if d.lower() != current_domain.lower()]

    import random
    chosen    = random.choice(other_domains) if other_domains else None
    if not chosen:
        return state

    cross_item = CROSS_DOMAIN_ITEMS[chosen]
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
