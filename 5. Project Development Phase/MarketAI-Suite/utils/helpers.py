"""
MarketAI Suite — General Helper Utilities
==========================================
Miscellaneous helpers used across services and routes.
"""

from __future__ import annotations

import uuid
import json
import re
from datetime import datetime, timezone
from typing import Any


def generate_id() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())


def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


def utcnow_iso() -> str:
    """Return the current UTC datetime as an ISO 8601 string."""
    return utcnow().isoformat()


def format_timestamp(ts: str | datetime) -> str:
    """Format a datetime or ISO string for display."""
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return ts
    return ts.strftime("%d %b %Y, %H:%M UTC")


def safe_json_loads(text: str, fallback: Any = None) -> Any:
    """
    Attempt to parse *text* as JSON.
    Returns *fallback* if parsing fails rather than raising.
    """
    if not text:
        return fallback
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return fallback


def extract_json_from_text(text: str) -> str | None:
    """
    Try to extract a JSON object or array from a larger text blob
    (e.g., when the LLM wraps JSON in markdown code fences).
    Returns the raw JSON string or None.
    """
    if not text:
        return None

    # Strip markdown code fences: ```json ... ```
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    # Try to find first { ... } or [ ... ] block
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                continue

    return None


def parse_ai_json(text: str, required_keys: list[str] | None = None) -> tuple[dict | list | None, str | None]:
    """
    Parse an AI response expected to contain JSON.

    Returns
    -------
    (parsed_object, error_message)
    On success: (dict/list, None)
    On failure: (None, error_description)
    """
    if not text:
        return None, "AI returned an empty response."

    # First attempt: direct parse
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Second attempt: extract from text
        raw = extract_json_from_text(text)
        if not raw:
            return None, "Could not extract valid JSON from AI response."
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            return None, f"AI returned malformed JSON: {exc}"

    # Optional key validation
    if required_keys and isinstance(parsed, dict):
        missing = [k for k in required_keys if k not in parsed]
        if missing:
            return None, f"AI response is missing expected fields: {', '.join(missing)}"

    return parsed, None


def truncate(text: str, max_len: int = 200, suffix: str = "…") -> str:
    """Truncate *text* to *max_len* characters, appending *suffix* if truncated."""
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def build_success_response(data: Any, message: str = "Success") -> dict:
    """Build a standard success API response envelope."""
    return {"success": True, "data": data, "message": message}


def build_error_response(code: str, message: str) -> dict:
    """Build a standard error API response envelope."""
    return {"success": False, "error": {"code": code, "message": message}}


def paginate_list(items: list, page: int = 1, per_page: int = 20) -> dict:
    """Return a paginated slice of *items* with metadata."""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": max(1, -(-total // per_page)),  # ceiling division
        },
    }
