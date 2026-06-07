import os
import re
import json
import random
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

from langgraph.graph import StateGraph, END

# ── Singleton FAISS store ─────────────────────────────────────────────────────
from memory.faiss_store import FAISSStore as _FAISSStore
_FAISS_STORE = _FAISSStore()
# ─────────────────────────────────────────────────────────────────────────────


# ── LLM helper ───────────────────────────────────────────────────────────────

def _call_gemini(system_prompt: str, user_message: str) -> dict:
    import time
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Only free-tier flash models — Pro models have 0 quota on free plans
    models = ["gemini-2.5-flash"]
    max_retries = 3
    last_err = None

    for model_name in models:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.0,
                        response_mime_type="application/json",
                    ),
                )
                text = response.text.strip()
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
                return json.loads(text)
            except Exception as e:
                last_err = e
                err_str = str(e)
                # Retry on rate limit (429) with exponential backoff
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = (2 ** attempt) * 5  # 5s, 10s, 20s
                    time.sleep(wait)
                    continue
                # Non-rate-limit error — skip to next model
                break

    raise RuntimeError(f"All Gemini models failed: {last_err}")

# ── State ────────────────────────────────────────────────────────────────────

class RecoAgentState(TypedDict):
    user_persona: dict
    top_k: int
    domain: str
    context_query: str
    candidate_products: list
    final_result: dict
    errors: list


# ── Nodes ────────────────────────────────────────────────────────────────────

def retrieve(state: RecoAgentState) -> RecoAgentState:
    """FAISS semantic search — skipped for cold-start users who go straight to fallback."""
    persona = state["user_persona"]
    
    # Cold-start users get better results from curated fallback than sparse FAISS
    if persona.get("is_cold_start", False):
        state["candidate_products"] = []
        return state

    store = _FAISS_STORE
    domain = state["domain"].strip().lower()
    query = state.get("context_query", "").strip()
    if not query:
        query = " ".join(persona.get("preferred_categories", [state["domain"]]))

    # Inject domain keyword so TF-IDF scores domain-relevant items higher
    domain_query = f"{query} {domain}"
    results = store.search(domain_query, k=50)

    filtered = [
        r for r in results
        if r.get("category", "").strip().lower() == domain
        or domain in r.get("category", "").strip().lower()
    ]

    top_k = state.get("top_k", 5)
    if len(filtered) < top_k:
        filtered = results

    state["candidate_products"] = filtered[:20]
    return state

