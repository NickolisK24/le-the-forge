"""Dry-run comparison for v2 stat/modifier adapter data."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from app.normalization.v2 import V2ModifierRegistry, V2StatRegistry
from app.repositories.v2.paths import artifact_path

from .eligibility import evaluate_modifier_record


COMPARISON_CATEGORIES = frozenset(
    {
        "matches_current_expectation",
        "blocked_by_value_normalization",
        "blocked_by_unknown_operation",
        "blocked_by_identity_resolution",
        "blocked_by_unsupported_behavior",
        "blocked_by_stable_calculable_policy",
        "blocked_by_missing_golden_baseline",
        "blocked_by_schema_mismatch",
        "unknown_needs_review",
    }
)

GOLDEN_BASELINE_REQUIREMENTS = (
    "known item affix stat output",
    "known passive node stat output",
    "known skill node stat output",
    "known unique/set unsupported behavior exclusions",
    "value scale examples for each normalization family",
    "operation examples for flat, increased, more, and conditional behavior",
    "old planner output versus v2 adapter dry-run comparison snapshots",
)

CURRENT_PLANNER_EXPECTATION_GAPS = (
    "v2 values are still source_units or unknown, while planner math requires normalized values",
    "v2 operation identity is unknown for many passive and skill rows",
    "v2 stat identity still includes stat:unknown and raw serialized stat IDs",
    "v2 scripted, unsupported, and text-only mechanics are intentionally blocked",
    "skill-derived modifier rows retain unresolved or ambiguous source identity gaps",
    "golden output baselines do not yet exist for mechanical remap",
)


class V2StatModifierDryRunComparison:
    """Read-only comparison of v2 modifier rows against future planner gates."""

    def __init__(
        self,
        *,
        root: str | Path | None = None,
        stat_registry: V2StatRegistry | None = None,
        modifier_registry: V2ModifierRegistry | None = None,
    ) -> None:
        self.root = Path(root) if root is not None else None
        self._stat_registry = stat_registry
        self._modifier_registry = modifier_registry

    def load_stat_registry(self) -> V2StatRegistry:
        if self._stat_registry is not None:
            return self._stat_registry
        return V2StatRegistry(artifact_path("stat_registry", root=self.root)).load()

    def load_modifier_registry(self) -> V2ModifierRegistry:
        if self._modifier_registry is not None:
            return self._modifier_registry
        return V2ModifierRegistry(artifact_path("modifier_registry", root=self.root)).load()

    def summarize_dry_run(self, *, sample_limit: int = 10) -> dict[str, Any]:
        stat_registry = self.load_stat_registry()
        modifier_registry = self.load_modifier_registry()
        stats = stat_registry.list_stats()
        modifiers = modifier_registry.list_modifiers()

        operation_counts: Counter[str] = Counter()
        value_scale_counts: Counter[str] = Counter()
        source_type_counts: Counter[str] = Counter()
        blocked_reason_counts: Counter[str] = Counter()
        comparison_category_counts: Counter[str] = Counter()
        stat_identity_counts: Counter[str] = Counter()
        source_record_status_counts: Counter[str] = Counter()
        special_behavior_counts: Counter[str] = Counter()
        adapter_visible_count = 0
        planner_calculable_count = 0
        stable_calculable_count = 0
        blocked_samples: list[dict[str, Any]] = []

        for record in modifiers:
            adapter_visible_count += 1
            result = evaluate_modifier_record(record)
            operation_counts[result.operation] += 1
            value_scale_counts[result.value_scale_status] += 1
            source_type_counts[result.source_type] += 1
            blocked_reason_counts.update(result.blocked_reasons)
            comparison_category_counts[_comparison_category(record, result.blocked_reasons)] += 1
            stat_identity_counts[_stat_identity_status(result.stat_id)] += 1
            source_record_status_counts[str(record.get("source_record_status") or "unknown")] += 1
            special_behavior_counts[str(record.get("special_behavior_classification") or "none")] += 1
            if result.eligible:
                planner_calculable_count += 1
            if result.stable_calculable:
                stable_calculable_count += 1
            if result.blocked_reasons and len(blocked_samples) < sample_limit:
                blocked_samples.append(
                    {
                        **result.to_dict(),
                        "comparison_category": _comparison_category(record, result.blocked_reasons),
                        "raw_stat_id": record.get("raw_stat_id"),
                        "raw_stat_name": record.get("raw_stat_name"),
                    }
                )

        return {
            "summary": {
                "stat_registry_count": len(stats),
                "modifier_row_count": len(modifiers),
                "adapter_visible_modifier_count": adapter_visible_count,
                "planner_calculable_modifier_count": planner_calculable_count,
                "stable_calculable_modifier_count": stable_calculable_count,
                "blocked_modifier_count": len(modifiers) - planner_calculable_count,
                "source_unit_value_scale_count": value_scale_counts.get("source_units", 0),
                "unknown_value_scale_count": value_scale_counts.get("unknown", 0),
                "production_consumed": False,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
            "operation_distribution": dict(sorted(operation_counts.items())),
            "value_scale_distribution": dict(sorted(value_scale_counts.items())),
            "source_type_distribution": dict(sorted(source_type_counts.items())),
            "blocked_reason_counts": dict(sorted(blocked_reason_counts.items())),
            "comparison_category_summary": dict(sorted(comparison_category_counts.items())),
            "stat_identity_findings": dict(sorted(stat_identity_counts.items())),
            "modifier_identity_coverage": {
                "canonical_modifier_id_count": sum(1 for record in modifiers if record.get("canonical_modifier_id")),
                "source_type_counts": dict(sorted(source_type_counts.items())),
                "source_record_status_counts": dict(sorted(source_record_status_counts.items())),
                "source_identity_status_counts": dict(sorted(Counter(str(record.get("source_identity_status") or "unknown") for record in modifiers).items())),
            },
            "unsupported_scripted_text_only_counts": {
                "source_record_status_counts": dict(sorted(source_record_status_counts.items())),
                "special_behavior_classification_counts": dict(sorted(special_behavior_counts.items())),
            },
            "current_planner_expectation_gaps": list(CURRENT_PLANNER_EXPECTATION_GAPS),
            "golden_baseline_requirements": list(GOLDEN_BASELINE_REQUIREMENTS),
            "blocked_samples": blocked_samples,
            "allowed_comparison_categories": sorted(COMPARISON_CATEGORIES),
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
            },
        }


def _comparison_category(record: dict[str, Any], blocked_reasons: tuple[str, ...]) -> str:
    reasons = set(blocked_reasons)
    if not reasons:
        return "matches_current_expectation"
    if {"source_units_value_scale", "unknown_value_scale"} & reasons:
        return "blocked_by_value_normalization"
    if "unknown_operation" in reasons:
        return "blocked_by_unknown_operation"
    if {"unresolved_stat_identity", "unresolved_skill_identity"} & reasons:
        return "blocked_by_identity_resolution"
    if {"unsupported_behavior", "scripted_behavior", "text_only_behavior", "unknown_behavior"} & reasons:
        return "blocked_by_unsupported_behavior"
    if "not_stable_calculable" in reasons or record.get("stable_calculable") is not True:
        return "blocked_by_stable_calculable_policy"
    return "unknown_needs_review"


def _stat_identity_status(stat_id: str) -> str:
    if not stat_id or stat_id == "stat:unknown":
        return "unknown"
    if stat_id.startswith("stat:"):
        return "canonicalized"
    return "unknown_needs_review"
