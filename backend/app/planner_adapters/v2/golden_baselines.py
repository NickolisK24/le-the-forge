"""Golden baseline planning for future v2 planner remap work."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE_STATUSES = frozenset(
    {
        "safe_non_mechanical_now",
        "blocked_by_value_normalization",
        "blocked_by_identity_resolution",
        "blocked_by_unsupported_mechanics",
        "blocked_by_missing_existing_baseline",
        "blocked_by_missing_fixture",
        "blocked_by_behavioral_risk",
        "future_mechanical_required",
        "unknown_needs_review",
    }
)

FIXTURE_ROOT = "backend/tests/fixtures/v2/golden_baselines"

BASELINE_CATEGORIES: tuple[dict[str, Any], ...] = (
    {
        "category_id": "item_base_display_metadata",
        "description": "Non-calculating item/base identity and provenance metadata.",
        "current_status": "safe_non_mechanical_now",
        "blocker_reason": None,
        "fixture_path": f"{FIXTURE_ROOT}/item_base_display_metadata.json",
        "required_future_assertions": ["metadata envelope compatibility", "planner-calculable remains false"],
        "safe_to_create_now": True,
        "mechanical_calculation_involved": False,
        "production_output_affected": False,
    },
    {
        "category_id": "affix_display_provenance",
        "description": "Non-calculating affix identity, tier count, and provenance metadata.",
        "current_status": "safe_non_mechanical_now",
        "blocker_reason": None,
        "fixture_path": f"{FIXTURE_ROOT}/affix_display_provenance.json",
        "required_future_assertions": ["modifier values remain absent", "blocked reasons remain visible"],
        "safe_to_create_now": True,
        "mechanical_calculation_involved": False,
        "production_output_affected": False,
    },
    {
        "category_id": "passive_identity_metadata",
        "description": "Passive tree and node identity/provenance metadata without effect math.",
        "current_status": "safe_non_mechanical_now",
        "blocker_reason": None,
        "fixture_path": f"{FIXTURE_ROOT}/passive_identity_metadata.json",
        "required_future_assertions": ["tooltip text is not inferred", "effect rows remain non-calculating"],
        "safe_to_create_now": True,
        "mechanical_calculation_involved": False,
        "production_output_affected": False,
    },
    {
        "category_id": "skill_identity_metadata",
        "description": "Skill and skill tree identity/provenance metadata without effect math.",
        "current_status": "safe_non_mechanical_now",
        "blocker_reason": None,
        "fixture_path": f"{FIXTURE_ROOT}/skill_identity_metadata.json",
        "required_future_assertions": ["unresolved identity refs remain visible", "bridge safe remains false"],
        "safe_to_create_now": True,
        "mechanical_calculation_involved": False,
        "production_output_affected": False,
    },
    {
        "category_id": "stat_registry_identity",
        "description": "Stat registry identity and source-label coverage.",
        "current_status": "safe_non_mechanical_now",
        "blocker_reason": None,
        "fixture_path": f"{FIXTURE_ROOT}/stat_registry_identity.json",
        "required_future_assertions": ["unknown stat IDs remain blocked", "registry count changes are reviewed"],
        "safe_to_create_now": True,
        "mechanical_calculation_involved": False,
        "production_output_affected": False,
    },
    {
        "category_id": "modifier_identity",
        "description": "Modifier registry identity, operation, value-scale, and blocked-reason coverage.",
        "current_status": "safe_non_mechanical_now",
        "blocker_reason": None,
        "fixture_path": f"{FIXTURE_ROOT}/dry_run_summary_snapshot.json",
        "required_future_assertions": ["planner-calculable count remains gated", "blocked reason counts remain explicit"],
        "safe_to_create_now": True,
        "mechanical_calculation_involved": False,
        "production_output_affected": False,
    },
    {
        "category_id": "known_item_affix_stat_output",
        "description": "Existing planner output for representative item affix stat math.",
        "current_status": "blocked_by_value_normalization",
        "blocker_reason": "v2 affix values are source_units and no planner-normalized scale contract exists",
        "fixture_path": f"{FIXTURE_ROOT}/future_item_affix_stat_output.json",
        "required_future_assertions": ["legacy output snapshot", "v2 dry-run parity", "approved value scale family"],
        "safe_to_create_now": False,
        "mechanical_calculation_involved": True,
        "production_output_affected": False,
    },
    {
        "category_id": "known_passive_node_stat_output",
        "description": "Existing planner output for representative passive node stat math.",
        "current_status": "blocked_by_unsupported_mechanics",
        "blocker_reason": "passive effects include scripted and unsupported behavior that is not planner-calculable",
        "fixture_path": f"{FIXTURE_ROOT}/future_passive_node_stat_output.json",
        "required_future_assertions": ["legacy passive output snapshot", "unsupported behavior remains excluded"],
        "safe_to_create_now": False,
        "mechanical_calculation_involved": True,
        "production_output_affected": False,
    },
    {
        "category_id": "known_skill_node_stat_output",
        "description": "Existing planner output for representative skill node stat math.",
        "current_status": "blocked_by_identity_resolution",
        "blocker_reason": "skill identity still has unresolved and ambiguous references",
        "fixture_path": f"{FIXTURE_ROOT}/future_skill_node_stat_output.json",
        "required_future_assertions": ["legacy skill output snapshot", "identity gap remains blocked"],
        "safe_to_create_now": False,
        "mechanical_calculation_involved": True,
        "production_output_affected": False,
    },
    {
        "category_id": "unique_set_unsupported_exclusions",
        "description": "Assertions that unsupported unique/set mechanics remain excluded from stable math.",
        "current_status": "blocked_by_unsupported_mechanics",
        "blocker_reason": "unique/set special behavior remains text-only or unsupported",
        "fixture_path": f"{FIXTURE_ROOT}/unique_set_unsupported_exclusions.json",
        "required_future_assertions": ["unsupported report entries never become stable-calculable by default"],
        "safe_to_create_now": True,
        "mechanical_calculation_involved": False,
        "production_output_affected": False,
    },
    {
        "category_id": "value_scale_normalization_examples",
        "description": "Golden examples proving source-unit to planner-normalized conversion families.",
        "current_status": "blocked_by_value_normalization",
        "blocker_reason": "Phase 10.5 found no safe normalization families",
        "fixture_path": f"{FIXTURE_ROOT}/future_value_scale_examples.json",
        "required_future_assertions": ["source contract", "before/after normalized values", "legacy parity"],
        "safe_to_create_now": False,
        "mechanical_calculation_involved": True,
        "production_output_affected": False,
    },
    {
        "category_id": "operation_examples",
        "description": "Golden examples for flat, increased, more, and conditional operation handling.",
        "current_status": "blocked_by_missing_existing_baseline",
        "blocker_reason": "operation expectations are not locked against current planner output",
        "fixture_path": f"{FIXTURE_ROOT}/future_operation_examples.json",
        "required_future_assertions": ["legacy operation output", "v2 operation classification", "conditional handling rules"],
        "safe_to_create_now": False,
        "mechanical_calculation_involved": True,
        "production_output_affected": False,
    },
    {
        "category_id": "planner_output_vs_v2_dry_run_snapshots",
        "description": "Snapshot comparisons between current planner output and v2 adapter dry-run explanations.",
        "current_status": "future_mechanical_required",
        "blocker_reason": "requires selected representative builds and dry-run parity harness",
        "fixture_path": f"{FIXTURE_ROOT}/future_planner_output_vs_v2_dry_run.json",
        "required_future_assertions": ["legacy planner output unchanged", "v2 adapter explains every blocked delta"],
        "safe_to_create_now": False,
        "mechanical_calculation_involved": True,
        "production_output_affected": False,
    },
)


def build_golden_baseline_plan(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[4]
    dry_run = _read_optional_json(repo_root / "docs" / "generated" / "v2_stat_modifier_dry_run_report.json")
    categories = [dict(category) for category in BASELINE_CATEGORIES]
    status_counts = Counter(category["current_status"] for category in categories)
    blocker_counts = Counter(
        category["current_status"]
        for category in categories
        if category["current_status"] != "safe_non_mechanical_now"
    )
    mechanical_count = sum(1 for category in categories if category["mechanical_calculation_involved"])
    safe_now_count = sum(1 for category in categories if category["safe_to_create_now"])
    blocked_count = len(categories) - safe_now_count

    return {
        "summary": {
            "baseline_category_count": len(categories),
            "safe_now_fixture_count": safe_now_count,
            "blocked_fixture_count": blocked_count,
            "mechanical_fixture_count": mechanical_count,
            "non_mechanical_fixture_count": len(categories) - mechanical_count,
            "production_consumed": False,
            "stable_calculable_count": 0,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
        },
        "baseline_categories": categories,
        "allowed_statuses": sorted(BASELINE_STATUSES),
        "status_counts": dict(sorted(status_counts.items())),
        "blocker_summary": dict(sorted(blocker_counts.items())),
        "fixture_paths": sorted({category["fixture_path"] for category in categories}),
        "future_assertion_requirements": _future_assertion_requirements(categories),
        "required_preconditions_before_mechanical_remap": [
            "stable-calculable gates pass for a limited modifier family",
            "value scale policy has explicit source contracts or legacy parity baselines",
            "unresolved and ambiguous skill identity refs remain blocked or are proven by source data",
            "unsupported/scripted/text-only mechanics remain excluded from stable math",
            "legacy planner output snapshots exist for representative builds",
            "v2 dry-run comparison explains every accepted and blocked delta",
        ],
        "dry_run_reference": {
            "modifier_row_count": dry_run.get("summary", {}).get("modifier_row_count"),
            "blocked_modifier_count": dry_run.get("summary", {}).get("blocked_modifier_count"),
            "comparison_category_summary": dry_run.get("comparison_category_summary", {}),
            "value_scale_distribution": dry_run.get("value_scale_distribution", {}),
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
            "stable_calculable_count": 0,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
        },
    }


def _future_assertion_requirements(categories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "category_id": category["category_id"],
            "required_future_assertions": list(category["required_future_assertions"]),
            "mechanical_calculation_involved": category["mechanical_calculation_involved"],
        }
        for category in categories
    ]


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