def cold_start_check(state: RecoAgentState) -> RecoAgentState:
    """Cold-start fallback with real Nigerian-relevant products by domain."""
    if not state["candidate_products"]:
        domain = state["domain"].strip().lower()

        DOMAIN_FALLBACK_PRODUCTS: dict = {
            "fashion": [
                {"id": "fb_fashion_1",  "name": "Nike Air Force 1 Low Sneakers",           "brand": "Nike",        "price": 45000, "description": "Classic low-top sneakers, all-white, unisex fit. Very popular on Jumia Nigeria."},
                {"id": "fb_fashion_2",  "name": "Adidas Originals Trefoil Hoodie",          "brand": "Adidas",      "price": 38000, "description": "Comfortable cotton hoodie with iconic trefoil logo. Available in multiple colours."},
                {"id": "fb_fashion_3",  "name": "H&M Slim-Fit Chino Trousers",             "brand": "H&M",         "price": 18500, "description": "Slim-fit cotton chinos, available in khaki, black and navy. Office or casual wear."},
                {"id": "fb_fashion_4",  "name": "Zara Oversized Linen Shirt",              "brand": "Zara",        "price": 22000, "description": "Lightweight linen shirt, perfect for Lagos heat. Relaxed oversized cut."},
                {"id": "fb_fashion_5",  "name": "Puma RS-X Sneakers",                      "brand": "Puma",        "price": 42000, "description": "Bold chunky-sole sneakers with retro running DNA. Cushioned for all-day comfort."},
                {"id": "fb_fashion_6",  "name": "New Balance 574 Core Sneakers",           "brand": "New Balance", "price": 39000, "description": "Heritage lifestyle sneaker with suede and mesh upper. Extremely comfortable."},
                {"id": "fb_fashion_7",  "name": "Reebok Classic Leather Sneakers",         "brand": "Reebok",      "price": 35000, "description": "Timeless leather sneaker that goes with everything. Cushioned insole for comfort."},
                {"id": "fb_fashion_8",  "name": "Converse Chuck Taylor All Star High-Top", "brand": "Converse",    "price": 28000, "description": "Iconic canvas high-top sneaker. Beloved staple for students and creatives alike."},
                {"id": "fb_fashion_9",  "name": "Ankara Print Kimono Jacket",              "brand": "Local Craft", "price": 15000, "description": "Vibrant African print kimono jacket. Perfect for owambe, outings and casual looks."},
                {"id": "fb_fashion_10", "name": "Premium Agbada Senator Set",              "brand": "Royal Threads","price": 35000, "description": "Premium Agbada for men. Perfect for weddings and formal Nigerian events."},
            ],
            "electronics": [
                {"id": "fb_elec_1",  "name": "Tecno Spark 20 Pro Smartphone",        "brand": "Tecno",    "price": 145000, "description": "6.78 inch FHD+ display, 256GB storage, 5000mAh battery. Top seller on Jumia Nigeria."},
                {"id": "fb_elec_2",  "name": "Oraimo FreePods 4 TWS Earbuds",        "brand": "Oraimo",   "price": 12500,  "description": "True wireless earbuds with 32hr total playback, ENC noise cancellation. Great value."},
                {"id": "fb_elec_3",  "name": "Xiaomi Redmi Note 13 Pro 4G",          "brand": "Xiaomi",   "price": 198000, "description": "200MP OIS camera, 120Hz AMOLED display, 5100mAh battery. Camera king at this price."},
                {"id": "fb_elec_4",  "name": "Hisense 43-inch FHD Smart TV",         "brand": "Hisense",  "price": 265000, "description": "Full HD Smart TV with Android OS, built-in Netflix and YouTube."},
                {"id": "fb_elec_5",  "name": "Anker PowerCore 20000 Power Bank",     "brand": "Anker",    "price": 28000,  "description": "20,000mAh high-capacity power bank. NEPA solution for Lagos."},
                {"id": "fb_elec_6",  "name": "itel P55 Plus Smartphone",             "brand": "itel",     "price": 68000,  "description": "Budget-friendly with big 6000mAh battery and 6.6 inch screen."},
                {"id": "fb_elec_7",  "name": "Samsung Galaxy Buds FE",               "brand": "Samsung",  "price": 55000,  "description": "Active noise cancellation, 6hr playtime plus 21hr with case."},
                {"id": "fb_elec_8",  "name": "Infinix Note 30 Pro",                  "brand": "Infinix",  "price": 185000, "description": "AMOLED display, 45W fast charging, 108MP main camera."},
                {"id": "fb_elec_9",  "name": "Romoss Sense 8+ 30000mAh Power Bank",  "brand": "Romoss",   "price": 22000,  "description": "Massive 30,000mAh capacity with PD fast charge."},
                {"id": "fb_elec_10", "name": "JBL Flip 6 Bluetooth Speaker",         "brand": "JBL",      "price": 62000,  "description": "Waterproof Bluetooth speaker with deep bass and 12hr battery."},
            ],
            "beauty": [
                {"id": "fb_beauty_1",  "name": "Neutrogena Hydro Boost Water Gel",      "brand": "Neutrogena",  "price": 14500, "description": "Lightweight gel moisturiser with hyaluronic acid. Keeps skin hydrated in Lagos humidity."},
                {"id": "fb_beauty_2",  "name": "SheaMoisture African Black Soap",       "brand": "SheaMoisture","price": 8500,  "description": "Natural black soap with shea butter. Great for acne-prone and melanin-rich skin."},
                {"id": "fb_beauty_3",  "name": "Maybelline Fit Me Foundation",           "brand": "Maybelline",  "price": 11000, "description": "Oil-free foundation with shades for deeper Nigerian skin tones."},
                {"id": "fb_beauty_4",  "name": "Nivea Nourishing Cocoa Body Lotion",    "brand": "Nivea",       "price": 4800,  "description": "Rich cocoa lotion with a subtle glow finish. Deeply moisturises Nigerian skin."},
                {"id": "fb_beauty_5",  "name": "Cantu Shea Butter Leave-In Cream",      "brand": "Cantu",       "price": 8800,  "description": "Leave-in conditioner with pure shea butter. Keeps 4C curls and coils moisturised."},
                {"id": "fb_beauty_6",  "name": "Palmer's Cocoa Butter Body Lotion",     "brand": "Palmer's",    "price": 5500,  "description": "Classic cocoa butter lotion loved across Nigeria. Leaves skin soft and glowing."},
                {"id": "fb_beauty_7",  "name": "ORS Olive Oil Replenishing Conditioner","brand": "ORS",         "price": 7200,  "description": "Deep conditioning treatment for relaxed and natural hair."},
                {"id": "fb_beauty_8",  "name": "Black Opal True Color Stick Foundation","brand": "Black Opal",  "price": 9000,  "description": "Concealer stick made for deeper complexions. Covers blemishes and evens skin tone."},
                {"id": "fb_beauty_9",  "name": "Revlon ColorStay Foundation SPF 15",    "brand": "Revlon",      "price": 12500, "description": "24-hour wear foundation that does not budge in heat or humidity."},
                {"id": "fb_beauty_10", "name": "Dark and Lovely Rich Colour Kit",       "brand": "Dark and Lovely","price": 5500,"description": "Long-lasting hair colour kit designed for natural African hair textures."},
            ],
            "books": [
                {"id": "fb_book_1",  "name": "Atomic Habits by James Clear",                     "brand": "Avery",         "price": 8500, "description": "The number 1 self-improvement book worldwide."},
                {"id": "fb_book_2",  "name": "Things Fall Apart by Chinua Achebe",               "brand": "Heinemann",     "price": 4500, "description": "African literary classic. Required reading and a timeless Nigerian story."},
                {"id": "fb_book_3",  "name": "Purple Hibiscus by Chimamanda Ngozi Adichie",      "brand": "Algonquin",     "price": 7000, "description": "Award-winning debut novel by Adichie. Deeply moving Nigerian coming-of-age story."},
                {"id": "fb_book_4",  "name": "The Psychology of Money by Morgan Housel",         "brand": "Harriman House","price": 9500, "description": "19 timeless lessons on wealth, greed, and happiness."},
                {"id": "fb_book_5",  "name": "Rich Dad Poor Dad by Robert Kiyosaki",             "brand": "Plata",         "price": 7500, "description": "The classic personal finance book."},
                {"id": "fb_book_6",  "name": "Half of a Yellow Sun by Chimamanda Ngozi Adichie", "brand": "Knopf",         "price": 8000, "description": "Powerful novel set during the Nigeria-Biafra War."},
                {"id": "fb_book_7",  "name": "The 48 Laws of Power by Robert Greene",            "brand": "Penguin",       "price": 9000, "description": "48 laws distilled from history's most powerful figures."},
                {"id": "fb_book_8",  "name": "Think and Grow Rich by Napoleon Hill",             "brand": "TarcherPerigee","price": 6500, "description": "Classic mindset and success book. Widely read by Nigerian entrepreneurs."},
                {"id": "fb_book_9",  "name": "WAEC Past Questions and Answers (All Subjects)",   "brand": "Tonad",         "price": 3500, "description": "Comprehensive WAEC past questions. Essential for SS3 students."},
                {"id": "fb_book_10", "name": "The Alchemist by Paulo Coelho",                    "brand": "HarperOne",     "price": 7000, "description": "Inspirational fable about following your dreams."},
            ],
            "food": [
                {"id": "fb_food_1",  "name": "Indomie Instant Noodles Chicken Flavour (40-pack)", "brand": "Indomie",    "price": 9500,  "description": "Nigeria's favourite instant noodle. Bulk pack for great savings."},
                {"id": "fb_food_2",  "name": "Golden Penny Semolina (5kg)",                        "brand": "Golden Penny","price": 6500, "description": "Smooth semolina for eba or puddings."},
                {"id": "fb_food_3",  "name": "Milo Chocolate Malt Drink (900g tin)",               "brand": "Nestle",     "price": 4800, "description": "Classic Nigerian breakfast staple."},
                {"id": "fb_food_4",  "name": "Peak Full Cream Milk Powder (900g)",                 "brand": "Peak",       "price": 5200, "description": "Nigerian household favourite for tea and cooking."},
                {"id": "fb_food_5",  "name": "Knorr Chicken Seasoning Cubes (50-pack)",            "brand": "Knorr",      "price": 2500, "description": "The go-to seasoning in every Nigerian kitchen."},
                {"id": "fb_food_6",  "name": "Dangote Sugar Refinery White Sugar (5kg)",           "brand": "Dangote",    "price": 8500, "description": "Trusted Nigerian brand refined white sugar."},
                {"id": "fb_food_7",  "name": "Honeywell Semovita (5kg)",                           "brand": "Honeywell",  "price": 6800, "description": "Semovita for smooth, stretchy swallow."},
                {"id": "fb_food_8",  "name": "Cadbury Bournvita Chocolate Drink (900g)",           "brand": "Cadbury",    "price": 4500, "description": "Energy-boosting chocolate malt drink."},
                {"id": "fb_food_9",  "name": "Sunola Vegetable Oil (5 litres)",                    "brand": "Sunola",     "price": 9800, "description": "Light cooking oil ideal for frying and stewing."},
                {"id": "fb_food_10", "name": "Titus Sardines in Tomato Sauce (125g x12)",          "brand": "Titus",      "price": 7200, "description": "Tasty sardines — affordable protein source."},
            ],
            "restaurants": [
                {"id": "fb_rest_1",  "name": "Chicken Republic Mighty Meal Deal",         "brand": "Chicken Republic",  "price": 6500,  "description": "Nigeria's most popular fast food combo."},
                {"id": "fb_rest_2",  "name": "Kilimanjaro Suya Platter for Two",          "brand": "Kilimanjaro",       "price": 14000, "description": "Signature suya platter with dipping sauces."},
                {"id": "fb_rest_3",  "name": "Sweet Sensation Jollof Rice and Chicken",  "brand": "Sweet Sensation",   "price": 5500,  "description": "Party-style jollof rice with grilled chicken."},
                {"id": "fb_rest_4",  "name": "Mr Biggs Meat Pie (6-pack)",               "brand": "Mr Biggs",          "price": 4200,  "description": "Iconic Nigerian meat pie with flaky pastry."},
                {"id": "fb_rest_5",  "name": "Tantalizers Egusi Soup and Eba Set Meal",  "brand": "Tantalizers",       "price": 5800,  "description": "Authentic egusi soup with smooth eba."},
                {"id": "fb_rest_6",  "name": "Yellow Chilli Pepper Soup with Catfish",   "brand": "The Yellow Chilli", "price": 9500,  "description": "Spicy catfish pepper soup — a Lagos favourite."},
                {"id": "fb_rest_7",  "name": "Nando's PERi-PERi Chicken Quarter Meal",  "brand": "Nando's",           "price": 8500,  "description": "Flame-grilled PERi-PERi chicken quarter with two sides."},
                {"id": "fb_rest_8",  "name": "Cold Stone Creamery Signature Creation",  "brand": "Cold Stone",        "price": 4500,  "description": "Made-to-order ice cream with mix-ins. Premium treat."},
                {"id": "fb_rest_9",  "name": "Domino's Pizza Nigerian Pepperoni Large",  "brand": "Domino's",          "price": 12500, "description": "Large pizza with generous pepperoni and extra cheese."},
                {"id": "fb_rest_10", "name": "Ocean Basket Fish and Chips",              "brand": "Ocean Basket",      "price": 16500, "description": "Crispy calamari with fish and chips. Date-night approved."},
            ],
        }

        fallback_products = DOMAIN_FALLBACK_PRODUCTS.get(domain, DOMAIN_FALLBACK_PRODUCTS["fashion"])
        state["candidate_products"] = [
            {
                "id": p["id"],
                "name": p["name"],
                "category": domain.title(),
                "price": p["price"],
                "brand": p["brand"],
                "description": p["description"],
            }
            for p in fallback_products
        ]
    return state


