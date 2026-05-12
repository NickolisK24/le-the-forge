"""Generate v2 canonical unique and set item bundles."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


DEFAULT_SOURCE_UNIQUES = Path(r"D:\Forge\last-epoch-data\exports_json\uniques.json")
DEFAULT_SOURCE_SET_BONUSES = Path(r"D:\Forge\last-epoch-data\exports_json\set_bonuses.json")
DEFAULT_ITEM_BASE_BUNDLE = ROOT / "docs" / "generated" / "v2_item_base_bundle.json"
DEFAULT_UNIQUE_OUTPUT = ROOT / "docs" / "generated" / "v2_unique_bundle.json"
DEFAULT_SET_OUTPUT = ROOT / "docs" / "generated" / "v2_set_bundle.json"
DEFAULT_VALIDATION_OUTPUT = ROOT / "docs" / "generated" / "v2_unique_set_validation_report.json"
DEFAULT_UNSUPPORTED_OUTPUT = ROOT / "docs" / "generated" / "v2_unique_set_unsupported_report.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_UNIQUE_SET_MIGRATION.md"
SPECIAL_MECHANIC_CLASSIFICATIONS = {
    "trusted_modifier",
    "partial_modifier",
    "text_only_effect",
    "scripted_runtime_behavior",
    "unsupported_special_behavior",
    "unknown",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build v2 unique and set item bundles.")
    parser.add_argument("--source-uniques", type=Path, default=DEFAULT_SOURCE_UNIQUES)
    parser.add_argument("--source-set-bonuses", type=Path, default=DEFAULT_SOURCE_SET_BONUSES)
    parser.add_argument("--item-base-bundle", type=Path, default=DEFAULT_ITEM_BASE_BUNDLE)
    parser.add_argument("--unique-output", type=Path, default=DEFAULT_UNIQUE_OUTPUT)
    parser.add_argument("--set-output", type=Path, default=DEFAULT_SET_OUTPUT)
    parser.add_argument("--validation-output", type=Path, default=DEFAULT_VALIDATION_OUTPUT)
    parser.add_argument("--unsupported-output", type=Path, default=DEFAULT_UNSUPPORTED_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def build_v2_unique_set_bundles(
    source_uniques: Path,
    source_set_bonuses: Path,
    item_base_bundle_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    source = _read_unique_source(source_uniques)
    set_bonus_source = _read_set_bonus_source(source_set_bonuses)
    base_index = _item_base_index(item_base_bundle_path)

    uniques = [
        _unique_record(source_uniques, source, record, base_index)
        for record in source.get("uniques") or []
        if isinstance(record, dict)
    ]
    set_items = [
        _set_item_record(source_uniques, source, record, base_index)
        for record in source.get("setItems") or []
        if isinstance(record, dict)
    ]
    set_groups = _set_group_records(source_uniques, source_set_bonuses, source, set_bonus_source, set_items)
    set_bonuses = _set_bonus_records(source_set_bonuses, set_bonus_source)

    validation = validate_v2_unique_set_records(uniques, set_groups, set_items, set_bonuses, set(base_index.values()))
    unsupported = unsupported_special_behavior_report(uniques, set_groups, set_items, set_bonuses)
    unique_bundle = {
        "schema_version": "v2.unique_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_uniques_path": str(source_uniques),
        "source_metadata": source.get("_meta", {}),
        "summary": _unique_summary(uniques, validation),
        "records": {"uniques": uniques},
        "metadata": _metadata(),
    }
    set_bundle = {
        "schema_version": "v2.set_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_uniques_path": str(source_uniques),
        "source_set_bonuses_path": str(source_set_bonuses),
        "source_metadata": {
            "uniques": source.get("_meta", {}),
            "set_bonuses": set_bonus_source.get("_meta", {}),
        },
        "summary": _set_summary(set_groups, set_items, set_bonuses, validation),
        "records": {
            "sets": set_groups,
            "set_items": set_items,
            "set_bonuses": set_bonuses,
        },
        "metadata": _metadata(),
    }
    return unique_bundle, set_bundle, validation, unsupported


def validate_v2_unique_set_records(
    uniques: list[dict[str, Any]],
    set_groups: list[dict[str, Any]],
    set_items: list[dict[str, Any]],
    set_bonuses: list[dict[str, Any]],
    item_base_ids: set[str] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    item_base_ids = item_base_ids or set()
    unique_ids = _validate_canonical_records(uniques, "unique", errors)
    set_group_ids = _validate_canonical_records(set_groups, "set_group", errors)
    set_item_ids = _validate_canonical_records(set_items, "set_item", errors)
    bonus_ids = _validate_canonical_records(set_bonuses, "set_bonus", errors)
    del unique_ids, set_item_ids, bonus_ids

    for record in uniques:
        _validate_claimed_base_link(record, item_base_ids, errors)
        _validate_modifier_rows(record, errors)
        _validate_special_classification(record, errors)
    for record in set_items:
        set_id = record.get("set_group_id")
        if not set_id:
            errors.append(_error(record.get("canonical_id"), "missing_set_group_id", "Set item must include set_group_id."))
        elif set_id not in set_group_ids:
            errors.append(_error(record.get("canonical_id"), "set_group_link_missing", f"Set group is missing: {set_id}"))
        _validate_claimed_base_link(record, item_base_ids, errors)
        _validate_modifier_rows(record, errors)
        _validate_special_classification(record, errors)
    for record in set_bonuses:
        set_id = record.get("set_group_id")
        if not set_id:
            errors.append(_error(record.get("canonical_id"), "missing_set_group_id", "Set bonus must include set_group_id."))
        elif set_id not in set_group_ids:
            errors.append(_error(record.get("canonical_id"), "set_bonus_group_missing", f"Set bonus references missing set group: {set_id}"))
        _validate_modifier_rows(record, errors)
        _validate_special_classification(record, errors)
    for record in set_groups:
        if record.get("canonical_id") != record.get("set_group_id"):
            errors.append(_error(record.get("canonical_id"), "set_group_id_conflict", "Set group canonical_id and set_group_id must match."))

    return {
        "summary": {
            "unique_count": len(uniques),
            "set_group_count": len(set_groups),
            "set_item_count": len(set_items),
            "set_bonus_count": len(set_bonuses),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "duplicate_unique_id_count": _count_code(errors, "duplicate_unique_id"),
            "duplicate_set_item_id_count": _count_code(errors, "duplicate_set_item_id"),
            "duplicate_set_group_id_count": _count_code(errors, "duplicate_set_group_id"),
            "missing_provenance_count": _count_code(errors, "missing_provenance"),
            "missing_support_status_count": _count_code(errors, "missing_support_status"),
            "invalid_trust_level_count": _count_code(errors, "invalid_trust_level"),
            "missing_base_link_count": _count_code(errors, "base_item_link_missing"),
            "set_group_link_missing_count": _count_code(errors, "set_group_link_missing"),
            "set_bonus_group_missing_count": _count_code(errors, "set_bonus_group_missing"),
            "unsupported_stable_calculation_count": _count_code(errors, "unsupported_stable_calculation"),
            "stable_calculable_count": 0,
            "production_consumed": False,
        },
        "errors": errors,
        "warnings": warnings,
        "metadata": _metadata(),
    }


def unsupported_special_behavior_report(
    uniques: list[dict[str, Any]],
    set_groups: list[dict[str, Any]],
    set_items: list[dict[str, Any]],
    set_bonuses: list[dict[str, Any]],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for kind, collection in (
        ("unique", uniques),
        ("set_group", set_groups),
        ("set_item", set_items),
        ("set_bonus", set_bonuses),
    ):
        for record in collection:
            classification = record.get("special_mechanic_classification")
            text_evidence = (
                record.get("tooltip_text")
                or record.get("unique_effect_text")
                or record.get("bonus_text")
                or record.get("description_text")
                or []
            )
            if classification == "partial_modifier" and not text_evidence:
                continue
            records.append({
                "record_type": kind,
                "canonical_id": record.get("canonical_id"),
                "display_name": record.get("display_name"),
                "special_mechanic_classification": classification,
                "support_status": record.get("support_status"),
                "text_evidence_count": len(text_evidence),
                "notes": record.get("notes") or record.get("warnings") or [],
            })
    counts = Counter(record["special_mechanic_classification"] for record in records)
    return {
        "summary": {
            "unsupported_or_text_only_count": len(records),
            "classification_counts": dict(sorted(counts.items())),
            "production_consumed": False,
        },
        "records": records,
        "metadata": _metadata(),
    }


def render_markdown(
    unique_bundle: dict[str, Any],
    set_bundle: dict[str, Any],
    validation: dict[str, Any],
    unsupported: dict[str, Any],
    *,
    command: str,
) -> str:
    unique_summary = unique_bundle["summary"]
    set_summary = set_bundle["summary"]
    unique_examples = "\n".join(
        f"| `{record['canonical_id']}` | {record['display_name']} | {record['item_type']} | {record['special_mechanic_classification']} | {len(record['modifier_rows'])} |"
        for record in unique_bundle["records"]["uniques"][:15]
    )
    set_examples = "\n".join(
        f"| `{record['canonical_id']}` | {record['display_name']} | `{record['set_group_id']}` | {record['special_mechanic_classification']} | {len(record['modifier_rows'])} |"
        for record in set_bundle["records"]["set_items"][:15]
    )
    return f"""# v2 Unique and Set Migration

