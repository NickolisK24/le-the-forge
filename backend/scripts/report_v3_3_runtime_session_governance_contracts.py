"""Generate the v3.3 runtime session governance contracts report."""

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

from app.runtime_intelligence.session_governance_contracts import default_runtime_session_governance_contracts  # noqa: E402
from app.runtime_intelligence.session_governance_hashing import hash_session_governance_manifest  # noqa: E402
from app.runtime_intelligence.session_governance_registry import export_session_governance_registry  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_session_governance_contracts_report() -> dict[str, Any]:
    contracts = default_runtime_session_governance_contracts()
    manifest = export_session_governance_registry(contracts)
    repeated = export_session_governance_registry(deepcopy(contracts))
    rows = manifest["session_contracts"]
    validation = manifest["registry_validation"]
    duplicate_detection = validation["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_session_governance_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_11_runtime_session_governance_contracts",
        "recommendation": "RUNTIME_SESSION_GOVERNANCE_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_session_governance_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "live_session_execution_enabled": False,
        "live_drift_detection_enabled": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "summary": {
            "total_session_governance_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "production_authorized_session_governance_count": sum(1 for row in rows if row["production_authorized"]),
            "session_id_required_contract_count": sum(1 for row in rows if row["requires_session_id"]),
            "input_manifest_hash_required_contract_count": sum(1 for row in rows if row["requires_input_manifest_hash"]),
            "lineage_hash_required_contract_count": sum(1 for row in rows if row["requires_lineage_hash"]),
            "replay_scope_required_contract_count": sum(1 for row in rows if row["requires_replay_scope"]),
            "drift_scope_required_contract_count": sum(1 for row in rows if row["requires_drift_scope"]),
            "rollback_path_required_contract_count": sum(1 for row in rows if row["requires_rollback_path"]),
            "invalidation_rule_required_contract_count": sum(1 for row in rows if row["requires_invalidation_rule"]),
            "session_isolating_contract_count": sum(1 for row in rows if row["isolates_session_state"]),
            "cross_session_mutation_blocking_contract_count": sum(1 for row in rows if row["blocks_cross_session_mutation"]),
            "invalidated_session_reuse_blocking_contract_count": sum(1 for row in rows if row["blocks_invalidated_session_reuse"]),
            "production_authorization_blocking_contract_count": sum(1 for row in rows if row["blocks_production_authorization"]),
            "rollback_visible_contract_count": sum(1 for row in rows if row["rollback_visible"]),
            "invalidation_visible_contract_count": sum(1 for row in rows if row["invalidation_visible"]),
            "drift_visible_contract_count": sum(1 for row in rows if row["drift_visible"]),
            "replay_mismatch_visible_contract_count": sum(1 for row in rows if row["replay_mismatch_visible"]),
            "boundary_visible_contract_count": sum(1 for row in rows if row["boundary_visible"]),
            "invalid_classification_reference_count": validation["invalid_classification_reference_count"],
            "invalid_evidence_reference_count": validation["invalid_evidence_reference_count"],
            "invalid_provenance_reference_count": validation["invalid_provenance_reference_count"],
            "invalid_reasoning_stage_reference_count": validation["invalid_reasoning_stage_reference_count"],
            "invalid_explanation_reference_count": validation["invalid_explanation_reference_count"],
            "invalid_confidence_reference_count": validation["invalid_confidence_reference_count"],
            "invalid_synthesis_reference_count": validation["invalid_synthesis_reference_count"],
            "invalid_boundary_reference_count": validation["invalid_boundary_reference_count"],
            "invalid_replay_reference_count": validation["invalid_replay_reference_count"],
            "invalid_drift_reference_count": validation["invalid_drift_reference_count"],
            "invalid_previous_session_reference_count": validation["invalid_previous_session_reference_count"],
            "previous_session_rank_violation_count": validation["previous_session_rank_violation_count"],
            "behavior_rule_violation_count": validation["behavior_rule_violation_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "session_governance_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["session_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_session_governance_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "required_previous_session_validation": {"passed": validation["invalid_previous_session_reference_count"] == 0, "invalid_previous_session_references": validation["invalid_previous_session_references"]},
        "previous_session_rank_validation": {"passed": validation["previous_session_rank_violation_count"] == 0, "previous_session_rank_violations": validation["previous_session_rank_violations"]},
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
            "drift": validation["invalid_drift_reference_count"] == 0,
        },
        "contracts_with_explicit_limitations": {row["session_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]},
        "contracts_with_explicit_risks": {row["session_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]},
        "safety_confirmations": {
            "runtime_session_governance_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_session_governance_contract_is_production_authorized": True,
            "live_session_execution_enabled": False,
            "live_drift_detection_enabled": False,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "active_runtime_reasoning_decisions_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_session_governance_contracts_report",
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
    rows = report["session_governance_manifest"]["session_contracts"]
    lines = [
        "# V3.3 Runtime Session Governance Contracts",
        "",
        "Phase 11 establishes deterministic runtime session governance contracts for planning-only runtime intelligence governance.",
        "",
        "## Boundaries",
        "",
        "Runtime session governance remains planning-only. Live session execution, drift detection, replay execution, synthesis execution, decision routing, active reasoning decisions, recommendation logic, production runtime routing, default manifest consumption, and production-authoritative manifest treatment remain disabled or prohibited.",
        "",
        "## Summary",
        "",
        f"- Total session contracts: `{summary['total_session_governance_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Invalid previous session references: `{summary['invalid_previous_session_reference_count']}`",
        f"- Previous session rank violations: `{summary['previous_session_rank_violation_count']}`",
        f"- Behavior-rule violations: `{summary['behavior_rule_violation_count']}`",
        f"- Production-authorized session contracts: `{summary['production_authorized_session_governance_count']}`",
        "",
        "## Session Contracts",
        "",
        "| Rank | Session | Session ID | Input Hash | Lineage | Replay Scope | Drift Scope | Rollback | Invalidation | Isolated | Blocks Production |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['session_label']}` | `{str(row['requires_session_id']).lower()}` | `{str(row['requires_input_manifest_hash']).lower()}` | `{str(row['requires_lineage_hash']).lower()}` | `{str(row['requires_replay_scope']).lower()}` | `{str(row['requires_drift_scope']).lower()}` | `{str(row['requires_rollback_path']).lower()}` | `{str(row['requires_invalidation_rule']).lower()}` | `{str(row['isolates_session_state']).lower()}` | `{str(row['blocks_production_authorization']).lower()}` |")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime session governance. They do not authorize production enablement, runtime consumption, live session execution, drift detection, replay execution, synthesis execution, decision routing, active reasoning decisions, recommendation logic, or autonomous planner mutation."])
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
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_session_governance_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_SESSION_GOVERNANCE_CONTRACTS.md")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_session_governance_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
