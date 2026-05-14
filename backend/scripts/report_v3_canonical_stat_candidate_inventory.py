"""Generate the v3 canonical stat candidate inventory report.

This report ranks future stat identity candidates for investigation only. It
does not resolve stat identities, promote candidates, normalize values, or
change planner behavior.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

STAT_REGISTRY_PATH = REPO_ROOT / "docs/generated/v2_stat_registry.json"
MODIFIER_REGISTRY_PATH = REPO_ROOT / "docs/generated/v2_modifier_registry.json"
DRY_RUN_REPORT_PATH = REPO_ROOT / "docs/generated/v2_stat_modifier_dry_run_report.json"
VALUE_CONTRACT_REPORT_PATH = REPO_ROOT / "docs/generated/v3_value_normalization_contract_report.json"
OPERATION_TAXONOMY_REPORT_PATH = REPO_ROOT / "docs/generated/v3_operation_semantics_taxonomy_report.json"
STAT_POLICY_REPORT_PATH = REPO_ROOT / "docs/generated/v3_stat_identity_resolution_policy_report.json"
V3_PLAN_REPORT_PATH = REPO_ROOT / "docs/generated/v3_mechanical_intelligence_plan.json"

OUTPUT_JSON_PATH = REPO_ROOT / "docs/generated/v3_canonical_stat_candidate_inventory_report.json"
OUTPUT_MD_PATH = REPO_ROOT / "docs/migration/V3_CANONICAL_STAT_CANDIDATE_INVENTORY.md"


CANDIDATE_ENTRY_FIELDS = [
    "candidate_id",
    "canonical_stat_id",
    "source_stat_ids",
    "source_labels",
    "domain",
    "modifier_row_count",
    "source_example_count",
    "operation_families",
    "value_scale_families",
    "identity_state",
    "candidate_status",
    "confidence_level",
    "ranking_reason",
    "blocking_reasons",
    "required_evidence",
    "golden_baseline_status",
    "unsupported_behavior_risk",
    "promotion_allowed",
    "recommended_future_action",
    "provenance",
]

ALLOWED_CANDIDATE_STATUSES = {
    "audit_only",
    "candidate_needs_evidence",
    "candidate_blocked_by_ambiguity",
    "candidate_blocked_by_operation_semantics",
    "candidate_blocked_by_value_normalization",
    "candidate_blocked_by_missing_baseline",
    "candidate_blocked_by_behavioral_context",
    "candidate_blocked_by_skill_identity_bridge",
    "excluded_unsupported_behavior",
    "excluded_tooltip_only",
    "unknown_needs_review",
}

SIMPLE_OPERATION_FAMILIES = {"flat", "increased", "duration", "cost", "cooldown", "chance"}
LOW_RISK_SOURCE_TYPES = {"affix", "item_implicit", "idol_affix_modifier"}
SKILL_SOURCE_TYPES = {"skill_node_modifier", "skill_structured_value"}
UNSUPPORTED_SOURCE_TYPES = {"unique_modifier", "set_item_modifier", "set_bonus_modifier"}
UNSUPPORTED_BEHAVIOR_VALUES = {"scripted_runtime_behavior", "text_only_effect", "unsupported_special_behavior", "unknown"}
GENERIC_SOURCE_LABELS = {"abilityproperty", "playerproperty"}

REQUIRED_EVIDENCE = [
    "confirmed canonical stat ID",
    "confirmed source stat ID/path",
    "stable source examples",
    "modifier examples",
    "known operation semantics",
    "known value scale or explicit no-normalization-needed decision",
    "unsupported behavior exclusions",
    "golden baseline references",
    "dry-run comparison evidence",
    "repeat validation evidence",
    "patch/version provenance",
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
        "stat_policy": _read_json(STAT_POLICY_REPORT_PATH),
        "v3_plan": _read_json(V3_PLAN_REPORT_PATH),
    }


def _identity_state_for_stat(record: dict[str, Any]) -> str:
    canonical_stat_id = str(record.get("canonical_stat_id") or "stat:unknown")
    source_stat_ids = record.get("source_stat_ids") or []
    raw_names = record.get("raw_names") or []
    if canonical_stat_id == "stat:unknown":
        return "blocked_by_unknown_stat"
    if not source_stat_ids:
        return "blocked_by_missing_source_id"
    if len(raw_names) > 1:
        return "blocked_by_ambiguous_mapping"
    return "canonical_candidate_needs_evidence"


def _domain_for_sources(source_types: set[str]) -> str:
    if source_types <= {"affix"}:
        return "affix"
    if source_types <= {"item_implicit"}:
        return "item_implicit"
    if source_types <= {"idol_affix_modifier"}:
        return "idol_affix_modifier"
    if source_types & SKILL_SOURCE_TYPES:
        return "skill"
    if source_types & UNSUPPORTED_SOURCE_TYPES:
        return "unique_set"
    if source_types:
        return "mixed"
    return "unknown"


def _unsupported_risk(modifiers: list[dict[str, Any]], source_types: set[str]) -> str:
    special_values = {str(item.get("special_behavior_classification") or "none") for item in modifiers}
    if source_types & UNSUPPORTED_SOURCE_TYPES:
        return "high"
    if special_values & UNSUPPORTED_BEHAVIOR_VALUES:
        return "high"
    if source_types & SKILL_SOURCE_TYPES:
        return "medium"
    return "low"


def _status_for_candidate(
    *,
    identity_state: str,
    operations: set[str],
    value_scales: set[str],
    source_types: set[str],
    unsupported_risk: str,
) -> tuple[str, list[str], str]:
    reasons: list[str] = []
    action = "collect complete identity evidence before any experimental promotion"

    if identity_state == "blocked_by_unknown_stat":
        return "unknown_needs_review", ["unknown_stat_identity"], "exclude until source stat identity exists"
    if identity_state == "blocked_by_ambiguous_mapping":
        reasons.append("ambiguous_source_mapping")
        status = "candidate_blocked_by_ambiguity"
        action = "split or prove ambiguous source labels before pilot consideration"
    elif source_types & UNSUPPORTED_SOURCE_TYPES:
        reasons.append("unsupported_unique_set_behavior")
        status = "excluded_unsupported_behavior"
        action = "keep excluded until unsupported behavior policy and baselines exist"
    elif source_types & SKILL_SOURCE_TYPES:
        reasons.append("skill_identity_bridge_required")
        status = "candidate_blocked_by_skill_identity_bridge"
        action = "wait for skill identity bridge policy before pilot consideration"
    elif unsupported_risk == "high":
        reasons.append("unsupported_or_scripted_behavior")
        status = "candidate_blocked_by_behavioral_context"
        action = "exclude unsupported behavior and establish explicit baseline coverage"
    elif "unknown" in operations:
        reasons.append("unknown_operation_semantics")
        status = "candidate_blocked_by_operation_semantics"
        action = "wait for operation semantics taxonomy evidence"
    elif value_scales - {"not_applicable"}:
        reasons.append("value_normalization_audit_only")
        status = "candidate_blocked_by_value_normalization"
        action = "wait for value normalization evidence and baseline coverage"
    else:
        status = "candidate_needs_evidence"

    if not reasons:
        reasons.append("missing_golden_baseline")
        status = "candidate_blocked_by_missing_baseline"
    elif "missing_golden_baseline" not in reasons:
        reasons.append("missing_golden_baseline")

    return status, sorted(set(reasons)), action


def _rank_score(
    *,
    identity_state: str,
    operations: set[str],
    value_scales: set[str],
    source_types: set[str],
    modifier_count: int,
    raw_name_count: int,
    unsupported_risk: str,
) -> int:
    score = 0
    if identity_state == "canonical_candidate_needs_evidence":
        score += 40
    if raw_name_count == 1:
        score += 15
    if source_types and source_types <= LOW_RISK_SOURCE_TYPES:
        score += 20
    if operations and operations <= SIMPLE_OPERATION_FAMILIES:
        score += 15
    if value_scales == {"source_units"}:
        score += 5
    if unsupported_risk == "low":
        score += 10
    if source_types & SKILL_SOURCE_TYPES:
        score -= 25
    if source_types & UNSUPPORTED_SOURCE_TYPES:
        score -= 35
    if identity_state == "blocked_by_ambiguous_mapping":
        score -= 30
    if "unknown" in operations:
        score -= 25
    if "unknown" in value_scales:
        score -= 15
    return score + min(modifier_count, 100) // 10


def _build_candidate_entry(record: dict[str, Any], modifiers: list[dict[str, Any]]) -> dict[str, Any]:
    canonical_stat_id = str(record.get("canonical_stat_id") or "stat:unknown")
    source_stat_ids = [str(item) for item in record.get("source_stat_ids") or []]
    raw_names = [str(item) for item in record.get("raw_names") or []]
    source_types = {str(item.get("source_type") or "unknown") for item in modifiers}
    operations = {str(item.get("operation") or "unknown") for item in modifiers}
    value_scales = {str(item.get("value_scale_status") or "unknown") for item in modifiers}
    identity_state = _identity_state_for_stat(record)
    unsupported_risk = _unsupported_risk(modifiers, source_types)
    status, blocking_reasons, action = _status_for_candidate(
        identity_state=identity_state,
        operations=operations,
        value_scales=value_scales,
        source_types=source_types,
        unsupported_risk=unsupported_risk,
    )
    score = _rank_score(
        identity_state=identity_state,
        operations=operations,
        value_scales=value_scales,
        source_types=source_types,
        modifier_count=len(modifiers),
        raw_name_count=len(raw_names),
        unsupported_risk=unsupported_risk,
    )
    if score >= 70:
        confidence = "medium_for_future_investigation"
    elif score >= 40:
        confidence = "low_pending_evidence"
    else:
        confidence = "blocked_or_unknown"

    source_examples = sorted({str(item.get("source_id") or "unknown") for item in modifiers})[:10]
    modifier_examples = [
        str(item.get("canonical_modifier_id") or "unknown")
        for item in modifiers[:5]
    ]
    domain = _domain_for_sources(source_types)
    return {
        "candidate_id": f"candidate:{canonical_stat_id.removeprefix('stat:') or 'unknown'}",
        "canonical_stat_id": canonical_stat_id,
        "source_stat_ids": source_stat_ids,
        "source_labels": raw_names,
        "domain": domain,
        "modifier_row_count": len(modifiers),
        "source_example_count": len(source_examples),
        "operation_families": sorted(operations),
        "value_scale_families": sorted(value_scales),
        "identity_state": identity_state,
        "candidate_status": status,
        "confidence_level": confidence,
        "ranking_score": score,
        "ranking_reason": (
            "ranked by narrow source identity, low ambiguity, simple operation families, "
            "source-unit-only value scale, low unsupported behavior risk, and modifier coverage"
        ),
        "blocking_reasons": blocking_reasons,
        "required_evidence": REQUIRED_EVIDENCE,
        "golden_baseline_status": "missing",
        "unsupported_behavior_risk": unsupported_risk,
        "promotion_allowed": False,
        "recommended_future_action": action,
        "source_examples": source_examples,
        "modifier_examples": modifier_examples,
        "provenance": record.get("provenance", {}),
    }


def _build_inventory(stat_records: list[dict[str, Any]], modifier_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    modifiers_by_stat: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for modifier in modifier_records:
        modifiers_by_stat[str(modifier.get("stat_id") or "stat:unknown")].append(modifier)
    entries = [
        _build_candidate_entry(record, modifiers_by_stat.get(str(record.get("canonical_stat_id")), []))
        for record in stat_records
    ]
    return sorted(entries, key=lambda item: (item["ranking_score"], item["modifier_row_count"]), reverse=True)


def build_v3_canonical_stat_candidate_inventory_report() -> dict[str, Any]:
    sources = _load_sources()
    stat_records = sources["stat_registry"]["records"]["stats"]
    modifier_records = sources["modifier_registry"]["records"]["modifiers"]
    stat_policy = sources["stat_policy"]
    dry_run_summary = sources["dry_run"]["summary"]

    inventory = _build_inventory(stat_records, modifier_records)
    status_counts = Counter(item["candidate_status"] for item in inventory)
    identity_counts = Counter(item["identity_state"] for item in inventory)
    excluded = [
        item
        for item in inventory
        if item["candidate_status"] in {"excluded_unsupported_behavior", "excluded_tooltip_only", "unknown_needs_review"}
    ][:20]
    recommended = [
        item
        for item in inventory
        if item["candidate_status"] in {
            "candidate_blocked_by_value_normalization",
            "candidate_blocked_by_missing_baseline",
            "candidate_needs_evidence",
        }
        and item["unsupported_behavior_risk"] == "low"
        and item["domain"] in LOW_RISK_SOURCE_TYPES
        and not (set(label.lower() for label in item["source_labels"]) & GENERIC_SOURCE_LABELS)
    ][:10]

    report = {
        "schema_version": "v3.canonical_stat_candidate_inventory.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "total_stat_registry_entries": len(stat_records),
            "total_modifier_rows": len(modifier_records),
            "unresolved_stat_identity_count": stat_policy["current_stat_identity_landscape"]["unresolved_stat_identity_count"],
            "ambiguous_mapping_stat_count": stat_policy["current_stat_identity_landscape"]["classification_counts"]["blocked_by_ambiguous_mapping"],
            "ambiguous_mapping_modifier_count": stat_policy["current_stat_identity_landscape"]["modifier_counts_by_identity_state"]["blocked_by_ambiguous_mapping"],
            "candidate_needs_evidence_stat_count": stat_policy["current_stat_identity_landscape"]["classification_counts"]["canonical_candidate_needs_evidence"],
            "candidate_needs_evidence_modifier_count": stat_policy["current_stat_identity_landscape"]["modifier_counts_by_identity_state"]["canonical_candidate_needs_evidence"],
            "excluded_or_blocked_candidate_count": sum(
                count
                for status, count in status_counts.items()
                if status != "candidate_needs_evidence"
            ),
            "recommended_pilot_candidate_count": len(recommended),
        },
        "candidate_entry_fields": CANDIDATE_ENTRY_FIELDS,
        "allowed_candidate_statuses": sorted(ALLOWED_CANDIDATE_STATUSES),
        "candidate_status_distribution": _counter_dict(status_counts),
        "identity_state_distribution": _counter_dict(identity_counts),
        "conservative_ranking_criteria": [
            "clear source identity",
            "low ambiguity",
            "simple operation families",
            "simple value scale requirements",
            "many modifier examples",
            "low unsupported behavior risk",
            "no skill identity bridge requirement",
            "likely golden baseline feasibility",
        ],
        "candidate_inventory_entries": inventory[:50],
        "recommended_pilot_candidates": recommended,
        "explicitly_excluded_candidates": excluded,
        "dependency_summaries": {
            "operation_semantics": {
                "status": "taxonomy_only",
                "unknown_operation_count": sources["operation_taxonomy"]["unknown_operation_count"],
            },
            "value_normalization": {
                "status": "audit_only",
                "unknown_value_scale_count": sources["value_contract"]["current_value_scale_state"]["unknown_value_scale_count"],
                "source_units_value_scale_count": sources["value_contract"]["current_value_scale_state"]["source_units_value_scale_count"],
            },
            "stat_identity_policy": {
                "status": "policy_only",
                "unresolved_stat_identity_count": stat_policy["current_stat_identity_landscape"]["unresolved_stat_identity_count"],
                "ambiguous_mapping_stat_count": stat_policy["current_stat_identity_landscape"]["classification_counts"]["blocked_by_ambiguous_mapping"],
            },
            "golden_baselines": {
                "status": "missing_mechanical_baselines",
            },
        },
        "evidence_gaps": [
            {
                "id": "recommended_candidate_evidence_gap",
                "applies_to": [item["candidate_id"] for item in recommended],
                "missing_evidence": REQUIRED_EVIDENCE,
            }
        ],
        "production_remap_blockers": [
            "planner-calculable count remains 0",
            "stable-calculable count remains 0",
            "production consumed remains false",
            "value normalization remains audit_only",
            "operation semantics remain taxonomy-only",
            "ambiguous mappings remain blocked",
            "unresolved stat identities remain blocked",
            "skill identity bridge remains unbridged",
            "golden mechanical baselines are missing",
        ],
        "safety_confirmations": {
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
            "dry_run_top_blocked_reasons": dry_run_summary["top_blocked_reasons"],
            "stat_policy_recommended_next_phase": stat_policy["recommended_next_phase"],
            "operation_taxonomy_recommended_next_phase": sources["operation_taxonomy"]["recommended_next_phase"],
            "value_contract_recommended_next_phase": sources["value_contract"]["recommended_next_phase"],
            "v3_plan_recommended_sequence": sources["v3_plan"]["recommended_v3_phase_sequence"],
        },
        "recommended_next_phase": "v3_skill_identity_bridge_policy",
        "metadata": {
            "audit_only": True,
            "stat_identity_resolution_implemented": False,
            "planner_remap_performed": False,
            "production_consumed": False,
            "source": "v3_canonical_stat_candidate_inventory",
        },
    }
    return report


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# V3 Canonical Stat Candidate Inventory",
        "",
        "This document ranks future canonical stat identity candidates for investigation only.",
        "It does not promote stat identities, normalize values, implement operation semantics, or change planner output.",
        "",
        "## Summary",
        "",
        f"- Total stat registry entries: `{summary['total_stat_registry_entries']}`",
        f"- Total modifier rows: `{summary['total_modifier_rows']}`",
        f"- Unresolved stat identity count: `{summary['unresolved_stat_identity_count']}`",
        f"- Ambiguous mapping stat count: `{summary['ambiguous_mapping_stat_count']}`",
        f"- Ambiguous mapping modifier count: `{summary['ambiguous_mapping_modifier_count']}`",
        f"- Candidate-needs-evidence stat count: `{summary['candidate_needs_evidence_stat_count']}`",
        f"- Candidate-needs-evidence modifier count: `{summary['candidate_needs_evidence_modifier_count']}`",
        "",
        "## Candidate Status Distribution",
        "",
    ]
    lines.extend(
        f"- `{status}`: `{count}`"
        for status, count in report["candidate_status_distribution"].items()
    )
    lines.extend(
        [
            "",
            "## Ranking Criteria",
            "",
            *[f"- {item}" for item in report["conservative_ranking_criteria"]],
            "",
            "## Recommended Future Pilot Candidates",
            "",
            "| Candidate | Domain | Modifiers | Status | Blocking Reasons |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for item in report["recommended_pilot_candidates"][:10]:
        lines.append(
            f"| `{item['canonical_stat_id']}` | `{item['domain']}` | `{item['modifier_row_count']}` | "
            f"`{item['candidate_status']}` | `{', '.join(item['blocking_reasons'])}` |"
        )
    lines.extend(
        [
            "",
            "## Explicit Exclusions And Blockers",
            "",
            "| Candidate | Status | Reason |",
            "| --- | --- | --- |",
        ]
    )
    for item in report["explicitly_excluded_candidates"][:12]:
        lines.append(
            f"| `{item['canonical_stat_id']}` | `{item['candidate_status']}` | `{', '.join(item['blocking_reasons'])}` |"
        )
    lines.extend(
        [
            "",
            "## Evidence Gaps",
            "",
            *[f"- {item}" for item in REQUIRED_EVIDENCE],
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
    report = build_v3_canonical_stat_candidate_inventory_report()
    OUTPUT_JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD_PATH.write_text(_render_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    report = write_report()
    print(
        json.dumps(
            {
                "total_stat_registry_entries": report["summary"]["total_stat_registry_entries"],
                "total_modifier_rows": report["summary"]["total_modifier_rows"],
                "unresolved_stat_identity_count": report["summary"]["unresolved_stat_identity_count"],
                "recommended_pilot_candidate_count": report["summary"]["recommended_pilot_candidate_count"],
                "candidate_status_distribution": report["candidate_status_distribution"],
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
