"""Generate the v3 mechanical intelligence planning and scope audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ALLOWED_CLASSIFICATIONS = frozenset(
    {
        "ready_for_policy_design",
        "blocked_by_value_normalization",
        "blocked_by_operation_semantics",
        "blocked_by_stat_identity",
        "blocked_by_skill_identity",
        "blocked_by_unsupported_mechanics",
        "blocked_by_missing_golden_baseline",
        "blocked_by_behavioral_risk",
        "blocked_by_schema_gap",
        "future_patch_resilience_followup",
        "unknown_needs_review",
    }
)

MECHANICAL_DOMAINS: tuple[dict[str, Any], ...] = (
    {
        "id": "value_normalization",
        "description": "Define source-unit and unknown value scale contracts before any planner math uses v2 values.",
        "classification": "ready_for_policy_design",
        "severity": "critical",
        "depends_on": [],
    },
    {
        "id": "operation_semantics",
        "description": "Define flat, increased, more, less, chance, duration, cooldown, cost, conditional, and unknown operation semantics.",
        "classification": "blocked_by_value_normalization",
        "severity": "critical",
        "depends_on": ["value_normalization"],
    },
    {
        "id": "stat_identity_resolution",
        "description": "Resolve canonical stat identities for target domains before stable stat aggregation.",
        "classification": "ready_for_policy_design",
        "severity": "critical",
        "depends_on": [],
    },
    {
        "id": "modifier_application_semantics",
        "description": "Define deterministic modifier application order, stacking, scope, and exclusion behavior.",
        "classification": "blocked_by_operation_semantics",
        "severity": "critical",
        "depends_on": ["value_normalization", "operation_semantics", "stat_identity_resolution"],
    },
    {
        "id": "item_affix_stat_output",
        "description": "Compare item base, implicit, and affix stat output against current planner behavior.",
        "classification": "blocked_by_missing_golden_baseline",
        "severity": "high",
        "depends_on": ["value_normalization", "operation_semantics", "stat_identity_resolution", "golden_mechanical_baselines"],
    },
    {
        "id": "passive_node_stat_output",
        "description": "Compare passive node effects only after unsupported/scripted behavior and baselines are explicit.",
        "classification": "blocked_by_unsupported_mechanics",
        "severity": "high",
        "depends_on": ["operation_semantics", "golden_mechanical_baselines", "unsupported_mechanic_policy"],
    },
    {
        "id": "skill_node_stat_output",
        "description": "Compare skill node effects only after skill identity and unsupported behavior policies are approved.",
        "classification": "blocked_by_skill_identity",
        "severity": "high",
        "depends_on": ["skill_identity_bridge_policy", "operation_semantics", "golden_mechanical_baselines"],
    },
    {
        "id": "unique_set_unsupported_behavior_exclusions",
        "description": "Keep unique/set scripted and text-only mechanics explicitly excluded unless future policy proves support.",
        "classification": "blocked_by_unsupported_mechanics",
        "severity": "high",
        "depends_on": ["unsupported_mechanic_policy"],
    },
    {
        "id": "idol_mechanic_treatment",
        "description": "Classify idol affix mechanics through the same value, operation, identity, and baseline gates.",
        "classification": "blocked_by_value_normalization",
        "severity": "medium",
        "depends_on": ["value_normalization", "operation_semantics", "stat_identity_resolution"],
    },
    {
        "id": "skill_identity_bridge_policy",
        "description": "Define when source evidence is sufficient to bridge skill identities without guessing.",
        "classification": "ready_for_policy_design",
        "severity": "critical",
        "depends_on": [],
    },
    {
        "id": "deterministic_stat_resolution_adapter",
        "description": "Design a deterministic adapter that can explain every accepted and blocked stat effect.",
        "classification": "blocked_by_missing_golden_baseline",
        "severity": "critical",
        "depends_on": ["value_normalization", "operation_semantics", "stat_identity_resolution", "golden_mechanical_baselines"],
    },
    {
        "id": "experimental_mechanical_dry_run_comparison",
        "description": "Compare old planner output with v3 candidate output without changing production behavior.",
        "classification": "blocked_by_missing_golden_baseline",
        "severity": "critical",
        "depends_on": ["deterministic_stat_resolution_adapter", "golden_mechanical_baselines"],
    },
    {
        "id": "production_planner_remap_gates",
        "description": "Audit all gates before any approved production planner remap.",
        "classification": "blocked_by_behavioral_risk",
        "severity": "critical",
        "depends_on": ["experimental_mechanical_dry_run_comparison"],
    },
)

V3_PHASE_SEQUENCE: tuple[dict[str, Any], ...] = (
    {"order": 1, "id": "v3_value_normalization_contract_design", "description": "Design value normalization contracts and source-unit policy."},
    {"order": 2, "id": "v3_operation_semantics_taxonomy", "description": "Define operation taxonomy and unsupported operation handling."},
    {"order": 3, "id": "v3_stat_identity_resolution_policy", "description": "Define stat identity resolution policy and target-domain scope."},
    {"order": 4, "id": "v3_skill_identity_bridge_policy", "description": "Define evidence requirements for skill identity bridges."},
    {"order": 5, "id": "v3_golden_mechanical_baseline_creation", "description": "Create existing-production golden baselines before mechanical changes."},
    {"order": 6, "id": "v3_deterministic_stat_resolution_adapter_design", "description": "Design deterministic adapter behavior and explanations."},
    {"order": 7, "id": "v3_experimental_mechanical_dry_run_mode", "description": "Add opt-in dry-run comparison without changing production output."},
    {"order": 8, "id": "v3_item_affix_mechanical_comparison", "description": "Compare item and affix mechanical output under approved gates."},
    {"order": 9, "id": "v3_passive_skill_mechanical_comparison", "description": "Compare passive and skill output under approved identity and unsupported policies."},
    {"order": 10, "id": "v3_limited_opt_in_mechanical_adapter_mode", "description": "Expose limited opt-in mechanical adapter mode after dry-run evidence."},
    {"order": 11, "id": "v3_production_planner_remap_gate_audit", "description": "Audit production remap gates and rollback/debug path."},
    {"order": 12, "id": "v3_production_remap_after_stable_gates", "description": "Production remap only after all stable-calculable gates pass."},
)

PRODUCTION_REMAP_GATES = (
    "stable-calculable count greater than zero only through proven policy",
    "value normalization contracts approved",
    "operation semantics approved",
    "stat identities resolved for target domain",
    "skill identity bridge policy approved",
    "unsupported/scripted mechanics excluded",
    "golden baselines passing",
    "old planner versus v3 dry-run comparison passing",
    "production non-consumption guard intentionally updated only when remap is approved",
    "rollback and debug path exists",
)


def build_v3_mechanical_intelligence_plan(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    reports = _load_source_reports(repo_root)
    v2_release = reports["v2_release_readiness"]
    v2_5_release = reports["v2_5_release_readiness"]
    dry_run = reports["stat_modifier_dry_run"]
    baselines = reports["golden_baseline_plan"]
    passive_skill = reports["passive_skill_identity"]

    safety = _safety_status(v2_release=v2_release, v2_5_release=v2_5_release, dry_run=dry_run, baselines=baselines)
    readiness = {
        "v3_planning_ready": bool(
            v2_release.get("readiness_decision", {}).get("v2_infrastructure_ready") is True
            and v2_5_release.get("readiness_decision", {}).get("v2_5_trust_ux_ready") is True
            and safety["production_consumed"] is False
        ),
        "v3_mechanical_implementation_ready": False,
        "production_planner_remap_ready": False,
        "recommended_next_phase": "v3_value_normalization_contract_design",
    }

    return {
        "schema_version": "v3.mechanical_intelligence_plan.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "readiness_decision": readiness,
        "current_readiness_status": {
            "v2": v2_release.get("readiness_decision", {}),
            "v2_5": v2_5_release.get("readiness_decision", {}),
            "safety": safety,
        },
        "mechanical_blocker_summary": _mechanical_blocker_summary(dry_run=dry_run, baselines=baselines, passive_skill=passive_skill),
        "mechanical_domains": [dict(domain) for domain in MECHANICAL_DOMAINS],
        "classification_counts": _classification_counts(MECHANICAL_DOMAINS),
        "required_policy_decisions": _required_policy_decisions(),
        "required_golden_baselines": _required_golden_baselines(baselines),
        "required_dry_run_comparison_layers": _required_dry_run_layers(),
        "required_adapter_gates": _required_adapter_gates(),
        "systems_that_must_remain_blocked": _systems_that_must_remain_blocked(),
        "recommended_v3_phase_sequence": [dict(step) for step in V3_PHASE_SEQUENCE],
        "production_remap_gate_requirements": list(PRODUCTION_REMAP_GATES),
        "production_remap_readiness": {
            "ready": False,
            "blocked_by": [
                "stable_calculable_count_zero",
                "value_normalization_audit_only",
                "unknown_value_scales",
                "source_units_value_scales",
                "unknown_operations",
                "unresolved_stat_identities",
                "unbridged_skill_identities",
                "missing_mechanical_golden_baselines",
                "missing_dry_run_parity",
            ],
        },
        "source_report_evidence": {
            "stat_registry_count": dry_run.get("summary", {}).get("stat_registry_count"),
            "modifier_row_count": dry_run.get("summary", {}).get("modifier_row_count"),
            "blocked_modifier_count": dry_run.get("summary", {}).get("blocked_modifier_count"),
            "source_unit_value_scale_count": dry_run.get("summary", {}).get("source_unit_value_scale_count"),
            "unknown_value_scale_count": dry_run.get("summary", {}).get("unknown_value_scale_count"),
            "operation_distribution": dry_run.get("operation_distribution", {}),
            "stat_identity_findings": dry_run.get("stat_identity_findings", {}),
            "skill_identity_audit": passive_skill.get("skill_identity_audit_summary", {}),
            "golden_baseline_summary": baselines.get("summary", {}),
        },
        "safety_confirmations": safety,
        "metadata": {
            "source": "v3_mechanical_intelligence_plan",
            "planning_only": True,
            "runtime_behavior_changed": False,
            "production_consumed": False,
            "planner_remap_performed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    decision = report["readiness_decision"]
    safety = report["safety_confirmations"]
    lines = [
        "# V3 Mechanical Intelligence Plan",
        "",
        "This audit defines the v3 scope and order of work. It is planning-only.",
        "It does not implement mechanics, normalize values, bridge skill identities, or change planner output.",
        "",
        "## Readiness Decision",
        "",
        f"- V3 planning ready: `{str(decision['v3_planning_ready']).lower()}`",
        f"- V3 mechanical implementation ready: `{str(decision['v3_mechanical_implementation_ready']).lower()}`",
        f"- Production planner remap ready: `{str(decision['production_planner_remap_ready']).lower()}`",
        f"- Recommended next phase: `{decision['recommended_next_phase']}`",
        "",
        "## Scope",
        "",
        "V3 should deliver deterministic, explainable mechanical intelligence only after policy, identity, value, operation, baseline, and dry-run gates are satisfied.",
        "",
        "## Non-Goals",
        "",
        "- Do not implement value normalization in this phase.",
        "- Do not implement stat or modifier calculations in this phase.",
        "- Do not wire v2 data into production planner math.",
        "- Do not infer tooltip mechanics.",
        "- Do not bridge unresolved skill identities.",
        "- Do not promote records to stable-calculable.",
        "",
        "## Mechanical Domains",
        "",
        "| Domain | Classification | Severity |",
        "| --- | --- | --- |",
    ]
    for domain in report["mechanical_domains"]:
        lines.append(f"| `{domain['id']}` | `{domain['classification']}` | `{domain['severity']}` |")
    lines.extend(["", "## Ordered Phase Sequence", "", "| Order | Phase | Description |", "| ---: | --- | --- |"])
    for step in report["recommended_v3_phase_sequence"]:
        lines.append(f"| `{step['order']}` | `{step['id']}` | {step['description']} |")
    lines.extend(["", "## Production Remap Gates", ""])
    lines.extend(f"- {gate}" for gate in report["production_remap_gate_requirements"])
    lines.extend(["", "## Required Golden Baseline Strategy", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["required_golden_baselines"])
    lines.extend(["", "## Known Risks", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["systems_that_must_remain_blocked"])
    lines.extend(
        [
            "",
            "## Safety State",
            "",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Planner-calculable count: `{safety['planner_calculable_count']}`",
            f"- Stable-calculable count: `{safety['stable_calculable_count']}`",
            f"- Value normalization: `{safety['value_normalization_status']}`",
            f"- Skill identity bridge: `{safety['skill_identity_bridge_status']}`",
            f"- Runtime behavior changed: `{str(safety['runtime_behavior_changed']).lower()}`",
            "",
            "## Recommended Next Phase",
            "",
            "`v3_value_normalization_contract_design` should define value families, source-unit handling, unknown value policy, approval criteria, and fixtures without changing production planner behavior.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_source_reports(repo_root: Path) -> dict[str, dict[str, Any]]:
    generated = repo_root / "docs" / "generated"
    return {
        "v2_release_readiness": _read_json(generated / "v2_release_readiness_report.json"),
        "v2_5_release_readiness": _read_json(generated / "v2_5_release_readiness_report.json"),
        "stat_modifier_dry_run": _read_json(generated / "v2_stat_modifier_dry_run_report.json"),
        "golden_baseline_plan": _read_json(generated / "v2_golden_baseline_plan.json"),
        "planner_adapter": _read_json(generated / "v2_planner_adapter_report.json"),
        "planner_adapter_diagnostics": _read_json(generated / "v2_planner_adapter_diagnostics_report.json"),
        "planner_remap_readiness": _read_json(generated / "v2_planner_remap_readiness_report.json"),
        "passive_skill_identity": _read_json(generated / "v2_passive_skill_identity_remap_report.json"),
        "affix_display_provenance": _read_json(generated / "v2_affix_display_provenance_report.json"),
        "item_base_display_metadata": _read_json(generated / "v2_item_base_display_metadata_report.json"),
    }


def _mechanical_blocker_summary(*, dry_run: dict[str, Any], baselines: dict[str, Any], passive_skill: dict[str, Any]) -> dict[str, Any]:
    dry_summary = dry_run.get("summary", {})
    baseline_summary = baselines.get("summary", {})
    skill_audit = passive_skill.get("skill_identity_audit_summary", {})
    return {
        "blocked_modifier_count": dry_summary.get("blocked_modifier_count"),
        "top_blocked_reasons": dry_summary.get("top_blocked_reasons", []),
        "value_normalization": {
            "status": dry_summary.get("value_normalization_status"),
            "source_unit_value_scale_count": dry_summary.get("source_unit_value_scale_count"),
            "unknown_value_scale_count": dry_summary.get("unknown_value_scale_count"),
        },
        "operation_semantics": {
            "unknown_operation_count": dry_run.get("operation_distribution", {}).get("unknown"),
            "operation_distribution": dry_run.get("operation_distribution", {}),
        },
        "stat_identity": dry_run.get("stat_identity_findings", {}),
        "skill_identity": skill_audit,
        "golden_baselines": baseline_summary,
    }


def _required_policy_decisions() -> list[dict[str, str]]:
    return [
        {"id": "value_scale_family_policy", "description": "Which source value families may be converted, and with what proof."},
        {"id": "unknown_value_policy", "description": "Unknown value scales remain blocked until source contracts or baselines prove them."},
        {"id": "operation_taxonomy_policy", "description": "Each operation must have deterministic stacking and scope semantics."},
        {"id": "stat_identity_policy", "description": "Target domains need resolved canonical stat identities before aggregation."},
        {"id": "skill_identity_bridge_policy", "description": "Bridges require source-stable evidence; display-name guessing remains disallowed."},
        {"id": "unsupported_mechanic_policy", "description": "Scripted, text-only, and unsupported mechanics remain excluded by default."},
    ]


def _required_golden_baselines(baselines: dict[str, Any]) -> list[dict[str, Any]]:
    categories = baselines.get("baseline_categories", [])
    required_ids = {
        "known_item_affix_stat_output",
        "known_passive_node_stat_output",
        "known_skill_node_stat_output",
        "unique_set_unsupported_exclusions",
        "value_scale_normalization_examples",
        "operation_examples",
        "planner_output_vs_v2_dry_run_snapshots",
    }
    return [
        {
            "id": item.get("category_id"),
            "description": item.get("description"),
            "current_status": item.get("current_status"),
            "required_future_assertions": item.get("required_future_assertions", []),
        }
        for item in categories
        if item.get("category_id") in required_ids
    ]


def _required_dry_run_layers() -> list[dict[str, str]]:
    return [
        {"id": "legacy_output_snapshot_layer", "description": "Capture existing planner output without changing it."},
        {"id": "v3_candidate_output_layer", "description": "Compute candidate output in opt-in dry-run mode only."},
        {"id": "delta_explanation_layer", "description": "Explain every accepted, rejected, and blocked delta."},
        {"id": "domain_gate_layer", "description": "Limit dry-run scope to domains with approved policies and baselines."},
    ]


def _required_adapter_gates() -> list[dict[str, str]]:
    return [
        {"id": "read_only_default", "description": "Adapter remains read-only by default."},
        {"id": "explicit_opt_in", "description": "Mechanical dry-run requires explicit opt-in."},
        {"id": "stable_calculable_policy", "description": "Stable-calculable records require approved value, operation, identity, and baseline evidence."},
        {"id": "production_non_consumption_guard", "description": "Production guard remains false until a deliberate remap approval."},
    ]


def _systems_that_must_remain_blocked() -> list[dict[str, str]]:
    return [
        {"id": "unknown_value_scales", "description": "Unknown values remain blocked from mechanical use."},
        {"id": "source_units_without_contracts", "description": "Source-unit values remain blocked until conversion contracts are approved."},
        {"id": "unknown_operations", "description": "Unknown operations remain blocked."},
        {"id": "unresolved_stat_identities", "description": "Unresolved stat identities remain blocked."},
        {"id": "unresolved_skill_identities", "description": "Unresolved or ambiguous skill identities remain unbridged."},
        {"id": "scripted_text_only_unsupported_mechanics", "description": "Scripted, text-only, and unsupported mechanics remain excluded by default."},
    ]


def _safety_status(*, v2_release: dict[str, Any], v2_5_release: dict[str, Any], dry_run: dict[str, Any], baselines: dict[str, Any]) -> dict[str, Any]:
    dry_summary = dry_run.get("summary", {})
    v2_safety = v2_release.get("safety_confirmations", {})
    v2_5_safety = v2_5_release.get("safety_confirmations", {})
    baseline_summary = baselines.get("summary", {})
    return {
        "v2_infrastructure_ready": bool(v2_release.get("readiness_decision", {}).get("v2_infrastructure_ready") is True),
        "v2_5_trust_ux_ready": bool(v2_5_release.get("readiness_decision", {}).get("v2_5_trust_ux_ready") is True),
        "production_planner_ready": False,
        "mechanical_remap_ready": False,
        "production_consumed": bool(v2_safety.get("production_consumed") is True or v2_5_safety.get("production_consumed") is True),
        "planner_calculable_count": int(dry_summary.get("planner_calculable_modifier_count") or 0),
        "stable_calculable_count": int(dry_summary.get("stable_calculable_modifier_count") or baseline_summary.get("stable_calculable_count") or 0),
        "value_normalization_status": dry_summary.get("value_normalization_status") or "audit_only",
        "skill_identity_bridge_status": dry_summary.get("skill_identity_bridge_status") or baseline_summary.get("skill_identity_bridge_status") or "unbridged",
        "runtime_behavior_changed": False,
        "planner_output_changed": False,
        "crafting_behavior_changed": False,
        "simulation_behavior_changed": False,
        "stat_aggregation_behavior_changed": False,
        "value_normalization_promoted": False,
        "skill_identity_bridge_added": False,
    }


def _classification_counts(items: tuple[dict[str, Any], ...]) -> dict[str, int]:
    return {
        classification: sum(1 for item in items if item["classification"] == classification)
        for classification in sorted(ALLOWED_CLASSIFICATIONS)
        if any(item["classification"] == classification for item in items)
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_mechanical_intelligence_plan.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_MECHANICAL_INTELLIGENCE_PLAN.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_mechanical_intelligence_plan(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["readiness_decision"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
