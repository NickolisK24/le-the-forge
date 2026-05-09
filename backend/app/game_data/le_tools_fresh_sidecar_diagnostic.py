"""Developer-only diagnostics for freshly built LE Tools sidecars."""

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
from app.game_data.le_tools_import_context_sidecar import build_sidecar_from_fixture
from app.game_data.le_tools_import_context_sidecar_validator import (
    load_sidecar,
    validate_sidecar_artifact,
)
from app.game_data.le_tools_import_stage_context_report import DEFAULT_STAGE_FIXTURE


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAVED_SIDECAR = BACKEND_ROOT / "tests" / "fixtures" / "le_tools_import_context_sidecar_current.json"
STATUS_KEYS = [
    STATUS_RESOLVED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_DEFERRED,
    STATUS_UNRESOLVED,
]
REQUIRED_TOP_LEVEL_KEYS = {"production_safe", "source", "importer", "build_id", "generated_at", "items", "summary"}
REQUIRED_ITEM_KEYS = {"index", "slot", "raw", "mapped", "resolver", "context"}
REQUIRED_RAW_KEYS = {"item_type", "base_type_id", "subtype_id", "name", "source_item_id"}
REQUIRED_MAPPED_KEYS = {"slot", "base_type_id", "subtype_id", "has_item_type", "mapped_item_id", "mapped_name"}
REQUIRED_RESOLVER_KEYS = {
    "status",
    "bundle_item_type_id",
    "match_source",
    "production_safe",
    "warnings",
    "notes",
}
REQUIRED_CONTEXT_KEYS = {
    "has_base_type_id",
    "has_subtype_id",
    "subtype_only",
    "has_raw_item_type_signal",
    "requires_test_pairing",
}


def build_fresh_sidecar_diagnostic(
    fixture_path: str | Path = DEFAULT_STAGE_FIXTURE,
    saved_sidecar_path: str | Path = DEFAULT_SAVED_SIDECAR,
) -> dict[str, Any]:
    """Build a fresh diagnostic sidecar and validate it against saved expectations."""

    fresh_sidecar, _mapped_gear = build_sidecar_from_fixture(fixture_path)
    saved_sidecar = load_sidecar(saved_sidecar_path)
    return diagnose_fresh_sidecar(
        fresh_sidecar,
        saved_sidecar=saved_sidecar,
        fixture_path=Path(fixture_path),
        saved_sidecar_path=Path(saved_sidecar_path),
    )


