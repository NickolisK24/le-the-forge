"""Generate the v2 canonical skill and skill tree bundles."""

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


DEFAULT_SOURCE_SKILLS = Path(r"D:\Forge\last-epoch-data\exports_json\skills_with_trees.json")
DEFAULT_LAYOUT_SKILLS = ROOT / "frontend" / "src" / "data" / "raw" / "skill-tree-layout.json"
DEFAULT_CLASS_MASTERY_BUNDLE = ROOT / "docs" / "generated" / "v2_class_mastery_bundle.json"
DEFAULT_SKILL_OUTPUT = ROOT / "docs" / "generated" / "v2_skill_bundle.json"
DEFAULT_SKILL_TREE_OUTPUT = ROOT / "docs" / "generated" / "v2_skill_tree_bundle.json"
DEFAULT_VALIDATION_OUTPUT = ROOT / "docs" / "generated" / "v2_skill_validation_report.json"
DEFAULT_UNSUPPORTED_OUTPUT = ROOT / "docs" / "generated" / "v2_skill_unsupported_report.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_SKILL_TREE_MIGRATION.md"

SPECIAL_BEHAVIOR_CLASSIFICATIONS = {
    "trusted_modifier",
    "partial_modifier",
    "text_only_effect",
    "scripted_runtime_behavior",
    "unsupported_special_behavior",
    "unknown",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the v2 skill and skill tree bundles.")
    parser.add_argument("--source-skills", type=Path, default=DEFAULT_SOURCE_SKILLS)
    parser.add_argument("--layout-skills", type=Path, default=DEFAULT_LAYOUT_SKILLS)
    parser.add_argument("--class-mastery-bundle", type=Path, default=DEFAULT_CLASS_MASTERY_BUNDLE)
    parser.add_argument("--skill-output", type=Path, default=DEFAULT_SKILL_OUTPUT)
    parser.add_argument("--skill-tree-output", type=Path, default=DEFAULT_SKILL_TREE_OUTPUT)
    parser.add_argument("--validation-output", type=Path, default=DEFAULT_VALIDATION_OUTPUT)
    parser.add_argument("--unsupported-output", type=Path, default=DEFAULT_UNSUPPORTED_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def build_v2_skill_tree_bundles(
    source_skills: Path,
    layout_skills: Path,
    class_mastery_bundle: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    source = _read_json(source_skills, "skill source")
    class_mastery = _read_json(class_mastery_bundle, "class/mastery bundle")
    layout = _read_layout(layout_skills)
    class_skill_links = _class_mastery_skill_links(class_mastery)
    skills: list[dict[str, Any]] = []
    trees: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []

    for raw_skill in source.get("skills") or []:
        if not isinstance(raw_skill, dict):
            continue
        skill_id = _skill_id(raw_skill)
        tree_id = _tree_id(raw_skill) if isinstance(raw_skill.get("skillTree"), dict) else None
        skill = _skill_record(source_skills, raw_skill, skill_id, tree_id)
        skills.append(skill)
        if not tree_id:
            continue
        raw_tree = raw_skill["skillTree"]
        tree_nodes: list[dict[str, Any]] = []
        for raw_node in raw_tree.get("nodes") or []:
            if not isinstance(raw_node, dict):
                continue
            node = _node_record(source_skills, layout_skills, raw_skill, raw_tree, raw_node, skill_id, tree_id, layout)
            tree_nodes.append(node)
            nodes.append(node)
        trees.append(_tree_record(source_skills, raw_skill, raw_tree, skill_id, tree_id, tree_nodes))

    cross_reference = _cross_reference_skill_links(skills, class_skill_links)
    validation = validate_v2_skill_tree_records(skills, trees, nodes, class_mastery, cross_reference)
    unsupported = build_unsupported_report(skills, nodes)
    skill_bundle = {
        "schema_version": "v2.skill_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_skills_path": str(source_skills),
        "source_metadata": source.get("meta", {}),
        "summary": _skill_summary(skills, trees, nodes, validation, unsupported, cross_reference),
        "records": {"skills": skills},
        "cross_reference": cross_reference,
        "metadata": _metadata("v2_skill_bundle"),
    }
    tree_bundle = {
        "schema_version": "v2.skill_tree_bundle.1",
        "generated_on": date.today().isoformat(),
        "source_skills_path": str(source_skills),
        "layout_skills_path": str(layout_skills),
        "source_metadata": source.get("meta", {}),
        "summary": _tree_summary(skills, trees, nodes, validation, unsupported),
        "records": {"skill_trees": trees, "skill_nodes": nodes},
        "metadata": _metadata("v2_skill_tree_bundle"),
    }
    return skill_bundle, tree_bundle, validation, unsupported


def validate_v2_skill_tree_records(
    skills: list[dict[str, Any]],
    trees: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    class_mastery_bundle: dict[str, Any] | None = None,
    cross_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    skill_ids = _validate_common_records(skills, "skill", errors)
    tree_ids = _validate_common_records(trees, "skill_tree", errors)
    node_ids = _validate_common_records(nodes, "skill_node", errors)
    class_ids = {record.get("canonical_id") for record in (class_mastery_bundle or {}).get("records", {}).get("classes", [])}
    mastery_ids = {record.get("canonical_id") for record in (class_mastery_bundle or {}).get("records", {}).get("masteries", [])}

    for skill in skills:
        canonical_id = skill.get("canonical_id")
        for class_id in skill.get("owner_class_ids") or []:
            if class_id not in class_ids:
                errors.append(_error(canonical_id, "skill_missing_class_link", f"Missing owner class {class_id}."))
        for mastery_id in skill.get("owner_mastery_ids") or []:
            if mastery_id not in mastery_ids:
                errors.append(_error(canonical_id, "skill_missing_mastery_link", f"Missing owner mastery {mastery_id}."))
        if skill.get("skill_tree_id") and skill.get("skill_tree_id") not in tree_ids:
            errors.append(_error(canonical_id, "skill_missing_tree_link", f"Missing skill tree {skill.get('skill_tree_id')}."))
        if skill.get("stable_calculable") is True or skill.get("support_status") == SupportStatus.TRUSTED.value:
            errors.append(_error(canonical_id, "unsupported_stable_calculation", "Skills are not stable-calculable in Phase 9."))

    for tree in trees:
        canonical_id = tree.get("canonical_id")
        if tree.get("skill_id") not in skill_ids:
            errors.append(_error(canonical_id, "skill_tree_missing_skill_link", f"Missing skill {tree.get('skill_id')}."))
        for class_id in tree.get("owner_class_ids") or []:
            if class_id not in class_ids:
                errors.append(_error(canonical_id, "skill_tree_missing_class_link", f"Missing owner class {class_id}."))
        for mastery_id in tree.get("owner_mastery_ids") or []:
            if mastery_id not in mastery_ids:
                errors.append(_error(canonical_id, "skill_tree_missing_mastery_link", f"Missing owner mastery {mastery_id}."))
        if not isinstance(tree.get("node_ids"), list):
            errors.append(_error(canonical_id, "invalid_node_links", "Skill tree node_ids must be a list."))
        else:
            for node_id in tree.get("node_ids") or []:
                if node_id not in node_ids:
                    errors.append(_error(canonical_id, "skill_tree_links_missing_node", f"Skill tree links missing node {node_id}."))
        for edge in tree.get("edges") or []:
            if not isinstance(edge, list) or len(edge) != 2 or not all(isinstance(value, str) for value in edge):
                errors.append(_error(canonical_id, "invalid_edge_shape", "Skill tree edges must be [from_id, to_id] string pairs."))

    for node in nodes:
        canonical_id = node.get("canonical_id")
        if node.get("skill_tree_id") not in tree_ids:
            errors.append(_error(canonical_id, "skill_node_missing_tree_link", f"Missing skill tree {node.get('skill_tree_id')}."))
        if node.get("skill_id") not in skill_ids:
            errors.append(_error(canonical_id, "skill_node_missing_skill_link", f"Missing skill {node.get('skill_id')}."))
        position = node.get("position")
        if position and (not isinstance(position, dict) or not all(isinstance(position.get(axis), (int, float)) for axis in ("x", "y"))):
            errors.append(_error(canonical_id, "invalid_position_shape", "Skill node position must include numeric x and y."))
        if not isinstance(node.get("max_points"), int) or node.get("max_points") < 0:
            errors.append(_error(canonical_id, "invalid_max_points", "Skill node max_points must be a non-negative integer."))
        if not isinstance(node.get("required_points"), int) or node.get("required_points") < 0:
            errors.append(_error(canonical_id, "invalid_required_points", "Skill node required_points must be a non-negative integer."))
        if node.get("special_behavior_classification") not in SPECIAL_BEHAVIOR_CLASSIFICATIONS:
            errors.append(_error(canonical_id, "invalid_special_behavior_classification", "Skill node has invalid special behavior classification."))
        if node.get("stable_calculable") is True or node.get("support_status") == SupportStatus.TRUSTED.value:
            errors.append(_error(canonical_id, "unsupported_stable_calculation", "Skill nodes are not stable-calculable in Phase 9."))
        for modifier in node.get("modifier_rows") or []:
            if not isinstance(modifier, dict) or not modifier.get("provenance"):
                errors.append(_error(canonical_id, "modifier_missing_provenance", "Modifier row is missing provenance."))
            if not isinstance(modifier, dict) or not modifier.get("support_status"):
                errors.append(_error(canonical_id, "modifier_missing_support_status", "Modifier row is missing support_status."))
        for connection in node.get("connections") or []:
            if not isinstance(connection, str):
                errors.append(_error(canonical_id, "invalid_connection_shape", "Skill node connections must be canonical node IDs."))

    for unresolved in (cross_reference or {}).get("unresolved_skill_source_ids", []):
        warnings.append(_warning("cross_reference", "unresolved_class_mastery_skill_link", f"Class/mastery skill link did not resolve: {unresolved}."))
    for skill in skills:
        if "source_skill_id_missing" in (skill.get("warnings") or []):
            warnings.append(_warning(skill.get("canonical_id"), "source_skill_id_missing", "Skill source record did not include an id; canonical ID was derived from the display name."))

    return {
        "summary": {
            "skill_count": len(skills),
            "skill_tree_count": len(trees),
            "skill_node_count": len(nodes),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "duplicate_skill_id_count": _count_code(errors, "duplicate_skill_id"),
            "duplicate_skill_tree_id_count": _count_code(errors, "duplicate_skill_tree_id"),
            "duplicate_skill_node_id_count": _count_code(errors, "duplicate_skill_node_id"),
            "skill_tree_missing_skill_link_count": _count_code(errors, "skill_tree_missing_skill_link"),
            "skill_node_missing_tree_link_count": _count_code(errors, "skill_node_missing_tree_link"),
            "skill_node_missing_skill_link_count": _count_code(errors, "skill_node_missing_skill_link"),
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
        "metadata": _metadata("v2_skill_validation_report"),
    }


def build_unsupported_report(skills: list[dict[str, Any]], nodes: list[dict[str, Any]]) -> dict[str, Any]:
    skill_records = [
        {
            "canonical_id": skill["canonical_id"],
            "display_name": skill["display_name"],
            "skill_tree_id": skill.get("skill_tree_id"),
            "special_behavior_classification": skill["special_behavior_classification"],
            "description_text": skill.get("description_text"),
            "notes": skill.get("warnings", []),
        }
        for skill in skills
        if skill["special_behavior_classification"] != "partial_modifier"
    ]
    node_records = [
        {
            "canonical_id": node["canonical_id"],
            "display_name": node["display_name"],
            "skill_tree_id": node["skill_tree_id"],
            "skill_id": node["skill_id"],
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
            "skill_count": len(skills),
            "skill_node_count": len(nodes),
            "unsupported_or_text_only_skill_count": len(skill_records),
            "unsupported_or_text_only_node_count": len(node_records),
            "unsupported_or_text_only_count": len(skill_records) + len(node_records),
            "skill_classification_counts": dict(Counter(skill["special_behavior_classification"] for skill in skills)),
            "node_classification_counts": dict(Counter(node["special_behavior_classification"] for node in nodes)),
            "production_consumed": False,
        },
        "records": {"skills": skill_records, "skill_nodes": node_records},
        "metadata": _metadata("v2_skill_unsupported_report"),
    }


def render_markdown(skill_bundle: dict[str, Any], tree_bundle: dict[str, Any], validation: dict[str, Any], unsupported: dict[str, Any], *, command: str) -> str:
    skill_summary = skill_bundle["summary"]
    tree_summary = tree_bundle["summary"]
    top_tree_rows = "\n".join(
        f"| `{tree['canonical_id']}` | {tree['display_name']} | `{tree['skill_id']}` | {len(tree['node_ids'])} |"
        for tree in tree_bundle["records"]["skill_trees"][:15]
    )
    node_classification_rows = "\n".join(
        f"| {name} | {count} |"
        for name, count in sorted(tree_summary["node_special_behavior_classification_counts"].items())
    )
    skill_classification_rows = "\n".join(
        f"| {name} | {count} |"
        for name, count in sorted(skill_summary["skill_special_behavior_classification_counts"].items())
    )
    return f"""# v2 Skill Tree Migration

## Purpose

Phase 9 creates read-only canonical skill and skill tree bundles from extracted skill data. Skill tree layout is supplemented from existing frontend raw layout data when available.

This phase does not replace production skill behavior, calculate skill effects, normalize modifiers, or remap the planner.

## Generation Command

```powershell
{command}
```

## Summary

- Skill count: {skill_summary["skill_count"]}
- Skill tree count: {tree_summary["skill_tree_count"]}
- Skill node count: {tree_summary["skill_node_count"]}
- Layout supplement matched nodes: {tree_summary["layout_matched_node_count"]}
- Unsupported/text-only skill records: {unsupported["summary"]["unsupported_or_text_only_skill_count"]}
- Unsupported/text-only node records: {unsupported["summary"]["unsupported_or_text_only_node_count"]}
- Stable-calculable count: 0
- Validation errors: {validation["summary"]["error_count"]}
- Validation warnings: {validation["summary"]["warning_count"]}
- Production consumed: false

## Skill Behavior Classification

| Classification | Count |
| --- | ---: |
{skill_classification_rows}

## Skill Node Behavior Classification

| Classification | Count |
| --- | ---: |
{node_classification_rows}

## Sample Skill Trees

| Tree ID | Display name | Skill ID | Nodes |
| --- | --- | --- | ---: |
{top_tree_rows}

## Class/Mastery Cross-Reference

- Class/mastery linked skill source IDs: {skill_bundle["cross_reference"]["class_mastery_skill_link_count"]}
- Resolved links: {skill_bundle["cross_reference"]["resolved_skill_link_count"]}
- Unresolved links: {skill_bundle["cross_reference"]["unresolved_skill_link_count"]}
- Manual bridge count: {skill_bundle["cross_reference"]["manual_bridge_count"]}

The current skill export does not expose the same source path IDs used by class/mastery records, so these links are reported instead of inferred.

## Unsupported and Text-Only Findings

Unsupported/text-only records are written to `docs/generated/v2_skill_unsupported_report.json`. These records preserve serialized evidence and text, but they are not treated as planner-calculable.

## Migration Implications

- Skills, skill trees, and skill nodes are available for experimental lookup and debug inspection.
- Modifier-like rows remain `partial`; value normalization and stat routing are unresolved.
- Tooltip and description text is display/debug evidence only.
- Existing skill API, planner behavior, stat aggregation, and simulation behavior remain unchanged.

## Deferred

- Modifier normalization and value-scale policy.
- Planner remapping to v2 skills and skill tree nodes.
- Stable calculation of skill effects.
- Class/mastery skill ownership bridging unless a future source exposes stable IDs.

## Recommended Next Step

Proceed to modifier/stat normalization planning after Checkpoint 9 review.
"""


def write_outputs(
    skill_bundle: dict[str, Any],
    tree_bundle: dict[str, Any],
    validation: dict[str, Any],
    unsupported: dict[str, Any],
    markdown: str,
    skill_output: Path,
    skill_tree_output: Path,
    validation_output: Path,
    unsupported_output: Path,
    markdown_output: Path,
) -> None:
    for path in (skill_output, skill_tree_output, validation_output, unsupported_output, markdown_output):
        path.parent.mkdir(parents=True, exist_ok=True)
    skill_output.write_text(json.dumps(skill_bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    skill_tree_output.write_text(json.dumps(tree_bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    unsupported_output.write_text(json.dumps(unsupported, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(markdown, encoding="utf-8")


def _skill_record(source_path: Path, raw_skill: dict[str, Any], skill_id: str, tree_id: str | None) -> dict[str, Any]:
    warnings = []
    if not raw_skill.get("id"):
        warnings.append("source_skill_id_missing")
    special = _skill_special_behavior(raw_skill)
    if special != "partial_modifier":
        warnings.append(f"not_stable_calculable:{special}")
    return {
        "canonical_id": skill_id,
        "display_name": str(raw_skill.get("name") or raw_skill.get("id") or "Unknown Skill"),
        "source_id": str(raw_skill.get("id") or _slug(raw_skill.get("name"))),
        "source_file": str(source_path),
        "patch_version": None,
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, str(raw_skill.get("id") or _slug(raw_skill.get("name"))), "Extracted skill record."),
        "owner_class_ids": [],
        "owner_mastery_ids": [],
        "source_skill_id": raw_skill.get("id") or None,
        "skill_tree_id": tree_id,
        "skill_tags": _strings(raw_skill.get("tagsDecoded")),
        "damage_types": sorted(set(_strings(raw_skill.get("tagsDecoded")) + _strings(raw_skill.get("conversionDamageTagsDecoded")))),
        "scaling_tags": _attribute_scaling(raw_skill.get("attributeScaling")),
        "cost": {
            "mana_cost": raw_skill.get("manaCost"),
            "minimum_mana_cost": raw_skill.get("minimumManaCost"),
            "channel_cost": raw_skill.get("channelCost"),
            "free_when_out_of_mana": raw_skill.get("freeWhenOutOfMana"),
        },
        "cast_data": {
            "use_delay": raw_skill.get("useDelay"),
            "use_duration": raw_skill.get("useDuration"),
            "minimum_use_duration": raw_skill.get("minimumUseDuration"),
            "channel_time_limit": raw_skill.get("channelTimeLimit"),
            "channelled": raw_skill.get("channelled"),
            "instant_cast": raw_skill.get("instantCast"),
            "speed_scaler": raw_skill.get("speedScaler"),
            "speed_multiplier": raw_skill.get("speedMultiplier"),
        },
        "cooldown": {
            "max_charges": raw_skill.get("maxCharges"),
            "charges_per_second": raw_skill.get("chargesPerSecond"),
            "shared_cooldown": raw_skill.get("sharedCooldown"),
            "cannot_reset_cooldown": raw_skill.get("cannotResetCooldown"),
        },
        "requirements": {
            "requires_weapon_type": raw_skill.get("requireWeaponType"),
            "permitted_weapon_types": raw_skill.get("permittedWeaponTypes") or [],
            "requires_shield": raw_skill.get("requiresShield"),
            "requires_dual_wield": raw_skill.get("requiresDualWield"),
        },
        "behavior_flags": {
            "is_zone_ability": raw_skill.get("isZoneAbility"),
            "traversal_skill": raw_skill.get("traversalSkill"),
            "evade_skill": raw_skill.get("evadeSkill"),
            "counts_as_movement": raw_skill.get("countsAsMovement"),
            "is_transform": raw_skill.get("isTransform"),
            "combo_ability": raw_skill.get("comboAbility"),
            "minions_use_ability": raw_skill.get("minionsUseAbility"),
            "targets_allies": raw_skill.get("targetsAllies"),
            "targets_self_only": raw_skill.get("targetsSelfOnly"),
            "only_target_minions": raw_skill.get("onlyTargetMinions"),
        },
        "description_text": raw_skill.get("description") or "",
        "tooltip_text": raw_skill.get("altText") or "",
        "text_effects": [value for value in [raw_skill.get("description"), raw_skill.get("altText"), raw_skill.get("lore")] if value],
        "special_behavior_classification": special,
        "damage_source_status": raw_skill.get("damageSourceStatus"),
        "damage_source_notes": raw_skill.get("damageSourceNotes") or [],
        "stable_calculable": False,
        "warnings": warnings,
        "raw_reference": {"source_skill_id": raw_skill.get("id"), "m_name": raw_skill.get("_mName")},
        "normalized_fields": {"canonical_kind": "skill"},
        "consumer_safe_fields": {"planner_consumed": False, "debug_only": True},
    }


def _tree_record(source_path: Path, raw_skill: dict[str, Any], raw_tree: dict[str, Any], skill_id: str, tree_id: str, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "canonical_id": tree_id,
        "display_name": f"{raw_tree.get('ability') or raw_skill.get('name')} Skill Tree",
        "source_id": str(raw_tree.get("sourceId") or raw_skill.get("id")),
        "source_file": str(source_path),
        "patch_version": None,
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, str(raw_tree.get("sourceId") or raw_skill.get("id")), "Extracted skill tree record."),
        "skill_id": skill_id,
        "owner_class_ids": [],
        "owner_mastery_ids": [],
        "source_tree_id": raw_tree.get("sourceId") or raw_skill.get("id"),
        "source_tree_class_name": raw_tree.get("className"),
        "node_ids": [node["canonical_id"] for node in nodes],
        "edges": _tree_edges(nodes),
        "stable_calculable": False,
        "warnings": [],
        "raw_reference": {"source_skill_id": raw_skill.get("id"), "source_tree_id": raw_tree.get("sourceId")},
        "normalized_fields": {"canonical_kind": "skill_tree"},
        "consumer_safe_fields": {"planner_consumed": False, "debug_only": True},
    }


def _node_record(
    source_path: Path,
    layout_path: Path,
    raw_skill: dict[str, Any],
    raw_tree: dict[str, Any],
    raw_node: dict[str, Any],
    skill_id: str,
    tree_id: str,
    layout: dict[tuple[str, int], dict[str, Any]],
) -> dict[str, Any]:
    raw_node_id = int(raw_node.get("id"))
    node_id = _node_id(tree_id, raw_node_id)
    layout_node = layout.get((str(raw_skill.get("id") or ""), raw_node_id), {})
    effect_hints = raw_node.get("effectHints") or []
    if not effect_hints:
        effect_hints = [_stat_hint(stat, index) for index, stat in enumerate(raw_node.get("stats") or []) if isinstance(stat, dict)]
    special = _special_behavior(effect_hints, raw_node)
    warnings = []
    if not layout_node:
        warnings.append("layout_supplement_missing")
    if special != "partial_modifier":
        warnings.append(f"not_stable_calculable:{special}")
    return {
        "canonical_id": node_id,
        "display_name": str(raw_node.get("name") or f"Skill Node {raw_node_id}"),
        "source_id": f"{raw_tree.get('sourceId') or raw_skill.get('id')}:{raw_node_id}",
        "source_file": str(source_path),
        "patch_version": None,
        "support_status": SupportStatus.PARTIAL.value,
        "trust_level": TrustLevel.GENERATED_FROM_GAME_DATA.value,
        "provenance": _provenance(source_path, f"{raw_tree.get('sourceId') or raw_skill.get('id')}:{raw_node_id}", "Extracted skill tree node record with optional layout supplement."),
        "skill_tree_id": tree_id,
        "skill_id": skill_id,
        "owner_class_ids": [],
        "owner_mastery_ids": [],
        "source_tree_id": raw_tree.get("sourceId") or raw_skill.get("id"),
        "source_node_id": raw_node_id,
        "position": _position(layout_node),
        "connections": [],
        "edge_requirements": [_requirement(tree_id, requirement) for requirement in raw_node.get("requirements") or [] if isinstance(requirement, dict)],
        "max_points": int(raw_node.get("maxPoints") or 0),
        "required_points": int(raw_node.get("masteryRequirement") or 0),
        "node_type": layout_node.get("node_type") or _node_type(layout_node, raw_node),
        "modifier_rows": [_modifier_row(source_path, node_id, hint, index) for index, hint in enumerate(effect_hints) if isinstance(hint, dict)],
        "modifier_references": [],
        "description_text": raw_node.get("description") or raw_node.get("nodeDescription") or "",
        "tooltip_text": raw_node.get("altText") or "",
        "text_effects": [value for value in [raw_node.get("description"), raw_node.get("nodeDescription"), raw_node.get("altText"), raw_node.get("loreText")] if value],
        "special_behavior_classification": special,
        "effect_hint_classifications": sorted({str(hint.get("classification")) for hint in effect_hints if isinstance(hint, dict) and hint.get("classification")}),
        "layout_provenance": {"source_path": str(layout_path), "source_id": layout_node.get("id")} if layout_node else None,
        "icon": layout_node.get("icon"),
        "stable_calculable": False,
        "warnings": warnings,
        "raw_reference": {"source_skill_id": raw_skill.get("id"), "source_node_id": raw_node_id},
        "normalized_fields": {"canonical_kind": "skill_node"},
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
        "provenance": _provenance(source_path, f"{node_id}:effect:{index}", "Serialized skill tree effect hint."),
        "stable_calculable": False,
    }


def _skill_special_behavior(raw_skill: dict[str, Any]) -> str:
    if raw_skill.get("mutatorHints") or raw_skill.get("summonedActors") or raw_skill.get("damageSourceStatus") == "runtime_or_mutator_driven":
        return "scripted_runtime_behavior"
    if raw_skill.get("damageSources"):
        return "partial_modifier"
    if raw_skill.get("description") or raw_skill.get("altText") or raw_skill.get("lore"):
        return "text_only_effect"
    return "unknown"


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
    if raw_node.get("description") or raw_node.get("nodeDescription") or raw_node.get("altText") or raw_node.get("loreText"):
        return "text_only_effect"
    return "unknown"


def _stat_hint(stat: dict[str, Any], index: int) -> dict[str, Any]:
    classification = "stat_modifier_serialized"
    name = str(stat.get("statName") or "")
    if stat.get("overrideSprite") or stat.get("property") == 54:
        classification = "unsafe_to_infer"
    elif any(token in name.lower() for token in ("chance", "stacks", "ignite", "bleed", "poison", "shred", "slow", "chill", "shock")):
        classification = "ailment_or_status_serialized"
    return {"classification": classification, "source": "stats", "sourcePath": ["stats", str(index)], **stat}


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
    if not isinstance(payload, dict):
        return {}
    records: dict[tuple[str, int], dict[str, Any]] = {}
    for tree_id, tree in payload.items():
        if not isinstance(tree, dict):
            continue
        for child in tree.get("children") or []:
            if isinstance(child, dict) and isinstance(child.get("nodeId"), int):
                records[(str(tree_id), int(child["nodeId"]))] = {"id": f"{tree_id}:{child['nodeId']}", **child}
    return records


def _class_mastery_skill_links(bundle: dict[str, Any]) -> list[str]:
    links: list[str] = []
    for key in ("classes", "masteries"):
        for record in bundle.get("records", {}).get(key, []) or []:
            if isinstance(record, dict):
                links.extend(str(value) for value in record.get("skill_ids") or [])
    return sorted(set(links))


def _cross_reference_skill_links(skills: list[dict[str, Any]], class_skill_links: list[str]) -> dict[str, Any]:
    skill_by_source_id = {
        f"skill:{skill.get('source_skill_id')}": skill.get("canonical_id")
        for skill in skills
        if skill.get("source_skill_id")
    }
    entries = [
        {
            "class_mastery_skill_source_id": source_id,
            "resolved_skill_id": skill_by_source_id.get(source_id),
            "status": "resolved" if source_id in skill_by_source_id else "unresolved",
        }
        for source_id in class_skill_links
    ]
    return {
        "class_mastery_skill_link_count": len(entries),
        "resolved_skill_link_count": sum(1 for entry in entries if entry["status"] == "resolved"),
        "unresolved_skill_link_count": sum(1 for entry in entries if entry["status"] == "unresolved"),
        "unresolved_skill_source_ids": [entry["class_mastery_skill_source_id"] for entry in entries if entry["status"] == "unresolved"],
        "class_mastery_skill_links": entries,
        "manual_bridge_count": 0,
    }


def _skill_summary(skills: list[dict[str, Any]], trees: list[dict[str, Any]], nodes: list[dict[str, Any]], validation: dict[str, Any], unsupported: dict[str, Any], cross_reference: dict[str, Any]) -> dict[str, Any]:
    return {
        "skill_count": len(skills),
        "skill_with_tree_count": sum(1 for skill in skills if skill.get("skill_tree_id")),
        "skill_tree_count": len(trees),
        "skill_node_count": len(nodes),
        "support_status_counts": dict(Counter(skill["support_status"] for skill in skills)),
        "trust_level_counts": dict(Counter(skill["trust_level"] for skill in skills)),
        "skill_special_behavior_classification_counts": dict(Counter(skill["special_behavior_classification"] for skill in skills)),
        "unsupported_or_text_only_skill_count": unsupported["summary"]["unsupported_or_text_only_skill_count"],
        "stable_calculable_count": 0,
        "validation_error_count": validation["summary"]["error_count"],
        "validation_warning_count": validation["summary"]["warning_count"],
        "class_mastery_resolved_skill_link_count": cross_reference["resolved_skill_link_count"],
        "class_mastery_unresolved_skill_link_count": cross_reference["unresolved_skill_link_count"],
        "manual_bridge_count": 0,
        "production_consumed": False,
    }


def _tree_summary(skills: list[dict[str, Any]], trees: list[dict[str, Any]], nodes: list[dict[str, Any]], validation: dict[str, Any], unsupported: dict[str, Any]) -> dict[str, Any]:
    return {
        "skill_count": len(skills),
        "skill_tree_count": len(trees),
        "skill_node_count": len(nodes),
        "layout_matched_node_count": sum(1 for node in nodes if node.get("layout_provenance")),
        "support_status_counts": dict(Counter([*[tree["support_status"] for tree in trees], *[node["support_status"] for node in nodes]])),
        "trust_level_counts": dict(Counter([*[tree["trust_level"] for tree in trees], *[node["trust_level"] for node in nodes]])),
        "node_special_behavior_classification_counts": dict(Counter(node["special_behavior_classification"] for node in nodes)),
        "unsupported_or_text_only_node_count": unsupported["summary"]["unsupported_or_text_only_node_count"],
        "stable_calculable_count": 0,
        "validation_error_count": validation["summary"]["error_count"],
        "validation_warning_count": validation["summary"]["warning_count"],
        "production_consumed": False,
    }


def _skill_id(raw_skill: dict[str, Any]) -> str:
    return f"skill:{_slug(raw_skill.get('id') or raw_skill.get('name'))}"


def _tree_id(raw_skill: dict[str, Any]) -> str:
    return f"skill_tree:{_slug(raw_skill.get('id') or raw_skill.get('name'))}"


def _node_id(tree_id: str, raw_node_id: int) -> str:
    return f"skill_node:{tree_id.split(':', 1)[1]}:{raw_node_id}"


def _tree_edges(nodes: list[dict[str, Any]]) -> list[list[str]]:
    edges: set[tuple[str, str]] = set()
    node_ids = {node["canonical_id"] for node in nodes}
    for node in nodes:
        for requirement in node.get("edge_requirements") or []:
            source = requirement.get("node_id")
            if source in node_ids:
                edges.add(tuple(sorted((node["canonical_id"], source))))
    return [list(edge) for edge in sorted(edges)]


def _position(layout_node: dict[str, Any]) -> dict[str, float]:
    rect = layout_node.get("rect") if isinstance(layout_node, dict) else None
    if isinstance(rect, list) and len(rect) >= 2 and isinstance(rect[0], (int, float)) and isinstance(rect[1], (int, float)):
        return {"x": float(rect[0]), "y": float(rect[1])}
    if isinstance(layout_node.get("x"), (int, float)) and isinstance(layout_node.get("y"), (int, float)):
        return {"x": float(layout_node["x"]), "y": float(layout_node["y"])}
    return {}


def _requirement(tree_id: str, requirement: dict[str, Any]) -> dict[str, Any]:
    raw_node_id = requirement.get("nodeId", requirement.get("node"))
    return {"node_id": _node_id(tree_id, int(raw_node_id)), "points": int(requirement.get("requirement") or 0)}


def _node_type(layout_node: dict[str, Any], raw_node: dict[str, Any]) -> str:
    if raw_node.get("maxPoints") == 0:
        return "root"
    if layout_node.get("nodeSize") == 2:
        return "notable"
    return "core"


def _attribute_scaling(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({str(record.get("attribute")) for record in value if isinstance(record, dict) and record.get("attribute")})


def _strings(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _provenance(source_path: Path, source_id: str, note: str) -> dict[str, Any]:
    return {
        "source_path": str(source_path),
        "source_id": source_id,
        "source_type": "generated_from_game_data",
        "extraction_method": "last_epoch_data_export",
        "notes": [note],
    }


def _metadata(source: str) -> dict[str, Any]:
    return {"source": source, "read_only": True, "experimental": True, "production_safe": False, "production_consumed": False}


def _slug(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "_", text)
    return text if re.search(r"[a-z0-9]", text) else "unknown"


def _error(record_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"record_id": record_id, "severity": "error", "code": code, "message": message}


def _warning(record_id: Any, code: str, message: str) -> dict[str, Any]:
    return {"record_id": record_id, "severity": "warning", "code": code, "message": message}


def _count_code(entries: list[dict[str, Any]], code: str) -> int:
    return sum(1 for entry in entries if entry.get("code") == code)


def main() -> int:
    args = parse_args()
    skill_bundle, tree_bundle, validation, unsupported = build_v2_skill_tree_bundles(args.source_skills, args.layout_skills, args.class_mastery_bundle)
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_skill_tree_bundle.py "
        f"--source-skills {args.source_skills} "
        f"--layout-skills {args.layout_skills} "
        f"--class-mastery-bundle {args.class_mastery_bundle} "
        f"--skill-output {args.skill_output} "
        f"--skill-tree-output {args.skill_tree_output} "
        f"--validation-output {args.validation_output} "
        f"--unsupported-output {args.unsupported_output} "
        f"--markdown-output {args.markdown_output}"
    )
    write_outputs(skill_bundle, tree_bundle, validation, unsupported, render_markdown(skill_bundle, tree_bundle, validation, unsupported, command=command), args.skill_output, args.skill_tree_output, args.validation_output, args.unsupported_output, args.markdown_output)
    print(json.dumps({"skills": skill_bundle["summary"], "skill_trees": tree_bundle["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
