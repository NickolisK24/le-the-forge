"""Generate the v3 stat identity resolution policy report.

This report is policy-only. It defines the evidence and gate structure for
future stat identity promotion without resolving identities or changing runtime
planner behavior.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

STAT_REGISTRY_PATH = REPO_ROOT / "docs/generated/v2_stat_registry.json"
MODIFIER_REGISTRY_PATH = REPO_ROOT / "docs/generated/v2_modifier_registry.json"
DRY_RUN_REPORT_PATH = REPO_ROOT / "docs/generated/v2_stat_modifier_dry_run_report.json"
VALUE_CONTRACT_REPORT_PATH = REPO_ROOT / "docs/generated/v3_value_normalization_contract_report.json"
OPERATION_TAXONOMY_REPORT_PATH = REPO_ROOT / "docs/generated/v3_operation_semantics_taxonomy_report.json"
V3_PLAN_REPORT_PATH = REPO_ROOT / "docs/generated/v3_mechanical_intelligence_plan.json"

OUTPUT_JSON_PATH = REPO_ROOT / "docs/generated/v3_stat_identity_resolution_policy_report.json"
OUTPUT_MD_PATH = REPO_ROOT / "docs/migration/V3_STAT_IDENTITY_RESOLUTION_POLICY.md"


REQUIRED_POLICY_FIELDS = [
    "stat_identity_id",
    "canonical_stat_id",
    "source_stat_id",
    "source_label",
    "domain",
    "identity_state",
    "match_method",
    "confidence_level",
    "source_examples",
    "modifier_examples",
    "operation_dependencies",
    "value_scale_dependencies",
    "golden_baseline_refs",
    "unsupported_behavior_exclusions",
    "validation_status",
    "promotion_status",
    "blocked_reasons",
    "provenance",
]

IDENTITY_STATES = {
    "audit_only",
    "source_known",
    "canonical_candidate_needs_evidence",
    "blocked_by_missing_source_id",
    "blocked_by_ambiguous_mapping",
    "blocked_by_unknown_stat",
    "blocked_by_behavioral_context",
    "blocked_by_operation_semantics",
    "blocked_by_value_normalization",
    "blocked_by_missing_baseline",
    "unknown_needs_review",
    "planner_identity_experimental",
    "planner_identity_stable",
}

CURRENT_IDENTITY_STATES = IDENTITY_STATES - {
    "planner_identity_experimental",
    "planner_identity_stable",
}

EVIDENCE_REQUIREMENTS = [
    {
        "id": "source_stat_id_path",
        "description": "Source stat ID and source path are present and version-traceable.",
    },
    {
        "id": "canonical_stat_id",
        "description": "Canonical target stat ID is explicit and reversible.",
    },
    {
        "id": "stable_source_examples",
        "description": "Representative source examples are stable across exports.",
    },
    {
        "id": "modifier_examples",
        "description": "Representative modifier examples reference the candidate identity.",
    },
    {
        "id": "known_operation_semantics",
        "description": "Operation semantics are approved for the candidate domain.",
    },
    {
        "id": "known_value_scale_or_unnecessary",
        "description": "Value scale is approved or explicitly irrelevant to identity use.",
    },
    {
        "id": "unsupported_scripted_behavior_exclusions",
        "description": "Unsupported, scripted, and text-only mechanics are excluded or modeled.",
    },
    {
        "id": "golden_baseline_coverage",
        "description": "Existing behavior and candidate identity behavior have golden coverage.",
    },
    {
        "id": "patch_version_provenance",
        "description": "Patch, export, and provenance traceability is recorded.",
    },
    {
        "id": "dry_run_comparison_evidence",
        "description": "Dry-run comparison proves no production planner consumption.",
    },
    {
        "id": "repeat_validation_evidence",
        "description": "Repeated validation confirms the mapping remains stable.",
    },
]

DISALLOWED_ASSUMPTIONS = [
    "Do not infer stat identity from tooltip text.",
    "Do not guess semantic identity from labels alone.",
    "Do not infer planner behavior without approved operation semantics.",
    "Do not infer planner behavior without value normalization evidence.",
    "Do not assume scripted or runtime mechanics from structural names.",
    "Do not assume unsupported unique or set mechanics are calculable.",
    "Do not bridge skill identities to make stat identity promotion pass.",
    "Do not apply cross-domain identity mappings without domain-specific evidence.",
]

FUTURE_SEQUENCE = [
    "Inventory source stat identity forms.",
    "Classify identity states.",
    "Select narrow canonical candidate.",
    "Collect source examples.",
    "Collect modifier examples.",
    "Verify operation semantics.",
    "Verify value normalization.",
    "Establish golden baseline.",
    "Run dry-run comparison.",
    "Mark experimental only.",
    "Repeat validation.",
    "Promote stable only after sustained evidence.",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _load_sources() -> dict[str, dict[str, Any]]:
    return {
        "stat_registry": _read_json(STAT_REGISTRY_PATH),
        "modifier_registry": _read_json(MODIFIER_REGISTRY_PATH),
        "dry_run": _read_json(DRY_RUN_REPORT_PATH),
        "value_contract": _read_json(VALUE_CONTRACT_REPORT_PATH),
        "operation_taxonomy": _read_json(OPERATION_TAXONOMY_REPORT_PATH),
        "v3_plan": _read_json(V3_PLAN_REPORT_PATH),
    }


def _classify_stat_record(record: dict[str, Any]) -> dict[str, Any]:
    canonical_stat_id = str(record.get("canonical_stat_id") or "stat:unknown")
    source_stat_ids = record.get("source_stat_ids") or []
    raw_names = record.get("raw_names") or []
    warnings = [str(item) for item in record.get("warnings") or []]
    source_categories = record.get("source_categories") or []

    blocked_reasons: list[str] = []
    if canonical_stat_id == "stat:unknown":
        identity_state = "blocked_by_unknown_stat"
        blocked_reasons.append("unknown_stat")
    elif not source_stat_ids:
        identity_state = "blocked_by_missing_source_id"
        blocked_reasons.append("missing_source_stat_id")
    elif len(raw_names) > 1:
        identity_state = "blocked_by_ambiguous_mapping"
        blocked_reasons.append("multiple_raw_names_for_canonical_stat")
    else:
        identity_state = "canonical_candidate_needs_evidence"
        blocked_reasons.append("candidate_requires_complete_evidence")

    if any("scripted_runtime_behavior" in warning or "unsupported_special_behavior" in warning for warning in warnings):
        blocked_reasons.append("behavioral_context_not_planner_safe")
    if any(category in {"unique_modifier", "set_item_modifier", "set_bonus_modifier"} for category in source_categories):
        blocked_reasons.append("unique_set_behavior_exclusion_required")
    if any("source-units" in warning or "source_units" in warning for warning in warnings):
        blocked_reasons.append("value_normalization_audit_only")

    return {
        "canonical_stat_id": canonical_stat_id,
        "identity_state": identity_state,
        "modifier_count": int(record.get("modifier_count") or 0),
        "source_category_count": len(source_categories),
        "source_stat_id_count": len(source_stat_ids),
        "raw_name_count": len(raw_names),
        "blocked_reasons": sorted(set(blocked_reasons)),
        "promotion_status": identity_state,
        "planner_identity_safe": False,
    }


def _build_stat_identity_landscape(
    stat_records: list[dict[str, Any]],
    modifier_records: list[dict[str, Any]],
    dry_run_summary: dict[str, Any],
) -> dict[str, Any]:
    classifications = [_classify_stat_record(record) for record in stat_records]
    state_counts = Counter(item["identity_state"] for item in classifications)
    modifier_counts_by_state: Counter[str] = Counter()
    blocker_counts: Counter[str] = Counter()
    for item in classifications:
        modifier_counts_by_state[item["identity_state"]] += item["modifier_count"]
        blocker_counts.update(item["blocked_reasons"])

    stat_id_counts = Counter(str(record.get("stat_id") or "stat:unknown") for record in modifier_records)
    source_type_counts = Counter(str(record.get("source_type") or "unknown") for record in modifier_records)

    unknown_stat_modifier_count = int(stat_id_counts.get("stat:unknown", 0))
    unresolved_from_dry_run = int(dry_run_summary.get("top_blocked_reasons", [{}])[8].get("count", 0)) if dry_run_summary.get("top_blocked_reasons") else unknown_stat_modifier_count
    unresolved_stat_identity_count = int(dry_run_summary.get("unresolved_stat_identity_count") or unknown_stat_modifier_count or unresolved_from_dry_run)

    return {
        "stat_registry_count": len(stat_records),
        "modifier_row_count": len(modifier_records),
        "unresolved_stat_identity_count": unresolved_stat_identity_count,
        "modifier_rows_affected_by_unresolved_stat_identity": unknown_stat_modifier_count,
        "classification_counts": _counter_dict(state_counts),
        "modifier_counts_by_identity_state": _counter_dict(modifier_counts_by_state),
        "blocker_counts": _counter_dict(blocker_counts),
        "source_type_counts": _counter_dict(source_type_counts),
        "top_modifier_stat_ids": [
            {"stat_id": stat_id, "count": count}
            for stat_id, count in stat_id_counts.most_common(10)
        ],
        "sample_identity_classifications": classifications[:12],
    }


def build_v3_stat_identity_resolution_policy_report() -> dict[str, Any]:
    sources = _load_sources()
    stat_records = sources["stat_registry"]["records"]["stats"]
    modifier_records = sources["modifier_registry"]["records"]["modifiers"]
    dry_run_summary = sources["dry_run"]["summary"]
    value_state = sources["value_contract"]["current_value_scale_state"]
    operation_state = sources["operation_taxonomy"]["current_operation_distribution"]

    landscape = _build_stat_identity_landscape(stat_records, modifier_records, dry_run_summary)

    report = {
        "schema_version": "v3.stat_identity_resolution_policy.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "current_stat_identity_landscape": landscape,
        "identity_classification_summaries": [
            {
                "identity_state": state,
                "stat_count": landscape["classification_counts"].get(state, 0),
                "modifier_count": landscape["modifier_counts_by_identity_state"].get(state, 0),
                "planner_identity_safe": False,
            }
            for state in sorted(CURRENT_IDENTITY_STATES)
        ],
        "policy_fields": REQUIRED_POLICY_FIELDS,
        "identity_states": sorted(IDENTITY_STATES),
        "current_allowed_identity_states": sorted(CURRENT_IDENTITY_STATES),
        "evidence_requirements": EVIDENCE_REQUIREMENTS,
        "disallowed_assumptions": DISALLOWED_ASSUMPTIONS,
        "classification_philosophy": {
            "summary": "Stat identities are versioned evidence claims, not permanent truths.",
            "principles": [
                "trusted",
                "validated",
                "explainable",
                "patch_resilient",
                "then_intelligent",
            ],
            "reversibility_required": True,
        },
        "operation_semantic_dependencies": {
            "required": True,
            "status": "blocked",
            "unknown_operation_count": operation_state["unknown_operation_count"],
            "reason": "stat identity promotion cannot affect planner math until operation semantics are approved.",
        },
        "value_normalization_dependencies": {
            "required": True,
            "status": value_state["value_normalization_status"],
            "unknown_value_scale_count": value_state["unknown_value_scale_count"],
            "source_units_value_scale_count": value_state["source_units_value_scale_count"],
            "reason": "stat identity promotion cannot imply value conversion while normalization is audit-only.",
        },
        "golden_baseline_dependencies": [
            "source stat inventory baseline",
            "canonical candidate mapping baseline",
            "modifier example baseline",
            "operation dependency baseline",
            "value scale dependency baseline",
            "old planner versus dry-run stat identity comparison",
        ],
        "production_remap_blockers": [
            {
                "id": "planner_calculable_zero",
                "blocked": True,
                "detail": "planner-calculable modifier count remains 0",
            },
            {
                "id": "stable_calculable_zero",
                "blocked": True,
                "detail": "stable-calculable modifier count remains 0",
            },
            {
                "id": "unresolved_stat_identities",
                "blocked": True,
                "detail": f"{landscape['unresolved_stat_identity_count']} modifier rows remain affected by unresolved stat identity",
            },
            {
                "id": "operation_semantics_unapproved",
                "blocked": True,
                "detail": "operation semantics remain taxonomy-only",
            },
            {
                "id": "value_normalization_audit_only",
                "blocked": True,
                "detail": "value normalization remains audit-only",
            },
            {
                "id": "missing_golden_baselines",
                "blocked": True,
                "detail": "mechanical stat identity baselines are not implemented",
            },
        ],
        "future_sequence": [
            {"order": index + 1, "description": description}
            for index, description in enumerate(FUTURE_SEQUENCE)
        ],
        "recommended_next_phase": "v3_skill_identity_bridge_policy",
        "safety_confirmations": {
            "stat_identities_promoted": False,
            "stat_calculations_changed": False,
            "values_normalized": False,
            "operation_semantics_implemented": False,
            "planner_calculable_promoted": False,
            "stable_calculable_promoted": False,
            "production_consumed": False,
            "production_planner_changed": False,
            "unresolved_stat_identities_blocked": True,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
            "skill_identity_bridge_added": False,
            "planner_calculable_count": 0,
            "stable_calculable_count": 0,
        },
        "source_report_evidence": {
            "v3_plan_recommended_next_phase": sources["v3_plan"]["readiness_decision"]["recommended_next_phase"],
            "value_contract_recommended_next_phase": sources["value_contract"]["recommended_next_phase"],
            "operation_taxonomy_recommended_next_phase": sources["operation_taxonomy"]["recommended_next_phase"],
            "dry_run_top_blocked_reasons": dry_run_summary["top_blocked_reasons"],
        },
        "metadata": {
            "design_only": True,
            "stat_identity_resolution_implemented": False,
            "planner_remap_performed": False,
            "production_consumed": False,
            "source": "v3_stat_identity_resolution_policy",
        },
    }
    return report


def _render_markdown(report: dict[str, Any]) -> str:
    landscape = report["current_stat_identity_landscape"]
    lines = [
        "# V3 Stat Identity Resolution Policy",
        "",
        "This document defines the stat identity resolution policy.",
        "It does not implement stat identity resolution, stat math, value normalization, or planner output changes.",
        "",
        "## Current Stat Identity Landscape",
        "",
        f"- Stat registry entries: `{landscape['stat_registry_count']}`",
        f"- Modifier rows: `{landscape['modifier_row_count']}`",
        f"- Unresolved stat identity count: `{landscape['unresolved_stat_identity_count']}`",
        f"- Modifier rows affected by unresolved stat identity: `{landscape['modifier_rows_affected_by_unresolved_stat_identity']}`",
        "",
        "## Identity Classification Summary",
        "",
        "| Identity State | Stat Count | Modifier Count |",
        "| --- | ---: | ---: |",
    ]
    for item in report["identity_classification_summaries"]:
        if item["stat_count"] or item["modifier_count"]:
            lines.append(
                f"| `{item['identity_state']}` | `{item['stat_count']}` | `{item['modifier_count']}` |"
            )

    lines.extend(
        [
            "",
            "## Policy Fields",
            "",
            *[f"- `{field}`" for field in report["policy_fields"]],
            "",
            "## Identity States",
            "",
            *[f"- `{state}`" for state in report["identity_states"]],
            "",
            "Current records are not allowed to use `planner_identity_experimental` or `planner_identity_stable` in this phase.",
            "",
            "## Evidence Requirements",
            "",
        ]
    )
    lines.extend(
        f"- `{item['id']}`: {item['description']}"
        for item in report["evidence_requirements"]
    )
    lines.extend(
        [
            "",
            "## Disallowed Assumptions",
            "",
            *[f"- {item}" for item in report["disallowed_assumptions"]],
            "",
            "## Classification Philosophy",
            "",
            "Stat identities are versioned evidence claims, not permanent truths.",
            "Mappings must remain reversible when future patches invalidate assumptions.",
            "The ordering is trusted, validated, explainable, patch-resilient, then intelligent.",
            "",
            "## Dependencies",
            "",
            f"- Operation semantics: `{report['operation_semantic_dependencies']['status']}`",
            f"- Unknown operations: `{report['operation_semantic_dependencies']['unknown_operation_count']}`",
            f"- Value normalization: `{report['value_normalization_dependencies']['status']}`",
            f"- Unknown value scales: `{report['value_normalization_dependencies']['unknown_value_scale_count']}`",
            f"- Source-units value scales: `{report['value_normalization_dependencies']['source_units_value_scale_count']}`",
            "",
            "## Production Remap Blockers",
            "",
        ]
    )
    lines.extend(
        f"- `{item['id']}`: {item['detail']}"
        for item in report["production_remap_blockers"]
    )
    lines.extend(
        [
            "",
            "## Future Sequence",
            "",
            "| Order | Step |",
            "| ---: | --- |",
        ]
    )
    lines.extend(
        f"| `{item['order']}` | {item['description']} |"
        for item in report["future_sequence"]
    )
    safety = report["safety_confirmations"]
    lines.extend(
        [
            "",
            "## Safety Confirmations",
            "",
            f"- Stat identities promoted: `{str(safety['stat_identities_promoted']).lower()}`",
            f"- Stat calculations changed: `{str(safety['stat_calculations_changed']).lower()}`",
            f"- Values normalized: `{str(safety['values_normalized']).lower()}`",
            f"- Operation semantics implemented: `{str(safety['operation_semantics_implemented']).lower()}`",
            f"- Planner-calculable promoted: `{str(safety['planner_calculable_promoted']).lower()}`",
            f"- Stable-calculable promoted: `{str(safety['stable_calculable_promoted']).lower()}`",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Production planner changed: `{str(safety['production_planner_changed']).lower()}`",
            f"- Unresolved stat identities blocked: `{str(safety['unresolved_stat_identities_blocked']).lower()}`",
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
    report = build_v3_stat_identity_resolution_policy_report()
    OUTPUT_JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD_PATH.write_text(_render_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    report = write_report()
    landscape = report["current_stat_identity_landscape"]
    print(
        json.dumps(
            {
                "stat_registry_count": landscape["stat_registry_count"],
                "modifier_row_count": landscape["modifier_row_count"],
                "unresolved_stat_identity_count": landscape["unresolved_stat_identity_count"],
                "planner_calculable_count": report["safety_confirmations"]["planner_calculable_count"],
                "stable_calculable_count": report["safety_confirmations"]["stable_calculable_count"],
                "value_normalization_status": report["safety_confirmations"]["value_normalization_status"],
                "recommended_next_phase": report["recommended_next_phase"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
