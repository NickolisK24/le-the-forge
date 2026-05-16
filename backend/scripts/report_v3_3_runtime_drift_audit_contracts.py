"""Generate the v3.3 runtime drift audit contracts report."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.drift_audit_contracts import default_runtime_drift_audit_contracts  # noqa: E402
from app.runtime_intelligence.drift_audit_hashing import hash_drift_audit_manifest  # noqa: E402
from app.runtime_intelligence.drift_audit_registry import export_drift_audit_registry  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_drift_audit_contracts_report() -> dict[str, Any]:
    contracts = default_runtime_drift_audit_contracts()
    manifest = export_drift_audit_registry(contracts)
    repeated = export_drift_audit_registry(deepcopy(contracts))
    rows = manifest["drift_contracts"]
    validation = manifest["registry_validation"]
    duplicate_detection = validation["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_drift_audit_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_10_runtime_drift_audit_contracts",
        "recommendation": "RUNTIME_DRIFT_AUDIT_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_drift_audit_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "live_drift_detection_enabled": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "summary": {
            "total_drift_audit_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "production_authorized_drift_audit_count": sum(1 for row in rows if row["production_authorized"]),
            "invalid_drift_category_count": validation["invalid_drift_category_count"],
            "invalid_drift_action_count": validation["invalid_drift_action_count"],
            "baseline_hash_required_drift_count": sum(1 for row in rows if row["requires_baseline_hash"]),
            "current_hash_required_drift_count": sum(1 for row in rows if row["requires_current_hash"]),
            "diff_summary_required_drift_count": sum(1 for row in rows if row["requires_diff_summary"]),
            "replay_validation_required_drift_count": sum(1 for row in rows if row["requires_replay_validation"]),
            "manual_review_required_drift_count": sum(1 for row in rows if row["requires_manual_review"]),
            "confidence_upgrade_blocking_drift_count": sum(1 for row in rows if row["blocks_confidence_upgrade"]),
            "production_authorization_blocking_drift_count": sum(1 for row in rows if row["blocks_production_authorization"]),
            "drift_preserving_audit_count": sum(1 for row in rows if row["preserves_drift"]),
            "conflict_preserving_audit_count": sum(1 for row in rows if row["preserves_conflicts"]),
            "unsupported_preserving_audit_count": sum(1 for row in rows if row["preserves_unsupported"]),
            "blocker_preserving_audit_count": sum(1 for row in rows if row["preserves_blockers"]),
            "boundary_visible_audit_count": sum(1 for row in rows if row["boundary_visible"]),
            "replay_mismatch_visible_audit_count": sum(1 for row in rows if row["replay_mismatch_visible"]),
            "invalid_classification_reference_count": validation["invalid_classification_reference_count"],
            "invalid_evidence_reference_count": validation["invalid_evidence_reference_count"],
            "invalid_provenance_reference_count": validation["invalid_provenance_reference_count"],
            "invalid_reasoning_stage_reference_count": validation["invalid_reasoning_stage_reference_count"],
            "invalid_explanation_reference_count": validation["invalid_explanation_reference_count"],
            "invalid_confidence_reference_count": validation["invalid_confidence_reference_count"],
            "invalid_synthesis_reference_count": validation["invalid_synthesis_reference_count"],
            "invalid_boundary_reference_count": validation["invalid_boundary_reference_count"],
            "invalid_replay_reference_count": validation["invalid_replay_reference_count"],
            "behavior_rule_violation_count": validation["behavior_rule_violation_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "drift_audit_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["drift_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_drift_audit_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "drift_category_validation": {"passed": validation["invalid_drift_category_count"] == 0, "invalid_drift_categories": validation["invalid_drift_categories"]},
        "drift_action_validation": {"passed": validation["invalid_drift_action_count"] == 0, "invalid_drift_actions": validation["invalid_drift_actions"]},
        "behavior_rule_validation": {"passed": validation["behavior_rule_violation_count"] == 0, "behavior_rule_violations": validation["behavior_rule_violations"]},
        "compatibility_validation": {
            "classification": validation["invalid_classification_reference_count"] == 0,
            "evidence": validation["invalid_evidence_reference_count"] == 0,
            "provenance": validation["invalid_provenance_reference_count"] == 0,
            "reasoning": validation["invalid_reasoning_stage_reference_count"] == 0,
            "explanation": validation["invalid_explanation_reference_count"] == 0,
            "confidence": validation["invalid_confidence_reference_count"] == 0,
            "synthesis": validation["invalid_synthesis_reference_count"] == 0,
            "boundary": validation["invalid_boundary_reference_count"] == 0,
            "replay": validation["invalid_replay_reference_count"] == 0,
        },
        "contracts_with_explicit_limitations": {row["drift_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]},
        "contracts_with_explicit_risks": {row["drift_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]},
        "safety_confirmations": {
            "runtime_drift_audit_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_drift_audit_contract_is_production_authorized": True,
            "live_drift_detection_enabled": False,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "active_runtime_reasoning_decisions_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_drift_audit_contracts_report",
            "governance_only": True,
            "runtime_behavior_enabled": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    rows = report["drift_audit_manifest"]["drift_contracts"]
    lines = [
        "# V3.3 Runtime Drift Audit Contracts",
        "",
        "Phase 10 establishes deterministic runtime drift audit contracts for planning-only runtime intelligence governance.",
        "",
        "## Boundaries",
        "",
        "Runtime drift audit remains planning-only. Live drift detection, live replay execution, live synthesis execution, live decision routing, active reasoning decisions, recommendation logic, production runtime routing, default manifest consumption, and production-authoritative manifest treatment remain disabled or prohibited.",
        "",
        "## Summary",
        "",
        f"- Total drift audit contracts: `{summary['total_drift_audit_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Invalid drift categories: `{summary['invalid_drift_category_count']}`",
        f"- Invalid drift actions: `{summary['invalid_drift_action_count']}`",
        f"- Behavior-rule violations: `{summary['behavior_rule_violation_count']}`",
        f"- Production-authorized drift audits: `{summary['production_authorized_drift_audit_count']}`",
        "",
        "## Drift Contracts",
        "",
        "| Rank | Drift | Category | Action | Baseline Hash | Current Hash | Diff | Replay | Manual Review | Blocks Confidence | Blocks Production |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['drift_label']}` | `{row['drift_category']}` | `{row['drift_action']}` | `{str(row['requires_baseline_hash']).lower()}` | `{str(row['requires_current_hash']).lower()}` | `{str(row['requires_diff_summary']).lower()}` | `{str(row['requires_replay_validation']).lower()}` | `{str(row['requires_manual_review']).lower()}` | `{str(row['blocks_confidence_upgrade']).lower()}` | `{str(row['blocks_production_authorization']).lower()}` |")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime drift audit governance. They do not authorize production enablement, runtime consumption, live drift detection, replay execution, synthesis execution, decision routing, active reasoning decisions, recommendation logic, or autonomous planner mutation."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _deterministic_ordering_valid(rows: list[dict[str, Any]]) -> bool:
    return [row["deterministic_rank"] for row in rows] == sorted(row["deterministic_rank"] for row in rows)


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_drift_audit_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_DRIFT_AUDIT_CONTRACTS.md")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_drift_audit_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
