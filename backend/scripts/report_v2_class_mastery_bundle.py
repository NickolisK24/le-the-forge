"""Generate the v2 canonical class/mastery bundle."""

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


DEFAULT_SOURCE_CLASSES = Path(r"D:\Forge\last-epoch-data\exports_json\classes.json")
DEFAULT_AFFIX_BUNDLE = ROOT / "docs" / "generated" / "v2_affix_bundle.json"
DEFAULT_ITEM_BASE_BUNDLE = ROOT / "docs" / "generated" / "v2_item_base_bundle.json"
DEFAULT_UNIQUE_BUNDLE = ROOT / "docs" / "generated" / "v2_unique_bundle.json"
DEFAULT_SET_BUNDLE = ROOT / "docs" / "generated" / "v2_set_bundle.json"
DEFAULT_IDOL_BUNDLE = ROOT / "docs" / "generated" / "v2_idol_bundle.json"
DEFAULT_IDOL_AFFIX_BUNDLE = ROOT / "docs" / "generated" / "v2_idol_affix_bundle.json"
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "v2_class_mastery_bundle.json"
DEFAULT_VALIDATION_OUTPUT = ROOT / "docs" / "generated" / "v2_class_mastery_validation_report.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_CLASS_MASTERY_MIGRATION.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the v2 class/mastery bundle.")
    parser.add_argument("--source-classes", type=Path, default=DEFAULT_SOURCE_CLASSES)
    parser.add_argument("--affix-bundle", type=Path, default=DEFAULT_AFFIX_BUNDLE)
    parser.add_argument("--item-base-bundle", type=Path, default=DEFAULT_ITEM_BASE_BUNDLE)
    parser.add_argument("--unique-bundle", type=Path, default=DEFAULT_UNIQUE_BUNDLE)
    parser.add_argument("--set-bundle", type=Path, default=DEFAULT_SET_BUNDLE)
    parser.add_argument("--idol-bundle", type=Path, default=DEFAULT_IDOL_BUNDLE)
    parser.add_argument("--idol-affix-bundle", type=Path, default=DEFAULT_IDOL_AFFIX_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validation-output", type=Path, default=DEFAULT_VALIDATION_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def build_v2_class_mastery_bundle(
    source_classes: Path,
    *,
    reference_bundle_paths: list[Path] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source = _read_json(source_classes, "class source")
    class_records: list[dict[str, Any]] = []
    mastery_records: list[dict[str, Any]] = []

    for raw_class in source.get("classes") or []:
        if not isinstance(raw_class, dict):
            continue
        class_id = _class_id(raw_class)
        mastery_ids: list[str] = []
        for index, raw_mastery in enumerate(raw_class.get("masteries") or []):
            if not isinstance(raw_mastery, dict) or index == 0:
                continue
            mastery_id = _mastery_id(raw_class, raw_mastery)
            mastery_ids.append(mastery_id)
            mastery_records.append(_mastery_record(source_classes, source, raw_class, raw_mastery, index, class_id, mastery_id))
        class_records.append(_class_record(source_classes, source, raw_class, class_id, mastery_ids))

    cross_reference = collect_class_mastery_cross_references(
        reference_bundle_paths or [
            DEFAULT_AFFIX_BUNDLE,
            DEFAULT_ITEM_BASE_BUNDLE,
            DEFAULT_UNIQUE_BUNDLE,
            DEFAULT_SET_BUNDLE,
            DEFAULT_IDOL_BUNDLE,
            DEFAULT_IDOL_AFFIX_BUNDLE,
        ],
        class_records,
        mastery_records,
    )
    _attach_restriction_coverage(class_records, mastery_records, cross_reference)
    validation = validate_v2_class_mastery_records(class_records, mastery_records, cross_reference)
    bundle = {
        "schema_version": "v2.class_mastery_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_classes_path": str(source_classes),
        "source_metadata": source.get("_meta", {}),
        "summary": _bundle_summary(class_records, mastery_records, validation, cross_reference),
        "records": {"classes": class_records, "masteries": mastery_records},
        "cross_reference": cross_reference,
        "metadata": _metadata(),
    }
    return bundle, validation


def validate_v2_class_mastery_records(
    classes: list[dict[str, Any]],
    masteries: list[dict[str, Any]],
    cross_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    class_ids = _validate_common_records(classes, "class", errors)
    mastery_ids = _validate_common_records(masteries, "mastery", errors)

    for record in classes:
        canonical_id = record.get("canonical_id")
        if not isinstance(record.get("mastery_ids"), list):
            errors.append(_error(canonical_id, "invalid_mastery_links", "Class mastery_ids must be a list."))
            continue
        for mastery_id in record.get("mastery_ids") or []:
            if mastery_id not in mastery_ids:
                errors.append(_error(canonical_id, "class_links_missing_mastery", f"Class links missing mastery {mastery_id}."))
        if not isinstance(record.get("known_restriction_labels"), list):
            errors.append(_error(canonical_id, "invalid_restriction_labels", "known_restriction_labels must be a list."))
        if record.get("manual_bridge") is True and record.get("trust_level") != TrustLevel.MANUAL_BRIDGE.value:
            errors.append(_error(canonical_id, "manual_bridge_not_marked", "Manual bridges must use trust_level manual_bridge."))
        if record.get("stable_calculable") is True:
            errors.append(_error(canonical_id, "unsupported_stable_calculation", "Classes are not stable-calculable in Phase 7."))

    for record in masteries:
        canonical_id = record.get("canonical_id")
        if record.get("class_id") not in class_ids:
            errors.append(_error(canonical_id, "mastery_parent_missing", f"Mastery parent class is missing: {record.get('class_id')}."))
        if not isinstance(record.get("known_restriction_labels"), list):
            errors.append(_error(canonical_id, "invalid_restriction_labels", "known_restriction_labels must be a list."))
        if record.get("manual_bridge") is True and record.get("trust_level") != TrustLevel.MANUAL_BRIDGE.value:
            errors.append(_error(canonical_id, "manual_bridge_not_marked", "Manual bridges must use trust_level manual_bridge."))
        if record.get("stable_calculable") is True:
            errors.append(_error(canonical_id, "unsupported_stable_calculation", "Masteries are not stable-calculable in Phase 7."))

    for label in (cross_reference or {}).get("unmapped_labels", []):
        warnings.append(_warning("cross_reference", "unmapped_restriction_label", f"Restriction label did not map to a class/mastery record: {label}."))

    return {
        "summary": {
            "class_count": len(classes),
            "mastery_count": len(masteries),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "duplicate_class_id_count": _count_code(errors, "duplicate_class_id"),
            "duplicate_mastery_id_count": _count_code(errors, "duplicate_mastery_id"),
            "missing_provenance_count": _count_code(errors, "missing_provenance"),
            "missing_support_status_count": _count_code(errors, "missing_support_status"),
            "invalid_trust_level_count": _count_code(errors, "invalid_trust_level"),
            "mastery_parent_missing_count": _count_code(errors, "mastery_parent_missing"),
            "class_links_missing_mastery_count": _count_code(errors, "class_links_missing_mastery"),
            "manual_bridge_not_marked_count": _count_code(errors, "manual_bridge_not_marked"),
            "manual_bridge_count": sum(1 for record in [*classes, *masteries] if record.get("trust_level") == TrustLevel.MANUAL_BRIDGE.value),
            "stable_calculable_count": 0,
            "production_consumed": False,
        },
        "errors": errors,
        "warnings": warnings,
        "cross_reference": cross_reference or {},
        "metadata": _metadata(),
    }


def collect_class_mastery_cross_references(
    bundle_paths: list[Path],
    classes: list[dict[str, Any]],
    masteries: list[dict[str, Any]],
) -> dict[str, Any]:
    class_lookup = {_normalize_label(record["display_name"]): record["canonical_id"] for record in classes}
    mastery_lookup = {_normalize_label(record["display_name"]): record["canonical_id"] for record in masteries}
    label_counts: Counter[str] = Counter()
    source_breakdown: dict[str, Counter[str]] = defaultdict(Counter)
    mapped_labels: dict[str, dict[str, Any]] = {}

    for path in bundle_paths:
        if not path.exists():
            continue
        payload = _read_json(path, "reference bundle")
        for collection_name, records in (payload.get("records") or {}).items():
            if not isinstance(records, list):
                continue
            source_key = f"{path.name}:{collection_name}"
            for record in records:
                if not isinstance(record, dict):
                    continue
                for label in _restriction_labels(record):
                    label_counts[label] += 1
                    source_breakdown[label][source_key] += 1

    for label, count in sorted(label_counts.items()):
        normalized = _normalize_label(label)
        class_id = class_lookup.get(normalized)
        mastery_id = mastery_lookup.get(normalized)
        if class_id or mastery_id:
            mapped_labels[label] = {
                "label": label,
                "count": count,
                "mapped_class_id": class_id,
                "mapped_mastery_id": mastery_id,
                "source_breakdown": dict(sorted(source_breakdown[label].items())),
            }

    return {
        "restriction_label_count": sum(label_counts.values()),
        "unique_restriction_label_count": len(label_counts),
        "mapped_label_count": len(mapped_labels),
        "unmapped_label_count": len(label_counts) - len(mapped_labels),
        "labels": [
            {
                "label": label,
                "count": count,
                "mapped_class_id": mapped_labels.get(label, {}).get("mapped_class_id"),
                "mapped_mastery_id": mapped_labels.get(label, {}).get("mapped_mastery_id"),
                "source_breakdown": dict(sorted(source_breakdown[label].items())),
            }
            for label, count in sorted(label_counts.items())
        ],
        "mapped_labels": list(mapped_labels.values()),
        "unmapped_labels": [label for label in sorted(label_counts) if label not in mapped_labels],
    }


def render_markdown(bundle: dict[str, Any], validation: dict[str, Any], *, command: str) -> str:
    summary = bundle["summary"]
    class_rows = "\n".join(
        f"| `{record['canonical_id']}` | {record['display_name']} | {len(record['mastery_ids'])} | {', '.join(record['known_restriction_labels']) or 'None'} |"
        for record in bundle["records"]["classes"]
    )
    mastery_rows = "\n".join(
        f"| `{record['canonical_id']}` | {record['display_name']} | `{record['class_id']}` | {', '.join(record['known_restriction_labels']) or 'None'} |"
        for record in bundle["records"]["masteries"]
    )
    cross_rows = "\n".join(
        f"| {entry['label']} | {entry['count']} | `{entry.get('mapped_class_id') or ''}` | `{entry.get('mapped_mastery_id') or ''}` |"
        for entry in bundle["cross_reference"]["labels"]
    ) or "| None | 0 |  |  |"
    return f"""# v2 Class and Mastery Migration

## Purpose

Phase 7 creates a read-only canonical class/mastery bundle from the extracted class registry. The bundle is used for diagnostics, validation, and future class/mastery references only.

This phase does not implement passive trees, skill trees, planner remapping, or stable-calculable class behavior.

## Generation Command

```powershell
{command}
```

## Summary

- Class count: {summary["class_count"]}
- Mastery count: {summary["mastery_count"]}
- Restriction labels found in existing v2 bundles: {summary["unique_restriction_label_count"]}
- Restriction labels mapped to class/mastery records: {summary["mapped_restriction_label_count"]}
- Restriction labels unmapped: {summary["unmapped_restriction_label_count"]}
- Manual bridge count: {summary["manual_bridge_count"]}
- Stable-calculable count: 0
- Validation errors: {validation["summary"]["error_count"]}
- Validation warnings: {validation["summary"]["warning_count"]}
- Production consumed: false

## Classes

| Canonical ID | Display name | Masteries | Existing restriction labels |
| --- | --- | ---: | --- |
{class_rows}

## Masteries

| Canonical ID | Display name | Parent class | Existing restriction labels |
| --- | --- | --- | --- |
{mastery_rows}

## Cross-Reference Findings

| Restriction label | Count | Class mapping | Mastery mapping |
| --- | ---: | --- | --- |
{cross_rows}

Existing generated v2 affix, item, unique/set, and idol bundles were scanned for class/mastery restriction labels. The scan reports mappings only; it does not rewrite prior bundles.

## Manual Bridge Findings

Manual bridge records: {summary["manual_bridge_count"]}

The extracted class registry provided class and mastery records for this phase, so no manual bridge was needed. If later phases add temporary bridge records, they must use `trust_level: manual_bridge` and explain the source gap in provenance.

## Migration Implications

- Classes and masteries are available for experimental lookup and debug inspection.
- Records remain `partial` because passives, skills, and modifier normalization are not complete.
- Restriction labels from prior v2 bundles can now be audited against canonical class/mastery records.
- Existing planner, crafting, stat aggregation, and simulation behavior remain unchanged.

## Deferred

- Passive tree generation and validation.
- Skill tree generation and validation.
- Planner remapping to canonical class/mastery IDs.
- Stable planner eligibility for class/mastery-linked effects.

## Recommended Next Step

Proceed to Phase 8 passive infrastructure after Checkpoint 7 review.
"""


def write_outputs(bundle: dict[str, Any], validation: dict[str, Any], markdown: str, output: Path, validation_output: Path, markdown_output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    validation_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(markdown, encoding="utf-8")


def _class_record(source_path: Path, source: dict[str, Any], raw_class: dict[str, Any], canonical_id: str, mastery_ids: list[str]) -> dict[str, Any]:
    display_name = _display_name(raw_class)
    skill_source_ids = _class_skill_source_ids(raw_class)
    passive_tree_ids = [f"passive_tree:{_slug(raw_class.get('treeID'))}"] if raw_class.get("treeID") else []
    return {
        "canonical_id": canonical_id,
        "display_name": display_name,
        "source_id": f"class:{raw_class.get('id')}",
        "source_file": str(source_path),
        "patch_version": _patch_version(source),
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, f"class:{raw_class.get('id')}", "generated_from_game_data", "Extracted class registry record."),
        "source_class_id": raw_class.get("id"),
        "source_tree_id": raw_class.get("treeID"),
        "mastery_ids": mastery_ids,
        "passive_tree_ids": passive_tree_ids,
        "skill_ids": skill_source_ids,
        "linked_skill_source_ids": skill_source_ids,
        "linked_passive_tree_source_ids": [raw_class.get("treeID")] if raw_class.get("treeID") else [],
        "known_restriction_labels": [],
        "base_stats": raw_class.get("stats") or {},
        "stable_calculable": False,
        "manual_bridge": False,
        "warnings": [],
        "raw_reference": {"source_class_id": raw_class.get("id"), "treeID": raw_class.get("treeID")},
        "normalized_fields": {"canonical_kind": "class"},
        "consumer_safe_fields": {"planner_consumed": False, "debug_only": True},
    }


def _mastery_record(
    source_path: Path,
    source: dict[str, Any],
    raw_class: dict[str, Any],
    raw_mastery: dict[str, Any],
    source_index: int,
    class_id: str,
    mastery_id: str,
) -> dict[str, Any]:
    display_name = _display_name(raw_mastery)
    skill_source_ids = _mastery_skill_source_ids(raw_mastery)
    return {
        "canonical_id": mastery_id,
        "display_name": display_name,
        "source_id": f"class:{raw_class.get('id')}:mastery:{source_index}",
        "source_file": str(source_path),
        "patch_version": _patch_version(source),
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, f"class:{raw_class.get('id')}:mastery:{source_index}", "generated_from_game_data", "Extracted mastery entry nested under class registry record."),
        "source_class_id": raw_class.get("id"),
        "source_mastery_index": source_index,
        "source_mastery_id": raw_mastery.get("localizationKey") or raw_mastery.get("name"),
        "class_id": class_id,
        "passive_tree_ids": [],
        "skill_ids": skill_source_ids,
        "linked_skill_source_ids": skill_source_ids,
        "linked_passive_tree_source_ids": [],
        "known_restriction_labels": [],
        "stable_calculable": False,
        "manual_bridge": False,
        "warnings": [],
        "raw_reference": {
            "source_class_id": raw_class.get("id"),
            "source_mastery_index": source_index,
            "localizationKey": raw_mastery.get("localizationKey"),
            "masteryAbilityPathId": raw_mastery.get("masteryAbilityPathId"),
        },
        "normalized_fields": {"canonical_kind": "mastery"},
        "consumer_safe_fields": {"planner_consumed": False, "debug_only": True},
    }


def _attach_restriction_coverage(classes: list[dict[str, Any]], masteries: list[dict[str, Any]], cross_reference: dict[str, Any]) -> None:
    labels_by_class: dict[str, list[str]] = defaultdict(list)
    labels_by_mastery: dict[str, list[str]] = defaultdict(list)
    for entry in cross_reference.get("mapped_labels") or []:
        if entry.get("mapped_class_id"):
            labels_by_class[entry["mapped_class_id"]].append(entry["label"])
        if entry.get("mapped_mastery_id"):
            labels_by_mastery[entry["mapped_mastery_id"]].append(entry["label"])
    for record in classes:
        record["known_restriction_labels"] = sorted(labels_by_class.get(record["canonical_id"], []))
    for record in masteries:
        record["known_restriction_labels"] = sorted(labels_by_mastery.get(record["canonical_id"], []))


def _validate_common_records(records: list[dict[str, Any]], kind: str, errors: list[dict[str, Any]]) -> set[str]:
    seen: set[str] = set()
    ids: set[str] = set()
    for record in records:
        canonical_id = record.get("canonical_id")
        try:
            validate_canonical_id(canonical_id)
        except ValueError as exc:
            errors.append(_error(canonical_id, f"invalid_{kind}_id", str(exc)))
            continue
        if canonical_id in seen:
            errors.append(_error(canonical_id, f"duplicate_{kind}_id", f"Duplicate {kind} canonical_id."))
        seen.add(canonical_id)
        ids.add(canonical_id)
        if not record.get("display_name"):
            errors.append(_error(canonical_id, "missing_display_name", "display_name is required."))
        provenance = record.get("provenance")
        if not isinstance(provenance, dict) or not provenance.get("source_path") or not provenance.get("source_id"):
            errors.append(_error(canonical_id, "missing_provenance", "provenance.source_path and provenance.source_id are required."))
        if not record.get("support_status"):
            errors.append(_error(canonical_id, "missing_support_status", "support_status is required."))
        else:
            try:
                SupportStatus(str(record.get("support_status")))
            except ValueError:
                errors.append(_error(canonical_id, "invalid_support_status", "support_status is invalid."))
        try:
            TrustLevel(str(record.get("trust_level")))
        except ValueError:
            errors.append(_error(canonical_id, "invalid_trust_level", "trust_level is invalid."))
        if record.get("trust_level") in {TrustLevel.GAME_EXTRACTED.value, TrustLevel.GENERATED_FROM_GAME_DATA.value} and not record.get("source_file"):
            errors.append(_error(canonical_id, "missing_source_reference", "Generated/extracted records require source_file."))
    return ids


def _restriction_labels(record: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for key in ("class_restrictions", "mastery_restrictions"):
        values = record.get(key)
        if isinstance(values, list):
            labels.extend(str(value) for value in values if value not in (None, "", "Any"))
        elif values not in (None, "", "Any"):
            labels.append(str(values))
    return labels


def _bundle_summary(classes: list[dict[str, Any]], masteries: list[dict[str, Any]], validation: dict[str, Any], cross_reference: dict[str, Any]) -> dict[str, Any]:
    return {
        "class_count": len(classes),
        "mastery_count": len(masteries),
        "support_status_counts": dict(Counter(record["support_status"] for record in [*classes, *masteries])),
        "trust_level_counts": dict(Counter(record["trust_level"] for record in [*classes, *masteries])),
        "manual_bridge_count": validation["summary"]["manual_bridge_count"],
        "stable_calculable_count": 0,
        "unique_restriction_label_count": cross_reference["unique_restriction_label_count"],
        "mapped_restriction_label_count": cross_reference["mapped_label_count"],
        "unmapped_restriction_label_count": cross_reference["unmapped_label_count"],
        "validation_error_count": validation["summary"]["error_count"],
        "validation_warning_count": validation["summary"]["warning_count"],
        "production_consumed": False,
    }


def _class_id(raw_class: dict[str, Any]) -> str:
    return f"class:{_slug(_display_name(raw_class))}"


def _mastery_id(raw_class: dict[str, Any], raw_mastery: dict[str, Any]) -> str:
    return f"mastery:{_slug(_display_name(raw_class))}:{_slug(_display_name(raw_mastery))}"


def _display_name(record: dict[str, Any]) -> str:
    return str(record.get("displayName") or record.get("name") or record.get("localizationKey") or "Unknown")


def _class_skill_source_ids(raw_class: dict[str, Any]) -> list[str]:
    ids: set[int] = set()
    abilities = raw_class.get("abilities") or {}
    for value in abilities.get("defaultPathIds") or []:
        if isinstance(value, int) and value:
            ids.add(value)
    for value in abilities.get("knownPathIds") or []:
        if isinstance(value, int) and value:
            ids.add(value)
    for entry in abilities.get("unlockable") or []:
        if isinstance(entry, dict) and isinstance(entry.get("abilityPathId"), int) and entry.get("abilityPathId"):
            ids.add(entry["abilityPathId"])
    return [f"skill_path:{value}" for value in sorted(ids)]


def _mastery_skill_source_ids(raw_mastery: dict[str, Any]) -> list[str]:
    ids: set[int] = set()
    if isinstance(raw_mastery.get("masteryAbilityPathId"), int) and raw_mastery.get("masteryAbilityPathId"):
        ids.add(raw_mastery["masteryAbilityPathId"])
    for value in raw_mastery.get("abilityPathIds") or []:
        if isinstance(value, int) and value:
            ids.add(value)
    return [f"skill_path:{value}" for value in sorted(ids)]


def _provenance(source_path: Path, source_id: str, source_type: str, note: str) -> dict[str, Any]:
    return {
        "source_path": str(source_path),
        "source_id": source_id,
        "source_type": source_type,
        "extraction_method": "last_epoch_data_export",
        "notes": [note],
    }


def _patch_version(source: dict[str, Any]) -> str | None:
    install_path = str((source.get("_meta") or {}).get("game_build", {}).get("installPath") or "")
    return Path(install_path).name or None


def _metadata() -> dict[str, Any]:
    return {
        "source": "v2_class_mastery_bundle",
        "read_only": True,
        "experimental": True,
        "production_safe": False,
        "production_consumed": False,
    }


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return payload


def _slug(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def _normalize_label(value: Any) -> str:
    return _slug(value).replace("_", "")


def _error(record_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"record_id": record_id, "severity": "error", "code": code, "message": message}


def _warning(record_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"record_id": record_id, "severity": "warning", "code": code, "message": message}


def _count_code(entries: list[dict[str, Any]], code: str) -> int:
    return sum(1 for entry in entries if entry.get("code") == code)


def main() -> int:
    args = parse_args()
    reference_paths = [
        args.affix_bundle,
        args.item_base_bundle,
        args.unique_bundle,
        args.set_bundle,
        args.idol_bundle,
        args.idol_affix_bundle,
    ]
    bundle, validation = build_v2_class_mastery_bundle(args.source_classes, reference_bundle_paths=reference_paths)
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_class_mastery_bundle.py "
        f"--source-classes {args.source_classes} "
        f"--affix-bundle {args.affix_bundle} "
        f"--item-base-bundle {args.item_base_bundle} "
        f"--unique-bundle {args.unique_bundle} "
        f"--set-bundle {args.set_bundle} "
        f"--idol-bundle {args.idol_bundle} "
        f"--idol-affix-bundle {args.idol_affix_bundle} "
        f"--output {args.output} "
        f"--validation-output {args.validation_output} "
        f"--markdown-output {args.markdown_output}"
    )
    write_outputs(bundle, validation, render_markdown(bundle, validation, command=command), args.output, args.validation_output, args.markdown_output)
    print(json.dumps(bundle["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
