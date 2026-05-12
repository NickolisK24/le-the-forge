"""Generate the v2 canonical affix bundle and validation report."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id
from app.repositories.v2.affix_repository import V2AffixBundleError, V2AffixRepository
from data.loaders.forge_safe_affix_bundle_loader import ForgeSafeAffixBundleLoader


DEFAULT_SOURCE_BUNDLE = Path(
    r"D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json"
)
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "v2_affix_bundle.json"
DEFAULT_VALIDATION_OUTPUT = ROOT / "docs" / "generated" / "v2_affix_validation_report.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_AFFIX_MIGRATION.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the v2 canonical affix bundle.")
    parser.add_argument("--source-bundle", type=Path, default=DEFAULT_SOURCE_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validation-output", type=Path, default=DEFAULT_VALIDATION_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def build_v2_affix_bundle(source_bundle: Path) -> dict[str, Any]:
    loaded = ForgeSafeAffixBundleLoader().load(source_bundle)
    modifier_index = loaded.modifiers_by_affix_identity
    affixes = [
        _canonical_affix(record, modifier_index.get(_source_affix_identity(record), ()))
        for record in loaded.affixes
    ]
    validation = validate_v2_affix_records(affixes)
    summary = _summary(affixes, loaded.summary, validation)
    return {
        "schema_version": "v2.affix_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_bundle_path": str(source_bundle),
        "source_schema_version": loaded.schema_version,
        "source_export_policy": loaded.export_policy,
        "summary": summary,
        "validation_summary": validation["summary"],
        "records": {
            "affixes": affixes,
        },
        "metadata": {
            "phase": "phase_3_affix_infrastructure",
            "read_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "uses_canonical_contracts": True,
            "stable_planner_consumed": False,
        },
    }


def validate_v2_affix_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    seen: set[str] = set()
    equipment_count = 0
    idol_count = 0
    stable_calculable_count = 0
    for index, record in enumerate(records):
        canonical_id = record.get("canonical_id")
        context = {"index": index, "canonical_id": canonical_id}
        try:
            validate_canonical_id(canonical_id)
        except ValueError as exc:
            errors.append({**context, "code": "invalid_canonical_id", "message": str(exc)})
            continue
        if canonical_id in seen:
            errors.append({**context, "code": "duplicate_canonical_id", "message": "Duplicate canonical ID."})
        seen.add(canonical_id)
        if not record.get("provenance"):
            errors.append({**context, "code": "missing_provenance", "message": "Provenance is required."})
        if not record.get("support_status"):
            errors.append({**context, "code": "missing_support_status", "message": "Support status is required."})
        else:
            try:
                SupportStatus(str(record["support_status"]))
            except ValueError:
                errors.append({**context, "code": "invalid_support_status", "message": "Support status is invalid."})
        try:
            TrustLevel(str(record.get("trust_level")))
        except ValueError:
            errors.append({**context, "code": "invalid_trust_level", "message": "Trust level is invalid."})
        if not isinstance(record.get("tier_ranges"), list) or not record.get("tier_ranges"):
            errors.append({**context, "code": "missing_tier_ranges", "message": "Tier ranges are required."})
        if not isinstance(record.get("slot_restrictions"), list):
            errors.append({**context, "code": "invalid_slot_restrictions", "message": "Slot restrictions must be a list."})
        if not isinstance(record.get("item_type_restrictions"), list):
            errors.append({**context, "code": "invalid_item_type_restrictions", "message": "Item type restrictions must be a list."})
        if record.get("stable_calculable") is True:
            stable_calculable_count += 1
            if record.get("support_status") != SupportStatus.TRUSTED.value:
                errors.append({**context, "code": "unsupported_stable_calculation", "message": "Only trusted records may be stable-calculable."})
        if record.get("affix_domain") == "equipment":
            equipment_count += 1
            if str(record.get("source_type")).lower() == "idol":
                errors.append({**context, "code": "mixed_equipment_idol_domain", "message": "Equipment domain cannot use idol source type."})
        elif record.get("affix_domain") == "idol":
            idol_count += 1
        else:
            warnings.append({**context, "code": "unknown_affix_domain", "message": "Affix domain could not be classified."})
        if record.get("support_status") in {SupportStatus.UNKNOWN.value, SupportStatus.UNSUPPORTED.value}:
            warnings.append({**context, "code": "non_calculable_record", "message": "Record is displayable but not stable-calculable."})

    return {
        "summary": {
            "record_count": len(records),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "duplicate_canonical_id_count": _count_code(errors, "duplicate_canonical_id"),
            "missing_provenance_count": _count_code(errors, "missing_provenance"),
            "missing_support_status_count": _count_code(errors, "missing_support_status"),
            "invalid_trust_level_count": _count_code(errors, "invalid_trust_level"),
            "invalid_tier_data_count": _count_code(errors, "missing_tier_ranges"),
            "invalid_slot_restriction_shape_count": _count_code(errors, "invalid_slot_restrictions"),
            "stable_calculable_blocked_count": _count_code(errors, "unsupported_stable_calculation"),
            "stable_calculable_count": stable_calculable_count,
            "equipment_affix_count": equipment_count,
            "idol_affix_count": idol_count,
            "production_consumed": False,
        },
        "errors": errors,
        "warnings": warnings,
        "metadata": {
            "read_only": True,
            "experimental": True,
            "production_safe": False,
            "stable_planner_consumed": False,
        },
    }


def _canonical_affix(
    record: dict[str, Any],
    modifiers: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    source_identity = _source_affix_identity(record)
    canonical_id = _canonical_id(source_identity, record)
    categories = [str(value) for value in record.get("categories") or []]
    source_type = str(record.get("source_type") or "unknown")
    domain = _affix_domain(record)
    tier_ranges = [_tier_range(tier) for tier in record.get("tier_data") or []]
    modifier_references = [_modifier_reference(modifier) for modifier in modifiers]
    warnings = _warnings(record, tier_ranges, modifier_references)
    item_values = [str(value) for value in record.get("eligible_item_types") or []]
    return {
        "canonical_id": canonical_id,
        "display_name": record.get("display_name") or record.get("affix_name") or canonical_id,
        "source_id": source_identity,
        "source_affix_id": record.get("affix_id"),
        "source_file": _provenance(record).get("source_path"),
        "patch_version": None,
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": {
            "source_path": _provenance(record).get("source_path"),
            "source_type": source_type,
            "source_id": source_identity,
            "extraction_method": "forge_safe_affix_bundle",
            "schema_version": "v2.affix_bundle.1",
            "notes": [
                "Source tier values are preserved without planner value-scale normalization.",
            ],
            "raw_reference": {
                "source_affix_identity": source_identity,
                "affix_id": record.get("affix_id"),
            },
        },
        "source_type": source_type,
        "affix_domain": domain,
        "affix_type": _affix_type(categories),
        "prefix_suffix": _prefix_suffix(categories),
        "categories": categories,
        "tags": [str(value) for value in record.get("tags") or []],
        "item_applicability": item_values,
        "slot_restrictions": item_values,
        "item_type_restrictions": item_values,
        "class_restrictions": [],
        "mastery_restrictions": [],
        "tier_ranges": tier_ranges,
        "tier_count": len(tier_ranges),
        "modifier_references": modifier_references,
        "modifier_reference_count": len(modifier_references),
        "value_scale_policy": "source_units_preserved_pending_v2_value_normalization",
        "polarity_policy": "source_sign_preserved_no_inference",
        "stable_calculable": False,
        "warnings": warnings,
        "raw_reference": _raw_reference_summary(record, modifiers, source_identity),
        "normalized_fields": {
            "tier_ranges": tier_ranges,
            "modifier_references": modifier_references,
        },
        "consumer_safe_fields": {
            "display_name": record.get("display_name") or record.get("affix_name") or canonical_id,
            "support_status": SupportStatus.PARTIAL.value,
            "stable_calculable": False,
            "slot_restrictions": item_values,
        },
    }


def _summary(
    affixes: list[dict[str, Any]],
    source_summary: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    status_counts = Counter(record["support_status"] for record in affixes)
    domain_counts = Counter(record["affix_domain"] for record in affixes)
    prefix_counts = Counter(record["prefix_suffix"] or "unknown" for record in affixes)
    modifier_counts = Counter(str(record["modifier_reference_count"]) for record in affixes)
    return {
        "affix_count": len(affixes),
        "support_status_counts": dict(sorted(status_counts.items())),
        "trust_level_counts": dict(sorted(Counter(record["trust_level"] for record in affixes).items())),
        "affix_domain_counts": dict(sorted(domain_counts.items())),
        "prefix_suffix_counts": dict(sorted(prefix_counts.items())),
        "modifier_reference_count_distribution": dict(sorted(modifier_counts.items())),
        "stable_calculable_count": sum(1 for record in affixes if record["stable_calculable"]),
        "records_with_warnings_count": sum(1 for record in affixes if record["warnings"]),
        "source_affix_count": source_summary.get("affix_count"),
        "source_modifier_count": source_summary.get("modifier_count"),
        "validation_error_count": validation["summary"]["error_count"],
        "validation_warning_count": validation["summary"]["warning_count"],
        "production_consumed": False,
    }


def render_markdown(
    bundle: dict[str, Any],
    validation: dict[str, Any],
    *,
    command: str,
) -> str:
    summary = bundle["summary"]
    status_rows = _count_rows(summary["support_status_counts"])
    domain_rows = _count_rows(summary["affix_domain_counts"])
    prefix_rows = _count_rows(summary["prefix_suffix_counts"])
    modifier_rows = _count_rows(summary["modifier_reference_count_distribution"])
    examples = "\n".join(
        f"| `{record['canonical_id']}` | {record['display_name']} | {record['affix_domain']} | {record['prefix_suffix'] or 'unknown'} | {record['modifier_reference_count']} |"
        for record in bundle["records"]["affixes"][:20]
    )
    return f"""# v2 Affix Migration

