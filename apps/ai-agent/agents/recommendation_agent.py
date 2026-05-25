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
      Step 2: If still empty, fall back to domain-based popular real items.
      Step 3: Scores will be kept low (0.3–0.6) to reflect uncertainty.
    """
    persona = state["user_persona"]
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
                {"id": "fb_fashion_9",  "name": "Fila Disruptor II Platform Sneakers",     "brand": "Fila",        "price": 31000, "description": "Chunky platform sneaker with retro 90s flair. Thick sole for height boost."},
                {"id": "fb_fashion_10", "name": "Ankara Print Kimono Jacket",              "brand": "Local Craft", "price": 15000, "description": "Vibrant African print kimono jacket. Perfect for owambe, outings and casual looks."},
            ],
            "electronics": [
                {"id": "fb_elec_1",  "name": "Tecno Spark 20 Pro Smartphone",        "brand": "Tecno",    "price": 145000, "description": "6.78 inch FHD+ display, 256GB storage, 5000mAh battery. Top seller on Jumia Nigeria."},
                {"id": "fb_elec_2",  "name": "Oraimo FreePods 4 TWS Earbuds",        "brand": "Oraimo",   "price": 12500,  "description": "True wireless earbuds with 32hr total playback, ENC noise cancellation. Great value."},
                {"id": "fb_elec_3",  "name": "Xiaomi Redmi Note 13 Pro 4G",          "brand": "Xiaomi",   "price": 198000, "description": "200MP OIS camera, 120Hz AMOLED display, 5100mAh battery. Camera king at this price."},
                {"id": "fb_elec_4",  "name": "Hisense 43-inch FHD Smart TV",         "brand": "Hisense",  "price": 265000, "description": "Full HD Smart TV with Android OS, built-in Netflix and YouTube. Great for the living room."},
                {"id": "fb_elec_5",  "name": "Anker PowerCore 20000 Power Bank",     "brand": "Anker",    "price": 28000,  "description": "20,000mAh high-capacity power bank with 2 USB-A ports and USB-C. NEPA solution."},
                {"id": "fb_elec_6",  "name": "itel P55 Plus Smartphone",             "brand": "itel",     "price": 68000,  "description": "Budget-friendly with big 6000mAh battery and 6.6 inch screen. Great first phone choice."},
                {"id": "fb_elec_7",  "name": "Samsung Galaxy Buds FE",               "brand": "Samsung",  "price": 55000,  "description": "Active noise cancellation, 6hr playtime plus 21hr with case. Premium Samsung sound."},
                {"id": "fb_elec_8",  "name": "Syinix 32-inch HD Smart TV",           "brand": "Syinix",   "price": 115000, "description": "HD Smart TV with Android, built-in WiFi, HDMI and USB ports. Affordable quality."},
                {"id": "fb_elec_9",  "name": "Infinix Note 30 Pro",                 "brand": "Infinix",  "price": 185000, "description": "AMOLED display, 45W fast charging, 108MP main camera. Popular among Nigerian youth."},
                {"id": "fb_elec_10", "name": "Romoss Sense 8+ 30000mAh Power Bank", "brand": "Romoss",   "price": 22000,  "description": "Massive 30,000mAh capacity with PD fast charge. Survive any power outage in style."},
            ],
            "books": [
                {"id": "fb_book_1",  "name": "Atomic Habits by James Clear",                    "brand": "Avery",         "price": 8500, "description": "The number 1 self-improvement book worldwide. Build good habits, break bad ones. Must-read."},
                {"id": "fb_book_2",  "name": "Things Fall Apart by Chinua Achebe",              "brand": "Heinemann",     "price": 4500, "description": "African literary classic. Required reading and a timeless Nigerian story."},
                {"id": "fb_book_3",  "name": "Purple Hibiscus by Chimamanda Ngozi Adichie",     "brand": "Algonquin",     "price": 7000, "description": "Award-winning debut novel by Adichie. Deeply moving Nigerian coming-of-age story."},
                {"id": "fb_book_4",  "name": "The Psychology of Money by Morgan Housel",        "brand": "Harriman House", "price": 9500, "description": "19 timeless lessons on wealth, greed, and happiness. Essential finance read."},
                {"id": "fb_book_5",  "name": "Rich Dad Poor Dad by Robert Kiyosaki",            "brand": "Plata",         "price": 7500, "description": "The classic personal finance book that changes how you think about money."},
                {"id": "fb_book_6",  "name": "Half of a Yellow Sun by Chimamanda Ngozi Adichie","brand": "Knopf",         "price": 8000, "description": "Powerful novel set during the Nigeria-Biafra War. Emotionally gripping."},
                {"id": "fb_book_7",  "name": "Think and Grow Rich by Napoleon Hill",            "brand": "TarcherPerigee","price": 6500, "description": "Classic mindset and success book. Widely read by Nigerian entrepreneurs."},
                {"id": "fb_book_8",  "name": "The Alchemist by Paulo Coelho",                   "brand": "HarperOne",     "price": 7000, "description": "Inspirational fable about following your dreams. Beloved globally and in Nigeria."},
                {"id": "fb_book_9",  "name": "WAEC Past Questions and Answers (All Subjects)",  "brand": "Tonad",         "price": 3500, "description": "Comprehensive WAEC past questions with detailed solutions. Essential for SS3 students."},
                {"id": "fb_book_10", "name": "The 48 Laws of Power by Robert Greene",           "brand": "Penguin",       "price": 9000, "description": "48 laws distilled from history's most powerful figures. Widely read in Lagos boardrooms."},
            ],
            "food": [
                {"id": "fb_food_1",  "name": "Indomie Instant Noodles Chicken Flavour (40-pack)", "brand": "Indomie",    "price": 9500,  "description": "Nigeria's favourite instant noodle. Bulk pack for great savings."},
                {"id": "fb_food_2",  "name": "Golden Penny Semolina (5kg)",                       "brand": "Golden Penny","price": 6500,  "description": "Smooth semolina for eba, swallow or puddings. Consistently high quality."},
                {"id": "fb_food_3",  "name": "Dangote Sugar Refinery White Sugar (50kg)",          "brand": "Dangote",    "price": 68000, "description": "Bulk refined white sugar. Trusted Nigerian brand for households and businesses."},
                {"id": "fb_food_4",  "name": "Milo Chocolate Malt Drink (900g tin)",               "brand": "Nestle",     "price": 4800,  "description": "Chocolate energy drink beloved by Nigerian kids and adults. Classic breakfast staple."},
                {"id": "fb_food_5",  "name": "Peak Full Cream Milk Powder (900g)",                 "brand": "Peak",       "price": 5200,  "description": "Creamy full-fat milk powder. Nigerian household favourite for tea, pap and cooking."},
                {"id": "fb_food_6",  "name": "Titus Sardines in Tomato Sauce (125g x12)",          "brand": "Titus",      "price": 7200,  "description": "Tasty sardines perfect for bread, rice or noodles. Affordable protein source."},
                {"id": "fb_food_7",  "name": "Honeywell Semovita (5kg)",                           "brand": "Honeywell",  "price": 6800,  "description": "Semovita for smooth, stretchy swallow. Pairs perfectly with egusi or okra soup."},
                {"id": "fb_food_8",  "name": "Cadbury Bournvita Chocolate Drink (900g)",           "brand": "Cadbury",    "price": 4500,  "description": "Energy-boosting chocolate malt drink. Classic Nigerian school mornings in a tin."},
                {"id": "fb_food_9",  "name": "Sunola Vegetable Oil (5 litres)",                    "brand": "Sunola",     "price": 9800,  "description": "Light cooking oil ideal for frying, stewing and baking. Popular in Nigerian kitchens."},
                {"id": "fb_food_10", "name": "Knorr Chicken Seasoning Cubes (50-pack)",            "brand": "Knorr",      "price": 2500,  "description": "The go-to seasoning in every Nigerian kitchen. Makes everything taste like mama's cooking."},
            ],
            "beauty": [
                {"id": "fb_beauty_1",  "name": "Neutrogena Hydro Boost Water Gel Moisturiser",  "brand": "Neutrogena",  "price": 14500, "description": "Lightweight gel moisturiser with hyaluronic acid. Keeps skin hydrated in Lagos humidity."},
                {"id": "fb_beauty_2",  "name": "SheaMoisture African Black Soap Face Wash",     "brand": "SheaMoisture","price": 8500,  "description": "Natural black soap with shea butter. Great for acne-prone and melanin-rich skin."},
                {"id": "fb_beauty_3",  "name": "Maybelline Fit Me Matte and Poreless Foundation","brand": "Maybelline",  "price": 11000, "description": "Oil-free foundation with buildable coverage. Shades available for deeper Nigerian skin tones."},
                {"id": "fb_beauty_4",  "name": "Dark and Lovely Fade Resistant Rich Colour Kit", "brand": "Dark and Lovely","price": 5500,"description": "Long-lasting hair colour kit designed for natural African hair textures. Vibrant results."},
                {"id": "fb_beauty_5",  "name": "Nivea Nourishing Cocoa Body Lotion (400ml)",    "brand": "Nivea",       "price": 4800,  "description": "Rich cocoa lotion with a subtle glow finish. Deeply moisturises Nigerian skin."},
                {"id": "fb_beauty_6",  "name": "ORS Olive Oil Replenishing Conditioner",        "brand": "ORS",         "price": 7200,  "description": "Deep conditioning treatment for relaxed and natural hair. Restores moisture and shine."},
                {"id": "fb_beauty_7",  "name": "Black Opal True Color Skin Perfecting Stick",   "brand": "Black Opal",  "price": 9000,  "description": "Concealer stick made for deeper complexions. Covers blemishes and evens skin tone."},
                {"id": "fb_beauty_8",  "name": "Cantu Shea Butter Leave-In Conditioning Cream", "brand": "Cantu",       "price": 8800,  "description": "Leave-in conditioner with pure shea butter. Keeps 4C curls and coils moisturised."},
                {"id": "fb_beauty_9",  "name": "Revlon ColorStay Longwear Foundation SPF 15",   "brand": "Revlon",      "price": 12500, "description": "24-hour wear foundation that does not budge in heat or humidity. Great for events."},
                {"id": "fb_beauty_10", "name": "Palmer's Cocoa Butter Formula Body Lotion",     "brand": "Palmer's",    "price": 5500,  "description": "Classic cocoa butter lotion loved across Nigeria. Leaves skin soft and glowing."},
            ],
            "restaurants": [
                {"id": "fb_rest_1",  "name": "Chicken Republic Mighty Meal Deal",          "brand": "Chicken Republic", "price": 6500,  "description": "2 pieces chicken plus large chips plus drink. Nigeria's most popular fast food combo."},
                {"id": "fb_rest_2",  "name": "Kilimanjaro 2-Can-Dine Suya Platter",        "brand": "Kilimanjaro",     "price": 14000, "description": "Signature suya platter for two with dipping sauces and fresh pepper slices."},
                {"id": "fb_rest_3",  "name": "Domino's Pizza Nigerian Pepperoni Large",    "brand": "Domino's",        "price": 12500, "description": "Large pizza with generous pepperoni topping and extra cheese. Nigerian fan favourite."},
                {"id": "fb_rest_4",  "name": "Sweet Sensation Jollof Rice and Chicken",   "brand": "Sweet Sensation", "price": 5500,  "description": "Party-style jollof rice with grilled chicken. The ultimate Nigerian comfort meal."},
                {"id": "fb_rest_5",  "name": "Mr Biggs Meat Pie (6-pack)",                "brand": "Mr Biggs",        "price": 4200,  "description": "Iconic Nigerian meat pie with flaky pastry and savoury beef filling. Pure nostalgia."},
                {"id": "fb_rest_6",  "name": "Tantalizers Egusi Soup and Eba Set Meal",   "brand": "Tantalizers",     "price": 5800,  "description": "Authentic egusi soup with smooth eba and assorted meat. Real Naija food done right."},
                {"id": "fb_rest_7",  "name": "Yellow Chilli Pepper Soup with Catfish",    "brand": "The Yellow Chilli","price": 9500,  "description": "Spicy catfish pepper soup made to the original recipe. A Lagos favourite."},
                {"id": "fb_rest_8",  "name": "Cold Stone Creamery Signature Creation",    "brand": "Cold Stone",      "price": 4500,  "description": "Made-to-order ice cream with mix-ins. Premium treat across Lagos and Abuja outlets."},
                {"id": "fb_rest_9",  "name": "Ocean Basket Calamari and Fish and Chips",  "brand": "Ocean Basket",    "price": 16500, "description": "Crispy calamari with lemon aioli and generous fish and chips. Date-night approved."},
                {"id": "fb_rest_10", "name": "Nando's PERi-PERi Chicken Quarter Meal",   "brand": "Nando's",         "price": 8500,  "description": "Flame-grilled PERi-PERi chicken quarter with two sides. Medium heat is the sweet spot."},
            ],
        }

        fallback_products = DOMAIN_FALLBACK_PRODUCTS.get(domain)

        if fallback_products:
            fallback_items = [
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
        else:
            fallback_items = [
                {
                    "id": f"popular_{domain}_{i}",
                    "name": p["name"],
                    "category": domain.title(),
                    "price": p["price"],
                    "brand": p["brand"],
                    "description": p["description"],
                }
                for i, p in enumerate(DOMAIN_FALLBACK_PRODUCTS.get("fashion", [])[:10], 1)
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
            brand = c.get("brand", "")
            desc = c.get("description", "")
            if desc and len(desc) > 20:
                short_desc = desc.split(".")[0].strip()
                reason = f"{short_desc}. Recommended for your {state['domain']} interest."
            elif brand:
                reason = f"Top-rated {brand} product that fits your {state['domain']} preference. E go work for you!"
            else:
                reason = f"Highly rated {state['domain']} item that matches your shopping profile."
            items.append({
                "item_id": str(c.get("id", f"item_{i}")),
                "item_name": c.get("name", f"Product {i+1}"),
                "category": c.get("category", state["domain"].title()),
                "score": round(score, 2),
                "reason": reason,
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