## Purpose

Phase 5 creates read-only canonical unique and set item bundles on top of the v2 contracts and the Phase 4 item base infrastructure. It preserves extracted modifier rows, set membership, base links where available, and text-only/special effect evidence without simulating unique or set mechanics.

This phase does not remap planner behavior, implement special runtime behavior, or mark unique/set records as stable planner inputs.

## Generation Command

```powershell
{command}
```

## Summary

- Unique count: {unique_summary["unique_count"]}
- Set group count: {set_summary["set_group_count"]}
- Set item count: {set_summary["set_item_count"]}
- Set bonus count: {set_summary["set_bonus_count"]}
- Stable-calculable count: 0
- Validation errors: {validation["summary"]["error_count"]}
- Validation warnings: {validation["summary"]["warning_count"]}
- Unsupported/text-only/special behavior records: {unsupported["summary"]["unsupported_or_text_only_count"]}
- Production consumed: false

## Unique Classification Counts

| Classification | Count |
| --- | ---: |
{_count_rows(unique_summary["special_mechanic_classification_counts"])}

## Set Classification Counts

| Classification | Count |
| --- | ---: |
{_count_rows(set_summary["special_mechanic_classification_counts"])}

## Unsupported and Text-Only Findings

| Classification | Count |
| --- | ---: |
{_count_rows(unsupported["summary"]["classification_counts"])}

