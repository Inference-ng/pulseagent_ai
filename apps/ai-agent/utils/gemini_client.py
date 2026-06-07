"""
apps/ai-agent/utils/gemini_client.py
Shared Gemini REST client used by both Task A and Task B agents.

Key fixes vs the original:
  1. Logs the REAL error per attempt instead of silently swallowing it.
  2. Removes `responseMimeType: application/json` — this flag is only
     supported on a subset of Gemini models/regions and was the most
     likely cause of silent 400 failures on Render's free tier.
     JSON is enforced via the prompt instead (already done in both agents).
  3. Tries gemini-2.0-flash first (more capable, same price tier on free quota),
     then falls back to gemini-2.0-flash-lite.
  4. Raises a RuntimeError that includes the actual last error message,
     so the fallback `reasoning` field shows something useful in the UI.
  5. Increases per-request timeout to 45 s (Render cold-starts are slow).
"""

import json
import logging
import os
import re
import time

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model priority list — most capable first, cheaper model as fallback
# ---------------------------------------------------------------------------
_MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]


def call_gemini(system_prompt: str, user_message: str, temperature: float = 0.7) -> dict:
    """
    Call the Gemini REST API and return a parsed JSON dict.

    Tries each model in _MODELS with 2 attempts each.
    Raises RuntimeError (with the real error message) if all attempts fail.
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set in environment variables.")

    last_error: Exception | None = None

    for model_name in _MODELS:
        for attempt in range(2):
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model_name}:generateContent?key={api_key}"
            )
            payload = {
                # system_instruction is supported on all v1beta Gemini models
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": user_message}]}],
                "generationConfig": {
                    # NOTE: responseMimeType removed — it caused silent 400 errors
                    # on free-tier Render deploys for flash-lite. JSON output is
                    # enforced via the prompt ("Respond ONLY with valid JSON...").
                    "temperature": temperature,
                    "maxOutputTokens": 1024,
                },
            }

            try:
                response = httpx.post(url, json=payload, timeout=45)

                # Rate-limited — back off and retry
                if response.status_code == 429:
                    wait_secs = (attempt + 1) * 5
                    logger.warning(
                        "[Gemini] 429 rate limit on %s attempt %d — waiting %ds",
                        model_name, attempt + 1, wait_secs,
                    )
                    time.sleep(wait_secs)
                    continue

                # Any other non-2xx — log and try next model
                if not response.is_success:
                    last_error = RuntimeError(
                        f"HTTP {response.status_code} from {model_name}: {response.text[:300]}"
                    )
                    logger.error("[Gemini] %s", last_error)
                    break  # don't retry same model on non-429 HTTP errors

                data = response.json()

                # Parse response text
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

                # Strip markdown code fences if the model wrapped the JSON anyway
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)

                return json.loads(raw_text)

            except json.JSONDecodeError as e:
                last_error = RuntimeError(f"JSON parse error from {model_name}: {e}. Raw: {raw_text[:200]}")
                logger.error("[Gemini] %s", last_error)
                continue

            except Exception as e:  # network errors, timeouts, etc.
                last_error = e
                logger.error(
                    "[Gemini] %s attempt %d failed: %s: %s",
                    model_name, attempt + 1, type(e).__name__, e,
                )
                time.sleep((attempt + 1) * 2)  # brief back-off before retry
                continue

    raise RuntimeError(
        f"All Gemini models failed. Last error: {last_error}"
    )
