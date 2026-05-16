"""Deterministic orchestration intent models for v3.6 Phase 4."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


INTENT_INFORMATIONAL = "informational_intent"
INTENT_COMPATIBILITY_CHECK = "compatibility_check_intent"
INTENT_GOVERNANCE_REVIEW = "governance_review_intent"
INTENT_DEPENDENCY_ANALYSIS = "dependency_analysis_intent"
INTENT_CONTINUITY_ANALYSIS = "continuity_analysis_intent"
INTENT_UNSUPPORTED_DOMAIN = "unsupported_domain_intent"
INTENT_PROHIBITED_DOMAIN = "prohibited_domain_intent"
INTENT_POLICY_BOUNDARY = "policy_boundary_intent"
INTENT_ORCHESTRATION_SIMULATION = "orchestration_simulation_intent"
INTENT_TYPES: tuple[str, ...] = (
    INTENT_INFORMATIONAL,
    INTENT_COMPATIBILITY_CHECK,
    INTENT_GOVERNANCE_REVIEW,
    INTENT_DEPENDENCY_ANALYSIS,
    INTENT_CONTINUITY_ANALYSIS,
    INTENT_UNSUPPORTED_DOMAIN,
    INTENT_PROHIBITED_DOMAIN,
    INTENT_POLICY_BOUNDARY,
    INTENT_ORCHESTRATION_SIMULATION,
)

INTENT_SUPPORTED = "intent_supported"
INTENT_UNSUPPORTED = "intent_unsupported"
INTENT_PROHIBITED = "intent_prohibited"
INTENT_SUPPORT_STATES: tuple[str, ...] = (
    INTENT_SUPPORTED,
    INTENT_UNSUPPORTED,
    INTENT_PROHIBITED,
)

INTENT_CLASSIFIED_AS_TYPE = "intent_classified_as_type"
INTENT_CLASSIFIED_AS_SUPPORTED = "intent_classified_as_supported"
INTENT_CLASSIFIED_AS_UNSUPPORTED = "intent_classified_as_unsupported"
INTENT_CLASSIFIED_AS_PROHIBITED = "intent_classified_as_prohibited"
INTENT_GOVERNANCE_BOUNDARY_VISIBLE = "intent_governance_boundary_visible"
INTENT_COMPATIBILITY_DOMAIN_VISIBLE = "intent_compatibility_domain_visible"
INTENT_DEPENDENCY_DOMAIN_VISIBLE = "intent_dependency_domain_visible"
INTENT_BLOCKER_DOMAIN_VISIBLE = "intent_blocker_domain_visible"
INTENT_UNSUPPORTED_DOMAIN_VISIBLE = "intent_unsupported_domain_visible"
INTENT_PROHIBITED_DOMAIN_VISIBLE = "intent_prohibited_domain_visible"
INTENT_PROVENANCE_GAP = "intent_provenance_gap"
INTENT_EXPLAINABILITY_GAP = "intent_explainability_gap"
INTENT_INTEGRITY_GAP = "intent_integrity_gap"
INTENT_HASH_MISMATCH = "intent_hash_mismatch"
INTENT_GOVERNANCE_BOUNDARY_GAP = "intent_governance_boundary_gap"

INTENT_CONTINUITY_PRESERVED = "intent_continuity_preserved"
INTENT_CONTINUITY_GAP = "intent_continuity_gap"

INTENT_CLASSIFICATION_STABLE = "intent_classification_stable"
INTENT_CLASSIFICATION_STABLE_WITH_VISIBLE_FINDINGS = "intent_classification_stable_with_visible_findings"
INTENT_CLASSIFICATION_BLOCKED_BY_CONTINUITY_GAP = "intent_classification_blocked_by_continuity_gap"

INTENT_EXPLAINABILITY_STABLE = "intent_explainability_stable"
INTENT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "intent_explainability_blocked_by_visibility_gap"

INTENT_INTEGRITY_STABLE = "intent_integrity_stable"
INTENT_INTEGRITY_BLOCKED_BY_REGISTRY_GAP = "intent_integrity_blocked_by_registry_gap"
INTENT_INTEGRITY_BLOCKED_BY_HASH_GAP = "intent_integrity_blocked_by_hash_gap"
INTENT_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP = "intent_integrity_blocked_by_provenance_gap"
INTENT_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "intent_integrity_blocked_by_explainability_gap"
INTENT_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP = "intent_integrity_blocked_by_governance_gap"
INTENT_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP = "intent_integrity_blocked_by_compatibility_gap"
INTENT_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP = "intent_integrity_blocked_by_dependency_gap"
INTENT_INTEGRITY_BLOCKED_BY_BLOCKER_GAP = "intent_integrity_blocked_by_blocker_gap"
INTENT_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP = "intent_integrity_blocked_by_supported_domain_gap"


@dataclass(frozen=True)
class OrchestrationIntentIdentifier:
    intent_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationIntentProvenance:
    source_phase: str
    source_artifact: str
    upstream_policy_ids: tuple[str, ...]
    compatibility_relationship_ids: tuple[str, ...]
    resolution_record_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntentRecord:
    identifier: OrchestrationIntentIdentifier
    intent_type: str
    support_state: str
    intent_goal: str
    policy_domains: tuple[str, ...]
    compatibility_domains: tuple[str, ...]
    dependency_domains: tuple[str, ...]
    governance_boundaries: tuple[str, ...]
    blocker_domains: tuple[str, ...]
    unsupported_domains: tuple[str, ...]
    prohibited_domains: tuple[str, ...]
    supported_domains: tuple[str, ...]
    provenance: OrchestrationIntentProvenance
    governance_metadata: Mapping[str, Any]
    classifier_evidence_ids: tuple[str, ...]
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


@dataclass(frozen=True)
class OrchestrationIntentRegistry:
    registry_id: str
    schema_version: str
    records: tuple[OrchestrationIntentRecord, ...]
    registry_metadata: Mapping[str, Any]
    planning_only: bool = True
    non_production: bool = True


@dataclass(frozen=True)
class OrchestrationIntentFinding:
    intent_id: str
    classification: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntentClassificationRecord:
    intent_id: str
    intent_type: str
    support_state: str
    intent_hash: str
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
    findings: tuple[OrchestrationIntentFinding, ...]


@dataclass(frozen=True)
class OrchestrationIntentClassificationInput:
    intent_registry: OrchestrationIntentRegistry
    expected_registry_hash: str | None = None
    expected_intent_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationIntentClassificationResult:
    registry_id: str
    intent_classification_status: str
    planning_only: bool
    classification_records: tuple[OrchestrationIntentClassificationRecord, ...]
    registered_intent_count: int
    supported_intent_count: int
    unsupported_intent_count: int
    prohibited_intent_count: int
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
    finding_summary: tuple[OrchestrationIntentFinding, ...]
    deterministic_registry_hash: str
    deterministic_intent_classification_hash: str
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


@dataclass(frozen=True)
class OrchestrationIntentExplanationRecord:
    intent_id: str
    intent_type: str
    support_state: str
    explanation_status: str
    intent_goal_visibility: tuple[str, ...]
    policy_domain_visibility: tuple[str, ...]
    compatibility_domain_visibility: tuple[str, ...]
    governance_boundary_visibility: tuple[str, ...]
    dependency_domain_visibility: tuple[str, ...]
    blocker_domain_visibility: tuple[str, ...]
    unsupported_domain_visibility: tuple[str, ...]
    prohibited_domain_visibility: tuple[str, ...]
    supported_domain_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    classification_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntentExplainabilityResult:
    registry_id: str
    intent_explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationIntentExplanationRecord, ...]
    supported_explanation_count: int
    unsupported_explanation_count: int
    prohibited_explanation_count: int
    governance_boundary_visibility_count: int
    compatibility_domain_visibility_count: int
    dependency_domain_visibility_count: int
    blocker_domain_visibility_count: int
    unsupported_domain_visibility_count: int
    prohibited_domain_visibility_count: int
    deterministic_intent_explainability_hash: str
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


@dataclass(frozen=True)
class OrchestrationIntentIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntentIntegrityInput:
    intent_registry: OrchestrationIntentRegistry
    classification_result: OrchestrationIntentClassificationResult
    explainability_result: OrchestrationIntentExplainabilityResult
    expected_registry_hash: str | None = None
    expected_classification_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationIntentIntegrityResult:
    registry_id: str
    intent_integrity_status: str
    planning_only: bool
    registry_integrity: OrchestrationIntentIntegritySummary
    intent_hash_integrity: OrchestrationIntentIntegritySummary
    provenance_integrity: OrchestrationIntentIntegritySummary
    explainability_integrity: OrchestrationIntentIntegritySummary
    governance_integrity: OrchestrationIntentIntegritySummary
    compatibility_integrity: OrchestrationIntentIntegritySummary
    dependency_integrity: OrchestrationIntentIntegritySummary
    blocker_integrity: OrchestrationIntentIntegritySummary
    supported_domain_integrity: OrchestrationIntentIntegritySummary
    deterministic_serialization_integrity: OrchestrationIntentIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_intent_integrity_hash: str
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


def export_intent_provenance(provenance: OrchestrationIntentProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field in (
        "upstream_policy_ids",
        "compatibility_relationship_ids",
        "resolution_record_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
        "governance_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def export_intent_record(record: OrchestrationIntentRecord) -> dict[str, Any]:
    data = _export_intent_record_base(record)
    data["deterministic_intent_hash"] = hash_intent_record(record)
    return data


def serialize_intent_record(record: OrchestrationIntentRecord) -> str:
    return stable_serialize(export_intent_record(record))


def hash_intent_record(record: OrchestrationIntentRecord) -> str:
    return deterministic_hash(_export_intent_record_base(record))


def export_intent_registry(registry: OrchestrationIntentRegistry) -> dict[str, Any]:
    data = asdict(registry)
    data["records"] = [
        export_intent_record(record)
        for record in sorted(registry.records, key=lambda item: item.identifier.intent_id)
    ]
    data["registry_metadata"] = dict(sorted(registry.registry_metadata.items()))
    data["deterministic_intent_registry_hash"] = hash_intent_registry(registry)
    return data


def serialize_intent_registry(registry: OrchestrationIntentRegistry) -> str:
    return stable_serialize(export_intent_registry(registry))


def hash_intent_registry(registry: OrchestrationIntentRegistry) -> str:
    return deterministic_hash(
        {
            "registry_id": registry.registry_id,
            "schema_version": registry.schema_version,
            "records": [
                export_intent_record(record)
                for record in sorted(registry.records, key=lambda item: item.identifier.intent_id)
            ],
            "registry_metadata": dict(sorted(registry.registry_metadata.items())),
            "planning_only": registry.planning_only,
            "non_production": registry.non_production,
        }
    )


def export_intent_finding(finding: OrchestrationIntentFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_intent_classification_record(record: OrchestrationIntentClassificationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["findings"] = [export_intent_finding(finding) for finding in sorted(record.findings, key=_finding_sort_key)]
    return data


def export_intent_classification_result(result: OrchestrationIntentClassificationResult) -> dict[str, Any]:
    data = asdict(result)
    data["classification_records"] = [
        export_intent_classification_record(record)
        for record in sorted(result.classification_records, key=lambda item: item.intent_id)
    ]
    data["finding_summary"] = [export_intent_finding(finding) for finding in sorted(result.finding_summary, key=_finding_sort_key)]
    return data


def serialize_intent_classification_result(result: OrchestrationIntentClassificationResult) -> str:
    return stable_serialize(export_intent_classification_result(result))


def hash_intent_classification_result(result: OrchestrationIntentClassificationResult) -> str:
    data = export_intent_classification_result(result)
    data.pop("deterministic_intent_classification_hash", None)
    return deterministic_hash(data)


def export_intent_explanation_record(record: OrchestrationIntentExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "intent_goal_visibility",
        "policy_domain_visibility",
        "compatibility_domain_visibility",
        "governance_boundary_visibility",
        "dependency_domain_visibility",
        "blocker_domain_visibility",
        "unsupported_domain_visibility",
        "prohibited_domain_visibility",
        "supported_domain_visibility",
        "provenance_visibility",
        "classification_visibility",
        "integrity_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_intent_explainability_result(result: OrchestrationIntentExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_intent_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.intent_id)
    ]
    return data


def serialize_intent_explainability_result(result: OrchestrationIntentExplainabilityResult) -> str:
    return stable_serialize(export_intent_explainability_result(result))


def hash_intent_explainability_result(result: OrchestrationIntentExplainabilityResult) -> str:
    data = export_intent_explainability_result(result)
    data.pop("deterministic_intent_explainability_hash", None)
    return deterministic_hash(data)


def export_intent_integrity_summary(summary: OrchestrationIntentIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_intent_integrity_result(result: OrchestrationIntentIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "registry_integrity",
        "intent_hash_integrity",
        "provenance_integrity",
        "explainability_integrity",
        "governance_integrity",
        "compatibility_integrity",
        "dependency_integrity",
        "blocker_integrity",
        "supported_domain_integrity",
        "deterministic_serialization_integrity",
    ):
        data[field] = export_intent_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_intent_integrity_result(result: OrchestrationIntentIntegrityResult) -> str:
    return stable_serialize(export_intent_integrity_result(result))


def hash_intent_integrity_result(result: OrchestrationIntentIntegrityResult) -> str:
    data = export_intent_integrity_result(result)
    data.pop("deterministic_intent_integrity_hash", None)
    return deterministic_hash(data)


def _export_intent_record_base(record: OrchestrationIntentRecord) -> dict[str, Any]:
    data = asdict(record)
    data["identifier"] = asdict(record.identifier)
    data["provenance"] = export_intent_provenance(record.provenance)
    data["governance_metadata"] = dict(sorted(record.governance_metadata.items()))
    for field in (
        "policy_domains",
        "compatibility_domains",
        "dependency_domains",
        "governance_boundaries",
        "blocker_domains",
        "unsupported_domains",
        "prohibited_domains",
        "supported_domains",
        "classifier_evidence_ids",
        "explainability_reference_ids",
        "integrity_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def _finding_sort_key(finding: OrchestrationIntentFinding) -> tuple[str, str, str]:
    return (finding.intent_id, finding.classification, finding.reason)
