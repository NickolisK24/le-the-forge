"""Developer-only comparison of saved and fresh LE Tools sidecar diagnostics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.game_data.bundle_item_type_dry_run_resolver import (
    STATUS_DEFERRED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
)
from app.game_data.le_tools_fresh_sidecar_diagnostic import (
    DEFAULT_SAVED_SIDECAR,
    build_fresh_sidecar_diagnostic,
)
from app.game_data.le_tools_import_stage_context_report import DEFAULT_STAGE_FIXTURE
from app.game_data.le_tools_sidecar_diagnostic_consumer import consume_sidecar_diagnostic


COUNT_KEYS = [
    "total_items",
    STATUS_RESOLVED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_DEFERRED,
    STATUS_UNRESOLVED,
    "missing_identity",
    "ambiguous",
    "unsafe",
    "subtype_only",
    "name_only",
]


def build_sidecar_diagnostic_comparison(
    sidecar_path: str | Path = DEFAULT_SAVED_SIDECAR,
    fixture_path: str | Path = DEFAULT_STAGE_FIXTURE,
) -> dict[str, Any]:
    saved = consume_sidecar_diagnostic(sidecar_path)
    fresh = build_fresh_sidecar_diagnostic(
        fixture_path=fixture_path,
        saved_sidecar_path=sidecar_path,
    )
    return compare_sidecar_diagnostics(saved, fresh)


def compare_sidecar_diagnostics(saved: dict[str, Any], fresh: dict[str, Any]) -> dict[str, Any]:
    saved_norm = _normalize_saved(saved)
    fresh_norm = _normalize_fresh(fresh)
    count_deltas = {
        key: {
            "saved": saved_norm["counts"].get(key, 0),
            "fresh": fresh_norm["counts"].get(key, 0),
            "delta": fresh_norm["counts"].get(key, 0) - saved_norm["counts"].get(key, 0),
        }
        for key in COUNT_KEYS
    }
    warning_delta = _message_delta(saved_norm["warnings"], fresh_norm["warnings"])
    error_delta = _message_delta(saved_norm["errors"], fresh_norm["errors"])
    shape_agreement = {
        "fresh_matches_saved_top_level_keys": bool((fresh.get("shape") or {}).get("top_level_keys_match_saved")),
        "fresh_matches_saved_summary_keys": bool((fresh.get("shape") or {}).get("summary_keys_match_saved")),
        "fresh_item_count_matches_saved": saved_norm["counts"]["total_items"] == fresh_norm["counts"]["total_items"],
        "fresh_item_sections_present": bool((fresh.get("shape") or {}).get("item_sections_present")),
    }
    migration_gate_status = _migration_gate_status(
        saved_norm=saved_norm,
        fresh_norm=fresh_norm,
        count_deltas=count_deltas,
        warning_delta=warning_delta,
        error_delta=error_delta,
        shape_agreement=shape_agreement,
    )
    return {
        "production_safe": False,
        "migration_gate_status": migration_gate_status,
        "saved_sidecar_status": saved_norm["status"],
        "fresh_sidecar_status": fresh_norm["status"],
        "shape_agreement": shape_agreement,
        "count_deltas": count_deltas,
        "warning_delta": warning_delta,
        "error_delta": error_delta,
        "saved": saved_norm,
        "fresh": fresh_norm,
        "recommendations": _recommendations(migration_gate_status, count_deltas, warning_delta, error_delta),
    }


def render_sidecar_diagnostic_comparison(report: dict[str, Any]) -> str:
    lines = [
        "# LE Tools Sidecar Diagnostic Comparison Report",
        "",
        f"- migration_gate_status: {report['migration_gate_status']}",
        "- production_safe: false",
        f"- saved_sidecar_status: {report['saved_sidecar_status']}",
        f"- fresh_sidecar_status: {report['fresh_sidecar_status']}",
        "",
        "## Shape Agreement",
        "",
    ]
    for key, value in report["shape_agreement"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Count Deltas", ""])
    for key in COUNT_KEYS:
        delta = report["count_deltas"][key]
        lines.append(f"- {key}: saved={delta['saved']} fresh={delta['fresh']} delta={delta['delta']}")

    lines.extend(["", "## Warning Delta", ""])
    lines.extend(_render_message_delta(report["warning_delta"]))
    lines.extend(["", "## Error Delta", ""])
    lines.extend(_render_message_delta(report["error_delta"]))
    lines.extend(["", "## Recommendations", ""])
    lines.extend(_format_messages(report["recommendations"]))
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- This comparison is diagnostic-only and non-production.",
            "- It does not modify importers, loaders, production output, APIs, frontend behavior, or simulation.",
            "- production_safe remains false.",
            "- subtype_id-only identity and name-only matching remain blocked.",
            "- This report does not claim production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def sidecar_diagnostic_comparison_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def _normalize_saved(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary") or {}
    counts = {
        "total_items": summary.get("total_items", 0),
        STATUS_RESOLVED: summary.get(STATUS_RESOLVED, 0),
        STATUS_NEEDS_CONTEXT: summary.get(STATUS_NEEDS_CONTEXT, 0),
        STATUS_NEEDS_REVIEW: summary.get(STATUS_NEEDS_REVIEW, 0),
        STATUS_DEFERRED: summary.get(STATUS_DEFERRED, 0),
        STATUS_UNRESOLVED: summary.get(STATUS_UNRESOLVED, 0),
        "missing_identity": len(report.get("records_requiring_base_type_id") or [])
        + len(report.get("unresolved_records") or []),
        "ambiguous": len(report.get("manual_review_records") or []),
        "unsafe": 0,
        "subtype_only": len(report.get("subtype_only_blocked_records") or []),
        "name_only": len(report.get("name_only_blocked_records") or []),
    }
    return {
        "status": report.get("validation_status"),
        "production_safe": False,
        "counts": counts,
        "warnings": list(report.get("warnings") or []),
        "errors": list(report.get("errors") or []),
        "sidecar_path": report.get("sidecar_path"),
    }


def _normalize_fresh(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary") or {}
    counts = {key: summary.get(key, 0) for key in COUNT_KEYS}
    return {
        "status": report.get("status"),
        "validation_status": report.get("validation_status"),
        "production_safe": False,
        "counts": counts,
        "warnings": list(report.get("warnings") or []),
        "errors": list(report.get("errors") or []),
        "fixture_path": report.get("fixture_path"),
        "saved_sidecar_path": report.get("saved_sidecar_path"),
    }


def _message_delta(saved_messages: list[str], fresh_messages: list[str]) -> dict[str, Any]:
    saved_set = set(saved_messages)
    fresh_set = set(fresh_messages)
    return {
        "saved_count": len(saved_messages),
        "fresh_count": len(fresh_messages),
        "added_in_fresh": sorted(fresh_set - saved_set),
        "missing_from_fresh": sorted(saved_set - fresh_set),
    }


def _migration_gate_status(
    *,
    saved_norm: dict[str, Any],
    fresh_norm: dict[str, Any],
    count_deltas: dict[str, dict[str, int]],
    warning_delta: dict[str, Any],
    error_delta: dict[str, Any],
    shape_agreement: dict[str, bool],
) -> str:
    if saved_norm["errors"] or fresh_norm["errors"] or error_delta["added_in_fresh"] or error_delta["missing_from_fresh"]:
        return "blocked"
    if fresh_norm["counts"].get("unsafe", 0) > 0 or saved_norm["counts"].get("unsafe", 0) > 0:
        return "blocked"
    structural_shape_ok = (
        shape_agreement["fresh_matches_saved_top_level_keys"]
        and shape_agreement["fresh_matches_saved_summary_keys"]
        and shape_agreement["fresh_item_sections_present"]
    )
    if not structural_shape_ok:
        return "blocked"
    if any(delta["delta"] != 0 for delta in count_deltas.values()):
        return "warning"
    if saved_norm["warnings"] or fresh_norm["warnings"]:
        return "warning"
    return "diagnostic_only_pass"


def _recommendations(
    migration_gate_status: str,
    count_deltas: dict[str, dict[str, int]],
    warning_delta: dict[str, Any],
    error_delta: dict[str, Any],
) -> list[str]:
    recommendations = [
        "Keep this comparison diagnostic-only and non-production.",
        "Do not consume bundle item type IDs in production from this report.",
        "Keep production_safe=false.",
    ]
    if migration_gate_status == "blocked":
        recommendations.append("Do not expand diagnostics until blocking errors, unsafe records, or shape mismatches are resolved.")
    if migration_gate_status == "warning":
        recommendations.append("Review warning/count deltas before using fresh sidecars as a broader diagnostic baseline.")
    if any(delta["delta"] != 0 for delta in count_deltas.values()):
        recommendations.append("Investigate count drift between saved and fresh diagnostics.")
    if warning_delta["added_in_fresh"] or warning_delta["missing_from_fresh"]:
        recommendations.append("Review warning deltas; do not treat warning drift as migration readiness.")
    if error_delta["added_in_fresh"] or error_delta["missing_from_fresh"]:
        recommendations.append("Resolve error deltas before any consumer expansion.")
    return recommendations


def _render_message_delta(delta: dict[str, Any]) -> list[str]:
    lines = [
        f"- saved_count: {delta['saved_count']}",
        f"- fresh_count: {delta['fresh_count']}",
        "- added_in_fresh:",
    ]
    lines.extend(f"  - {message}" for message in delta["added_in_fresh"]) if delta["added_in_fresh"] else lines.append("  - none")
    lines.append("- missing_from_fresh:")
    lines.extend(f"  - {message}" for message in delta["missing_from_fresh"]) if delta["missing_from_fresh"] else lines.append("  - none")
    return lines


def _format_messages(messages: list[str]) -> list[str]:
    if not messages:
        return ["- none"]
    return [f"- {message}" for message in messages]
