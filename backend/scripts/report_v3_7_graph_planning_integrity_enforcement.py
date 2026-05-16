"""Generate the v3.7 graph planning integrity enforcement report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.classification_hashing import deterministic_hash  # noqa: E402
from app.runtime_orchestration.v3_7_graph_integrity_audit import (  # noqa: E402
    V37_GRAPH_INTEGRITY_AUDIT_STABLE,
    audit_v3_7_graph_integrity,
    export_v3_7_graph_integrity_audit_result,
)
from app.runtime_orchestration.v3_7_graph_integrity_enforcement import (  # noqa: E402
    enforce_v3_7_graph_planning_integrity,
)
from app.runtime_orchestration.v3_7_graph_integrity_explainability import (  # noqa: E402
    V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_integrity,
    export_v3_7_graph_integrity_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_integrity_findings import (  # noqa: E402
    count_v3_7_graph_integrity_findings_by_classification,
    export_v3_7_graph_integrity_finding_records,
)
from app.runtime_orchestration.v3_7_graph_integrity_models import (  # noqa: E402
    export_v3_7_graph_integrity_counts,
    export_v3_7_graph_integrity_enforcement_result,
    hash_v3_7_graph_integrity_enforcement_result,
    hash_v3_7_graph_integrity_policy,
    validate_v3_7_graph_integrity_hash_stability,
    validate_v3_7_graph_integrity_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_integrity_provenance import (  # noqa: E402
    V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
    audit_v3_7_graph_integrity_provenance,
    export_v3_7_graph_integrity_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_integrity_replay import (  # noqa: E402
    export_v3_7_graph_integrity_replay_evidence_records,
    validate_v3_7_graph_integrity_replay_evidence,
)
from app.runtime_orchestration.v3_7_graph_integrity_validation import (  # noqa: E402
    V37_GRAPH_INTEGRITY_VALIDATION_STABLE,
    export_v3_7_graph_integrity_validation_result,
    validate_v3_7_graph_integrity,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_planning_integrity_enforcement_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    enforcement = enforce_v3_7_graph_planning_integrity()
    validation = validate_v3_7_graph_integrity((enforcement,))
    audit = audit_v3_7_graph_integrity(enforcement)
    provenance = audit_v3_7_graph_integrity_provenance(enforcement)
    explainability = explain_v3_7_graph_integrity(enforcement)
    replay = validate_v3_7_graph_integrity_replay_evidence(enforcement)
    serialization = validate_v3_7_graph_integrity_serialization_stability(enforcement)
    hashing = validate_v3_7_graph_integrity_hash_stability(enforcement)
    counts = export_v3_7_graph_integrity_counts(enforcement)
    report = {
        "schema_version": "v3_7.graph_planning_integrity_enforcement_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_graph_planning_integrity_enforcement",
        "repo_root": str(root),
        "architectural_purpose": "deterministic graph planning integrity enforcement",
        "integrity_enforcement_is_non_executable": True,
        "integrity_enforcement_validates_planning_evidence_only": True,
        "valid_integrity_does_not_authorize_execution": True,
        "blocked_integrity_does_not_perform_runtime_blocking": True,
        "enforcement_outcomes_are_planning_validation_only": True,
        "integrity_enforcement_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute": True,
        "graph_execution_enabled": False,
        "integrity_driven_execution_enabled": False,
        "orchestration_authorization_enabled": False,
        "routing_enabled": False,
        "scheduling_enabled": False,
        "dispatch_enabled": False,
        "traversal_logic_enabled": False,
        "path_selection_enabled": False,
        "scenario_selection_enabled": False,
        "optimization_engine_enabled": False,
        "recommendation_enabled": False,
        "autonomous_orchestration_enabled": False,
        "runtime_mutation_enabled": False,
        "persistent_runtime_writes_enabled": False,
        "runtime_decision_making_enabled": False,
        "execution_gates_enabled": False,
        "callable_orchestration_flows_enabled": False,
        "runtime_control_system_enabled": False,
        "integrity_policy_counts": {
            "policy_count": counts["integrity_policy_count"],
            "policy_requirement_count": len(enforcement.policy.requirements),
            "execution_boundary_requirement_count": len(enforcement.policy.execution_boundary_requirements),
        },
        "enforcement_result_counts": {
            "enforcement_result_count": counts["enforcement_result_count"],
            "enforcement_outcome": enforcement.enforcement_outcome,
            "evidence_source_count": counts["evidence_source_count"],
        },
        "integrity_finding_totals": {
            "integrity_finding_count": counts["integrity_finding_count"],
            "finding_classification_counts": count_v3_7_graph_integrity_findings_by_classification(enforcement.findings),
        },
        "blocked_finding_totals": {
            "blocked_finding_count": counts["blocked_finding_count"],
            "active_blocking_finding_count": sum(1 for finding in enforcement.findings if finding.blocks_validation),
        },
        "warning_finding_totals": {
            "warning_finding_count": counts["warning_finding_count"],
        },
        "execution_boundary_violation_totals": {
            "execution_boundary_violation_count": validation.execution_boundary_violation_count,
            "execution_boundary_violations_blocked": validation.execution_boundary_violations_blocked,
            "execution_boundary_continuity_preserved": audit.execution_boundary_continuity_preserved,
        },
        "evidence_source_counts": {
            "evidence_source_count": len(enforcement.evidence_source_references),
            "graph_source_count": _source_type_count(enforcement, "graph_foundations"),
            "governance_source_count": _source_type_count(enforcement, "governance"),
            "compatibility_source_count": _source_type_count(enforcement, "compatibility"),
            "evaluation_source_count": _source_type_count(enforcement, "evaluation"),
            "session_source_count": _source_type_count(enforcement, "session"),
            "scenario_source_count": _source_type_count(enforcement, "scenario"),
            "aggregation_source_count": _source_type_count(enforcement, "aggregation"),
        },
        "replay_evidence_counts": {
            "replay_evidence_count": replay["replay_evidence_count"],
            "non_executable_replay_evidence": replay["non_executable_replay_evidence"],
            "runtime_replay": replay["runtime_replay"],
            "execution_authorization": replay["execution_authorization"],
        },
        "rollback_continuity_counts": {
            "rollback_reference_count": replay["rollback_reference_count"],
            "rollback_continuity_preserved": replay["rollback_continuity_preserved"],
        },
        "provenance_continuity_totals": {
            "provenance_status": provenance.provenance_status,
            "provenance_record_count": provenance.provenance_record_count,
            "enforcement_provenance_preserved": provenance.enforcement_provenance_preserved,
            "policy_provenance_preserved": provenance.policy_provenance_preserved,
            "graph_provenance_preserved": provenance.graph_provenance_preserved,
            "governance_provenance_preserved": provenance.governance_provenance_preserved,
            "compatibility_provenance_preserved": provenance.compatibility_provenance_preserved,
            "evaluation_provenance_preserved": provenance.evaluation_provenance_preserved,
            "session_provenance_preserved": provenance.session_provenance_preserved,
            "scenario_provenance_preserved": provenance.scenario_provenance_preserved,
            "aggregation_provenance_preserved": provenance.aggregation_provenance_preserved,
            "replay_provenance_preserved": provenance.replay_provenance_preserved,
            "rollback_provenance_preserved": provenance.rollback_provenance_preserved,
            "explainability_provenance_preserved": provenance.explainability_provenance_preserved,
            "continuity_provenance_preserved": provenance.continuity_provenance_preserved,
        },
        "explainability_continuity_totals": {
            "explainability_status": explainability.explainability_status,
            "explanation_count": explainability.explanation_count,
            "enforcement_explanation_count": explainability.enforcement_explanation_count,
            "policy_explanation_count": explainability.policy_explanation_count,
            "evidence_source_explanation_count": explainability.evidence_source_explanation_count,
            "finding_explanation_count": explainability.finding_explanation_count,
            "warning_explanation_count": explainability.warning_explanation_count,
            "blocked_explanation_count": explainability.blocked_explanation_count,
            "execution_boundary_explanation_count": explainability.execution_boundary_explanation_count,
            "does_not_authorize_explanation_count": explainability.does_not_authorize_explanation_count,
        },
        "validation_totals": {
            "validation_status": validation.validation_status,
            "valid": validation.valid,
            "finding_count": validation.finding_count,
            "error_count": validation.error_count,
            "visibility_finding_count": validation.visibility_finding_count,
            "duplicate_policy_identity_count": validation.duplicate_policy_identity_count,
            "duplicate_enforcement_identity_count": validation.duplicate_enforcement_identity_count,
            "hidden_prohibited_finding_count": validation.hidden_prohibited_finding_count,
            "hidden_unsupported_finding_count": validation.hidden_unsupported_finding_count,
            "hidden_unknown_finding_count": validation.hidden_unknown_finding_count,
            "execution_boundary_violation_count": validation.execution_boundary_violation_count,
            "integrity_enforcement_non_executable": validation.integrity_enforcement_non_executable,
            "valid_integrity_does_not_authorize_execution": validation.valid_integrity_does_not_authorize_execution,
            "execution_boundary_violations_blocked": validation.execution_boundary_violations_blocked,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "policy_hash": hash_v3_7_graph_integrity_policy(enforcement.policy),
            "integrity_hash": hash_v3_7_graph_integrity_enforcement_result(enforcement),
            "validation_hash": validation.deterministic_validation_hash,
            "audit_hash": audit.deterministic_audit_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_GRAPH_INTEGRITY_VALIDATION_STABLE,
            "audit_coverage": audit.audit_status == V37_GRAPH_INTEGRITY_AUDIT_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED,
            "explainability_coverage": explainability.explainability_status == V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE,
            "replay_continuity_coverage": replay["replay_continuity_preserved"],
            "rollback_continuity_coverage": replay["rollback_continuity_preserved"],
            "non_executable_confirmation": validation.integrity_enforcement_non_executable,
            "no_execution_authorization_confirmation": validation.valid_integrity_does_not_authorize_execution,
            "execution_boundary_enforcement_confirmation": validation.execution_boundary_violations_blocked,
        },
        "integrity_enforcement_record": export_v3_7_graph_integrity_enforcement_result(enforcement),
        "finding_records": export_v3_7_graph_integrity_finding_records(enforcement.findings),
        "replay_evidence_records": export_v3_7_graph_integrity_replay_evidence_records(enforcement.replay_evidence),
        "validation_result": export_v3_7_graph_integrity_validation_result(validation),
        "audit_result": export_v3_7_graph_integrity_audit_result(audit),
        "provenance_result": export_v3_7_graph_integrity_provenance_result(provenance),
        "explainability_result": export_v3_7_graph_integrity_explainability_result(explainability),
        "explicit_limitations": [
            "integrity enforcement is non-executable",
            "integrity enforcement validates planning evidence only",
            "valid integrity does not authorize execution",
            "blocked integrity does not perform runtime blocking",
            "enforcement outcomes are planning validation outcomes only",
            "integrity enforcement does not route, schedule, dispatch, traverse, optimize, recommend, or execute",
        ],
        "summary": {
            "enforcement_outcome": enforcement.enforcement_outcome,
            "validation_status": validation.validation_status,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "provenance_continuity_verified": validation.provenance_continuity_preserved,
            "explainability_continuity_verified": validation.explainability_continuity_preserved,
            "replay_continuity_verified": validation.replay_continuity_preserved,
            "rollback_continuity_verified": validation.rollback_continuity_preserved,
            "non_executable_verified": validation.integrity_enforcement_non_executable,
            "no_execution_authorization_verified": validation.valid_integrity_does_not_authorize_execution,
            "execution_boundary_enforcement_verified": validation.execution_boundary_violations_blocked,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.7 Graph Planning Integrity Enforcement",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 Phase 8 adds deterministic graph planning integrity enforcement.",
        "",
        "Integrity enforcement is NON-executable.",
        "",
        "Integrity enforcement validates planning evidence only.",
        "",
        "Valid integrity does NOT authorize execution.",
        "",
        "Blocked integrity does NOT perform runtime blocking.",
        "",
        "Enforcement outcomes are planning validation outcomes only.",
        "",
        "Integrity enforcement does NOT route, schedule, dispatch, traverse, optimize, recommend, or execute.",
        "",
        "Planning integrity enforcement checks deterministic planning evidence. Runtime orchestration control would control runtime behavior. This phase implements planning integrity enforcement only, not runtime orchestration control.",
        "",
        "## Deterministic Scope",
        "",
        f"- Enforcement outcome: `{report['enforcement_result_counts']['enforcement_outcome']}`",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Integrity findings: `{report['integrity_finding_totals']['integrity_finding_count']}`",
        f"- Evidence sources: `{report['evidence_source_counts']['evidence_source_count']}`",
        f"- Execution-boundary violations: `{report['execution_boundary_violation_totals']['execution_boundary_violation_count']}`",
        f"- Serialization stable: `{report['deterministic_guarantees']['serialization_stable']}`",
        f"- Hash stable: `{report['deterministic_guarantees']['hash_stable']}`",
        "",
        "## Explicit Non-Execution Guarantees",
        "",
        "- Graph execution remains disabled.",
        "- Integrity-driven execution remains disabled.",
        "- Orchestration authorization remains disabled.",
        "- Routing remains disabled.",
        "- Scheduling remains disabled.",
        "- Dispatch remains disabled.",
        "- Traversal remains disabled.",
        "- Runtime path selection remains disabled.",
        "- Scenario execution selection remains disabled.",
        "- Optimization for execution remains disabled.",
        "- Recommendation to execute remains disabled.",
        "- Callable execution flow references remain prohibited.",
        "",
        "## Planning Integrity Enforcement vs Runtime Orchestration Control",
        "",
        "Planning integrity enforcement validates deterministic evidence continuity, provenance, explainability, replay, rollback, and execution-boundary preservation.",
        "",
        "Runtime orchestration control would authorize or direct runtime behavior. This phase does not implement runtime orchestration control.",
        "",
        "## Generated Evidence",
        "",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        f"- Integrity hash: `{report['deterministic_guarantees']['integrity_hash']}`",
        f"- Policy hash: `{report['deterministic_guarantees']['policy_hash']}`",
        f"- Validation hash: `{report['deterministic_guarantees']['validation_hash']}`",
        f"- Audit hash: `{report['deterministic_guarantees']['audit_hash']}`",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _source_type_count(enforcement, source_type: str) -> int:
    return sum(1 for item in enforcement.evidence_source_types if item == source_type)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "docs" / "generated" / "v3_7_graph_planning_integrity_enforcement_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "docs" / "migration" / "V3_7_GRAPH_PLANNING_INTEGRITY_ENFORCEMENT.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_7_graph_planning_integrity_enforcement_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
