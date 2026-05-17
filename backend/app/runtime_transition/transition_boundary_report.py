"""Report builders for deterministic v3.9 transition boundary intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .transition_boundary_classifier import classify_v3_9_transition_boundaries
from .transition_boundary_models import (
    BOUNDARY_CLASSIFICATION_BLOCKED,
    BOUNDARY_CLASSIFICATION_INCOMPLETE,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_SAFE,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    export_transition_boundary_report,
)
from .transition_boundary_serialization import (
    hash_transition_boundary_report,
    validate_transition_boundary_hash_stability,
    validate_transition_boundary_serialization_stability,
)
from .transition_boundary_validation import validate_transition_boundary_report
from .transition_foundation_hashing import deterministic_hash


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"

SOURCE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/generated/v3_9_transition_foundations_report.json",
    "docs/migration/V3_9_TRANSITION_FOUNDATIONS.md",
)


def build_v3_9_transition_boundary_intelligence_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    boundary_report = classify_v3_9_transition_boundaries()
    validation = validate_transition_boundary_report(boundary_report)
    serialization = validate_transition_boundary_serialization_stability(boundary_report)
    hashing = validate_transition_boundary_hash_stability(boundary_report)
    source_artifacts = [_source_artifact_status(root, path) for path in SOURCE_ARTIFACT_PATHS]
    source_artifact_count = len(source_artifacts)
    present_source_artifact_count = sum(1 for artifact in source_artifacts if artifact["present"])
    report = {
        "schema_version": "v3_9.transition_boundary_intelligence_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.9_transition_boundary_intelligence",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic coordination transition boundary classification before deeper transition reasoning"
        ),
        "boundary_report_status": boundary_report.report_status,
        "source_foundation_id": boundary_report.source_foundation_id,
        "non_executable": boundary_report.non_executable,
        "transition_execution_enabled": boundary_report.transition_execution_enabled,
        "orchestration_execution_enabled": boundary_report.orchestration_execution_enabled,
        "graph_traversal_enabled": boundary_report.graph_traversal_enabled,
        "routing_enabled": boundary_report.routing_enabled,
        "scheduling_enabled": boundary_report.scheduling_enabled,
        "dispatch_enabled": boundary_report.dispatch_enabled,
        "runtime_orchestration_engine_enabled": boundary_report.runtime_orchestration_engine_enabled,
        "runtime_mutation_enabled": boundary_report.runtime_mutation_enabled,
        "authorization_enabled": boundary_report.authorization_enabled,
        "approval_enabled": boundary_report.approval_enabled,
        "optimization_enabled": boundary_report.optimization_enabled,
        "recommendation_enabled": boundary_report.recommendation_enabled,
        "ranking_enabled": boundary_report.ranking_enabled,
        "scoring_enabled": boundary_report.scoring_enabled,
        "selection_enabled": boundary_report.selection_enabled,
        "autonomous_behavior_enabled": boundary_report.autonomous_behavior_enabled,
        "callable_orchestration_flow_enabled": boundary_report.callable_orchestration_flow_enabled,
        "transition_handler_enabled": boundary_report.transition_handler_enabled,
        "state_machine_enabled": boundary_report.state_machine_enabled,
        "production_behavior_enabled": boundary_report.production_behavior_enabled,
        "hidden_fallback_enabled": boundary_report.hidden_fallback_enabled,
        "silent_correction_enabled": boundary_report.silent_correction_enabled,
        "source_artifacts": source_artifacts,
        "source_artifact_totals": {
            "source_artifact_count": source_artifact_count,
            "present_source_artifact_count": present_source_artifact_count,
            "missing_source_artifact_count": source_artifact_count - present_source_artifact_count,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
        "classification_counts": dict(boundary_report.classification_counts),
        "boundary_totals": {
            "boundary_input_count": validation["boundary_input_count"],
            "classification_record_count": validation["classification_record_count"],
            "finding_count": validation["finding_count"],
            "safe_transition_count": validation["safe_transition_count"],
            "unsupported_behavior_detection_count": validation["unsupported_behavior_detection_count"],
            "prohibited_behavior_detection_count": validation["prohibited_behavior_detection_count"],
            "unknown_behavior_detection_count": validation["unknown_behavior_detection_count"],
            "incomplete_behavior_detection_count": validation["incomplete_behavior_detection_count"],
            "blocked_behavior_detection_count": validation["blocked_behavior_detection_count"],
            "hidden_non_safe_state_count": validation["hidden_non_safe_state_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
        },
        "deterministic_guarantees": {
            "boundary_serialization_stable": serialization["stable"],
            "boundary_hash_stable": hashing["stable"],
            "boundary_hash": hash_transition_boundary_report(boundary_report),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_boundary_evidence_count": validation["replay_safe_boundary_evidence_count"],
            "all_findings_have_replay_evidence": validation["replay_safe_boundary_evidence_count"]
            == validation["finding_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_boundary_evidence_count": validation["rollback_safe_boundary_evidence_count"],
            "all_findings_have_rollback_evidence": validation["rollback_safe_boundary_evidence_count"]
            == validation["finding_count"],
        },
        "provenance_guarantees": {
            "provenance_safe_boundary_evidence_count": validation["provenance_safe_boundary_evidence_count"],
            "all_findings_preserve_provenance": validation["provenance_safe_boundary_evidence_count"]
            == validation["finding_count"],
        },
        "explainability_guarantees": {
            "explainability_safe_boundary_evidence_count": validation[
                "explainability_safe_boundary_evidence_count"
            ],
            "all_non_safe_states_have_explainability": validation["vague_non_safe_output_count"] == 0,
            "hidden_non_safe_state_count": validation["hidden_non_safe_state_count"],
            "non_safe_not_fail_visible_count": validation["non_safe_not_fail_visible_count"],
        },
        "non_execution_guarantees": {
            "transition_execution_absent": not boundary_report.transition_execution_enabled,
            "orchestration_execution_absent": not boundary_report.orchestration_execution_enabled,
            "graph_traversal_absent": not boundary_report.graph_traversal_enabled,
            "routing_absent": not boundary_report.routing_enabled,
            "scheduling_absent": not boundary_report.scheduling_enabled,
            "dispatch_absent": not boundary_report.dispatch_enabled,
            "runtime_orchestration_engine_absent": not boundary_report.runtime_orchestration_engine_enabled,
            "runtime_mutation_absent": not boundary_report.runtime_mutation_enabled,
            "authorization_absent": not boundary_report.authorization_enabled,
            "approval_absent": not boundary_report.approval_enabled,
            "optimization_absent": not boundary_report.optimization_enabled,
            "recommendation_absent": not boundary_report.recommendation_enabled,
            "ranking_absent": not boundary_report.ranking_enabled,
            "scoring_absent": not boundary_report.scoring_enabled,
            "selection_absent": not boundary_report.selection_enabled,
            "autonomous_behavior_absent": not boundary_report.autonomous_behavior_enabled,
            "callable_orchestration_flow_absent": not boundary_report.callable_orchestration_flow_enabled,
            "transition_handler_absent": not boundary_report.transition_handler_enabled,
            "state_machine_absent": not boundary_report.state_machine_enabled,
            "production_behavior_absent": not boundary_report.production_behavior_enabled,
            "hidden_fallback_absent": not boundary_report.hidden_fallback_enabled,
            "silent_correction_absent": not boundary_report.silent_correction_enabled,
            "report_execution_capability_violation_count": validation[
                "report_execution_capability_violation_count"
            ],
        },
        "classification_semantics": {
            BOUNDARY_CLASSIFICATION_SAFE: "all required deterministic references exist and no non-safe markers are present",
            BOUNDARY_CLASSIFICATION_UNSUPPORTED: "known transition state or domain is outside modeled support",
            BOUNDARY_CLASSIFICATION_PROHIBITED: "requested behavior is prohibited by non-execution boundaries",
            BOUNDARY_CLASSIFICATION_UNKNOWN: "transition intent or semantics cannot be deterministically interpreted",
            BOUNDARY_CLASSIFICATION_INCOMPLETE: "required identity, state, provenance, continuity, or evidence reference is missing",
            BOUNDARY_CLASSIFICATION_BLOCKED: "governance, boundary policy, or integrity precondition blocks the transition",
        },
        "boundary_report": export_transition_boundary_report(boundary_report),
        "explicit_limitations": [
            "v3.9 Phase 2 transition boundary intelligence is non-executable",
            "v3.9 Phase 2 does not enable orchestration execution",
            "v3.9 Phase 2 does not enable transition execution",
            "v3.9 Phase 2 does not enable graph traversal",
            "v3.9 Phase 2 does not enable routing, scheduling, or dispatch",
            "v3.9 Phase 2 does not enable runtime orchestration engines",
            "v3.9 Phase 2 does not enable runtime mutation",
            "v3.9 Phase 2 does not enable authorization or approval systems",
            "v3.9 Phase 2 does not enable optimization or recommendations",
            "v3.9 Phase 2 does not enable ranking, scoring, or selection",
            "v3.9 Phase 2 does not enable autonomous behavior",
            "v3.9 Phase 2 does not enable callable orchestration flows",
            "v3.9 Phase 2 does not enable transition handlers or state machines",
            "v3.9 Phase 2 does not enable production behavior",
        ],
        "summary": {
            "boundary_report_status": boundary_report.report_status,
            "validation_error_count": validation["validation_error_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "safe_transition_count": validation["safe_transition_count"],
            "unsupported_behavior_detection_count": validation["unsupported_behavior_detection_count"],
            "prohibited_behavior_detection_count": validation["prohibited_behavior_detection_count"],
            "unknown_behavior_detection_count": validation["unknown_behavior_detection_count"],
            "incomplete_behavior_detection_count": validation["incomplete_behavior_detection_count"],
            "blocked_behavior_detection_count": validation["blocked_behavior_detection_count"],
            "hidden_non_safe_state_count": validation["hidden_non_safe_state_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
            "report_execution_capability_violation_count": validation[
                "report_execution_capability_violation_count"
            ],
            "replay_verified": validation["replay_safe_boundary_evidence_count"] == validation["finding_count"],
            "rollback_verified": validation["rollback_safe_boundary_evidence_count"] == validation["finding_count"],
            "provenance_verified": validation["provenance_safe_boundary_evidence_count"]
            == validation["finding_count"],
            "explainability_verified": validation["vague_non_safe_output_count"] == 0,
            "non_executable_verified": boundary_report.non_executable,
            "orchestration_boundaries_enforced": validation["report_execution_capability_violation_count"] == 0,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_transition_boundary_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.9 Transition Boundary Intelligence",
        "",
        "## What Phase 2 Added",
        "",
        "v3.9 Phase 2 adds deterministic coordination transition boundary intelligence on top of the Phase 1 transition foundations.",
        "",
        "It classifies transition boundary inputs as `safe`, `unsupported`, `prohibited`, `unknown`, `incomplete`, or `blocked` before deeper transition reasoning exists.",
        "",
        "This phase does NOT enable orchestration execution, routing, scheduling, dispatch, traversal, optimization, recommendation, ranking, scoring, selection, authorization, or runtime mutation.",
        "",
        "## How Boundary Classification Works",
        "",
        "- `safe` requires source state, destination state, transition identity, provenance references, continuity references, evidence references, and no non-safe markers.",
        "- `unsupported` records known domains, states, or capabilities outside modeled support.",
        "- `prohibited` records requested behavior that violates hard non-execution boundaries.",
        "- `unknown` records transition intents or semantics that cannot be deterministically interpreted.",
        "- `incomplete` records missing source, destination, identity, provenance, continuity, or evidence references.",
        "- `blocked` records governance, boundary policy, or integrity precondition blockers.",
        "",
        "## Why Non-Safe States Are Fail-Visible",
        "",
        "Every non-safe finding carries a visible reason, deterministic evidence reference, provenance reference, continuity reference, and explainability message.",
        "",
        "No non-safe finding is hidden, silently corrected, or converted into a safe classification.",
        "",
        "## Boundary Totals",
        "",
        f"- Safe transitions: `{report['summary']['safe_transition_count']}`",
        f"- Unsupported detections: `{report['summary']['unsupported_behavior_detection_count']}`",
        f"- Prohibited detections: `{report['summary']['prohibited_behavior_detection_count']}`",
        f"- Unknown detections: `{report['summary']['unknown_behavior_detection_count']}`",
        f"- Incomplete detections: `{report['summary']['incomplete_behavior_detection_count']}`",
        f"- Blocked detections: `{report['summary']['blocked_behavior_detection_count']}`",
        f"- Hidden non-safe states: `{report['summary']['hidden_non_safe_state_count']}`",
        f"- Execution-boundary violation detections: `{report['summary']['execution_boundary_violation_count']}`",
        "",
        "## Deterministic Guarantees",
        "",
        f"- Boundary report status: `{report['summary']['boundary_report_status']}`",
        f"- Validation errors: `{report['summary']['validation_error_count']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Boundary hash: `{report['deterministic_guarantees']['boundary_hash']}`",
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
        "- State machines.",
        "- Production behavior.",
        "",
        "## Non-Execution Boundaries",
        "",
        f"- Transition execution absent: `{report['non_execution_guarantees']['transition_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Graph traversal absent: `{report['non_execution_guarantees']['graph_traversal_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Runtime mutation absent: `{report['non_execution_guarantees']['runtime_mutation_absent']}`",
        f"- Authorization absent: `{report['non_execution_guarantees']['authorization_absent']}`",
        f"- Report execution capability violations: `{report['non_execution_guarantees']['report_execution_capability_violation_count']}`",
        "",
        "## Generated Evidence",
        "",
        "- JSON report: `docs/generated/v3_9_transition_boundary_intelligence_report.json`",
        "- This migration note: `docs/migration/V3_9_TRANSITION_BOUNDARY_INTELLIGENCE.md`",
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
