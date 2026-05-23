"""
verify.py — Elebiemayo Iseoluwa Emmanuel
Run this to confirm all Task A & Task B modules are working before testing.

Usage (from apps/ai-agent/ directory):
    python verify.py

Usage (from repo root):
    python apps/ai-agent/verify.py
"""
import sys
import os
import logging

# ── Path setup ──────────────────────────────────────────────────────────────
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

# Silence noisy library loggers so output stays clean on Windows terminals
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
# ─────────────────────────────────────────────────────────────────────────────

from dotenv import load_dotenv
load_dotenv(os.path.join(_this_dir, ".env"))

PASS = "[PASS]"
FAIL = "[FAIL]"
results = []

def check(label, fn):
    try:
        fn()
        print(f"  {PASS} {label}")
        results.append(True)
    except Exception as e:
        print(f"  {FAIL} {label}")
        print(f"         -> {e}")
        results.append(False)

print("")
print("=" * 60)
print("  PurseAgent AI - Elebiemayo Emmanuel's Task Audit")
print("=" * 60)

# ── 1. Core Libraries ────────────────────────────────────────────────────────
print("\n[1/5] Core library imports")
check("langchain_google_genai",    lambda: __import__("langchain_google_genai"))
check("langgraph",                 lambda: __import__("langgraph"))
check("faiss",                     lambda: __import__("faiss"))
check("python-dotenv",             lambda: __import__("dotenv"))
check("pandas",                    lambda: __import__("pandas"))

# ── 2. Prompt / Schema modules ───────────────────────────────────────────────
print("\n[2/5] Prompt & Schema modules")
check("schemas.models",            lambda: __import__("schemas.models"))
check("prompts.nigerian_context",  lambda: __import__("prompts.nigerian_context"))
check("prompts.task_a_prompt",     lambda: __import__("prompts.task_a_prompt"))
check("prompts.task_b_prompt",     lambda: __import__("prompts.task_b_prompt"))

# ── 3. Memory / FAISS ────────────────────────────────────────────────────────
print("\n[3/5] Memory (FAISS store)")

def _check_faiss():
    from memory.faiss_store import FAISSStore
    store = FAISSStore()
    assert store.index is not None, "FAISS index is None"
    if store.index.ntotal == 0:
        raise AssertionError(
            "FAISS index is empty (0 items).\n"
            "         Fix: run  python data/scripts/loader.py  then  python data/scripts/embed.py"
        )
    hits = store.search("sneakers for owambe", k=3)
    print(f"         -> {store.index.ntotal} items in index | search returned {len(hits)} hit(s)")
    if hits:
        print(f"         -> Top hit: {hits[0].get('name')} [{hits[0].get('category')}]")

check("sentence_transformers",     lambda: __import__("sentence_transformers"))
check("memory.faiss_store (init + search)", _check_faiss)

# ── 4. Agent imports ─────────────────────────────────────────────────────────
print("\n[4/5] Agent module imports")
check("agents.user_modeling_agent",    lambda: __import__("agents.user_modeling_agent"))
check("agents.recommendation_agent",   lambda: __import__("agents.recommendation_agent"))

# ── 5. API Key ───────────────────────────────────────────────────────────────
print("\n[5/5] GOOGLE_API_KEY")

def _check_key():
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key or key == "your_gemini_api_key_here":
        raise ValueError(
            "GOOGLE_API_KEY is not set.\n"
            "         Fix: open apps/ai-agent/.env and replace the placeholder with your real key.\n"
            "         Free key: https://aistudio.google.com/app/apikey"
        )
    masked = key[:8] + "..." + key[-4:]
    print(f"         -> Key found: {masked}")

check("GOOGLE_API_KEY loaded from .env", _check_key)

# ── Summary ───────────────────────────────────────────────────────────────────
passed = sum(results)
total  = len(results)
print("")
print("=" * 60)
if passed == total:
    print(f"  ALL {total}/{total} CHECKS PASSED")
    print("  Your tasks are ready. Run: python apps/ai-agent/manual_test.py")
else:
    print(f"  {passed}/{total} checks passed - fix the [FAIL] items above")
print("=" * 60)
print("")
