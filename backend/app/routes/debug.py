"""Debug-only developer inspection routes.

These routes are disabled by default and are not production data consumers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from data.loaders.forge_safe_affixes_loader import (
    ForgeSafeAffixLoader,
    ForgeSafeAffixLoaderError,
)


debug_bp = Blueprint("debug", __name__)

DEFAULT_SAMPLE_LIMIT = 5
MAX_SAMPLE_LIMIT = 50


@debug_bp.route("/forge-safe-affixes", methods=["GET"])
def forge_safe_affixes():
    """Inspect the configured Forge-safe canonical affix export."""

    if not current_app.config.get("FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED", False):
        return jsonify({
            "success": False,
            "error": "debug_endpoint_disabled",
            "message": "Forge-safe affix debug endpoint is disabled.",
        }), 404

    source_path = _configured_export_path()
    if not source_path:
        return jsonify({
            "success": False,
            "error": "missing_export_path",
            "message": "FORGE_SAFE_AFFIX_EXPORT_PATH is not configured.",
        }), 503

    try:
        loaded = ForgeSafeAffixLoader().load(source_path)
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "export_file_missing",
            "message": str(exc),
        }), 404
    except ForgeSafeAffixLoaderError as exc:
        return jsonify({
            "success": False,
            "error": "export_validation_failed",
            "message": str(exc),
        }), 422

    affix_id = request.args.get("affix_id")
    limit = _parse_limit(request.args.get("limit"))
    sample = _sample_records(loaded.records, limit=limit, affix_id=affix_id)
    summary = loaded.summary
    return jsonify({
        "success": True,
        "debug_only": True,
        "read_only": True,
        "production_consumer": False,
        "source_path": str(loaded.source_path),
        "loaded_record_count": loaded.count,
        "warning_count": len(loaded.warnings),
        "warnings": list(loaded.warnings),
        "export_policy": loaded.export_policy,
        "export_status": summary.get("export_status"),
        "total_affix_records_seen": summary.get("total_affix_records_seen"),
        "excluded_affix_records": summary.get("excluded_affix_records"),
        "sample_count": len(sample),
        "sample_records": sample,
    })


def _configured_export_path() -> Path | None:
    configured = current_app.config.get("FORGE_SAFE_AFFIX_EXPORT_PATH")
    if not configured:
        return None
    return Path(configured)


def _parse_limit(raw: str | None) -> int:
    if raw is None:
        return DEFAULT_SAMPLE_LIMIT
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_SAMPLE_LIMIT
    return max(0, min(value, MAX_SAMPLE_LIMIT))


def _sample_records(
    records: tuple[dict[str, Any], ...],
    *,
    limit: int,
    affix_id: str | None,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for record in records:
        if affix_id is not None and str(record.get("affix_id")) != affix_id:
            continue
        selected.append(_sample_record(record))
        if len(selected) >= limit:
            break
    return selected


def _sample_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "affix_id": record.get("affix_id"),
        "name": record.get("affix_name") or record.get("display_name"),
        "source_type": record.get("source_type"),
        "item_type": record.get("item_type"),
        "eligible_item_types": record.get("eligible_item_types") or [],
    }
