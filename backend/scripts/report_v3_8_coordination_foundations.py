"""Generate the v3.8 coordination foundations audit report."""

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

from runtime_coordination.coordination_foundation_models import (  # noqa: E402
    default_v3_8_coordination_foundation,
    deterministic_hash,
    export_v3_8_coordination_foundation,
    hash_v3_8_coordination_foundation,
    validate_v3_8_coordination_foundation_guarantees,
    validate_v3_8_coordination_hash_stability,
    validate_v3_8_coordination_serialization_stability,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"

SOURCE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/generated/v3_7_closeout_and_v3_8_readiness_report.json",
    "docs/generated/v3_7_graph_planning_continuity_certification_report.json",
    "docs/generated/v3_7_graph_planning_integrity_enforcement_report.json",
    "docs/generated/v3_7_graph_planning_intelligence_aggregation_report.json",
)


def build_v3_8_coordination_foundations_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    foundation = default_v3_8_coordination_foundation()
    serialization = validate_v3_8_coordination_serialization_stability(foundation)
    hashing = validate_v3_8_coordination_hash_stability(foundation)
    validation = validate_v3_8_coordination_foundation_guarantees(foundation)
    source_artifacts = [_source_artifact_status(root, relative_path) for relative_path in SOURCE_ARTIFACT_PATHS]
    source_artifact_count = len(source_artifacts)
    present_source_artifact_count = sum(1 for artifact in source_artifacts if artifact["present"])
    report = {
        "schema_version": "v3_8.coordination_foundations_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_foundations",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic orchestration-planning coordination foundation intelligence"
        ),
        "foundation_status": validation["validation_status"],
        "foundation_is_non_executable": foundation.non_executable,
        "foundation_models_planning_coordination_only": foundation.planning_coordination_only,
        "coordination_execution_enabled": foundation.coordination_execution_enabled,
        "orchestration_execution_enabled": foundation.orchestration_execution_enabled,
        "execution_authorization_enabled": foundation.execution_authorization_enabled,
        "routing_enabled": foundation.routing_enabled,
        "scheduling_enabled": foundation.scheduling_enabled,
        "dispatch_enabled": foundation.dispatch_enabled,
        "traversal_execution_enabled": foundation.traversal_execution_enabled,
        "graph_traversal_execution_enabled": foundation.graph_traversal_execution_enabled,
        "runtime_path_selection_enabled": foundation.runtime_path_selection_enabled,
        "recommendation_enabled": foundation.recommendation_enabled,
        "optimization_enabled": foundation.optimization_enabled,
        "autonomous_orchestration_enabled": foundation.autonomous_orchestration_enabled,
        "callable_execution_flow_enabled": foundation.callable_execution_flow_enabled,
        "persistent_runtime_mutation_enabled": foundation.persistent_runtime_mutation_enabled,
        "persistent_runtime_writes_enabled": foundation.persistent_runtime_writes_enabled,
        "hidden_state_transition_enabled": foundation.hidden_state_transition_enabled,
        "silent_fallback_enabled": foundation.silent_fallback_enabled,
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
            "deterministic_foundation_hash": hash_v3_8_coordination_foundation(foundation),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "identity_guarantees": {
            "stable_identity": foundation.identity.coordination_id,
            "schema_version": foundation.identity.schema_version,
            "phase_id": foundation.identity.phase_id,
            "deterministic_equality_preserved": foundation == default_v3_8_coordination_foundation(),
        },
        "continuity_guarantees": {
            "continuity_status": foundation.continuity_state.continuity_status,
            "continuity_preserved": foundation.continuity_state.continuity_preserved,
            "continuity_reference_count": len(foundation.continuity_state.preserved_reference_ids),
            "relationship_chain_count": len(foundation.relationship_chains),
            "relationship_count": len(foundation.relationships),
        },
        "provenance_guarantees": {
            "provenance_status": foundation.provenance_state.provenance_status,
            "provenance_preserved": foundation.provenance_state.provenance_preserved,
            "lineage_reference_count": len(foundation.provenance_state.lineage_reference_ids),
            "prior_phase_reference_count": len(foundation.provenance_state.prior_phase_reference_ids),
        },
        "replay_guarantees": {
            "replay_safe": validation["replay_safe"],
            "replay_evidence_count": len(foundation.replay_evidence),
            "runtime_replay_enabled": any(evidence.runtime_replay_enabled for evidence in foundation.replay_evidence),
        },
        "rollback_guarantees": {
            "rollback_safe": validation["rollback_safe"],
            "rollback_evidence_count": len(foundation.rollback_evidence),
            "rollback_execution_enabled": any(
                evidence.rollback_execution_enabled for evidence in foundation.rollback_evidence
            ),
        },
        "explainability_guarantees": {
            "explainability_status": foundation.explainability_state.explainability_status,
            "fail_visible": foundation.explainability_state.fail_visible,
            "hidden_state": foundation.explainability_state.hidden_state,
            "unsupported_state_count": len(foundation.unsupported_states),
            "prohibited_state_count": len(foundation.prohibited_states),
            "unknown_state_count": len(foundation.unknown_states),
            "fail_visible_state_count": validation["fail_visible_state_count"],
        },
        "integrity_guarantees": {
            "integrity_status": foundation.integrity_state.integrity_status,
            "integrity_preserved": foundation.integrity_state.integrity_preserved,
            "execution_boundary_violation_count": validation["execution_boundary_violation_count"],
            "relationship_execution_violation_count": validation["relationship_execution_violation_count"],
            "chain_execution_violation_count": validation["chain_execution_violation_count"],
            "hidden_transition_detected": validation["hidden_transition_detected"],
            "silent_fallback_detected": validation["silent_fallback_detected"],
        },
        "non_execution_guarantees": {
            "coordination_execution_absent": not foundation.coordination_execution_enabled,
            "orchestration_execution_absent": not foundation.orchestration_execution_enabled,
            "execution_authorization_absent": not foundation.execution_authorization_enabled,
            "routing_absent": not foundation.routing_enabled,
            "scheduling_absent": not foundation.scheduling_enabled,
            "dispatch_absent": not foundation.dispatch_enabled,
            "traversal_execution_absent": not foundation.traversal_execution_enabled,
            "graph_traversal_execution_absent": not foundation.graph_traversal_execution_enabled,
            "runtime_path_selection_absent": not foundation.runtime_path_selection_enabled,
            "recommendation_absent": not foundation.recommendation_enabled,
            "optimization_absent": not foundation.optimization_enabled,
            "autonomous_orchestration_absent": not foundation.autonomous_orchestration_enabled,
            "callable_execution_flow_absent": not foundation.callable_execution_flow_enabled,
            "persistent_runtime_mutation_absent": not foundation.persistent_runtime_mutation_enabled,
            "persistent_runtime_writes_absent": not foundation.persistent_runtime_writes_enabled,
            "hidden_state_transition_absent": not foundation.hidden_state_transition_enabled,
            "silent_fallback_absent": not foundation.silent_fallback_enabled,
        },
        "coordination_foundation": export_v3_8_coordination_foundation(foundation),
        "explicit_limitations": [
            "v3.8 coordination foundations are non-executable",
            "v3.8 does not enable orchestration execution",
            "v3.8 does not enable orchestration routing",
            "v3.8 does not enable orchestration scheduling",
            "v3.8 does not enable orchestration dispatch",
            "v3.8 does not enable graph traversal execution",
            "v3.8 does not enable orchestration optimization",
            "v3.8 does not enable recommendation systems",
            "v3.8 does not enable execution authorization",
            "v3.8 does not introduce persistent runtime mutation",
        ],
        "summary": {
            "foundation_status": validation["validation_status"],
            "validation_error_count": validation["validation_error_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "continuity_verified": foundation.continuity_state.continuity_preserved,
            "provenance_verified": foundation.provenance_state.provenance_preserved,
            "replay_verified": validation["replay_safe"],
            "rollback_verified": validation["rollback_safe"],
            "explainability_verified": foundation.explainability_state.fail_visible
            and not foundation.explainability_state.hidden_state,
            "integrity_verified": foundation.integrity_state.integrity_preserved,
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
        "# v3.8 Coordination Foundations",
        "",
        "## Architectural Purpose",
        "",
        "v3.8 establishes deterministic orchestration-planning coordination foundation intelligence.",
        "",
        "The foundation layer models coordination identity, references, boundaries, relationships, continuity, provenance, explainability, integrity, replay evidence, and rollback evidence.",
        "",
        "This phase is NON-executable.",
        "",
        "This phase does NOT enable orchestration execution, routing, scheduling, dispatch, traversal execution, optimization, recommendation, execution authorization, runtime mutation, or callable execution flows.",
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
        "## Continuity Guarantees",
        "",
        f"- Continuity preserved: `{report['continuity_guarantees']['continuity_preserved']}`",
        f"- Continuity references: `{report['continuity_guarantees']['continuity_reference_count']}`",
        f"- Relationship chains: `{report['continuity_guarantees']['relationship_chain_count']}`",
        f"- Relationships: `{report['continuity_guarantees']['relationship_count']}`",
        f"- Source artifact continuity preserved: `{report['source_artifact_totals']['source_artifact_continuity_preserved']}`",
        "",
        "## Provenance Guarantees",
        "",
        f"- Provenance preserved: `{report['provenance_guarantees']['provenance_preserved']}`",
        f"- Lineage references: `{report['provenance_guarantees']['lineage_reference_count']}`",
        f"- Prior phase references: `{report['provenance_guarantees']['prior_phase_reference_count']}`",
        "",
        "## Explainability Guarantees",
        "",
        f"- Explainability fail-visible: `{report['explainability_guarantees']['fail_visible']}`",
        f"- Hidden explainability state: `{report['explainability_guarantees']['hidden_state']}`",
        f"- Unsupported states: `{report['explainability_guarantees']['unsupported_state_count']}`",
        f"- Prohibited states: `{report['explainability_guarantees']['prohibited_state_count']}`",
        f"- Unknown states: `{report['explainability_guarantees']['unknown_state_count']}`",
        f"- Fail-visible states: `{report['explainability_guarantees']['fail_visible_state_count']}`",
        "",
        "## Integrity Guarantees",
        "",
        f"- Integrity preserved: `{report['integrity_guarantees']['integrity_preserved']}`",
        f"- Execution-boundary violations: `{report['integrity_guarantees']['execution_boundary_violation_count']}`",
        f"- Relationship execution violations: `{report['integrity_guarantees']['relationship_execution_violation_count']}`",
        f"- Chain execution violations: `{report['integrity_guarantees']['chain_execution_violation_count']}`",
        f"- Hidden transitions detected: `{report['integrity_guarantees']['hidden_transition_detected']}`",
        f"- Silent fallback detected: `{report['integrity_guarantees']['silent_fallback_detected']}`",
        "",
        "## Replay And Rollback Guarantees",
        "",
        f"- Replay safe: `{report['replay_guarantees']['replay_safe']}`",
        f"- Replay evidence count: `{report['replay_guarantees']['replay_evidence_count']}`",
        f"- Runtime replay enabled: `{report['replay_guarantees']['runtime_replay_enabled']}`",
        f"- Rollback safe: `{report['rollback_guarantees']['rollback_safe']}`",
        f"- Rollback evidence count: `{report['rollback_guarantees']['rollback_evidence_count']}`",
        f"- Rollback execution enabled: `{report['rollback_guarantees']['rollback_execution_enabled']}`",
        "",
        "## Prohibited Behaviors",
        "",
        "- Orchestration execution remains prohibited.",
        "- Runtime execution engines remain prohibited.",
        "- Graph traversal execution remains prohibited.",
        "- Orchestration dispatch remains prohibited.",
        "- Orchestration routing remains prohibited.",
        "- Orchestration scheduling remains prohibited.",
        "- Orchestration optimization remains prohibited.",
        "- Recommendation systems remain prohibited.",
        "- Autonomous orchestration remains prohibited.",
        "- Execution authorization remains prohibited.",
        "- Persistent runtime mutation remains prohibited.",
        "- Callable execution flows remain prohibited.",
        "- Hidden state transitions and silent fallback behavior remain prohibited.",
        "",
        "## Non-Execution Boundaries",
        "",
        f"- Coordination execution absent: `{report['non_execution_guarantees']['coordination_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Traversal execution absent: `{report['non_execution_guarantees']['traversal_execution_absent']}`",
        f"- Execution authorization absent: `{report['non_execution_guarantees']['execution_authorization_absent']}`",
        f"- Callable execution flow absent: `{report['non_execution_guarantees']['callable_execution_flow_absent']}`",
        "",
        "## Generated Evidence",
        "",
        "- JSON report: `docs/generated/v3_8_coordination_foundations_report.json`",
        "- This migration note: `docs/migration/V3_8_COORDINATION_FOUNDATIONS.md`",
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
        / "v3_8_coordination_foundations_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_FOUNDATIONS.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_foundations_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
