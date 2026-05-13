"""Generate read-only v2 stat and modifier normalization reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.normalization.v2.modifier_policy import (
    MODIFIER_OPERATIONS,
    VALUE_SCALE_STATUSES,
    classify_operation,
    classify_value_scale,
    is_stable_modifier_eligible,
    normalize_stat_id,
)

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs" / "generated"
MIGRATION = ROOT / "docs" / "migration"

DEFAULT_INPUTS = {
    "affix": GENERATED / "v2_affix_bundle.json",
    "item_implicit": GENERATED / "v2_item_implicit_bundle.json",
    "unique": GENERATED / "v2_unique_bundle.json",
    "set": GENERATED / "v2_set_bundle.json",
    "idol": GENERATED / "v2_idol_bundle.json",
    "idol_affix": GENERATED / "v2_idol_affix_bundle.json",
    "passive": GENERATED / "v2_passive_tree_bundle.json",
    "skill": GENERATED / "v2_skill_bundle.json",
    "skill_tree": GENERATED / "v2_skill_tree_bundle.json",
}

DEFAULT_SKILL_IDENTITY = GENERATED / "v2_skill_identity_alignment_report.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--affix-bundle", type=Path, default=DEFAULT_INPUTS["affix"])
    parser.add_argument("--item-implicit-bundle", type=Path, default=DEFAULT_INPUTS["item_implicit"])
    parser.add_argument("--unique-bundle", type=Path, default=DEFAULT_INPUTS["unique"])
    parser.add_argument("--set-bundle", type=Path, default=DEFAULT_INPUTS["set"])
    parser.add_argument("--idol-bundle", type=Path, default=DEFAULT_INPUTS["idol"])
    parser.add_argument("--idol-affix-bundle", type=Path, default=DEFAULT_INPUTS["idol_affix"])
    parser.add_argument("--passive-tree-bundle", type=Path, default=DEFAULT_INPUTS["passive"])
    parser.add_argument("--skill-bundle", type=Path, default=DEFAULT_INPUTS["skill"])
    parser.add_argument("--skill-tree-bundle", type=Path, default=DEFAULT_INPUTS["skill_tree"])
    parser.add_argument("--skill-identity-report", type=Path, default=DEFAULT_SKILL_IDENTITY)
    parser.add_argument("--stat-output", type=Path, default=GENERATED / "v2_stat_registry.json")
    parser.add_argument("--modifier-output", type=Path, default=GENERATED / "v2_modifier_registry.json")
    parser.add_argument("--validation-output", type=Path, default=GENERATED / "v2_modifier_validation_report.json")
    parser.add_argument("--blocked-reasons-output", type=Path, default=GENERATED / "v2_modifier_blocked_reasons_report.json")
    parser.add_argument("--markdown-output", type=Path, default=MIGRATION / "V2_STAT_MODIFIER_NORMALIZATION.md")
    args = parser.parse_args()

    payloads = {
        "affix": _read_json(args.affix_bundle),
        "item_implicit": _read_json(args.item_implicit_bundle),
        "unique": _read_json(args.unique_bundle),
        "set": _read_json(args.set_bundle),
        "idol": _read_json(args.idol_bundle),
        "idol_affix": _read_json(args.idol_affix_bundle),
        "passive": _read_json(args.passive_tree_bundle),
        "skill": _read_json(args.skill_bundle),
        "skill_tree": _read_json(args.skill_tree_bundle),
    }
    skill_identity = _read_json(args.skill_identity_report) if args.skill_identity_report.exists() else {}
    reports = build_v2_stat_modifier_reports(payloads, skill_identity)

    _write_json(args.stat_output, reports["stat_registry"])
    _write_json(args.modifier_output, reports["modifier_registry"])
    _write_json(args.validation_output, reports["validation_report"])
    _write_json(args.blocked_reasons_output, reports["blocked_reasons_report"])
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown_report(reports), encoding="utf-8")
    return 0


def build_v2_stat_modifier_reports(payloads: dict[str, dict[str, Any]], skill_identity: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    generated_on = datetime.now(UTC).isoformat()
    identity_summary = _skill_identity_summary(skill_identity or {})
    modifiers = list(_collect_modifier_records(payloads, identity_summary))
    stats = _build_stat_records(modifiers, generated_on)
    validation = validate_modifier_records(modifiers, stats, identity_summary, generated_on)
    blocked = _build_blocked_reasons_report(modifiers, generated_on)

    modifier_registry = {
        "schema_version": "v2.modifier_registry.1",
        "generated_on": generated_on,
        "metadata": _metadata("v2_stat_modifier_normalization"),
        "summary": {
            "modifier_count": len(modifiers),
            "stat_count": len(stats),
            "stable_calculable_count": sum(1 for row in modifiers if row["stable_calculable"]),
            "source_type_counts": dict(sorted(Counter(row["source_type"] for row in modifiers).items())),
            "operation_counts": dict(sorted(Counter(row["operation"] for row in modifiers).items())),
            "value_scale_status_counts": dict(sorted(Counter(row["value_scale_status"] for row in modifiers).items())),
            "blocked_reason_counts": blocked["summary"]["blocked_reason_counts"],
            "unresolved_skill_reference_count": identity_summary["unresolved_reference_count"],
            "ambiguous_skill_reference_count": identity_summary["ambiguous_reference_count"],
            "production_consumed": False,
        },
        "records": {"modifiers": modifiers},
    }
    stat_registry = {
        "schema_version": "v2.stat_registry.1",
        "generated_on": generated_on,
        "metadata": _metadata("v2_stat_modifier_normalization"),
        "summary": {
            "stat_count": len(stats),
            "modifier_count": len(modifiers),
            "source_category_counts": _stat_source_counts(stats),
            "support_status_counts": dict(sorted(Counter(row["support_status"] for row in stats).items())),
            "trust_level_counts": dict(sorted(Counter(row["trust_level"] for row in stats).items())),
            "production_consumed": False,
        },
        "records": {"stats": stats},
    }
    return {
        "stat_registry": stat_registry,
        "modifier_registry": modifier_registry,
        "validation_report": validation,
        "blocked_reasons_report": blocked,
    }


def validate_modifier_records(
    modifiers: list[dict[str, Any]],
    stats: list[dict[str, Any]],
    identity_summary: dict[str, Any],
    generated_on: str | None = None,
) -> dict[str, Any]:
    stat_ids = {row["canonical_stat_id"] for row in stats}
    seen: set[str] = set()
    summary = Counter()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for index, row in enumerate(modifiers):
        modifier_id = row.get("canonical_modifier_id")
        if not modifier_id:
            _error(errors, summary, row, "missing_canonical_modifier_id", index)
        elif modifier_id in seen:
            _error(errors, summary, row, "duplicate_canonical_modifier_id", index)
        else:
            seen.add(str(modifier_id))
        for field, code in (
            ("source_type", "missing_source_type"),
            ("source_id", "missing_source_id"),
            ("stat_id", "missing_stat_id"),
            ("operation", "missing_operation"),
            ("value_scale_status", "missing_value_scale_status"),
            ("support_status", "missing_support_status"),
            ("trust_level", "missing_trust_level"),
        ):
            if not row.get(field):
                _error(errors, summary, row, code, index)
        if row.get("stat_id") not in stat_ids:
            _error(errors, summary, row, "stat_id_not_in_registry", index)
        if row.get("operation") not in MODIFIER_OPERATIONS:
            _error(errors, summary, row, "invalid_operation", index)
        if row.get("value_scale_status") not in VALUE_SCALE_STATUSES:
            _error(errors, summary, row, "invalid_value_scale_status", index)
        if not isinstance(row.get("provenance"), dict) or not row.get("provenance"):
            _error(errors, summary, row, "missing_provenance", index)
        if row.get("stable_calculable") is True:
            stable, reasons = is_stable_modifier_eligible(row)
            if not stable:
                _error(errors, summary, row, "unsafe_stable_calculable_modifier", index, reasons=reasons)
        if row.get("source_identity_status") in {"ambiguous", "unresolved"}:
            _warning(warnings, summary, row, "source_identity_gap_blocks_stability", index)
    return {
        "schema_version": "v2.modifier_validation_report.1",
        "generated_on": generated_on or datetime.now(UTC).isoformat(),
        "metadata": _metadata("v2_stat_modifier_normalization"),
        "summary": {
            "modifier_count": len(modifiers),
            "stat_count": len(stats),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "stable_calculable_count": sum(1 for row in modifiers if row.get("stable_calculable") is True),
            "missing_canonical_modifier_id_count": summary["missing_canonical_modifier_id"],
            "duplicate_canonical_modifier_id_count": summary["duplicate_canonical_modifier_id"],
            "missing_source_type_count": summary["missing_source_type"],
            "missing_source_id_count": summary["missing_source_id"],
            "missing_stat_id_count": summary["missing_stat_id"],
            "missing_operation_count": summary["missing_operation"],
            "invalid_operation_count": summary["invalid_operation"],
            "missing_value_scale_status_count": summary["missing_value_scale_status"],
            "invalid_value_scale_status_count": summary["invalid_value_scale_status"],
            "missing_provenance_count": summary["missing_provenance"],
            "missing_support_status_count": summary["missing_support_status"],
            "invalid_trust_level_count": summary["invalid_trust_level"],
            "unsafe_stable_calculable_modifier_count": summary["unsafe_stable_calculable_modifier"],
            "source_identity_gap_warning_count": summary["source_identity_gap_blocks_stability"],
            "unresolved_skill_reference_count": identity_summary["unresolved_reference_count"],
            "ambiguous_skill_reference_count": identity_summary["ambiguous_reference_count"],
            "production_consumed": False,
        },
        "errors": errors,
        "warnings": warnings,
    }


def _collect_modifier_records(payloads: dict[str, dict[str, Any]], identity_summary: dict[str, Any]) -> Iterable[dict[str, Any]]:
    yield from _collect_affix_modifiers(payloads.get("affix", {}), "affix")
    yield from _collect_row_modifiers(payloads.get("item_implicit", {}), "item_implicit", ["records", "implicits"])
    yield from _collect_row_modifiers(payloads.get("unique", {}), "unique_modifier", ["records", "uniques"])
    yield from _collect_row_modifiers(payloads.get("set", {}), "set_item_modifier", ["records", "set_items"])
    yield from _collect_row_modifiers(payloads.get("set", {}), "set_bonus_modifier", ["records", "set_bonuses"])
    yield from _collect_row_modifiers(payloads.get("idol", {}), "idol_modifier", ["records", "idols"])
    yield from _collect_row_modifiers(payloads.get("idol_affix", {}), "idol_affix_modifier", ["records", "idol_affixes"])
    yield from _collect_row_modifiers(payloads.get("passive", {}), "passive_node_modifier", ["records", "passive_nodes"])
    yield from _collect_skill_structured_modifiers(payloads.get("skill", {}), identity_summary)
    yield from _collect_row_modifiers(payloads.get("skill_tree", {}), "skill_node_modifier", ["records", "skill_nodes"], identity_summary=identity_summary)


def _collect_affix_modifiers(payload: dict[str, Any], source_type: str) -> Iterable[dict[str, Any]]:
    for source in _records_at(payload, ["records", "affixes"]):
        refs = source.get("modifier_references") or []
        tier_ranges = source.get("tier_ranges") or []
        raw_min = _min_numeric(row.get("min_value") for row in tier_ranges)
        raw_max = _max_numeric(row.get("max_value") for row in tier_ranges)
        value_scale = _value_scale_from_tiers(tier_ranges)
        for index, row in enumerate(refs):
            row = dict(row)
            row["value_min"] = raw_min
            row["value_max"] = raw_max
            row["value_scale"] = value_scale
            row.setdefault("provenance", source.get("provenance"))
            yield _normalize_modifier_row(source, row, source_type, index)


def _collect_row_modifiers(
    payload: dict[str, Any],
    source_type: str,
    path: list[str],
    *,
    identity_summary: dict[str, Any] | None = None,
) -> Iterable[dict[str, Any]]:
    for source in _records_at(payload, path):
        rows = source.get("modifier_rows") or []
        for index, row in enumerate(rows):
            yield _normalize_modifier_row(source, row, source_type, index, identity_summary=identity_summary)


def _collect_skill_structured_modifiers(payload: dict[str, Any], identity_summary: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for source in _records_at(payload, ["records", "skills"]):
        for field, operation in (("cost", "cost"), ("cooldown", "cooldown"), ("cast_data", "duration")):
            value = source.get(field)
            if not isinstance(value, dict):
                continue
            for key, raw_value in value.items():
                if not isinstance(raw_value, (int, float)) or raw_value == 0:
                    continue
                row = {
                    "modifier_id": f"{source.get('canonical_id')}:{field}:{key}",
                    "modifier_type": operation.upper(),
                    "property": key,
                    "property_path": f"{operation.upper()}.{field}.{key}",
                    "value_min": raw_value,
                    "value_max": raw_value,
                    "value_scale": "source_units",
                    "provenance": source.get("provenance"),
                    "support_status": source.get("support_status"),
                    "trust_level": source.get("trust_level"),
                    "stable_calculable": False,
                }
                yield _normalize_modifier_row(source, row, "skill_structured_value", 0, identity_summary=identity_summary)


def _normalize_modifier_row(
    source: dict[str, Any],
    row: dict[str, Any],
    source_type: str,
    index: int,
    *,
    identity_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_stat = row.get("property_path") or row.get("resolved_property_key") or row.get("property") or row.get("stat_name") or row.get("statName")
    stat_id = normalize_stat_id(raw_stat)
    operation = classify_operation(modifier_type=row.get("modifier_type"), property_path=row.get("property_path"), stat_label=raw_stat)
    source_id = str(source.get("canonical_id") or source.get("source_id") or "unknown")
    row_id = str(row.get("modifier_id") or row.get("row_id") or f"{source_id}:modifier:{index}")
    canonical_modifier_id = _canonical_modifier_id(source_type, source_id, row_id, index)
    value_scale_status = classify_value_scale(row)
    source_status = str(source.get("support_status") or row.get("support_status") or "unknown")
    trust_level = str(source.get("trust_level") or row.get("trust_level") or "unknown")
    source_identity_status = _source_identity_status(source, source_type, identity_summary or {})
    record = {
        "canonical_modifier_id": canonical_modifier_id,
        "source_type": source_type,
        "source_id": source_id,
        "source_display_name": source.get("display_name"),
        "stat_id": stat_id,
        "raw_stat_id": row.get("property") or row.get("property_path") or row.get("property_id") or row.get("property"),
        "raw_stat_name": row.get("stat_name") or row.get("statName") or row.get("property") or row.get("property_path"),
        "operation": operation,
        "raw_operation": row.get("modifier_type"),
        "raw_value_min": _coerce_number(row.get("value_min", row.get("min_value", row.get("value")))),
        "raw_value_max": _coerce_number(row.get("value_max", row.get("max_value", row.get("value")))),
        "normalized_value_min": None,
        "normalized_value_max": None,
        "value_scale_status": value_scale_status,
        "polarity": _polarity(row),
        "tags": sorted(str(tag) for tag in row.get("tags") or []),
        "conditions": {
            "source_special_behavior_classification": source.get("special_behavior_classification"),
            "source_identity_status": source_identity_status,
        },
        "support_status": source_status,
        "trust_level": trust_level,
        "source_record_status": source_status if source_status in {"text_only", "unsupported", "experimental", "unknown"} else "modifier_row",
        "special_behavior_classification": source.get("special_behavior_classification"),
        "source_identity_status": source_identity_status,
        "stable_calculable": False,
        "reason_not_stable_calculable": [],
        "provenance": row.get("provenance") or source.get("provenance") or {},
        "warnings": list(source.get("warnings") or []) + list(row.get("warnings") or []),
    }
    stable, reasons = is_stable_modifier_eligible(record)
    record["stable_calculable"] = stable
    record["reason_not_stable_calculable"] = reasons
    return record


def _build_stat_records(modifiers: list[dict[str, Any]], generated_on: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in modifiers:
        grouped[row["stat_id"]].append(row)
    stats: list[dict[str, Any]] = []
    for stat_id, rows in sorted(grouped.items()):
        raw_names = sorted({str(row.get("raw_stat_name") or row.get("raw_stat_id") or "unknown") for row in rows})
        source_types = sorted({str(row["source_type"]) for row in rows})
        stats.append(
            {
                "canonical_stat_id": stat_id,
                "display_name": raw_names[0] if raw_names else stat_id,
                "source_stat_ids": sorted({str(row.get("raw_stat_id")) for row in rows if row.get("raw_stat_id") is not None}),
                "raw_names": raw_names,
                "source_categories": source_types,
                "first_seen_source": source_types[0] if source_types else "unknown",
                "modifier_count": len(rows),
                "support_status": _combined_support_status(rows),
                "trust_level": _combined_trust_level(rows),
                "warnings": sorted({warning for row in rows for warning in row.get("warnings", [])}),
                "provenance": {
                    "extraction_method": "v2_stat_modifier_normalization",
                    "notes": ["Collected from generated v2 modifier-like rows; values remain source-preserved unless explicitly planner-normalized."],
                    "schema_version": "v2.stat_registry.1",
                    "source_id": stat_id,
                    "source_path": "docs/generated/v2_*_bundle.json",
                    "source_type": "v2_stat_registry",
                    "generated_on": generated_on,
                },
            }
        )
    return stats


def _build_blocked_reasons_report(modifiers: list[dict[str, Any]], generated_on: str) -> dict[str, Any]:
    reason_counts = Counter(reason for row in modifiers for reason in row.get("reason_not_stable_calculable", []))
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in modifiers:
        for reason in row.get("reason_not_stable_calculable", []):
            if len(examples[reason]) < 10:
                examples[reason].append(
                    {
                        "canonical_modifier_id": row["canonical_modifier_id"],
                        "source_type": row["source_type"],
                        "source_id": row["source_id"],
                        "stat_id": row["stat_id"],
                        "operation": row["operation"],
                    }
                )
    return {
        "schema_version": "v2.modifier_blocked_reasons_report.1",
        "generated_on": generated_on,
        "metadata": _metadata("v2_stat_modifier_normalization"),
        "summary": {
            "modifier_count": len(modifiers),
            "blocked_modifier_count": sum(1 for row in modifiers if row.get("reason_not_stable_calculable")),
            "blocked_reason_counts": dict(sorted(reason_counts.items())),
            "production_consumed": False,
        },
        "examples": dict(sorted(examples.items())),
    }


def _markdown_report(reports: dict[str, dict[str, Any]]) -> str:
    modifier_summary = reports["modifier_registry"]["summary"]
    stat_summary = reports["stat_registry"]["summary"]
    validation_summary = reports["validation_report"]["summary"]
    blocked_counts = modifier_summary["blocked_reason_counts"]
    top_blocked = sorted(blocked_counts.items(), key=lambda item: item[1], reverse=True)[:10]
    lines = [
        "# V2 Stat and Modifier Normalization",
        "",
        "## Purpose",
        "",
        "This report defines the read-only Phase 10 normalization layer for stat-like identifiers and modifier-like rows across generated v2 data bundles. It does not remap planner, crafting, stat aggregation, or simulation behavior.",
        "",
        "## Generation command",
        "",
        "```powershell",
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_stat_modifier_normalization.py --stat-output docs\\generated\\v2_stat_registry.json --modifier-output docs\\generated\\v2_modifier_registry.json --validation-output docs\\generated\\v2_modifier_validation_report.json --blocked-reasons-output docs\\generated\\v2_modifier_blocked_reasons_report.json --markdown-output docs\\migration\\V2_STAT_MODIFIER_NORMALIZATION.md",
        "```",
        "",
        "## Summary",
        "",
        f"- Stat registry entries: `{stat_summary['stat_count']}`",
        f"- Modifier registry entries: `{modifier_summary['modifier_count']}`",
        f"- Stable-calculable modifiers: `{modifier_summary['stable_calculable_count']}`",
        f"- Validation errors: `{validation_summary['error_count']}`",
        f"- Validation warnings: `{validation_summary['warning_count']}`",
        f"- Unresolved skill references retained as identity gaps: `{modifier_summary['unresolved_skill_reference_count']}`",
        f"- Ambiguous skill references retained as identity gaps: `{modifier_summary['ambiguous_skill_reference_count']}`",
        "",
        "## Value Scale Policy",
        "",
        "Planner-safe value normalization is not inferred in this phase. Source values are preserved as `source_units` unless a source row already proves planner-normalized values. `source_units` and `unknown` value scales are display/debug-only and block stable planner eligibility.",
        "",
        "## Operation Breakdown",
        "",
    ]
    for operation, count in modifier_summary["operation_counts"].items():
        lines.append(f"- `{operation}`: `{count}`")
    lines.extend(["", "## Value Scale Breakdown", ""])
    for status, count in modifier_summary["value_scale_status_counts"].items():
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(["", "## Top Blocked Reasons", ""])
    for reason, count in top_blocked:
        lines.append(f"- `{reason}`: `{count}`")
    lines.extend(
        [
            "",
            "## Skill Identity Handling",
            "",
            "Phase 10 preserves the Phase 9.5 identity result. Safely resolved class/mastery skill identity can be reported, but unresolved and ambiguous class/mastery skill references remain blocked from stable planner eligibility. No bridge is inferred from display names or nested evidence.",
            "",
            "## Migration Implications",
            "",
            "The modifier registry is suitable for debugging, review, and policy development. It is not a planner input yet because value scale normalization remains unresolved and most source records are still partial, scripted, unsupported, or text-only.",
            "",
            "## Recommended Next Step",
            "",
            "Define a value normalization policy for the most common source-unit modifier families before any test-only planner adapter consumes normalized rows.",
        ]
    )
    return "\n".join(lines) + "\n"


def _records_at(payload: dict[str, Any], path: list[str]) -> list[dict[str, Any]]:
    node: Any = payload
    for key in path:
        if not isinstance(node, dict):
            return []
        node = node.get(key)
    return node if isinstance(node, list) else []


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _metadata(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "read_only": True,
        "experimental": True,
        "production_safe": False,
        "production_consumed": False,
        "stable_planner_consumed": False,
    }


def _skill_identity_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary") if isinstance(report, dict) else {}
    return {
        "resolved_reference_count": int(summary.get("top_level_path_match_count") or summary.get("resolved_reference_count") or 0),
        "unresolved_reference_count": int(summary.get("unresolved_reference_count") or 0),
        "ambiguous_reference_count": int(summary.get("ambiguous_match_count") or summary.get("ambiguous_reference_count") or 0),
    }


def _source_identity_status(source: dict[str, Any], source_type: str, identity_summary: dict[str, Any]) -> str:
    if source_type not in {"skill_structured_value", "skill_node_modifier"}:
        return "not_applicable"
    if identity_summary.get("unresolved_reference_count", 0) or identity_summary.get("ambiguous_reference_count", 0):
        return "partially_unresolved"
    return "resolved"


def _canonical_modifier_id(source_type: str, source_id: str, row_id: str, index: int) -> str:
    raw = "|".join(str(part) for part in (source_type, source_id, row_id, index))
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return "modifier:" + ":".join(_slug(part) for part in (source_type, source_id, row_id, str(index), digest) if part)


def _slug(value: Any) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_") or "unknown"


def _min_numeric(values: Iterable[Any]) -> float | None:
    numbers = [_coerce_number(value) for value in values]
    numbers = [value for value in numbers if value is not None]
    return min(numbers) if numbers else None


def _max_numeric(values: Iterable[Any]) -> float | None:
    numbers = [_coerce_number(value) for value in values]
    numbers = [value for value in numbers if value is not None]
    return max(numbers) if numbers else None


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace("%", "")
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _value_scale_from_tiers(tiers: list[dict[str, Any]]) -> str:
    scales = {str(tier.get("value_scale")) for tier in tiers if tier.get("value_scale")}
    if len(scales) == 1 and next(iter(scales)) in VALUE_SCALE_STATUSES:
        return next(iter(scales))
    return "unknown" if not scales else "source_units"


def _polarity(row: dict[str, Any]) -> str:
    if row.get("polarity"):
        return str(row["polarity"])
    values = [_coerce_number(row.get("value_min", row.get("min_value", row.get("value")))), _coerce_number(row.get("value_max", row.get("max_value", row.get("value"))))]
    values = [value for value in values if value is not None]
    if not values:
        return "unknown"
    if all(value >= 0 for value in values):
        return "positive"
    if all(value <= 0 for value in values):
        return "negative"
    return "mixed"


def _combined_support_status(rows: list[dict[str, Any]]) -> str:
    statuses = {row.get("support_status") for row in rows}
    if statuses == {"trusted"}:
        return "trusted"
    if "partial" in statuses:
        return "partial"
    return sorted(str(status or "unknown") for status in statuses)[0]


def _combined_trust_level(rows: list[dict[str, Any]]) -> str:
    levels = {row.get("trust_level") for row in rows}
    if levels == {"game_extracted"}:
        return "game_extracted"
    if "generated_from_game_data" in levels:
        return "generated_from_game_data"
    return sorted(str(level or "unknown") for level in levels)[0]


def _stat_source_counts(stats: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for stat in stats:
        for source in stat["source_categories"]:
            counts[source] += 1
    return dict(sorted(counts.items()))


def _error(errors: list[dict[str, Any]], summary: Counter, row: dict[str, Any], code: str, index: int, *, reasons: list[str] | None = None) -> None:
    summary[code] += 1
    errors.append({"code": code, "index": index, "canonical_modifier_id": row.get("canonical_modifier_id"), "reasons": reasons or []})


def _warning(warnings: list[dict[str, Any]], summary: Counter, row: dict[str, Any], code: str, index: int) -> None:
    summary[code] += 1
    warnings.append({"code": code, "index": index, "canonical_modifier_id": row.get("canonical_modifier_id")})


if __name__ == "__main__":
    raise SystemExit(main())
