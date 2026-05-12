"""Generate v2 canonical item base and implicit bundles."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


DEFAULT_SOURCE_ITEMS = Path(r"D:\Forge\last-epoch-data\exports_json\items.json")
DEFAULT_BASE_OUTPUT = ROOT / "docs" / "generated" / "v2_item_base_bundle.json"
DEFAULT_IMPLICIT_OUTPUT = ROOT / "docs" / "generated" / "v2_item_implicit_bundle.json"
DEFAULT_VALIDATION_OUTPUT = ROOT / "docs" / "generated" / "v2_item_validation_report.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_ITEM_BASE_MIGRATION.md"
MAX_PHASE4_EQUIPMENT_BASE_TYPE_ID = 24


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build v2 item base and implicit bundles.")
    parser.add_argument("--source-items", type=Path, default=DEFAULT_SOURCE_ITEMS)
    parser.add_argument("--base-output", type=Path, default=DEFAULT_BASE_OUTPUT)
    parser.add_argument("--implicit-output", type=Path, default=DEFAULT_IMPLICIT_OUTPUT)
    parser.add_argument("--validation-output", type=Path, default=DEFAULT_VALIDATION_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def build_v2_item_bundles(source_items: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    payload = _read_items(source_items)
    base_records: list[dict[str, Any]] = []
    implicit_records: list[dict[str, Any]] = []
    for base_type in payload.get("equippable") or []:
        if not isinstance(base_type, dict):
            continue
        if not _is_phase4_equipment_base_type(base_type):
            continue
        for subtype in base_type.get("subTypes") or []:
            if not isinstance(subtype, dict):
                continue
            base_record = _base_record(source_items, payload, base_type, subtype)
            base_records.append(base_record)
            for index, implicit in enumerate(subtype.get("implicits") or []):
                if isinstance(implicit, dict):
                    implicit_record = _implicit_record(
                        source_items,
                        payload,
                        base_type,
                        subtype,
                        implicit,
                        index,
                        base_record["canonical_id"],
                    )
                    implicit_records.append(implicit_record)
                    base_record["implicit_ids"].append(implicit_record["canonical_id"])

    validation = validate_v2_item_records(base_records, implicit_records)
    base_bundle = {
        "schema_version": "v2.item_base_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_items_path": str(source_items),
        "source_metadata": payload.get("_meta", {}),
        "summary": _base_summary(base_records, payload, validation),
        "records": {"item_bases": base_records},
        "metadata": _metadata(),
    }
    implicit_bundle = {
        "schema_version": "v2.item_implicit_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_items_path": str(source_items),
        "source_metadata": payload.get("_meta", {}),
        "summary": _implicit_summary(implicit_records, validation),
        "records": {"implicits": implicit_records},
        "metadata": _metadata(),
    }
    return base_bundle, implicit_bundle, validation


def validate_v2_item_records(
    item_bases: list[dict[str, Any]],
    implicits: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    base_ids = _validate_canonical_records(item_bases, "item_base", errors)
    implicit_ids = _validate_canonical_records(implicits, "implicit", errors)
    del implicit_ids
    for record in item_bases:
        canonical_id = record.get("canonical_id")
        if not record.get("item_category"):
            errors.append(_error(canonical_id, "missing_item_category", "Item category is required."))
        if not record.get("item_type"):
            errors.append(_error(canonical_id, "missing_item_type", "Item type is required."))
        if not record.get("subtype"):
            errors.append(_error(canonical_id, "missing_subtype", "Subtype is required."))
        if record.get("slot") is not None and not isinstance(record.get("slot"), str):
            errors.append(_error(canonical_id, "invalid_equipment_slot", "Equipment slot must be text."))
        requirements = record.get("requirements")
        if not isinstance(requirements, dict):
            errors.append(_error(canonical_id, "invalid_requirement_shape", "Requirements must be an object."))
        for implicit_id in record.get("implicit_ids") or []:
            if implicit_id not in {implicit.get("canonical_id") for implicit in implicits}:
                errors.append(_error(canonical_id, "implicit_link_missing", f"Implicit is missing: {implicit_id}"))

    for record in implicits:
        canonical_id = record.get("canonical_id")
        base_id = record.get("item_base_id")
        if base_id not in base_ids:
            errors.append(_error(canonical_id, "implicit_base_link_missing", f"Item base is missing: {base_id}"))
        if not isinstance(record.get("modifier_references"), list):
            errors.append(_error(canonical_id, "invalid_modifier_references", "Modifier references must be a list."))
        for modifier in record.get("modifier_rows") or []:
            if not isinstance(modifier, dict):
                errors.append(_error(canonical_id, "invalid_modifier_row", "Modifier row must be an object."))
                continue
            if not modifier.get("provenance"):
                errors.append(_error(canonical_id, "modifier_missing_provenance", "Implicit modifier row is missing provenance."))
            if not modifier.get("support_status"):
                errors.append(_error(canonical_id, "modifier_missing_support_status", "Implicit modifier row is missing support status."))
            if modifier.get("stable_calculable") is True:
                errors.append(_error(canonical_id, "unsupported_stable_calculation", "Implicit modifiers are not stable-calculable in Phase 4."))

    return {
        "summary": {
            "item_base_count": len(item_bases),
            "implicit_count": len(implicits),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "duplicate_item_base_id_count": _count_code(errors, "duplicate_item_base_id"),
            "duplicate_implicit_id_count": _count_code(errors, "duplicate_implicit_id"),
            "missing_provenance_count": _count_code(errors, "missing_provenance"),
            "missing_support_status_count": _count_code(errors, "missing_support_status"),
            "invalid_trust_level_count": _count_code(errors, "invalid_trust_level"),
            "implicit_base_link_missing_count": _count_code(errors, "implicit_base_link_missing"),
            "stable_calculable_count": 0,
            "production_consumed": False,
        },
        "errors": errors,
        "warnings": warnings,
        "metadata": _metadata(),
    }


def _validate_canonical_records(
    records: list[dict[str, Any]],
    kind: str,
    errors: list[dict[str, Any]],
) -> set[str]:
    seen: set[str] = set()
    for record in records:
        canonical_id = record.get("canonical_id")
        try:
            validate_canonical_id(canonical_id)
        except ValueError as exc:
            errors.append(_error(canonical_id, "invalid_canonical_id", str(exc)))
            continue
        duplicate_code = f"duplicate_{kind}_id"
        if canonical_id in seen:
            errors.append(_error(canonical_id, duplicate_code, "Duplicate canonical ID."))
        seen.add(canonical_id)
        if not record.get("provenance"):
            errors.append(_error(canonical_id, "missing_provenance", "Provenance is required."))
        try:
            SupportStatus(str(record.get("support_status")))
        except ValueError:
            errors.append(_error(canonical_id, "missing_support_status", "Support status is required or invalid."))
        try:
            TrustLevel(str(record.get("trust_level")))
        except ValueError:
            errors.append(_error(canonical_id, "invalid_trust_level", "Trust level is invalid."))
        provenance = record.get("provenance")
        if record.get("trust_level") in {TrustLevel.GAME_EXTRACTED.value, TrustLevel.GENERATED_FROM_GAME_DATA.value}:
            if not isinstance(provenance, dict) or not provenance.get("source_id"):
                errors.append(_error(canonical_id, "missing_source_reference", "Generated or extracted records require source_id."))
        if record.get("stable_calculable") is True:
            errors.append(_error(canonical_id, "unsupported_stable_calculation", "Phase 4 records must not be stable-calculable."))
    return seen


def _base_record(source_items: Path, payload: dict[str, Any], base_type: dict[str, Any], subtype: dict[str, Any]) -> dict[str, Any]:
    base_type_id = base_type.get("baseTypeID")
    subtype_id = subtype.get("subTypeID")
    canonical_id = f"item_base:equippable:{base_type_id}:{subtype_id}"
    item_type = str(base_type.get("type") or base_type.get("displayName") or "unknown").lower()
    classification = _classification(item_type, subtype)
    source_id = f"equippable:{base_type_id}:{subtype_id}"
    return {
        "canonical_id": canonical_id,
        "display_name": subtype.get("displayName") or subtype.get("name") or canonical_id,
        "source_id": source_id,
        "source_file": str(source_items),
        "patch_version": _game_version(payload),
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_items, source_id, "item_base", payload, base_type_id, subtype_id),
        "item_category": "equipment",
        "item_type": item_type,
        "subtype": subtype.get("name"),
        "equipment_slot": item_type,
        "slot": item_type,
        "classification": classification,
        "class_restrictions": _restriction_values(subtype.get("classRequirement")),
        "mastery_restrictions": _restriction_values(subtype.get("subClassRequirement")),
        "requirements": {
            "level": subtype.get("levelRequirement"),
            "attributes": {},
            "class": subtype.get("classRequirement"),
            "mastery": subtype.get("subClassRequirement"),
        },
        "level_requirement": subtype.get("levelRequirement"),
        "attribute_requirements": {},
        "implicit_ids": [],
        "base_stats": _base_stats(base_type, subtype),
        "tags": [str(tag) for tag in subtype.get("tags") or []],
        "grid_size": base_type.get("gridSize"),
        "maximum_affixes": base_type.get("maximumAffixes"),
        "cannot_drop": subtype.get("cannotDrop"),
        "stable_calculable": False,
        "warnings": _base_warnings(subtype),
        "raw_reference": {
            "baseTypeID": base_type_id,
            "subTypeID": subtype_id,
            "type": base_type.get("type"),
            "name": subtype.get("name"),
        },
        "normalized_fields": {},
        "consumer_safe_fields": {
            "display_name": subtype.get("displayName") or subtype.get("name") or canonical_id,
            "item_type": item_type,
            "slot": item_type,
            "support_status": SupportStatus.PARTIAL.value,
            "stable_calculable": False,
        },
    }


def _implicit_record(
    source_items: Path,
    payload: dict[str, Any],
    base_type: dict[str, Any],
    subtype: dict[str, Any],
    implicit: dict[str, Any],
    index: int,
    base_id: str,
) -> dict[str, Any]:
    base_type_id = base_type.get("baseTypeID")
    subtype_id = subtype.get("subTypeID")
    canonical_id = f"implicit:equippable:{base_type_id}:{subtype_id}:{index}"
    source_id = f"equippable:{base_type_id}:{subtype_id}:implicit:{index}"
    modifier_id = f"item_implicit:equippable:{base_type_id}:{subtype_id}:{index}"
    modifier_ref = {
        "modifier_id": modifier_id,
        "property": implicit.get("property"),
        "property_path": _property_path(implicit),
        "source_record_id": source_id,
    }
    modifier_row = {
        "modifier_id": modifier_id,
        "property": implicit.get("property"),
        "property_path": _property_path(implicit),
        "modifier_type": implicit.get("modifierType"),
        "value_min": implicit.get("value"),
        "value_max": implicit.get("maxValue"),
        "tags": [str(tag) for tag in implicit.get("tags") or []],
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "stable_calculable": False,
        "provenance": _provenance(source_items, source_id, "item_implicit", payload, base_type_id, subtype_id),
    }
    return {
        "canonical_id": canonical_id,
        "display_name": _implicit_display_name(implicit),
        "source_id": source_id,
        "source_file": str(source_items),
        "patch_version": _game_version(payload),
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_items, source_id, "item_implicit", payload, base_type_id, subtype_id),
        "item_base_id": base_id,
        "item_type": str(base_type.get("type") or "unknown").lower(),
        "modifier_references": [modifier_ref],
        "modifier_rows": [modifier_row],
        "value_range": {
            "min": implicit.get("value"),
            "max": implicit.get("maxValue"),
            "value_scale": "source_units",
            "polarity": _polarity(implicit.get("value"), implicit.get("maxValue")),
        },
        "stable_calculable": False,
        "warnings": ["Implicit value scale is source-units only; planner normalization is pending."],
        "raw_reference": {
            "baseTypeID": base_type_id,
            "subTypeID": subtype_id,
            "implicit_index": index,
            "property": implicit.get("property"),
            "modifierType": implicit.get("modifierType"),
        },
        "normalized_fields": {"modifier_references": [modifier_ref]},
        "consumer_safe_fields": {
            "display_name": _implicit_display_name(implicit),
            "support_status": SupportStatus.PARTIAL.value,
            "stable_calculable": False,
        },
    }


def render_markdown(base_bundle: dict[str, Any], implicit_bundle: dict[str, Any], validation: dict[str, Any], *, command: str) -> str:
    base_summary = base_bundle["summary"]
    implicit_summary = implicit_bundle["summary"]
    examples = "\n".join(
        f"| `{record['canonical_id']}` | {record['display_name']} | {record['item_type']} | {record['level_requirement']} | {len(record['implicit_ids'])} |"
        for record in base_bundle["records"]["item_bases"][:20]
    )
    return f"""# v2 Item Base Migration

