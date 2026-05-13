"""Generate the v2 canonical passive tree bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


DEFAULT_SOURCE_PASSIVES = Path(r"D:\Forge\last-epoch-data\exports_json\passive_trees.json")
DEFAULT_LAYOUT_PASSIVES = ROOT / "data" / "classes" / "passives.json"
DEFAULT_CLASS_MASTERY_BUNDLE = ROOT / "docs" / "generated" / "v2_class_mastery_bundle.json"
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "v2_passive_tree_bundle.json"
DEFAULT_VALIDATION_OUTPUT = ROOT / "docs" / "generated" / "v2_passive_tree_validation_report.json"
DEFAULT_UNSUPPORTED_OUTPUT = ROOT / "docs" / "generated" / "v2_passive_unsupported_report.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_PASSIVE_TREE_MIGRATION.md"

SPECIAL_BEHAVIOR_CLASSIFICATIONS = {
    "trusted_modifier",
    "partial_modifier",
    "text_only_effect",
    "scripted_runtime_behavior",
    "unsupported_special_behavior",
    "unknown",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the v2 passive tree bundle.")
    parser.add_argument("--source-passives", type=Path, default=DEFAULT_SOURCE_PASSIVES)
    parser.add_argument("--layout-passives", type=Path, default=DEFAULT_LAYOUT_PASSIVES)
    parser.add_argument("--class-mastery-bundle", type=Path, default=DEFAULT_CLASS_MASTERY_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validation-output", type=Path, default=DEFAULT_VALIDATION_OUTPUT)
    parser.add_argument("--unsupported-output", type=Path, default=DEFAULT_UNSUPPORTED_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def build_v2_passive_tree_bundle(
    source_passives: Path,
    layout_passives: Path,
    class_mastery_bundle: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source = _read_json(source_passives, "passive tree source")
    class_mastery = _read_json(class_mastery_bundle, "class/mastery bundle")
    layout = _read_layout(layout_passives)
    class_lookup, mastery_lookup, passive_tree_links = _class_mastery_lookups(class_mastery)
    trees: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []

    for raw_tree in source.get("passiveTrees") or []:
        if not isinstance(raw_tree, dict):
            continue
        tree_id = _tree_id(raw_tree)
        owner_class_id = class_lookup.get(_normalize(raw_tree.get("class")))
        tree_nodes: list[dict[str, Any]] = []
        for raw_node in raw_tree.get("nodes") or []:
            if not isinstance(raw_node, dict):
                continue
            node = _node_record(source_passives, layout_passives, raw_tree, raw_node, tree_id, owner_class_id, mastery_lookup, layout)
            tree_nodes.append(node)
            nodes.append(node)
        trees.append(_tree_record(source_passives, source, raw_tree, tree_id, owner_class_id, tree_nodes))

    cross_reference = _cross_reference_passive_links(trees, passive_tree_links)
    validation = validate_v2_passive_tree_records(trees, nodes, class_mastery, cross_reference)
    unsupported = build_unsupported_report(nodes)
    bundle = {
        "schema_version": "v2.passive_tree_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_passives_path": str(source_passives),
        "layout_passives_path": str(layout_passives),
        "class_mastery_bundle_path": str(class_mastery_bundle),
        "source_metadata": source.get("meta", {}),
        "summary": _bundle_summary(trees, nodes, validation, unsupported, cross_reference),
        "records": {"passive_trees": trees, "passive_nodes": nodes},
        "cross_reference": cross_reference,
        "metadata": _metadata(),
    }
    return bundle, validation, unsupported


def validate_v2_passive_tree_records(
    trees: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    class_mastery_bundle: dict[str, Any] | None = None,
    cross_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    tree_ids = _validate_common_records(trees, "passive_tree", errors)
    node_ids = _validate_common_records(nodes, "passive_node", errors)
    class_ids = {record.get("canonical_id") for record in (class_mastery_bundle or {}).get("records", {}).get("classes", [])}
    mastery_ids = {record.get("canonical_id") for record in (class_mastery_bundle or {}).get("records", {}).get("masteries", [])}

    for tree in trees:
        canonical_id = tree.get("canonical_id")
        if tree.get("owner_class_id") and tree.get("owner_class_id") not in class_ids:
            errors.append(_error(canonical_id, "passive_tree_missing_class_link", f"Missing owner class {tree.get('owner_class_id')}."))
        if tree.get("owner_mastery_id") and tree.get("owner_mastery_id") not in mastery_ids:
            errors.append(_error(canonical_id, "passive_tree_missing_mastery_link", f"Missing owner mastery {tree.get('owner_mastery_id')}."))
        if not isinstance(tree.get("node_ids"), list):
            errors.append(_error(canonical_id, "invalid_node_links", "Passive tree node_ids must be a list."))
        else:
            for node_id in tree.get("node_ids") or []:
                if node_id not in node_ids:
                    errors.append(_error(canonical_id, "passive_tree_links_missing_node", f"Passive tree links missing node {node_id}."))
        for edge in tree.get("edges") or []:
            if not isinstance(edge, list) or len(edge) != 2 or not all(isinstance(value, str) for value in edge):
                errors.append(_error(canonical_id, "invalid_edge_shape", "Passive tree edges must be [from_id, to_id] string pairs."))

    for node in nodes:
        canonical_id = node.get("canonical_id")
        if node.get("tree_id") not in tree_ids:
            errors.append(_error(canonical_id, "passive_node_missing_tree_link", f"Missing passive tree {node.get('tree_id')}."))
        if node.get("owner_class_id") and node.get("owner_class_id") not in class_ids:
            errors.append(_error(canonical_id, "passive_node_missing_class_link", f"Missing owner class {node.get('owner_class_id')}."))
        if node.get("owner_mastery_id") and node.get("owner_mastery_id") not in mastery_ids:
            errors.append(_error(canonical_id, "passive_node_missing_mastery_link", f"Missing owner mastery {node.get('owner_mastery_id')}."))
        position = node.get("position")
        if position and (not isinstance(position, dict) or not all(isinstance(position.get(axis), (int, float)) for axis in ("x", "y"))):
            errors.append(_error(canonical_id, "invalid_position_shape", "Passive node position must include numeric x and y."))
        if not isinstance(node.get("max_points"), int) or node.get("max_points") < 0:
            errors.append(_error(canonical_id, "invalid_max_points", "Passive node max_points must be a non-negative integer."))
        if not isinstance(node.get("required_points"), int) or node.get("required_points") < 0:
            errors.append(_error(canonical_id, "invalid_required_points", "Passive node required_points must be a non-negative integer."))
        if node.get("special_behavior_classification") not in SPECIAL_BEHAVIOR_CLASSIFICATIONS:
            errors.append(_error(canonical_id, "invalid_special_behavior_classification", "Passive node has invalid special behavior classification."))
        if node.get("stable_calculable") is True or node.get("support_status") == SupportStatus.TRUSTED.value:
            errors.append(_error(canonical_id, "unsupported_stable_calculation", "Passive nodes are not stable-calculable in Phase 8."))
        for modifier in node.get("modifier_rows") or []:
            if not isinstance(modifier, dict) or not modifier.get("provenance"):
                errors.append(_error(canonical_id, "modifier_missing_provenance", "Modifier row is missing provenance."))
            if not isinstance(modifier, dict) or not modifier.get("support_status"):
                errors.append(_error(canonical_id, "modifier_missing_support_status", "Modifier row is missing support_status."))
        for edge in node.get("connections") or []:
            if not isinstance(edge, str):
                errors.append(_error(canonical_id, "invalid_connection_shape", "Passive node connections must be canonical node IDs."))

    for unresolved in (cross_reference or {}).get("unresolved_passive_tree_ids", []):
        warnings.append(_warning("cross_reference", "unresolved_class_mastery_passive_tree_link", f"Class/mastery passive tree link did not resolve: {unresolved}."))

    return {
        "summary": {
            "passive_tree_count": len(trees),
            "passive_node_count": len(nodes),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "duplicate_passive_tree_id_count": _count_code(errors, "duplicate_passive_tree_id"),
            "duplicate_passive_node_id_count": _count_code(errors, "duplicate_passive_node_id"),
            "passive_node_missing_tree_link_count": _count_code(errors, "passive_node_missing_tree_link"),
            "passive_tree_missing_class_link_count": _count_code(errors, "passive_tree_missing_class_link"),
            "passive_node_missing_class_link_count": _count_code(errors, "passive_node_missing_class_link"),
            "missing_provenance_count": _count_code(errors, "missing_provenance"),
            "missing_support_status_count": _count_code(errors, "missing_support_status"),
            "invalid_trust_level_count": _count_code(errors, "invalid_trust_level"),
            "unsupported_stable_calculation_count": _count_code(errors, "unsupported_stable_calculation"),
            "stable_calculable_count": 0,
            "production_consumed": False,
        },
        "errors": errors,
        "warnings": warnings,
        "cross_reference": cross_reference or {},
        "metadata": _metadata(),
    }


def build_unsupported_report(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    evidence = [
        {
            "canonical_id": node["canonical_id"],
            "display_name": node["display_name"],
            "tree_id": node["tree_id"],
            "owner_class_id": node.get("owner_class_id"),
            "owner_mastery_id": node.get("owner_mastery_id"),
            "special_behavior_classification": node["special_behavior_classification"],
            "effect_hint_classifications": node["effect_hint_classifications"],
            "description_text": node.get("description_text"),
            "notes": node.get("warnings", []),
        }
        for node in nodes
        if node["special_behavior_classification"] != "partial_modifier"
    ]
    return {
        "summary": {
            "passive_node_count": len(nodes),
            "unsupported_or_text_only_count": len(evidence),
            "classification_counts": dict(Counter(node["special_behavior_classification"] for node in nodes)),
            "production_consumed": False,
        },
        "records": evidence,
        "metadata": _metadata(),
    }


def render_markdown(bundle: dict[str, Any], validation: dict[str, Any], unsupported: dict[str, Any], *, command: str) -> str:
    summary = bundle["summary"]
    tree_rows = "\n".join(
        f"| `{tree['canonical_id']}` | {tree['display_name']} | `{tree.get('owner_class_id') or ''}` | {len(tree['node_ids'])} |"
        for tree in bundle["records"]["passive_trees"]
    )
    classification_rows = "\n".join(
        f"| {name} | {count} |"
        for name, count in sorted(summary["special_behavior_classification_counts"].items())
    )
    cross_rows = "\n".join(
        f"| `{entry['passive_tree_id']}` | `{entry.get('resolved_tree_id') or ''}` | {entry['status']} |"
        for entry in bundle["cross_reference"]["class_mastery_passive_tree_links"]
    )
    return f"""# v2 Passive Tree Migration

