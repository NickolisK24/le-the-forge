"""Experimental read-only data consumption routes.

These endpoints are disabled by default. They expose controlled internal
consumption layers without replacing production planner, crafting, simulation,
or existing affix behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from data.loaders.forge_safe_affixes_loader import ForgeSafeAffixLoaderError
from data.repositories.forge_safe_affix_repository import ForgeSafeAffixRepository


experimental_bp = Blueprint("experimental", __name__)

DEFAULT_LIMIT = 50
MAX_LIMIT = 100


@experimental_bp.route("/forge-safe-affixes", methods=["GET"])
def forge_safe_affix_catalog():
    """Query the controlled Forge-safe affix repository."""

    if not current_app.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED", False):
        return jsonify({
            "success": False,
            "error": "experimental_catalog_disabled",
            "message": "Forge-safe affix catalog is disabled.",
        }), 404

    source_path = _configured_export_path()
    if not source_path:
        return jsonify({
            "success": False,
            "error": "missing_export_path",
            "message": "FORGE_SAFE_AFFIX_EXPORT_PATH is not configured.",
        }), 503

    parsed = _parse_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400

    try:
        repository = ForgeSafeAffixRepository(source_path).load()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "export_file_missing",
            "message": str(exc),
        }), 404
    except (ForgeSafeAffixLoaderError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": "export_validation_failed",
            "message": str(exc),
        }), 422

    records = _query_records(
        repository,
        affix_id=parsed["affix_id"],
        query=parsed["q"],
        source_type=parsed["source_type"],
        item_type=parsed["item_type"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    summary = repository.get_summary()
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "source_path": summary["source_path"],
        "result_count": len(records),
        "total_loaded_count": repository.count(),
        "query": {
            "limit": parsed["limit"],
            "offset": parsed["offset"],
            "q": parsed["q"],
            "affix_id": parsed["affix_id"],
            "source_type": parsed["source_type"],
            "item_type": parsed["item_type"],
        },
        "warning_count": summary["warning_count"],
        "warnings": summary["warnings"],
        "export_policy": summary["export_policy"],
        "export_status": summary["export_status"],
        "total_affix_records_seen": summary["total_affix_records_seen"],
        "excluded_affix_records": summary["excluded_affix_records"],
        "summary": summary["summary"],
        "records": records,
    })


def _configured_export_path() -> Path | None:
    configured = current_app.config.get("FORGE_SAFE_AFFIX_EXPORT_PATH")
    if not configured:
        return None
    return Path(configured)


def _parse_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    offset = _parse_non_negative_int("offset", request.args.get("offset"), 0, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
        "q": request.args.get("q") or request.args.get("search") or "",
        "affix_id": request.args.get("affix_id") or "",
        "source_type": request.args.get("source_type") or "",
        "item_type": request.args.get("item_type") or "",
        "errors": errors,
    }


def _parse_non_negative_int(
    name: str,
    raw: str | None,
    default: int,
    errors: list[str],
) -> int:
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except ValueError:
        errors.append(f"{name} must be an integer")
        return default
    if value < 0:
        errors.append(f"{name} must be non-negative")
        return default
    return value


def _query_records(
    repository: ForgeSafeAffixRepository,
    *,
    affix_id: str,
    query: str,
    source_type: str,
    item_type: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    if affix_id:
        record = repository.get_by_affix_id(affix_id)
        records = [record] if record is not None else []
    elif query:
        records = repository.search(query, limit=repository.count())
    elif source_type:
        records = repository.filter_by_source_type(source_type, limit=repository.count())
    elif item_type:
        records = repository.filter_by_item_type(item_type, limit=repository.count())
    else:
        records = repository.list_affixes()

    if source_type and (affix_id or query or item_type):
        expected_source = source_type.lower()
        records = [
            record for record in records
            if str(record.get("source_type", "")).lower() == expected_source
        ]
    if item_type and (affix_id or query or source_type):
        expected_item = item_type.lower()
        records = [
            record for record in records
            if _record_matches_item_type(record, expected_item)
        ]
    return records[offset : offset + limit]


def _record_matches_item_type(record: dict[str, Any], expected: str) -> bool:
    if str(record.get("item_type", "")).lower() == expected:
        return True
    return any(
        str(value).lower() == expected
        for value in (record.get("eligible_item_types") or [])
    )