## Purpose

Phase 3 creates a read-only canonical affix bundle on top of the v2 data contracts. The bundle preserves deterministic Forge-safe affix/modifier relationships and exposes validation diagnostics for later repository, API, debug, and planner work.

This phase does not remap planner, crafting, stat aggregation, simulation, item, passive, skill, idol, unique, or set behavior.

## Generation Command

```powershell
{command}
```

## Summary

- Affix count: {summary["affix_count"]}
- Stable-calculable count: {summary["stable_calculable_count"]}
- Records with warnings: {summary["records_with_warnings_count"]}
- Validation errors: {validation["summary"]["error_count"]}
- Validation warnings: {validation["summary"]["warning_count"]}
- Production consumed: false

## Support Status Counts

| Support status | Count |
| --- | ---: |
{status_rows}

## Affix Domain Counts

| Domain | Count |
| --- | ---: |
{domain_rows}

## Prefix/Suffix Counts

| Classification | Count |
| --- | ---: |
{prefix_rows}

## Modifier Reference Count Distribution

| Modifier references | Affix count |
| --- | ---: |
{modifier_rows}

## Example Canonical Affixes

| Canonical ID | Display name | Domain | Prefix/suffix | Modifier references |
| --- | --- | --- | --- | ---: |
{examples}

## Value and Polarity Policy

