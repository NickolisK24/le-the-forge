"""Deterministic orchestration evaluation trace models for v3.6 Phase 7."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


TRACE_STEP_SUPPORTABILITY = "supportability_evaluation_trace_step"
TRACE_STEP_GOVERNANCE = "governance_evaluation_trace_step"
TRACE_STEP_COMPATIBILITY = "compatibility_evaluation_trace_step"
TRACE_STEP_DEPENDENCY = "dependency_evaluation_trace_step"
TRACE_STEP_BLOCKER = "blocker_chain_trace_step"
TRACE_STEP_UNSUPPORTED_DOMAIN = "unsupported_domain_trace_step"
TRACE_STEP_PROHIBITED_DOMAIN = "prohibited_domain_trace_step"
TRACE_STEP_PROVENANCE = "provenance_trace_step"
TRACE_STEP_EXPLAINABILITY = "explainability_trace_step"
TRACE_STEP_INTEGRITY = "integrity_validation_trace_step"
TRACE_STEP_TYPES: tuple[str, ...] = (
    TRACE_STEP_SUPPORTABILITY,
    TRACE_STEP_GOVERNANCE,
    TRACE_STEP_COMPATIBILITY,
    TRACE_STEP_DEPENDENCY,
    TRACE_STEP_BLOCKER,
    TRACE_STEP_UNSUPPORTED_DOMAIN,
    TRACE_STEP_PROHIBITED_DOMAIN,
    TRACE_STEP_PROVENANCE,
    TRACE_STEP_EXPLAINABILITY,
    TRACE_STEP_INTEGRITY,
)

TRACE_CLASSIFICATION_GOVERNANCE = "governance_evaluation_trace"
TRACE_CLASSIFICATION_COMPATIBILITY = "compatibility_evaluation_trace"
TRACE_CLASSIFICATION_DEPENDENCY = "dependency_evaluation_trace"
TRACE_CLASSIFICATION_BLOCKER = "blocker_chain_trace"
TRACE_CLASSIFICATION_UNSUPPORTED = "unsupported_domain_trace"
TRACE_CLASSIFICATION_PROHIBITED = "prohibited_domain_trace"
TRACE_CLASSIFICATION_PROVENANCE = "provenance_continuity_trace"
TRACE_CLASSIFICATION_EXPLAINABILITY = "explainability_continuity_trace"
TRACE_CLASSIFICATION_INTEGRITY = "integrity_validation_trace"
TRACE_CLASSIFICATIONS: tuple[str, ...] = (
    TRACE_CLASSIFICATION_GOVERNANCE,
    TRACE_CLASSIFICATION_COMPATIBILITY,
    TRACE_CLASSIFICATION_DEPENDENCY,
    TRACE_CLASSIFICATION_BLOCKER,
    TRACE_CLASSIFICATION_UNSUPPORTED,
    TRACE_CLASSIFICATION_PROHIBITED,
    TRACE_CLASSIFICATION_PROVENANCE,
    TRACE_CLASSIFICATION_EXPLAINABILITY,
    TRACE_CLASSIFICATION_INTEGRITY,
)

TRACE_SUPPORTED = "trace_supported"
TRACE_UNSUPPORTED = "trace_unsupported"
TRACE_PROHIBITED = "trace_prohibited"
TRACE_GOVERNANCE_BLOCKED = "trace_governance_blocked"
TRACE_COMPATIBILITY_BLOCKED = "trace_compatibility_blocked"
TRACE_DEPENDENCY_BLOCKED = "trace_dependency_blocked"
TRACE_STATES: tuple[str, ...] = (
    TRACE_SUPPORTED,
    TRACE_UNSUPPORTED,
    TRACE_PROHIBITED,
    TRACE_GOVERNANCE_BLOCKED,
    TRACE_COMPATIBILITY_BLOCKED,
    TRACE_DEPENDENCY_BLOCKED,
)

TRACE_CLASSIFIED_AS_SUPPORTED = "trace_classified_as_supported"
TRACE_CLASSIFIED_AS_UNSUPPORTED = "trace_classified_as_unsupported"
TRACE_CLASSIFIED_AS_PROHIBITED = "trace_classified_as_prohibited"
TRACE_CLASSIFIED_AS_GOVERNANCE_BLOCKED = "trace_classified_as_governance_blocked"
TRACE_CLASSIFIED_AS_COMPATIBILITY_BLOCKED = "trace_classified_as_compatibility_blocked"
TRACE_CLASSIFIED_AS_DEPENDENCY_BLOCKED = "trace_classified_as_dependency_blocked"
TRACE_STEP_VISIBLE = "trace_step_visible"
TRACE_REASONING_CHAIN_VISIBLE = "trace_reasoning_chain_visible"
TRACE_GOVERNANCE_BOUNDARY_VISIBLE = "trace_governance_boundary_visible"
TRACE_COMPATIBILITY_DOMAIN_VISIBLE = "trace_compatibility_domain_visible"
TRACE_DEPENDENCY_DOMAIN_VISIBLE = "trace_dependency_domain_visible"
TRACE_BLOCKER_DOMAIN_VISIBLE = "trace_blocker_domain_visible"
TRACE_UNSUPPORTED_DOMAIN_VISIBLE = "trace_unsupported_domain_visible"
TRACE_PROHIBITED_DOMAIN_VISIBLE = "trace_prohibited_domain_visible"
TRACE_SUPPORTED_DOMAIN_VISIBLE = "trace_supported_domain_visible"
TRACE_POLICY_VISIBLE = "trace_policy_visible"
TRACE_PROVENANCE_GAP = "trace_provenance_gap"
TRACE_EXPLAINABILITY_GAP = "trace_explainability_gap"
TRACE_INTEGRITY_GAP = "trace_integrity_gap"
TRACE_HASH_MISMATCH = "trace_hash_mismatch"
TRACE_GOVERNANCE_BOUNDARY_GAP = "trace_governance_boundary_gap"
TRACE_STEP_GAP = "trace_step_gap"
TRACE_POLICY_GAP = "trace_policy_gap"

TRACE_CONTINUITY_PRESERVED = "trace_continuity_preserved"
TRACE_CONTINUITY_GAP = "trace_continuity_gap"

TRACE_BUILD_STABLE = "trace_build_stable"
TRACE_BUILD_STABLE_WITH_VISIBLE_FINDINGS = "trace_build_stable_with_visible_findings"
TRACE_BUILD_BLOCKED_BY_CONTINUITY_GAP = "trace_build_blocked_by_continuity_gap"

TRACE_EXPLAINABILITY_STABLE = "trace_explainability_stable"
TRACE_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "trace_explainability_blocked_by_visibility_gap"

TRACE_INTEGRITY_STABLE = "trace_integrity_stable"
TRACE_INTEGRITY_BLOCKED_BY_REGISTRY_GAP = "trace_integrity_blocked_by_registry_gap"
TRACE_INTEGRITY_BLOCKED_BY_HASH_GAP = "trace_integrity_blocked_by_hash_gap"
TRACE_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP = "trace_integrity_blocked_by_provenance_gap"
TRACE_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "trace_integrity_blocked_by_explainability_gap"
TRACE_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP = "trace_integrity_blocked_by_governance_gap"
TRACE_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP = "trace_integrity_blocked_by_compatibility_gap"
TRACE_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP = "trace_integrity_blocked_by_dependency_gap"
TRACE_INTEGRITY_BLOCKED_BY_BLOCKER_GAP = "trace_integrity_blocked_by_blocker_gap"
TRACE_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP = "trace_integrity_blocked_by_supported_domain_gap"
TRACE_INTEGRITY_BLOCKED_BY_STEP_GAP = "trace_integrity_blocked_by_step_gap"
TRACE_INTEGRITY_BLOCKED_BY_POLICY_GAP = "trace_integrity_blocked_by_policy_gap"


@dataclass(frozen=True)
class OrchestrationEvaluationTraceIdentifier:
    trace_id: str
    preflight_id: str
    intent_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationEvaluationTraceStep:
    step_id: str
    step_type: str
    sequence_id: int
    description: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationTraceProvenance:
    source_phase: str
    source_artifact: str
    preflight_id: str
    intent_id: str
    policy_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationTraceRecord:
    identifier: OrchestrationEvaluationTraceIdentifier
    trace_state: str
    preflight_state: str
    trace_classifications: tuple[str, ...]
    trace_steps: tuple[OrchestrationEvaluationTraceStep, ...]
    reasoning_chain: tuple[str, ...]
    policy_ids: tuple[str, ...]
    governance_boundaries: tuple[str, ...]
    compatibility_domains: tuple[str, ...]
    dependency_domains: tuple[str, ...]
    blocker_domains: tuple[str, ...]
    unsupported_domains: tuple[str, ...]
    prohibited_domains: tuple[str, ...]
    supported_domains: tuple[str, ...]
    provenance: OrchestrationEvaluationTraceProvenance
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
    trace_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationEvaluationTraceRegistry:
    registry_id: str
    schema_version: str
    records: tuple[OrchestrationEvaluationTraceRecord, ...]
    registry_metadata: Mapping[str, Any]
    planning_only: bool = True
    non_production: bool = True


@dataclass(frozen=True)
class OrchestrationEvaluationTraceFinding:
    trace_id: str
    preflight_id: str
    classification: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationTraceBuildRecord:
    trace_id: str
    preflight_id: str
    trace_state: str
    trace_hash: str
    trace_step_count: int
    reasoning_step_count: int
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
    findings: tuple[OrchestrationEvaluationTraceFinding, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationTraceBuildInput:
    trace_registry: OrchestrationEvaluationTraceRegistry
    expected_registry_hash: str | None = None
    expected_trace_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationEvaluationTraceBuildResult:
    registry_id: str
    trace_build_status: str
    planning_only: bool
    build_records: tuple[OrchestrationEvaluationTraceBuildRecord, ...]
    registered_trace_count: int
    governance_trace_count: int
    compatibility_trace_count: int
    dependency_trace_count: int
    blocker_trace_count: int
    unsupported_trace_count: int
    prohibited_trace_count: int
    provenance_trace_count: int
    explainability_trace_count: int
    integrity_trace_count: int
    trace_step_count: int
    reasoning_step_count: int
    provenance_continuity_status: str
    explainability_continuity_status: str
    integrity_continuity_status: str
    governance_continuity_status: str
    finding_summary: tuple[OrchestrationEvaluationTraceFinding, ...]
    deterministic_registry_hash: str
    deterministic_trace_build_hash: str
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
    trace_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationEvaluationTraceExplanationRecord:
    trace_id: str
    preflight_id: str
    trace_state: str
    explanation_status: str
    reasoning_chain_visibility: tuple[str, ...]
    trace_step_visibility: tuple[str, ...]
    governance_boundary_visibility: tuple[str, ...]
    compatibility_domain_visibility: tuple[str, ...]
    dependency_domain_visibility: tuple[str, ...]
    blocker_domain_visibility: tuple[str, ...]
    unsupported_domain_visibility: tuple[str, ...]
    prohibited_domain_visibility: tuple[str, ...]
    supported_domain_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    build_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationTraceExplainabilityResult:
    registry_id: str
    trace_explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationEvaluationTraceExplanationRecord, ...]
    governance_explanation_count: int
    compatibility_explanation_count: int
    dependency_explanation_count: int
    blocker_explanation_count: int
    unsupported_explanation_count: int
    prohibited_explanation_count: int
    trace_step_visibility_count: int
    reasoning_chain_visibility_count: int
    deterministic_trace_explainability_hash: str
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
    trace_execution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationEvaluationTraceIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationTraceIntegrityInput:
    trace_registry: OrchestrationEvaluationTraceRegistry
    build_result: OrchestrationEvaluationTraceBuildResult
    explainability_result: OrchestrationEvaluationTraceExplainabilityResult
    expected_registry_hash: str | None = None
    expected_build_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationEvaluationTraceIntegrityResult:
    registry_id: str
    trace_integrity_status: str
    planning_only: bool
    registry_integrity: OrchestrationEvaluationTraceIntegritySummary
    trace_hash_integrity: OrchestrationEvaluationTraceIntegritySummary
    provenance_integrity: OrchestrationEvaluationTraceIntegritySummary
    explainability_integrity: OrchestrationEvaluationTraceIntegritySummary
    governance_integrity: OrchestrationEvaluationTraceIntegritySummary
    compatibility_integrity: OrchestrationEvaluationTraceIntegritySummary
    dependency_integrity: OrchestrationEvaluationTraceIntegritySummary
    blocker_integrity: OrchestrationEvaluationTraceIntegritySummary
    supported_domain_integrity: OrchestrationEvaluationTraceIntegritySummary
    trace_step_integrity: OrchestrationEvaluationTraceIntegritySummary
    policy_integrity: OrchestrationEvaluationTraceIntegritySummary
    deterministic_serialization_integrity: OrchestrationEvaluationTraceIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_trace_integrity_hash: str
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
    trace_execution_enabled: bool = False


def export_trace_step(step: OrchestrationEvaluationTraceStep) -> dict[str, Any]:
    data = asdict(step)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_trace_provenance(provenance: OrchestrationEvaluationTraceProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field in (
        "policy_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
        "governance_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def export_trace_record(record: OrchestrationEvaluationTraceRecord) -> dict[str, Any]:
    data = _export_trace_record_base(record)
    data["deterministic_trace_hash"] = hash_trace_record(record)
    return data


def serialize_trace_record(record: OrchestrationEvaluationTraceRecord) -> str:
    return stable_serialize(export_trace_record(record))


def hash_trace_record(record: OrchestrationEvaluationTraceRecord) -> str:
    return deterministic_hash(_export_trace_record_base(record))


def export_trace_registry(registry: OrchestrationEvaluationTraceRegistry) -> dict[str, Any]:
    data = asdict(registry)
    data["records"] = [
        export_trace_record(record)
        for record in sorted(registry.records, key=lambda item: item.identifier.trace_id)
    ]
    data["registry_metadata"] = dict(sorted(registry.registry_metadata.items()))
    data["deterministic_trace_registry_hash"] = hash_trace_registry(registry)
    return data


def serialize_trace_registry(registry: OrchestrationEvaluationTraceRegistry) -> str:
    return stable_serialize(export_trace_registry(registry))


def hash_trace_registry(registry: OrchestrationEvaluationTraceRegistry) -> str:
    return deterministic_hash(
        {
            "registry_id": registry.registry_id,
            "schema_version": registry.schema_version,
            "records": [
                export_trace_record(record)
                for record in sorted(registry.records, key=lambda item: item.identifier.trace_id)
            ],
            "registry_metadata": dict(sorted(registry.registry_metadata.items())),
            "planning_only": registry.planning_only,
            "non_production": registry.non_production,
        }
    )


def export_trace_finding(finding: OrchestrationEvaluationTraceFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_trace_build_record(record: OrchestrationEvaluationTraceBuildRecord) -> dict[str, Any]:
    data = asdict(record)
    data["findings"] = [export_trace_finding(finding) for finding in sorted(record.findings, key=_finding_sort_key)]
    return data


def export_trace_build_result(result: OrchestrationEvaluationTraceBuildResult) -> dict[str, Any]:
    data = asdict(result)
    data["build_records"] = [
        export_trace_build_record(record)
        for record in sorted(result.build_records, key=lambda item: item.trace_id)
    ]
    data["finding_summary"] = [export_trace_finding(finding) for finding in sorted(result.finding_summary, key=_finding_sort_key)]
    return data


def serialize_trace_build_result(result: OrchestrationEvaluationTraceBuildResult) -> str:
    return stable_serialize(export_trace_build_result(result))


def hash_trace_build_result(result: OrchestrationEvaluationTraceBuildResult) -> str:
    data = export_trace_build_result(result)
    data.pop("deterministic_trace_build_hash", None)
    return deterministic_hash(data)


def export_trace_explanation_record(record: OrchestrationEvaluationTraceExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "reasoning_chain_visibility",
        "trace_step_visibility",
        "governance_boundary_visibility",
        "compatibility_domain_visibility",
        "dependency_domain_visibility",
        "blocker_domain_visibility",
        "unsupported_domain_visibility",
        "prohibited_domain_visibility",
        "supported_domain_visibility",
        "provenance_visibility",
        "build_visibility",
        "integrity_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_trace_explainability_result(result: OrchestrationEvaluationTraceExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_trace_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.trace_id)
    ]
    return data


def serialize_trace_explainability_result(result: OrchestrationEvaluationTraceExplainabilityResult) -> str:
    return stable_serialize(export_trace_explainability_result(result))


def hash_trace_explainability_result(result: OrchestrationEvaluationTraceExplainabilityResult) -> str:
    data = export_trace_explainability_result(result)
    data.pop("deterministic_trace_explainability_hash", None)
    return deterministic_hash(data)


def export_trace_integrity_summary(summary: OrchestrationEvaluationTraceIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_trace_integrity_result(result: OrchestrationEvaluationTraceIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "registry_integrity",
        "trace_hash_integrity",
        "provenance_integrity",
        "explainability_integrity",
        "governance_integrity",
        "compatibility_integrity",
        "dependency_integrity",
        "blocker_integrity",
        "supported_domain_integrity",
        "trace_step_integrity",
        "policy_integrity",
        "deterministic_serialization_integrity",
    ):
        data[field] = export_trace_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_trace_integrity_result(result: OrchestrationEvaluationTraceIntegrityResult) -> str:
    return stable_serialize(export_trace_integrity_result(result))


def hash_trace_integrity_result(result: OrchestrationEvaluationTraceIntegrityResult) -> str:
    data = export_trace_integrity_result(result)
    data.pop("deterministic_trace_integrity_hash", None)
    return deterministic_hash(data)


def _export_trace_record_base(record: OrchestrationEvaluationTraceRecord) -> dict[str, Any]:
    data = asdict(record)
    data["identifier"] = asdict(record.identifier)
    data["trace_steps"] = [
        export_trace_step(step)
        for step in sorted(record.trace_steps, key=lambda item: (item.sequence_id, item.step_id))
    ]
    data["provenance"] = export_trace_provenance(record.provenance)
    data["governance_metadata"] = dict(sorted(record.governance_metadata.items()))
    for field in (
        "trace_classifications",
        "reasoning_chain",
        "policy_ids",
        "governance_boundaries",
        "compatibility_domains",
        "dependency_domains",
        "blocker_domains",
        "unsupported_domains",
        "prohibited_domains",
        "supported_domains",
        "explainability_reference_ids",
        "integrity_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def _finding_sort_key(finding: OrchestrationEvaluationTraceFinding) -> tuple[str, str, str, str]:
    return (finding.trace_id, finding.preflight_id, finding.classification, finding.reason)
