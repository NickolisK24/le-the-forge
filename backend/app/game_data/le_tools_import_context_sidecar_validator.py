"""Developer-only validator for LE Tools import context sidecars."""

from __future__ import annotations

from copy import deepcopy
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
from app.game_data.le_tools_import_context_sidecar import validate_sidecar


ALLOWED_STATUSES = {
    STATUS_RESOLVED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_DEFERRED,
    STATUS_UNRESOLVED,
}
COLLAPSED_SLUGS = {"axe", "mace", "sword", "idol_1x1"}


def load_sidecar(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Sidecar JSON must be an object.")
    return data


def validate_sidecar_artifact(sidecar: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(sidecar)
    try:
        errors = validate_sidecar(candidate)
    except (KeyError, TypeError, AttributeError) as exc:
        errors = [f"sidecar structure is malformed: {exc}"]
    errors.extend(_structural_errors(candidate))
    warnings = _warnings(candidate)
    status = "failed" if errors else ("warning" if warnings else "passed")
    return {
        "status": status,
        "production_safe": False,
        "errors": errors,
        "warnings": warnings,
        "summary": _status_summary(candidate),
    }


def render_validation_result(result: dict[str, Any]) -> str:
    lines = [
        "# LE Tools Import Context Sidecar Validation Report",
        "",
        f"- status: {result['status']}",
        "- production_safe: false",
        "",
        "## Summary",
        "",
    ]
    for key, value in result["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Errors", ""])
    lines.extend(_format_messages(result["errors"]))
    lines.extend(["", "## Warnings", ""])
    lines.extend(_format_messages(result["warnings"]))
    lines.extend(
        [
            "",
            "## Safe Properties",
            "",
            "- Validation is developer-only and does not mutate sidecar files.",
            "- production_safe must remain false globally and per item.",
            "- subtype-only, name-only, spear, and collapsed-without-context records cannot resolve.",
            "",
            "## Failure Conditions",
            "",
            "- production_safe=true anywhere.",
            "- Resolved subtype-only or name-only records.",
            "- Resolved spear records.",
            "- Resolved collapsed slugs without base_type_id context.",
            "- Summary counts that do not match item statuses.",
            "",
        ]
    )
    return "\n".join(lines)


def validation_result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True)


def _structural_errors(sidecar: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    items = sidecar.get("items")
    if not isinstance(items, list):
        return ["items must be a list"]
    for item in items:
        index = item.get("index")
        for section in ("raw", "mapped", "resolver", "context"):
            if not isinstance(item.get(section), dict):
                errors.append(f"item {index} missing {section} section")
        resolver = item.get("resolver") if isinstance(item.get("resolver"), dict) else {}
        status = resolver.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"item {index} resolver.status is invalid: {status}")
    if not isinstance(sidecar.get("summary"), dict):
        errors.append("summary must be an object")
    return errors


def _warnings(sidecar: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    items = sidecar.get("items") if isinstance(sidecar.get("items"), list) else []
    summary = sidecar.get("summary") if isinstance(sidecar.get("summary"), dict) else {}

    if items and all(not (item.get("mapped") or {}).get("has_item_type") for item in items):
        warnings.append("mapped.has_item_type is false for all items.")
    if any((item.get("context") or {}).get("requires_test_pairing") for item in items):
        warnings.append("One or more items require test-only pairing.")
    if (summary.get("raw_with_subtype_only") or 0) > 0:
        warnings.append("One or more raw records contain subtype_id without base_type_id.")
    if (summary.get(STATUS_UNRESOLVED) or 0) > 0:
        warnings.append("One or more records are unresolved.")
    if (summary.get(STATUS_NEEDS_CONTEXT) or 0) > 0:
        warnings.append("One or more records need base_type_id context.")
    if (summary.get(STATUS_NEEDS_REVIEW) or 0) > 0:
        warnings.append("One or more records need manual review.")

    source_values = " ".join(
        str(sidecar.get(key) or "")
        for key in ("source", "build_id", "fixture", "fixture_source")
    ).lower()
    if "synthetic" in source_values or "offline" in source_values:
        warnings.append("Sidecar source appears synthetic/offline.")
    return warnings


def _status_summary(sidecar: dict[str, Any]) -> dict[str, int]:
    items = sidecar.get("items") if isinstance(sidecar.get("items"), list) else []
    counts = {
        "total_items": len(items),
        STATUS_RESOLVED: 0,
        STATUS_NEEDS_CONTEXT: 0,
        STATUS_NEEDS_REVIEW: 0,
        STATUS_DEFERRED: 0,
        STATUS_UNRESOLVED: 0,
    }
    for item in items:
        resolver = item.get("resolver") if isinstance(item.get("resolver"), dict) else {}
        status = resolver.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def _format_messages(messages: list[str]) -> list[str]:
    if not messages:
        return ["- none"]
    return [f"- {message}" for message in messages]