Tier values are preserved in source units. No planner value-scale normalization is applied in this phase. Polarity is preserved from source values without inference.

## Migration Implications

- The generated bundle is appropriate for experimental inspection and validation.
- Records are `partial`, not `trusted`, because value-scale normalization and planner eligibility remain unresolved.
- Equipment/idol domain separation is explicit in the bundle.
- Stable planner consumption remains blocked.

## Deferred

- Full planner remap.
- Value-scale normalization policy.
- Item/passive/skill/idol/unique/set infrastructure.
- Stable API contracts outside experimental routes.

## Checkpoint 3

Checkpoint 3 is ready for review when the generated bundle, validation report, repository, experimental routes, debug page, and focused tests pass.
"""


def _source_affix_identity(record: dict[str, Any]) -> str:
    return str(_provenance(record).get("source_affix_identity") or f"{record.get('source_type', 'unknown')}:{record.get('affix_id')}")


def _canonical_id(source_identity: str, record: dict[str, Any]) -> str:
    safe = source_identity.lower().replace(" ", "_").replace("/", "_")
    if ":" not in safe:
        safe = f"{str(record.get('source_type') or 'unknown').lower()}:{record.get('affix_id')}"
    return f"affix:{safe}"


def _provenance(record: dict[str, Any]) -> dict[str, Any]:
    provenance = record.get("provenance")
    return provenance if isinstance(provenance, dict) else {}


def _affix_domain(record: dict[str, Any]) -> str:
    values = [str(record.get("source_type") or ""), str(record.get("item_type") or "")]
    values.extend(str(value) for value in record.get("eligible_item_types") or [])
    lowered = " ".join(values).lower()
    if "idol" in lowered:
        return "idol"
    if "equipment" in lowered or record.get("eligible_item_types"):
        return "equipment"
    return "unknown"


def _affix_type(categories: list[str]) -> str | None:
    if any(value.upper() == "PREFIX" for value in categories):
        return "prefix"
    if any(value.upper() == "SUFFIX" for value in categories):
        return "suffix"
    return None


def _prefix_suffix(categories: list[str]) -> str | None:
    return _affix_type(categories)


def _tier_range(tier: dict[str, Any]) -> dict[str, Any]:
    minimum = tier.get("minRoll")
    maximum = tier.get("maxRoll")
    return {
        "tier": tier.get("tier"),
        "min_value": minimum,
        "max_value": maximum,
        "tier_group": tier.get("tier_group"),
        "value_scale": "source_units",
        "polarity": _polarity(minimum, maximum),
    }


def _polarity(minimum: Any, maximum: Any) -> str:
    values = [value for value in (minimum, maximum) if isinstance(value, (int, float))]
    if not values:
        return "unknown"
    if all(value >= 0 for value in values):
        return "positive"
    if all(value <= 0 for value in values):
        return "negative"
    return "mixed"


def _modifier_reference(modifier: dict[str, Any]) -> dict[str, Any]:
    return {
        "modifier_id": str(modifier.get("modifier_id")),
        "property": modifier.get("property"),
        "property_path": _property_path(modifier),
        "modifier_type": modifier.get("modifier_type"),
        "source_record_id": _modifier_source(modifier).get("source_affix_identity"),
        "tags": [str(value) for value in modifier.get("tags") or []],
    }


def _modifier_source(modifier: dict[str, Any]) -> dict[str, Any]:
    source = modifier.get("source")
    return source if isinstance(source, dict) else {}


def _property_path(modifier: dict[str, Any]) -> str | None:
    pieces = [modifier.get("modifier_type"), modifier.get("property")]
    tags = modifier.get("tags") or []
    if tags:
        pieces.append(".".join(str(tag) for tag in tags))
    text = ".".join(str(piece) for piece in pieces if piece not in (None, ""))
    return text or None


def _raw_reference_summary(
    record: dict[str, Any],
    modifiers: tuple[dict[str, Any], ...],
    source_identity: str,
) -> dict[str, Any]:
    return {
        "source_affix_identity": source_identity,
        "affix_id": record.get("affix_id"),
        "source_type": record.get("source_type"),
        "source_path": _provenance(record).get("source_path"),
        "categories": [str(value) for value in record.get("categories") or []],
        "eligible_item_types": [str(value) for value in record.get("eligible_item_types") or []],
        "deterministic_modifier_data": record.get("deterministic_modifier_data"),
        "modifier_ids": [str(modifier.get("modifier_id")) for modifier in modifiers],
    }


def _warnings(
    record: dict[str, Any],
    tier_ranges: list[dict[str, Any]],
    modifier_references: list[dict[str, Any]],
) -> list[str]:
    warnings = [
        "Value scale is source-units only; planner normalization is pending.",
    ]
    if not tier_ranges:
        warnings.append("Tier range data is missing.")
    if not modifier_references:
        warnings.append("Modifier references are missing.")
    if not _affix_type([str(value) for value in record.get("categories") or []]):
        warnings.append("Prefix/suffix classification is unavailable.")
    if _affix_domain(record) == "unknown":
        warnings.append("Affix domain could not be classified as equipment or idol.")
    return warnings


def _count_code(items: list[dict[str, Any]], code: str) -> int:
    return sum(1 for item in items if item.get("code") == code)


def _count_rows(counts: dict[str, int]) -> str:
    return "\n".join(f"| `{key}` | {value} |" for key, value in sorted(counts.items()))


def main() -> int:
    args = parse_args()
    bundle = build_v2_affix_bundle(args.source_bundle)
    validation = validate_v2_affix_records(bundle["records"]["affixes"])
    try:
        V2AffixRepository(args.output).load_payload(bundle)
    except V2AffixBundleError as exc:
        validation["errors"].append({"code": "repository_validation_failed", "message": str(exc)})
        validation["summary"]["error_count"] = len(validation["errors"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.validation_output.parent.mkdir(parents=True, exist_ok=True)
    args.validation_output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_affix_bundle.py "
        f"--source-bundle {_display_path(args.source_bundle)} "
        f"--output {_display_path(args.output)} "
        f"--validation-output {_display_path(args.validation_output)} "
        f"--markdown-output {_display_path(args.markdown_output)}"
    )
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(bundle, validation, command=command), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "summary": bundle["summary"], "validation": validation["summary"]}, indent=2))
    return 0 if validation["summary"]["error_count"] == 0 else 1


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix().replace("/", "\\")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
