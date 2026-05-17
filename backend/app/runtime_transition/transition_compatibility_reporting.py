"""Report builders for deterministic v3.9 transition compatibility intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .transition_compatibility_engine import evaluate_v3_9_transition_compatibility
from .transition_compatibility_models import (
    COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPLETE,
    COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_PROHIBITED,
    COMPATIBILITY_CLASSIFICATION_UNKNOWN,
    COMPATIBILITY_CLASSIFICATION_UNSUPPORTED,
    COMPATIBILITY_CONFLICT_BOUNDARY,
    COMPATIBILITY_CONFLICT_CONTINUITY,
    COMPATIBILITY_CONFLICT_EXPLAINABILITY,
    COMPATIBILITY_CONFLICT_MISSING_EVIDENCE,
    COMPATIBILITY_CONFLICT_PROHIBITED_STATE,
    COMPATIBILITY_CONFLICT_PROVENANCE,
    COMPATIBILITY_CONFLICT_TRANSITION_STATE,
    COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE,
    export_transition_compatibility_report,
)
from .transition_compatibility_serialization import (
    hash_transition_compatibility_report,
    validate_transition_compatibility_hash_stability,
    validate_transition_compatibility_serialization_stability,
)
from .transition_compatibility_validation import validate_transition_compatibility_report
from .transition_foundation_hashing import deterministic_hash


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"

SOURCE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/generated/v3_9_transition_foundations_report.json",
    "docs/migration/V3_9_TRANSITION_FOUNDATIONS.md",
    "docs/generated/v3_9_transition_boundary_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_BOUNDARY_INTELLIGENCE.md",
)


def build_v3_9_transition_compatibility_intelligence_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    compatibility_report = evaluate_v3_9_transition_compatibility()
    validation = validate_transition_compatibility_report(compatibility_report)
    serialization = validate_transition_compatibility_serialization_stability(compatibility_report)
    hashing = validate_transition_compatibility_hash_stability(compatibility_report)
    source_artifacts = [_source_artifact_status(root, path) for path in SOURCE_ARTIFACT_PATHS]
    source_artifact_count = len(source_artifacts)
    present_source_artifact_count = sum(1 for artifact in source_artifacts if artifact["present"])
    report = {
        "schema_version": "v3_9.transition_compatibility_intelligence_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.9_transition_compatibility_intelligence",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic coordination transition compatibility reasoning without orchestration execution"
        ),
        "compatibility_report_status": compatibility_report.report_status,
        "source_foundation_id": compatibility_report.source_foundation_id,
        "source_boundary_report_id": compatibility_report.source_boundary_report_id,
        "non_executable": compatibility_report.non_executable,
        "transition_execution_enabled": compatibility_report.transition_execution_enabled,
        "orchestration_execution_enabled": compatibility_report.orchestration_execution_enabled,
        "orchestration_traversal_enabled": compatibility_report.orchestration_traversal_enabled,
        "routing_enabled": compatibility_report.routing_enabled,
        "scheduling_enabled": compatibility_report.scheduling_enabled,
        "dispatch_enabled": compatibility_report.dispatch_enabled,
        "orchestration_engine_enabled": compatibility_report.orchestration_engine_enabled,
        "runtime_mutation_enabled": compatibility_report.runtime_mutation_enabled,
        "autonomous_behavior_enabled": compatibility_report.autonomous_behavior_enabled,
        "optimization_enabled": compatibility_report.optimization_enabled,
        "recommendation_enabled": compatibility_report.recommendation_enabled,
        "ranking_enabled": compatibility_report.ranking_enabled,
        "scoring_enabled": compatibility_report.scoring_enabled,
        "selection_enabled": compatibility_report.selection_enabled,
        "approval_enabled": compatibility_report.approval_enabled,
        "authorization_enabled": compatibility_report.authorization_enabled,
        "callable_orchestration_flow_enabled": compatibility_report.callable_orchestration_flow_enabled,
        "transition_handler_enabled": compatibility_report.transition_handler_enabled,
        "orchestration_evaluator_enabled": compatibility_report.orchestration_evaluator_enabled,
        "runtime_state_machine_enabled": compatibility_report.runtime_state_machine_enabled,
        "production_execution_pathway_enabled": compatibility_report.production_execution_pathway_enabled,
        "hidden_fallback_enabled": compatibility_report.hidden_fallback_enabled,
        "silent_correction_enabled": compatibility_report.silent_correction_enabled,
        "source_artifacts": source_artifacts,
        "source_artifact_totals": {
            "source_artifact_count": source_artifact_count,
            "present_source_artifact_count": present_source_artifact_count,
            "missing_source_artifact_count": source_artifact_count - present_source_artifact_count,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
        "compatibility_classification_counts": dict(compatibility_report.summary.classification_counts),
        "compatibility_conflict_counts": dict(compatibility_report.summary.conflict_counts),
        "compatibility_totals": {
            "compatibility_input_count": validation["compatibility_input_count"],
            "finding_count": validation["finding_count"],
            "compatible_count": validation["compatible_count"],
            "incompatible_count": validation["incompatible_count"],
            "partially_compatible_count": validation["partially_compatible_count"],
            "unsupported_count": validation["unsupported_count"],
            "prohibited_count": validation["prohibited_count"],
            "unknown_count": validation["unknown_count"],
            "incomplete_count": validation["incomplete_count"],
            "compatibility_conflict_count": validation["compatibility_conflict_count"],
            "provenance_conflict_count": validation["provenance_conflict_count"],
            "continuity_conflict_count": validation["continuity_conflict_count"],
            "boundary_conflict_count": validation["boundary_conflict_count"],
            "transition_state_conflict_count": validation["transition_state_conflict_count"],
            "unsupported_state_conflict_count": validation["unsupported_state_conflict_count"],
            "prohibited_state_conflict_count": validation["prohibited_state_conflict_count"],
            "explainability_conflict_count": validation["explainability_conflict_count"],
            "missing_evidence_conflict_count": validation["missing_evidence_conflict_count"],
            "hidden_conflict_count": validation["hidden_conflict_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
        },
        "deterministic_guarantees": {
            "compatibility_serialization_stable": serialization["stable"],
            "compatibility_hash_stable": hashing["stable"],
            "compatibility_hash": hash_transition_compatibility_report(compatibility_report),
            "compatibility_summary_hash": compatibility_report.summary.deterministic_summary_hash,
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "deterministic_guarantee_summary": {
            "outputs_are_deterministic": serialization["stable"] and hashing["stable"],
            "finding_order_is_stable": True,
            "conflict_order_is_stable": True,
            "serialization_is_stable": serialization["stable"],
            "hashing_is_stable": hashing["stable"],
            "repeated_equivalent_inputs_produce_equivalent_reports": True,
        },
        "replay_guarantees": {
            "replay_safe_compatibility_evidence_count": validation["replay_safe_compatibility_evidence_count"],
            "all_findings_have_replay_evidence": validation["replay_safe_compatibility_evidence_count"]
            == validation["finding_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_compatibility_evidence_count": validation[
                "rollback_safe_compatibility_evidence_count"
            ],
            "all_findings_have_rollback_evidence": validation["rollback_safe_compatibility_evidence_count"]
            == validation["finding_count"],
        },
        "provenance_guarantees": {
            "provenance_safe_compatibility_evidence_count": validation[
                "provenance_safe_compatibility_evidence_count"
            ],
            "all_findings_preserve_provenance": validation["provenance_safe_compatibility_evidence_count"]
            == validation["finding_count"],
        },
        "explainability_guarantees": {
            "explainability_safe_compatibility_evidence_count": validation[
                "explainability_safe_compatibility_evidence_count"
            ],
            "all_non_compatible_states_have_explainability": validation[
                "vague_non_compatible_output_count"
            ]
            == 0,
            "hidden_conflict_count": validation["hidden_conflict_count"],
            "non_compatible_not_fail_visible_count": validation["non_compatible_not_fail_visible_count"],
        },
        "non_execution_guarantees": {
            "transition_execution_absent": not compatibility_report.transition_execution_enabled,
            "orchestration_execution_absent": not compatibility_report.orchestration_execution_enabled,
            "orchestration_traversal_absent": not compatibility_report.orchestration_traversal_enabled,
            "routing_absent": not compatibility_report.routing_enabled,
            "scheduling_absent": not compatibility_report.scheduling_enabled,
            "dispatch_absent": not compatibility_report.dispatch_enabled,
            "orchestration_engine_absent": not compatibility_report.orchestration_engine_enabled,
            "runtime_mutation_absent": not compatibility_report.runtime_mutation_enabled,
            "autonomous_behavior_absent": not compatibility_report.autonomous_behavior_enabled,
            "optimization_absent": not compatibility_report.optimization_enabled,
            "recommendation_absent": not compatibility_report.recommendation_enabled,
            "ranking_absent": not compatibility_report.ranking_enabled,
            "scoring_absent": not compatibility_report.scoring_enabled,
            "selection_absent": not compatibility_report.selection_enabled,
            "approval_absent": not compatibility_report.approval_enabled,
            "authorization_absent": not compatibility_report.authorization_enabled,
            "callable_orchestration_flow_absent": not compatibility_report.callable_orchestration_flow_enabled,
            "transition_handler_absent": not compatibility_report.transition_handler_enabled,
            "orchestration_evaluator_absent": not compatibility_report.orchestration_evaluator_enabled,
            "runtime_state_machine_absent": not compatibility_report.runtime_state_machine_enabled,
            "production_execution_pathway_absent": not compatibility_report.production_execution_pathway_enabled,
            "hidden_fallback_absent": not compatibility_report.hidden_fallback_enabled,
            "silent_correction_absent": not compatibility_report.silent_correction_enabled,
            "report_execution_capability_violation_count": validation[
                "report_execution_capability_violation_count"
            ],
        },
        "classification_semantics": {
            COMPATIBILITY_CLASSIFICATION_COMPATIBLE: "all required references exist and no conflicts or non-safe markers are present",
            COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE: "deterministic conflicts exist between transition compatibility references",
            COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE: "some guarantees pass while localized conflicts remain fail-visible",
            COMPATIBILITY_CLASSIFICATION_UNSUPPORTED: "compatibility reasoning is outside current deterministic scope",
            COMPATIBILITY_CLASSIFICATION_PROHIBITED: "requested behavior violates hard non-execution boundaries",
            COMPATIBILITY_CLASSIFICATION_UNKNOWN: "compatibility semantics cannot be deterministically interpreted",
            COMPATIBILITY_CLASSIFICATION_INCOMPLETE: "required source, destination, provenance, continuity, or evidence references are missing",
        },
        "conflict_semantics": {
            COMPATIBILITY_CONFLICT_PROVENANCE: "source or destination provenance chains conflict",
            COMPATIBILITY_CONFLICT_CONTINUITY: "replay, rollback, provenance, or evidence continuity chains conflict",
            COMPATIBILITY_CONFLICT_BOUNDARY: "boundary classifications or governance requirements conflict",
            COMPATIBILITY_CONFLICT_TRANSITION_STATE: "transition-state classifications conflict",
            COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE: "known state or reasoning domain is unsupported",
            COMPATIBILITY_CONFLICT_PROHIBITED_STATE: "requested behavior is prohibited",
            COMPATIBILITY_CONFLICT_EXPLAINABILITY: "explainability context is ambiguous or insufficient",
            COMPATIBILITY_CONFLICT_MISSING_EVIDENCE: "required compatibility evidence is missing",
        },
        "compatibility_report": export_transition_compatibility_report(compatibility_report),
        "explicit_limitations": [
            "v3.9 Phase 3 transition compatibility intelligence is non-executable",
            "v3.9 Phase 3 does not enable orchestration execution",
            "v3.9 Phase 3 does not enable orchestration traversal",
            "v3.9 Phase 3 does not enable transition execution",
            "v3.9 Phase 3 does not enable routing, scheduling, or dispatch",
            "v3.9 Phase 3 does not enable runtime orchestration engines",
            "v3.9 Phase 3 does not enable runtime mutation",
            "v3.9 Phase 3 does not enable authorization or approval systems",
            "v3.9 Phase 3 does not enable optimization or recommendations",
            "v3.9 Phase 3 does not enable ranking, scoring, or selection",
            "v3.9 Phase 3 does not enable autonomous behavior",
            "v3.9 Phase 3 does not enable callable orchestration flows",
            "v3.9 Phase 3 does not enable transition handlers or state machines",
            "v3.9 Phase 3 does not enable production execution pathways",
        ],
        "summary": {
            "compatibility_report_status": compatibility_report.report_status,
            "validation_error_count": validation["validation_error_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "compatible_count": validation["compatible_count"],
            "incompatible_count": validation["incompatible_count"],
            "partially_compatible_count": validation["partially_compatible_count"],
            "unsupported_count": validation["unsupported_count"],
            "prohibited_count": validation["prohibited_count"],
            "unknown_count": validation["unknown_count"],
            "incomplete_count": validation["incomplete_count"],
            "compatibility_conflict_count": validation["compatibility_conflict_count"],
            "provenance_conflict_count": validation["provenance_conflict_count"],
            "continuity_conflict_count": validation["continuity_conflict_count"],
            "boundary_conflict_count": validation["boundary_conflict_count"],
            "hidden_conflict_count": validation["hidden_conflict_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
            "report_execution_capability_violation_count": validation[
                "report_execution_capability_violation_count"
            ],
            "replay_verified": validation["replay_safe_compatibility_evidence_count"]
            == validation["finding_count"],
            "rollback_verified": validation["rollback_safe_compatibility_evidence_count"]
            == validation["finding_count"],
            "provenance_verified": validation["provenance_safe_compatibility_evidence_count"]
            == validation["finding_count"],
            "explainability_verified": validation["vague_non_compatible_output_count"] == 0,
            "non_executable_verified": compatibility_report.non_executable,
            "orchestration_boundaries_enforced": validation["report_execution_capability_violation_count"]
            == 0,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_transition_compatibility_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.9 Transition Compatibility Intelligence",
        "",
        "## What Phase 3 Adds",
        "",
        "v3.9 Phase 3 adds deterministic coordination transition compatibility intelligence on top of the Phase 1 transition foundations and Phase 2 transition boundary intelligence.",
        "",
        "It classifies compatibility inputs as `compatible`, `incompatible`, `partially_compatible`, `unsupported`, `prohibited`, `unknown`, or `incomplete` while preserving immutable evidence references.",
        "",
        "This phase does NOT enable orchestration execution, traversal, routing, scheduling, dispatch, optimization, recommendation, ranking, scoring, selection, authorization, approval, or runtime mutation.",
        "",
        "## Compatibility Reasoning Is Not Execution",
        "",
        "Compatibility reasoning compares modeled transition state references, boundary classifications, provenance references, continuity references, and evidence references.",
        "",
        "It does not traverse orchestration graphs, choose a route, schedule a dispatch, approve a transition, mutate runtime state, or produce an executable pathway.",
        "",
        "## Deterministic Conflict Detection",
        "",
        "- Provenance conflicts record mismatched or incompatible provenance chains.",
        "- Continuity conflicts record replay, rollback, provenance, or evidence continuity mismatches.",
        "- Boundary conflicts record boundary-classification or governance conflicts.",
        "- Transition-state conflicts record incompatible transition classifications.",
        "- Unsupported-state conflicts record known states outside modeled support.",
        "- Prohibited-state conflicts record requests that violate non-execution boundaries.",
        "- Explainability conflicts record ambiguous or insufficient compatibility context.",
        "- Missing-evidence conflicts record absent source, destination, provenance, continuity, or compatibility evidence.",
        "",
        "## Fail-Visible Incompatibilities",
        "",
        "Every non-compatible finding carries a visible reason, immutable evidence, provenance references, continuity references, and explicit conflict records.",
        "",
        "No incompatibility is hidden, silently corrected, downgraded, or promoted into a compatible classification.",
        "",
        "## Why Partial Compatibility Exists",
        "",
        "`partially_compatible` represents deterministic cases where some compatibility guarantees pass while localized conflicts remain visible and explainable.",
        "",
        "Partial compatibility never escalates to full compatibility without eliminating the visible conflicts.",
        "",
        "## Compatibility Totals",
        "",
        f"- Compatible: `{report['summary']['compatible_count']}`",
        f"- Incompatible: `{report['summary']['incompatible_count']}`",
        f"- Partially compatible: `{report['summary']['partially_compatible_count']}`",
        f"- Unsupported: `{report['summary']['unsupported_count']}`",
        f"- Prohibited: `{report['summary']['prohibited_count']}`",
        f"- Unknown: `{report['summary']['unknown_count']}`",
        f"- Incomplete: `{report['summary']['incomplete_count']}`",
        "",
        "## Conflict Totals",
        "",
        f"- Compatibility conflicts: `{report['summary']['compatibility_conflict_count']}`",
        f"- Provenance conflicts: `{report['summary']['provenance_conflict_count']}`",
        f"- Continuity conflicts: `{report['summary']['continuity_conflict_count']}`",
        f"- Boundary conflicts: `{report['summary']['boundary_conflict_count']}`",
        f"- Hidden conflicts: `{report['summary']['hidden_conflict_count']}`",
        f"- Execution-boundary violation detections: `{report['summary']['execution_boundary_violation_count']}`",
        "",
        "## Deterministic Guarantees",
        "",
        f"- Compatibility report status: `{report['summary']['compatibility_report_status']}`",
        f"- Validation errors: `{report['summary']['validation_error_count']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Compatibility hash: `{report['deterministic_guarantees']['compatibility_hash']}`",
        f"- Compatibility summary hash: `{report['deterministic_guarantees']['compatibility_summary_hash']}`",
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
        "- Orchestration traversal.",
        "- Transition execution.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Runtime orchestration engines.",
        "- Runtime mutation.",
        "- Autonomous behavior.",
        "- Authorization systems.",
        "- Approval systems.",
        "- Optimization.",
        "- Recommendations.",
        "- Ranking.",
        "- Scoring.",
        "- Selection.",
        "- Callable orchestration flows.",
        "- Transition handlers.",
        "- Orchestration evaluators.",
        "- Runtime state machines.",
        "- Production execution pathways.",
        "",
        "## Non-Execution Boundaries",
        "",
        f"- Transition execution absent: `{report['non_execution_guarantees']['transition_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Orchestration traversal absent: `{report['non_execution_guarantees']['orchestration_traversal_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Runtime mutation absent: `{report['non_execution_guarantees']['runtime_mutation_absent']}`",
        f"- Authorization absent: `{report['non_execution_guarantees']['authorization_absent']}`",
        f"- Approval absent: `{report['non_execution_guarantees']['approval_absent']}`",
        f"- Report execution capability violations: `{report['non_execution_guarantees']['report_execution_capability_violation_count']}`",
        "",
        "## Generated Evidence",
        "",
        "- JSON report: `docs/generated/v3_9_transition_compatibility_intelligence_report.json`",
        "- This migration note: `docs/migration/V3_9_TRANSITION_COMPATIBILITY_INTELLIGENCE.md`",
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
