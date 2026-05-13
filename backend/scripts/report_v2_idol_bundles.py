"""Generate v2 canonical idol and idol-affix bundles."""

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
DEFAULT_SOURCE_AFFIX_BUNDLE = ROOT / "docs" / "generated" / "v2_affix_bundle.json"
DEFAULT_IDOL_OUTPUT = ROOT / "docs" / "generated" / "v2_idol_bundle.json"
DEFAULT_IDOL_AFFIX_OUTPUT = ROOT / "docs" / "generated" / "v2_idol_affix_bundle.json"
DEFAULT_VALIDATION_OUTPUT = ROOT / "docs" / "generated" / "v2_idol_validation_report.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_IDOL_MIGRATION.md"
IDOL_BASE_TYPE_MIN = 25
IDOL_BASE_TYPE_MAX = 33


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build v2 idol and idol-affix bundles.")
    parser.add_argument("--source-items", type=Path, default=DEFAULT_SOURCE_ITEMS)
    parser.add_argument("--source-affix-bundle", type=Path, default=DEFAULT_SOURCE_AFFIX_BUNDLE)
    parser.add_argument("--idol-output", type=Path, default=DEFAULT_IDOL_OUTPUT)
    parser.add_argument("--idol-affix-output", type=Path, default=DEFAULT_IDOL_AFFIX_OUTPUT)
    parser.add_argument("--validation-output", type=Path, default=DEFAULT_VALIDATION_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def build_v2_idol_bundles(source_items: Path, source_affix_bundle: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    items = _read_items(source_items)
    affixes = _read_affix_bundle(source_affix_bundle)
    idol_records: list[dict[str, Any]] = []
    for base_type in items.get("equippable") or []:
        if not isinstance(base_type, dict) or not _is_idol_base_type(base_type):
            continue
        for subtype in base_type.get("subTypes") or []:
            if isinstance(subtype, dict):
                idol_records.append(_idol_record(source_items, items, base_type, subtype))

    idol_affixes = [
        _idol_affix_record(source_affix_bundle, record)
        for record in affixes.get("records", {}).get("affixes", [])
        if isinstance(record, dict) and record.get("affix_domain") == "idol"
    ]
    idol_ids = {record["canonical_id"] for record in idol_records}
    validation = validate_v2_idol_records(idol_records, idol_affixes, idol_ids)
    idol_bundle = {
        "schema_version": "v2.idol_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_items_path": str(source_items),
        "source_metadata": items.get("_meta", {}),
        "summary": _idol_summary(idol_records, validation),
        "records": {"idols": idol_records},
        "metadata": _metadata(),
    }
    idol_affix_bundle = {
        "schema_version": "v2.idol_affix_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_affix_bundle_path": str(source_affix_bundle),
        "source_metadata": affixes.get("source_metadata", {}),
        "summary": _idol_affix_summary(idol_affixes, validation),
        "records": {"idol_affixes": idol_affixes},
        "metadata": _metadata(),
    }
    return idol_bundle, idol_affix_bundle, validation


def validate_v2_idol_records(
    idols: list[dict[str, Any]],
    idol_affixes: list[dict[str, Any]],
    idol_ids: set[str] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    seen_idols = _validate_common_records(idols, "idol", errors)
    seen_affixes = _validate_common_records(idol_affixes, "idol_affix", errors)
    del seen_idols, seen_affixes
    allowed_shapes = _idol_shapes_from_ids(idol_ids or {record["canonical_id"] for record in idols})

    for record in idols:
        canonical_id = record.get("canonical_id")
        dims = record.get("dimensions")
        if not isinstance(dims, dict) or not isinstance(dims.get("width"), int) or not isinstance(dims.get("height"), int):
            errors.append(_error(canonical_id, "invalid_idol_dimensions", "Idol dimensions must include integer width and height."))
        if not record.get("idol_shape"):
            errors.append(_error(canonical_id, "invalid_idol_shape", "Idol shape is required."))
        if not isinstance(record.get("class_restrictions"), list):
            errors.append(_error(canonical_id, "invalid_class_restrictions", "Class restrictions must be a list."))
        if not isinstance(record.get("mastery_restrictions"), list):
            errors.append(_error(canonical_id, "invalid_mastery_restrictions", "Mastery restrictions must be a list."))
        if record.get("stable_calculable") is True:
            errors.append(_error(canonical_id, "unsupported_stable_calculation", "Idols are not stable-calculable in Phase 6."))
        for modifier in record.get("modifier_rows") or []:
            _validate_modifier_row(canonical_id, modifier, errors)

    for record in idol_affixes:
        canonical_id = record.get("canonical_id")
        if record.get("affix_domain") != "idol":
            errors.append(_error(canonical_id, "idol_affix_domain_mismatch", "Idol affix must stay in idol domain."))
        if str(canonical_id).startswith("affix:equipment:"):
            errors.append(_error(canonical_id, "idol_affix_mixed_with_equipment", "Idol affix uses equipment canonical namespace."))
        if not isinstance(record.get("tier_ranges"), list) or not record.get("tier_ranges"):
            errors.append(_error(canonical_id, "invalid_tier_ranges", "Idol affix tier ranges are required."))
        for tier in record.get("tier_ranges") or []:
            if not isinstance(tier, dict) or "min_value" not in tier or "max_value" not in tier:
                errors.append(_error(canonical_id, "invalid_tier_value_range", "Tier ranges must include min_value and max_value."))
        if not isinstance(record.get("idol_type_restrictions"), list):
            errors.append(_error(canonical_id, "invalid_idol_type_restrictions", "Idol type restrictions must be a list."))
        for idol_type in record.get("idol_type_restrictions") or []:
            if str(idol_type) not in allowed_shapes:
                warnings.append(_warning(canonical_id, "unmatched_idol_type_restriction", f"No idol base shape matched {idol_type}."))
        for modifier in record.get("modifier_rows") or []:
            _validate_modifier_row(canonical_id, modifier, errors)

    return {
        "summary": {
            "idol_count": len(idols),
            "idol_affix_count": len(idol_affixes),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "duplicate_idol_id_count": _count_code(errors, "duplicate_idol_id"),
            "duplicate_idol_affix_id_count": _count_code(errors, "duplicate_idol_affix_id"),
            "missing_provenance_count": _count_code(errors, "missing_provenance"),
            "missing_support_status_count": _count_code(errors, "missing_support_status"),
            "invalid_trust_level_count": _count_code(errors, "invalid_trust_level"),
            "idol_affix_mixed_with_equipment_count": _count_code(errors, "idol_affix_mixed_with_equipment"),
            "unsupported_stable_calculation_count": _count_code(errors, "unsupported_stable_calculation"),
            "stable_calculable_count": 0,
            "production_consumed": False,
        },
        "errors": errors,
        "warnings": warnings,
        "metadata": _metadata(),
    }


def render_markdown(idol_bundle: dict[str, Any], idol_affix_bundle: dict[str, Any], validation: dict[str, Any], *, command: str) -> str:
    idol_summary = idol_bundle["summary"]
    affix_summary = idol_affix_bundle["summary"]
    examples = "\n".join(
        f"| `{record['canonical_id']}` | {record['display_name']} | {record['idol_shape']} | {record['dimensions']['width']}x{record['dimensions']['height']} | {', '.join(record['class_restrictions']) or 'Any'} |"
        for record in idol_bundle["records"]["idols"][:20]
    )
    affix_examples = "\n".join(
        f"| `{record['canonical_id']}` | {record['display_name']} | {record['prefix_suffix']} | {len(record['tier_ranges'])} | {', '.join(record['idol_type_restrictions'][:3])} |"
        for record in idol_affix_bundle["records"]["idol_affixes"][:20]
    )
    return f"""# v2 Idol Migration

## Purpose

Phase 6 creates read-only canonical idol and idol-affix bundles. Idol bases are generated from extracted item subtype data, while idol affixes are generated from the Phase 3 v2 affix bundle and re-namespaced so they remain separate from equipment affixes.

This phase does not remap planner behavior or implement idol slot behavior.

## Generation Command

```powershell
{command}
```

## Summary

- Idol count: {idol_summary["idol_count"]}
- Idol affix count: {affix_summary["idol_affix_count"]}
- Stable-calculable count: 0
- Validation errors: {validation["summary"]["error_count"]}
- Validation warnings: {validation["summary"]["warning_count"]}
- Production consumed: false

## Idol Shape Counts

| Shape | Count |
| --- | ---: |
{_count_rows(idol_summary["idol_shape_counts"])}

## Idol Class Restriction Counts

| Class | Count |
| --- | ---: |
{_count_rows(idol_summary["class_restriction_counts"])}

## Idol Affix Prefix/Suffix Counts

| Classification | Count |
| --- | ---: |
{_count_rows(affix_summary["prefix_suffix_counts"])}

## Example Idol Bases

| Canonical ID | Display name | Shape | Dimensions | Class |
| --- | --- | --- | --- | --- |
{examples}

## Example Idol Affixes

| Canonical ID | Display name | Prefix/Suffix | Tiers | Idol restrictions |
| --- | --- | --- | ---: | --- |
{affix_examples}

## Migration Implications

- Idols and idol affixes are available for experimental lookup and debug inspection.
- Idol affixes are intentionally separate from equipment affixes.
- Records remain `partial` because value-scale and modifier normalization are unresolved.
- Existing planner and idol slot behavior remain unchanged.

## Deferred

- Planner idol slot behavior.
- Modifier/value normalization.
- Stable stat aggregation from idol affixes.
- Class/mastery, passive, and skill infrastructure.

## Checkpoint 6

Checkpoint 6 is ready for review when generated bundles, validation report, repository, routes, debug page, and focused tests pass.
"""


def _idol_record(source_items: Path, payload: dict[str, Any], base_type: dict[str, Any], subtype: dict[str, Any]) -> dict[str, Any]:
    base_type_id = base_type.get("baseTypeID")
    subtype_id = subtype.get("subTypeID")
    source_id = f"idol:{base_type_id}:{subtype_id}"
    canonical_id = f"idol:{base_type_id}:{subtype_id}"
    item_type = str(base_type.get("type") or "unknown")
    shape = item_type.lower()
    dimensions = _idol_dimensions(item_type)
    modifier_rows = [
        _modifier_row(source_items, payload, implicit, f"{source_id}:implicit:{index}", "idol_implicit")
        for index, implicit in enumerate(subtype.get("implicits") or [])
        if isinstance(implicit, dict)
    ]
    warnings = ["Idol base is not stable planner-consumed in Phase 6."]
    if not dimensions:
        warnings.append("Idol dimensions could not be parsed from source item type.")
    return {
        "canonical_id": canonical_id,
        "display_name": subtype.get("displayName") or subtype.get("name") or base_type.get("displayName") or canonical_id,
        "source_id": source_id,
        "source_file": str(source_items),
        "patch_version": _game_version(payload),
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_items, source_id, "idol", payload, base_type_id, subtype_id),
        "item_category": "idol",
        "item_type": item_type,
        "subtype": subtype.get("name"),
        "equipment_slot": "idol",
        "slot": "idol",
        "classification": "idol",
        "idol_size": base_type.get("displayName") or base_type.get("name"),
        "idol_shape": shape,
        "dimensions": dimensions or {"width": 0, "height": 0},
        "class_restrictions": _restriction_values(subtype.get("classRequirement")),
        "mastery_restrictions": _restriction_values(subtype.get("subClassRequirement")),
        "requirements": {"level": subtype.get("levelRequirement"), "class": subtype.get("classRequirement"), "mastery": subtype.get("subClassRequirement"), "attributes": {}},
        "level_requirement": subtype.get("levelRequirement"),
        "attribute_requirements": {},
        "modifier_references": [_modifier_ref(row) for row in modifier_rows],
        "modifier_rows": modifier_rows,
        "allowed_affix_ids": [],
        "stable_calculable": False,
        "warnings": warnings,
        "raw_reference": {"baseTypeID": base_type_id, "subTypeID": subtype_id, "type": base_type.get("type"), "name": subtype.get("name")},
        "normalized_fields": {"modifier_references": [_modifier_ref(row) for row in modifier_rows]},
        "consumer_safe_fields": {"display_name": subtype.get("displayName") or subtype.get("name") or canonical_id, "support_status": SupportStatus.PARTIAL.value, "stable_calculable": False},
    }


def _idol_affix_record(source_affix_bundle: Path, record: dict[str, Any]) -> dict[str, Any]:
    source_affix_id = record.get("source_affix_id")
    canonical_id = f"idol_affix:{source_affix_id}"
    idol_types = [str(value) for value in record.get("slot_restrictions") or record.get("item_type_restrictions") or []]
    modifier_rows = [
        {
            **modifier,
            "support_status": SupportStatus.PARTIAL.value,
            "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
            "stable_calculable": False,
            "provenance": {
                "source_path": str(source_affix_bundle),
                "source_type": "idol_affix_modifier",
                "source_id": modifier.get("source_record_id") or modifier.get("modifier_id"),
                "extraction_method": "v2_affix_bundle_idol_projection",
                "patch_version": record.get("patch_version"),
                "schema_version": "v2.idol.1",
                "notes": ["Projected from v2 idol-domain affix data; value scale remains source-preserved."],
                "raw_reference": {"source_affix_id": source_affix_id, "modifier_id": modifier.get("modifier_id")},
            },
        }
        for modifier in record.get("modifier_references") or []
        if isinstance(modifier, dict)
    ]
    return {
        **{key: value for key, value in record.items() if key not in {"canonical_id", "source_id", "provenance", "modifier_references", "normalized_fields", "consumer_safe_fields"}},
        "canonical_id": canonical_id,
        "source_id": f"idol_affix:{source_affix_id}",
        "source_file": str(source_affix_bundle),
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": {
            "source_path": str(source_affix_bundle),
            "source_type": "idol_affix",
            "source_id": f"idol_affix:{source_affix_id}",
            "extraction_method": "v2_affix_bundle_idol_projection",
            "patch_version": record.get("patch_version"),
            "schema_version": "v2.idol.1",
            "notes": ["Idol affix is projected into an idol-only namespace and is not an equipment affix."],
            "raw_reference": {"source_canonical_id": record.get("canonical_id"), "source_affix_id": source_affix_id},
        },
        "affix_domain": "idol",
        "idol_type_restrictions": idol_types,
        "slot_restrictions": idol_types,
        "item_type_restrictions": idol_types,
        "modifier_references": [_modifier_ref(row) for row in modifier_rows],
        "modifier_rows": modifier_rows,
        "stable_calculable": False,
        "warnings": list(record.get("warnings") or []) + ["Idol affix remains separate from equipment affixes and is not stable planner-consumed in Phase 6."],
        "normalized_fields": {"modifier_references": [_modifier_ref(row) for row in modifier_rows], "tier_ranges": record.get("tier_ranges") or []},
        "consumer_safe_fields": {"display_name": record.get("display_name"), "support_status": SupportStatus.PARTIAL.value, "stable_calculable": False, "idol_type_restrictions": idol_types},
    }


def _validate_common_records(records: list[dict[str, Any]], kind: str, errors: list[dict[str, Any]]) -> set[str]:
    seen: set[str] = set()
    for record in records:
        canonical_id = record.get("canonical_id")
        try:
            validate_canonical_id(canonical_id)
        except ValueError as exc:
            errors.append(_error(canonical_id, "invalid_canonical_id", str(exc)))
            continue
        if canonical_id in seen:
            errors.append(_error(canonical_id, f"duplicate_{kind}_id", "Duplicate canonical ID."))
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
    return seen


def _validate_modifier_row(canonical_id: Any, modifier: Any, errors: list[dict[str, Any]]) -> None:
    if not isinstance(modifier, dict):
        errors.append(_error(canonical_id, "invalid_modifier_row", "Modifier row must be an object."))
        return
    if not modifier.get("provenance"):
        errors.append(_error(canonical_id, "modifier_missing_provenance", "Modifier row is missing provenance."))
    if not modifier.get("support_status"):
        errors.append(_error(canonical_id, "modifier_missing_support_status", "Modifier row is missing support status."))
    if modifier.get("stable_calculable") is True:
        errors.append(_error(canonical_id, "unsupported_stable_calculation", "Modifier row is not stable-calculable in Phase 6."))


def _read_items(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"items export not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("equippable"), list):
        raise ValueError("items export must contain equippable list")
    return data


def _read_affix_bundle(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"v2 affix bundle not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("records", {}).get("affixes"), list):
        raise ValueError("v2 affix bundle must contain records.affixes list")
    return data


def _is_idol_base_type(base_type: dict[str, Any]) -> bool:
    base_type_id = base_type.get("baseTypeID")
    item_type = str(base_type.get("type") or "")
    return isinstance(base_type_id, int) and IDOL_BASE_TYPE_MIN <= base_type_id <= IDOL_BASE_TYPE_MAX and item_type.startswith("IDOL_")


def _idol_dimensions(item_type: str) -> dict[str, int] | None:
    if "1x1" in item_type:
        return {"width": 1, "height": 1}
    for width, height in ((2, 1), (1, 2), (3, 1), (1, 3), (4, 1), (1, 4), (2, 2)):
        if f"{width}x{height}" in item_type:
            return {"width": width, "height": height}
    return None


def _metadata() -> dict[str, Any]:
    return {"phase": "phase_6_idol_infrastructure", "read_only": True, "experimental": True, "production_consumer": False, "production_safe": False, "stable_planner_consumed": False, "uses_canonical_contracts": True}


def _provenance(source_items: Path, source_id: str, source_type: str, payload: dict[str, Any], base_type_id: Any, subtype_id: Any) -> dict[str, Any]:
    return {"source_path": str(source_items), "source_type": source_type, "source_id": source_id, "extraction_method": "last_epoch_items_export", "patch_version": _game_version(payload), "schema_version": "v2.idol.1", "notes": ["Generated from extracted idol subtype data."], "raw_reference": {"baseTypeID": base_type_id, "subTypeID": subtype_id}}


def _modifier_row(source_path: Path, payload: dict[str, Any], mod: dict[str, Any], source_id: str, source_type: str) -> dict[str, Any]:
    return {"modifier_id": source_id.replace(":", "_"), "property": mod.get("property"), "property_path": _property_path(mod), "modifier_type": mod.get("modifierType"), "value_min": mod.get("value"), "value_max": mod.get("maxValue", mod.get("value")), "tags": [str(tag) for tag in mod.get("tags") or []], "support_status": SupportStatus.PARTIAL.value, "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value, "stable_calculable": False, "provenance": {"source_path": str(source_path), "source_type": source_type, "source_id": source_id, "extraction_method": "last_epoch_items_export", "patch_version": _game_version(payload), "schema_version": "v2.idol.1", "notes": ["Value scale remains source-preserved."], "raw_reference": {"property": mod.get("property")}}}


def _modifier_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {"modifier_id": row.get("modifier_id"), "property": row.get("property"), "property_path": row.get("property_path"), "source_record_id": row.get("provenance", {}).get("source_id")}


def _property_path(mod: dict[str, Any]) -> str:
    parts = [mod.get("modifierType"), mod.get("property")]
    parts.extend(str(tag) for tag in mod.get("tags") or [] if str(tag) != "None")
    return ".".join(str(part) for part in parts if part not in (None, ""))


def _idol_summary(records: list[dict[str, Any]], validation: dict[str, Any]) -> dict[str, Any]:
    classes = Counter((record["class_restrictions"][0] if record["class_restrictions"] else "Any") for record in records)
    return {"idol_count": len(records), "idol_shape_counts": dict(sorted(Counter(record["idol_shape"] for record in records).items())), "class_restriction_counts": dict(sorted(classes.items())), "records_with_implicits_count": sum(1 for record in records if record["modifier_rows"]), "support_status_counts": dict(sorted(Counter(record["support_status"] for record in records).items())), "trust_level_counts": dict(sorted(Counter(record["trust_level"] for record in records).items())), "stable_calculable_count": 0, "validation_error_count": validation["summary"]["error_count"], "production_consumed": False}


def _idol_affix_summary(records: list[dict[str, Any]], validation: dict[str, Any]) -> dict[str, Any]:
    return {"idol_affix_count": len(records), "prefix_suffix_counts": dict(sorted(Counter(record.get("prefix_suffix") for record in records).items())), "idol_type_restriction_counts": dict(sorted(Counter(value for record in records for value in record.get("idol_type_restrictions") or []).items())), "modifier_row_count": sum(len(record.get("modifier_rows") or []) for record in records), "support_status_counts": dict(sorted(Counter(record["support_status"] for record in records).items())), "trust_level_counts": dict(sorted(Counter(record["trust_level"] for record in records).items())), "stable_calculable_count": 0, "validation_error_count": validation["summary"]["error_count"], "production_consumed": False}


def _idol_shapes_from_ids(ids: set[str]) -> set[str]:
    return {shape for shape in ("IDOL_1x1_ETERRA", "IDOL_1x1_LAGON", "IDOL_2x1", "IDOL_1x2", "IDOL_3x1", "IDOL_1x3", "IDOL_4x1", "IDOL_1x4", "IDOL_2x2")}


def _restriction_values(value: Any) -> list[str]:
    if value in (None, "", "Any"):
        return []
    return [str(value)]


def _game_version(payload: dict[str, Any]) -> str | None:
    meta = payload.get("_meta") or {}
    game_build = meta.get("game_build") if isinstance(meta, dict) else {}
    if isinstance(game_build, dict) and game_build.get("installPath"):
        return str(game_build["installPath"]).split("\\")[-1]
    return None


def _error(canonical_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"canonical_id": canonical_id, "code": code, "message": message}


def _warning(canonical_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"canonical_id": canonical_id, "code": code, "message": message}


def _count_code(errors: list[dict[str, Any]], code: str) -> int:
    return sum(1 for error in errors if error.get("code") == code)


def _count_rows(counts: dict[str, int]) -> str:
    return "\n".join(f"| {key} | {value} |" for key, value in sorted(counts.items())) or "| none | 0 |"


def main() -> int:
    args = parse_args()
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_idol_bundles.py "
        f"--source-items {args.source_items} --source-affix-bundle {args.source_affix_bundle} "
        f"--idol-output {args.idol_output} --idol-affix-output {args.idol_affix_output} "
        f"--validation-output {args.validation_output} --markdown-output {args.markdown_output}"
    )
    idol_bundle, idol_affix_bundle, validation = build_v2_idol_bundles(args.source_items, args.source_affix_bundle)
    for path, payload in ((args.idol_output, idol_bundle), (args.idol_affix_output, idol_affix_bundle), (args.validation_output, validation)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(idol_bundle, idol_affix_bundle, validation, command=command), encoding="utf-8")
    print(json.dumps({"idol_count": idol_bundle["summary"]["idol_count"], "idol_affix_count": idol_affix_bundle["summary"]["idol_affix_count"], "validation_error_count": validation["summary"]["error_count"], "validation_warning_count": validation["summary"]["warning_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