def diagnose_fresh_sidecar(
    sidecar: dict[str, Any],
    saved_sidecar: dict[str, Any] | None = None,
    fixture_path: str | Path | None = None,
    saved_sidecar_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return a serializable diagnostic report for a freshly built sidecar."""

    candidate = deepcopy(sidecar)
    validation = validate_sidecar_artifact(candidate)
    errors = list(validation["errors"])
    warnings = list(validation["warnings"])
    errors.extend(_shape_errors(candidate, saved_sidecar))
    warnings.extend(_metadata_warnings(candidate))

    records = [_record_diagnostic(item) for item in candidate.get("items", []) if isinstance(item, dict)]
    unsafe_records = [record for record in records if record["unsafe_reasons"]]
    missing_identity_records = [record for record in records if record["identity_classification"] == "missing"]
    ambiguous_records = [record for record in records if record["identity_classification"] == "ambiguous"]
    unresolved_records = [record for record in records if record["resolver_status"] == STATUS_UNRESOLVED]
    needs_context_records = [record for record in records if record["resolver_status"] == STATUS_NEEDS_CONTEXT]
    subtype_only_records = [record for record in records if record["context"].get("subtype_only")]
    name_only_records = [
        record
        for record in records
        if not record["context"].get("has_raw_item_type_signal")
        and record["raw"].get("name")
        and record["resolver_status"] != STATUS_RESOLVED
    ]

    if unsafe_records:
        errors.append("One or more fresh sidecar records are unsafe for diagnostic consumption.")
    if missing_identity_records:
        warnings.append("One or more fresh sidecar records are missing item type identity context.")
    if ambiguous_records:
        warnings.append("One or more fresh sidecar records require manual review.")
    if needs_context_records:
        warnings.append("One or more fresh sidecar records need base_type_id context.")
    if unresolved_records:
        warnings.append("One or more fresh sidecar records are unresolved.")
    if subtype_only_records:
        warnings.append("One or more fresh sidecar records contain subtype_id without base_type_id.")
    if name_only_records:
        warnings.append("One or more fresh sidecar records are name-only and remain blocked.")

    status = "failed" if errors else ("warning" if warnings else "passed")
    return {
        "status": status,
        "production_safe": False,
        "fixture_path": str(fixture_path) if fixture_path else None,
        "saved_sidecar_path": str(saved_sidecar_path) if saved_sidecar_path else None,
        "validation_status": validation["status"],
        "errors": _dedupe(errors),
        "warnings": _dedupe(warnings),
        "summary": {
            **validation["summary"],
            "missing_identity": len(missing_identity_records),
            "ambiguous": len(ambiguous_records),
            "unsafe": len(unsafe_records),
            "subtype_only": len(subtype_only_records),
            "name_only": len(name_only_records),
        },
        "shape": _shape_summary(candidate, saved_sidecar),
        "records": records,
        "missing_identity_records": missing_identity_records,
        "ambiguous_records": ambiguous_records,
        "unsafe_records": unsafe_records,
        "needs_context_records": needs_context_records,
        "unresolved_records": unresolved_records,
        "recommendations": _recommendations(
            missing_identity_records=missing_identity_records,
            ambiguous_records=ambiguous_records,
            unsafe_records=unsafe_records,
            needs_context_records=needs_context_records,
            unresolved_records=unresolved_records,
        ),
    }


def render_fresh_sidecar_diagnostic(report: dict[str, Any]) -> str:
    lines = [
        "# Fresh LE Tools Sidecar Diagnostic Validation Report",
        "",
        f"- status: {report['status']}",
        f"- validation_status: {report['validation_status']}",
        "- production_safe: false",
        f"- fixture_path: {report['fixture_path'] or 'null'}",
        f"- saved_sidecar_path: {report['saved_sidecar_path'] or 'null'}",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Shape", ""])
    for key, value in report["shape"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Errors", ""])
    lines.extend(_format_messages(report["errors"]))
    lines.extend(["", "## Warnings", ""])
    lines.extend(_format_messages(report["warnings"]))
    lines.extend(["", "## Missing / Ambiguous / Unsafe Records", ""])
    surfaced = report["missing_identity_records"] + report["ambiguous_records"] + report["unsafe_records"]
    if not surfaced:
        lines.append("- none")
    for record in surfaced:
        lines.append(
            "- index={index} slot={slot} raw_type={raw_type} status={status} identity={identity} "
            "reasons={reasons}".format(
                index=record["index"],
                slot=record["slot"] or "null",
                raw_type=record["raw"].get("item_type") or "null",
                status=record["resolver_status"],
                identity=record["identity_classification"],
                reasons=", ".join(record["unsafe_reasons"] or record["warnings"] or ["none"]),
            )
        )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(_format_messages(report["recommendations"]))
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- This validation is diagnostic-only and non-production.",
            "- It does not change importer output, loaders, API behavior, frontend behavior, or simulation.",
            "- production_safe remains false.",
            "- subtype_id-only identity and name-only matching remain blocked.",
            "",
        ]
    )
    return "\n".join(lines)


def fresh_sidecar_diagnostic_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def _record_diagnostic(item: dict[str, Any]) -> dict[str, Any]:
    raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
    mapped = item.get("mapped") if isinstance(item.get("mapped"), dict) else {}
    resolver = item.get("resolver") if isinstance(item.get("resolver"), dict) else {}
    context = item.get("context") if isinstance(item.get("context"), dict) else {}
    status = resolver.get("status")
    unsafe_reasons: list[str] = []
    warnings: list[str] = []

    has_base = raw.get("base_type_id") is not None or mapped.get("base_type_id") is not None
    has_subtype = raw.get("subtype_id") is not None or mapped.get("subtype_id") is not None
    has_item_type = raw.get("item_type") is not None

    if context.get("subtype_only") or (has_subtype and not has_base):
        warnings.append("subtype_id is present without base_type_id")
        if status == STATUS_RESOLVED:
            unsafe_reasons.append("subtype_id-only record resolved")
    if not has_item_type:
        warnings.append("missing raw item type signal")
    if not has_item_type and raw.get("name") and status == STATUS_RESOLVED:
        unsafe_reasons.append("name-only record resolved")
    if raw.get("item_type") == "spear" and status == STATUS_RESOLVED:
        unsafe_reasons.append("spear record resolved")
    if status == STATUS_NEEDS_REVIEW:
        warnings.append("manual review required")
    if status == STATUS_NEEDS_CONTEXT:
        warnings.append("base_type_id context required")
    if status == STATUS_UNRESOLVED:
        warnings.append("record unresolved")

    identity_classification = "safe"
    if unsafe_reasons:
        identity_classification = "unsafe"
    elif status == STATUS_NEEDS_REVIEW:
        identity_classification = "ambiguous"
    elif not has_item_type:
        identity_classification = "missing"
    elif status in {STATUS_NEEDS_CONTEXT, STATUS_UNRESOLVED}:
        identity_classification = "missing"

    return {
        "index": item.get("index"),
        "slot": item.get("slot"),
        "resolver_status": status,
        "bundle_item_type_id": resolver.get("bundle_item_type_id"),
        "match_source": resolver.get("match_source"),
        "production_safe": False,
        "raw": {
            "item_type": raw.get("item_type"),
            "base_type_id": raw.get("base_type_id"),
            "subtype_id": raw.get("subtype_id"),
            "name": raw.get("name"),
            "source_item_id": raw.get("source_item_id"),
        },
        "mapped": {
            "base_type_id": mapped.get("base_type_id"),
            "subtype_id": mapped.get("subtype_id"),
            "has_item_type": mapped.get("has_item_type"),
            "mapped_item_id": mapped.get("mapped_item_id"),
            "mapped_name": mapped.get("mapped_name"),
        },
        "context": {
            "has_base_type_id": bool(context.get("has_base_type_id")),
            "has_subtype_id": bool(context.get("has_subtype_id")),
            "subtype_only": bool(context.get("subtype_only")),
            "has_raw_item_type_signal": bool(context.get("has_raw_item_type_signal")),
            "requires_test_pairing": bool(context.get("requires_test_pairing")),
        },
        "identity_classification": identity_classification,
        "warnings": warnings,
        "unsafe_reasons": unsafe_reasons,
    }


def _shape_errors(sidecar: dict[str, Any], saved_sidecar: dict[str, Any] | None) -> list[str]:
    errors: list[str] = []
    missing_top = REQUIRED_TOP_LEVEL_KEYS - set(sidecar)
    if missing_top:
        errors.append(f"fresh sidecar missing top-level keys: {sorted(missing_top)}")

    for item in sidecar.get("items", []) if isinstance(sidecar.get("items"), list) else []:
        if not isinstance(item, dict):
            errors.append("fresh sidecar item must be an object")
            continue
        index = item.get("index")
        missing_item = REQUIRED_ITEM_KEYS - set(item)
        if missing_item:
            errors.append(f"item {index} missing keys: {sorted(missing_item)}")
        for section_name, required in (
            ("raw", REQUIRED_RAW_KEYS),
            ("mapped", REQUIRED_MAPPED_KEYS),
            ("resolver", REQUIRED_RESOLVER_KEYS),
            ("context", REQUIRED_CONTEXT_KEYS),
        ):
            section = item.get(section_name)
            if not isinstance(section, dict):
                continue
            missing = required - set(section)
            if missing:
                errors.append(f"item {index} {section_name} missing keys: {sorted(missing)}")

    if saved_sidecar:
        errors.extend(_saved_shape_mismatches(sidecar, saved_sidecar))
    return errors


def _saved_shape_mismatches(sidecar: dict[str, Any], saved_sidecar: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(sidecar.keys()) != set(saved_sidecar.keys()):
        errors.append("fresh sidecar top-level shape does not match saved sidecar keys")
    fresh_summary_keys = set((sidecar.get("summary") or {}).keys())
    saved_summary_keys = set((saved_sidecar.get("summary") or {}).keys())
    if fresh_summary_keys != saved_summary_keys:
        errors.append("fresh sidecar summary shape does not match saved sidecar summary keys")
    fresh_items = sidecar.get("items") if isinstance(sidecar.get("items"), list) else []
    saved_items = saved_sidecar.get("items") if isinstance(saved_sidecar.get("items"), list) else []
    if fresh_items and saved_items:
        for section in ("raw", "mapped", "resolver", "context"):
            fresh_keys = set((fresh_items[0].get(section) or {}).keys())
            saved_keys = set((saved_items[0].get(section) or {}).keys())
            if fresh_keys != saved_keys:
                errors.append(f"fresh sidecar {section} shape does not match saved sidecar")
    return errors


def _metadata_warnings(sidecar: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if sidecar.get("production_safe") is not False:
        warnings.append("fresh sidecar production_safe is not false")
    if not sidecar.get("source"):
        warnings.append("fresh sidecar source metadata is missing")
    if not sidecar.get("importer"):
        warnings.append("fresh sidecar importer metadata is missing")
    if not sidecar.get("build_id"):
        warnings.append("fresh sidecar build_id metadata is missing")
    if not sidecar.get("generated_at"):
        warnings.append("fresh sidecar generated_at metadata is missing")
    return warnings


def _shape_summary(sidecar: dict[str, Any], saved_sidecar: dict[str, Any] | None) -> dict[str, Any]:
    fresh_items = sidecar.get("items") if isinstance(sidecar.get("items"), list) else []
    saved_items = saved_sidecar.get("items") if saved_sidecar and isinstance(saved_sidecar.get("items"), list) else []
    return {
        "top_level_keys_match_saved": bool(saved_sidecar) and set(sidecar.keys()) == set(saved_sidecar.keys()),
        "summary_keys_match_saved": bool(saved_sidecar)
        and set((sidecar.get("summary") or {}).keys()) == set((saved_sidecar.get("summary") or {}).keys()),
        "item_count": len(fresh_items),
        "saved_item_count": len(saved_items),
        "item_sections_present": all(REQUIRED_ITEM_KEYS.issubset(item) for item in fresh_items if isinstance(item, dict)),
    }


def _recommendations(
    *,
    missing_identity_records: list[dict[str, Any]],
    ambiguous_records: list[dict[str, Any]],
    unsafe_records: list[dict[str, Any]],
    needs_context_records: list[dict[str, Any]],
    unresolved_records: list[dict[str, Any]],
) -> list[str]:
    recommendations = [
        "Keep this validation diagnostic-only and non-production.",
        "Do not consume freshly built sidecars in production.",
        "Keep production_safe=false.",
    ]
    if unsafe_records:
        recommendations.append("Block any consumer until unsafe records are fixed.")
    if missing_identity_records or needs_context_records:
        recommendations.append("Thread base_type_id and raw item type context before expanding consumers.")
    if ambiguous_records:
        recommendations.append("Manually review ambiguous records before adding adapter coverage.")
    if unresolved_records:
        recommendations.append("Keep unresolved records blocked; do not use name-only matching.")
    return recommendations


def _dedupe(messages: list[str]) -> list[str]:
    deduped: list[str] = []
    for message in messages:
        if message not in deduped:
            deduped.append(message)
    return deduped


def _format_messages(messages: list[str]) -> list[str]:
    if not messages:
        return ["- none"]
    return [f"- {message}" for message in messages]
