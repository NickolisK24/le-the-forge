"""Report builders for deterministic v3.9 transition evaluation intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .transition_evaluation_engine import evaluate_v3_9_transition_evaluation
from .transition_evaluation_models import (
    EVALUATION_CLASSIFICATION_BLOCKED,
    EVALUATION_CLASSIFICATION_INCOMPLETE,
    EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_PROHIBITED,
    EVALUATION_CLASSIFICATION_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNKNOWN,
    EVALUATION_CLASSIFICATION_UNSUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNSUPPORTED,
    EVALUATION_FINDING_COMPATIBILITY,
    EVALUATION_FINDING_CONTINUITY,
    EVALUATION_FINDING_EXPLAINABILITY,
    EVALUATION_FINDING_GOVERNANCE,
    EVALUATION_FINDING_INTEGRITY,
    EVALUATION_FINDING_MISSING_EVIDENCE,
    EVALUATION_FINDING_PROHIBITED,
    EVALUATION_FINDING_PROVENANCE,
    EVALUATION_FINDING_UNCERTAINTY,
    EVALUATION_FINDING_UNSUPPORTED,
    export_transition_evaluation_report,
)
from .transition_evaluation_serialization import (
    hash_transition_evaluation_report,
    validate_transition_evaluation_hash_stability,
    validate_transition_evaluation_serialization_stability,
)
from .transition_evaluation_validation import validate_transition_evaluation_report
from .transition_foundation_hashing import deterministic_hash


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"

SOURCE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/generated/v3_9_transition_foundations_report.json",
    "docs/migration/V3_9_TRANSITION_FOUNDATIONS.md",
    "docs/generated/v3_9_transition_boundary_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_BOUNDARY_INTELLIGENCE.md",
    "docs/generated/v3_9_transition_compatibility_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_COMPATIBILITY_INTELLIGENCE.md",
)


def build_v3_9_transition_evaluation_intelligence_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    evaluation_report = evaluate_v3_9_transition_evaluation()
    validation = validate_transition_evaluation_report(evaluation_report)
    serialization = validate_transition_evaluation_serialization_stability(evaluation_report)
    hashing = validate_transition_evaluation_hash_stability(evaluation_report)
    source_artifacts = [_source_artifact_status(root, path) for path in SOURCE_ARTIFACT_PATHS]
    source_artifact_count = len(source_artifacts)
    present_source_artifact_count = sum(1 for artifact in source_artifacts if artifact["present"])
    report = {
        "schema_version": "v3_9.transition_evaluation_intelligence_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.9_transition_evaluation_intelligence",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic coordination transition evaluation reasoning without transition execution"
        ),
        "evaluation_report_status": evaluation_report.report_status,
        "source_foundation_id": evaluation_report.source_foundation_id,
        "source_boundary_report_id": evaluation_report.source_boundary_report_id,
        "source_compatibility_report_id": evaluation_report.source_compatibility_report_id,
        "non_executable": evaluation_report.non_executable,
        "transition_execution_enabled": evaluation_report.transition_execution_enabled,
        "orchestration_execution_enabled": evaluation_report.orchestration_execution_enabled,
        "orchestration_traversal_enabled": evaluation_report.orchestration_traversal_enabled,
        "runtime_orchestration_engine_enabled": evaluation_report.runtime_orchestration_engine_enabled,
        "routing_enabled": evaluation_report.routing_enabled,
        "scheduling_enabled": evaluation_report.scheduling_enabled,
        "dispatch_enabled": evaluation_report.dispatch_enabled,
        "runtime_mutation_enabled": evaluation_report.runtime_mutation_enabled,
        "approval_enabled": evaluation_report.approval_enabled,
        "authorization_enabled": evaluation_report.authorization_enabled,
        "optimization_enabled": evaluation_report.optimization_enabled,
        "recommendation_enabled": evaluation_report.recommendation_enabled,
        "ranking_enabled": evaluation_report.ranking_enabled,
        "scoring_enabled": evaluation_report.scoring_enabled,
        "selection_enabled": evaluation_report.selection_enabled,
        "autonomous_orchestration_behavior_enabled": evaluation_report.autonomous_orchestration_behavior_enabled,
        "transition_handler_enabled": evaluation_report.transition_handler_enabled,
        "orchestration_evaluator_enabled": evaluation_report.orchestration_evaluator_enabled,
        "runtime_state_machine_enabled": evaluation_report.runtime_state_machine_enabled,
        "callable_orchestration_flow_enabled": evaluation_report.callable_orchestration_flow_enabled,
        "production_execution_pathway_enabled": evaluation_report.production_execution_pathway_enabled,
        "hidden_fallback_enabled": evaluation_report.hidden_fallback_enabled,
        "silent_correction_enabled": evaluation_report.silent_correction_enabled,
        "implicit_approval_enabled": evaluation_report.implicit_approval_enabled,
        "source_artifacts": source_artifacts,
        "source_artifact_totals": {
            "source_artifact_count": source_artifact_count,
            "present_source_artifact_count": present_source_artifact_count,
            "missing_source_artifact_count": source_artifact_count - present_source_artifact_count,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
        "evaluation_classification_counts": dict(evaluation_report.summary.classification_counts),
        "evaluation_finding_counts": dict(evaluation_report.summary.finding_category_counts),
        "evaluation_totals": {
            "evaluation_input_count": validation["evaluation_input_count"],
            "visibility_count": validation["visibility_count"],
            "evaluation_finding_count": validation["evaluation_finding_count"],
            "successful_count": validation["successful_count"],
            "partially_successful_count": validation["partially_successful_count"],
            "unsuccessful_count": validation["unsuccessful_count"],
            "unsupported_count": validation["unsupported_count"],
            "prohibited_count": validation["prohibited_count"],
            "unknown_count": validation["unknown_count"],
            "incomplete_count": validation["incomplete_count"],
            "blocked_count": validation["blocked_count"],
            "governance_finding_count": validation["governance_finding_count"],
            "uncertainty_finding_count": validation["uncertainty_finding_count"],
            "missing_evidence_finding_count": validation["missing_evidence_finding_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
            "hidden_finding_count": validation["hidden_finding_count"],
        },
        "deterministic_guarantees": {
            "evaluation_serialization_stable": serialization["stable"],
            "evaluation_hash_stable": hashing["stable"],
            "evaluation_hash": hash_transition_evaluation_report(evaluation_report),
            "evaluation_summary_hash": evaluation_report.summary.deterministic_summary_hash,
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "deterministic_guarantee_summary": {
            "outputs_are_deterministic": serialization["stable"] and hashing["stable"],
            "finding_order_is_stable": True,
            "visibility_order_is_stable": True,
            "serialization_is_stable": serialization["stable"],
            "hashing_is_stable": hashing["stable"],
            "repeated_equivalent_evaluations_produce_equivalent_outputs": True,
        },
        "replay_guarantees": {
            "replay_safe_evaluation_evidence_count": validation["replay_safe_evaluation_evidence_count"],
            "replay_continuity_preserved_count": validation["replay_continuity_preserved_count"],
            "all_findings_have_replay_evidence": validation["replay_safe_evaluation_evidence_count"]
            == validation["finding_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evaluation_evidence_count": validation["rollback_safe_evaluation_evidence_count"],
            "rollback_continuity_preserved_count": validation["rollback_continuity_preserved_count"],
            "all_findings_have_rollback_evidence": validation["rollback_safe_evaluation_evidence_count"]
            == validation["finding_count"],
        },
        "provenance_guarantees": {
            "provenance_safe_evaluation_evidence_count": validation[
                "provenance_safe_evaluation_evidence_count"
            ],
            "provenance_continuity_preserved_count": validation["provenance_continuity_preserved_count"],
            "all_findings_preserve_provenance": validation["provenance_safe_evaluation_evidence_count"]
            == validation["finding_count"],
        },
        "explainability_guarantees": {
            "explainability_safe_evaluation_evidence_count": validation[
                "explainability_safe_evaluation_evidence_count"
            ],
            "explainability_continuity_preserved_count": validation[
                "explainability_continuity_preserved_count"
            ],
            "all_findings_have_explainability": validation["finding_not_fail_visible_count"] == 0,
            "hidden_finding_count": validation["hidden_finding_count"],
            "uncertainty_finding_count": validation["uncertainty_finding_count"],
        },
        "non_execution_guarantees": {
            "transition_execution_absent": not evaluation_report.transition_execution_enabled,
            "orchestration_execution_absent": not evaluation_report.orchestration_execution_enabled,
            "orchestration_traversal_absent": not evaluation_report.orchestration_traversal_enabled,
            "runtime_orchestration_engine_absent": not evaluation_report.runtime_orchestration_engine_enabled,
            "routing_absent": not evaluation_report.routing_enabled,
            "scheduling_absent": not evaluation_report.scheduling_enabled,
            "dispatch_absent": not evaluation_report.dispatch_enabled,
            "runtime_mutation_absent": not evaluation_report.runtime_mutation_enabled,
            "approval_absent": not evaluation_report.approval_enabled,
            "authorization_absent": not evaluation_report.authorization_enabled,
            "optimization_absent": not evaluation_report.optimization_enabled,
            "recommendation_absent": not evaluation_report.recommendation_enabled,
            "ranking_absent": not evaluation_report.ranking_enabled,
            "scoring_absent": not evaluation_report.scoring_enabled,
            "selection_absent": not evaluation_report.selection_enabled,
            "autonomous_orchestration_behavior_absent": not evaluation_report.autonomous_orchestration_behavior_enabled,
            "transition_handler_absent": not evaluation_report.transition_handler_enabled,
            "orchestration_evaluator_absent": not evaluation_report.orchestration_evaluator_enabled,
            "runtime_state_machine_absent": not evaluation_report.runtime_state_machine_enabled,
            "callable_orchestration_flow_absent": not evaluation_report.callable_orchestration_flow_enabled,
            "production_execution_pathway_absent": not evaluation_report.production_execution_pathway_enabled,
            "hidden_fallback_absent": not evaluation_report.hidden_fallback_enabled,
            "silent_correction_absent": not evaluation_report.silent_correction_enabled,
            "implicit_approval_absent": not evaluation_report.implicit_approval_enabled,
            "report_execution_capability_violation_count": validation[
                "report_execution_capability_violation_count"
            ],
        },
        "classification_semantics": {
            EVALUATION_CLASSIFICATION_SUCCESSFUL: "compatible transition relationship with all deterministic continuity present and no non-safe markers",
            EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL: "some evaluation guarantees pass while visible uncertainty remains",
            EVALUATION_CLASSIFICATION_UNSUCCESSFUL: "deterministic evaluation, compatibility, continuity, provenance, explainability, governance, or integrity findings fail",
            EVALUATION_CLASSIFICATION_UNSUPPORTED: "evaluation domain is outside supported deterministic scope",
            EVALUATION_CLASSIFICATION_PROHIBITED: "requested evaluation behavior violates hard non-execution boundaries",
            EVALUATION_CLASSIFICATION_UNKNOWN: "evaluation semantics cannot be deterministically interpreted",
            EVALUATION_CLASSIFICATION_INCOMPLETE: "required evaluation, continuity, provenance, compatibility, or explainability evidence is missing",
            EVALUATION_CLASSIFICATION_BLOCKED: "governance, integrity, or execution-boundary policy blocks evaluation",
        },
        "finding_semantics": {
            EVALUATION_FINDING_COMPATIBILITY: "compatibility evidence finding",
            EVALUATION_FINDING_CONTINUITY: "replay or rollback continuity finding",
            EVALUATION_FINDING_PROVENANCE: "provenance chain finding",
            EVALUATION_FINDING_EXPLAINABILITY: "explainability continuity finding",
            EVALUATION_FINDING_GOVERNANCE: "governance policy finding",
            EVALUATION_FINDING_INTEGRITY: "integrity policy finding",
            EVALUATION_FINDING_UNSUPPORTED: "unsupported evaluation finding",
            EVALUATION_FINDING_PROHIBITED: "prohibited behavior finding",
            EVALUATION_FINDING_MISSING_EVIDENCE: "missing evidence finding",
            EVALUATION_FINDING_UNCERTAINTY: "explicit uncertainty finding",
        },
        "evaluation_report": export_transition_evaluation_report(evaluation_report),
        "explicit_limitations": [
            "v3.9 Phase 4 transition evaluation intelligence is non-executable",
            "v3.9 Phase 4 does not enable orchestration execution",
            "v3.9 Phase 4 does not enable transition execution",
            "v3.9 Phase 4 does not enable orchestration traversal",
            "v3.9 Phase 4 does not enable routing, scheduling, or dispatch",
            "v3.9 Phase 4 does not enable runtime orchestration engines",
            "v3.9 Phase 4 does not enable runtime mutation",
            "v3.9 Phase 4 does not enable authorization or approval systems",
            "v3.9 Phase 4 does not enable optimization or recommendations",
            "v3.9 Phase 4 does not enable ranking, scoring, or selection",
            "v3.9 Phase 4 does not enable autonomous orchestration behavior",
            "v3.9 Phase 4 does not enable transition handlers or runtime state machines",
            "v3.9 Phase 4 does not enable callable orchestration flows",
            "v3.9 Phase 4 does not enable production execution pathways",
        ],
        "summary": {
            "evaluation_report_status": evaluation_report.report_status,
            "validation_error_count": validation["validation_error_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "successful_count": validation["successful_count"],
            "partially_successful_count": validation["partially_successful_count"],
            "unsuccessful_count": validation["unsuccessful_count"],
            "unsupported_count": validation["unsupported_count"],
            "prohibited_count": validation["prohibited_count"],
            "unknown_count": validation["unknown_count"],
            "incomplete_count": validation["incomplete_count"],
            "blocked_count": validation["blocked_count"],
            "evaluation_finding_count": validation["evaluation_finding_count"],
            "governance_finding_count": validation["governance_finding_count"],
            "uncertainty_finding_count": validation["uncertainty_finding_count"],
            "missing_evidence_finding_count": validation["missing_evidence_finding_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
            "hidden_finding_count": validation["hidden_finding_count"],
            "report_execution_capability_violation_count": validation[
                "report_execution_capability_violation_count"
            ],
            "replay_verified": validation["replay_safe_evaluation_evidence_count"] == validation["finding_count"],
            "rollback_verified": validation["rollback_safe_evaluation_evidence_count"]
            == validation["finding_count"],
            "provenance_verified": validation["provenance_safe_evaluation_evidence_count"]
            == validation["finding_count"],
            "explainability_verified": validation["finding_not_fail_visible_count"] == 0,
            "non_executable_verified": evaluation_report.non_executable,
            "orchestration_boundaries_enforced": validation["report_execution_capability_violation_count"] == 0,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_transition_evaluation_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.9 Transition Evaluation Intelligence",
        "",
        "## What Phase 4 Adds",
        "",
        "v3.9 Phase 4 adds deterministic transition evaluation intelligence on top of Phase 3 compatibility intelligence.",
        "",
        "It evaluates transition state relationships and emits explainable evidence-driven evaluation findings without enabling execution behavior.",
        "",
        "This phase does NOT enable orchestration execution, traversal, routing, scheduling, dispatch, optimization, recommendation, ranking, scoring, selection, authorization, approval, or runtime mutation.",
        "",
        "## Evaluation Is Not Execution",
        "",
        "Evaluation compares compatibility classifications, continuity references, provenance references, evidence references, and explainability context.",
        "",
        "It does not execute a transition, traverse an orchestration graph, choose a route, schedule dispatch, authorize behavior, approve a transition, mutate runtime state, or produce an executable pathway.",
        "",
        "## Deterministic Evaluation Reasoning",
        "",
        "- `successful` requires compatibility, no conflicts, provenance continuity, replay continuity, rollback continuity, explainability continuity, and no non-safe markers.",
        "- `partially_successful` records passed guarantees and failed guarantees without escalating to success.",
        "- `unsuccessful` records deterministic failed compatibility, continuity, provenance, explainability, governance, or integrity findings.",
        "- `unsupported`, `prohibited`, `unknown`, `incomplete`, and `blocked` remain explicit classifications.",
        "",
        "## Fail-Visible Findings",
        "",
        "Every evaluation finding includes a visible reason, evidence reference, provenance reference, continuity reference, and explainability message.",
        "",
        "No finding is hidden, silently corrected, downgraded, or converted into a successful evaluation.",
        "",
        "## Uncertainty Visibility",
        "",
        "Uncertainty is modeled as explicit `uncertainty` findings and `unknown` or `partially_successful` visibility records.",
        "",
        "Uncertainty never authorizes execution and never silently becomes success.",
        "",
        "## Governance-Safe Evaluation",
        "",
        "Governance and integrity findings can block evaluation while preserving deterministic evidence, provenance, replay, rollback, and explainability continuity.",
        "",
        "## Evaluation Totals",
        "",
        f"- Successful: `{report['summary']['successful_count']}`",
        f"- Partially successful: `{report['summary']['partially_successful_count']}`",
        f"- Unsuccessful: `{report['summary']['unsuccessful_count']}`",
        f"- Unsupported: `{report['summary']['unsupported_count']}`",
        f"- Prohibited: `{report['summary']['prohibited_count']}`",
        f"- Unknown: `{report['summary']['unknown_count']}`",
        f"- Incomplete: `{report['summary']['incomplete_count']}`",
        f"- Blocked: `{report['summary']['blocked_count']}`",
        "",
        "## Finding Totals",
        "",
        f"- Evaluation findings: `{report['summary']['evaluation_finding_count']}`",
        f"- Governance findings: `{report['summary']['governance_finding_count']}`",
        f"- Uncertainty findings: `{report['summary']['uncertainty_finding_count']}`",
        f"- Missing-evidence findings: `{report['summary']['missing_evidence_finding_count']}`",
        f"- Execution-boundary violation detections: `{report['summary']['execution_boundary_violation_count']}`",
        f"- Hidden findings: `{report['summary']['hidden_finding_count']}`",
        "",
        "## Deterministic Guarantees",
        "",
        f"- Evaluation report status: `{report['summary']['evaluation_report_status']}`",
        f"- Validation errors: `{report['summary']['validation_error_count']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Evaluation hash: `{report['deterministic_guarantees']['evaluation_hash']}`",
        f"- Evaluation summary hash: `{report['deterministic_guarantees']['evaluation_summary_hash']}`",
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
        "- Orchestration traversal.",
        "- Runtime orchestration engines.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Runtime mutation.",
        "- Approval systems.",
        "- Authorization systems.",
        "- Optimization.",
        "- Recommendations.",
        "- Ranking.",
        "- Scoring.",
        "- Selection.",
        "- Autonomous orchestration behavior.",
        "- Transition handlers.",
        "- Orchestration evaluators.",
        "- Runtime state machines.",
        "- Callable orchestration flows.",
        "- Production execution pathways.",
        "",
        "## Builds On Compatibility Intelligence",
        "",
        "Phase 4 consumes Phase 3 compatibility outputs as evidence references, then evaluates relationship readiness without changing compatibility reasoning or enabling behavior.",
        "",
        "## Generated Evidence",
        "",
        "- JSON report: `docs/generated/v3_9_transition_evaluation_intelligence_report.json`",
        "- This migration note: `docs/migration/V3_9_TRANSITION_EVALUATION_INTELLIGENCE.md`",
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
