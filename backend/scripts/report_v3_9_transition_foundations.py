"""Generate the v3.9 transition foundations report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_transition.transition_foundation_hashing import (  # noqa: E402
    deterministic_hash,
    hash_v3_9_transition_foundation,
)
from runtime_transition.transition_foundation_models import (  # noqa: E402
    TRANSITION_CLASSIFICATIONS,
    default_v3_9_transition_foundation,
    export_v3_9_transition_foundation,
)
from runtime_transition.transition_foundation_validation import (  # noqa: E402
    validate_v3_9_transition_foundation_guarantees,
    validate_v3_9_transition_hash_stability,
    validate_v3_9_transition_serialization_stability,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"

SOURCE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/generated/v3_8_closeout_and_v3_9_readiness_report.json",
    "docs/generated/v3_8_coordination_foundations_report.json",
    "docs/generated/v3_8_coordination_integrity_enforcement_report.json",
    "docs/generated/v3_8_coordination_continuity_certification_report.json",
)


def build_v3_9_transition_foundations_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    foundation = default_v3_9_transition_foundation()
    validation = validate_v3_9_transition_foundation_guarantees(foundation)
    serialization = validate_v3_9_transition_serialization_stability(foundation)
    hashing = validate_v3_9_transition_hash_stability(foundation)
    source_artifacts = [_source_artifact_status(root, path) for path in SOURCE_ARTIFACT_PATHS]
    source_artifact_count = len(source_artifacts)
    present_source_artifact_count = sum(1 for artifact in source_artifacts if artifact["present"])
    report = {
        "schema_version": "v3_9.transition_foundations_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.9_transition_foundations",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic orchestration-planning coordination transition intelligence foundations"
        ),
        "foundation_status": validation["validation_status"],
        "foundation_is_non_executable": foundation.non_executable,
        "foundation_models_transition_intelligence_only": foundation.transition_modeling_only,
        "coordination_transition_execution_enabled": foundation.coordination_transition_execution_enabled,
        "orchestration_execution_enabled": foundation.orchestration_execution_enabled,
        "orchestration_traversal_enabled": foundation.orchestration_traversal_enabled,
        "routing_enabled": foundation.routing_enabled,
        "scheduling_enabled": foundation.scheduling_enabled,
        "dispatch_enabled": foundation.dispatch_enabled,
        "runtime_orchestration_engine_enabled": foundation.runtime_orchestration_engine_enabled,
        "runtime_state_machine_enabled": foundation.runtime_state_machine_enabled,
        "transition_execution_handler_enabled": foundation.transition_execution_handler_enabled,
        "dispatch_pipeline_enabled": foundation.dispatch_pipeline_enabled,
        "orchestration_evaluator_enabled": foundation.orchestration_evaluator_enabled,
        "optimization_enabled": foundation.optimization_enabled,
        "recommendation_enabled": foundation.recommendation_enabled,
        "ranking_enabled": foundation.ranking_enabled,
        "scoring_enabled": foundation.scoring_enabled,
        "selection_enabled": foundation.selection_enabled,
        "authorization_enabled": foundation.authorization_enabled,
        "autonomous_orchestration_enabled": foundation.autonomous_orchestration_enabled,
        "hidden_mutation_enabled": foundation.hidden_mutation_enabled,
        "runtime_mutation_enabled": foundation.runtime_mutation_enabled,
        "implicit_transition_approval_enabled": foundation.implicit_transition_approval_enabled,
        "silent_fallback_enabled": foundation.silent_fallback_enabled,
        "hidden_correction_enabled": foundation.hidden_correction_enabled,
        "inferred_orchestration_action_enabled": foundation.inferred_orchestration_action_enabled,
        "production_execution_pathway_enabled": foundation.production_execution_pathway_enabled,
        "callable_orchestration_flow_enabled": foundation.callable_orchestration_flow_enabled,
        "source_artifacts": source_artifacts,
        "source_artifact_totals": {
            "source_artifact_count": source_artifact_count,
            "present_source_artifact_count": present_source_artifact_count,
            "missing_source_artifact_count": source_artifact_count - present_source_artifact_count,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
        "validation_totals": validation,
        "deterministic_guarantees": {
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "deterministic_foundation_hash": hash_v3_9_transition_foundation(foundation),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "identity_guarantees": {
            "stable_transition_identity": foundation.identity.transition_id,
            "schema_version": foundation.identity.schema_version,
            "phase_id": foundation.identity.phase_id,
            "deterministic_equality_preserved": foundation == default_v3_9_transition_foundation(),
        },
        "state_classification_guarantees": {
            "allowed_classifications": list(TRANSITION_CLASSIFICATIONS),
            "supported_state_count": validation["supported_state_count"],
            "unsupported_state_count": validation["unsupported_state_count"],
            "prohibited_state_count": validation["prohibited_state_count"],
            "unknown_state_count": validation["unknown_state_count"],
            "incomplete_state_count": validation["incomplete_state_count"],
            "blocked_state_count": validation["blocked_state_count"],
            "fail_visible_non_ready_state_count": validation["fail_visible_non_ready_state_count"],
            "hidden_non_ready_state_count": validation["hidden_non_ready_state_count"],
            "invalid_transition_state_count": validation["invalid_transition_state_count"],
        },
        "provenance_guarantees": {
            "provenance_preserved": validation["provenance_preserved"],
            "provenance_reference_count": validation["provenance_reference_count"],
            "missing_provenance_reference_count": validation["missing_provenance_reference_count"],
            "invalid_provenance_reference_count": validation["invalid_provenance_reference_count"],
            "no_inferred_provenance": validation["no_inferred_provenance"],
        },
        "continuity_guarantees": {
            "continuity_preserved": validation["continuity_preserved"],
            "continuity_reference_count": validation["continuity_reference_count"],
            "continuity_chain_count": validation["continuity_chain_count"],
            "invalid_continuity_reference_count": validation["invalid_continuity_reference_count"],
            "invalid_continuity_chain_count": validation["invalid_continuity_chain_count"],
            "immutable_continuity_chains": validation["immutable_continuity_chains"],
        },
        "replay_guarantees": {
            "replay_safe": validation["replay_safe"],
            "runtime_replay_enabled": any(
                reference.runtime_replay_enabled for reference in foundation.continuity_references
            ),
        },
        "rollback_guarantees": {
            "rollback_safe": validation["rollback_safe"],
            "rollback_execution_enabled": any(
                reference.rollback_execution_enabled for reference in foundation.continuity_references
            ),
        },
        "evidence_guarantees": {
            "evidence_record_count": validation["evidence_record_count"],
            "immutable_evidence_records": validation["immutable_evidence_records"],
            "incomplete_evidence_reference_count": validation["incomplete_evidence_reference_count"],
        },
        "non_execution_guarantees": {
            "coordination_transition_execution_absent": not foundation.coordination_transition_execution_enabled,
            "orchestration_execution_absent": not foundation.orchestration_execution_enabled,
            "orchestration_traversal_absent": not foundation.orchestration_traversal_enabled,
            "routing_absent": not foundation.routing_enabled,
            "scheduling_absent": not foundation.scheduling_enabled,
            "dispatch_absent": not foundation.dispatch_enabled,
            "runtime_orchestration_engine_absent": not foundation.runtime_orchestration_engine_enabled,
            "runtime_state_machine_absent": not foundation.runtime_state_machine_enabled,
            "transition_execution_handler_absent": not foundation.transition_execution_handler_enabled,
            "dispatch_pipeline_absent": not foundation.dispatch_pipeline_enabled,
            "orchestration_evaluator_absent": not foundation.orchestration_evaluator_enabled,
            "optimization_absent": not foundation.optimization_enabled,
            "recommendation_absent": not foundation.recommendation_enabled,
            "ranking_absent": not foundation.ranking_enabled,
            "scoring_absent": not foundation.scoring_enabled,
            "selection_absent": not foundation.selection_enabled,
            "authorization_absent": not foundation.authorization_enabled,
            "autonomous_orchestration_absent": not foundation.autonomous_orchestration_enabled,
            "hidden_mutation_absent": not foundation.hidden_mutation_enabled,
            "runtime_mutation_absent": not foundation.runtime_mutation_enabled,
            "implicit_transition_approval_absent": not foundation.implicit_transition_approval_enabled,
            "silent_fallback_absent": not foundation.silent_fallback_enabled,
            "hidden_correction_absent": not foundation.hidden_correction_enabled,
            "inferred_orchestration_action_absent": not foundation.inferred_orchestration_action_enabled,
            "production_execution_pathway_absent": not foundation.production_execution_pathway_enabled,
            "callable_orchestration_flow_absent": not foundation.callable_orchestration_flow_enabled,
        },
        "transition_foundation": export_v3_9_transition_foundation(foundation),
        "explicit_limitations": [
            "v3.9 Phase 1 transition foundations are non-executable",
            "v3.9 Phase 1 does not enable orchestration execution",
            "v3.9 Phase 1 does not enable orchestration traversal",
            "v3.9 Phase 1 does not enable routing, scheduling, or dispatch",
            "v3.9 Phase 1 does not enable runtime orchestration engines",
            "v3.9 Phase 1 does not enable transition execution handlers",
            "v3.9 Phase 1 does not enable optimization or recommendation systems",
            "v3.9 Phase 1 does not enable ranking, scoring, or selection",
            "v3.9 Phase 1 does not enable authorization",
            "v3.9 Phase 1 does not enable runtime mutation",
            "v3.9 Phase 1 does not enable implicit transition approval",
            "v3.9 Phase 1 does not enable hidden correction or silent fallback behavior",
            "v3.9 Phase 1 does not enable production execution pathways",
        ],
        "summary": {
            "foundation_status": validation["validation_status"],
            "validation_error_count": validation["validation_error_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "transition_reference_count": validation["transition_reference_count"],
            "state_reference_count": validation["state_reference_count"],
            "provenance_reference_count": validation["provenance_reference_count"],
            "continuity_reference_count": validation["continuity_reference_count"],
            "continuity_chain_count": validation["continuity_chain_count"],
            "evidence_record_count": validation["evidence_record_count"],
            "fail_visible_non_ready_state_count": validation["fail_visible_non_ready_state_count"],
            "hidden_non_ready_state_count": validation["hidden_non_ready_state_count"],
            "invalid_transition_state_count": validation["invalid_transition_state_count"],
            "missing_provenance_reference_count": validation["missing_provenance_reference_count"],
            "invalid_continuity_chain_count": validation["invalid_continuity_chain_count"],
            "incomplete_evidence_reference_count": validation["incomplete_evidence_reference_count"],
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
            "continuity_verified": validation["continuity_preserved"],
            "provenance_verified": validation["provenance_preserved"],
            "replay_verified": validation["replay_safe"],
            "rollback_verified": validation["rollback_safe"],
            "immutable_evidence_records": validation["immutable_evidence_records"],
            "non_executable_verified": foundation.non_executable,
            "orchestration_boundaries_enforced": validation["execution_boundary_violation_count"] == 0,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.9 Transition Foundations",
        "",
        "## What v3.9 Phase 1 Establishes",
        "",
        "v3.9 Phase 1 establishes deterministic orchestration-planning coordination transition intelligence foundations.",
        "",
        "It introduces immutable transition identities, transition references, state classification references, provenance references, continuity references, continuity chains, evidence records, deterministic serialization, deterministic hashing, and fail-visible validation evidence.",
        "",
        "This phase does NOT enable orchestration execution.",
        "",
        "## Deterministic Guarantees",
        "",
        f"- Foundation status: `{report['summary']['foundation_status']}`",
        f"- Validation errors: `{report['summary']['validation_error_count']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Deterministic foundation hash: `{report['deterministic_guarantees']['deterministic_foundation_hash']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Provenance Guarantees",
        "",
        f"- Provenance preserved: `{report['provenance_guarantees']['provenance_preserved']}`",
        f"- Provenance references: `{report['provenance_guarantees']['provenance_reference_count']}`",
        f"- Missing provenance references: `{report['provenance_guarantees']['missing_provenance_reference_count']}`",
        f"- Invalid provenance references: `{report['provenance_guarantees']['invalid_provenance_reference_count']}`",
        f"- Inferred provenance allowed: `{not report['provenance_guarantees']['no_inferred_provenance']}`",
        "",
        "## Continuity Guarantees",
        "",
        f"- Continuity preserved: `{report['continuity_guarantees']['continuity_preserved']}`",
        f"- Continuity references: `{report['continuity_guarantees']['continuity_reference_count']}`",
        f"- Continuity chains: `{report['continuity_guarantees']['continuity_chain_count']}`",
        f"- Invalid continuity references: `{report['continuity_guarantees']['invalid_continuity_reference_count']}`",
        f"- Invalid continuity chains: `{report['continuity_guarantees']['invalid_continuity_chain_count']}`",
        f"- Immutable continuity chains: `{report['continuity_guarantees']['immutable_continuity_chains']}`",
        "",
        "## Replay Rollback And Evidence",
        "",
        f"- Replay safe: `{report['replay_guarantees']['replay_safe']}`",
        f"- Runtime replay enabled: `{report['replay_guarantees']['runtime_replay_enabled']}`",
        f"- Rollback safe: `{report['rollback_guarantees']['rollback_safe']}`",
        f"- Rollback execution enabled: `{report['rollback_guarantees']['rollback_execution_enabled']}`",
        f"- Evidence records: `{report['evidence_guarantees']['evidence_record_count']}`",
        f"- Immutable evidence records: `{report['evidence_guarantees']['immutable_evidence_records']}`",
        "",
        "## Fail-Visible Classification",
        "",
        f"- Supported states: `{report['state_classification_guarantees']['supported_state_count']}`",
        f"- Unsupported states: `{report['state_classification_guarantees']['unsupported_state_count']}`",
        f"- Prohibited states: `{report['state_classification_guarantees']['prohibited_state_count']}`",
        f"- Unknown states: `{report['state_classification_guarantees']['unknown_state_count']}`",
        f"- Incomplete states: `{report['state_classification_guarantees']['incomplete_state_count']}`",
        f"- Blocked states: `{report['state_classification_guarantees']['blocked_state_count']}`",
        f"- Fail-visible non-ready states: `{report['state_classification_guarantees']['fail_visible_non_ready_state_count']}`",
        f"- Hidden non-ready states: `{report['state_classification_guarantees']['hidden_non_ready_state_count']}`",
        f"- Invalid transition states: `{report['state_classification_guarantees']['invalid_transition_state_count']}`",
        "",
        "## What Remains Prohibited",
        "",
        "- Orchestration execution.",
        "- Orchestration traversal.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Runtime orchestration engines.",
        "- Runtime state machines.",
        "- Transition execution handlers.",
        "- Dispatch pipelines.",
        "- Orchestration evaluators.",
        "- Optimization systems.",
        "- Recommendation systems.",
        "- Ranking systems.",
        "- Scoring systems.",
        "- Selection systems.",
        "- Authorization systems.",
        "- Autonomous orchestration behavior.",
        "- Hidden mutation behavior.",
        "- Runtime mutation.",
        "- Implicit transition approval.",
        "- Silent fallback behavior.",
        "- Hidden correction behavior.",
        "- Inferred orchestration actions.",
        "- Production execution pathways.",
        "- Callable orchestration flows.",
        "",
        "## Non-Execution Guarantees",
        "",
        f"- Coordination transition execution absent: `{report['non_execution_guarantees']['coordination_transition_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Runtime orchestration engine absent: `{report['non_execution_guarantees']['runtime_orchestration_engine_absent']}`",
        f"- Runtime mutation absent: `{report['non_execution_guarantees']['runtime_mutation_absent']}`",
        f"- Callable orchestration flow absent: `{report['non_execution_guarantees']['callable_orchestration_flow_absent']}`",
        f"- Execution-boundary violations: `{report['summary']['execution_boundary_violation_count']}`",
        "",
        "## Generated Evidence",
        "",
        "- JSON report: `docs/generated/v3_9_transition_foundations_report.json`",
        "- This migration note: `docs/migration/V3_9_TRANSITION_FOUNDATIONS.md`",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "generated"
        / "v3_9_transition_foundations_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_9_TRANSITION_FOUNDATIONS.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_9_transition_foundations_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
