"""Deterministic v3.7 graph planning continuity certification models.

Certification records planning continuity evidence only. It does not certify
execution readiness, authorize orchestration, route work, schedule work,
dispatch work, traverse graphs, optimize runtime decisions, or execute.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance


V3_7_GRAPH_CERTIFICATION_PHASE_ID = "v3_7_graph_planning_continuity_certification"
V37_CERTIFICATION_OUTCOME_CERTIFIED = "certified"
V37_CERTIFICATION_OUTCOME_UNCERTIFIED = "uncertified"
V37_CERTIFICATION_OUTCOME_BLOCKED = "blocked"
V37_CERTIFICATION_OUTCOME_WARNING = "warning"
V37_CERTIFICATION_OUTCOME_AUDIT_FAILED = "audit_failed"
V37_CERTIFICATION_OUTCOMES: tuple[str, ...] = (
    V37_CERTIFICATION_OUTCOME_CERTIFIED,
    V37_CERTIFICATION_OUTCOME_UNCERTIFIED,
    V37_CERTIFICATION_OUTCOME_BLOCKED,
    V37_CERTIFICATION_OUTCOME_WARNING,
    V37_CERTIFICATION_OUTCOME_AUDIT_FAILED,
)

V37_CERTIFICATION_FINDING_PASSED = "certification_passed"
V37_CERTIFICATION_FINDING_FAILED = "certification_failed"
V37_CERTIFICATION_FINDING_BLOCKED = "certification_blocked"
V37_CERTIFICATION_FINDING_WARNING = "certification_warning"
V37_CERTIFICATION_FINDING_SCOPE_COMPLETE = "scope_complete"
V37_CERTIFICATION_FINDING_SCOPE_INCOMPLETE = "scope_incomplete"
V37_CERTIFICATION_FINDING_CONTINUITY_CERTIFIED = "continuity_certified"
V37_CERTIFICATION_FINDING_CONTINUITY_UNCERTIFIED = "continuity_uncertified"
V37_CERTIFICATION_FINDING_PROVENANCE_CERTIFIED = "provenance_certified"
V37_CERTIFICATION_FINDING_PROVENANCE_UNCERTIFIED = "provenance_uncertified"
V37_CERTIFICATION_FINDING_EXPLAINABILITY_CERTIFIED = "explainability_certified"
V37_CERTIFICATION_FINDING_EXPLAINABILITY_UNCERTIFIED = "explainability_uncertified"
V37_CERTIFICATION_FINDING_REPLAY_CERTIFIED = "replay_certified"
V37_CERTIFICATION_FINDING_REPLAY_UNCERTIFIED = "replay_uncertified"
V37_CERTIFICATION_FINDING_ROLLBACK_CERTIFIED = "rollback_certified"
V37_CERTIFICATION_FINDING_ROLLBACK_UNCERTIFIED = "rollback_uncertified"
V37_CERTIFICATION_FINDING_INTEGRITY_CERTIFIED = "integrity_certified"
V37_CERTIFICATION_FINDING_INTEGRITY_UNCERTIFIED = "integrity_uncertified"
V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_CERTIFIED = "execution_boundary_certified"
V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_UNCERTIFIED = "execution_boundary_uncertified"
V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED = "hidden_risk_state_detected"
V37_CERTIFICATION_FINDING_CLASSIFICATIONS: tuple[str, ...] = (
    V37_CERTIFICATION_FINDING_PASSED,
    V37_CERTIFICATION_FINDING_FAILED,
    V37_CERTIFICATION_FINDING_BLOCKED,
    V37_CERTIFICATION_FINDING_WARNING,
    V37_CERTIFICATION_FINDING_SCOPE_COMPLETE,
    V37_CERTIFICATION_FINDING_SCOPE_INCOMPLETE,
    V37_CERTIFICATION_FINDING_CONTINUITY_CERTIFIED,
    V37_CERTIFICATION_FINDING_CONTINUITY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_PROVENANCE_CERTIFIED,
    V37_CERTIFICATION_FINDING_PROVENANCE_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_EXPLAINABILITY_CERTIFIED,
    V37_CERTIFICATION_FINDING_EXPLAINABILITY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_REPLAY_CERTIFIED,
    V37_CERTIFICATION_FINDING_REPLAY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_ROLLBACK_CERTIFIED,
    V37_CERTIFICATION_FINDING_ROLLBACK_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_INTEGRITY_CERTIFIED,
    V37_CERTIFICATION_FINDING_INTEGRITY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_CERTIFIED,
    V37_CERTIFICATION_FINDING_EXECUTION_BOUNDARY_UNCERTIFIED,
    V37_CERTIFICATION_FINDING_HIDDEN_RISK_STATE_DETECTED,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphCertificationIdentity:
    certification_id: str
    certification_version: str
    phase_id: str
    stable_identity_key: str


@dataclass(frozen=True)
class V37GraphCertificationMetadata:
    metadata_key: str
    metadata_value: str


@dataclass(frozen=True)
class V37GraphCertificationScopeIdentity:
    scope_id: str
    certification_id: str
    scope_version: str
    phase_id: str
    stable_identity_key: str


@dataclass(frozen=True)
class V37GraphCertificationScopeReference:
    reference_id: str
    reference_type: str
    phase_id: str
    artifact_id: str
    artifact_hash: str
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    continuity_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in ("provenance_references", "explainability_references", "continuity_hashes"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphCertificationScope:
    identity: V37GraphCertificationScopeIdentity
    metadata: tuple[V37GraphCertificationMetadata, ...]
    references: tuple[V37GraphCertificationScopeReference, ...]
    provenance: V37GraphProvenance
    scope_is_non_executable: bool = True
    validates_planning_continuity_only: bool = True
    scope_does_not_mark_runtime_readiness: bool = True
    routing_scheduling_dispatch_traversal_prohibited: bool = True

    def __post_init__(self) -> None:
        for field_name in ("metadata", "references"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


@dataclass(frozen=True)
class V37GraphCertificationFinding:
    finding_id: str
    finding_classification: str
    subject_type: str
    subject_id: str
    severity: str
    summary: str
    evidence_references: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False
    active_violation: bool = False
    blocks_certification: bool = False
    execution_authorization: bool = False
    runtime_readiness_certification: bool = False
    routing_authorization: bool = False
    scheduling_authorization: bool = False
    dispatch_authorization: bool = False
    traversal_authorization: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class V37GraphCertificationEvidence:
    evidence_id: str
    certification_id: str
    scope_id: str
    graph_evidence_references: tuple[str, ...]
    governance_evidence_references: tuple[str, ...]
    compatibility_evidence_references: tuple[str, ...]
    evaluation_evidence_references: tuple[str, ...]
    session_evidence_references: tuple[str, ...]
    scenario_evidence_references: tuple[str, ...]
    aggregation_evidence_references: tuple[str, ...]
    integrity_evidence_references: tuple[str, ...]
    continuity_hashes: tuple[str, ...]
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    replay_references: tuple[str, ...]
    rollback_references: tuple[str, ...]
    execution_boundary_references: tuple[str, ...]
    replay_safe: bool = True
    rollback_safe: bool = True
    non_executable_evidence: bool = True
    runtime_readiness_certification: bool = False
    execution_authorization: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "graph_evidence_references",
            "governance_evidence_references",
            "compatibility_evidence_references",
            "evaluation_evidence_references",
            "session_evidence_references",
            "scenario_evidence_references",
            "aggregation_evidence_references",
            "integrity_evidence_references",
            "continuity_hashes",
            "provenance_references",
            "explainability_references",
            "replay_references",
            "rollback_references",
            "execution_boundary_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphCertificationReplayEvidence:
    replay_evidence_id: str
    certification_id: str
    scope_id: str
    certification_outcome: str
    finding_references: tuple[str, ...]
    evidence_source_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    continuity_hashes: tuple[str, ...]
    non_executable_replay_evidence: bool = True
    runtime_replay: bool = False
    execution_authorization: bool = False
    runtime_readiness_certification: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "finding_references",
            "evidence_source_references",
            "provenance_references",
            "explainability_references",
            "continuity_hashes",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphPlanningContinuityCertification:
    identity: V37GraphCertificationIdentity
    metadata: tuple[V37GraphCertificationMetadata, ...]
    scope: V37GraphCertificationScope
    evidence: V37GraphCertificationEvidence
    certification_outcome: str
    findings: tuple[V37GraphCertificationFinding, ...]
    replay_evidence: tuple[V37GraphCertificationReplayEvidence, ...]
    rollback_continuity_references: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_reference_ids: tuple[str, ...]
    continuity_hash_references: tuple[str, ...]
    certification_is_non_executable: bool = True
    certification_validates_planning_continuity_only: bool = True
    certified_continuity_does_not_authorize_execution: bool = True
    certification_does_not_mark_runtime_execution_readiness: bool = True
    certification_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute: bool = True
    graph_execution_enabled: bool = False
    certification_driven_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    execution_readiness_approval_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    traversal_logic_enabled: bool = False
    path_selection_enabled: bool = False
    scenario_selection_enabled: bool = False
    optimization_engine_enabled: bool = False
    recommendation_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    persistent_runtime_writes_enabled: bool = False
    runtime_decision_making_enabled: bool = False
    executable_certification_gates_enabled: bool = False
    runtime_control_system_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "metadata",
            "findings",
            "replay_evidence",
            "rollback_continuity_references",
            "explainability_reference_ids",
            "continuity_hash_references",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_graph_certification_identity(identity: V37GraphCertificationIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_graph_certification_metadata(metadata: V37GraphCertificationMetadata) -> dict[str, Any]:
    return asdict(metadata)


def export_v3_7_graph_certification_scope_identity(identity: V37GraphCertificationScopeIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_graph_certification_scope_reference(reference: V37GraphCertificationScopeReference) -> dict[str, Any]:
    data = asdict(reference)
    for field_name in ("provenance_references", "explainability_references", "continuity_hashes"):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_certification_scope(scope: V37GraphCertificationScope) -> dict[str, Any]:
    return {
        "identity": export_v3_7_graph_certification_scope_identity(scope.identity),
        "metadata": [
            export_v3_7_graph_certification_metadata(metadata)
            for metadata in sorted(scope.metadata, key=lambda item: item.metadata_key)
        ],
        "references": [
            export_v3_7_graph_certification_scope_reference(reference)
            for reference in sorted(scope.references, key=lambda item: item.reference_id)
        ],
        "provenance": _export_provenance(scope.provenance),
        "scope_is_non_executable": scope.scope_is_non_executable,
        "validates_planning_continuity_only": scope.validates_planning_continuity_only,
        "scope_does_not_mark_runtime_readiness": scope.scope_does_not_mark_runtime_readiness,
        "routing_scheduling_dispatch_traversal_prohibited": scope.routing_scheduling_dispatch_traversal_prohibited,
    }


def export_v3_7_graph_certification_finding(finding: V37GraphCertificationFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_references"] = sorted(data["evidence_references"])
    return data


def export_v3_7_graph_certification_evidence(evidence: V37GraphCertificationEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "graph_evidence_references",
        "governance_evidence_references",
        "compatibility_evidence_references",
        "evaluation_evidence_references",
        "session_evidence_references",
        "scenario_evidence_references",
        "aggregation_evidence_references",
        "integrity_evidence_references",
        "continuity_hashes",
        "provenance_references",
        "explainability_references",
        "replay_references",
        "rollback_references",
        "execution_boundary_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_certification_replay_evidence(evidence: V37GraphCertificationReplayEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "finding_references",
        "evidence_source_references",
        "provenance_references",
        "explainability_references",
        "continuity_hashes",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_planning_continuity_certification(
    certification: V37GraphPlanningContinuityCertification,
) -> dict[str, Any]:
    return {
        "identity": export_v3_7_graph_certification_identity(certification.identity),
        "metadata": [
            export_v3_7_graph_certification_metadata(metadata)
            for metadata in sorted(certification.metadata, key=lambda item: item.metadata_key)
        ],
        "scope": export_v3_7_graph_certification_scope(certification.scope),
        "evidence": export_v3_7_graph_certification_evidence(certification.evidence),
        "certification_outcome": certification.certification_outcome,
        "findings": [
            export_v3_7_graph_certification_finding(finding)
            for finding in sorted(certification.findings, key=lambda item: item.finding_id)
        ],
        "replay_evidence": [
            export_v3_7_graph_certification_replay_evidence(evidence)
            for evidence in sorted(certification.replay_evidence, key=lambda item: item.replay_evidence_id)
        ],
        "rollback_continuity_references": sorted(certification.rollback_continuity_references),
        "provenance": _export_provenance(certification.provenance),
        "explainability_reference_ids": sorted(certification.explainability_reference_ids),
        "continuity_hash_references": sorted(certification.continuity_hash_references),
        "certification_is_non_executable": certification.certification_is_non_executable,
        "certification_validates_planning_continuity_only": certification.certification_validates_planning_continuity_only,
        "certified_continuity_does_not_authorize_execution": certification.certified_continuity_does_not_authorize_execution,
        "certification_does_not_mark_runtime_execution_readiness": certification.certification_does_not_mark_runtime_execution_readiness,
        "certification_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute": certification.certification_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute,
        "graph_execution_enabled": certification.graph_execution_enabled,
        "certification_driven_execution_enabled": certification.certification_driven_execution_enabled,
        "orchestration_authorization_enabled": certification.orchestration_authorization_enabled,
        "execution_readiness_approval_enabled": certification.execution_readiness_approval_enabled,
        "routing_enabled": certification.routing_enabled,
        "scheduling_enabled": certification.scheduling_enabled,
        "dispatch_enabled": certification.dispatch_enabled,
        "traversal_logic_enabled": certification.traversal_logic_enabled,
        "path_selection_enabled": certification.path_selection_enabled,
        "scenario_selection_enabled": certification.scenario_selection_enabled,
        "optimization_engine_enabled": certification.optimization_engine_enabled,
        "recommendation_enabled": certification.recommendation_enabled,
        "autonomous_orchestration_enabled": certification.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": certification.runtime_mutation_enabled,
        "persistent_runtime_writes_enabled": certification.persistent_runtime_writes_enabled,
        "runtime_decision_making_enabled": certification.runtime_decision_making_enabled,
        "executable_certification_gates_enabled": certification.executable_certification_gates_enabled,
        "runtime_control_system_enabled": certification.runtime_control_system_enabled,
    }


def export_v3_7_graph_certification_counts(
    certification: V37GraphPlanningContinuityCertification,
) -> dict[str, int]:
    return {
        "certification_count": 1,
        "scope_count": 1,
        "scope_reference_count": len(certification.scope.references),
        "certification_evidence_count": 1,
        "finding_count": len(certification.findings),
        "blocked_finding_count": sum(1 for finding in certification.findings if finding.blocks_certification),
        "replay_evidence_count": len(certification.replay_evidence),
        "rollback_continuity_reference_count": len(certification.rollback_continuity_references),
    }


def serialize_v3_7_graph_certification_scope(scope: V37GraphCertificationScope) -> str:
    return stable_serialize(export_v3_7_graph_certification_scope(scope))


def hash_v3_7_graph_certification_scope(scope: V37GraphCertificationScope) -> str:
    return deterministic_hash(export_v3_7_graph_certification_scope(scope))


def serialize_v3_7_graph_planning_continuity_certification(
    certification: V37GraphPlanningContinuityCertification,
) -> str:
    return stable_serialize(export_v3_7_graph_planning_continuity_certification(certification))


def hash_v3_7_graph_planning_continuity_certification(
    certification: V37GraphPlanningContinuityCertification,
) -> str:
    return deterministic_hash(export_v3_7_graph_planning_continuity_certification(certification))


def validate_v3_7_graph_certification_serialization_stability(
    certification: V37GraphPlanningContinuityCertification,
) -> dict[str, Any]:
    first = serialize_v3_7_graph_planning_continuity_certification(certification)
    second = serialize_v3_7_graph_planning_continuity_certification(certification)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_graph_planning_continuity_certification",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_graph_certification_hash_stability(
    certification: V37GraphPlanningContinuityCertification,
) -> dict[str, Any]:
    first = hash_v3_7_graph_planning_continuity_certification(certification)
    second = hash_v3_7_graph_planning_continuity_certification(certification)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_graph_planning_continuity_certification",
    }


def _export_provenance(provenance: V37GraphProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field_name in (
        "lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "governance_references",
        "compatibility_references",
        "explainability_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data
