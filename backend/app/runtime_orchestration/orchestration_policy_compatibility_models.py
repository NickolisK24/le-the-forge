"""Deterministic orchestration policy compatibility models for v3.6 Phase 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


COMPATIBILITY_COMPATIBLE = "compatibility_compatible"
COMPATIBILITY_INCOMPATIBLE = "compatibility_incompatible"
COMPATIBILITY_PROHIBITED = "compatibility_prohibited"
COMPATIBILITY_UNSUPPORTED = "compatibility_unsupported"
COMPATIBILITY_DEPENDENCY_BLOCKED = "compatibility_dependency_blocked"
COMPATIBILITY_GOVERNANCE_BLOCKED = "compatibility_governance_blocked"
COMPATIBILITY_CONTINUITY_BLOCKED = "compatibility_continuity_blocked"
COMPATIBILITY_STATES: tuple[str, ...] = (
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_INCOMPATIBLE,
    COMPATIBILITY_PROHIBITED,
    COMPATIBILITY_UNSUPPORTED,
    COMPATIBILITY_DEPENDENCY_BLOCKED,
    COMPATIBILITY_GOVERNANCE_BLOCKED,
    COMPATIBILITY_CONTINUITY_BLOCKED,
)

COMPATIBILITY_CONTINUITY_PRESERVED = "compatibility_continuity_preserved"
COMPATIBILITY_CONTINUITY_GAP = "compatibility_continuity_gap"

COMPATIBILITY_BLOCKED_BY_INCOMPATIBILITY = "compatibility_blocked_by_incompatibility"
COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING = "compatibility_blocked_by_prohibited_pairing"
COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION = "compatibility_blocked_by_unsupported_combination"
COMPATIBILITY_BLOCKED_BY_DEPENDENCY_CONFLICT = "compatibility_blocked_by_dependency_conflict"
COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT = "compatibility_blocked_by_governance_conflict"
COMPATIBILITY_BLOCKED_BY_CONTINUITY_GAP = "compatibility_blocked_by_continuity_gap"
COMPATIBILITY_BLOCKED_BY_PROVENANCE_GAP = "compatibility_blocked_by_provenance_gap"
COMPATIBILITY_BLOCKED_BY_INTEGRITY_GAP = "compatibility_blocked_by_integrity_gap"
COMPATIBILITY_BLOCKED_BY_EXPLAINABILITY_GAP = "compatibility_blocked_by_explainability_gap"
COMPATIBILITY_BLOCKED_BY_HASH_MISMATCH = "compatibility_blocked_by_hash_mismatch"
COMPATIBILITY_BLOCKER_STATES: tuple[str, ...] = (
    COMPATIBILITY_BLOCKED_BY_INCOMPATIBILITY,
    COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING,
    COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION,
    COMPATIBILITY_BLOCKED_BY_DEPENDENCY_CONFLICT,
    COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT,
    COMPATIBILITY_BLOCKED_BY_CONTINUITY_GAP,
    COMPATIBILITY_BLOCKED_BY_PROVENANCE_GAP,
    COMPATIBILITY_BLOCKED_BY_INTEGRITY_GAP,
    COMPATIBILITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    COMPATIBILITY_BLOCKED_BY_HASH_MISMATCH,
)

COMPATIBILITY_EVALUATION_STABLE = "compatibility_evaluation_stable"
COMPATIBILITY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS = "compatibility_evaluation_stable_with_visible_blockers"
COMPATIBILITY_EVALUATION_BLOCKED_BY_CONTINUITY_GAP = "compatibility_evaluation_blocked_by_continuity_gap"
COMPATIBILITY_EVALUATION_REQUIRES_MANUAL_REVIEW = "compatibility_evaluation_requires_manual_review"
COMPATIBILITY_EVALUATION_STATUSES: tuple[str, ...] = (
    COMPATIBILITY_EVALUATION_BLOCKED_BY_CONTINUITY_GAP,
    COMPATIBILITY_EVALUATION_REQUIRES_MANUAL_REVIEW,
    COMPATIBILITY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS,
    COMPATIBILITY_EVALUATION_STABLE,
)

COMPATIBILITY_EXPLAINABILITY_STABLE = "compatibility_explainability_stable"
COMPATIBILITY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "compatibility_explainability_blocked_by_visibility_gap"

COMPATIBILITY_INTEGRITY_STABLE = "compatibility_integrity_stable"
COMPATIBILITY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP = "compatibility_integrity_blocked_by_registry_gap"
COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP = "compatibility_integrity_blocked_by_hash_gap"
COMPATIBILITY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP = "compatibility_integrity_blocked_by_provenance_gap"
COMPATIBILITY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP = "compatibility_integrity_blocked_by_dependency_gap"
COMPATIBILITY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP = "compatibility_integrity_blocked_by_governance_gap"
COMPATIBILITY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "compatibility_integrity_blocked_by_explainability_gap"
COMPATIBILITY_INTEGRITY_BLOCKED_BY_CLASSIFICATION_GAP = "compatibility_integrity_blocked_by_classification_gap"
COMPATIBILITY_INTEGRITY_REQUIRES_MANUAL_REVIEW = "compatibility_integrity_requires_manual_review"
COMPATIBILITY_INTEGRITY_STATUSES: tuple[str, ...] = (
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_CLASSIFICATION_GAP,
    COMPATIBILITY_INTEGRITY_REQUIRES_MANUAL_REVIEW,
    COMPATIBILITY_INTEGRITY_STABLE,
)


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityIdentifier:
    relationship_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityProvenance:
    source_phase: str
    source_artifact: str
    upstream_policy_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyDependencyConflict:
    conflict_id: str
    policy_ids: tuple[str, ...]
    dependency_chain: tuple[str, ...]
    conflict_reason: str


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityBlockerChain:
    blocker_chain_id: str
    blocker_states: tuple[str, ...]
    policy_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityRelationship:
    identifier: OrchestrationPolicyCompatibilityIdentifier
    policy_ids: tuple[str, ...]
    compatibility_state: str
    compatibility_classification: str
    dependency_conflicts: tuple[OrchestrationPolicyDependencyConflict, ...]
    governance_conflicts: tuple[str, ...]
    blocker_chains: tuple[OrchestrationPolicyCompatibilityBlockerChain, ...]
    provenance: OrchestrationPolicyCompatibilityProvenance
    governance_metadata: Mapping[str, Any]
    support_rationale: tuple[str, ...]
    blocker_reasons: tuple[str, ...]
    integrity_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    audit_log_writing_enabled: bool = False
    production_consumption_enabled: bool = False
    graph_execution_enabled: bool = False
    graph_traversal_behavior_enabled: bool = False
    scheduling_behavior_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    runtime_trace_capture_enabled: bool = False
    production_state_reads_enabled: bool = False
    live_replay_enabled: bool = False
    persistent_audit_storage_enabled: bool = False
    compatibility_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityRegistry:
    registry_id: str
    schema_version: str
    relationships: tuple[OrchestrationPolicyCompatibilityRelationship, ...]
    registry_metadata: Mapping[str, Any]
    planning_only: bool = True
    non_production: bool = True


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityBlocker:
    relationship_id: str
    blocker_state: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityEvaluationRecord:
    relationship_id: str
    policy_ids: tuple[str, ...]
    compatibility_state: str
    relationship_hash: str
    dependency_conflict_count: int
    governance_conflict_count: int
    blocker_chain_count: int
    provenance_continuity_state: str
    governance_continuity_state: str
    integrity_continuity_state: str
    explainability_continuity_state: str
    blockers: tuple[OrchestrationPolicyCompatibilityBlocker, ...]


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityEvaluationInput:
    compatibility_registry: OrchestrationPolicyCompatibilityRegistry
    selected_policy_ids: tuple[str, ...] = ()
    expected_registry_hash: str | None = None
    expected_relationship_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityEvaluationResult:
    registry_id: str
    compatibility_evaluation_status: str
    planning_only: bool
    non_production: bool
    relationship_records: tuple[OrchestrationPolicyCompatibilityEvaluationRecord, ...]
    registered_relationship_count: int
    compatible_relationship_count: int
    incompatible_relationship_count: int
    prohibited_relationship_count: int
    unsupported_relationship_count: int
    dependency_conflict_count: int
    governance_conflict_count: int
    blocker_chain_count: int
    blocker_count: int
    multi_policy_compatibility_state: str
    selected_policy_ids: tuple[str, ...]
    provenance_continuity_status: str
    governance_continuity_status: str
    integrity_continuity_status: str
    explainability_continuity_status: str
    blocker_summary: tuple[OrchestrationPolicyCompatibilityBlocker, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_registry_hash: str
    deterministic_compatibility_evaluation_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    audit_log_writing_enabled: bool = False
    production_consumption_enabled: bool = False
    graph_execution_enabled: bool = False
    graph_traversal_behavior_enabled: bool = False
    scheduling_behavior_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    runtime_trace_capture_enabled: bool = False
    production_state_reads_enabled: bool = False
    live_replay_enabled: bool = False
    persistent_audit_storage_enabled: bool = False
    compatibility_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityExplanationRecord:
    relationship_id: str
    policy_ids: tuple[str, ...]
    compatibility_state: str
    explanation_status: str
    why_compatible: tuple[str, ...]
    why_incompatible: tuple[str, ...]
    why_prohibited: tuple[str, ...]
    why_unsupported: tuple[str, ...]
    dependency_conflict_chain: tuple[str, ...]
    governance_conflict_chain: tuple[str, ...]
    continuity_conflict_chain: tuple[str, ...]
    blocker_chain_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityExplainabilityResult:
    registry_id: str
    compatibility_explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationPolicyCompatibilityExplanationRecord, ...]
    compatible_explanation_count: int
    incompatible_explanation_count: int
    prohibited_explanation_count: int
    unsupported_explanation_count: int
    dependency_conflict_visibility_count: int
    governance_conflict_visibility_count: int
    continuity_conflict_visibility_count: int
    blocker_chain_visibility_count: int
    deterministic_compatibility_explainability_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    compatibility_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityIntegrityInput:
    compatibility_registry: OrchestrationPolicyCompatibilityRegistry
    evaluation_result: OrchestrationPolicyCompatibilityEvaluationResult
    explainability_result: OrchestrationPolicyCompatibilityExplainabilityResult
    expected_registry_hash: str | None = None
    expected_evaluation_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationPolicyCompatibilityIntegrityResult:
    registry_id: str
    compatibility_integrity_status: str
    planning_only: bool
    registry_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    compatibility_hash_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    provenance_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    dependency_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    governance_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    explainability_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    classification_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    blocker_chain_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    deterministic_serialization_integrity: OrchestrationPolicyCompatibilityIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_compatibility_integrity_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    compatibility_execution_enabled: bool = False


def export_compatibility_provenance(provenance: OrchestrationPolicyCompatibilityProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field in ("upstream_policy_ids", "replay_reference_ids", "rollback_reference_ids", "governance_reference_ids"):
        data[field] = sorted(data[field])
    return data


def export_dependency_conflict(conflict: OrchestrationPolicyDependencyConflict) -> dict[str, Any]:
    data = asdict(conflict)
    data["policy_ids"] = sorted(data["policy_ids"])
    data["dependency_chain"] = sorted(data["dependency_chain"])
    return data


def export_blocker_chain(chain: OrchestrationPolicyCompatibilityBlockerChain) -> dict[str, Any]:
    data = asdict(chain)
    data["blocker_states"] = sorted(data["blocker_states"])
    data["policy_ids"] = sorted(data["policy_ids"])
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_compatibility_relationship(relationship: OrchestrationPolicyCompatibilityRelationship) -> dict[str, Any]:
    data = _export_compatibility_relationship_base(relationship)
    data["deterministic_relationship_hash"] = hash_compatibility_relationship(relationship)
    return data


def serialize_compatibility_relationship(relationship: OrchestrationPolicyCompatibilityRelationship) -> str:
    return stable_serialize(export_compatibility_relationship(relationship))


def hash_compatibility_relationship(relationship: OrchestrationPolicyCompatibilityRelationship) -> str:
    return deterministic_hash(_export_compatibility_relationship_base(relationship))


def export_compatibility_registry(registry: OrchestrationPolicyCompatibilityRegistry) -> dict[str, Any]:
    data = asdict(registry)
    data["relationships"] = [
        export_compatibility_relationship(relationship)
        for relationship in sorted(registry.relationships, key=lambda item: item.identifier.relationship_id)
    ]
    data["registry_metadata"] = dict(sorted(registry.registry_metadata.items()))
    data["deterministic_compatibility_registry_hash"] = hash_compatibility_registry(registry)
    return data


def serialize_compatibility_registry(registry: OrchestrationPolicyCompatibilityRegistry) -> str:
    return stable_serialize(export_compatibility_registry(registry))


def hash_compatibility_registry(registry: OrchestrationPolicyCompatibilityRegistry) -> str:
    return deterministic_hash(
        {
            "registry_id": registry.registry_id,
            "schema_version": registry.schema_version,
            "relationships": [
                export_compatibility_relationship(relationship)
                for relationship in sorted(registry.relationships, key=lambda item: item.identifier.relationship_id)
            ],
            "registry_metadata": dict(sorted(registry.registry_metadata.items())),
            "planning_only": registry.planning_only,
            "non_production": registry.non_production,
        }
    )


def export_compatibility_blocker(blocker: OrchestrationPolicyCompatibilityBlocker) -> dict[str, Any]:
    data = asdict(blocker)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_compatibility_evaluation_record(record: OrchestrationPolicyCompatibilityEvaluationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["policy_ids"] = sorted(data["policy_ids"])
    data["blockers"] = [export_compatibility_blocker(blocker) for blocker in sorted(record.blockers, key=_blocker_sort_key)]
    return data


def export_compatibility_evaluation_result(result: OrchestrationPolicyCompatibilityEvaluationResult) -> dict[str, Any]:
    data = asdict(result)
    data["relationship_records"] = [
        export_compatibility_evaluation_record(record)
        for record in sorted(result.relationship_records, key=lambda item: item.relationship_id)
    ]
    data["selected_policy_ids"] = sorted(data["selected_policy_ids"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    data["blocker_summary"] = [export_compatibility_blocker(blocker) for blocker in sorted(result.blocker_summary, key=_blocker_sort_key)]
    return data


def serialize_compatibility_evaluation_result(result: OrchestrationPolicyCompatibilityEvaluationResult) -> str:
    return stable_serialize(export_compatibility_evaluation_result(result))


def hash_compatibility_evaluation_result(result: OrchestrationPolicyCompatibilityEvaluationResult) -> str:
    data = export_compatibility_evaluation_result(result)
    data.pop("deterministic_compatibility_evaluation_hash", None)
    return deterministic_hash(data)


def export_compatibility_explanation_record(record: OrchestrationPolicyCompatibilityExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "policy_ids",
        "why_compatible",
        "why_incompatible",
        "why_prohibited",
        "why_unsupported",
        "dependency_conflict_chain",
        "governance_conflict_chain",
        "continuity_conflict_chain",
        "blocker_chain_visibility",
        "provenance_visibility",
        "integrity_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_compatibility_explainability_result(result: OrchestrationPolicyCompatibilityExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_compatibility_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.relationship_id)
    ]
    return data


def serialize_compatibility_explainability_result(result: OrchestrationPolicyCompatibilityExplainabilityResult) -> str:
    return stable_serialize(export_compatibility_explainability_result(result))


def hash_compatibility_explainability_result(result: OrchestrationPolicyCompatibilityExplainabilityResult) -> str:
    data = export_compatibility_explainability_result(result)
    data.pop("deterministic_compatibility_explainability_hash", None)
    return deterministic_hash(data)


def export_compatibility_integrity_summary(summary: OrchestrationPolicyCompatibilityIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_compatibility_integrity_result(result: OrchestrationPolicyCompatibilityIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "registry_integrity",
        "compatibility_hash_integrity",
        "provenance_integrity",
        "dependency_integrity",
        "governance_integrity",
        "explainability_integrity",
        "classification_integrity",
        "blocker_chain_integrity",
        "deterministic_serialization_integrity",
    ):
        data[field] = export_compatibility_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_compatibility_integrity_result(result: OrchestrationPolicyCompatibilityIntegrityResult) -> str:
    return stable_serialize(export_compatibility_integrity_result(result))


def hash_compatibility_integrity_result(result: OrchestrationPolicyCompatibilityIntegrityResult) -> str:
    data = export_compatibility_integrity_result(result)
    data.pop("deterministic_compatibility_integrity_hash", None)
    return deterministic_hash(data)


def _export_compatibility_relationship_base(relationship: OrchestrationPolicyCompatibilityRelationship) -> dict[str, Any]:
    data = asdict(relationship)
    data["identifier"] = asdict(relationship.identifier)
    data["policy_ids"] = sorted(data["policy_ids"])
    data["dependency_conflicts"] = [
        export_dependency_conflict(conflict)
        for conflict in sorted(relationship.dependency_conflicts, key=lambda item: item.conflict_id)
    ]
    data["blocker_chains"] = [
        export_blocker_chain(chain)
        for chain in sorted(relationship.blocker_chains, key=lambda item: item.blocker_chain_id)
    ]
    data["provenance"] = export_compatibility_provenance(relationship.provenance)
    data["governance_metadata"] = dict(sorted(relationship.governance_metadata.items()))
    for field in (
        "governance_conflicts",
        "support_rationale",
        "blocker_reasons",
        "integrity_reference_ids",
        "explainability_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def _blocker_sort_key(blocker: OrchestrationPolicyCompatibilityBlocker) -> tuple[str, str, str]:
    return (blocker.relationship_id, blocker.blocker_state, blocker.reason)
