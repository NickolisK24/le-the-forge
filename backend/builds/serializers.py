"""
E7 — Build Serialization

Exports and imports BuildDefinition objects as:
  - JSON strings (save/load, share via clipboard)
  - URL-safe tokens (compact base64-encoded gzipped JSON for URL embedding)
"""

from __future__ import annotations
import json
import gzip
import base64

from builds.build_definition import BuildDefinition


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------

def export_json(build: BuildDefinition) -> str:
    """Serialise a BuildDefinition to a JSON string."""
    return json.dumps(build.to_dict(), separators=(",", ":"))


def import_json(data: str) -> BuildDefinition:
    """
    Deserialise a BuildDefinition from a JSON string.

    Raises
    ------
    ValueError  — if `data` is not valid JSON or missing required fields.
    """
    try:
        d = json.loads(data)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    _require_fields(d, ("character_class", "mastery"))
    return BuildDefinition.from_dict(d)


# ---------------------------------------------------------------------------
# URL-safe token format (base64-encoded gzipped JSON)
# ---------------------------------------------------------------------------

def export_url(build: BuildDefinition) -> str:
    """
    Return a compact, URL-safe token representing the build.

    Encoding: gzip → base64url (no padding)
    """
    raw = export_json(build).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=6)
    return base64.urlsafe_b64encode(compressed).rstrip(b"=").decode("ascii")


def import_url(token: str) -> BuildDefinition:
    """
    Decode a URL-safe token back into a BuildDefinition.

    Raises
    ------
    ValueError  — if the token is corrupted or missing required fields.
    """
    # Restore padding
    padding = 4 - len(token) % 4
    if padding != 4:
        token += "=" * padding
    try:
        compressed = base64.urlsafe_b64decode(token.encode("ascii"))
        raw = gzip.decompress(compressed)
        data = raw.decode("utf-8")
    except Exception as exc:
        raise ValueError(f"Corrupted build token: {exc}") from exc

    return import_json(data)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require_fields(d: dict, fields: tuple[str, ...]) -> None:
    missing = [f for f in fields if f not in d]
    if missing:
        raise ValueError(f"Build definition missing required fields: {missing}")
