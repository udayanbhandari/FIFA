"""AI Insights Assistant implementation incorporating Vertex AI / Gemini.

Features:
- Lazy import of Google GenAI SDK to keep startup fast and credential-free
- Prompt configuration loaded from versioned YAML files
- Structured JSON output parsing and validation
- Strict safety filters & data validation whitelists
- 60-second TTL cache using SHA-256 keys and threading lock
- Graceful degradation fallback to rule-based assistance on any failure
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import yaml

from app.assistant.rules import get_rule_based_assistance
from app.config import get_settings
from app.models import AssistantResponse, FanAssistantQuery, Language, SuggestedAction

if TYPE_CHECKING:
    from google import genai
    from google.genai import types

logger = logging.getLogger("stadiumiq.assistant")

# ── Local cache configuration ──
# 60s TTL cache to avoid duplicate GenAI API calls for identical queries
_TTL_CACHE_DURATION_SECS = 60
_cache_store: dict[str, tuple[float, AssistantResponse]] = {}
_cache_lock = asyncio.Lock()


@lru_cache
def _get_gemini_client(project: str, region: str) -> genai.Client:
    """Lazily import and initialize the Vertex AI client instance."""
    from google import genai
    return genai.Client(vertexai=True, project=project, location=region)


def _load_prompt_config(version: str) -> dict[str, Any]:
    """Load prompt configuration from external versioned YAML files."""
    try:
        # Load file dynamically
        path = f"app/assistant/prompts/{version}.yaml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning("Failed to load prompt version %s: %s. Using inline defaults.", version, e)
        # Safe inline default fallback
        return {
            "system_instruction": "You are StadiumIQ, an AI stadium operations and fan assistant for the FIFA World Cup 2026. Keep answers concise.",
            "temperature": 0.3,
            "max_output_tokens": 1024,
        }


def _validate_ai_response(payload: dict[str, Any], query: FanAssistantQuery) -> AssistantResponse:
    """Validate JSON response from GenAI before trusting it.

    Ensures values are safe, bounds are respected, and types align.
    """
    answer = str(payload.get("answer", ""))
    if len(answer) > 1000 or not answer:
        raise ValueError("Invalid answer size or empty response")

    confidence = float(payload.get("confidence", 0.0))
    if not (0.0 <= confidence <= 1.0):
        confidence = 0.5

    zone_ref = payload.get("zone_reference")
    if zone_ref and (not isinstance(zone_ref, str) or len(zone_ref) > 100):
        zone_ref = None

    raw_actions = payload.get("suggested_actions", [])
    actions: list[SuggestedAction] = []
    if isinstance(raw_actions, list):
        for act in raw_actions:
            if isinstance(act, dict) and "action" in act and "details" in act:
                actions.append(
                    SuggestedAction(
                        action=str(act["action"])[:50],
                        details=str(act["details"])[:200],
                    )
                )

    return AssistantResponse(
        answer=answer,
        suggested_actions=actions,
        zone_reference=zone_ref,
        confidence=confidence,
        source="gemini",
        language=query.language,
    )


def _call_gemini(query: FanAssistantQuery, settings: Any) -> AssistantResponse:
    """Synchronous Gemini call. Designed to run inside a separate thread pool."""
    client = _get_gemini_client(settings.gcp_project_id, settings.gcp_region)
    prompt_config = _load_prompt_config(settings.gemini_prompt_version)

    from google.genai import types

    # Prepare configuration parameters
    sys_instruction = prompt_config.get("system_instruction")
    temperature = prompt_config.get("temperature", 0.3)
    max_tokens = prompt_config.get("max_output_tokens", 1024)

    # Use JSON mime type to ensure structured output schema
    config = types.GenerateContentConfig(
        system_instruction=sys_instruction,
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
    )

    # Context inclusion
    context_prompt = (
        f"Language requested: {query.language.value.upper()}\n"
        f"User current stadium location zone: {query.current_zone}\n"
        f"User query: {query.question}"
    )

    # Generate response
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=context_prompt,
        config=config,
    )

    if not response.text:
        raise ValueError("Empty generation result from Gemini model")

    # Parse response structured body
    data = json.loads(response.text)
    return _validate_ai_response(data, query)


def _get_cache_key(query: FanAssistantQuery) -> str:
    """Generate SHA-256 hash of prompt variables to use as cache key."""
    raw = f"{query.language.value}:{query.current_zone}:{query.question}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def get_fan_assistance(query: FanAssistantQuery) -> AssistantResponse:
    """Obtain fan assistance. Leverages Gemini with transparent rules-based fallback.

    Ensures the application never fails even if Vertex API is down or throttled.
    """
    settings = get_settings()

    # 1. Local Cache Check
    cache_key = _get_cache_key(query)
    async with _cache_lock:
        now = asyncio.get_running_loop().time()
        if cache_key in _cache_store:
            expiry, cached_res = _cache_store[cache_key]
            if now < expiry:
                # Return cached result with source tag updated to cache
                cached_res.source = "cache"
                return cached_res

    # If setting disables Gemini directly, skip to rules fallback
    if not settings.use_gemini:
        return get_rule_based_assistance(query)

    try:
        # Run sync Google GenAI request inside a thread pool to avoid event loop block
        response = await asyncio.to_thread(_call_gemini, query, settings)

        # Store in cache
        async with _cache_lock:
            expiry = asyncio.get_running_loop().time() + _TTL_CACHE_DURATION_SECS
            _cache_store[cache_key] = (expiry, response)

        # Log structure statistics
        hashed_device = hashlib.sha256(query.device_id.encode("utf-8")).hexdigest()[:8]
        logger.info(
            "Gemini response generated successfully",
            extra={
                "source": "gemini",
                "device_id_hash": hashed_device,
                "confidence": response.confidence,
            },
        )
        return response

    except Exception as e:
        logger.error("Gemini assistant call encountered error: %s. Falling back to rules.", e)
        # Graceful degradation fallback
        fallback = get_rule_based_assistance(query)
        # Clear/flag confidence score for fallback
        fallback.confidence = 0.5
        return fallback
