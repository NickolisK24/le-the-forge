"""
Structured diagnostics for failed or partial build imports.

Every ImportFailure carries a `diagnostics` record so an alert can answer:
what failed, at which stage, why (HTTP status / category / safe upstream
headers), against which app / data version, for which user, and whether the
failure can be retried. Nothing secret is retained: no cookies, no
authorization headers, no response bodies.
"""

from __future__ import annotations

import os
from typing import Any, Iterable, Mapping, Optional

# Missing-field evaluation state. A transport failure never evaluated
# completeness, so it must not be reported as "none missing".
NOT_EVALUATED = "NOT_EVALUATED"
NONE_MISSING = "NONE_MISSING"
MISSING_FIELDS_PRESENT = "MISSING_FIELDS_PRESENT"

# Failure stages, in pipeline order.
STAGE_URL_VALIDATION = "url_validation"
STAGE_FETCH = "fetch"
STAGE_PARSE = "parse"
STAGE_MAP = "map"
STAGE_PERSIST = "persist"
STAGE_PARTIAL = "partial_import"
STAGE_UNHANDLED = "unhandled"
STAGE_UNKNOWN = "unknown"

# Response headers that are safe and useful to retain (case-insensitive).
SAFE_UPSTREAM_HEADERS = (
    "server",
    "cf-ray",
    "cf-mitigated",
    "cf-cache-status",
    "content-type",
    "retry-after",
)
_HEADER_VALUE_LIMIT = 200


def safe_upstream_headers(headers: Optional[Mapping[str, Any]]) -> dict:
    """Return only allowlisted upstream response headers, truncated."""
    if not headers:
        return {}
    kept = {}
    for name, value in headers.items():
        key = str(name).lower()
        if key in SAFE_UPSTREAM_HEADERS:
            kept[key] = str(value)[:_HEADER_VALUE_LIMIT]
    return kept


def classify_http_status(status: Optional[int]) -> str:
    if status is None:
        return "unknown"
    if status in (401, 403):
        return "upstream_blocked"
    if status == 429:
        return "upstream_rate_limited"
    if status == 404:
        return "upstream_not_found"
    if 500 <= status < 600:
        return "upstream_server_error"
    if status >= 400:
        return "upstream_http_error"
    return "upstream_unexpected_response"


def http_failure_diagnostics(status: Optional[int], headers: Optional[Mapping[str, Any]] = None,
                             **extra: Any) -> dict:
    """Diagnostics for a failed upstream HTTP fetch (parsing never started)."""
    diag = {
        "failure_stage": STAGE_FETCH,
        "http_status": status,
        "error_category": classify_http_status(status),
        "upstream_headers": safe_upstream_headers(headers),
        "parsing_started": False,
    }
    diag.update(extra)
    return diag


def missing_field_state(parsing_started: bool, missing_fields: Optional[Iterable]) -> str:
    if not parsing_started:
        return NOT_EVALUATED
    return MISSING_FIELDS_PRESENT if list(missing_fields or []) else NONE_MISSING


def _app_version() -> str:
    try:
        from app import __version__
        return __version__
    except Exception:
        return "unknown"


def _app_commit() -> str:
    for var in ("RENDER_GIT_COMMIT", "GIT_COMMIT", "SOURCE_VERSION"):
        value = os.environ.get(var)
        if value:
            return value[:40]
    return "unknown"


def _data_version() -> str:
    try:
        from flask import current_app
        pipeline = current_app.extensions.get("game_data")
        version = getattr(pipeline, "version", None) or getattr(pipeline, "_version", None)
        return str(version) if version else "unknown"
    except Exception:
        return "unknown"


def summarize_partial_data(partial_data: Optional[Mapping]) -> dict:
    """Counts-only summary of what parsed; never the raw build payload."""
    if not isinstance(partial_data, Mapping):
        return {}

    def _count(value):
        if isinstance(value, (list, dict)):
            return len(value)
        if isinstance(value, int):
            return value
        return None

    summary = {}
    for key in ("character_class", "mastery", "level"):
        if partial_data.get(key) is not None:
            summary[key] = partial_data.get(key)
    for key, label in (("skills", "skills"), ("passive_tree", "passives"),
                       ("passives", "passives"), ("gear", "gear")):
        count = _count(partial_data.get(key))
        if count is not None and label not in summary:
            summary[label] = count
    if partial_data.get("raw_keys"):
        summary["raw_keys"] = [str(k) for k in list(partial_data["raw_keys"])[:30]]
    return summary


def build_failure_diagnostics(
    *,
    source: str,
    url: str,
    user_id: Optional[str],
    failure_stage: str,
    missing_fields: Optional[Iterable] = None,
    partial_data: Optional[Mapping] = None,
    importer_diagnostics: Optional[Mapping] = None,
    parsing_started: Optional[bool] = None,
    error_category: Optional[str] = None,
) -> dict:
    """Assemble the structured record stored on ImportFailure.diagnostics."""
    importer_diagnostics = dict(importer_diagnostics or {})
    stage = importer_diagnostics.get("failure_stage") or failure_stage
    if parsing_started is None:
        parsing_started = bool(importer_diagnostics.get("parsing_started", stage not in (
            STAGE_URL_VALIDATION, STAGE_FETCH, STAGE_UNHANDLED, STAGE_UNKNOWN)))
    missing = list(missing_fields or [])
    is_real_url = url.startswith("http://") or url.startswith("https://")
    return {
        "schema": "import_failure_diagnostics/v1",
        "source": source,
        "failure_stage": stage,
        "error_category": importer_diagnostics.get("error_category") or error_category or "unknown",
        "http_status": importer_diagnostics.get("http_status"),
        "upstream_headers": importer_diagnostics.get("upstream_headers") or {},
        "upstream_attempts": importer_diagnostics.get("attempts") or [],
        "parsing_started": parsing_started,
        "missing_field_state": missing_field_state(parsing_started, missing),
        "missing_field_count": len(missing),
        "partial_data_summary": summarize_partial_data(partial_data),
        "url": url,
        "user": user_id or "anonymous",
        "app_version": _app_version(),
        "app_commit": _app_commit(),
        "data_version": _data_version(),
        "extractor_version": "unknown",
        "replay": "url_retry" if is_real_url else "not_replayable_payload_not_stored",
    }
