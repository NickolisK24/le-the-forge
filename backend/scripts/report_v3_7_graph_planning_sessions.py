"""Generate the v3.7 graph planning sessions report."""

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
from app.runtime_orchestration.v3_7_graph_planning_session_audit import (  # noqa: E402
    V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE,
    audit_v3_7_graph_planning_session,
    export_v3_7_graph_planning_session_audit_result,
)
from app.runtime_orchestration.v3_7_graph_planning_session_explainability import (  # noqa: E402
    V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_planning_session,
    export_v3_7_graph_planning_session_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_planning_session_models import (  # noqa: E402
    V37_GRAPH_PLANNING_SESSION_STATUSES,
    V37_SESSION_STATUS_BLOCKED,
    V37_SESSION_STATUS_PROHIBITED,
    V37_SESSION_STATUS_UNKNOWN,
    V37_SESSION_STATUS_UNSUPPORTED,
    export_v3_7_graph_planning_session,
    export_v3_7_graph_planning_session_counts,
    hash_v3_7_graph_planning_session,
    validate_v3_7_graph_planning_session_hash_stability,
    validate_v3_7_graph_planning_session_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_planning_session_provenance import (  # noqa: E402
    V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_planning_session_provenance,
    export_v3_7_graph_planning_session_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_planning_session_replay import (  # noqa: E402
    export_v3_7_graph_planning_session_replay_evidence_records,
    validate_v3_7_graph_planning_session_replay_evidence,
)
from app.runtime_orchestration.v3_7_graph_planning_session_snapshots import (  # noqa: E402
    build_v3_7_graph_planning_session,
)
from app.runtime_orchestration.v3_7_graph_planning_session_validation import (  # noqa: E402
    V37_GRAPH_PLANNING_SESSION_VALIDATION_STABLE,
    export_v3_7_graph_planning_session_validation_result,
    validate_v3_7_graph_planning_sessions,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_planning_sessions_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    session = build_v3_7_graph_planning_session()
    validation = validate_v3_7_graph_planning_sessions((session,))
    audit = audit_v3_7_graph_planning_session(session)
    provenance = audit_v3_7_graph_planning_session_provenance(session)
    explainability = explain_v3_7_graph_planning_session(session)
    replay = validate_v3_7_graph_planning_session_replay_evidence(session)
    serialization = validate_v3_7_graph_planning_session_serialization_stability(session)
    hashing = validate_v3_7_graph_planning_session_hash_stability(session)
    report = {
        "schema_version": "v3_7.graph_planning_sessions_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_graph_planning_sessions",
        "repo_root": str(root),
        "architectural_purpose": "deterministic graph planning session intelligence",
        "planning_session_evidence": True,
        "runtime_orchestration_session_state": False,
        "planning_sessions_are_non_executable": True,
        "planning_sessions_are_evidence_containers_only": True,
        "session_replay_evidence_is_not_runtime_replay": True,
        "snapshots_do_not_imply_execution_state": True,
        "audit_trails_do_not_imply_runtime_history": True,
        "session_statuses_do_not_authorize_orchestration": True,
        "graph_planning_sessions_do_not_enable_routing_scheduling_dispatch": True,
        "graph_execution_enabled": False,
        "session_execution_enabled": False,
        "runtime_orchestration_enabled": False,
        "routing_enabled": False,
        "scheduling_enabled": False,
        "dispatch_enabled": False,
        "graph_traversal_execution_enabled": False,
        "path_selection_enabled": False,
        "graph_optimization_enabled": False,
        "recommendation_enabled": False,
        "autonomous_orchestration_enabled": False,
        "runtime_mutation_enabled": False,
        "persistent_runtime_writes_enabled": False,
        "background_orchestration_processing_enabled": False,
        "execution_capable_session_state_enabled": False,
        "session_driven_orchestration_behavior_enabled": False,
        "planning_session_counts": export_v3_7_graph_planning_session_counts(session),
        "session_status_counts": _status_counts((session.status,), V37_GRAPH_PLANNING_SESSION_STATUSES),
        "graph_snapshot_counts": {
            "snapshot_count": len(session.snapshots),
            "non_executable_snapshot_count": sum(1 for snapshot in session.snapshots if not snapshot.snapshot_is_executable),
            "execution_state_snapshot_count": sum(1 for snapshot in session.snapshots if snapshot.execution_state),
        },
        "audit_trail_counts": {
            "audit_trail_count": len(session.audit_trail),
            "fail_visible_audit_entry_count": sum(1 for entry in session.audit_trail if entry.fail_visible),
            "hidden_audit_entry_count": sum(1 for entry in session.audit_trail if entry.hidden),
        },
        "replay_evidence_counts": {
            "replay_evidence_count": replay["replay_evidence_count"],
            "non_executable_replay_evidence": replay["non_executable_replay_evidence"],
            "runtime_replay": replay["runtime_replay"],
            "orchestration_runtime_packet": replay["orchestration_runtime_packet"],
            "execution_authorization": replay["execution_authorization"],
        },
        "rollback_evidence_counts": {
            "rollback_evidence_count": replay["rollback_evidence_count"],
            "rollback_continuity_preserved": replay["rollback_continuity_preserved"],
        },
        "blocked_unsupported_prohibited_unknown_visibility_counts": {
            "blocked_visible_count": _audit_status_count(session, V37_SESSION_STATUS_BLOCKED),
            "unsupported_visible_count": _audit_status_count(session, V37_SESSION_STATUS_UNSUPPORTED),
            "prohibited_visible_count": _audit_status_count(session, V37_SESSION_STATUS_PROHIBITED),
            "unknown_visible_count": _audit_status_count(session, V37_SESSION_STATUS_UNKNOWN),
        },
        "provenance_continuity_totals": {
            "provenance_status": provenance.provenance_status,
            "provenance_record_count": provenance.provenance_record_count,
            "session_creation_provenance_preserved": provenance.session_creation_provenance_preserved,
            "graph_snapshot_provenance_preserved": provenance.graph_snapshot_provenance_preserved,
            "evaluation_provenance_preserved": provenance.evaluation_provenance_preserved,
            "replay_provenance_preserved": provenance.replay_provenance_preserved,
            "rollback_provenance_preserved": provenance.rollback_provenance_preserved,
            "audit_provenance_preserved": provenance.audit_provenance_preserved,
            "explainability_provenance_preserved": provenance.explainability_provenance_preserved,
            "continuity_provenance_preserved": provenance.continuity_provenance_preserved,
        },
        "explainability_continuity_totals": {
            "explainability_status": explainability.explainability_status,
            "explanation_count": explainability.explanation_count,
            "session_existence_explanation_count": explainability.session_existence_explanation_count,
            "snapshot_explanation_count": explainability.snapshot_explanation_count,
            "evaluation_evidence_explanation_count": explainability.evaluation_evidence_explanation_count,
            "visible_finding_explanation_count": explainability.visible_finding_explanation_count,
            "blocked_explanation_count": explainability.blocked_explanation_count,
            "unsupported_explanation_count": explainability.unsupported_explanation_count,
            "prohibited_explanation_count": explainability.prohibited_explanation_count,
            "unknown_explanation_count": explainability.unknown_explanation_count,
        },
        "validation_totals": {
            "validation_status": validation.validation_status,
            "valid": validation.valid,
            "finding_count": validation.finding_count,
            "error_count": validation.error_count,
            "visibility_finding_count": validation.visibility_finding_count,
            "duplicate_session_identity_count": validation.duplicate_session_identity_count,
            "hidden_prohibited_state_count": validation.hidden_prohibited_state_count,
            "hidden_unsupported_state_count": validation.hidden_unsupported_state_count,
            "hidden_unknown_state_count": validation.hidden_unknown_state_count,
            "non_execution_guarantee_preserved": validation.non_execution_guarantee_preserved,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "session_hash": hash_v3_7_graph_planning_session(session),
            "validation_hash": validation.deterministic_validation_hash,
            "audit_hash": audit.deterministic_audit_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_GRAPH_PLANNING_SESSION_VALIDATION_STABLE,
            "audit_coverage": audit.audit_status == V37_GRAPH_PLANNING_SESSION_AUDIT_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_GRAPH_PLANNING_SESSION_PROVENANCE_PRESERVED,
            "explainability_coverage": (
                explainability.explainability_status == V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE
            ),
            "replay_continuity_coverage": replay["replay_continuity_preserved"],
            "rollback_continuity_coverage": replay["rollback_continuity_preserved"],
            "non_execution_coverage": validation.non_execution_guarantee_preserved,
        },
        "planning_session": export_v3_7_graph_planning_session(session),
        "replay_evidence_records": export_v3_7_graph_planning_session_replay_evidence_records(session.replay_evidence),
        "validation_result": export_v3_7_graph_planning_session_validation_result(validation),
        "audit_result": export_v3_7_graph_planning_session_audit_result(audit),
        "provenance_result": export_v3_7_graph_planning_session_provenance_result(provenance),
        "explainability_result": export_v3_7_graph_planning_session_explainability_result(explainability),
        "explicit_limitations": [
            "planning sessions are non-executable",
            "planning sessions are evidence containers only",
            "session replay evidence is not runtime replay",
            "snapshots do not imply execution state",
            "audit trails do not imply runtime history",
            "session statuses do not authorize orchestration",
            "graph planning sessions do not enable routing, scheduling, or dispatch",
        ],
        "summary": {
            "planning_session_status": validation.validation_status,
            "planning_session_evidence": True,
            "runtime_orchestration_session_state": False,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "provenance_continuity_verified": validation.provenance_continuity_preserved,
            "explainability_continuity_verified": validation.explainability_continuity_preserved,
            "replay_continuity_verified": validation.replay_continuity_preserved,
            "rollback_continuity_verified": validation.rollback_continuity_preserved,
            "non_execution_guarantee_verified": validation.non_execution_guarantee_preserved,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.7 Graph Planning Sessions",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 Phase 5 adds deterministic graph planning session evidence containers.",
        "",
        "Planning sessions are NON-executable.",
        "",
        "Planning sessions are evidence containers only.",
        "",
        "Session replay evidence is NOT runtime replay.",
        "",
        "Snapshots do NOT imply execution state.",
        "",
        "Audit trails do NOT imply runtime history.",
        "",
        "Session statuses do NOT authorize orchestration.",
        "",
        "Graph planning sessions do NOT enable routing, scheduling, or dispatch.",
        "",
        "Planning session evidence groups deterministic graph reasoning artifacts. Runtime orchestration session state would control behavior. This phase implements planning session evidence only, not runtime orchestration session state.",
        "",
        "## Deterministic Scope",
        "",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Session hash: `{report['deterministic_guarantees']['session_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        f"- Planning sessions: `{report['planning_session_counts']['planning_session_count']}`",
        f"- Graph snapshots: `{report['graph_snapshot_counts']['snapshot_count']}`",
        f"- Audit trail entries: `{report['audit_trail_counts']['audit_trail_count']}`",
        f"- Replay evidence records: `{report['replay_evidence_counts']['replay_evidence_count']}`",
        f"- Rollback evidence records: `{report['rollback_evidence_counts']['rollback_evidence_count']}`",
        f"- Blocked visible states: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['blocked_visible_count']}`",
        f"- Unsupported visible states: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['unsupported_visible_count']}`",
        f"- Prohibited visible states: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['prohibited_visible_count']}`",
        f"- Unknown visible states: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['unknown_visible_count']}`",
        "",
        "## Verified Guarantees",
        "",
        "- deterministic session identity stability",
        "- deterministic snapshot stability",
        "- deterministic audit stability",
        "- deterministic replay evidence stability",
        "- deterministic rollback evidence stability",
        "- provenance continuity preservation",
        "- explainability continuity preservation",
        "- governance continuity preservation",
        "- compatibility continuity preservation",
        "- evaluation continuity preservation",
        "- fail-visible blocked states",
        "- fail-visible unsupported states",
        "- fail-visible prohibited states",
        "- fail-visible unknown states",
        "- deterministic serialization compatibility",
        "- deterministic hashing compatibility",
        "- sessions are non-executable",
        "",
        "## Explicit Non-Execution Boundary",
        "",
        "This implementation does not add graph execution.",
        "",
        "This implementation does not add session execution.",
        "",
        "This implementation does not add runtime orchestration.",
        "",
        "This implementation does not add routing, scheduling, dispatch, graph traversal execution, path selection, graph optimization, recommendation systems, autonomous orchestration, runtime mutation, persistent runtime writes, background orchestration processing, execution-capable session state, runtime state mutation, or session-driven orchestration behavior.",
        "",
        "Planning session evidence remains deterministic evidence, not runtime orchestration session state.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _status_counts(statuses: tuple[str, ...], expected_statuses: tuple[str, ...]) -> dict[str, int]:
    counts = {status: 0 for status in expected_statuses}
    for status in statuses:
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _audit_status_count(session, status: str) -> int:
    return sum(1 for entry in session.audit_trail if entry.session_status == status and entry.fail_visible and not entry.hidden)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = build_v3_7_graph_planning_sessions_report(args.repo_root)
    generated_path = args.repo_root / "docs/generated/v3_7_graph_planning_sessions_report.json"
    markdown_path = args.repo_root / "docs/migration/V3_7_GRAPH_PLANNING_SESSIONS.md"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_path)


if __name__ == "__main__":
    main()