## Purpose

Phase 4 creates read-only canonical item base and implicit bundles on top of the v2 data contracts. The generated data preserves extracted item subtype, requirement, slot, and implicit modifier evidence without remapping planner behavior.

This phase does not implement unique, set, idol, passive, skill, crafting, or planner migration.

## Generation Command

```powershell
{command}
```

## Summary

- Item base count: {base_summary["item_base_count"]}
- Implicit count: {implicit_summary["implicit_count"]}
- Base type count: {base_summary["base_type_count"]}
- Excluded non-Phase-4 base type count: {base_summary["excluded_non_phase4_base_type_count"]}
- Stable-calculable count: 0
- Validation errors: {validation["summary"]["error_count"]}
- Validation warnings: {validation["summary"]["warning_count"]}
- Production consumed: false

## Support Status Counts

| Support status | Count |
| --- | ---: |
{_count_rows(base_summary["support_status_counts"])}

## Item Classification Counts

| Classification | Count |
| --- | ---: |
{_count_rows(base_summary["classification_counts"])}

## Implicit Modifier Count Distribution

| Modifier rows | Implicit count |
| --- | ---: |
{_count_rows(implicit_summary["modifier_row_count_distribution"])}

## Example Item Bases

| Canonical ID | Display name | Item type | Level requirement | Implicits |
| --- | --- | --- | ---: | ---: |
{examples}

