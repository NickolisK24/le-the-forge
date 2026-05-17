"""Report builders for deterministic v3.9 transition session intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .transition_foundation_hashing import deterministic_hash
from .transition_session_engine import build_v3_9_transition_session
from .transition_session_models import (
    SESSION_CLASSIFICATION_BLOCKED,
    SESSION_CLASSIFICATION_COMPLETE,
    SESSION_CLASSIFICATION_INCOMPLETE,
    SESSION_CLASSIFICATION_PARTIALLY_COMPLETE,
    SESSION_CLASSIFICATION_PROHIBITED,
    SESSION_CLASSIFICATION_UNKNOWN,
    SESSION_CLASSIFICATION_UNSUPPORTED,
    SESSION_FINDING_COMPLETENESS,
    SESSION_FINDING_CONTINUITY,
    SESSION_FINDING_EVALUATION,
    SESSION_FINDING_EXPLAINABILITY,
    SESSION_FINDING_GOVERNANCE,
    SESSION_FINDING_INTEGRITY,
    SESSION_FINDING_MISSING_EVIDENCE,
    SESSION_FINDING_PROHIBITED,
    SESSION_FINDING_PROVENANCE,
    SESSION_FINDING_UNCERTAINTY,
    SESSION_FINDING_UNSUPPORTED,
    export_transition_session_report,
)
from .transition_session_serialization import (
    hash_transition_session_report,
    validate_transition_session_hash_stability,
    validate_transition_session_serialization_stability,
)
from .transition_session_validation import validate_transition_session_report


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"

SOURCE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/generated/v3_9_transition_foundations_report.json",
    "docs/migration/V3_9_TRANSITION_FOUNDATIONS.md",
    "docs/generated/v3_9_transition_boundary_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_BOUNDARY_INTELLIGENCE.md",
    "docs/generated/v3_9_transition_compatibility_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_COMPATIBILITY_INTELLIGENCE.md",
    "docs/generated/v3_9_transition_evaluation_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_EVALUATION_INTELLIGENCE.md",
)


def build_v3_9_transition_session_intelligence_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    session_report = build_v3_9_transition_session()
    validation = validate_transition_session_report(session_report)
    serialization = validate_transition_session_serialization_stability(session_report)
    hashing = validate_transition_session_hash_stability(session_report)
    source_artifacts = [_source_artifact_status(root, path) for path in SOURCE_ARTIFACT_PATHS]
    source_artifact_count = len(source_artifacts)
    present_source_artifact_count = sum(1 for artifact in source_artifacts if artifact["present"])
    report = {
        "schema_version": "v3_9.transition_session_intelligence_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.9_transition_session_intelligence",
        "repo_root": str(root),
        "architectural_purpose": "deterministic transition review session evidence packaging without transition execution",
        "session_report_status": session_report.report_status,
        "source_foundation_id": session_report.source_foundation_id,
        "source_boundary_report_id": session_report.source_boundary_report_id,
        "source_compatibility_report_id": session_report.source_compatibility_report_id,
        "source_evaluation_report_id": session_report.source_evaluation_report_id,
        "non_executable": session_report.non_executable,
        "orchestration_execution_enabled": session_report.orchestration_execution_enabled,
        "transition_execution_enabled": session_report.transition_execution_enabled,
        "graph_traversal_enabled": session_report.graph_traversal_enabled,
        "routing_enabled": session_report.routing_enabled,
        "scheduling_enabled": session_report.scheduling_enabled,
        "dispatch_enabled": session_report.dispatch_enabled,
        "runtime_orchestration_engine_enabled": session_report.runtime_orchestration_engine_enabled,
        "runtime_mutation_enabled": session_report.runtime_mutation_enabled,
        "authorization_enabled": session_report.authorization_enabled,
        "approval_enabled": session_report.approval_enabled,
        "optimization_enabled": session_report.optimization_enabled,
        "recommendation_enabled": session_report.recommendation_enabled,
        "ranking_enabled": session_report.ranking_enabled,
        "scoring_enabled": session_report.scoring_enabled,
        "selection_enabled": session_report.selection_enabled,
        "autonomous_behavior_enabled": session_report.autonomous_behavior_enabled,
        "callable_orchestration_flow_enabled": session_report.callable_orchestration_flow_enabled,
        "transition_handler_enabled": session_report.transition_handler_enabled,
        "runtime_state_machine_enabled": session_report.runtime_state_machine_enabled,
        "production_behavior_enabled": session_report.production_behavior_enabled,
        "hidden_fallback_enabled": session_report.hidden_fallback_enabled,
        "silent_correction_enabled": session_report.silent_correction_enabled,
        "source_artifacts": source_artifacts,
        "source_artifact_totals": {
            "source_artifact_count": source_artifact_count,
            "present_source_artifact_count": present_source_artifact_count,
            "missing_source_artifact_count": source_artifact_count - present_source_artifact_count,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
        "session_classification_counts": dict(session_report.summary.classification_counts),
        "session_finding_counts": dict(session_report.summary.finding_category_counts),
        "session_totals": {
            "session_input_count": validation["session_input_count"],
            "session_record_count": validation["session_record_count"],
            "evaluation_entry_count": validation["evaluation_entry_count"],
            "session_finding_count": validation["session_finding_count"],
            "complete_count": validation["complete_count"],
            "partially_complete_count": validation["partially_complete_count"],
            "incomplete_count": validation["incomplete_count"],
            "blocked_count": validation["blocked_count"],
            "unsupported_count": validation["unsupported_count"],
            "prohibited_count": validation["prohibited_count"],
            "unknown_count": validation["unknown_count"],
            "governance_finding_count": validation["governance_finding_count"],
            "uncertainty_finding_count": validation["uncertainty_finding_count"],
            "missing_evidence_finding_count": validation["missing_evidence_finding_count"],
            "hidden_session_finding_count": validation["hidden_session_finding_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
        },
        "deterministic_guarantees": {
            "session_serialization_stable": serialization["stable"],
            "session_hash_stable": hashing["stable"],
            "session_hash": hash_transition_session_report(session_report),
            "session_summary_hash": session_report.summary.deterministic_summary_hash,
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "deterministic_guarantee_summary": {
            "outputs_are_deterministic": serialization["stable"] and hashing["stable"],
            "entry_order_is_stable": True,
            "finding_order_is_stable": True,
            "record_order_is_stable": True,
            "serialization_is_stable": serialization["stable"],
            "hashing_is_stable": hashing["stable"],
            "repeated_equivalent_session_inputs_produce_equivalent_outputs": True,
        },
        "replay_guarantees": {
            "replay_safe_session_finding_count": validation["replay_safe_session_finding_count"],
            "replay_continuity_preserved_count": validation["replay_continuity_preserved_count"],
            "all_findings_have_replay_evidence": validation["replay_safe_session_finding_count"]
            == validation["session_finding_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_session_finding_count": validation["rollback_safe_session_finding_count"],
            "rollback_continuity_preserved_count": validation["rollback_continuity_preserved_count"],
            "all_findings_have_rollback_evidence": validation["rollback_safe_session_finding_count"]
            == validation["session_finding_count"],
        },
        "provenance_guarantees": {
            "provenance_safe_session_finding_count": validation["provenance_safe_session_finding_count"],
            "provenance_continuity_preserved_count": validation["provenance_continuity_preserved_count"],
            "all_findings_preserve_provenance": validation["provenance_safe_session_finding_count"]
            == validation["session_finding_count"],
        },
        "explainability_guarantees": {
            "explainability_safe_session_finding_count": validation["explainability_safe_session_finding_count"],
            "explainability_continuity_preserved_count": validation["explainability_continuity_preserved_count"],
            "all_findings_have_explainability": validation["finding_not_fail_visible_count"] == 0,
            "hidden_session_finding_count": validation["hidden_session_finding_count"],
            "uncertainty_finding_count": validation["uncertainty_finding_count"],
        },
        "non_execution_guarantees": {
            "orchestration_execution_absent": not session_report.orchestration_execution_enabled,
            "transition_execution_absent": not session_report.transition_execution_enabled,
            "graph_traversal_absent": not session_report.graph_traversal_enabled,
            "routing_absent": not session_report.routing_enabled,
            "scheduling_absent": not session_report.scheduling_enabled,
            "dispatch_absent": not session_report.dispatch_enabled,
            "runtime_orchestration_engine_absent": not session_report.runtime_orchestration_engine_enabled,
            "runtime_mutation_absent": not session_report.runtime_mutation_enabled,
            "authorization_absent": not session_report.authorization_enabled,
            "approval_absent": not session_report.approval_enabled,
            "optimization_absent": not session_report.optimization_enabled,
            "recommendation_absent": not session_report.recommendation_enabled,
            "ranking_absent": not session_report.ranking_enabled,
            "scoring_absent": not session_report.scoring_enabled,
            "selection_absent": not session_report.selection_enabled,
            "autonomous_behavior_absent": not session_report.autonomous_behavior_enabled,
            "callable_orchestration_flow_absent": not session_report.callable_orchestration_flow_enabled,
            "transition_handler_absent": not session_report.transition_handler_enabled,
            "runtime_state_machine_absent": not session_report.runtime_state_machine_enabled,
            "production_behavior_absent": not session_report.production_behavior_enabled,
            "hidden_fallback_absent": not session_report.hidden_fallback_enabled,
            "silent_correction_absent": not session_report.silent_correction_enabled,
            "report_execution_capability_violation_count": validation[
                "report_execution_capability_violation_count"
            ],
        },
        "classification_semantics": {
            SESSION_CLASSIFICATION_COMPLETE: "session identity, evaluation records, provenance, replay, rollback, explainability, and evidence are present with no non-safe markers",
            SESSION_CLASSIFICATION_PARTIALLY_COMPLETE: "at least one evaluation is complete while one or more required session guarantees remain visible",
            SESSION_CLASSIFICATION_INCOMPLETE: "session identity, evaluation records, provenance, continuity, or explainability evidence is missing",
            SESSION_CLASSIFICATION_BLOCKED: "governance, integrity, or execution-boundary preservation blocks the session",
            SESSION_CLASSIFICATION_UNSUPPORTED: "session domain or evidence is outside supported deterministic scope",
            SESSION_CLASSIFICATION_PROHIBITED: "requested session recording behavior violates non-execution boundaries",
            SESSION_CLASSIFICATION_UNKNOWN: "session semantics, provenance meaning, continuity meaning, or evidence meaning is uncertain",
        },
        "finding_semantics": {
            SESSION_FINDING_EVALUATION: "evaluation record packaging finding",
            SESSION_FINDING_CONTINUITY: "session replay or rollback continuity finding",
            SESSION_FINDING_PROVENANCE: "session provenance finding",
            SESSION_FINDING_EXPLAINABILITY: "session explainability finding",
            SESSION_FINDING_GOVERNANCE: "session governance finding",
            SESSION_FINDING_INTEGRITY: "session integrity finding",
            SESSION_FINDING_UNSUPPORTED: "unsupported session finding",
            SESSION_FINDING_PROHIBITED: "prohibited session behavior finding",
            SESSION_FINDING_MISSING_EVIDENCE: "missing session evidence finding",
            SESSION_FINDING_UNCERTAINTY: "uncertain session evidence finding",
            SESSION_FINDING_COMPLETENESS: "session completeness finding",
        },
        "session_report": export_transition_session_report(session_report),
        "explicit_limitations": [
            "v3.9 Phase 5 transition session intelligence is non-executable",
            "v3.9 Phase 5 does not enable orchestration execution",
            "v3.9 Phase 5 does not enable transition execution",
            "v3.9 Phase 5 does not enable graph traversal",
            "v3.9 Phase 5 does not enable routing, scheduling, or dispatch",
            "v3.9 Phase 5 does not enable runtime orchestration engines",
            "v3.9 Phase 5 does not enable runtime mutation",
            "v3.9 Phase 5 does not enable authorization or approval systems",
            "v3.9 Phase 5 does not enable optimization or recommendations",
            "v3.9 Phase 5 does not enable ranking, scoring, or selection",
            "v3.9 Phase 5 does not enable autonomous behavior",
            "v3.9 Phase 5 does not enable callable orchestration flows",
            "v3.9 Phase 5 does not enable transition handlers or runtime state machines",
            "v3.9 Phase 5 does not enable production behavior",
        ],
        "summary": {
            "session_report_status": session_report.report_status,
            "validation_error_count": validation["validation_error_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "complete_count": validation["complete_count"],
            "partially_complete_count": validation["partially_complete_count"],
            "incomplete_count": validation["incomplete_count"],
            "blocked_count": validation["blocked_count"],
            "unsupported_count": validation["unsupported_count"],
            "prohibited_count": validation["prohibited_count"],
            "unknown_count": validation["unknown_count"],
            "session_finding_count": validation["session_finding_count"],
            "evaluation_entry_count": validation["evaluation_entry_count"],
            "governance_finding_count": validation["governance_finding_count"],
            "uncertainty_finding_count": validation["uncertainty_finding_count"],
            "missing_evidence_finding_count": validation["missing_evidence_finding_count"],
            "hidden_session_finding_count": validation["hidden_session_finding_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
            "report_execution_capability_violation_count": validation[
                "report_execution_capability_violation_count"
            ],
            "replay_verified": validation["replay_safe_session_finding_count"] == validation["session_finding_count"],
            "rollback_verified": validation["rollback_safe_session_finding_count"]
            == validation["session_finding_count"],
            "provenance_verified": validation["provenance_safe_session_finding_count"]
            == validation["session_finding_count"],
            "explainability_verified": validation["finding_not_fail_visible_count"] == 0,
            "non_executable_verified": session_report.non_executable,
            "orchestration_boundaries_enforced": validation["report_execution_capability_violation_count"] == 0,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_transition_session_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.9 Transition Session Intelligence",
        "",
        "## What Phase 5 Adds",
        "",
        "v3.9 Phase 5 packages deterministic transition evaluations into immutable transition review session evidence.",
        "",
        "It records session identity, evaluation entries, findings, evidence, provenance, continuity, and visibility without enabling execution behavior.",
        "",
        "This phase does NOT enable orchestration execution, traversal, routing, scheduling, dispatch, optimization, recommendation, ranking, scoring, selection, authorization, approval, or runtime mutation.",
        "",
        "## Sessions Are Not Execution",
        "",
        "A transition session is a deterministic evidence container. It does not execute a transition, authorize a transition, traverse a graph, choose a route, schedule dispatch, approve behavior, mutate runtime state, or produce a production pathway.",
        "",
        "## Immutable Session Evidence",
        "",
        "Each session record contains immutable entries, evidence references, continuity references, visibility records, and fail-visible findings.",
        "",
        "Evaluation records are packaged as session entries while preserving their evidence identity and deterministic order.",
        "",
        "## Fail-Visible Session Findings",
        "",
        "Every session finding includes a reason, evidence reference, provenance reference, continuity reference, and explainability message.",
        "",
        "No session state is hidden, silently corrected, or promoted from partial or non-complete to complete.",
        "",
        "## Governance-Safe Session Tracking",
        "",
        "Governance and integrity findings can block a session while preserving deterministic evidence, provenance, replay, rollback, and explainability continuity.",
        "",
        "## Builds On Evaluation Intelligence",
        "",
        "Phase 5 consumes Phase 4 transition evaluation outputs as session evidence references and packages them without changing evaluation reasoning.",
        "",
        "## Session Totals",
        "",
        f"- Complete: `{report['summary']['complete_count']}`",
        f"- Partially complete: `{report['summary']['partially_complete_count']}`",
        f"- Incomplete: `{report['summary']['incomplete_count']}`",
        f"- Blocked: `{report['summary']['blocked_count']}`",
        f"- Unsupported: `{report['summary']['unsupported_count']}`",
        f"- Prohibited: `{report['summary']['prohibited_count']}`",
        f"- Unknown: `{report['summary']['unknown_count']}`",
        "",
        "## Finding Totals",
        "",
        f"- Session findings: `{report['summary']['session_finding_count']}`",
        f"- Evaluation entries: `{report['summary']['evaluation_entry_count']}`",
        f"- Governance findings: `{report['summary']['governance_finding_count']}`",
        f"- Uncertainty findings: `{report['summary']['uncertainty_finding_count']}`",
        f"- Missing-evidence findings: `{report['summary']['missing_evidence_finding_count']}`",
        f"- Hidden session findings: `{report['summary']['hidden_session_finding_count']}`",
        f"- Execution-boundary violation detections: `{report['summary']['execution_boundary_violation_count']}`",
        "",
        "## Deterministic Guarantees",
        "",
        f"- Session report status: `{report['summary']['session_report_status']}`",
        f"- Validation errors: `{report['summary']['validation_error_count']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Session hash: `{report['deterministic_guarantees']['session_hash']}`",
        f"- Session summary hash: `{report['deterministic_guarantees']['session_summary_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Replay Rollback Provenance And Explainability",
        "",
        f"- Replay verified: `{report['summary']['replay_verified']}`",
        f"- Rollback verified: `{report['summary']['rollback_verified']}`",
        f"- Provenance verified: `{report['summary']['provenance_verified']}`",
        f"- Explainability verified: `{report['summary']['explainability_verified']}`",
        "",
        "## What Remains Prohibited",
        "",
        "- Orchestration execution.",
        "- Transition execution.",
        "- Graph traversal.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Runtime orchestration engines.",
        "- Runtime mutation.",
        "- Authorization systems.",
        "- Approval systems.",
        "- Optimization.",
        "- Recommendations.",
        "- Ranking.",
        "- Scoring.",
        "- Selection.",
        "- Autonomous behavior.",
        "- Callable orchestration flows.",
        "- Transition handlers.",
        "- Runtime state machines.",
        "- Production behavior.",
        "",
        "## Generated Evidence",
        "",
        "- JSON report: `docs/generated/v3_9_transition_session_intelligence_report.json`",
        "- This migration note: `docs/migration/V3_9_TRANSITION_SESSION_INTELLIGENCE.md`",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _source_artifact_status(repo_root: Path, relative_path: str) -> dict[str, Any]:
    artifact_path = repo_root / relative_path
    if not artifact_path.exists():
        return {
            "path": relative_path,
            "present": False,
            "artifact_hash": "",
        }
    text = artifact_path.read_text(encoding="utf-8")
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError:
        payload = {"raw_text": text}
    return {
        "path": relative_path,
        "present": True,
        "artifact_hash": deterministic_hash(payload),
    }
