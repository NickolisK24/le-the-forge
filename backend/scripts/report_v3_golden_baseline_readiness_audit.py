"""Generate the v3 golden baseline readiness audit report.

This audit defines baseline readiness requirements only. It does not create
fixtures, execute baselines, promote candidates, or change planner behavior.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

CANDIDATE_INVENTORY_PATH = REPO_ROOT / "docs/generated/v3_canonical_stat_candidate_inventory_report.json"
STAT_POLICY_PATH = REPO_ROOT / "docs/generated/v3_stat_identity_resolution_policy_report.json"
OPERATION_TAXONOMY_PATH = REPO_ROOT / "docs/generated/v3_operation_semantics_taxonomy_report.json"
VALUE_CONTRACT_PATH = REPO_ROOT / "docs/generated/v3_value_normalization_contract_report.json"
V3_PLAN_PATH = REPO_ROOT / "docs/generated/v3_mechanical_intelligence_plan.json"
DRY_RUN_PATH = REPO_ROOT / "docs/generated/v2_stat_modifier_dry_run_report.json"

OUTPUT_JSON_PATH = REPO_ROOT / "docs/generated/v3_golden_baseline_readiness_audit_report.json"
OUTPUT_MD_PATH = REPO_ROOT / "docs/migration/V3_GOLDEN_BASELINE_READINESS_AUDIT.md"


BASELINE_READINESS_ENTRY_FIELDS = [
    "candidate_id",
    "canonical_stat_id",
    "baseline_readiness_state",
    "candidate_status_from_phase_5",
    "promotion_allowed",
    "baseline_creation_allowed",
    "required_baseline_case_types",
    "missing_baseline_evidence",
    "dependency_blockers",
    "operation_semantics_status",
    "value_normalization_status",
    "stat_identity_status",
    "skill_identity_bridge_status",
    "unsupported_behavior_risk",
    "repeat_validation_requirement",
    "recommended_future_action",
    "provenance",
]

ALLOWED_BASELINE_READINESS_STATES = {
    "audit_only",
    "blocked_by_candidate_status",
    "blocked_by_missing_golden_baseline",
    "blocked_by_operation_semantics",
    "blocked_by_value_normalization",
    "blocked_by_stat_identity_policy",
    "blocked_by_skill_identity_bridge",
    "blocked_by_unsupported_behavior",
    "blocked_by_ambiguous_mapping",
    "unknown_needs_review",
}

REQUIRED_BASELINE_CASE_TYPES = [
    "single_modifier_flat_stat",
    "single_modifier_increased_stat",
    "multiple_modifiers_same_stat",
    "mixed_operation_same_stat",
    "item_affix_source_only",
    "passive_source_only",
    "skill_tree_source_only",
    "idol_source_only",
    "class_attribute_source",
    "resistance_source",
    "negative_or_cost_modifier",
    "conditional_modifier_exclusion",
    "unsupported_behavior_exclusion",
]

FUTURE_FIXTURE_SCHEMA_FIELDS = [
    "baseline_id",
    "candidate_id",
    "canonical_stat_id",
    "source_record_refs",
    "input_modifiers",
    "expected_normalized_values",
    "expected_operation_semantics",
    "expected_final_stat_delta",
    "excluded_behavior_notes",
    "patch_version",
    "provenance",
    "validation_status",
]

EXCLUDED_BASELINE_CATEGORIES = [
    "unique/set scripted mechanics",
    "tooltip-only mechanics",
    "conditional runtime effects",
    "conversion mechanics",
    "threshold mechanics",
    "minion inheritance",
    "skill-specific behavior without skill bridge",
    "ambiguous source mappings",
    "unknown operation semantics",
    "unknown/source-unit value scales",
    "unsupported behavior",
]

BASELINE_EVIDENCE_REQUIREMENTS = [
    "confirmed canonical stat ID",
    "confirmed source stat ID/path",
    "stable source record references",
    "input modifier examples",
    "expected normalized value examples",
    "approved operation semantic examples",
    "expected final stat delta",
    "unsupported behavior exclusion notes",
    "old planner comparison evidence",
    "dry-run comparison evidence",
    "repeat validation evidence",
    "patch/version provenance",
]

REPEAT_VALIDATION_POLICY = {
    "minimum_repeated_runs": 3,
    "requires_distinct_exports_or_patch_snapshots": True,
    "requires_old_planner_comparison": True,
    "requires_dry_run_comparison": True,
    "requires_no_unexplained_delta": True,
    "requires_reversible_promotion_record": True,
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _load_sources() -> dict[str, dict[str, Any]]:
    return {
        "candidate_inventory": _read_json(CANDIDATE_INVENTORY_PATH),
        "stat_policy": _read_json(STAT_POLICY_PATH),
        "operation_taxonomy": _read_json(OPERATION_TAXONOMY_PATH),
        "value_contract": _read_json(VALUE_CONTRACT_PATH),
        "v3_plan": _read_json(V3_PLAN_PATH),
        "dry_run": _read_json(DRY_RUN_PATH),
    }


def _case_types_for_candidate(candidate: dict[str, Any]) -> list[str]:
    case_types: set[str] = set()
    operations = set(candidate.get("operation_families") or [])
    domain = str(candidate.get("domain") or "unknown")
    labels = {str(label).lower() for label in candidate.get("source_labels") or []}

    if "flat" in operations:
        case_types.add("single_modifier_flat_stat")
    if "increased" in operations:
        case_types.add("single_modifier_increased_stat")
    if candidate.get("modifier_row_count", 0) > 1:
        case_types.add("multiple_modifiers_same_stat")
    if len(operations) > 1:
        case_types.add("mixed_operation_same_stat")
    if domain in {"affix", "item_implicit", "mixed"}:
        case_types.add("item_affix_source_only")
    if domain == "skill":
        case_types.add("skill_tree_source_only")
    if domain == "idol_affix_modifier":
        case_types.add("idol_source_only")
    if labels & {"strength", "dexterity", "intelligence", "attunement"}:
        case_types.add("class_attribute_source")
    if any("resist" in label for label in labels):
        case_types.add("resistance_source")
    if operations & {"cost", "less", "reduced"}:
        case_types.add("negative_or_cost_modifier")
    if candidate.get("unsupported_behavior_risk") == "high":
        case_types.add("unsupported_behavior_exclusion")
    return sorted(case_types or {"single_modifier_flat_stat"})


def _readiness_state_for_candidate(candidate: dict[str, Any]) -> tuple[str, list[str], str]:
    status = str(candidate.get("candidate_status") or "unknown_needs_review")
    blockers = set(candidate.get("blocking_reasons") or [])
    if status == "candidate_blocked_by_ambiguity":
        return "blocked_by_ambiguous_mapping", ["ambiguous mapping must be split or proven"], "resolve ambiguity policy before baseline design"
    if status == "candidate_blocked_by_skill_identity_bridge":
        return "blocked_by_skill_identity_bridge", ["skill identity bridge is unbridged"], "wait for skill identity bridge policy"
    if status in {"excluded_unsupported_behavior", "excluded_tooltip_only"}:
        return "blocked_by_unsupported_behavior", ["unsupported behavior remains excluded"], "keep excluded until unsupported behavior policy and baselines exist"
    if status == "candidate_blocked_by_operation_semantics" or "unknown_operation_semantics" in blockers:
        return "blocked_by_operation_semantics", ["operation semantics are not approved"], "wait for operation semantics evidence"
    if status == "candidate_blocked_by_value_normalization" or "value_normalization_audit_only" in blockers:
        return "blocked_by_value_normalization", ["value normalization remains audit_only"], "wait for value normalization evidence"
    if status == "candidate_blocked_by_behavioral_context":
        return "blocked_by_unsupported_behavior", ["behavioral context is not planner-safe"], "define unsupported behavior exclusions"
    if status == "unknown_needs_review":
        return "unknown_needs_review", ["candidate status needs review"], "inventory source identity before baseline planning"
    if "missing_golden_baseline" in blockers or status in {"candidate_needs_evidence", "candidate_blocked_by_missing_baseline"}:
        return "blocked_by_missing_golden_baseline", ["golden baseline evidence is missing"], "design fixture only after dependencies are approved"
    return "blocked_by_candidate_status", ["candidate status is not ready for baseline creation"], "revisit after upstream policies advance"


def _build_readiness_entry(candidate: dict[str, Any]) -> dict[str, Any]:
    state, state_blockers, action = _readiness_state_for_candidate(candidate)
    dependency_blockers = sorted(
        set(state_blockers)
        | set(candidate.get("blocking_reasons") or [])
        | {
            "operation_semantics_taxonomy_only",
            "value_normalization_audit_only",
            "missing_repeat_validation",
        }
    )
    if candidate.get("identity_state") != "canonical_candidate_needs_evidence":
        dependency_blockers.append("stat_identity_policy_incomplete")
    if candidate.get("unsupported_behavior_risk") in {"medium", "high"}:
        dependency_blockers.append("unsupported_behavior_exclusion_required")
    return {
        "candidate_id": candidate["candidate_id"],
        "canonical_stat_id": candidate["canonical_stat_id"],
        "baseline_readiness_state": state,
        "candidate_status_from_phase_5": candidate["candidate_status"],
        "promotion_allowed": False,
        "baseline_creation_allowed": False,
        "required_baseline_case_types": _case_types_for_candidate(candidate),
        "missing_baseline_evidence": BASELINE_EVIDENCE_REQUIREMENTS,
        "dependency_blockers": sorted(set(dependency_blockers)),
        "operation_semantics_status": "taxonomy_only",
        "value_normalization_status": "audit_only",
        "stat_identity_status": candidate.get("identity_state", "unknown_needs_review"),
        "skill_identity_bridge_status": "unbridged",
        "unsupported_behavior_risk": candidate.get("unsupported_behavior_risk", "unknown"),
        "repeat_validation_requirement": REPEAT_VALIDATION_POLICY,
        "recommended_future_action": action,
        "provenance": candidate.get("provenance", {}),
    }


def build_v3_golden_baseline_readiness_audit_report() -> dict[str, Any]:
    sources = _load_sources()
    candidate_report = sources["candidate_inventory"]
    recommended_candidates = candidate_report["recommended_pilot_candidates"]
    inventory_entries = candidate_report["candidate_inventory_entries"]
    excluded_candidates = candidate_report["explicitly_excluded_candidates"]

    readiness_entries = [_build_readiness_entry(candidate) for candidate in recommended_candidates]
    excluded_entries = [_build_readiness_entry(candidate) for candidate in excluded_candidates]
    state_counts = Counter(entry["baseline_readiness_state"] for entry in readiness_entries + excluded_entries)

    report = {
        "schema_version": "v3.golden_baseline_readiness_audit.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "total_candidate_count_from_phase_5": candidate_report["summary"]["total_stat_registry_entries"],
            "phase_5_inventory_entry_count_in_report": len(inventory_entries),
            "recommended_pilot_candidate_count": len(recommended_candidates),
            "explicitly_excluded_candidate_count_in_report": len(excluded_candidates),
            "planner_calculable_count": 0,
            "stable_calculable_count": 0,
            "production_consumed": False,
        },
        "baseline_readiness_entry_fields": BASELINE_READINESS_ENTRY_FIELDS,
        "allowed_baseline_readiness_states": sorted(ALLOWED_BASELINE_READINESS_STATES),
        "candidate_readiness_distribution": _counter_dict(state_counts),
        "recommended_pilot_candidates_reviewed": readiness_entries,
        "excluded_candidate_readiness_entries": excluded_entries,
        "baseline_case_type_requirements": REQUIRED_BASELINE_CASE_TYPES,
        "baseline_evidence_requirements": BASELINE_EVIDENCE_REQUIREMENTS,
        "missing_evidence_summary": [
            {
                "id": "all_recommended_candidates_missing_complete_baseline_evidence",
                "candidate_ids": [entry["candidate_id"] for entry in readiness_entries],
                "missing_evidence": BASELINE_EVIDENCE_REQUIREMENTS,
            },
            {
                "id": "all_candidates_blocked_by_upstream_dependencies",
                "blockers": [
                    "value_normalization_audit_only",
                    "operation_semantics_taxonomy_only",
                    "stat_identity_policy_only",
                    "skill_identity_bridge_unbridged",
                    "missing_repeat_validation",
                ],
            },
        ],
        "dependency_blockers": {
            "operation_semantics": {
                "status": "taxonomy_only",
                "unknown_operation_count": sources["operation_taxonomy"]["unknown_operation_count"],
            },
            "value_normalization": {
                "status": "audit_only",
                "unknown_value_scale_count": sources["value_contract"]["current_value_scale_state"]["unknown_value_scale_count"],
                "source_units_value_scale_count": sources["value_contract"]["current_value_scale_state"]["source_units_value_scale_count"],
            },
            "stat_identity": {
                "status": "policy_only",
                "unresolved_stat_identity_count": sources["stat_policy"]["current_stat_identity_landscape"]["unresolved_stat_identity_count"],
                "ambiguous_mapping_stat_count": sources["stat_policy"]["current_stat_identity_landscape"]["classification_counts"]["blocked_by_ambiguous_mapping"],
            },
            "skill_identity": {
                "status": "unbridged",
            },
        },
        "repeat_validation_policy": REPEAT_VALIDATION_POLICY,
        "proposed_future_fixture_schema": {
            "description": "Future schema only; no fixture files are created in this phase.",
            "fields": FUTURE_FIXTURE_SCHEMA_FIELDS,
        },
        "excluded_baseline_categories": EXCLUDED_BASELINE_CATEGORIES,
        "production_remap_blockers": [
            "planner-calculable count remains 0",
            "stable-calculable count remains 0",
            "production consumed remains false",
            "value normalization remains audit_only",
            "operation semantics remain taxonomy-only",
            "stat identity policy remains audit-only",
            "skill identity bridge remains unbridged",
            "golden baselines are not created",
            "repeat validation has not run",
        ],
        "safety_confirmations": {
            "golden_baselines_created": False,
            "stat_identities_promoted": False,
            "canonical_candidates_promoted": False,
            "stat_calculations_changed": False,
            "values_normalized": False,
            "operation_semantics_implemented": False,
            "planner_calculable_promoted": False,
            "stable_calculable_promoted": False,
            "production_consumed": False,
            "production_planner_changed": False,
            "unresolved_stat_identities_blocked": True,
            "ambiguous_mappings_blocked": True,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
            "planner_calculable_count": 0,
            "stable_calculable_count": 0,
        },
        "source_report_evidence": {
            "phase_5_candidate_status_distribution": candidate_report["candidate_status_distribution"],
            "phase_5_recommended_candidate_ids": [item["candidate_id"] for item in recommended_candidates],
            "dry_run_top_blocked_reasons": sources["dry_run"]["summary"]["top_blocked_reasons"],
            "v3_plan_production_remap_gates": sources["v3_plan"]["production_remap_gate_requirements"],
        },
        "recommended_next_phase": "v3_skill_identity_bridge_policy",
        "metadata": {
            "audit_only": True,
            "golden_baselines_created": False,
            "planner_remap_performed": False,
            "production_consumed": False,
            "source": "v3_golden_baseline_readiness_audit",
        },
    }
    return report


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# V3 Golden Baseline Readiness Audit",
        "",
        "This document defines golden baseline readiness requirements only.",
        "It does not create fixtures, execute baselines, promote candidates, normalize values, or change planner output.",
        "",
        "## Summary",
        "",
        f"- Total candidate count from Phase 5: `{summary['total_candidate_count_from_phase_5']}`",
        f"- Recommended pilot candidates reviewed: `{summary['recommended_pilot_candidate_count']}`",
        f"- Explicitly excluded candidates reviewed: `{summary['explicitly_excluded_candidate_count_in_report']}`",
        f"- Planner-calculable count: `{summary['planner_calculable_count']}`",
        f"- Stable-calculable count: `{summary['stable_calculable_count']}`",
        "",
        "## Candidate Readiness Distribution",
        "",
    ]
    lines.extend(
        f"- `{state}`: `{count}`"
        for state, count in report["candidate_readiness_distribution"].items()
    )
    lines.extend(
        [
            "",
            "## Recommended Pilot Candidates Reviewed",
            "",
            "| Candidate | Readiness | Status From Phase 5 | Required Case Types |",
            "| --- | --- | --- | --- |",
        ]
    )
    for entry in report["recommended_pilot_candidates_reviewed"]:
        lines.append(
            f"| `{entry['canonical_stat_id']}` | `{entry['baseline_readiness_state']}` | "
            f"`{entry['candidate_status_from_phase_5']}` | `{', '.join(entry['required_baseline_case_types'])}` |"
        )
    lines.extend(
        [
            "",
            "## Required Future Baseline Case Types",
            "",
            *[f"- `{item}`" for item in report["baseline_case_type_requirements"]],
            "",
            "## Proposed Future Fixture Schema",
            "",
            *[f"- `{item}`" for item in report["proposed_future_fixture_schema"]["fields"]],
            "",
            "## Explicit Exclusions",
            "",
            *[f"- {item}" for item in report["excluded_baseline_categories"]],
            "",
            "## Repeat Validation Policy",
            "",
        ]
    )
    lines.extend(
        f"- `{key}`: `{str(value).lower() if isinstance(value, bool) else value}`"
        for key, value in report["repeat_validation_policy"].items()
    )
    lines.extend(
        [
            "",
            "## Production Remap Blockers",
            "",
            *[f"- {item}" for item in report["production_remap_blockers"]],
            "",
            "## Safety Confirmations",
            "",
        ]
    )
    safety = report["safety_confirmations"]
    lines.extend(
        [
            f"- Golden baselines created: `{str(safety['golden_baselines_created']).lower()}`",
            f"- Stat identities promoted: `{str(safety['stat_identities_promoted']).lower()}`",
            f"- Canonical candidates promoted: `{str(safety['canonical_candidates_promoted']).lower()}`",
            f"- Stat calculations changed: `{str(safety['stat_calculations_changed']).lower()}`",
            f"- Values normalized: `{str(safety['values_normalized']).lower()}`",
            f"- Operation semantics implemented: `{str(safety['operation_semantics_implemented']).lower()}`",
            f"- Planner-calculable promoted: `{str(safety['planner_calculable_promoted']).lower()}`",
            f"- Stable-calculable promoted: `{str(safety['stable_calculable_promoted']).lower()}`",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Production planner changed: `{str(safety['production_planner_changed']).lower()}`",
            f"- Unresolved stat identities blocked: `{str(safety['unresolved_stat_identities_blocked']).lower()}`",
            f"- Ambiguous mappings blocked: `{str(safety['ambiguous_mappings_blocked']).lower()}`",
            f"- Value normalization: `{safety['value_normalization_status']}`",
            f"- Skill identity bridge: `{safety['skill_identity_bridge_status']}`",
            "",
            "## Recommended Next Phase",
            "",
            f"`{report['recommended_next_phase']}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_report() -> dict[str, Any]:
    report = build_v3_golden_baseline_readiness_audit_report()
    OUTPUT_JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD_PATH.write_text(_render_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    report = write_report()
    print(
        json.dumps(
            {
                "total_candidate_count_from_phase_5": report["summary"]["total_candidate_count_from_phase_5"],
                "recommended_pilot_candidate_count": report["summary"]["recommended_pilot_candidate_count"],
                "candidate_readiness_distribution": report["candidate_readiness_distribution"],
                "planner_calculable_count": report["safety_confirmations"]["planner_calculable_count"],
                "stable_calculable_count": report["safety_confirmations"]["stable_calculable_count"],
                "recommended_next_phase": report["recommended_next_phase"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
