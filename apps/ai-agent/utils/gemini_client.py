"""
apps/ai-agent/utils/gemini_client.py
Multi-provider LLM client — Gemini → Groq → OpenRouter fallback chain.
Fast key/model rotation on 429, no long waits.
"""

import json
import logging
import os
import re
import time

import httpx

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Provider configurations
# ──────────────────────────────────────────────────────────────────────

# Gemini: free tier, flash-lite has higher RPM (~15) than flash (~2)
_GEMINI_MODELS = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]

# Groq: free tier, very fast inference, generous rate limits
# Sign up at https://console.groq.com — free 30 req/min
_GROQ_MODELS = ["llama-3.1-8b-instant", "gemma2-9b-it"]

# OpenRouter: aggregated provider, many free models available
# Sign up at https://openrouter.ai — free tier available
_OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.1-8b-instruct:free",
]


def _get_api_keys() -> list[str]:
    """Load all available Gemini API keys from environment."""
    keys = [
        os.environ.get("GOOGLE_API_KEY", ""),
        os.environ.get("GOOGLE_API_KEY_2", ""),
    ]
    return [k.strip() for k in keys if k.strip()]


def _get_groq_key() -> str:
    """Load Groq API key from environment."""
    return os.environ.get("GROQ_API_KEY", "").strip()


def _get_openrouter_key() -> str:
    """Load OpenRouter API key from environment."""
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


# ──────────────────────────────────────────────────────────────────────
# Provider call implementations
# ──────────────────────────────────────────────────────────────────────

def _call_gemini_provider(
    system_prompt: str, user_message: str, temperature: float
) -> dict | None:
    """Try all Gemini keys × models. Returns parsed dict or None."""
    api_keys = _get_api_keys()
    if not api_keys:
        logger.info("[Gemini] No API keys configured — skipping provider")
        return None

    for key_index, api_key in enumerate(api_keys):
        for model_name in _GEMINI_MODELS:
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

                if response.status_code == 429:
                    logger.warning(
                        "[Gemini] 429 rate limit on key %d, %s — skipping",
                        key_index + 1, model_name,
                    )
                    continue

                if not response.is_success:
                    logger.error(
                        "[Gemini] HTTP %d from key %d, %s: %s",
                        response.status_code, key_index + 1,
                        model_name, response.text[:300],
                    )
                    continue

                data = response.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return _parse_json(raw_text, f"Gemini/{model_name}")

            except json.JSONDecodeError as e:
                logger.error("[Gemini] JSON parse error from %s: %s", model_name, e)
                continue
            except Exception as e:
                logger.error("[Gemini] key %d, %s — %s: %s",
                             key_index + 1, model_name, type(e).__name__, e)
                time.sleep(1)
                continue

    logger.warning("[Gemini] All keys and models exhausted")
    return None


def _call_groq_provider(
    system_prompt: str, user_message: str, temperature: float
) -> dict | None:
    """Try Groq models. Returns parsed dict or None."""
    api_key = _get_groq_key()
    if not api_key:
        logger.info("[Groq] No API key configured — skipping provider")
        return None

    for model_name in _GROQ_MODELS:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"},
        }

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 429:
                logger.warning("[Groq] 429 rate limit on %s — skipping", model_name)
                continue

            if not response.is_success:
                logger.error(
                    "[Groq] HTTP %d from %s: %s",
                    response.status_code, model_name, response.text[:300],
                )
                continue

            data = response.json()
            raw_text = data["choices"][0]["message"]["content"].strip()
            return _parse_json(raw_text, f"Groq/{model_name}")

        except json.JSONDecodeError as e:
            logger.error("[Groq] JSON parse error from %s: %s", model_name, e)
            continue
        except Exception as e:
            logger.error("[Groq] %s — %s: %s", model_name, type(e).__name__, e)
            time.sleep(1)
            continue

    logger.warning("[Groq] All models exhausted")
    return None


def _call_openrouter_provider(
    system_prompt: str, user_message: str, temperature: float
) -> dict | None:
    """Try OpenRouter models. Returns parsed dict or None."""
    api_key = _get_openrouter_key()
    if not api_key:
        logger.info("[OpenRouter] No API key configured — skipping provider")
        return None

    for model_name in _OPENROUTER_MODELS:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pulseagent-ai.vercel.app",
            "X-Title": "PulseAgent AI",
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": 1024,
        }

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=45)

            if response.status_code == 429:
                logger.warning("[OpenRouter] 429 on %s — skipping", model_name)
                continue

            if not response.is_success:
                logger.error(
                    "[OpenRouter] HTTP %d from %s: %s",
                    response.status_code, model_name, response.text[:300],
                )
                continue

            data = response.json()
            raw_text = data["choices"][0]["message"]["content"].strip()
            return _parse_json(raw_text, f"OpenRouter/{model_name}")

        except json.JSONDecodeError as e:
            logger.error("[OpenRouter] JSON parse error from %s: %s", model_name, e)
            continue
        except Exception as e:
            logger.error("[OpenRouter] %s — %s: %s", model_name, type(e).__name__, e)
            time.sleep(1)
            continue

    logger.warning("[OpenRouter] All models exhausted")
    return None


# ──────────────────────────────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────────────────────────────

def _parse_json(raw_text: str, source: str) -> dict:
    """Strip markdown fences and parse JSON from raw LLM output."""
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)
    parsed = json.loads(raw_text)
    logger.info("[LLM] ✓ Success via %s", source)
    return parsed


# ──────────────────────────────────────────────────────────────────────
# Public API — drop-in replacement
# ──────────────────────────────────────────────────────────────────────

def call_gemini(system_prompt: str, user_message: str, temperature: float = 0.7) -> dict:
    """
    Call an LLM and return a parsed JSON dict.

    Provider fallback chain: Gemini → Groq → OpenRouter.
    On 429 or failure, moves to the next provider immediately.
    Raises RuntimeError if all providers fail.
    """
    errors: list[str] = []

    # 1) Try Gemini first (existing behaviour)
    try:
        result = _call_gemini_provider(system_prompt, user_message, temperature)
        if result is not None:
            return result
        errors.append("Gemini: all keys/models exhausted or rate-limited")
    except Exception as e:
        errors.append(f"Gemini: {e}")

    # 2) Try Groq as secondary provider
    try:
        result = _call_groq_provider(system_prompt, user_message, temperature)
        if result is not None:
            return result
        errors.append("Groq: all models exhausted or not configured")
    except Exception as e:
        errors.append(f"Groq: {e}")

    # 3) Try OpenRouter as tertiary provider
    try:
        result = _call_openrouter_provider(system_prompt, user_message, temperature)
        if result is not None:
            return result
        errors.append("OpenRouter: all models exhausted or not configured")
    except Exception as e:
        errors.append(f"OpenRouter: {e}")

    raise RuntimeError(
        f"All LLM providers exhausted. Errors: {'; '.join(errors)}"
    )
