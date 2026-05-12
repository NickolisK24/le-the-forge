"""Experimental read-only data consumption routes.

These endpoints are disabled by default. They expose controlled internal
consumption layers without replacing production planner, crafting, simulation,
or existing affix behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from data.loaders.forge_safe_affix_bundle_loader import ForgeSafeAffixBundleLoaderError
from data.loaders.forge_safe_affixes_loader import ForgeSafeAffixLoaderError
from data.repositories.forge_safe_affix_bundle_repository import ForgeSafeAffixBundleRepository
from data.repositories.forge_safe_affix_repository import ForgeSafeAffixRepository
from app.services.forge_safe_affix_comparison_service import (
    CompareOptions,
    compare_legacy_to_forge_safe_bundle,
)


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

    parsed = _parse_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400

    if _bundle_catalog_enabled():
        return _forge_safe_affix_bundle_catalog(parsed)
    return _forge_safe_canonical_affix_catalog(parsed)


@experimental_bp.route("/forge-safe-affixes/compare-legacy", methods=["GET"])
def compare_forge_safe_affixes_to_legacy():
    """Compare legacy Forge affix data to the Forge-safe bundle."""

    if not current_app.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED", False):
        return jsonify({
            "success": False,
            "error": "experimental_catalog_disabled",
            "message": "Forge-safe affix catalog is disabled.",
        }), 404
    if not _bundle_catalog_enabled():
        return jsonify({
            "success": False,
            "error": "bundle_catalog_disabled",
            "message": "FORGE_SAFE_AFFIX_BUNDLE_ENABLED must be true for legacy comparison.",
        }), 404

    parsed = _parse_compare_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400

    bundle_path = _configured_bundle_path()
    if not bundle_path:
        return jsonify({
            "success": False,
            "error": "missing_bundle_path",
            "message": "FORGE_SAFE_AFFIX_BUNDLE_PATH is not configured.",
        }), 503

    try:
        report = compare_legacy_to_forge_safe_bundle(
            str(bundle_path),
            options=CompareOptions(
                include_details=parsed["include_details"],
                limit=parsed["limit"],
            ),
        )
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "bundle_file_missing",
            "message": str(exc),
        }), 404
    except (ForgeSafeAffixBundleLoaderError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": "bundle_validation_failed",
            "message": str(exc),
        }), 422

    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "legacy_vs_forge_safe_bundle",
        "query": {
            "include_details": parsed["include_details"],
            "limit": parsed["limit"],
        },
        "comparison": report,
    })


@experimental_bp.route("/forge-safe-affixes/<affix_id>", methods=["GET"])
def forge_safe_affix_detail(affix_id: str):
    """Return one controlled Forge-safe affix record."""

    if not current_app.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED", False):
        return jsonify({
            "success": False,
            "error": "experimental_catalog_disabled",
            "message": "Forge-safe affix catalog is disabled.",
        }), 404

    parsed = _parse_query_args()
    if parsed["errors"]:
        return jsonify({
            "success": False,
            "error": "invalid_query",
            "message": "; ".join(parsed["errors"]),
        }), 400
    parsed["affix_id"] = affix_id
    parsed["limit"] = 1
    parsed["offset"] = 0

    if _bundle_catalog_enabled():
        return _forge_safe_affix_bundle_catalog(parsed, detail=True)
    return _forge_safe_canonical_affix_catalog(parsed, detail=True)


def _forge_safe_canonical_affix_catalog(parsed: dict[str, Any], *, detail: bool = False):
    source_path = _configured_export_path()
    if not source_path:
        return jsonify({
            "success": False,
            "error": "missing_export_path",
            "message": "FORGE_SAFE_AFFIX_EXPORT_PATH is not configured.",
        }), 503

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

    records = _query_canonical_records(
        repository,
        affix_id=parsed["affix_id"],
        query=parsed["q"],
        source_type=parsed["source_type"],
        item_type=parsed["item_type"],
        limit=parsed["limit"],
        offset=parsed["offset"],
    )
    summary = repository.get_summary()
    if detail and not records:
        return jsonify({
            "success": False,
            "error": "affix_not_found",
            "message": f"Forge-safe affix not found: {parsed['affix_id']}",
        }), 404
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "forge_safe_canonical_affixes",
        "source_path": summary["source_path"],
        "result_count": len(records),
        "total_loaded_count": repository.count(),
        "total_affixes": repository.count(),
        "total_modifiers": None,
        "query": {
            "limit": parsed["limit"],
            "offset": parsed["offset"],
            "q": parsed["q"],
            "affix_id": parsed["affix_id"],
            "source_type": parsed["source_type"],
            "item_type": parsed["item_type"],
            "include_modifiers": parsed["include_modifiers"],
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


def _forge_safe_affix_bundle_catalog(parsed: dict[str, Any], *, detail: bool = False):
    bundle_path = _configured_bundle_path()
    if not bundle_path:
        return jsonify({
            "success": False,
            "error": "missing_bundle_path",
            "message": "FORGE_SAFE_AFFIX_BUNDLE_PATH is not configured.",
        }), 503

    try:
        repository = ForgeSafeAffixBundleRepository(bundle_path).load()
    except FileNotFoundError as exc:
        return jsonify({
            "success": False,
            "error": "bundle_file_missing",
            "message": str(exc),
        }), 404
    except (ForgeSafeAffixBundleLoaderError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": "bundle_validation_failed",
            "message": str(exc),
        }), 422

    records = _query_bundle_records(
        repository,
        affix_id=parsed["affix_id"],
        query=parsed["q"],
        source_type=parsed["source_type"],
        item_type=parsed["item_type"],
        limit=parsed["limit"],
        offset=parsed["offset"],
        include_modifiers=parsed["include_modifiers"],
    )
    summary = repository.get_summary()
    if detail and not records:
        return jsonify({
            "success": False,
            "error": "affix_not_found",
            "message": f"Forge-safe affix not found: {parsed['affix_id']}",
        }), 404
    return jsonify({
        "success": True,
        "experimental": True,
        "read_only": True,
        "production_consumer": False,
        "data_source": "forge_safe_affix_bundle",
        "source_path": summary["source_path"],
        "result_count": len(records),
        "total_loaded_count": repository.count_affixes(),
        "total_affixes": repository.count_affixes(),
        "total_modifiers": repository.count_modifiers(),
        "query": {
            "limit": parsed["limit"],
            "offset": parsed["offset"],
            "q": parsed["q"],
            "affix_id": parsed["affix_id"],
            "source_type": parsed["source_type"],
            "item_type": parsed["item_type"],
            "include_modifiers": parsed["include_modifiers"],
        },
        "warning_count": summary["warning_count"],
        "warnings": summary["warnings"],
        "export_policy": summary["export_policy"],
        "export_status": summary["export_status"],
        "total_affix_records_seen": summary["total_affix_records_seen"],
        "excluded_affix_records": summary["excluded_affix_records"],
        "bundle_summary": summary["summary"],
        "cross_reference_validation": summary["cross_reference_validation"],
        "records": records,
    })


def _configured_export_path() -> Path | None:
    configured = current_app.config.get("FORGE_SAFE_AFFIX_EXPORT_PATH")
    if not configured:
        return None
    return Path(configured)


def _configured_bundle_path() -> Path | None:
    configured = current_app.config.get("FORGE_SAFE_AFFIX_BUNDLE_PATH")
    if not configured:
        return None
    return Path(configured)


def _bundle_catalog_enabled() -> bool:
    return current_app.config.get("FORGE_SAFE_AFFIX_BUNDLE_ENABLED", False)


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
        "include_modifiers": _parse_bool(request.args.get("include_modifiers")),
        "errors": errors,
    }


def _parse_compare_query_args() -> dict[str, Any]:
    errors: list[str] = []
    limit = _parse_non_negative_int("limit", request.args.get("limit"), DEFAULT_LIMIT, errors)
    return {
        "limit": min(limit, MAX_LIMIT),
        "include_details": _parse_bool(request.args.get("include_details")),
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


def _parse_bool(raw: str | None) -> bool:
    if raw is None:
        return False
    return raw.lower() in {"1", "true", "yes", "on"}


def _query_canonical_records(
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


def _query_bundle_records(
    repository: ForgeSafeAffixBundleRepository,
    *,
    affix_id: str,
    query: str,
    source_type: str,
    item_type: str,
    limit: int,
    offset: int,
    include_modifiers: bool,
) -> list[dict[str, Any]]:
    if affix_id:
        if include_modifiers:
            bundle_record = repository.get_affix_with_modifiers(affix_id)
            records = [_format_bundle_record(bundle_record, include_modifiers=True)] if bundle_record else []
        else:
            record = repository.get_affix(affix_id)
            records = [_format_bundle_record({"affix": record}, include_modifiers=False)] if record else []
    elif query:
        records = repository.search_affixes(query, limit=repository.count_affixes())
    elif source_type:
        records = repository.filter_by_source_type(source_type, limit=repository.count_affixes())
    elif item_type:
        records = repository.filter_by_item_type(item_type, limit=repository.count_affixes())
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

    page = records[offset : offset + limit]
    return [
        _format_bundle_affix(repository, record, include_modifiers=include_modifiers)
        for record in page
    ]


def _format_bundle_affix(
    repository: ForgeSafeAffixBundleRepository,
    affix: dict[str, Any],
    *,
    include_modifiers: bool,
) -> dict[str, Any]:
    identity = _source_affix_identity(affix)
    modifiers = repository.get_modifiers_for_affix(identity)
    record = dict(affix)
    record["modifier_count"] = len(modifiers)
    if include_modifiers:
        record["modifiers"] = modifiers
    return record


def _format_bundle_record(
    bundle_record: dict[str, Any] | None,
    *,
    include_modifiers: bool,
) -> dict[str, Any]:
    if not bundle_record or bundle_record.get("affix") is None:
        return {}
    record = dict(bundle_record["affix"])
    modifiers = bundle_record.get("modifiers") or []
    record["modifier_count"] = bundle_record.get("modifier_count", len(modifiers))
    if include_modifiers:
        record["modifiers"] = modifiers
    return record


def _record_matches_item_type(record: dict[str, Any], expected: str) -> bool:
    if str(record.get("item_type", "")).lower() == expected:
        return True
    return any(
        str(value).lower() == expected
        for value in (record.get("eligible_item_types") or [])
    )


def _source_affix_identity(record: dict[str, Any]) -> str:
    provenance = record.get("provenance")
    if isinstance(provenance, dict) and provenance.get("source_affix_identity"):
        return str(provenance["source_affix_identity"])
    return ""
