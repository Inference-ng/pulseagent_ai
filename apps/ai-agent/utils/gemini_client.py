"""
apps/ai-agent/utils/gemini_client.py
Shared Gemini REST client — fast key/model rotation on 429, no long waits.
"""

import json
import logging
import os
import re
import time

import httpx

logger = logging.getLogger(__name__)

# Free tier: flash-lite has higher RPM (~15) than flash (~2), so try it first
_MODELS = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]


def _get_api_keys() -> list[str]:
    """Load all available API keys from environment."""
    keys = [
        os.environ.get("GOOGLE_API_KEY", ""),
        os.environ.get("GOOGLE_API_KEY_2", ""),
    ]
    return [k.strip() for k in keys if k.strip()]


def call_gemini(system_prompt: str, user_message: str, temperature: float = 0.7) -> dict:
    """
    Call the Gemini REST API and return a parsed JSON dict.

    Rotates through all available API keys and models.
    On 429, moves to the next key/model immediately — no long waits.
    Raises RuntimeError with the real error message if everything fails.
    """
    api_keys = _get_api_keys()
    if not api_keys:
        raise RuntimeError("No Gemini API keys found. Set GOOGLE_API_KEY or GOOGLE_API_KEY_2.")

    last_error: Exception | None = None

    for key_index, api_key in enumerate(api_keys):
        logger.info("[Gemini] Trying API key %d/%d", key_index + 1, len(api_keys))

        for model_name in _MODELS:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model_name}:generateContent?key={api_key}"
            )
            payload = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": user_message}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 1024,
                },
            }

            try:
                response = httpx.post(url, json=payload, timeout=45)

                # Rate limited — move to next model/key immediately, no sleep
                if response.status_code == 429:
                    last_error = RuntimeError(
                        f"429 rate limit on key {key_index + 1}, {model_name}"
                    )
                    logger.warning("[Gemini] %s — skipping immediately", last_error)
                    continue  # try next model right away

                # Other HTTP error — log and try next model
                if not response.is_success:
                    last_error = RuntimeError(
                        f"HTTP {response.status_code} from key {key_index + 1}, "
                        f"{model_name}: {response.text[:400]}"
                    )
                    logger.error("[Gemini] %s", last_error)
                    continue  # try next model

                # Success — parse response
                data = response.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

                # Strip markdown fences just in case
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)

                parsed = json.loads(raw_text)
                logger.info(
                    "[Gemini] Success — key %d/%d, model %s",
                    key_index + 1, len(api_keys), model_name,
                )
                return parsed

            except json.JSONDecodeError as e:
                last_error = RuntimeError(
                    f"JSON parse error from {model_name}: {e}. Raw: {raw_text[:300]}"
                )
                logger.error("[Gemini] %s", last_error)
                continue

            except Exception as e:
                last_error = e
                logger.error(
                    "[Gemini] key %d, %s failed — %s: %s",
                    key_index + 1, model_name, type(e).__name__, e,
                )
                time.sleep(2)  # only sleep on network errors, not quota errors
                continue

    raise RuntimeError(f"All Gemini API keys and models exhausted. Last error: {last_error}")