## Purpose

Phase 8 creates a read-only canonical passive tree bundle from extracted passive tree data. Existing local passive JSON is used only as a layout supplement for position and connection fields already used by the current passive viewer.

This phase does not replace production passive behavior, calculate passive effects, implement skill trees, or remap the planner.

## Generation Command

```powershell
{command}
```

## Summary

- Passive tree count: {summary["passive_tree_count"]}
- Passive node count: {summary["passive_node_count"]}
- Layout supplement matched nodes: {summary["layout_matched_node_count"]}
- Unsupported/text-only node count: {unsupported["summary"]["unsupported_or_text_only_count"]}
- Stable-calculable count: 0
- Validation errors: {validation["summary"]["error_count"]}
- Validation warnings: {validation["summary"]["warning_count"]}
- Production consumed: false

## Passive Trees

| Tree ID | Display name | Owner class | Nodes |
| --- | --- | --- | ---: |
{tree_rows}

## Special Behavior Classification

| Classification | Count |
| --- | ---: |
{classification_rows}

## Class/Mastery Cross-Reference

| Class/mastery passive tree link | Resolved v2 passive tree | Status |
| --- | --- | --- |
{cross_rows}

## Unsupported and Text-Only Findings

Unsupported/text-only records are written to `docs/generated/v2_passive_unsupported_report.json`. These records preserve serialized evidence and text, but they are not treated as planner-calculable.

