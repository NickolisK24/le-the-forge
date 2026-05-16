"""Generate the v3.3 runtime replay orchestration contracts report."""

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

from app.runtime_intelligence.replay_orchestration_contracts import default_runtime_replay_orchestration_contracts  # noqa: E402
from app.runtime_intelligence.replay_orchestration_hashing import hash_replay_orchestration_manifest  # noqa: E402
from app.runtime_intelligence.replay_orchestration_registry import export_replay_orchestration_registry  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_replay_orchestration_contracts_report() -> dict[str, Any]:
    contracts = default_runtime_replay_orchestration_contracts()
    manifest = export_replay_orchestration_registry(contracts)
    repeated = export_replay_orchestration_registry(deepcopy(contracts))
    rows = manifest["replay_contracts"]
    validation = manifest["registry_validation"]
    duplicate_detection = validation["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_replay_orchestration_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_9_runtime_replay_orchestration_contracts",
        "recommendation": "RUNTIME_REPLAY_ORCHESTRATION_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_replay_orchestration_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "summary": {
            "total_replay_orchestration_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "production_authorized_replay_orchestration_count": sum(1 for row in rows if row["production_authorized"]),
            "input_hash_required_replay_count": sum(1 for row in rows if row["requires_input_hash"]),
            "output_hash_required_replay_count": sum(1 for row in rows if row["requires_output_hash"]),
            "sequence_hash_required_replay_count": sum(1 for row in rows if row["requires_sequence_hash"]),
            "mismatch_visible_replay_count": sum(1 for row in rows if row["mismatch_visible"]),
            "drift_visible_replay_count": sum(1 for row in rows if row["drift_visible"]),
            "conflict_visible_replay_count": sum(1 for row in rows if row["conflict_visible"]),
            "blocker_visible_replay_count": sum(1 for row in rows if row["blocker_visible"]),
            "boundary_visible_replay_count": sum(1 for row in rows if row["boundary_visible"]),
            "reproducibility_required_replay_count": sum(1 for row in rows if row["reproducibility_required"]),
            "invalid_classification_reference_count": validation["invalid_classification_reference_count"],
            "invalid_evidence_reference_count": validation["invalid_evidence_reference_count"],
            "invalid_provenance_reference_count": validation["invalid_provenance_reference_count"],
            "invalid_reasoning_stage_reference_count": validation["invalid_reasoning_stage_reference_count"],
            "invalid_explanation_reference_count": validation["invalid_explanation_reference_count"],
            "invalid_confidence_reference_count": validation["invalid_confidence_reference_count"],
            "invalid_synthesis_reference_count": validation["invalid_synthesis_reference_count"],
            "invalid_boundary_reference_count": validation["invalid_boundary_reference_count"],
            "invalid_previous_replay_reference_count": validation["invalid_previous_replay_reference_count"],
            "previous_replay_rank_violation_count": validation["previous_replay_rank_violation_count"],
            "hash_requirement_violation_count": validation["hash_requirement_violation_count"],
            "visibility_rule_violation_count": validation["visibility_rule_violation_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "replay_orchestration_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["replay_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_replay_orchestration_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "required_previous_replay_validation": {
            "passed": validation["invalid_previous_replay_reference_count"] == 0,
            "invalid_previous_replay_references": validation["invalid_previous_replay_references"],
        },
        "previous_replay_rank_validation": {
            "passed": validation["previous_replay_rank_violation_count"] == 0,
            "previous_replay_rank_violations": validation["previous_replay_rank_violations"],
        },
        "hash_requirement_validation": {
            "passed": validation["hash_requirement_violation_count"] == 0,
            "hash_requirement_violations": validation["hash_requirement_violations"],
        },
        "visibility_rule_validation": {
            "passed": validation["visibility_rule_violation_count"] == 0,
            "visibility_rule_violations": validation["visibility_rule_violations"],
        },
        "compatibility_validation": {
            "classification": validation["invalid_classification_reference_count"] == 0,
            "evidence": validation["invalid_evidence_reference_count"] == 0,
            "provenance": validation["invalid_provenance_reference_count"] == 0,
            "reasoning": validation["invalid_reasoning_stage_reference_count"] == 0,
            "explanation": validation["invalid_explanation_reference_count"] == 0,
            "confidence": validation["invalid_confidence_reference_count"] == 0,
            "synthesis": validation["invalid_synthesis_reference_count"] == 0,
            "boundary": validation["invalid_boundary_reference_count"] == 0,
        },
        "contracts_with_explicit_limitations": {row["replay_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]},
        "contracts_with_explicit_risks": {row["replay_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]},
        "safety_confirmations": {
            "runtime_replay_orchestration_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_replay_orchestration_contract_is_production_authorized": True,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "active_runtime_reasoning_decisions_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_replay_orchestration_contracts_report",
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
    rows = report["replay_orchestration_manifest"]["replay_contracts"]
    lines = [
        "# V3.3 Runtime Replay Orchestration Contracts",
        "",
        "Phase 9 establishes deterministic runtime replay orchestration contracts for planning-only runtime intelligence governance.",
        "",
        "## Boundaries",
        "",
        "Runtime replay orchestration remains planning-only. Live replay execution, live synthesis execution, live decision routing, active reasoning decisions, recommendation logic, production runtime routing, default manifest consumption, and production-authoritative manifest treatment remain disabled or prohibited.",
        "",
        "## Summary",
        "",
        f"- Total replay contracts: `{summary['total_replay_orchestration_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Duplicate detection passed: `{str(summary['duplicate_detection_passed']).lower()}`",
        f"- Invalid previous replay references: `{summary['invalid_previous_replay_reference_count']}`",
        f"- Previous replay rank violations: `{summary['previous_replay_rank_violation_count']}`",
        f"- Hash requirement violations: `{summary['hash_requirement_violation_count']}`",
        f"- Visibility rule violations: `{summary['visibility_rule_violation_count']}`",
        f"- Production-authorized replay contracts: `{summary['production_authorized_replay_orchestration_count']}`",
        "",
        "## Replay Contracts",
        "",
        "| Rank | Replay | Input Hash | Output Hash | Sequence Hash | Mismatch | Boundary | Reproducible |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['replay_label']}` | `{str(row['requires_input_hash']).lower()}` | `{str(row['requires_output_hash']).lower()}` | `{str(row['requires_sequence_hash']).lower()}` | `{str(row['mismatch_visible']).lower()}` | `{str(row['boundary_visible']).lower()}` | `{str(row['reproducibility_required']).lower()}` |")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime replay orchestration governance. They do not authorize production enablement, runtime consumption, live replay execution, live synthesis execution, live decision routing, active reasoning decisions, recommendation logic, or autonomous planner mutation."])
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
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_replay_orchestration_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_REPLAY_ORCHESTRATION_CONTRACTS.md")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_replay_orchestration_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