Tooltip and description text is retained as display/debug evidence only. It is not converted into calculated mechanics.

## Example Uniques

| Canonical ID | Display name | Item type | Classification | Modifier rows |
| --- | --- | --- | --- | ---: |
{unique_examples}

## Example Set Items

| Canonical ID | Display name | Set group | Classification | Modifier rows |
| --- | --- | --- | --- | ---: |
{set_examples}

## Migration Implications

- Unique and set records are available for experimental lookup and debug inspection.
- Structured modifier rows remain `partial`; value-scale and modifier normalization are unresolved.
- Text-only and special behavior remains displayable but is not calculated.
- Existing planner and `/api/ref/uniques` behavior remain unchanged.

## Deferred

- Runtime simulation for unique and set special mechanics.
- Stable modifier normalization and value-scale policy.
- Planner, crafting, stat aggregation, and simulation consumption.
- Idol, passive, and skill infrastructure.

## Checkpoint 5

Checkpoint 5 is ready for review when generated bundles, validation reports, unsupported report, repository, routes, debug page, and focused tests pass.
"""


def _unique_record(source_path: Path, payload: dict[str, Any], record: dict[str, Any], base_index: dict[str, str]) -> dict[str, Any]:
    source_id = f"unique:{record.get('id')}"
    canonical_id = f"unique:{_id_part(record.get('id'))}"
    base_item_id = _base_link(record, base_index)
    modifiers = _modifier_rows(source_path, payload, record.get("mods") or [], source_id, "unique_modifier")
    tooltip_text = _tooltip_text(record)
    classification = _special_classification(modifiers, tooltip_text)
    return _item_like_record(
        source_path,
        payload,
        record,
        canonical_id=canonical_id,
        source_id=source_id,
        provenance_type="unique",
        base_item_id=base_item_id,
        modifier_rows=modifiers,
        tooltip_text=tooltip_text,
        special_mechanic_classification=classification,
        extra={
            "unique_effect_text": tooltip_text,
            "implicit_links": _implicit_links(record, base_item_id),
            "legendary_type": record.get("legendaryType"),
            "can_drop_randomly": record.get("canDropRandomly"),
            "special_mechanic_notes": _special_notes(classification),
        },
    )


def _set_item_record(source_path: Path, payload: dict[str, Any], record: dict[str, Any], base_index: dict[str, str]) -> dict[str, Any]:
    set_group_id = _set_group_id(record.get("setId"))
    source_id = f"set_item:{record.get('id')}"
    canonical_id = f"set_item:{_id_part(record.get('id'))}"
    base_item_id = _base_link(record, base_index)
    modifiers = _modifier_rows(source_path, payload, record.get("mods") or [], source_id, "set_item_modifier")
    tooltip_text = _tooltip_text(record)
    classification = _special_classification(modifiers, tooltip_text)
    return _item_like_record(
        source_path,
        payload,
        record,
        canonical_id=canonical_id,
        source_id=source_id,
        provenance_type="set_item",
        base_item_id=base_item_id,
        modifier_rows=modifiers,
        tooltip_text=tooltip_text,
        special_mechanic_classification=classification,
        extra={
            "set_group_id": set_group_id,
            "set_group_display_name": None,
            "set_id": set_group_id,
            "bonus_text": tooltip_text,
            "implicit_links": _implicit_links(record, base_item_id),
            "special_mechanic_notes": _special_notes(classification),
        },
    )


def _item_like_record(
    source_path: Path,
    payload: dict[str, Any],
    record: dict[str, Any],
    *,
    canonical_id: str,
    source_id: str,
    provenance_type: str,
    base_item_id: str | None,
    modifier_rows: list[dict[str, Any]],
    tooltip_text: list[str],
    special_mechanic_classification: str,
    extra: dict[str, Any],
) -> dict[str, Any]:
    base = record.get("resolvedBaseItem") if isinstance(record.get("resolvedBaseItem"), dict) else {}
    subtype = base.get("subType") if isinstance(base.get("subType"), dict) else {}
    item_type = str(record.get("baseType") or base.get("type") or "unknown").lower()
    modifier_refs = [_modifier_ref(row) for row in modifier_rows]
    warnings = ["Unique/set record is not stable planner-consumed in Phase 5."]
    if base_item_id is None:
        warnings.append("No v2 item base link was established from extracted base identifiers.")
    if special_mechanic_classification != "partial_modifier":
        warnings.append("Special behavior is retained for display/debug only.")
    return {
        "canonical_id": canonical_id,
        "display_name": record.get("displayName") or record.get("name") or canonical_id,
        "source_id": source_id,
        "source_file": str(source_path),
        "patch_version": _game_version(payload),
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, source_id, provenance_type, payload, record),
        "base_item_id": base_item_id,
        "item_category": "equipment",
        "item_type": item_type,
        "subtype": subtype.get("name") or (record.get("subTypes") or [None])[0],
        "equipment_slot": item_type,
        "slot": item_type,
        "classification": _item_classification(item_type),
        "class_restrictions": _restriction_values(record.get("classRequirement") or subtype.get("classRequirement")),
        "mastery_restrictions": _restriction_values(record.get("subClassRequirement") or subtype.get("subClassRequirement")),
        "requirements": {
            "level": record.get("levelRequirement") or subtype.get("levelRequirement"),
            "attributes": {},
            "class": record.get("classRequirement") or subtype.get("classRequirement"),
            "mastery": record.get("subClassRequirement") or subtype.get("subClassRequirement"),
        },
        "level_requirement": record.get("levelRequirement") or subtype.get("levelRequirement"),
        "attribute_requirements": {},
        "modifier_references": modifier_refs,
        "modifier_rows": modifier_rows,
        "implicit_ids": [],
        "tooltip_text": tooltip_text,
        "lore_text": record.get("loreText"),
        "special_mechanic_classification": special_mechanic_classification,
        "stable_calculable": False,
        "warnings": warnings,
        "raw_reference": {
            "id": record.get("id"),
            "name": record.get("name"),
            "baseType": record.get("baseType"),
            "subTypes": record.get("subTypes"),
            "resolutionStatus": record.get("resolutionStatus"),
            "resolvedBaseItem": record.get("resolvedBaseItem"),
        },
        "normalized_fields": {"modifier_references": modifier_refs},
        "consumer_safe_fields": {
            "display_name": record.get("displayName") or record.get("name") or canonical_id,
            "support_status": SupportStatus.PARTIAL.value,
            "stable_calculable": False,
            "special_mechanic_classification": special_mechanic_classification,
        },
        **extra,
    }


def _set_group_records(
    unique_source_path: Path,
    set_bonus_source_path: Path,
    unique_source: dict[str, Any],
    set_bonus_source: dict[str, Any],
    set_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    item_ids_by_set: dict[str, list[str]] = defaultdict(list)
    names_by_set: dict[str, str] = {}
    for item in set_items:
        set_group_id = str(item["set_group_id"])
        item_ids_by_set[set_group_id].append(item["canonical_id"])
    for group in set_bonus_source.get("setBonuses") or []:
        if not isinstance(group, dict):
            continue
        set_group_id = _set_group_id(group.get("setId"))
        if group.get("setName"):
            names_by_set[set_group_id] = str(group["setName"])
    groups: list[dict[str, Any]] = []
    for set_group_id in sorted(item_ids_by_set, key=lambda value: int(value.split(":")[-1]) if value.split(":")[-1].isdigit() else value):
        source_id = f"set_group:{set_group_id.split(':')[-1]}"
        display_name = names_by_set.get(set_group_id) or f"Set {set_group_id.split(':')[-1]}"
        groups.append({
            "canonical_id": set_group_id,
            "display_name": display_name,
            "source_id": source_id,
            "source_file": str(set_bonus_source_path),
            "patch_version": _game_version(unique_source),
            "support_status": SupportStatus.PARTIAL.value,
            "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
            "provenance": {
                "source_path": str(set_bonus_source_path),
                "source_type": "set_group",
                "source_id": source_id,
                "extraction_method": "last_epoch_set_bonus_export",
                "patch_version": _game_version(unique_source),
                "schema_version": "v2.unique_set.1",
                "notes": ["Generated from extracted set item and set bonus data."],
                "raw_reference": {"setId": set_group_id.split(":")[-1]},
            },
            "set_group_id": set_group_id,
            "set_group_display_name": display_name,
            "item_ids": sorted(item_ids_by_set[set_group_id]),
            "bonus_ids": [],
            "bonus_modifier_references": [],
            "bonus_text": [],
            "special_mechanic_classification": "unknown",
            "stable_calculable": False,
            "warnings": ["Set group is not stable planner-consumed in Phase 5."],
            "raw_reference": {"setId": set_group_id.split(":")[-1]},
            "normalized_fields": {},
            "consumer_safe_fields": {
                "display_name": display_name,
                "support_status": SupportStatus.PARTIAL.value,
                "stable_calculable": False,
            },
        })
    bonus_ids_by_set: dict[str, list[str]] = defaultdict(list)
    bonus_text_by_set: dict[str, list[str]] = defaultdict(list)
    bonus_refs_by_set: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for bonus in _set_bonus_records(set_bonus_source_path, set_bonus_source):
        bonus_ids_by_set[bonus["set_group_id"]].append(bonus["canonical_id"])
        bonus_text_by_set[bonus["set_group_id"]].extend(bonus.get("description_text") or [])
        bonus_refs_by_set[bonus["set_group_id"]].extend(bonus.get("modifier_references") or [])
    for group in groups:
        group["bonus_ids"] = bonus_ids_by_set[group["set_group_id"]]
        group["bonus_text"] = bonus_text_by_set[group["set_group_id"]]
        group["bonus_modifier_references"] = bonus_refs_by_set[group["set_group_id"]]
        group["special_mechanic_classification"] = _group_classification(group)
    return groups


def _set_bonus_records(source_path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for group in payload.get("setBonuses") or []:
        if not isinstance(group, dict):
            continue
        set_group_id = _set_group_id(group.get("setId"))
        for index, bonus in enumerate(group.get("bonuses") or []):
            if not isinstance(bonus, dict):
                continue
            source_id = f"set_bonus:{group.get('setId')}:{index}"
            canonical_id = f"set_bonus:{_id_part(group.get('setId'))}:{index}"
            modifier_rows = []
            if isinstance(bonus.get("mod"), dict):
                modifier_rows = _modifier_rows(source_path, payload, [bonus["mod"]], source_id, "set_bonus_modifier")
            description_text = _bonus_text(bonus)
            classification = _special_classification(modifier_rows, description_text)
            records.append({
                "canonical_id": canonical_id,
                "display_name": f"{group.get('setName') or set_group_id} {bonus.get('piecesRequired')} piece bonus",
                "source_id": source_id,
                "source_file": str(source_path),
                "patch_version": _game_version(payload),
                "support_status": SupportStatus.PARTIAL.value,
                "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
                "provenance": {
                    "source_path": str(source_path),
                    "source_type": "set_bonus",
                    "source_id": source_id,
                    "extraction_method": "last_epoch_set_bonus_export",
                    "patch_version": _game_version(payload),
                    "schema_version": "v2.unique_set.1",
                    "notes": ["Generated from extracted set bonus data; text descriptions are not inferred as mechanics."],
                    "raw_reference": {"setId": group.get("setId"), "bonus_index": index},
                },
                "set_group_id": set_group_id,
                "set_group_display_name": group.get("setName"),
                "required_pieces": bonus.get("piecesRequired"),
                "description_text": description_text,
                "modifier_references": [_modifier_ref(row) for row in modifier_rows],
                "modifier_rows": modifier_rows,
                "special_mechanic_classification": classification,
                "stable_calculable": False,
                "warnings": ["Set bonus is not stable planner-consumed in Phase 5."],
                "raw_reference": {"setId": group.get("setId"), "bonus_index": index, "kind": bonus.get("kind")},
                "normalized_fields": {"modifier_references": [_modifier_ref(row) for row in modifier_rows]},
                "consumer_safe_fields": {
                    "display_name": f"{group.get('setName') or set_group_id} {bonus.get('piecesRequired')} piece bonus",
                    "support_status": SupportStatus.PARTIAL.value,
                    "stable_calculable": False,
                    "special_mechanic_classification": classification,
                },
            })
    return records


def _modifier_rows(source_path: Path, payload: dict[str, Any], mods: list[Any], source_id: str, source_type: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, mod in enumerate(mods):
        if not isinstance(mod, dict):
            continue
        modifier_id = f"{source_type}:{source_id}:{index}".replace(":", "_", 1)
        source_modifier_id = f"{source_id}:modifier:{index}"
        row = {
            "modifier_id": modifier_id,
            "property": mod.get("property"),
            "property_path": _property_path(mod),
            "modifier_type": mod.get("modifierType"),
            "value_min": mod.get("value"),
            "value_max": mod.get("maxValue", mod.get("value")),
            "tags": [str(tag) for tag in mod.get("tags") or []],
            "special_tag": mod.get("specialTag", mod.get("extraTag")),
            "extra_tag": mod.get("extraTag"),
            "can_roll": mod.get("canRoll"),
            "roll_id": mod.get("rollId"),
            "hide_in_tooltip": mod.get("hideInTooltip"),
            "support_status": SupportStatus.PARTIAL.value,
            "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
            "stable_calculable": False,
            "provenance": {
                "source_path": str(source_path),
                "source_type": source_type,
                "source_id": source_modifier_id,
                "extraction_method": "last_epoch_unique_set_export",
                "patch_version": _game_version(payload),
                "schema_version": "v2.unique_set.1",
                "notes": ["Value scale remains source-preserved; stable normalization is deferred."],
                "raw_reference": {"modifier_index": index, "property": mod.get("property")},
            },
        }
        rows.append(row)
    return rows


def _validate_canonical_records(records: list[dict[str, Any]], kind: str, errors: list[dict[str, Any]]) -> set[str]:
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
        if record.get("stable_calculable") is True or record.get("support_status") == SupportStatus.TRUSTED.value:
            errors.append(_error(canonical_id, "unsupported_stable_calculation", "Phase 5 records must not be stable-calculable."))
    return seen


def _validate_claimed_base_link(record: dict[str, Any], item_base_ids: set[str], errors: list[dict[str, Any]]) -> None:
    base_id = record.get("base_item_id")
    if base_id and item_base_ids and base_id not in item_base_ids:
        errors.append(_error(record.get("canonical_id"), "base_item_link_missing", f"Claimed base item is missing: {base_id}"))


def _validate_modifier_rows(record: dict[str, Any], errors: list[dict[str, Any]]) -> None:
    for modifier in record.get("modifier_rows") or []:
        if not isinstance(modifier, dict):
            errors.append(_error(record.get("canonical_id"), "invalid_modifier_row", "Modifier row must be an object."))
            continue
        if not modifier.get("provenance"):
            errors.append(_error(record.get("canonical_id"), "modifier_missing_provenance", "Modifier row is missing provenance."))
        if not modifier.get("support_status"):
            errors.append(_error(record.get("canonical_id"), "modifier_missing_support_status", "Modifier row is missing support status."))
        if modifier.get("stable_calculable") is True:
            errors.append(_error(record.get("canonical_id"), "unsupported_stable_calculation", "Modifier row is not stable-calculable in Phase 5."))


def _validate_special_classification(record: dict[str, Any], errors: list[dict[str, Any]]) -> None:
    if record.get("special_mechanic_classification") not in SPECIAL_MECHANIC_CLASSIFICATIONS:
        errors.append(_error(record.get("canonical_id"), "invalid_special_mechanic_classification", "Special mechanic classification is invalid."))


def _read_unique_source(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"unique export not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("uniques"), list) or not isinstance(data.get("setItems"), list):
        raise ValueError("unique export must contain uniques and setItems lists")
    return data


def _read_set_bonus_source(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"set bonus export not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("setBonuses"), list):
        raise ValueError("set bonus export must contain setBonuses list")
    return data


def _item_base_index(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    index: dict[str, str] = {}
    for record in payload.get("records", {}).get("item_bases", []):
        raw = record.get("raw_reference") if isinstance(record, dict) else {}
        key = _base_key(raw.get("baseTypeID"), raw.get("subTypeID"))
        if key:
            index[key] = record["canonical_id"]
    return index


def _base_link(record: dict[str, Any], base_index: dict[str, str]) -> str | None:
    resolved = record.get("resolvedBaseItem") if isinstance(record.get("resolvedBaseItem"), dict) else {}
    subtype = resolved.get("subType") if isinstance(resolved.get("subType"), dict) else {}
    key = _base_key(resolved.get("baseTypeID"), subtype.get("subTypeID"))
    if key and key in base_index:
        return base_index[key]
    base_type_id = resolved.get("baseTypeID")
    for subtype_id in record.get("subTypes") or []:
        key = _base_key(base_type_id, subtype_id)
        if key and key in base_index:
            return base_index[key]
    return None


def _base_key(base_type_id: Any, subtype_id: Any) -> str | None:
    if base_type_id is None or subtype_id is None:
        return None
    return f"{base_type_id}:{subtype_id}"


def _metadata() -> dict[str, Any]:
    return {
        "phase": "phase_5_unique_set_infrastructure",
        "read_only": True,
        "experimental": True,
        "production_consumer": False,
        "production_safe": False,
        "stable_planner_consumed": False,
        "uses_canonical_contracts": True,
    }


def _provenance(source_path: Path, source_id: str, source_type: str, payload: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_path": str(source_path),
        "source_type": source_type,
        "source_id": source_id,
        "extraction_method": "last_epoch_unique_set_export",
        "patch_version": _game_version(payload),
        "schema_version": "v2.unique_set.1",
        "notes": ["Generated from extracted unique/set data; tooltip text is not inferred as mechanics."],
        "raw_reference": {"id": record.get("id"), "name": record.get("name")},
    }


def _unique_summary(records: list[dict[str, Any]], validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "unique_count": len(records),
        "support_status_counts": dict(sorted(Counter(record["support_status"] for record in records).items())),
        "trust_level_counts": dict(sorted(Counter(record["trust_level"] for record in records).items())),
        "item_type_counts": dict(sorted(Counter(record["item_type"] for record in records).items())),
        "special_mechanic_classification_counts": dict(sorted(Counter(record["special_mechanic_classification"] for record in records).items())),
        "records_with_base_links_count": sum(1 for record in records if record.get("base_item_id")),
        "records_with_tooltip_text_count": sum(1 for record in records if record.get("tooltip_text")),
        "modifier_row_count": sum(len(record.get("modifier_rows") or []) for record in records),
        "stable_calculable_count": 0,
        "validation_error_count": validation["summary"]["error_count"],
        "production_consumed": False,
    }


def _set_summary(groups: list[dict[str, Any]], items: list[dict[str, Any]], bonuses: list[dict[str, Any]], validation: dict[str, Any]) -> dict[str, Any]:
    all_records = groups + items + bonuses
    return {
        "set_group_count": len(groups),
        "set_item_count": len(items),
        "set_bonus_count": len(bonuses),
        "support_status_counts": dict(sorted(Counter(record["support_status"] for record in all_records).items())),
        "trust_level_counts": dict(sorted(Counter(record["trust_level"] for record in all_records).items())),
        "item_type_counts": dict(sorted(Counter(record.get("item_type", "set_group_or_bonus") for record in items).items())),
        "special_mechanic_classification_counts": dict(sorted(Counter(record["special_mechanic_classification"] for record in all_records).items())),
        "set_items_with_base_links_count": sum(1 for record in items if record.get("base_item_id")),
        "set_bonuses_with_modifier_rows_count": sum(1 for record in bonuses if record.get("modifier_rows")),
        "modifier_row_count": sum(len(record.get("modifier_rows") or []) for record in items + bonuses),
        "stable_calculable_count": 0,
        "validation_error_count": validation["summary"]["error_count"],
        "production_consumed": False,
    }


def _tooltip_text(record: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for entry in record.get("tooltipDescriptions") or []:
        if not isinstance(entry, dict):
            continue
        for key in ("text", "altText"):
            value = entry.get(key)
            if value:
                values.append(str(value))
    return values


def _bonus_text(bonus: dict[str, Any]) -> list[str]:
    values = []
    for key in ("text", "altText"):
        if bonus.get(key):
            values.append(str(bonus[key]))
    return values


def _special_classification(modifier_rows: list[dict[str, Any]], text: list[str]) -> str:
    if modifier_rows:
        return "partial_modifier"
    if text:
        return "text_only_effect"
    return "unknown"


def _group_classification(group: dict[str, Any]) -> str:
    if group.get("bonus_modifier_references"):
        return "partial_modifier"
    if group.get("bonus_text"):
        return "text_only_effect"
    return "unknown"


def _special_notes(classification: str) -> list[str]:
    if classification == "partial_modifier":
        return ["Structured modifier rows exist but remain partial until value normalization is solved."]
    if classification == "text_only_effect":
        return ["Text effect is display/debug evidence only and is not calculated."]
    return ["No deterministic modifier or text effect was available in extracted data."]


def _modifier_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "modifier_id": row.get("modifier_id"),
        "property": row.get("property"),
        "property_path": row.get("property_path"),
        "source_record_id": row.get("provenance", {}).get("source_id"),
    }


def _implicit_links(record: dict[str, Any], base_item_id: str | None) -> list[dict[str, Any]]:
    return [
        {
            "base_item_id": base_item_id,
            "implicit_index": index,
            "property": mod.get("property"),
            "modifier_type": mod.get("modifierType"),
        }
        for index, mod in enumerate(record.get("resolvedImplicitMods") or [])
        if isinstance(mod, dict)
    ]


def _property_path(mod: dict[str, Any]) -> str:
    parts = [mod.get("modifierType"), mod.get("property")]
    parts.extend(str(tag) for tag in mod.get("tags") or [] if str(tag) != "None")
    if mod.get("specialTag") not in (None, 0):
        parts.append(f"special:{mod.get('specialTag')}")
    return ".".join(str(part) for part in parts if part not in (None, ""))


def _item_classification(item_type: str) -> str:
    if any(token in item_type for token in ("axe", "dagger", "mace", "sceptre", "sword", "wand", "staff", "bow", "crossbow", "spear", "fist")):
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


def _set_group_id(set_id: Any) -> str:
    return f"set:{_id_part(set_id)}"


def _id_part(value: Any) -> str:
    if value is None:
        return "unknown"
    return _slug(str(value))


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9._:-]+", "_", value.strip().lower())
    slug = slug.strip("._:-")
    return slug or "unknown"


def _game_version(payload: dict[str, Any]) -> str | None:
    meta = payload.get("_meta") or {}
    game_build = meta.get("game_build") if isinstance(meta, dict) else {}
    if isinstance(game_build, dict) and game_build.get("installPath"):
        return str(game_build["installPath"]).split("\\")[-1]
    return None


def _error(canonical_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"canonical_id": canonical_id, "code": code, "message": message}


def _count_code(errors: list[dict[str, Any]], code: str) -> int:
    return sum(1 for error in errors if error.get("code") == code)


def _count_rows(counts: dict[str, int]) -> str:
    if not counts:
        return "| none | 0 |"
    return "\n".join(f"| {key} | {value} |" for key, value in sorted(counts.items()))


def main() -> int:
    args = parse_args()
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_unique_set_bundles.py "
        f"--source-uniques {args.source_uniques} "
        f"--source-set-bonuses {args.source_set_bonuses} "
        f"--item-base-bundle {args.item_base_bundle} "
        f"--unique-output {args.unique_output} "
        f"--set-output {args.set_output} "
        f"--validation-output {args.validation_output} "
        f"--unsupported-output {args.unsupported_output} "
        f"--markdown-output {args.markdown_output}"
    )
    unique_bundle, set_bundle, validation, unsupported = build_v2_unique_set_bundles(
        args.source_uniques,
        args.source_set_bonuses,
        args.item_base_bundle,
    )
    for path, payload in (
        (args.unique_output, unique_bundle),
        (args.set_output, set_bundle),
        (args.validation_output, validation),
        (args.unsupported_output, unsupported),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(
        render_markdown(unique_bundle, set_bundle, validation, unsupported, command=command),
        encoding="utf-8",
    )
    print(json.dumps({
        "unique_count": unique_bundle["summary"]["unique_count"],
        "set_group_count": set_bundle["summary"]["set_group_count"],
        "set_item_count": set_bundle["summary"]["set_item_count"],
        "set_bonus_count": set_bundle["summary"]["set_bonus_count"],
        "validation_error_count": validation["summary"]["error_count"],
        "unsupported_or_text_only_count": unsupported["summary"]["unsupported_or_text_only_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