def rank(state: RecoAgentState) -> RecoAgentState:
    """LLM re-ranks the top-20 candidates to top-K with per-item Nigerian-voice reasoning."""
    persona = state["user_persona"]
    candidates = state["candidate_products"]
    top_k = state["top_k"]
    is_cold_start = persona.get("is_cold_start", False)

    if not candidates:
        state["final_result"] = {"recommendations": [], "is_cold_start": is_cold_start, "total": 0}
        return state

    from prompts.nigerian_context import get_context_for_persona
    nigerian_ctx = get_context_for_persona(persona)

    candidates_str = ""
    for i, c in enumerate(candidates[:20], 1):
        stars_info   = f", Stars: {c.get('stars', 'N/A')}"   if c.get("stars")        else ""
        reviews_info = f", Reviews: {c.get('review_count')}" if c.get("review_count") else ""
        candidates_str += (
            f"{i}. Name: {c.get('name', 'Unknown')}, "
            f"Category: {c.get('category', 'N/A')}, "
            f"Price: \u20a6{c.get('price', 0)}, "
            f"Brand: {c.get('brand', 'N/A')}"
            f"{stars_info}{reviews_info}\n"
        )

    confidence_note = (
        "Since this is a cold-start user, assign confidence scores between 0.3 and 0.6."
        if is_cold_start
        else "Assign confidence scores between 0.6 and 0.95 based on persona fit."
    )

    system_prompt = f"""{nigerian_ctx}

You are a product recommendation engine for a Nigerian e-commerce platform.
Given a user persona and candidate products, select and rank the top {top_k} most relevant items.
{confidence_note}
Include one cross-domain suggestion if the user's history is domain-specific.
Write each recommendation reason in authentic Nigerian voice — warm, direct, real.

IMPORTANT: Respond ONLY with valid JSON — no markdown, no code fences:
{{
  "recommendations": [
    {{
      "item_id": "<string>",
      "item_name": "<string>",
      "category": "<string>",
      "score": <float 0.0-1.0>,
      "reason": "<one sentence reason in Nigerian voice>"
    }}
  ],
  "is_cold_start": <true|false>,
  "total": <int>
}}"""

    user_message = f"""User Persona:
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

Return the top {top_k} ranked recommendations as JSON."""

    try:
        result = _call_gemini(system_prompt, user_message)
        if "recommendations" not in result:
            raise ValueError("Missing 'recommendations' key in LLM response")
        result["is_cold_start"] = is_cold_start
        result["total"] = len(result["recommendations"])
        state["final_result"] = result
    except Exception as e:
        state["errors"].append(str(e))
        score_base = 0.4 if is_cold_start else 0.7
        items = []
        for i, c in enumerate(candidates[:top_k]):
            score = max(0.3, score_base - i * 0.03)
            desc = c.get("description", "")
            brand = c.get("brand", "")
            reason = (
                f"{desc.split('.')[0].strip()}. Recommended for your {state['domain']} interest."
                if desc and len(desc) > 20
                else f"Top-rated {brand} product for your {state['domain']} preference. E go work for you!"
            )
            items.append({
                "item_id": str(c.get("id", f"item_{i}")),
                "item_name": c.get("name", f"Product {i+1}"),
                "category": c.get("category", state["domain"].title()),
                "score": round(score, 2),
                "reason": reason,
            })
        state["final_result"] = {"recommendations": items, "is_cold_start": is_cold_start, "total": len(items)}
    return state


