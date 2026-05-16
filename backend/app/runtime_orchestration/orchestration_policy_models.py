"""Deterministic orchestration policy intelligence models for v3.6."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


POLICY_SUPPORTED = "policy_supported"
POLICY_PROHIBITED = "policy_prohibited"
POLICY_UNSUPPORTED = "policy_unsupported"
POLICY_BLOCKED = "policy_blocked"
POLICY_REQUIRES_MANUAL_REVIEW = "policy_requires_manual_review"
POLICY_SUPPORT_STATES: tuple[str, ...] = (
    POLICY_SUPPORTED,
    POLICY_PROHIBITED,
    POLICY_UNSUPPORTED,
    POLICY_BLOCKED,
    POLICY_REQUIRES_MANUAL_REVIEW,
)

POLICY_CLASSIFICATION_GOVERNANCE_BOUNDARY = "governance_boundary"
POLICY_CLASSIFICATION_POLICY_MODELING = "policy_modeling"
POLICY_CLASSIFICATION_POLICY_EXPLAINABILITY = "policy_explainability"
POLICY_CLASSIFICATION_POLICY_INTEGRITY = "policy_integrity"
POLICY_CLASSIFICATION_ORCHESTRATION_EXECUTION = "orchestration_execution"
POLICY_CLASSIFICATION_ORCHESTRATION_ROUTING = "orchestration_routing"
POLICY_CLASSIFICATION_AUTONOMOUS_ORCHESTRATION = "autonomous_orchestration"
POLICY_CLASSIFICATION_PRODUCTION_RUNTIME_ACCESS = "production_runtime_access"
POLICY_CLASSIFICATIONS: tuple[str, ...] = (
    POLICY_CLASSIFICATION_GOVERNANCE_BOUNDARY,
    POLICY_CLASSIFICATION_POLICY_MODELING,
    POLICY_CLASSIFICATION_POLICY_EXPLAINABILITY,
    POLICY_CLASSIFICATION_POLICY_INTEGRITY,
    POLICY_CLASSIFICATION_ORCHESTRATION_EXECUTION,
    POLICY_CLASSIFICATION_ORCHESTRATION_ROUTING,
    POLICY_CLASSIFICATION_AUTONOMOUS_ORCHESTRATION,
    POLICY_CLASSIFICATION_PRODUCTION_RUNTIME_ACCESS,
)

POLICY_DEPENDENCY_SATISFIED = "policy_dependency_satisfied"
POLICY_DEPENDENCY_MISSING = "policy_dependency_missing"
POLICY_DEPENDENCY_GAP = "policy_dependency_gap"
POLICY_DEPENDENCY_UNSUPPORTED = "policy_dependency_unsupported"
POLICY_DEPENDENCY_PROHIBITED = "policy_dependency_prohibited"
POLICY_DEPENDENCY_STATES: tuple[str, ...] = (
    POLICY_DEPENDENCY_SATISFIED,
    POLICY_DEPENDENCY_MISSING,
    POLICY_DEPENDENCY_GAP,
    POLICY_DEPENDENCY_UNSUPPORTED,
    POLICY_DEPENDENCY_PROHIBITED,
)

POLICY_CONTINUITY_PRESERVED = "policy_continuity_preserved"
POLICY_CONTINUITY_GAP = "policy_continuity_gap"
POLICY_CONTINUITY_NOT_APPLICABLE = "policy_continuity_not_applicable"
POLICY_CONTINUITY_STATES: tuple[str, ...] = (
    POLICY_CONTINUITY_PRESERVED,
    POLICY_CONTINUITY_GAP,
    POLICY_CONTINUITY_NOT_APPLICABLE,
)

POLICY_BLOCKED_BY_PROHIBITION = "policy_blocked_by_prohibition"
POLICY_BLOCKED_BY_UNSUPPORTED_STATE = "policy_blocked_by_unsupported_state"
POLICY_BLOCKED_BY_MISSING_DEPENDENCY = "policy_blocked_by_missing_dependency"
POLICY_BLOCKED_BY_DEPENDENCY_GAP = "policy_blocked_by_dependency_gap"
POLICY_BLOCKED_BY_GOVERNANCE_GAP = "policy_blocked_by_governance_gap"
POLICY_BLOCKED_BY_PROVENANCE_GAP = "policy_blocked_by_provenance_gap"
POLICY_BLOCKED_BY_INTEGRITY_GAP = "policy_blocked_by_integrity_gap"
POLICY_BLOCKED_BY_EXPLAINABILITY_GAP = "policy_blocked_by_explainability_gap"
POLICY_BLOCKED_BY_HASH_MISMATCH = "policy_blocked_by_hash_mismatch"
POLICY_BLOCKED_BY_EXECUTION_LEAK = "policy_blocked_by_execution_leak"
POLICY_BLOCKED_BY_PRODUCTION_LEAK = "policy_blocked_by_production_leak"
POLICY_BLOCKER_STATES: tuple[str, ...] = (
    POLICY_BLOCKED_BY_PROHIBITION,
    POLICY_BLOCKED_BY_UNSUPPORTED_STATE,
    POLICY_BLOCKED_BY_MISSING_DEPENDENCY,
    POLICY_BLOCKED_BY_DEPENDENCY_GAP,
    POLICY_BLOCKED_BY_GOVERNANCE_GAP,
    POLICY_BLOCKED_BY_PROVENANCE_GAP,
    POLICY_BLOCKED_BY_INTEGRITY_GAP,
    POLICY_BLOCKED_BY_EXPLAINABILITY_GAP,
    POLICY_BLOCKED_BY_HASH_MISMATCH,
    POLICY_BLOCKED_BY_EXECUTION_LEAK,
    POLICY_BLOCKED_BY_PRODUCTION_LEAK,
)

POLICY_EVALUATION_STABLE = "policy_evaluation_stable"
POLICY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS = "policy_evaluation_stable_with_visible_blockers"
POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP = "policy_evaluation_blocked_by_policy_continuity_gap"
POLICY_EVALUATION_REQUIRES_MANUAL_REVIEW = "policy_evaluation_requires_manual_review"
POLICY_EVALUATION_STATUSES: tuple[str, ...] = (
    POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP,
    POLICY_EVALUATION_REQUIRES_MANUAL_REVIEW,
    POLICY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS,
    POLICY_EVALUATION_STABLE,
)

POLICY_EXPLAINABILITY_STABLE = "policy_explainability_stable"
POLICY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "policy_explainability_blocked_by_visibility_gap"
POLICY_EXPLAINABILITY_STATUSES: tuple[str, ...] = (
    POLICY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    POLICY_EXPLAINABILITY_STABLE,
)

POLICY_INTEGRITY_STABLE = "policy_integrity_stable"
POLICY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP = "policy_integrity_blocked_by_registry_gap"
POLICY_INTEGRITY_BLOCKED_BY_POLICY_HASH_GAP = "policy_integrity_blocked_by_policy_hash_gap"
POLICY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP = "policy_integrity_blocked_by_provenance_gap"
POLICY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP = "policy_integrity_blocked_by_dependency_gap"
POLICY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP = "policy_integrity_blocked_by_governance_gap"
POLICY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "policy_integrity_blocked_by_explainability_gap"
POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH = "policy_integrity_blocked_by_hash_mismatch"
POLICY_INTEGRITY_REQUIRES_MANUAL_REVIEW = "policy_integrity_requires_manual_review"
POLICY_INTEGRITY_STATUSES: tuple[str, ...] = (
    POLICY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_POLICY_HASH_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH,
    POLICY_INTEGRITY_REQUIRES_MANUAL_REVIEW,
    POLICY_INTEGRITY_STABLE,
)


@dataclass(frozen=True)
class OrchestrationPolicyIdentifier:
    policy_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationPolicyProvenance:
    source_phase: str
    source_artifact: str
    upstream_policy_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyDependency:
    dependency_id: str
    required_policy_id: str
    required_support_states: tuple[str, ...]
    continuity_reference_id: str
    blocker_state: str = POLICY_BLOCKED_BY_DEPENDENCY_GAP


@dataclass(frozen=True)
class OrchestrationPolicyDefinition:
    identifier: OrchestrationPolicyIdentifier
    display_name: str
    classification: str
    support_state: str
    allowed_state_ids: tuple[str, ...]
    prohibited_state_ids: tuple[str, ...]
    unsupported_state_ids: tuple[str, ...]
    dependencies: tuple[OrchestrationPolicyDependency, ...]
    provenance: OrchestrationPolicyProvenance
    governance_metadata: Mapping[str, Any]
    support_rationale: tuple[str, ...]
    blocker_reasons: tuple[str, ...]
    integrity_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    manual_review_reasons: tuple[str, ...] = ()
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
    policy_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyRegistry:
    registry_id: str
    schema_version: str
    policies: tuple[OrchestrationPolicyDefinition, ...]
    registry_metadata: Mapping[str, Any]
    planning_only: bool = True
    non_production: bool = True


@dataclass(frozen=True)
class OrchestrationPolicyBlocker:
    policy_id: str
    blocker_state: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyEvaluationRecord:
    policy_id: str
    classification: str
    support_state: str
    effective_state: str
    policy_hash: str
    dependency_state: str
    dependency_chain: tuple[str, ...]
    governance_continuity_state: str
    provenance_continuity_state: str
    integrity_continuity_state: str
    explainability_continuity_state: str
    blockers: tuple[OrchestrationPolicyBlocker, ...]


@dataclass(frozen=True)
class OrchestrationPolicyEvaluationInput:
    registry: OrchestrationPolicyRegistry
    expected_registry_hash: str | None = None
    expected_policy_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationPolicyEvaluationResult:
    registry_id: str
    policy_evaluation_status: str
    planning_only: bool
    non_production: bool
    policy_records: tuple[OrchestrationPolicyEvaluationRecord, ...]
    registered_policy_count: int
    supported_policy_count: int
    prohibited_policy_count: int
    unsupported_policy_count: int
    blocker_count: int
    supported_policy_ids: tuple[str, ...]
    prohibited_policy_ids: tuple[str, ...]
    unsupported_policy_ids: tuple[str, ...]
    dependency_continuity_status: str
    provenance_continuity_status: str
    governance_continuity_status: str
    integrity_continuity_status: str
    explainability_continuity_status: str
    blocker_summary: tuple[OrchestrationPolicyBlocker, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_registry_hash: str
    deterministic_policy_evaluation_hash: str
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
    policy_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyExplanationRecord:
    policy_id: str
    explanation_status: str
    support_state: str
    classification: str
    why_supported: tuple[str, ...]
    why_blocked: tuple[str, ...]
    why_prohibited: tuple[str, ...]
    why_unsupported: tuple[str, ...]
    dependency_chain_visibility: tuple[str, ...]
    governance_chain_visibility: tuple[str, ...]
    continuity_gap_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]
    blocker_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyExplainabilityResult:
    registry_id: str
    explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationPolicyExplanationRecord, ...]
    supported_explanation_count: int
    prohibited_explanation_count: int
    unsupported_explanation_count: int
    blocked_explanation_count: int
    dependency_chain_visibility_count: int
    governance_chain_visibility_count: int
    continuity_gap_visibility_count: int
    provenance_visibility_count: int
    integrity_visibility_count: int
    deterministic_explainability_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    policy_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyIntegrityInput:
    registry: OrchestrationPolicyRegistry
    evaluation_result: OrchestrationPolicyEvaluationResult
    explainability_result: OrchestrationPolicyExplainabilityResult
    expected_registry_hash: str | None = None
    expected_evaluation_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationPolicyIntegrityResult:
    registry_id: str
    policy_integrity_status: str
    planning_only: bool
    registry_integrity: OrchestrationPolicyIntegritySummary
    policy_hash_integrity: OrchestrationPolicyIntegritySummary
    provenance_integrity: OrchestrationPolicyIntegritySummary
    dependency_integrity: OrchestrationPolicyIntegritySummary
    governance_integrity: OrchestrationPolicyIntegritySummary
    explainability_integrity: OrchestrationPolicyIntegritySummary
    evaluation_integrity: OrchestrationPolicyIntegritySummary
    deterministic_serialization_integrity: OrchestrationPolicyIntegritySummary
    blocker_visibility_integrity: OrchestrationPolicyIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_policy_integrity_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    policy_execution_enabled: bool = False


def export_policy_identifier(identifier: OrchestrationPolicyIdentifier) -> dict[str, Any]:
    return asdict(identifier)


def export_policy_provenance(provenance: OrchestrationPolicyProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field in (
        "upstream_policy_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
        "governance_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def export_policy_dependency(dependency: OrchestrationPolicyDependency) -> dict[str, Any]:
    data = asdict(dependency)
    data["required_support_states"] = sorted(data["required_support_states"])
    return data


def export_policy_definition(policy: OrchestrationPolicyDefinition) -> dict[str, Any]:
    data = _export_policy_definition_base(policy)
    data["deterministic_policy_hash"] = hash_policy_definition(policy)
    return data


def serialize_policy_definition(policy: OrchestrationPolicyDefinition) -> str:
    return stable_serialize(export_policy_definition(policy))


def hash_policy_definition(policy: OrchestrationPolicyDefinition) -> str:
    return deterministic_hash(_export_policy_definition_base(policy))


def export_policy_registry(registry: OrchestrationPolicyRegistry) -> dict[str, Any]:
    data = asdict(registry)
    data["policies"] = [
        export_policy_definition(policy)
        for policy in sorted(registry.policies, key=lambda item: item.identifier.policy_id)
    ]
    data["registry_metadata"] = dict(sorted(registry.registry_metadata.items()))
    data["deterministic_registry_hash"] = hash_policy_registry(registry)
    return data


def serialize_policy_registry(registry: OrchestrationPolicyRegistry) -> str:
    return stable_serialize(export_policy_registry(registry))


def hash_policy_registry(registry: OrchestrationPolicyRegistry) -> str:
    return deterministic_hash(
        {
            "registry_id": registry.registry_id,
            "schema_version": registry.schema_version,
            "policies": [
                export_policy_definition(policy)
                for policy in sorted(registry.policies, key=lambda item: item.identifier.policy_id)
            ],
            "registry_metadata": dict(sorted(registry.registry_metadata.items())),
            "planning_only": registry.planning_only,
            "non_production": registry.non_production,
        }
    )


def export_policy_blocker(blocker: OrchestrationPolicyBlocker) -> dict[str, Any]:
    data = asdict(blocker)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_policy_evaluation_record(record: OrchestrationPolicyEvaluationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["dependency_chain"] = sorted(data["dependency_chain"])
    data["blockers"] = [export_policy_blocker(item) for item in sorted(record.blockers, key=_blocker_sort_key)]
    return data


def export_policy_evaluation_result(result: OrchestrationPolicyEvaluationResult) -> dict[str, Any]:
    data = asdict(result)
    data["policy_records"] = [
        export_policy_evaluation_record(record)
        for record in sorted(result.policy_records, key=lambda item: item.policy_id)
    ]
    for field in (
        "supported_policy_ids",
        "prohibited_policy_ids",
        "unsupported_policy_ids",
        "manual_review_summary",
    ):
        data[field] = sorted(data[field])
    data["blocker_summary"] = [export_policy_blocker(item) for item in sorted(result.blocker_summary, key=_blocker_sort_key)]
    return data


def serialize_policy_evaluation_result(result: OrchestrationPolicyEvaluationResult) -> str:
    return stable_serialize(export_policy_evaluation_result(result))


def hash_policy_evaluation_result(result: OrchestrationPolicyEvaluationResult) -> str:
    data = export_policy_evaluation_result(result)
    data.pop("deterministic_policy_evaluation_hash", None)
    return deterministic_hash(data)


def export_policy_explanation_record(record: OrchestrationPolicyExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "why_supported",
        "why_blocked",
        "why_prohibited",
        "why_unsupported",
        "dependency_chain_visibility",
        "governance_chain_visibility",
        "continuity_gap_visibility",
        "provenance_visibility",
        "integrity_visibility",
        "blocker_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_policy_explainability_result(result: OrchestrationPolicyExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_policy_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.policy_id)
    ]
    return data


def serialize_policy_explainability_result(result: OrchestrationPolicyExplainabilityResult) -> str:
    return stable_serialize(export_policy_explainability_result(result))


def hash_policy_explainability_result(result: OrchestrationPolicyExplainabilityResult) -> str:
    data = export_policy_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)


def export_policy_integrity_summary(summary: OrchestrationPolicyIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_policy_integrity_result(result: OrchestrationPolicyIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "registry_integrity",
        "policy_hash_integrity",
        "provenance_integrity",
        "dependency_integrity",
        "governance_integrity",
        "explainability_integrity",
        "evaluation_integrity",
        "deterministic_serialization_integrity",
        "blocker_visibility_integrity",
    ):
        data[field] = export_policy_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_policy_integrity_result(result: OrchestrationPolicyIntegrityResult) -> str:
    return stable_serialize(export_policy_integrity_result(result))


def hash_policy_integrity_result(result: OrchestrationPolicyIntegrityResult) -> str:
    data = export_policy_integrity_result(result)
    data.pop("deterministic_policy_integrity_hash", None)
    return deterministic_hash(data)


def _export_policy_definition_base(policy: OrchestrationPolicyDefinition) -> dict[str, Any]:
    data = asdict(policy)
    data["identifier"] = export_policy_identifier(policy.identifier)
    data["dependencies"] = [
        export_policy_dependency(dependency)
        for dependency in sorted(policy.dependencies, key=lambda item: item.dependency_id)
    ]
    data["provenance"] = export_policy_provenance(policy.provenance)
    data["governance_metadata"] = dict(sorted(policy.governance_metadata.items()))
    for field in (
        "allowed_state_ids",
        "prohibited_state_ids",
        "unsupported_state_ids",
        "support_rationale",
        "blocker_reasons",
        "integrity_reference_ids",
        "explainability_reference_ids",
        "manual_review_reasons",
    ):
        data[field] = sorted(data[field])
    return data


def _blocker_sort_key(blocker: OrchestrationPolicyBlocker) -> tuple[str, str, str]:
    return (blocker.policy_id, blocker.blocker_state, blocker.reason)
