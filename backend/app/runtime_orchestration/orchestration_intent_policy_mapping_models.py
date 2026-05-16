"""Deterministic orchestration intent-policy mapping models for v3.6 Phase 5."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


MAPPING_INTENT_TO_POLICY = "intent_to_policy_mapping"
MAPPING_INTENT_TO_GOVERNANCE = "intent_to_governance_mapping"
MAPPING_INTENT_TO_COMPATIBILITY = "intent_to_compatibility_mapping"
MAPPING_INTENT_TO_BLOCKER = "intent_to_blocker_mapping"
MAPPING_INTENT_TO_DEPENDENCY = "intent_to_dependency_mapping"
MAPPING_INTENT_TO_PROHIBITED_DOMAIN = "intent_to_prohibited_domain_mapping"
MAPPING_INTENT_TO_UNSUPPORTED_DOMAIN = "intent_to_unsupported_domain_mapping"
MAPPING_INTENT_TO_SUPPORTED_DOMAIN = "intent_to_supported_domain_mapping"
MAPPING_CLASSIFICATIONS: tuple[str, ...] = (
    MAPPING_INTENT_TO_POLICY,
    MAPPING_INTENT_TO_GOVERNANCE,
    MAPPING_INTENT_TO_COMPATIBILITY,
    MAPPING_INTENT_TO_BLOCKER,
    MAPPING_INTENT_TO_DEPENDENCY,
    MAPPING_INTENT_TO_PROHIBITED_DOMAIN,
    MAPPING_INTENT_TO_UNSUPPORTED_DOMAIN,
    MAPPING_INTENT_TO_SUPPORTED_DOMAIN,
)

MAPPING_SUPPORTED = "mapping_supported"
MAPPING_UNSUPPORTED = "mapping_unsupported"
MAPPING_PROHIBITED = "mapping_prohibited"
MAPPING_SUPPORT_STATES: tuple[str, ...] = (
    MAPPING_SUPPORTED,
    MAPPING_UNSUPPORTED,
    MAPPING_PROHIBITED,
)

MAPPING_CLASSIFIED_AS_SUPPORTED = "mapping_classified_as_supported"
MAPPING_CLASSIFIED_AS_UNSUPPORTED = "mapping_classified_as_unsupported"
MAPPING_CLASSIFIED_AS_PROHIBITED = "mapping_classified_as_prohibited"
MAPPING_POLICY_APPLICABILITY_VISIBLE = "mapping_policy_applicability_visible"
MAPPING_GOVERNANCE_BOUNDARY_VISIBLE = "mapping_governance_boundary_visible"
MAPPING_COMPATIBILITY_DOMAIN_VISIBLE = "mapping_compatibility_domain_visible"
MAPPING_DEPENDENCY_DOMAIN_VISIBLE = "mapping_dependency_domain_visible"
MAPPING_BLOCKER_DOMAIN_VISIBLE = "mapping_blocker_domain_visible"
MAPPING_UNSUPPORTED_DOMAIN_VISIBLE = "mapping_unsupported_domain_visible"
MAPPING_PROHIBITED_DOMAIN_VISIBLE = "mapping_prohibited_domain_visible"
MAPPING_SUPPORTED_DOMAIN_VISIBLE = "mapping_supported_domain_visible"
MAPPING_PROVENANCE_GAP = "mapping_provenance_gap"
MAPPING_EXPLAINABILITY_GAP = "mapping_explainability_gap"
MAPPING_INTEGRITY_GAP = "mapping_integrity_gap"
MAPPING_HASH_MISMATCH = "mapping_hash_mismatch"
MAPPING_GOVERNANCE_BOUNDARY_GAP = "mapping_governance_boundary_gap"
MAPPING_POLICY_APPLICABILITY_GAP = "mapping_policy_applicability_gap"

MAPPING_CONTINUITY_PRESERVED = "mapping_continuity_preserved"
MAPPING_CONTINUITY_GAP = "mapping_continuity_gap"

MAPPING_ANALYSIS_STABLE = "mapping_analysis_stable"
MAPPING_ANALYSIS_STABLE_WITH_VISIBLE_FINDINGS = "mapping_analysis_stable_with_visible_findings"
MAPPING_ANALYSIS_BLOCKED_BY_CONTINUITY_GAP = "mapping_analysis_blocked_by_continuity_gap"

MAPPING_EXPLAINABILITY_STABLE = "mapping_explainability_stable"
MAPPING_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "mapping_explainability_blocked_by_visibility_gap"

MAPPING_INTEGRITY_STABLE = "mapping_integrity_stable"
MAPPING_INTEGRITY_BLOCKED_BY_REGISTRY_GAP = "mapping_integrity_blocked_by_registry_gap"
MAPPING_INTEGRITY_BLOCKED_BY_HASH_GAP = "mapping_integrity_blocked_by_hash_gap"
MAPPING_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP = "mapping_integrity_blocked_by_provenance_gap"
MAPPING_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "mapping_integrity_blocked_by_explainability_gap"
MAPPING_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP = "mapping_integrity_blocked_by_governance_gap"
MAPPING_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP = "mapping_integrity_blocked_by_compatibility_gap"
MAPPING_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP = "mapping_integrity_blocked_by_dependency_gap"
MAPPING_INTEGRITY_BLOCKED_BY_BLOCKER_GAP = "mapping_integrity_blocked_by_blocker_gap"
MAPPING_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP = "mapping_integrity_blocked_by_supported_domain_gap"
MAPPING_INTEGRITY_BLOCKED_BY_POLICY_GAP = "mapping_integrity_blocked_by_policy_gap"


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingIdentifier:
    mapping_id: str
    intent_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingProvenance:
    source_phase: str
    source_artifact: str
    intent_id: str
    policy_ids: tuple[str, ...]
    compatibility_relationship_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingRecord:
    identifier: OrchestrationIntentPolicyMappingIdentifier
    mapping_state: str
    mapping_classifications: tuple[str, ...]
    policy_ids: tuple[str, ...]
    governance_boundaries: tuple[str, ...]
    compatibility_domains: tuple[str, ...]
    dependency_domains: tuple[str, ...]
    blocker_domains: tuple[str, ...]
    unsupported_domains: tuple[str, ...]
    prohibited_domains: tuple[str, ...]
    supported_domains: tuple[str, ...]
    mapping_rationale: tuple[str, ...]
    provenance: OrchestrationIntentPolicyMappingProvenance
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
    mapping_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingRegistry:
    registry_id: str
    schema_version: str
    records: tuple[OrchestrationIntentPolicyMappingRecord, ...]
    registry_metadata: Mapping[str, Any]
    planning_only: bool = True
    non_production: bool = True


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingFinding:
    mapping_id: str
    intent_id: str
    classification: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingAnalysisRecord:
    mapping_id: str
    intent_id: str
    mapping_state: str
    mapping_hash: str
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
    findings: tuple[OrchestrationIntentPolicyMappingFinding, ...]


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingInput:
    mapping_registry: OrchestrationIntentPolicyMappingRegistry
    expected_registry_hash: str | None = None
    expected_mapping_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingResult:
    registry_id: str
    mapping_analysis_status: str
    planning_only: bool
    analysis_records: tuple[OrchestrationIntentPolicyMappingAnalysisRecord, ...]
    registered_mapping_count: int
    supported_mapping_count: int
    unsupported_mapping_count: int
    prohibited_mapping_count: int
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
    finding_summary: tuple[OrchestrationIntentPolicyMappingFinding, ...]
    deterministic_registry_hash: str
    deterministic_mapping_analysis_hash: str
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
    mapping_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingExplanationRecord:
    mapping_id: str
    intent_id: str
    mapping_state: str
    explanation_status: str
    policy_applicability_visibility: tuple[str, ...]
    governance_boundary_visibility: tuple[str, ...]
    compatibility_domain_visibility: tuple[str, ...]
    dependency_domain_visibility: tuple[str, ...]
    blocker_domain_visibility: tuple[str, ...]
    unsupported_domain_visibility: tuple[str, ...]
    prohibited_domain_visibility: tuple[str, ...]
    supported_domain_visibility: tuple[str, ...]
    mapping_rationale_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    analysis_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingExplainabilityResult:
    registry_id: str
    mapping_explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationIntentPolicyMappingExplanationRecord, ...]
    supported_explanation_count: int
    unsupported_explanation_count: int
    prohibited_explanation_count: int
    policy_applicability_visibility_count: int
    governance_boundary_visibility_count: int
    compatibility_domain_visibility_count: int
    dependency_domain_visibility_count: int
    blocker_domain_visibility_count: int
    unsupported_domain_visibility_count: int
    prohibited_domain_visibility_count: int
    deterministic_mapping_explainability_hash: str
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
    mapping_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingIntegrityInput:
    mapping_registry: OrchestrationIntentPolicyMappingRegistry
    mapping_result: OrchestrationIntentPolicyMappingResult
    explainability_result: OrchestrationIntentPolicyMappingExplainabilityResult
    expected_registry_hash: str | None = None
    expected_mapping_analysis_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationIntentPolicyMappingIntegrityResult:
    registry_id: str
    mapping_integrity_status: str
    planning_only: bool
    registry_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    mapping_hash_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    provenance_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    explainability_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    governance_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    compatibility_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    dependency_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    blocker_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    supported_domain_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    policy_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    deterministic_serialization_integrity: OrchestrationIntentPolicyMappingIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_mapping_integrity_hash: str
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
    mapping_execution_enabled: bool = False


def export_mapping_provenance(provenance: OrchestrationIntentPolicyMappingProvenance) -> dict[str, Any]:
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


def export_mapping_record(record: OrchestrationIntentPolicyMappingRecord) -> dict[str, Any]:
    data = _export_mapping_record_base(record)
    data["deterministic_mapping_hash"] = hash_mapping_record(record)
    return data


def serialize_mapping_record(record: OrchestrationIntentPolicyMappingRecord) -> str:
    return stable_serialize(export_mapping_record(record))


def hash_mapping_record(record: OrchestrationIntentPolicyMappingRecord) -> str:
    return deterministic_hash(_export_mapping_record_base(record))


def export_mapping_registry(registry: OrchestrationIntentPolicyMappingRegistry) -> dict[str, Any]:
    data = asdict(registry)
    data["records"] = [
        export_mapping_record(record)
        for record in sorted(registry.records, key=lambda item: item.identifier.mapping_id)
    ]
    data["registry_metadata"] = dict(sorted(registry.registry_metadata.items()))
    data["deterministic_mapping_registry_hash"] = hash_mapping_registry(registry)
    return data


def serialize_mapping_registry(registry: OrchestrationIntentPolicyMappingRegistry) -> str:
    return stable_serialize(export_mapping_registry(registry))


def hash_mapping_registry(registry: OrchestrationIntentPolicyMappingRegistry) -> str:
    return deterministic_hash(
        {
            "registry_id": registry.registry_id,
            "schema_version": registry.schema_version,
            "records": [
                export_mapping_record(record)
                for record in sorted(registry.records, key=lambda item: item.identifier.mapping_id)
            ],
            "registry_metadata": dict(sorted(registry.registry_metadata.items())),
            "planning_only": registry.planning_only,
            "non_production": registry.non_production,
        }
    )


def export_mapping_finding(finding: OrchestrationIntentPolicyMappingFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_mapping_analysis_record(record: OrchestrationIntentPolicyMappingAnalysisRecord) -> dict[str, Any]:
    data = asdict(record)
    data["findings"] = [export_mapping_finding(finding) for finding in sorted(record.findings, key=_finding_sort_key)]
    return data


def export_mapping_result(result: OrchestrationIntentPolicyMappingResult) -> dict[str, Any]:
    data = asdict(result)
    data["analysis_records"] = [
        export_mapping_analysis_record(record)
        for record in sorted(result.analysis_records, key=lambda item: item.mapping_id)
    ]
    data["finding_summary"] = [export_mapping_finding(finding) for finding in sorted(result.finding_summary, key=_finding_sort_key)]
    return data


def serialize_mapping_result(result: OrchestrationIntentPolicyMappingResult) -> str:
    return stable_serialize(export_mapping_result(result))


def hash_mapping_result(result: OrchestrationIntentPolicyMappingResult) -> str:
    data = export_mapping_result(result)
    data.pop("deterministic_mapping_analysis_hash", None)
    return deterministic_hash(data)


def export_mapping_explanation_record(record: OrchestrationIntentPolicyMappingExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "policy_applicability_visibility",
        "governance_boundary_visibility",
        "compatibility_domain_visibility",
        "dependency_domain_visibility",
        "blocker_domain_visibility",
        "unsupported_domain_visibility",
        "prohibited_domain_visibility",
        "supported_domain_visibility",
        "mapping_rationale_visibility",
        "provenance_visibility",
        "analysis_visibility",
        "integrity_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_mapping_explainability_result(result: OrchestrationIntentPolicyMappingExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_mapping_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.mapping_id)
    ]
    return data


def serialize_mapping_explainability_result(result: OrchestrationIntentPolicyMappingExplainabilityResult) -> str:
    return stable_serialize(export_mapping_explainability_result(result))


def hash_mapping_explainability_result(result: OrchestrationIntentPolicyMappingExplainabilityResult) -> str:
    data = export_mapping_explainability_result(result)
    data.pop("deterministic_mapping_explainability_hash", None)
    return deterministic_hash(data)


def export_mapping_integrity_summary(summary: OrchestrationIntentPolicyMappingIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_mapping_integrity_result(result: OrchestrationIntentPolicyMappingIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "registry_integrity",
        "mapping_hash_integrity",
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
        data[field] = export_mapping_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_mapping_integrity_result(result: OrchestrationIntentPolicyMappingIntegrityResult) -> str:
    return stable_serialize(export_mapping_integrity_result(result))


def hash_mapping_integrity_result(result: OrchestrationIntentPolicyMappingIntegrityResult) -> str:
    data = export_mapping_integrity_result(result)
    data.pop("deterministic_mapping_integrity_hash", None)
    return deterministic_hash(data)


def _export_mapping_record_base(record: OrchestrationIntentPolicyMappingRecord) -> dict[str, Any]:
    data = asdict(record)
    data["identifier"] = asdict(record.identifier)
    data["provenance"] = export_mapping_provenance(record.provenance)
    data["governance_metadata"] = dict(sorted(record.governance_metadata.items()))
    for field in (
        "mapping_classifications",
        "policy_ids",
        "governance_boundaries",
        "compatibility_domains",
        "dependency_domains",
        "blocker_domains",
        "unsupported_domains",
        "prohibited_domains",
        "supported_domains",
        "mapping_rationale",
        "explainability_reference_ids",
        "integrity_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def _finding_sort_key(finding: OrchestrationIntentPolicyMappingFinding) -> tuple[str, str, str, str]:
    return (finding.mapping_id, finding.intent_id, finding.classification, finding.reason)
