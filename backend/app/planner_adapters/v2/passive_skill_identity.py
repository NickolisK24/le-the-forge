"""Identity-only passive and skill metadata views backed by v2 bundles."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from app.repositories.v2.passive_repository import V2PassiveRepository
from app.repositories.v2.paths import artifact_path
from app.repositories.v2.skill_repository import V2SkillRepository


PASSIVE_SKILL_IDENTITY_FIELDS = (
    "canonical_id",
    "display_name",
    "domain",
    "owner_class_ids",
    "owner_mastery_ids",
    "tree_id",
    "skill_id",
    "source_id",
    "source_path",
    "source_tree_id",
    "source_skill_id",
    "source_ability_path_id",
    "identity_match_status",
    "ownership_status",
    "provenance_summary",
    "support_status",
    "trust_level",
    "warnings",
    "debug_summary",
    "identity_only_eligible",
    "planner_calculable",
    "stable_calculable",
    "blocked_reasons",
)

EXCLUDED_CALCULATION_FIELDS = (
    "modifier_rows",
    "modifier_references",
    "effect_hint_classifications",
    "text_effects",
    "tooltip_text",
    "description_text",
    "damage_types",
    "skill_tags",
    "scaling_tags",
    "cast_data",
    "cooldown",
    "cost",
    "raw_value_min",
    "raw_value_max",
    "normalized_value_min",
    "normalized_value_max",
)

PASSIVE_SKILL_IDENTITY_BLOCKED_REASONS = (
    "identity_only_metadata",
    "passive_skill_effects_not_planner_calculable",
    "stable_calculable_false",
    "value_normalization_audit_only",
)

SKILL_IDENTITY_BRIDGE_BLOCKED_REASON = "skill_identity_bridge_unresolved"


class V2PassiveSkillIdentityMetadata:
    """Read-only identity/provenance metadata adapter for v2 passives and skills."""

    def __init__(
        self,
        *,
        root: str | Path | None = None,
        passive_repository: V2PassiveRepository | None = None,
        skill_repository: V2SkillRepository | None = None,
        identity_report_path: str | Path | None = None,
    ) -> None:
        self.root = Path(root) if root is not None else None
        self._passive_repository = passive_repository
        self._skill_repository = skill_repository
        self.identity_report_path = Path(identity_report_path) if identity_report_path is not None else self._default_identity_report_path()

    def load_passive_repository(self) -> V2PassiveRepository:
        if self._passive_repository is not None:
            return self._passive_repository
        return V2PassiveRepository(artifact_path("passive_tree_bundle", root=self.root)).load()

    def load_skill_repository(self) -> V2SkillRepository:
        if self._skill_repository is not None:
            return self._skill_repository
        return V2SkillRepository(
            artifact_path("skill_bundle", root=self.root),
            artifact_path("skill_tree_bundle", root=self.root),
        ).load()

    def summarize_identity_metadata(self, *, sample_limit: int = 10) -> dict[str, Any]:
        passive_repository = self.load_passive_repository()
        skill_repository = self.load_skill_repository()
        identity_report = _read_json(self.identity_report_path)
        identity_summary = _skill_identity_summary(identity_report)
        skill_identity_index = _skill_identity_index(identity_report)

        passive_tree_views = [build_passive_tree_identity_view(tree) for tree in passive_repository.list_trees()]
        passive_node_views = [
            build_passive_node_identity_view(node)
            for tree in passive_repository.list_trees()
            for node in passive_repository.get_nodes_by_tree(tree["canonical_id"])
        ]
        skill_views = [
            build_skill_identity_view(skill, identity_status=skill_identity_index.get(skill["canonical_id"], "not_class_mastery_referenced"))
            for skill in skill_repository.list_skills()
        ]
        skill_tree_views = [build_skill_tree_identity_view(tree) for tree in skill_repository.list_trees()]
        skill_node_views = [
            build_skill_node_identity_view(node)
            for tree in skill_repository.list_trees()
            for node in skill_repository.get_nodes_by_tree(tree["canonical_id"])
        ]
        all_views = passive_tree_views + passive_node_views + skill_views + skill_tree_views + skill_node_views

        domains = Counter(view["domain"] for view in all_views)
        blocked_reason_counts: Counter[str] = Counter()
        identity_status_counts: Counter[str] = Counter()
        ownership_status_counts: Counter[str] = Counter()
        for view in all_views:
            blocked_reason_counts.update(view["blocked_reasons"])
            identity_status_counts[str(view["identity_match_status"])] += 1
            ownership_status_counts[str(view["ownership_status"])] += 1

        identity_only_eligible_count = sum(1 for view in all_views if view["identity_only_eligible"])
        planner_calculable_count = sum(1 for view in all_views if view["planner_calculable"])
        stable_calculable_count = sum(1 for view in all_views if view["stable_calculable"])

        return {
            "summary": {
                "passive_identity_record_count": len(passive_tree_views) + len(passive_node_views),
                "passive_tree_count": len(passive_tree_views),
                "passive_node_count": len(passive_node_views),
                "skill_identity_record_count": len(skill_views) + len(skill_tree_views) + len(skill_node_views),
                "skill_count": len(skill_views),
                "skill_tree_count": len(skill_tree_views),
                "skill_node_count": len(skill_node_views),
                "identity_only_eligible_count": identity_only_eligible_count,
                "planner_calculable_count": planner_calculable_count,
                "stable_calculable_count": stable_calculable_count,
                "production_consumed": False,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
            "passive_domains": _domain_rows(domains, ("passive_tree", "passive_node")),
            "skill_domains": _domain_rows(domains, ("skill", "skill_tree", "skill_node")),
            "fields_exposed": list(PASSIVE_SKILL_IDENTITY_FIELDS),
            "fields_excluded_from_calculation": list(EXCLUDED_CALCULATION_FIELDS),
            "blocked_reason_counts": dict(sorted(blocked_reason_counts.items())),
            "identity_match_status_counts": dict(sorted(identity_status_counts.items())),
            "ownership_status_counts": dict(sorted(ownership_status_counts.items())),
            "metadata_samples": all_views[:sample_limit],
            "skill_identity_audit_summary": identity_summary,
            "skill_identity_examples": {
                "unresolved": identity_report.get("examples", {}).get("unresolved_records", [])[:3],
                "ambiguous": identity_report.get("examples", {}).get("ambiguous_records", [])[:3],
            },
            "passive_skill_tree_metadata_treatment": {
                "passive_tree_links_exposed": True,
                "skill_tree_links_exposed": True,
                "passive_node_effects_exposed_as_planner_stats": False,
                "skill_node_effects_exposed_as_planner_stats": False,
                "tooltip_text_used_for_mechanics": False,
                "notes": [
                    "Tree, owner, and source identity links are exposed as display/provenance metadata only.",
                    "Passive and skill effect text, modifier rows, and node values remain excluded from planner-calculable metadata.",
                ],
            },
            "safety_confirmations": {
                "production_consumed": False,
                "planner_remap_performed": False,
                "planner_output_changed": False,
                "crafting_behavior_changed": False,
                "simulation_behavior_changed": False,
                "stat_aggregation_behavior_changed": False,
                "value_normalization_promoted": False,
                "skill_identity_bridge_added": False,
                "planner_calculable_count": planner_calculable_count,
                "stable_calculable_count": stable_calculable_count,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
                "skill_identity_bridge_safe": False,
            },
        }

    def _default_identity_report_path(self) -> Path:
        root = self.root if self.root is not None else artifact_path("skill_bundle").parents[2]
        return root / "docs" / "generated" / "v2_skill_identity_alignment_report.json"


def build_passive_tree_identity_view(tree: dict[str, Any]) -> dict[str, Any]:
    return _identity_view(
        record=tree,
        domain="passive_tree",
        tree_id=tree.get("canonical_id"),
        owner_class_ids=[tree.get("owner_class_id")] if tree.get("owner_class_id") else [],
        owner_mastery_ids=[tree.get("owner_mastery_id")] if tree.get("owner_mastery_id") else [],
        source_tree_id=tree.get("source_tree_id"),
    )


def build_passive_node_identity_view(node: dict[str, Any]) -> dict[str, Any]:
    return _identity_view(
        record=node,
        domain="passive_node",
        tree_id=node.get("tree_id"),
        owner_class_ids=[node.get("owner_class_id")] if node.get("owner_class_id") else [],
        owner_mastery_ids=[node.get("owner_mastery_id")] if node.get("owner_mastery_id") else [],
        source_tree_id=node.get("source_tree_id"),
    )


def build_skill_identity_view(skill: dict[str, Any], *, identity_status: str = "not_class_mastery_referenced") -> dict[str, Any]:
    source_identity = skill.get("sourceIdentity") if isinstance(skill.get("sourceIdentity"), dict) else {}
    return _identity_view(
        record=skill,
        domain="skill",
        tree_id=skill.get("skill_tree_id"),
        skill_id=skill.get("canonical_id"),
        owner_class_ids=list(skill.get("owner_class_ids") or []),
        owner_mastery_ids=list(skill.get("owner_mastery_ids") or []),
        source_skill_id=skill.get("source_skill_id"),
        source_ability_path_id=source_identity.get("abilityPathId") or skill.get("source_ability_path_id"),
        identity_match_status=identity_status,
    )


def build_skill_tree_identity_view(tree: dict[str, Any]) -> dict[str, Any]:
    return _identity_view(
        record=tree,
        domain="skill_tree",
        tree_id=tree.get("canonical_id"),
        skill_id=tree.get("skill_id"),
        owner_class_ids=list(tree.get("owner_class_ids") or []),
        owner_mastery_ids=list(tree.get("owner_mastery_ids") or []),
        source_tree_id=tree.get("source_tree_id"),
        source_skill_id=tree.get("raw_reference", {}).get("source_skill_id") if isinstance(tree.get("raw_reference"), dict) else None,
    )


def build_skill_node_identity_view(node: dict[str, Any]) -> dict[str, Any]:
    return _identity_view(
        record=node,
        domain="skill_node",
        tree_id=node.get("skill_tree_id"),
        skill_id=node.get("skill_id"),
        owner_class_ids=list(node.get("owner_class_ids") or []),
        owner_mastery_ids=list(node.get("owner_mastery_ids") or []),
        source_tree_id=node.get("source_tree_id"),
        source_skill_id=node.get("raw_reference", {}).get("source_skill_id") if isinstance(node.get("raw_reference"), dict) else None,
    )


def _identity_view(
    *,
    record: dict[str, Any],
    domain: str,
    tree_id: Any = None,
    skill_id: Any = None,
    owner_class_ids: list[Any] | None = None,
    owner_mastery_ids: list[Any] | None = None,
    source_tree_id: Any = None,
    source_skill_id: Any = None,
    source_ability_path_id: Any = None,
    identity_match_status: str = "not_applicable",
) -> dict[str, Any]:
    provenance = record.get("provenance") if isinstance(record.get("provenance"), dict) else {}
    warnings = record.get("warnings") if isinstance(record.get("warnings"), list) else []
    canonical_id = str(record.get("canonical_id") or "")
    display_name = str(record.get("display_name") or canonical_id)
    source_path = str(provenance.get("source_path") or record.get("source_file") or "")
    classes = [str(value) for value in (owner_class_ids or []) if value]
    masteries = [str(value) for value in (owner_mastery_ids or []) if value]
    identity_only_eligible = bool(canonical_id and (display_name or source_path) and source_path)

    return {
        "canonical_id": canonical_id,
        "display_name": display_name,
        "domain": domain,
        "owner_class_ids": classes,
        "owner_mastery_ids": masteries,
        "tree_id": tree_id,
        "skill_id": skill_id,
        "source_id": record.get("source_id"),
        "source_path": source_path,
        "source_tree_id": source_tree_id,
        "source_skill_id": source_skill_id,
        "source_ability_path_id": source_ability_path_id,
        "identity_match_status": identity_match_status,
        "ownership_status": "owned" if classes or masteries or tree_id or skill_id else "unowned",
        "provenance_summary": _provenance_summary(provenance),
        "support_status": str(record.get("support_status") or "unknown"),
        "trust_level": str(record.get("trust_level") or "unknown"),
        "warnings": list(warnings),
        "debug_summary": {
            "source_id": record.get("source_id"),
            "patch_version": record.get("patch_version"),
            "special_behavior_classification": record.get("special_behavior_classification"),
            "stable_calculable_source": bool(record.get("stable_calculable") is True),
            "consumer_safe_fields": record.get("consumer_safe_fields"),
        },
        "identity_only_eligible": identity_only_eligible,
        "planner_calculable": False,
        "stable_calculable": False,
        "blocked_reasons": _blocked_reasons(domain, identity_match_status),
    }


def _blocked_reasons(domain: str, identity_match_status: str) -> list[str]:
    reasons = list(PASSIVE_SKILL_IDENTITY_BLOCKED_REASONS)
    if domain in {"skill", "skill_tree", "skill_node"}:
        reasons.append(SKILL_IDENTITY_BRIDGE_BLOCKED_REASON)
    if identity_match_status in {"unresolved", "ambiguous"}:
        reasons.append(f"skill_identity_{identity_match_status}")
    return reasons


def _skill_identity_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    return {
        "total_refs": int(summary.get("total_class_mastery_skill_references") or 0),
        "safe_top_level_matches": int(summary.get("top_level_path_match_count") or 0),
        "unresolved_refs": int(summary.get("unresolved_reference_count") or 0),
        "ambiguous_refs": int(summary.get("ambiguous_match_count") or 0),
        "bridge_safe": bool(summary.get("bridge_safe") is True),
        "recommended_mapping_strategy": summary.get("recommended_mapping_strategy"),
        "source_data_missing": bool(summary.get("source_data_missing") is True),
    }


def _skill_identity_index(report: dict[str, Any]) -> dict[str, str]:
    examples = report.get("examples") if isinstance(report.get("examples"), dict) else {}
    index: dict[str, str] = {}
    for record in examples.get("resolved_records") or []:
        for skill_id in record.get("candidate_skill_ids") or []:
            index[str(skill_id)] = "resolved_top_level"
    for record in examples.get("ambiguous_records") or []:
        for skill_id in record.get("candidate_skill_ids") or []:
            index[str(skill_id)] = "ambiguous"
    return index


def _domain_rows(domains: Counter[str], labels: tuple[str, ...]) -> list[dict[str, Any]]:
    return [{"domain": label, "identity_record_count": domains.get(label, 0)} for label in labels]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _provenance_summary(provenance: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_path": provenance.get("source_path"),
        "source_type": provenance.get("source_type"),
        "source_id": provenance.get("source_id"),
        "schema_version": provenance.get("schema_version"),
        "extraction_method": provenance.get("extraction_method"),
        "patch_version": provenance.get("patch_version"),
    }