def cross_domain(state: RecoAgentState) -> RecoAgentState:
    """Inject one cross-domain item only when the query explicitly signals interest outside the domain."""
    persona = state["user_persona"]
    domain  = state["domain"].lower()
    query   = state.get("context_query", "").lower()
    recs    = state["final_result"].get("recommendations", [])

    CROSS_SIGNALS = {
        "fashion":     ["book", "read", "novel", "food", "eat", "restaurant", "phone", "gadget", "tech"],
        "electronics": ["book", "read", "novel", "food", "eat", "restaurant", "wear", "cloth", "fashion"],
        "books":       ["wear", "cloth", "fashion", "shoe", "food", "eat", "phone", "gadget"],
        "food":        ["book", "read", "wear", "cloth", "fashion", "phone", "gadget"],
        "beauty":      ["book", "read", "food", "eat", "phone", "gadget"],
        "restaurants": ["book", "read", "wear", "cloth", "fashion", "phone", "gadget"],
    }

    if not any(w in query for w in CROSS_SIGNALS.get(domain, [])):
        return state
    if len(recs) < 3 or persona.get("is_cold_start", False):
        return state

    CROSS_DOMAIN_ITEMS = {
        "Books & Education": {"item_id": "cd_book_001", "item_name": "Atomic Habits by James Clear",       "category": "Books & Education", "score": 0.55, "reason": "This self-improvement book is highly rated among Nigerian professionals. E go add value!"},
        "Electronics":       {"item_id": "cd_elec_001", "item_name": "Oraimo FreePods 4 TWS Earbuds",      "category": "Electronics",       "score": 0.55, "reason": "Top-rated affordable earbuds on Jumia Nigeria — great value, no be lie."},
        "Food":              {"item_id": "cd_food_001", "item_name": "Knorr Chicken Cubes 50-pack",         "category": "Food",              "score": 0.55, "reason": "Every Nigerian kitchen needs Knorr. Add am to your order, abeg."},
        "Fashion":           {"item_id": "cd_fashion_001","item_name": "Premium Ankara Kaftan",             "category": "Fashion",           "score": 0.55, "reason": "A classic Nigerian wardrobe staple — perfect for owambe or any occasion."},
        "Beauty":            {"item_id": "cd_beauty_001","item_name": "SheaMoisture African Black Soap Bundle","category": "Beauty",         "score": 0.55, "reason": "Highly rated natural skincare — great for Nigerian skin in this Lagos heat."},
        "Restaurants":       {"item_id": "cd_rest_001", "item_name": "Chicken Republic Mighty Meal Deal",   "category": "Restaurants",      "score": 0.55, "reason": "After all that shopping, you deserve a treat. Chicken Republic dey everywhere!"},
    }

    other_domains = [d for d in CROSS_DOMAIN_ITEMS if d.lower() != domain]
    chosen = random.choice(other_domains) if other_domains else None
    if chosen:
        recs.append(CROSS_DOMAIN_ITEMS[chosen])
        state["final_result"]["recommendations"] = recs
        state["final_result"]["total"] = len(recs)
    return state


# ── Graph ────────────────────────────────────────────────────────────────────

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


def get_recommendations(
    user_persona: dict, top_k: int = 10, domain: str = "fashion", context_query: str = ""
) -> dict:
    """
    Task B entry point.
    Returns dict with keys: recommendations (list), is_cold_start (bool), total (int)
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
