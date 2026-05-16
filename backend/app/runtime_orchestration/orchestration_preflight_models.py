"""Deterministic orchestration preflight models for v3.6 Phase 6."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


PREFLIGHT_SUPPORTED = "preflight_supported"
PREFLIGHT_UNSUPPORTED = "preflight_unsupported"
PREFLIGHT_PROHIBITED = "preflight_prohibited"
PREFLIGHT_GOVERNANCE_BLOCKED = "preflight_governance_blocked"
PREFLIGHT_COMPATIBILITY_BLOCKED = "preflight_compatibility_blocked"
PREFLIGHT_DEPENDENCY_BLOCKED = "preflight_dependency_blocked"
PREFLIGHT_CONTINUITY_BLOCKED = "preflight_continuity_blocked"
PREFLIGHT_PROVENANCE_BLOCKED = "preflight_provenance_blocked"
PREFLIGHT_EXPLAINABILITY_BLOCKED = "preflight_explainability_blocked"
PREFLIGHT_STATES: tuple[str, ...] = (
    PREFLIGHT_SUPPORTED,
    PREFLIGHT_UNSUPPORTED,
    PREFLIGHT_PROHIBITED,
    PREFLIGHT_GOVERNANCE_BLOCKED,
    PREFLIGHT_COMPATIBILITY_BLOCKED,
    PREFLIGHT_DEPENDENCY_BLOCKED,
    PREFLIGHT_CONTINUITY_BLOCKED,
    PREFLIGHT_PROVENANCE_BLOCKED,
    PREFLIGHT_EXPLAINABILITY_BLOCKED,
)

PREFLIGHT_CLASSIFICATION_THEORETICAL_SUPPORT = "preflight_theoretical_support_evaluation"
PREFLIGHT_CLASSIFICATION_GOVERNANCE = "preflight_governance_boundary_evaluation"
PREFLIGHT_CLASSIFICATION_COMPATIBILITY = "preflight_compatibility_domain_evaluation"
PREFLIGHT_CLASSIFICATION_DEPENDENCY = "preflight_dependency_domain_evaluation"
PREFLIGHT_CLASSIFICATION_BLOCKER = "preflight_blocker_domain_evaluation"
PREFLIGHT_CLASSIFICATION_UNSUPPORTED = "preflight_unsupported_domain_evaluation"
PREFLIGHT_CLASSIFICATION_PROHIBITED = "preflight_prohibited_domain_evaluation"
PREFLIGHT_CLASSIFICATION_CONTINUITY = "preflight_continuity_evaluation"
PREFLIGHT_CLASSIFICATIONS: tuple[str, ...] = (
    PREFLIGHT_CLASSIFICATION_THEORETICAL_SUPPORT,
    PREFLIGHT_CLASSIFICATION_GOVERNANCE,
    PREFLIGHT_CLASSIFICATION_COMPATIBILITY,
    PREFLIGHT_CLASSIFICATION_DEPENDENCY,
    PREFLIGHT_CLASSIFICATION_BLOCKER,
    PREFLIGHT_CLASSIFICATION_UNSUPPORTED,
    PREFLIGHT_CLASSIFICATION_PROHIBITED,
    PREFLIGHT_CLASSIFICATION_CONTINUITY,
)

PREFLIGHT_CLASSIFIED_AS_SUPPORTED = "preflight_classified_as_supported"
PREFLIGHT_CLASSIFIED_AS_UNSUPPORTED = "preflight_classified_as_unsupported"
PREFLIGHT_CLASSIFIED_AS_PROHIBITED = "preflight_classified_as_prohibited"
PREFLIGHT_CLASSIFIED_AS_GOVERNANCE_BLOCKED = "preflight_classified_as_governance_blocked"
PREFLIGHT_CLASSIFIED_AS_COMPATIBILITY_BLOCKED = "preflight_classified_as_compatibility_blocked"
PREFLIGHT_CLASSIFIED_AS_DEPENDENCY_BLOCKED = "preflight_classified_as_dependency_blocked"
PREFLIGHT_CLASSIFIED_AS_CONTINUITY_BLOCKED = "preflight_classified_as_continuity_blocked"
PREFLIGHT_CLASSIFIED_AS_PROVENANCE_BLOCKED = "preflight_classified_as_provenance_blocked"
PREFLIGHT_CLASSIFIED_AS_EXPLAINABILITY_BLOCKED = "preflight_classified_as_explainability_blocked"
PREFLIGHT_GOVERNANCE_BOUNDARY_VISIBLE = "preflight_governance_boundary_visible"
PREFLIGHT_COMPATIBILITY_DOMAIN_VISIBLE = "preflight_compatibility_domain_visible"
PREFLIGHT_DEPENDENCY_DOMAIN_VISIBLE = "preflight_dependency_domain_visible"
PREFLIGHT_BLOCKER_DOMAIN_VISIBLE = "preflight_blocker_domain_visible"
PREFLIGHT_UNSUPPORTED_DOMAIN_VISIBLE = "preflight_unsupported_domain_visible"
PREFLIGHT_PROHIBITED_DOMAIN_VISIBLE = "preflight_prohibited_domain_visible"
PREFLIGHT_SUPPORTED_DOMAIN_VISIBLE = "preflight_supported_domain_visible"
PREFLIGHT_POLICY_VISIBLE = "preflight_policy_visible"
PREFLIGHT_PROVENANCE_GAP = "preflight_provenance_gap"
PREFLIGHT_EXPLAINABILITY_GAP = "preflight_explainability_gap"
PREFLIGHT_INTEGRITY_GAP = "preflight_integrity_gap"
PREFLIGHT_HASH_MISMATCH = "preflight_hash_mismatch"
PREFLIGHT_GOVERNANCE_BOUNDARY_GAP = "preflight_governance_boundary_gap"
PREFLIGHT_POLICY_GAP = "preflight_policy_gap"

PREFLIGHT_CONTINUITY_PRESERVED = "preflight_continuity_preserved"
PREFLIGHT_CONTINUITY_GAP = "preflight_continuity_gap"

PREFLIGHT_EVALUATION_STABLE = "preflight_evaluation_stable"
PREFLIGHT_EVALUATION_STABLE_WITH_VISIBLE_FINDINGS = "preflight_evaluation_stable_with_visible_findings"
PREFLIGHT_EVALUATION_BLOCKED_BY_CONTINUITY_GAP = "preflight_evaluation_blocked_by_continuity_gap"

PREFLIGHT_EXPLAINABILITY_STABLE = "preflight_explainability_stable"
PREFLIGHT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "preflight_explainability_blocked_by_visibility_gap"

PREFLIGHT_INTEGRITY_STABLE = "preflight_integrity_stable"
PREFLIGHT_INTEGRITY_BLOCKED_BY_REGISTRY_GAP = "preflight_integrity_blocked_by_registry_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_HASH_GAP = "preflight_integrity_blocked_by_hash_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP = "preflight_integrity_blocked_by_provenance_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "preflight_integrity_blocked_by_explainability_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP = "preflight_integrity_blocked_by_governance_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP = "preflight_integrity_blocked_by_compatibility_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP = "preflight_integrity_blocked_by_dependency_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_BLOCKER_GAP = "preflight_integrity_blocked_by_blocker_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP = "preflight_integrity_blocked_by_supported_domain_gap"
PREFLIGHT_INTEGRITY_BLOCKED_BY_POLICY_GAP = "preflight_integrity_blocked_by_policy_gap"


@dataclass(frozen=True)
class OrchestrationPreflightIdentifier:
    preflight_id: str
    intent_id: str
    mapping_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationPreflightProvenance:
    source_phase: str
    source_artifact: str
    intent_id: str
    mapping_id: str
    policy_ids: tuple[str, ...]
    compatibility_relationship_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPreflightRecord:
    identifier: OrchestrationPreflightIdentifier
    preflight_state: str
    preflight_classifications: tuple[str, ...]
    theoretically_supportable: bool
    policy_ids: tuple[str, ...]
    governance_boundaries: tuple[str, ...]
    compatibility_domains: tuple[str, ...]
    dependency_domains: tuple[str, ...]
    blocker_domains: tuple[str, ...]
    unsupported_domains: tuple[str, ...]
    prohibited_domains: tuple[str, ...]
    supported_domains: tuple[str, ...]
    preflight_rationale: tuple[str, ...]
    provenance: OrchestrationPreflightProvenance
    governance_metadata: Mapping[str, Any]
    explainability_reference_ids: tuple[str, ...]
    integrity_reference_ids: tuple[str, ...]
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    background_processing_enabled: bool = False
    recommendation_behavior_enabled: bool = False
    optimization_behavior_enabled: bool = False
    autonomous_behavior_enabled: bool = False
    graph_execution_enabled: bool = False
    preflight_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPreflightRegistry:
    registry_id: str
    schema_version: str
    records: tuple[OrchestrationPreflightRecord, ...]
    registry_metadata: Mapping[str, Any]
    planning_only: bool = True
    non_production: bool = True


@dataclass(frozen=True)
class OrchestrationPreflightFinding:
    preflight_id: str
    intent_id: str
    classification: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPreflightEvaluationRecord:
    preflight_id: str
    intent_id: str
    preflight_state: str
    preflight_hash: str
    theoretically_supportable: bool
    policy_count: int
    governance_boundary_count: int
    compatibility_domain_count: int
    dependency_domain_count: int
    blocker_domain_count: int
    unsupported_domain_count: int
    prohibited_domain_count: int
    supported_domain_count: int
    provenance_continuity_state: str
    explainability_continuity_state: str
    integrity_continuity_state: str
    governance_continuity_state: str
    findings: tuple[OrchestrationPreflightFinding, ...]


@dataclass(frozen=True)
class OrchestrationPreflightEvaluationInput:
    preflight_registry: OrchestrationPreflightRegistry
    expected_registry_hash: str | None = None
    expected_preflight_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationPreflightEvaluationResult:
    registry_id: str
    preflight_evaluation_status: str
    planning_only: bool
    evaluation_records: tuple[OrchestrationPreflightEvaluationRecord, ...]
    registered_preflight_count: int
    supported_preflight_count: int
    unsupported_preflight_count: int
    prohibited_preflight_count: int
    governance_blocked_count: int
    compatibility_blocked_count: int
    dependency_blocked_count: int
    continuity_blocked_count: int
    provenance_blocked_count: int
    explainability_blocked_count: int
    policy_count: int
    governance_boundary_count: int
    compatibility_domain_count: int
    dependency_domain_count: int
    blocker_domain_count: int
    unsupported_domain_count: int
    prohibited_domain_count: int
    supported_domain_count: int
    provenance_continuity_status: str
    explainability_continuity_status: str
    integrity_continuity_status: str
    governance_continuity_status: str
    finding_summary: tuple[OrchestrationPreflightFinding, ...]
    deterministic_registry_hash: str
    deterministic_preflight_evaluation_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    recommendation_behavior_enabled: bool = False
    optimization_behavior_enabled: bool = False
    autonomous_behavior_enabled: bool = False
    graph_execution_enabled: bool = False
    preflight_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPreflightExplanationRecord:
    preflight_id: str
    intent_id: str
    preflight_state: str
    explanation_status: str
    theoretical_supportability_visibility: tuple[str, ...]
    policy_visibility: tuple[str, ...]
    governance_boundary_visibility: tuple[str, ...]
    compatibility_domain_visibility: tuple[str, ...]
    dependency_domain_visibility: tuple[str, ...]
    blocker_domain_visibility: tuple[str, ...]
    unsupported_domain_visibility: tuple[str, ...]
    prohibited_domain_visibility: tuple[str, ...]
    supported_domain_visibility: tuple[str, ...]
    preflight_rationale_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    evaluation_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPreflightExplainabilityResult:
    registry_id: str
    preflight_explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationPreflightExplanationRecord, ...]
    supported_explanation_count: int
    unsupported_explanation_count: int
    prohibited_explanation_count: int
    governance_blocked_explanation_count: int
    compatibility_blocked_explanation_count: int
    dependency_blocked_explanation_count: int
    policy_visibility_count: int
    governance_boundary_visibility_count: int
    compatibility_domain_visibility_count: int
    dependency_domain_visibility_count: int
    blocker_domain_visibility_count: int
    unsupported_domain_visibility_count: int
    prohibited_domain_visibility_count: int
    deterministic_preflight_explainability_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    recommendation_behavior_enabled: bool = False
    optimization_behavior_enabled: bool = False
    autonomous_behavior_enabled: bool = False
    graph_execution_enabled: bool = False
    preflight_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPreflightIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPreflightIntegrityInput:
    preflight_registry: OrchestrationPreflightRegistry
    evaluation_result: OrchestrationPreflightEvaluationResult
    explainability_result: OrchestrationPreflightExplainabilityResult
    expected_registry_hash: str | None = None
    expected_evaluation_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationPreflightIntegrityResult:
    registry_id: str
    preflight_integrity_status: str
    planning_only: bool
    registry_integrity: OrchestrationPreflightIntegritySummary
    preflight_hash_integrity: OrchestrationPreflightIntegritySummary
    provenance_integrity: OrchestrationPreflightIntegritySummary
    explainability_integrity: OrchestrationPreflightIntegritySummary
    governance_integrity: OrchestrationPreflightIntegritySummary
    compatibility_integrity: OrchestrationPreflightIntegritySummary
    dependency_integrity: OrchestrationPreflightIntegritySummary
    blocker_integrity: OrchestrationPreflightIntegritySummary
    supported_domain_integrity: OrchestrationPreflightIntegritySummary
    policy_integrity: OrchestrationPreflightIntegritySummary
    deterministic_serialization_integrity: OrchestrationPreflightIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_preflight_integrity_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    recommendation_behavior_enabled: bool = False
    optimization_behavior_enabled: bool = False
    autonomous_behavior_enabled: bool = False
    graph_execution_enabled: bool = False
    preflight_execution_enabled: bool = False


def export_preflight_provenance(provenance: OrchestrationPreflightProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field in (
        "policy_ids",
        "compatibility_relationship_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
        "governance_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def export_preflight_record(record: OrchestrationPreflightRecord) -> dict[str, Any]:
    data = _export_preflight_record_base(record)
    data["deterministic_preflight_hash"] = hash_preflight_record(record)
    return data


def serialize_preflight_record(record: OrchestrationPreflightRecord) -> str:
    return stable_serialize(export_preflight_record(record))


def hash_preflight_record(record: OrchestrationPreflightRecord) -> str:
    return deterministic_hash(_export_preflight_record_base(record))


def export_preflight_registry(registry: OrchestrationPreflightRegistry) -> dict[str, Any]:
    data = asdict(registry)
    data["records"] = [
        export_preflight_record(record)
        for record in sorted(registry.records, key=lambda item: item.identifier.preflight_id)
    ]
    data["registry_metadata"] = dict(sorted(registry.registry_metadata.items()))
    data["deterministic_preflight_registry_hash"] = hash_preflight_registry(registry)
    return data


def serialize_preflight_registry(registry: OrchestrationPreflightRegistry) -> str:
    return stable_serialize(export_preflight_registry(registry))


def hash_preflight_registry(registry: OrchestrationPreflightRegistry) -> str:
    return deterministic_hash(
        {
            "registry_id": registry.registry_id,
            "schema_version": registry.schema_version,
            "records": [
                export_preflight_record(record)
                for record in sorted(registry.records, key=lambda item: item.identifier.preflight_id)
            ],
            "registry_metadata": dict(sorted(registry.registry_metadata.items())),
            "planning_only": registry.planning_only,
            "non_production": registry.non_production,
        }
    )


def export_preflight_finding(finding: OrchestrationPreflightFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_preflight_evaluation_record(record: OrchestrationPreflightEvaluationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["findings"] = [export_preflight_finding(finding) for finding in sorted(record.findings, key=_finding_sort_key)]
    return data


def export_preflight_evaluation_result(result: OrchestrationPreflightEvaluationResult) -> dict[str, Any]:
    data = asdict(result)
    data["evaluation_records"] = [
        export_preflight_evaluation_record(record)
        for record in sorted(result.evaluation_records, key=lambda item: item.preflight_id)
    ]
    data["finding_summary"] = [export_preflight_finding(finding) for finding in sorted(result.finding_summary, key=_finding_sort_key)]
    return data


def serialize_preflight_evaluation_result(result: OrchestrationPreflightEvaluationResult) -> str:
    return stable_serialize(export_preflight_evaluation_result(result))


def hash_preflight_evaluation_result(result: OrchestrationPreflightEvaluationResult) -> str:
    data = export_preflight_evaluation_result(result)
    data.pop("deterministic_preflight_evaluation_hash", None)
    return deterministic_hash(data)


def export_preflight_explanation_record(record: OrchestrationPreflightExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "theoretical_supportability_visibility",
        "policy_visibility",
        "governance_boundary_visibility",
        "compatibility_domain_visibility",
        "dependency_domain_visibility",
        "blocker_domain_visibility",
        "unsupported_domain_visibility",
        "prohibited_domain_visibility",
        "supported_domain_visibility",
        "preflight_rationale_visibility",
        "provenance_visibility",
        "evaluation_visibility",
        "integrity_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_preflight_explainability_result(result: OrchestrationPreflightExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_preflight_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.preflight_id)
    ]
    return data


def serialize_preflight_explainability_result(result: OrchestrationPreflightExplainabilityResult) -> str:
    return stable_serialize(export_preflight_explainability_result(result))


def hash_preflight_explainability_result(result: OrchestrationPreflightExplainabilityResult) -> str:
    data = export_preflight_explainability_result(result)
    data.pop("deterministic_preflight_explainability_hash", None)
    return deterministic_hash(data)


def export_preflight_integrity_summary(summary: OrchestrationPreflightIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_preflight_integrity_result(result: OrchestrationPreflightIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "registry_integrity",
        "preflight_hash_integrity",
        "provenance_integrity",
        "explainability_integrity",
        "governance_integrity",
        "compatibility_integrity",
        "dependency_integrity",
        "blocker_integrity",
        "supported_domain_integrity",
        "policy_integrity",
        "deterministic_serialization_integrity",
    ):
        data[field] = export_preflight_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_preflight_integrity_result(result: OrchestrationPreflightIntegrityResult) -> str:
    return stable_serialize(export_preflight_integrity_result(result))


def hash_preflight_integrity_result(result: OrchestrationPreflightIntegrityResult) -> str:
    data = export_preflight_integrity_result(result)
    data.pop("deterministic_preflight_integrity_hash", None)
    return deterministic_hash(data)


def _export_preflight_record_base(record: OrchestrationPreflightRecord) -> dict[str, Any]:
    data = asdict(record)
    data["identifier"] = asdict(record.identifier)
    data["provenance"] = export_preflight_provenance(record.provenance)
    data["governance_metadata"] = dict(sorted(record.governance_metadata.items()))
    for field in (
        "preflight_classifications",
        "policy_ids",
        "governance_boundaries",
        "compatibility_domains",
        "dependency_domains",
        "blocker_domains",
        "unsupported_domains",
        "prohibited_domains",
        "supported_domains",
        "preflight_rationale",
        "explainability_reference_ids",
        "integrity_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def _finding_sort_key(finding: OrchestrationPreflightFinding) -> tuple[str, str, str, str]:
    return (finding.preflight_id, finding.intent_id, finding.classification, finding.reason)