## Migration Implications

- Passive trees and nodes are available for experimental lookup and debug inspection.
- Modifier-like rows remain `partial`; value normalization and stat routing are unresolved.
- Tooltip and description text is display/debug evidence only.
- Existing passive API, planner behavior, stat aggregation, and simulation behavior remain unchanged.

## Deferred

- Skill tree infrastructure.
- Modifier normalization and value-scale policy.
- Planner remapping to v2 passive nodes.
- Stable calculation of passive effects.

## Recommended Next Step

Proceed to Phase 9 skill infrastructure after Checkpoint 8 review.
"""


def write_outputs(
    bundle: dict[str, Any],
    validation: dict[str, Any],
    unsupported: dict[str, Any],
    markdown: str,
    output: Path,
    validation_output: Path,
    unsupported_output: Path,
    markdown_output: Path,
) -> None:
    for path in (output, validation_output, unsupported_output, markdown_output):
        path.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    unsupported_output.write_text(json.dumps(unsupported, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(markdown, encoding="utf-8")


def _tree_record(source_path: Path, source: dict[str, Any], raw_tree: dict[str, Any], tree_id: str, owner_class_id: str | None, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "canonical_id": tree_id,
        "display_name": f"{raw_tree.get('class')} Passive Tree",
        "source_id": str(raw_tree.get("treeId")),
        "source_file": str(source_path),
        "patch_version": None,
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, str(raw_tree.get("treeId")), "Extracted passive tree record."),
        "owner_class_id": owner_class_id,
        "owner_mastery_id": None,
        "source_tree_id": raw_tree.get("treeId"),
        "node_ids": [node["canonical_id"] for node in nodes],
        "edges": _tree_edges(nodes),
        "stable_calculable": False,
        "warnings": [],
        "raw_reference": {"source_tree_id": raw_tree.get("treeId"), "class": raw_tree.get("class")},
        "normalized_fields": {"canonical_kind": "passive_tree"},
        "consumer_safe_fields": {"planner_consumed": False, "debug_only": True},
    }


def _node_record(
    source_path: Path,
    layout_path: Path,
    raw_tree: dict[str, Any],
    raw_node: dict[str, Any],
    tree_id: str,
    owner_class_id: str | None,
    mastery_lookup: dict[str, str],
    layout: dict[tuple[str, int], dict[str, Any]],
) -> dict[str, Any]:
    class_name = str(raw_tree.get("class") or "")
    raw_node_id = int(raw_node.get("id"))
    node_id = _node_id(tree_id, raw_node_id)
    mastery_name = raw_node.get("masteryName")
    owner_mastery_id = None if _normalize(mastery_name) == _normalize(class_name) else mastery_lookup.get((_normalize(class_name), _normalize(mastery_name)))
    layout_node = layout.get((class_name, raw_node_id), {})
    effect_hints = raw_node.get("effectHints") or []
    special = _special_behavior(effect_hints, raw_node)
    warnings = []
    if not layout_node:
        warnings.append("layout_supplement_missing")
    if special != "partial_modifier":
        warnings.append(f"not_stable_calculable:{special}")
    return {
        "canonical_id": node_id,
        "display_name": str(raw_node.get("name") or f"Passive Node {raw_node_id}"),
        "source_id": f"{raw_tree.get('treeId')}:{raw_node_id}",
        "source_file": str(source_path),
        "patch_version": None,
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, f"{raw_tree.get('treeId')}:{raw_node_id}", "Extracted passive node record with optional layout supplement."),
        "tree_id": tree_id,
        "owner_class_id": owner_class_id,
        "owner_mastery_id": owner_mastery_id,
        "source_tree_id": raw_tree.get("treeId"),
        "source_node_id": raw_node_id,
        "mastery_index": raw_node.get("mastery"),
        "mastery_name": mastery_name,
        "position": _position(layout_node),
        "connections": [_node_id(tree_id, _raw_connection_id(value)) for value in layout_node.get("connections") or [] if _raw_connection_id(value) is not None],
        "edge_requirements": [_requirement(tree_id, requirement) for requirement in raw_node.get("requirements") or []],
        "max_points": int(raw_node.get("maxPoints") or 0),
        "required_points": int(raw_node.get("masteryRequirement") or 0),
        "node_type": layout_node.get("node_type") or ("base" if not owner_mastery_id else "mastery"),
        "modifier_rows": [_modifier_row(source_path, node_id, hint, index) for index, hint in enumerate(effect_hints) if isinstance(hint, dict)],
        "modifier_references": [],
        "description_text": raw_node.get("nodeDescription") or raw_node.get("description") or "",
        "tooltip_text": raw_node.get("altText") or raw_node.get("loreText") or "",
        "text_effects": [value for value in [raw_node.get("nodeDescription"), raw_node.get("altText"), raw_node.get("loreText")] if value],
        "special_behavior_classification": special,
        "effect_hint_classifications": sorted({str(hint.get("classification")) for hint in effect_hints if isinstance(hint, dict) and hint.get("classification")}),
        "layout_provenance": {"source_path": str(layout_path), "source_id": layout_node.get("id")} if layout_node else None,
        "stable_calculable": False,
        "warnings": warnings,
        "raw_reference": {"source_tree_id": raw_tree.get("treeId"), "source_node_id": raw_node_id},
        "normalized_fields": {"canonical_kind": "passive_node"},
        "consumer_safe_fields": {"planner_consumed": False, "debug_only": True},
    }


def _modifier_row(source_path: Path, node_id: str, hint: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "row_id": f"{node_id}:effect:{index}",
        "stat_name": hint.get("statName"),
        "value": hint.get("value"),
        "property": hint.get("property"),
        "classification": hint.get("classification"),
        "resolved_property_key": hint.get("resolvedPropertyKey"),
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, f"{node_id}:effect:{index}", "Serialized passive effect hint."),
        "stable_calculable": False,
    }


def _special_behavior(effect_hints: list[Any], raw_node: dict[str, Any]) -> str:
    classifications = {hint.get("classification") for hint in effect_hints if isinstance(hint, dict)}
    if "unsafe_to_infer" in classifications:
        return "unsupported_special_behavior"
    scripted = {"trigger_or_relationship_serialized", "skill_mutator_serialized", "conversion_serialized"}
    if classifications & scripted:
        return "scripted_runtime_behavior"
    partial = {"stat_modifier_serialized", "minion_or_actor_modifier_serialized", "ailment_or_status_serialized"}
    if classifications and classifications <= partial:
        return "partial_modifier"
    if raw_node.get("nodeDescription") or raw_node.get("altText") or raw_node.get("loreText"):
        return "text_only_effect"
    return "unknown"


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


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return payload


def _read_layout(path: Path) -> dict[tuple[str, int], dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        return {}
    return {
        (str(record.get("character_class")), int(record.get("raw_node_id"))): record
        for record in payload
        if isinstance(record, dict) and record.get("character_class") and isinstance(record.get("raw_node_id"), int)
    }


def _class_mastery_lookups(bundle: dict[str, Any]) -> tuple[dict[str, str], dict[tuple[str, str], str], list[str]]:
    classes = bundle.get("records", {}).get("classes", [])
    masteries = bundle.get("records", {}).get("masteries", [])
    class_lookup = {_normalize(record.get("display_name")): record.get("canonical_id") for record in classes if isinstance(record, dict)}
    class_by_id = {record.get("canonical_id"): _normalize(record.get("display_name")) for record in classes if isinstance(record, dict)}
    mastery_lookup = {
        (class_by_id.get(record.get("class_id"), ""), _normalize(record.get("display_name"))): record.get("canonical_id")
        for record in masteries
        if isinstance(record, dict)
    }
    passive_tree_links = []
    for record in classes:
        if isinstance(record, dict):
            passive_tree_links.extend(str(value) for value in record.get("passive_tree_ids") or [])
    for record in masteries:
        if isinstance(record, dict):
            passive_tree_links.extend(str(value) for value in record.get("passive_tree_ids") or [])
    return class_lookup, mastery_lookup, sorted(set(passive_tree_links))


def _cross_reference_passive_links(trees: list[dict[str, Any]], passive_tree_links: list[str]) -> dict[str, Any]:
    tree_ids = {tree["canonical_id"] for tree in trees}
    entries = [
        {
            "passive_tree_id": passive_tree_id,
            "resolved_tree_id": passive_tree_id if passive_tree_id in tree_ids else None,
            "status": "resolved" if passive_tree_id in tree_ids else "unresolved",
        }
        for passive_tree_id in passive_tree_links
    ]
    return {
        "class_mastery_passive_tree_link_count": len(entries),
        "resolved_passive_tree_link_count": sum(1 for entry in entries if entry["status"] == "resolved"),
        "unresolved_passive_tree_link_count": sum(1 for entry in entries if entry["status"] == "unresolved"),
        "unresolved_passive_tree_ids": [entry["passive_tree_id"] for entry in entries if entry["status"] == "unresolved"],
        "class_mastery_passive_tree_links": entries,
        "manual_bridge_count": 0,
    }


def _bundle_summary(trees: list[dict[str, Any]], nodes: list[dict[str, Any]], validation: dict[str, Any], unsupported: dict[str, Any], cross_reference: dict[str, Any]) -> dict[str, Any]:
    return {
        "passive_tree_count": len(trees),
        "passive_node_count": len(nodes),
        "layout_matched_node_count": sum(1 for node in nodes if node.get("layout_provenance")),
        "support_status_counts": dict(Counter([*[tree["support_status"] for tree in trees], *[node["support_status"] for node in nodes]])),
        "trust_level_counts": dict(Counter([*[tree["trust_level"] for tree in trees], *[node["trust_level"] for node in nodes]])),
        "special_behavior_classification_counts": dict(Counter(node["special_behavior_classification"] for node in nodes)),
        "unsupported_or_text_only_count": unsupported["summary"]["unsupported_or_text_only_count"],
        "stable_calculable_count": 0,
        "validation_error_count": validation["summary"]["error_count"],
        "validation_warning_count": validation["summary"]["warning_count"],
        "class_mastery_resolved_passive_tree_link_count": cross_reference["resolved_passive_tree_link_count"],
        "class_mastery_unresolved_passive_tree_link_count": cross_reference["unresolved_passive_tree_link_count"],
        "manual_bridge_count": 0,
        "production_consumed": False,
    }


def _tree_id(raw_tree: dict[str, Any]) -> str:
    return f"passive_tree:{_slug(raw_tree.get('treeId'))}"


def _node_id(tree_id: str, raw_node_id: int) -> str:
    return f"passive_node:{tree_id.split(':', 1)[1]}:{raw_node_id}"


def _tree_edges(nodes: list[dict[str, Any]]) -> list[list[str]]:
    edges: set[tuple[str, str]] = set()
    node_ids = {node["canonical_id"] for node in nodes}
    for node in nodes:
        for other in node.get("connections") or []:
            if other in node_ids:
                edges.add(tuple(sorted((node["canonical_id"], other))))
        for requirement in node.get("edge_requirements") or []:
            source = requirement.get("node_id")
            if source in node_ids:
                edges.add(tuple(sorted((node["canonical_id"], source))))
    return [list(edge) for edge in sorted(edges)]


def _position(layout_node: dict[str, Any]) -> dict[str, float]:
    if isinstance(layout_node.get("x"), (int, float)) and isinstance(layout_node.get("y"), (int, float)):
        return {"x": float(layout_node["x"]), "y": float(layout_node["y"])}
    return {}


def _requirement(tree_id: str, requirement: dict[str, Any]) -> dict[str, Any]:
    return {"node_id": _node_id(tree_id, int(requirement.get("nodeId"))), "points": int(requirement.get("requirement") or 0)}


def _raw_connection_id(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"(\d+)$", value)
        return int(match.group(1)) if match else None
    return None


def _provenance(source_path: Path, source_id: str, note: str) -> dict[str, Any]:
    return {
        "source_path": str(source_path),
        "source_id": source_id,
        "source_type": "generated_from_game_data",
        "extraction_method": "last_epoch_data_export",
        "notes": [note],
    }


def _metadata() -> dict[str, Any]:
    return {"source": "v2_passive_tree_bundle", "read_only": True, "experimental": True, "production_safe": False, "production_consumed": False}


def _slug(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def _normalize(value: Any) -> str:
    return _slug(value).replace("_", "")


def _error(record_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"record_id": record_id, "severity": "error", "code": code, "message": message}


def _warning(record_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"record_id": record_id, "severity": "warning", "code": code, "message": message}


def _count_code(entries: list[dict[str, Any]], code: str) -> int:
    return sum(1 for entry in entries if entry.get("code") == code)


def main() -> int:
    args = parse_args()
    bundle, validation, unsupported = build_v2_passive_tree_bundle(args.source_passives, args.layout_passives, args.class_mastery_bundle)
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_passive_tree_bundle.py "
        f"--source-passives {args.source_passives} "
        f"--layout-passives {args.layout_passives} "
        f"--class-mastery-bundle {args.class_mastery_bundle} "
        f"--output {args.output} "
        f"--validation-output {args.validation_output} "
        f"--unsupported-output {args.unsupported_output} "
        f"--markdown-output {args.markdown_output}"
    )
    write_outputs(bundle, validation, unsupported, render_markdown(bundle, validation, unsupported, command=command), args.output, args.validation_output, args.unsupported_output, args.markdown_output)
    print(json.dumps(bundle["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
