# =============================================================================
# enricher.py — Fetches species info from Gemini and caches it locally.
# =============================================================================

import json
import logging
import re
from pathlib import Path

# import google.generativeai as genai
import google.genai as genai  

import snake_classifier_backend.config as config

logger = logging.getLogger(__name__)

# Configure Gemini client once
# if config.GEMINI_API_KEY:
#     genai.configure(api_key=config.GEMINI_API_KEY)
# else:
#     logger.warning("GEMINI_API_KEY is not set — enrichment will return placeholders.")

if config.GEMINI_API_KEY:
    _client = genai.Client(api_key=config.GEMINI_API_KEY)  # ← Create client once
else:
    _client = None
    logger.warning("GEMINI_API_KEY is not set — enrichment will return placeholders.")


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _load_cache() -> dict:
    path: Path = config.CACHE_PATH
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            logger.warning("Cache file is corrupt, starting fresh.")
    return {}


def _save_cache(cache: dict) -> None:
    config.CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.CACHE_PATH.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Gemini call
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """
You are a herpetology expert. Given the snake classification result below,
return a JSON object with EXACTLY these keys (no extra keys, no markdown):

{{
  "species_guess":        "<most likely snake species for this classification, e.g. 'King Cobra'>",
  "fun_fact":             "<one interesting fact about this species, 1-2 sentences>",
  "iucn_status":          "<IUCN Red List status: LC / NT / VU / EN / CR / DD / NE>",
  "conservation_note":    "<one sentence about conservation context>",
  "first_aid_tip":        "<if venomous: concise first-aid advice. if non-venomous: empty string>",
  "danger_level":         "<Low / Medium / High / Extreme>"
}}

Classification result:
- Label: {label}
- Is venomous: {is_venomous}
- Confidence: {confidence:.0%}
- Dataset context: Indian snake species

Respond with ONLY the raw JSON object. No explanation, no markdown fences.
"""


def _call_gemini(label: str, is_venomous: bool, confidence: float) -> dict:
    """Call Gemini and parse the JSON response."""

    if not _client:
        raise ValueError("Gemini client not initialized")

    
    prompt = _PROMPT_TEMPLATE.format(
        label=label,
        is_venomous=is_venomous,
        confidence=confidence,
    )

    # model = genai.GenerativeModel(config.GEMINI_MODEL)
    # response = model.generate_content(prompt)

    response = _client.models.generate_content(
        model=f"models/{config.GEMINI_MODEL}",
        contents=prompt
    )
    
    raw = response.text.strip()

    # Strip accidental markdown fences if Gemini adds them
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    return json.loads(raw)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# In-memory cache (populated from disk on first call)
_cache: dict | None = None

_PLACEHOLDER = {
    "species_guess":     "Indian Snake Species",
    "fun_fact":          "Snakes are fascinating reptiles found across India.",
    "iucn_status":       "DD",
    "conservation_note": "Conservation data unavailable at the moment.",
    "first_aid_tip":     "",
    "danger_level":      "Unknown",
}


def get_enrichment(label: str, is_venomous: bool, confidence: float) -> dict:
    """
    Return enrichment data for a classification result.
    Uses disk cache to avoid redundant Gemini calls.

    Args:
        label:       e.g. "Venomous"
        is_venomous: bool
        confidence:  float 0–1

    Returns:
        dict with species_guess, fun_fact, iucn_status, conservation_note,
             first_aid_tip, danger_level
    """
    global _cache

    # Load cache from disk on first call
    if _cache is None:
        _cache = _load_cache()

    # Cache key — based on label only (confidence doesn't change facts)
    cache_key = label.lower().replace(" ", "_")

    if cache_key in _cache:
        logger.debug("Cache hit for key '%s'.", cache_key)
        return _cache[cache_key]

    if not config.GEMINI_API_KEY:
        logger.warning("No Gemini key — returning placeholder enrichment.")
        return _PLACEHOLDER.copy()

    try:
        data = _call_gemini(label, is_venomous, confidence)
        _cache[cache_key] = data
        _save_cache(_cache)
        logger.info("Gemini enrichment fetched and cached for '%s'.", cache_key)
        return data

    except Exception as exc:
        logger.error("Gemini call failed: %s — returning placeholder.", exc)
        return _PLACEHOLDER.copy()
