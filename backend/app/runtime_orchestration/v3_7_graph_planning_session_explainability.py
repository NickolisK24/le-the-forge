"""Deterministic explainability for v3.7 graph planning sessions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_planning_session_models import (
    V37_SESSION_STATUS_BLOCKED,
    V37_SESSION_STATUS_PROHIBITED,
    V37_SESSION_STATUS_UNKNOWN,
    V37_SESSION_STATUS_UNSUPPORTED,
    V37GraphPlanningSession,
)
from .v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session


V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE = "v3_7_graph_planning_session_explainability_stable"
V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_BLOCKED = "v3_7_graph_planning_session_explainability_blocked"


@dataclass(frozen=True)
class V37GraphPlanningSessionExplanation:
    explanation_id: str
    subject_type: str
    subject_id: str
    session_status: str
    why_present: str
    graph_snapshot_references: tuple[str, ...]
    evaluation_evidence_references: tuple[str, ...]
    visible_finding_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    continuity_references: tuple[str, ...]
    reasoning_chain: tuple[str, ...]
    replay_safe: bool = True
    execution_authorization: bool = False


@dataclass(frozen=True)
class V37GraphPlanningSessionExplainabilityResult:
    explainability_status: str
    replay_safe: bool
    explanation_count: int
    session_existence_explanation_count: int
    snapshot_explanation_count: int
    evaluation_evidence_explanation_count: int
    visible_finding_explanation_count: int
    blocked_explanation_count: int
    unsupported_explanation_count: int
    prohibited_explanation_count: int
    unknown_explanation_count: int
    provenance_supported_explanation_count: int
    continuity_supported_explanation_count: int
    missing_explanation_subjects: tuple[str, ...]
    explanations: tuple[V37GraphPlanningSessionExplanation, ...]
    deterministic_explainability_hash: str = ""


def explain_v3_7_graph_planning_session(
    session: V37GraphPlanningSession | None = None,
) -> V37GraphPlanningSessionExplainabilityResult:
    planning_session = session or build_v3_7_graph_planning_session()
    explanations = _build_explanations(planning_session)
    expected_subjects = {("planning_session", planning_session.identity.session_id)}
    expected_subjects.update(("session_snapshot", snapshot.snapshot_id) for snapshot in planning_session.snapshots)
    expected_subjects.update(("session_evaluation_evidence", item.evidence_id) for item in planning_session.evaluation_evidence)
    expected_subjects.update(("session_audit_trail", entry.audit_entry_id) for entry in planning_session.audit_trail)
    actual_subjects = {(explanation.subject_type, explanation.subject_id) for explanation in explanations}
    missing = tuple(sorted(f"{kind}:{subject_id}" for kind, subject_id in expected_subjects - actual_subjects))
    blocked = bool(missing) or any(
        not explanation.why_present
        or not explanation.provenance_references
        or not explanation.continuity_references
        or explanation.execution_authorization
        for explanation in explanations
    )
    result = V37GraphPlanningSessionExplainabilityResult(
        explainability_status=(
            V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_BLOCKED
            if blocked
            else V37_GRAPH_PLANNING_SESSION_EXPLAINABILITY_STABLE
        ),
        replay_safe=not blocked,
        explanation_count=len(explanations),
        session_existence_explanation_count=sum(1 for item in explanations if item.subject_type == "planning_session"),
        snapshot_explanation_count=sum(1 for item in explanations if item.subject_type == "session_snapshot"),
        evaluation_evidence_explanation_count=sum(
            1 for item in explanations if item.subject_type == "session_evaluation_evidence"
        ),
        visible_finding_explanation_count=sum(1 for item in explanations if item.subject_type == "session_audit_trail"),
        blocked_explanation_count=sum(1 for item in explanations if item.session_status == V37_SESSION_STATUS_BLOCKED),
        unsupported_explanation_count=sum(
            1 for item in explanations if item.session_status == V37_SESSION_STATUS_UNSUPPORTED
        ),
        prohibited_explanation_count=sum(
            1 for item in explanations if item.session_status == V37_SESSION_STATUS_PROHIBITED
        ),
        unknown_explanation_count=sum(1 for item in explanations if item.session_status == V37_SESSION_STATUS_UNKNOWN),
        provenance_supported_explanation_count=sum(1 for item in explanations if item.provenance_references),
        continuity_supported_explanation_count=sum(1 for item in explanations if item.continuity_references),
        missing_explanation_subjects=missing,
        explanations=tuple(sorted(explanations, key=lambda item: item.explanation_id)),
    )
    return replace(
        result,
        deterministic_explainability_hash=hash_v3_7_graph_planning_session_explainability_result(result),
    )


def export_v3_7_graph_planning_session_explanation(
    explanation: V37GraphPlanningSessionExplanation,
) -> dict[str, Any]:
    data = asdict(explanation)
    for field_name in (
        "graph_snapshot_references",
        "evaluation_evidence_references",
        "visible_finding_references",
        "provenance_references",
        "continuity_references",
        "reasoning_chain",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_planning_session_explainability_result(
    result: V37GraphPlanningSessionExplainabilityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_explanation_subjects"] = sorted(data["missing_explanation_subjects"])
    data["explanations"] = [
        export_v3_7_graph_planning_session_explanation(explanation)
        for explanation in sorted(result.explanations, key=lambda item: item.explanation_id)
    ]
    return data


def serialize_v3_7_graph_planning_session_explainability_result(
    result: V37GraphPlanningSessionExplainabilityResult,
) -> str:
    return stable_serialize(export_v3_7_graph_planning_session_explainability_result(result))


def hash_v3_7_graph_planning_session_explainability_result(
    result: V37GraphPlanningSessionExplainabilityResult,
) -> str:
    data = export_v3_7_graph_planning_session_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)


def _build_explanations(
    session: V37GraphPlanningSession,
) -> tuple[V37GraphPlanningSessionExplanation, ...]:
    explanations: list[V37GraphPlanningSessionExplanation] = [
        V37GraphPlanningSessionExplanation(
            explanation_id=f"explain_session_{session.identity.session_id}",
            subject_type="planning_session",
            subject_id=session.identity.session_id,
            session_status=session.status,
            why_present="planning session groups deterministic graph reasoning evidence",
            graph_snapshot_references=tuple(snapshot.snapshot_id for snapshot in session.snapshots),
            evaluation_evidence_references=tuple(item.evidence_id for item in session.evaluation_evidence),
            visible_finding_references=tuple(entry.audit_entry_id for entry in session.audit_trail),
            provenance_references=(session.provenance.provenance_id,),
            continuity_references=session.continuity_hash_references,
            reasoning_chain=("session_identity", "graph_snapshot", "evaluation_evidence", "non_executable_container"),
        )
    ]
    for snapshot in session.snapshots:
        explanations.append(
            V37GraphPlanningSessionExplanation(
                explanation_id=f"explain_snapshot_{snapshot.snapshot_id}",
                subject_type="session_snapshot",
                subject_id=snapshot.snapshot_id,
                session_status=session.status,
                why_present="snapshot preserves graph identity, hashes, and continuity references without execution state",
                graph_snapshot_references=(snapshot.snapshot_id,),
                evaluation_evidence_references=snapshot.evaluation_evidence_references,
                visible_finding_references=(),
                provenance_references=snapshot.provenance_references,
                continuity_references=snapshot.replay_continuity_references + snapshot.rollback_continuity_references,
                reasoning_chain=("snapshot_identity", "graph_hash", "continuity_references", "not_execution_state"),
            )
        )
    for evidence in session.evaluation_evidence:
        explanations.append(
            V37GraphPlanningSessionExplanation(
                explanation_id=f"explain_evaluation_{evidence.evidence_id}",
                subject_type="session_evaluation_evidence",
                subject_id=evidence.evidence_id,
                session_status=session.status,
                why_present="session references deterministic graph evaluation evidence",
                graph_snapshot_references=(evidence.snapshot_id,),
                evaluation_evidence_references=evidence.evaluation_trace_references + evidence.evaluation_finding_references,
                visible_finding_references=evidence.evaluation_finding_references,
                provenance_references=evidence.provenance_references,
                continuity_references=(evidence.evaluation_hash, evidence.evaluation_validation_hash, evidence.continuity_audit_hash),
                reasoning_chain=("evaluation_traces", "evaluation_findings", "evaluation_hash", "session_scope"),
            )
        )
    for entry in session.audit_trail:
        explanations.append(
            V37GraphPlanningSessionExplanation(
                explanation_id=f"explain_audit_{entry.audit_entry_id}",
                subject_type="session_audit_trail",
                subject_id=entry.audit_entry_id,
                session_status=entry.session_status,
                why_present=entry.message,
                graph_snapshot_references=tuple(snapshot.snapshot_id for snapshot in session.snapshots),
                evaluation_evidence_references=entry.evidence_references,
                visible_finding_references=(entry.audit_entry_id,),
                provenance_references=(session.provenance.provenance_id,),
                continuity_references=session.continuity_hash_references,
                reasoning_chain=("audit_trail", entry.session_status, "fail_visible", "not_runtime_history"),
            )
        )
    return tuple(explanations)
