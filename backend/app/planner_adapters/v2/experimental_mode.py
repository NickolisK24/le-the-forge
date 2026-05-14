"""Opt-in experimental facade for v2 planner adapter diagnostics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .adapter import V2PlannerSafeAdapter
from .affix_metadata import V2AffixDisplayProvenanceMetadata
from .diagnostics import build_planner_adapter_diagnostics
from .golden_baselines import build_golden_baseline_plan
from .item_metadata import V2ItemBaseDisplayMetadata
from .metadata import V2PlannerMetadataRemap
from .passive_skill_identity import V2PassiveSkillIdentityMetadata
from .stat_modifier_dry_run import V2StatModifierDryRunComparison


GATE_MECHANISM = "explicit_enabled_argument"

INCLUDED_SUMMARIES = (
    "adapter_eligibility",
    "planner_adapter_diagnostics",
    "planner_metadata",
    "item_base_display_metadata",
    "affix_display_provenance",
    "passive_skill_identity",
    "stat_modifier_dry_run",
    "golden_baseline_readiness",
)


class V2ExperimentalPlannerAdapterMode:
    """Aggregate v2 adapter context behind an explicit disabled-by-default gate."""

    def __init__(self, *, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else None

    def summarize_mode(self, *, enabled: bool = False, sample_limit: int = 5) -> dict[str, Any]:
        if not enabled:
            return _disabled_summary()

        adapter = V2PlannerSafeAdapter(root=self.root).summarize_eligibility(sample_limit=sample_limit)
        diagnostics = build_planner_adapter_diagnostics(root=self.root, sample_limit=sample_limit)
        metadata = V2PlannerMetadataRemap(root=self.root).summarize_metadata(sample_limit=sample_limit)
        item_metadata = V2ItemBaseDisplayMetadata(root=self.root).summarize_metadata(sample_limit=sample_limit)
        affix_metadata = V2AffixDisplayProvenanceMetadata(root=self.root).summarize_metadata(sample_limit=sample_limit)
        passive_skill_identity = V2PassiveSkillIdentityMetadata(root=self.root).summarize_identity_metadata(
            sample_limit=sample_limit
        )
        stat_modifier_dry_run = V2StatModifierDryRunComparison(root=self.root).summarize_dry_run(
            sample_limit=sample_limit
        )
        golden_baselines = build_golden_baseline_plan(root=self.root)

        blocked_reason_summary = _combined_blocked_reasons(
            adapter.get("blocked_reason_counts", {}),
            diagnostics.get("blocked_reason_counts", {}),
            metadata.get("blocked_reason_counts", {}),
            item_metadata.get("blocked_reason_counts", {}),
            affix_metadata.get("blocked_reason_counts", {}),
            passive_skill_identity.get("blocked_reason_counts", {}),
            stat_modifier_dry_run.get("blocked_reason_counts", {}),
        )

        return {
            "schema_version": "v2.experimental_planner_adapter_mode.1",
            "mode": {
                "enabled": True,
                "active": True,
                "status": "enabled",
                "gate_mechanism": GATE_MECHANISM,
                "default_enabled": False,
                "read_only": True,
                "experimental": True,
                "optional_route_added": False,
            },
            "summary": {
                "summaries_included": list(INCLUDED_SUMMARIES),
                "adapter_visible_modifier_count": adapter["summary"]["inspected_modifier_count"],
                "planner_calculable_count": adapter["summary"]["eligible_planner_calculable_count"],
                "stable_calculable_count": adapter["summary"]["stable_calculable_count"],
                "blocked_modifier_count": adapter["summary"]["blocked_modifier_count"],
                "display_only_candidate_count": diagnostics["summary"]["display_only_candidate_count"],
                "blocked_mechanical_category_count": diagnostics["summary"]["blocked_mechanical_category_count"],
                "safe_now_baseline_fixture_count": golden_baselines["summary"]["safe_now_fixture_count"],
                "blocked_baseline_fixture_count": golden_baselines["summary"]["blocked_fixture_count"],
                "production_consumed": False,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
            "summaries": {
                "adapter_eligibility": adapter["summary"],
                "planner_adapter_diagnostics": diagnostics["summary"],
                "planner_metadata": metadata["summary"],
                "item_base_display_metadata": item_metadata["summary"],
                "affix_display_provenance": affix_metadata["summary"],
                "passive_skill_identity": passive_skill_identity["summary"],
                "stat_modifier_dry_run": stat_modifier_dry_run["summary"],
                "golden_baseline_readiness": golden_baselines["summary"],
            },
            "blocked_reason_summary": blocked_reason_summary,
            "baseline_readiness": {
                "safe_now_fixture_count": golden_baselines["summary"]["safe_now_fixture_count"],
                "blocked_fixture_count": golden_baselines["summary"]["blocked_fixture_count"],
                "mechanical_fixture_count": golden_baselines["summary"]["mechanical_fixture_count"],
                "non_mechanical_fixture_count": golden_baselines["summary"]["non_mechanical_fixture_count"],
                "blocker_summary": golden_baselines["blocker_summary"],
                "required_preconditions_before_mechanical_remap": golden_baselines[
                    "required_preconditions_before_mechanical_remap"
                ],
            },
            "diagnostic_context": {
                "display_only_candidates": diagnostics["display_only_candidates"],
                "blocked_mechanical_data": diagnostics["blocked_mechanical_data"],
                "future_remap_phase_status": diagnostics["future_remap_phase_status"],
                "stat_modifier_comparison_categories": stat_modifier_dry_run["comparison_category_summary"],
                "value_scale_distribution": stat_modifier_dry_run["value_scale_distribution"],
                "skill_identity_audit_summary": passive_skill_identity["skill_identity_audit_summary"],
            },
            "samples": {
                "adapter_blocked": adapter.get("blocked_samples", [])[:sample_limit],
                "stat_modifier_blocked": stat_modifier_dry_run.get("blocked_samples", [])[:sample_limit],
            },
            "safety_confirmations": _safety_confirmations(
                planner_calculable_count=adapter["summary"]["eligible_planner_calculable_count"],
                stable_calculable_count=adapter["summary"]["stable_calculable_count"],
            ),
        }


def _disabled_summary() -> dict[str, Any]:
    return {
        "schema_version": "v2.experimental_planner_adapter_mode.1",
        "mode": {
            "enabled": False,
            "active": False,
            "status": "disabled",
            "gate_mechanism": GATE_MECHANISM,
            "default_enabled": False,
            "read_only": True,
            "experimental": True,
            "optional_route_added": False,
        },
        "summary": {
            "summaries_included": [],
            "adapter_visible_modifier_count": 0,
            "planner_calculable_count": 0,
            "stable_calculable_count": 0,
            "blocked_modifier_count": 0,
            "display_only_candidate_count": 0,
            "blocked_mechanical_category_count": 0,
            "safe_now_baseline_fixture_count": 0,
            "blocked_baseline_fixture_count": 0,
            "production_consumed": False,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
        },
        "summaries": {},
        "blocked_reason_summary": [],
        "baseline_readiness": {},
        "diagnostic_context": {},
        "samples": {},
        "safety_confirmations": _safety_confirmations(planner_calculable_count=0, stable_calculable_count=0),
    }


def _combined_blocked_reasons(*reason_maps: dict[str, Any], limit: int = 12) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for reason_map in reason_maps:
        for reason, count in reason_map.items():
            counter[str(reason)] += int(count or 0)
    return [
        {"reason": reason, "count": count}
        for reason, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def _safety_confirmations(*, planner_calculable_count: int, stable_calculable_count: int) -> dict[str, Any]:
    return {
        "production_consumed": False,
        "production_planner_output_changed": False,
        "planner_remap_performed": False,
        "mechanical_calculations_performed": False,
        "production_planner_route_added": False,
        "crafting_behavior_changed": False,
        "simulation_behavior_changed": False,
        "stat_aggregation_behavior_changed": False,
        "value_normalization_promoted": False,
        "skill_identity_bridge_added": False,
        "planner_calculable_count": int(planner_calculable_count),
        "stable_calculable_count": int(stable_calculable_count),
        "value_normalization_status": "audit_only",
        "skill_identity_bridge_status": "unbridged",
    }
