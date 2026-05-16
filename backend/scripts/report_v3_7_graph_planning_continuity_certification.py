"""Generate the v3.7 graph planning continuity certification report."""

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
from app.runtime_orchestration.v3_7_graph_certification_audit import (  # noqa: E402
    V37_GRAPH_CERTIFICATION_AUDIT_STABLE,
    audit_v3_7_graph_certification,
    export_v3_7_graph_certification_audit_result,
)
from app.runtime_orchestration.v3_7_graph_certification_evidence import (  # noqa: E402
    build_v3_7_graph_planning_continuity_certification,
    count_v3_7_graph_certification_findings_by_classification,
    export_v3_7_graph_certification_finding_records,
)
from app.runtime_orchestration.v3_7_graph_certification_explainability import (  # noqa: E402
    V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_certification,
    export_v3_7_graph_certification_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_certification_models import (  # noqa: E402
    export_v3_7_graph_certification_counts,
    export_v3_7_graph_planning_continuity_certification,
    hash_v3_7_graph_certification_scope,
    hash_v3_7_graph_planning_continuity_certification,
    validate_v3_7_graph_certification_hash_stability,
    validate_v3_7_graph_certification_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_certification_provenance import (  # noqa: E402
    V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_certification_provenance,
    export_v3_7_graph_certification_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_certification_replay import (  # noqa: E402
    export_v3_7_graph_certification_replay_evidence_records,
    validate_v3_7_graph_certification_replay_evidence,
)
from app.runtime_orchestration.v3_7_graph_certification_validation import (  # noqa: E402
    V37_GRAPH_CERTIFICATION_VALIDATION_STABLE,
    export_v3_7_graph_certification_validation_result,
    validate_v3_7_graph_certification,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_planning_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = build_v3_7_graph_planning_continuity_certification()
    validation = validate_v3_7_graph_certification((certification,))
    audit = audit_v3_7_graph_certification(certification)
    provenance = audit_v3_7_graph_certification_provenance(certification)
    explainability = explain_v3_7_graph_certification(certification)
    replay = validate_v3_7_graph_certification_replay_evidence(certification)
    serialization = validate_v3_7_graph_certification_serialization_stability(certification)
    hashing = validate_v3_7_graph_certification_hash_stability(certification)
    counts = export_v3_7_graph_certification_counts(certification)
    report = {
        "schema_version": "v3_7.graph_planning_continuity_certification_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_graph_planning_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "end-to-end graph planning continuity certification",
        "certification_is_non_executable": True,
        "certification_validates_planning_continuity_only": True,
        "certified_continuity_does_not_authorize_execution": True,
        "certification_does_not_mark_runtime_execution_readiness": True,
        "certification_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute": True,
        "graph_execution_enabled": False,
        "certification_driven_execution_enabled": False,
        "orchestration_authorization_enabled": False,
        "execution_readiness_approval_enabled": False,
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
        "executable_certification_gates_enabled": False,
        "runtime_control_system_enabled": False,
        "certification_counts": {
            "certification_count": counts["certification_count"],
            "certification_evidence_count": counts["certification_evidence_count"],
        },
        "certification_scope_counts": {
            "scope_count": counts["scope_count"],
            "scope_reference_count": counts["scope_reference_count"],
            "graph_scope_count": _scope_type_count(certification, "graph_foundations"),
            "governance_scope_count": _scope_type_count(certification, "governance"),
            "compatibility_scope_count": _scope_type_count(certification, "compatibility"),
            "evaluation_scope_count": _scope_type_count(certification, "evaluation"),
            "session_scope_count": _scope_type_count(certification, "session"),
            "scenario_scope_count": _scope_type_count(certification, "scenario"),
            "aggregation_scope_count": _scope_type_count(certification, "aggregation"),
            "integrity_scope_count": _scope_type_count(certification, "integrity"),
        },
        "certification_outcome_counts": {
            "certified": 1 if certification.certification_outcome == "certified" else 0,
            "uncertified": 1 if certification.certification_outcome == "uncertified" else 0,
            "blocked": 1 if certification.certification_outcome == "blocked" else 0,
            "warning": 1 if certification.certification_outcome == "warning" else 0,
            "audit_failed": 1 if certification.certification_outcome == "audit_failed" else 0,
            "certification_outcome": certification.certification_outcome,
        },
        "certification_finding_totals": {
            "finding_count": counts["finding_count"],
            "finding_classification_counts": count_v3_7_graph_certification_findings_by_classification(certification.findings),
        },
        "incomplete_scope_totals": {
            "incomplete_scope_count": validation.incomplete_scope_count,
            "missing_scope_reference_count": validation.missing_scope_reference_count,
        },
        "blocked_certification_totals": {
            "blocked_finding_count": counts["blocked_finding_count"],
            "validation_error_count": validation.error_count,
        },
        "continuity_certification_totals": {
            "deterministic_serialization_stable": validation.deterministic_serialization_stable,
            "deterministic_hash_stable": validation.deterministic_hash_stable,
            "audit_continuity_preserved": audit.certification_scope_continuity_preserved,
        },
        "provenance_certification_totals": {
            "provenance_status": provenance.provenance_status,
            "provenance_record_count": provenance.provenance_record_count,
            "certification_provenance_preserved": provenance.certification_provenance_preserved,
            "scope_provenance_preserved": provenance.scope_provenance_preserved,
            "graph_provenance_preserved": provenance.graph_provenance_preserved,
            "governance_provenance_preserved": provenance.governance_provenance_preserved,
            "compatibility_provenance_preserved": provenance.compatibility_provenance_preserved,
            "evaluation_provenance_preserved": provenance.evaluation_provenance_preserved,
            "session_provenance_preserved": provenance.session_provenance_preserved,
            "scenario_provenance_preserved": provenance.scenario_provenance_preserved,
            "aggregation_provenance_preserved": provenance.aggregation_provenance_preserved,
            "integrity_provenance_preserved": provenance.integrity_provenance_preserved,
            "execution_boundary_provenance_preserved": provenance.execution_boundary_provenance_preserved,
        },
        "explainability_certification_totals": {
            "explainability_status": explainability.explainability_status,
            "explanation_count": explainability.explanation_count,
            "scope_explanation_count": explainability.scope_explanation_count,
            "evidence_source_explanation_count": explainability.evidence_source_explanation_count,
            "execution_boundary_explanation_count": explainability.execution_boundary_explanation_count,
            "does_not_authorize_explanation_count": explainability.does_not_authorize_explanation_count,
        },
        "replay_certification_totals": {
            "replay_evidence_count": replay["replay_evidence_count"],
            "non_executable_replay_evidence": replay["non_executable_replay_evidence"],
            "runtime_replay": replay["runtime_replay"],
            "execution_authorization": replay["execution_authorization"],
            "runtime_readiness_certification": replay["runtime_readiness_certification"],
            "replay_continuity_preserved": replay["replay_continuity_preserved"],
        },
        "rollback_certification_totals": {
            "rollback_reference_count": replay["rollback_reference_count"],
            "rollback_continuity_preserved": replay["rollback_continuity_preserved"],
        },
        "integrity_certification_totals": {
            "integrity_scope_count": _scope_type_count(certification, "integrity"),
            "integrity_evidence_reference_count": len(certification.evidence.integrity_evidence_references),
            "integrity_continuity_preserved": audit.integrity_continuity_preserved,
        },
        "execution_boundary_certification_totals": {
            "execution_boundary_certification_failure_count": validation.execution_boundary_certification_failure_count,
            "execution_boundary_continuity_preserved": audit.execution_boundary_continuity_preserved,
            "no_execution_authorization": validation.certified_continuity_does_not_authorize_execution,
            "no_runtime_readiness_certification": validation.certification_does_not_mark_runtime_execution_readiness,
        },
        "validation_totals": {
            "validation_status": validation.validation_status,
            "valid": validation.valid,
            "finding_count": validation.finding_count,
            "error_count": validation.error_count,
            "visibility_finding_count": validation.visibility_finding_count,
            "duplicate_certification_identity_count": validation.duplicate_certification_identity_count,
            "duplicate_scope_identity_count": validation.duplicate_scope_identity_count,
            "incomplete_scope_count": validation.incomplete_scope_count,
            "hidden_prohibited_finding_count": validation.hidden_prohibited_finding_count,
            "hidden_unsupported_finding_count": validation.hidden_unsupported_finding_count,
            "hidden_unknown_finding_count": validation.hidden_unknown_finding_count,
            "execution_boundary_certification_failure_count": validation.execution_boundary_certification_failure_count,
            "certification_non_executable": validation.certification_non_executable,
            "certified_continuity_does_not_authorize_execution": validation.certified_continuity_does_not_authorize_execution,
            "certification_does_not_mark_runtime_execution_readiness": validation.certification_does_not_mark_runtime_execution_readiness,
            "routing_scheduling_dispatch_traversal_prohibited": validation.routing_scheduling_dispatch_traversal_prohibited,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "scope_hash": hash_v3_7_graph_certification_scope(certification.scope),
            "certification_hash": hash_v3_7_graph_planning_continuity_certification(certification),
            "validation_hash": validation.deterministic_validation_hash,
            "audit_hash": audit.deterministic_audit_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_GRAPH_CERTIFICATION_VALIDATION_STABLE,
            "audit_coverage": audit.audit_status == V37_GRAPH_CERTIFICATION_AUDIT_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED,
            "explainability_coverage": explainability.explainability_status == V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE,
            "replay_continuity_coverage": replay["replay_continuity_preserved"],
            "rollback_continuity_coverage": replay["rollback_continuity_preserved"],
            "non_executable_confirmation": validation.certification_non_executable,
            "no_execution_authorization_confirmation": validation.certified_continuity_does_not_authorize_execution,
            "no_runtime_readiness_certification_confirmation": validation.certification_does_not_mark_runtime_execution_readiness,
        },
        "certification_record": export_v3_7_graph_planning_continuity_certification(certification),
        "finding_records": export_v3_7_graph_certification_finding_records(certification.findings),
        "replay_evidence_records": export_v3_7_graph_certification_replay_evidence_records(certification.replay_evidence),
        "validation_result": export_v3_7_graph_certification_validation_result(validation),
        "audit_result": export_v3_7_graph_certification_audit_result(audit),
        "provenance_result": export_v3_7_graph_certification_provenance_result(provenance),
        "explainability_result": export_v3_7_graph_certification_explainability_result(explainability),
        "explicit_limitations": [
            "certification is non-executable",
            "certification validates planning continuity only",
            "certified continuity does not authorize execution",
            "certification does not mark runtime execution readiness",
            "certification does not route, schedule, dispatch, traverse, optimize, recommend, or execute",
            "certification evidence is planning-readiness evidence only",
        ],
        "summary": {
            "certification_outcome": certification.certification_outcome,
            "validation_status": validation.validation_status,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "provenance_continuity_verified": validation.provenance_continuity_preserved,
            "explainability_continuity_verified": validation.explainability_continuity_preserved,
            "replay_continuity_verified": validation.replay_continuity_preserved,
            "rollback_continuity_verified": validation.rollback_continuity_preserved,
            "non_executable_verified": validation.certification_non_executable,
            "no_execution_authorization_verified": validation.certified_continuity_does_not_authorize_execution,
            "no_runtime_readiness_certification_verified": validation.certification_does_not_mark_runtime_execution_readiness,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.7 Graph Planning Continuity Certification",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 Phase 9 adds end-to-end graph planning continuity certification.",
        "",
        "Certification is NON-executable.",
        "",
        "Certification validates planning continuity only.",
        "",
        "Certified continuity does NOT authorize execution.",
        "",
        "Certification does NOT mark runtime execution readiness.",
        "",
        "Certification does NOT route, schedule, dispatch, traverse, optimize, recommend, or execute.",
        "",
        "Certification evidence is planning-readiness evidence only.",
        "",
        "Planning continuity certification certifies deterministic evidence continuity. Runtime execution readiness certification would certify runtime execution readiness. This phase implements planning continuity certification only, not runtime execution readiness certification.",
        "",
        "## Deterministic Scope",
        "",
        f"- Certification outcome: `{report['certification_outcome_counts']['certification_outcome']}`",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Scope references: `{report['certification_scope_counts']['scope_reference_count']}`",
        f"- Certification findings: `{report['certification_finding_totals']['finding_count']}`",
        f"- Execution-boundary failures: `{report['execution_boundary_certification_totals']['execution_boundary_certification_failure_count']}`",
        f"- Serialization stable: `{report['deterministic_guarantees']['serialization_stable']}`",
        f"- Hash stable: `{report['deterministic_guarantees']['hash_stable']}`",
        "",
        "## Explicit Non-Execution Guarantees",
        "",
        "- Graph execution remains disabled.",
        "- Certification-driven execution remains disabled.",
        "- Orchestration authorization remains disabled.",
        "- Execution readiness approval remains disabled.",
        "- Routing remains disabled.",
        "- Scheduling remains disabled.",
        "- Dispatch remains disabled.",
        "- Traversal remains disabled.",
        "- Runtime path selection remains disabled.",
        "- Scenario execution selection remains disabled.",
        "- Optimization for execution remains disabled.",
        "- Recommendation to execute remains disabled.",
        "- Executable certification gates remain prohibited.",
        "",
        "## Planning Continuity Certification vs Runtime Execution Readiness Certification",
        "",
        "Planning continuity certification validates deterministic continuity across planning evidence, provenance, explainability, replay, rollback, integrity, and execution-boundary records.",
        "",
        "Runtime execution readiness certification would certify readiness to execute runtime behavior. This phase does not implement runtime execution readiness certification.",
        "",
        "## Generated Evidence",
        "",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        f"- Certification hash: `{report['deterministic_guarantees']['certification_hash']}`",
        f"- Scope hash: `{report['deterministic_guarantees']['scope_hash']}`",
        f"- Validation hash: `{report['deterministic_guarantees']['validation_hash']}`",
        f"- Audit hash: `{report['deterministic_guarantees']['audit_hash']}`",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _scope_type_count(certification, reference_type: str) -> int:
    return sum(1 for reference in certification.scope.references if reference.reference_type == reference_type)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "docs" / "generated" / "v3_7_graph_planning_continuity_certification_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "docs" / "migration" / "V3_7_GRAPH_PLANNING_CONTINUITY_CERTIFICATION.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_7_graph_planning_continuity_certification_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
