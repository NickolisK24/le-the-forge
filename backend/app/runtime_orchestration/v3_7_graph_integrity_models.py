"""Deterministic v3.7 graph planning integrity enforcement models.

Integrity enforcement validates planning evidence only. It does not authorize
execution, route work, schedule work, dispatch work, traverse graphs, optimize
runtime decisions, or control orchestration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance


V3_7_GRAPH_INTEGRITY_PHASE_ID = "v3_7_graph_planning_integrity_enforcement"
V37_INTEGRITY_OUTCOME_VALID = "valid"
V37_INTEGRITY_OUTCOME_INVALID = "invalid"
V37_INTEGRITY_OUTCOME_BLOCKED = "blocked"
V37_INTEGRITY_OUTCOME_WARNING = "warning"
V37_INTEGRITY_OUTCOME_AUDIT_FAILED = "audit_failed"
V37_INTEGRITY_OUTCOMES: tuple[str, ...] = (
    V37_INTEGRITY_OUTCOME_VALID,
    V37_INTEGRITY_OUTCOME_INVALID,
    V37_INTEGRITY_OUTCOME_BLOCKED,
    V37_INTEGRITY_OUTCOME_WARNING,
    V37_INTEGRITY_OUTCOME_AUDIT_FAILED,
)

V37_INTEGRITY_FINDING_VALID = "integrity_valid"
V37_INTEGRITY_FINDING_INVALID = "integrity_invalid"
V37_INTEGRITY_FINDING_BLOCKED = "integrity_blocked"
V37_INTEGRITY_FINDING_WARNING = "integrity_warning"
V37_INTEGRITY_FINDING_CONTINUITY_VIOLATION = "continuity_violation"
V37_INTEGRITY_FINDING_PROVENANCE_VIOLATION = "provenance_violation"
V37_INTEGRITY_FINDING_EXPLAINABILITY_VIOLATION = "explainability_violation"
V37_INTEGRITY_FINDING_REPLAY_VIOLATION = "replay_violation"
V37_INTEGRITY_FINDING_ROLLBACK_VIOLATION = "rollback_violation"
V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION = "execution_boundary_violation"
V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE = "hidden_prohibited_state"
V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE = "hidden_unsupported_state"
V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE = "hidden_unknown_state"
V37_INTEGRITY_FINDING_CLASSIFICATIONS: tuple[str, ...] = (
    V37_INTEGRITY_FINDING_VALID,
    V37_INTEGRITY_FINDING_INVALID,
    V37_INTEGRITY_FINDING_BLOCKED,
    V37_INTEGRITY_FINDING_WARNING,
    V37_INTEGRITY_FINDING_CONTINUITY_VIOLATION,
    V37_INTEGRITY_FINDING_PROVENANCE_VIOLATION,
    V37_INTEGRITY_FINDING_EXPLAINABILITY_VIOLATION,
    V37_INTEGRITY_FINDING_REPLAY_VIOLATION,
    V37_INTEGRITY_FINDING_ROLLBACK_VIOLATION,
    V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION,
    V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphIntegrityPolicyIdentity:
    policy_id: str
    policy_version: str
    phase_id: str
    stable_identity_key: str


@dataclass(frozen=True)
class V37GraphIntegrityPolicyMetadata:
    metadata_key: str
    metadata_value: str


@dataclass(frozen=True)
class V37GraphIntegrityPolicyRequirement:
    requirement_id: str
    requirement_type: str
    required_reference_type: str
    description: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphIntegrityPolicy:
    identity: V37GraphIntegrityPolicyIdentity
    metadata: tuple[V37GraphIntegrityPolicyMetadata, ...]
    requirements: tuple[V37GraphIntegrityPolicyRequirement, ...]
    provenance: V37GraphProvenance
    execution_boundary_requirements: tuple[str, ...]
    policy_is_non_executable: bool = True
    validates_planning_evidence_only: bool = True
    valid_integrity_does_not_authorize_execution: bool = True
    enforcement_outcomes_are_planning_validation_only: bool = True
    execution_boundary_violations_blocked: bool = True
    execution_authorization_enabled: bool = False
    routing_authorization_enabled: bool = False
    scheduling_authorization_enabled: bool = False
    dispatch_authorization_enabled: bool = False
    traversal_authorization_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("metadata", "requirements", "execution_boundary_requirements"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


@dataclass(frozen=True)
class V37GraphIntegrityFinding:
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
    blocks_validation: bool = False
    execution_authorization: bool = False
    routing_authorization: bool = False
    scheduling_authorization: bool = False
    dispatch_authorization: bool = False
    traversal_authorization: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class V37GraphIntegrityEnforcementIdentity:
    enforcement_id: str
    policy_id: str
    aggregation_id: str
    enforcement_version: str
    phase_id: str
    stable_identity_key: str


@dataclass(frozen=True)
class V37GraphIntegrityReplayEvidence:
    replay_evidence_id: str
    enforcement_id: str
    policy_id: str
    evidence_source_references: tuple[str, ...]
    integrity_finding_references: tuple[str, ...]
    blocked_finding_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    continuity_hashes: tuple[str, ...]
    non_executable_replay_evidence: bool = True
    runtime_replay: bool = False
    execution_authorization: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_source_references",
            "integrity_finding_references",
            "blocked_finding_references",
            "provenance_references",
            "explainability_references",
            "continuity_hashes",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphIntegrityEnforcementResult:
    identity: V37GraphIntegrityEnforcementIdentity
    policy: V37GraphIntegrityPolicy
    metadata: tuple[V37GraphIntegrityPolicyMetadata, ...]
    evidence_source_references: tuple[str, ...]
    evidence_source_types: tuple[str, ...]
    enforcement_outcome: str
    findings: tuple[V37GraphIntegrityFinding, ...]
    replay_evidence: tuple[V37GraphIntegrityReplayEvidence, ...]
    rollback_continuity_references: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_reference_ids: tuple[str, ...]
    continuity_hash_references: tuple[str, ...]
    integrity_enforcement_is_non_executable: bool = True
    integrity_enforcement_validates_planning_evidence_only: bool = True
    valid_integrity_does_not_authorize_execution: bool = True
    blocked_integrity_does_not_perform_runtime_blocking: bool = True
    enforcement_outcomes_are_planning_validation_only: bool = True
    integrity_enforcement_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute: bool = True
    graph_execution_enabled: bool = False
    integrity_driven_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
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
    execution_gates_enabled: bool = False
    callable_orchestration_flows_enabled: bool = False
    runtime_control_system_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "metadata",
            "evidence_source_references",
            "evidence_source_types",
            "findings",
            "replay_evidence",
            "rollback_continuity_references",
            "explainability_reference_ids",
            "continuity_hash_references",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_graph_integrity_policy_identity(identity: V37GraphIntegrityPolicyIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_graph_integrity_policy_metadata(metadata: V37GraphIntegrityPolicyMetadata) -> dict[str, Any]:
    return asdict(metadata)


def export_v3_7_graph_integrity_policy_requirement(requirement: V37GraphIntegrityPolicyRequirement) -> dict[str, Any]:
    return asdict(requirement)


def export_v3_7_graph_integrity_policy(policy: V37GraphIntegrityPolicy) -> dict[str, Any]:
    return {
        "identity": export_v3_7_graph_integrity_policy_identity(policy.identity),
        "metadata": [
            export_v3_7_graph_integrity_policy_metadata(metadata)
            for metadata in sorted(policy.metadata, key=lambda item: item.metadata_key)
        ],
        "requirements": [
            export_v3_7_graph_integrity_policy_requirement(requirement)
            for requirement in sorted(policy.requirements, key=lambda item: item.requirement_id)
        ],
        "provenance": _export_provenance(policy.provenance),
        "execution_boundary_requirements": sorted(policy.execution_boundary_requirements),
        "policy_is_non_executable": policy.policy_is_non_executable,
        "validates_planning_evidence_only": policy.validates_planning_evidence_only,
        "valid_integrity_does_not_authorize_execution": policy.valid_integrity_does_not_authorize_execution,
        "enforcement_outcomes_are_planning_validation_only": policy.enforcement_outcomes_are_planning_validation_only,
        "execution_boundary_violations_blocked": policy.execution_boundary_violations_blocked,
        "execution_authorization_enabled": policy.execution_authorization_enabled,
        "routing_authorization_enabled": policy.routing_authorization_enabled,
        "scheduling_authorization_enabled": policy.scheduling_authorization_enabled,
        "dispatch_authorization_enabled": policy.dispatch_authorization_enabled,
        "traversal_authorization_enabled": policy.traversal_authorization_enabled,
    }


def export_v3_7_graph_integrity_finding(finding: V37GraphIntegrityFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_references"] = sorted(data["evidence_references"])
    return data


def export_v3_7_graph_integrity_enforcement_identity(
    identity: V37GraphIntegrityEnforcementIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_graph_integrity_replay_evidence(evidence: V37GraphIntegrityReplayEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "evidence_source_references",
        "integrity_finding_references",
        "blocked_finding_references",
        "provenance_references",
        "explainability_references",
        "continuity_hashes",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_integrity_enforcement_result(
    result: V37GraphIntegrityEnforcementResult,
) -> dict[str, Any]:
    return {
        "identity": export_v3_7_graph_integrity_enforcement_identity(result.identity),
        "policy": export_v3_7_graph_integrity_policy(result.policy),
        "metadata": [
            export_v3_7_graph_integrity_policy_metadata(metadata)
            for metadata in sorted(result.metadata, key=lambda item: item.metadata_key)
        ],
        "evidence_source_references": sorted(result.evidence_source_references),
        "evidence_source_types": sorted(result.evidence_source_types),
        "enforcement_outcome": result.enforcement_outcome,
        "findings": [
            export_v3_7_graph_integrity_finding(finding)
            for finding in sorted(result.findings, key=lambda item: item.finding_id)
        ],
        "replay_evidence": [
            export_v3_7_graph_integrity_replay_evidence(evidence)
            for evidence in sorted(result.replay_evidence, key=lambda item: item.replay_evidence_id)
        ],
        "rollback_continuity_references": sorted(result.rollback_continuity_references),
        "provenance": _export_provenance(result.provenance),
        "explainability_reference_ids": sorted(result.explainability_reference_ids),
        "continuity_hash_references": sorted(result.continuity_hash_references),
        "integrity_enforcement_is_non_executable": result.integrity_enforcement_is_non_executable,
        "integrity_enforcement_validates_planning_evidence_only": result.integrity_enforcement_validates_planning_evidence_only,
        "valid_integrity_does_not_authorize_execution": result.valid_integrity_does_not_authorize_execution,
        "blocked_integrity_does_not_perform_runtime_blocking": result.blocked_integrity_does_not_perform_runtime_blocking,
        "enforcement_outcomes_are_planning_validation_only": result.enforcement_outcomes_are_planning_validation_only,
        "integrity_enforcement_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute": result.integrity_enforcement_does_not_route_schedule_dispatch_traverse_optimize_recommend_or_execute,
        "graph_execution_enabled": result.graph_execution_enabled,
        "integrity_driven_execution_enabled": result.integrity_driven_execution_enabled,
        "orchestration_authorization_enabled": result.orchestration_authorization_enabled,
        "routing_enabled": result.routing_enabled,
        "scheduling_enabled": result.scheduling_enabled,
        "dispatch_enabled": result.dispatch_enabled,
        "traversal_logic_enabled": result.traversal_logic_enabled,
        "path_selection_enabled": result.path_selection_enabled,
        "scenario_selection_enabled": result.scenario_selection_enabled,
        "optimization_engine_enabled": result.optimization_engine_enabled,
        "recommendation_enabled": result.recommendation_enabled,
        "autonomous_orchestration_enabled": result.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": result.runtime_mutation_enabled,
        "persistent_runtime_writes_enabled": result.persistent_runtime_writes_enabled,
        "runtime_decision_making_enabled": result.runtime_decision_making_enabled,
        "execution_gates_enabled": result.execution_gates_enabled,
        "callable_orchestration_flows_enabled": result.callable_orchestration_flows_enabled,
        "runtime_control_system_enabled": result.runtime_control_system_enabled,
    }


def export_v3_7_graph_integrity_counts(result: V37GraphIntegrityEnforcementResult) -> dict[str, int]:
    return {
        "integrity_policy_count": 1,
        "enforcement_result_count": 1,
        "evidence_source_count": len(result.evidence_source_references),
        "integrity_finding_count": len(result.findings),
        "blocked_finding_count": sum(1 for finding in result.findings if finding.blocks_validation),
        "warning_finding_count": sum(1 for finding in result.findings if finding.severity == "warning"),
        "replay_evidence_count": len(result.replay_evidence),
        "rollback_continuity_reference_count": len(result.rollback_continuity_references),
    }


def serialize_v3_7_graph_integrity_policy(policy: V37GraphIntegrityPolicy) -> str:
    return stable_serialize(export_v3_7_graph_integrity_policy(policy))


def hash_v3_7_graph_integrity_policy(policy: V37GraphIntegrityPolicy) -> str:
    return deterministic_hash(export_v3_7_graph_integrity_policy(policy))


def serialize_v3_7_graph_integrity_enforcement_result(
    result: V37GraphIntegrityEnforcementResult,
) -> str:
    return stable_serialize(export_v3_7_graph_integrity_enforcement_result(result))


def hash_v3_7_graph_integrity_enforcement_result(
    result: V37GraphIntegrityEnforcementResult,
) -> str:
    return deterministic_hash(export_v3_7_graph_integrity_enforcement_result(result))


def validate_v3_7_graph_integrity_serialization_stability(
    result: V37GraphIntegrityEnforcementResult,
) -> dict[str, Any]:
    first = serialize_v3_7_graph_integrity_enforcement_result(result)
    second = serialize_v3_7_graph_integrity_enforcement_result(result)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_graph_planning_integrity_enforcement",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_graph_integrity_hash_stability(
    result: V37GraphIntegrityEnforcementResult,
) -> dict[str, Any]:
    first = hash_v3_7_graph_integrity_enforcement_result(result)
    second = hash_v3_7_graph_integrity_enforcement_result(result)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_graph_planning_integrity_enforcement",
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