## Migration Implications

- Item base and implicit records are available for experimental lookup and debug inspection.
- Records remain `partial` and non-stable because value-scale policy and planner compatibility have not been reviewed.
- Implicit records are linked back to item base IDs for future compatibility checks.
- Existing `/api/ref/base-items` and planner behavior remain unchanged.

## Deferred

- Unique and set item infrastructure.
- Idol-specific infrastructure.
- Planner remapping and implicit stat aggregation.
- Value-scale normalization policy.

## Checkpoint 4

Checkpoint 4 is ready for review when the generated item bundles, validation report, repository, experimental routes, debug view, and focused tests pass.
"""


def _read_items(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"items export not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("items export must be a JSON object")
    if not isinstance(data.get("equippable"), list):
        raise ValueError("items export equippable must be a list")
    return data


def _is_phase4_equipment_base_type(base_type: dict[str, Any]) -> bool:
    base_type_id = base_type.get("baseTypeID")
    return isinstance(base_type_id, int) and base_type_id <= MAX_PHASE4_EQUIPMENT_BASE_TYPE_ID


def _metadata() -> dict[str, Any]:
    return {
        "phase": "phase_4_item_base_implicit_infrastructure",
        "read_only": True,
        "experimental": True,
        "production_consumer": False,
        "production_safe": False,
        "stable_planner_consumed": False,
        "uses_canonical_contracts": True,
    }


def _provenance(
    source_items: Path,
    source_id: str,
    source_type: str,
    payload: dict[str, Any],
    base_type_id: Any,
    subtype_id: Any,
) -> dict[str, Any]:
    return {
        "source_path": str(source_items),
        "source_type": source_type,
        "source_id": source_id,
        "extraction_method": "last_epoch_items_export",
        "patch_version": _game_version(payload),
        "schema_version": "v2.item.1",
        "notes": ["Generated from extracted item subtype data; value scale remains source-preserved."],
        "raw_reference": {"baseTypeID": base_type_id, "subTypeID": subtype_id},
    }


def _base_summary(records: list[dict[str, Any]], source: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_base_count": len(records),
        "base_type_count": sum(1 for base_type in source.get("equippable") or [] if isinstance(base_type, dict) and _is_phase4_equipment_base_type(base_type)),
        "excluded_non_phase4_base_type_count": sum(1 for base_type in source.get("equippable") or [] if isinstance(base_type, dict) and not _is_phase4_equipment_base_type(base_type)),
        "support_status_counts": dict(sorted(Counter(record["support_status"] for record in records).items())),
        "trust_level_counts": dict(sorted(Counter(record["trust_level"] for record in records).items())),
        "item_type_counts": dict(sorted(Counter(record["item_type"] for record in records).items())),
        "classification_counts": dict(sorted(Counter(record["classification"] for record in records).items())),
        "records_with_implicits_count": sum(1 for record in records if record["implicit_ids"]),
        "records_with_class_restrictions_count": sum(1 for record in records if record["class_restrictions"]),
        "stable_calculable_count": 0,
        "validation_error_count": validation["summary"]["error_count"],
        "production_consumed": False,
    }


def _implicit_summary(records: list[dict[str, Any]], validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "implicit_count": len(records),
        "support_status_counts": dict(sorted(Counter(record["support_status"] for record in records).items())),
        "trust_level_counts": dict(sorted(Counter(record["trust_level"] for record in records).items())),
        "property_counts": dict(sorted(Counter(row["property"] for record in records for row in record["modifier_rows"]).items())),
        "modifier_row_count_distribution": dict(sorted(Counter(str(len(record["modifier_rows"])) for record in records).items())),
        "stable_calculable_count": 0,
        "validation_error_count": validation["summary"]["error_count"],
        "production_consumed": False,
    }


def _classification(item_type: str, subtype: dict[str, Any]) -> str:
    tags = {str(tag).lower() for tag in subtype.get("tags") or []}
    if "idol" in item_type:
        return "idol"
    if "weapon" in tags or any(token in item_type for token in ("axe", "dagger", "mace", "sceptre", "sword", "wand", "staff", "bow", "crossbow", "spear", "fist")):
        return "weapon"
    if any(token in item_type for token in ("helmet", "body", "boots", "gloves", "shield")):
        return "armor"
    if any(token in item_type for token in ("belt", "amulet", "ring", "relic", "quiver", "catalyst")):
        return "accessory"
    return "unknown"


def _restriction_values(value: Any) -> list[str]:
    if value in (None, "", "Any"):
        return []
    return [str(value)]


def _base_stats(base_type: dict[str, Any], subtype: dict[str, Any]) -> dict[str, Any]:
    return {
        "affix_effect_modifier": base_type.get("affixEffectModifier"),
        "maximum_affixes": base_type.get("maximumAffixes"),
        "max_sockets": base_type.get("maxSockets"),
        "added_weapon_range": subtype.get("addedWeaponRange"),
        "attack_rate": subtype.get("attackRate"),
        "im_set_tier": subtype.get("IMSetTier"),
    }


def _base_warnings(subtype: dict[str, Any]) -> list[str]:
    warnings = ["Item base is not stable planner-consumed in Phase 4."]
    if not subtype.get("implicits"):
        warnings.append("No implicit rows are present for this subtype.")
    if subtype.get("isLegacySubType"):
        warnings.append("Subtype is marked legacy in source data.")
    return warnings


def _implicit_display_name(implicit: dict[str, Any]) -> str:
    modifier = implicit.get("modifierType") or "modifier"
    prop = implicit.get("property") or "unknown_property"
    tags = ".".join(str(tag) for tag in implicit.get("tags") or [] if str(tag) != "None")
    return f"{modifier} {prop}{f' [{tags}]' if tags else ''}"


def _property_path(implicit: dict[str, Any]) -> str:
    parts = [implicit.get("modifierType"), implicit.get("property")]
    tags = [str(tag) for tag in implicit.get("tags") or [] if str(tag) != "None"]
    parts.extend(tags)
    return ".".join(str(part) for part in parts if part not in (None, ""))


def _polarity(minimum: Any, maximum: Any) -> str:
    values = [value for value in (minimum, maximum) if isinstance(value, (int, float))]
    if not values:
        return "unknown"
    if all(value >= 0 for value in values):
        return "positive"
    if all(value <= 0 for value in values):
        return "negative"
    return "mixed"


def _game_version(payload: dict[str, Any]) -> str | None:
    game_build = (payload.get("_meta") or {}).get("game_build") or {}
    install_path = game_build.get("installPath")
    if not install_path:
        return None
    return str(install_path).split("\\")[-1]


def _error(canonical_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"canonical_id": canonical_id, "code": code, "message": message}


def _count_code(items: list[dict[str, Any]], code: str) -> int:
    return sum(1 for item in items if item.get("code") == code)


def _count_rows(counts: dict[str, int]) -> str:
    return "\n".join(f"| `{key}` | {value} |" for key, value in sorted(counts.items()))


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix().replace("/", "\\")
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    base_bundle, implicit_bundle, validation = build_v2_item_bundles(args.source_items)
    for path, payload in [
        (args.base_output, base_bundle),
        (args.implicit_output, implicit_bundle),
        (args.validation_output, validation),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_item_bundles.py "
        f"--source-items {_display_path(args.source_items)} "
        f"--base-output {_display_path(args.base_output)} "
        f"--implicit-output {_display_path(args.implicit_output)} "
        f"--validation-output {_display_path(args.validation_output)} "
        f"--markdown-output {_display_path(args.markdown_output)}"
    )
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(
        render_markdown(base_bundle, implicit_bundle, validation, command=command),
        encoding="utf-8",
    )
    print(json.dumps({
        "base_output": str(args.base_output),
        "implicit_output": str(args.implicit_output),
        "base_summary": base_bundle["summary"],
        "implicit_summary": implicit_bundle["summary"],
        "validation": validation["summary"],
    }, indent=2))
    return 0 if validation["summary"]["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
