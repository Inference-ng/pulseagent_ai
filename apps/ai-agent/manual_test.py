"""
manual_test.py — Elebiemayo Iseoluwa Emmanuel

Run this file to manually test the AI Agent module and see the LLM's outputs in action!
Command: python apps/ai-agent/manual_test.py   (from repo root)
         OR: python manual_test.py              (from apps/ai-agent/)
"""
# ── Windows Terminal Fix (must be FIRST — before any other import) ────────────
import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"   # no Unicode progress bars
os.environ["TRANSFORMERS_VERBOSITY"] = "error"       # silence transformer logs
os.environ["TOKENIZERS_PARALLELISM"] = "false"       # silence tokenizer warnings
# ─────────────────────────────────────────────────────────────────────────────

import sys
import time

# Ensure the ai-agent directory is always on the path,
# regardless of where this script is invoked from.
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(_this_dir, ".env"))

# NOTE: agents are imported lazily inside each test function.
# This avoids a Windows segfault caused by PyTorch + FAISS native DLLs
# loading at the same time when both modules are imported at startup.

# ── Pre-warm FAISS native DLLs BEFORE any LangChain/Gemini imports ────────────
# On Windows, FAISS and sentence-transformers must load their native C++ DLLs
# FIRST. If langchain_google_genai loads first it pulls in conflicting MKL libs,
# causing a fatal 0xC0000005 Access Violation when FAISS loads later.
from memory.faiss_store import FAISSStore as _PreWarmFAISS
_prewarmed_store = _PreWarmFAISS()   # loads DLLs into memory now
del _PreWarmFAISS                     # clean up the class ref (store stays warm)
# ─────────────────────────────────────────────────────────────────────────────


def safe_print(text):
    """Print text safely on Windows cp1252 terminals — replaces unencodable chars."""
    print(text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))

def test_task_a():
    from agents.user_modeling_agent import simulate_review

    print("\n" + "="*50)
    print("TESTING TASK A: USER MODELING (SIMULATED REVIEW)")
    print("="*50)

    # 1. Define a sample Nigerian User Persona
    user_persona = {
        "user_id": "U12345",
        "purchase_history": ["Infinix Hot 10", "Oraimo Powerbank"],
        "avg_rating_given": 4.2,
        "price_sensitivity": "high",
        "preferred_categories": ["Electronics", "Gadgets"],
        "is_cold_start": False
    }

    # 2. Define a product to review
    product = {
        "name": "JBL Flip 6 Waterproof Speaker",
        "category": "Electronics",
        "price": 62000,
        "brand": "JBL",
        "description": "Portable Bluetooth speaker with deep bass and waterproof design."
    }

    print(f"User: Budget-conscious buyer who likes Electronics.")
    print(f"Product: {product['name']} (N{product['price']})")
    print("Generating review via Gemini...\n")

    start_time = time.time()
    result = simulate_review(user_persona, product)
    elapsed = time.time() - start_time

    print(f"[DONE] Generated in {elapsed:.2f} seconds!")
    print(f"[RATING]  Predicted Rating: {result.get('predicted_rating')}/5.0")
    safe_print(f"[REVIEW]  Simulated Review:\n  \"{result.get('simulated_review')}\"")
    safe_print(f"[REASON]  AI Reasoning:\n  {result.get('reasoning')}")


def test_task_b():
    from agents.recommendation_agent import get_recommendations

    print("\n" + "="*50)
    print("TESTING TASK B: RECOMMENDATION ENGINE (COLD-START)")
    print("="*50)

    # 1. Define a brand new user (Cold-Start)
    cold_start_persona = {
        "user_id": "NEW_USER_999",
        "purchase_history": [],
        "price_sensitivity": "medium",
        "preferred_categories": ["Fashion"],
        "is_cold_start": True
    }

    context_query = "I want a nice shoe for an owambe party this weekend."
    domain = "Fashion"

    print(f"User: Brand new user (Cold-Start)")
    print(f"Query: \"{context_query}\"")
    print("Fetching FAISS context & ranking via Gemini...\n")

    start_time = time.time()
    result = get_recommendations(cold_start_persona, top_k=3, domain=domain, context_query=context_query)
    elapsed = time.time() - start_time

    print(f"[DONE] Generated in {elapsed:.2f} seconds!")
    print(f"[COLD START] Is Cold Start: {result.get('is_cold_start')}")

    print("\n[TOP RECOMMENDATIONS]")
    for i, rec in enumerate(result.get('recommendations', [])):
        name = rec.get('item_name') or rec.get('name', f'Item {i+1}')
        safe_print(f"  {i+1}. {name} (Score: {rec.get('score', 'N/A')})")
        safe_print(f"     Reason: {rec.get('reason', 'N/A')}")


if __name__ == "__main__":
    test_task_a()
    time.sleep(2)  # brief pause between API calls
    test_task_b()
    print("\n" + "="*50)
    print("ALL MANUAL TESTS COMPLETED SUCCESSFULLY!")
    print("="*50 + "\n")
