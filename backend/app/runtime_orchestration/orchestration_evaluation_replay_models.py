"""Deterministic orchestration evaluation replay packet models for v3.6 Phase 8."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


REPLAY_EVIDENCE_INTENT = "intent_evidence_packet"
REPLAY_EVIDENCE_POLICY_MAPPING = "policy_mapping_evidence_packet"
REPLAY_EVIDENCE_GOVERNANCE = "governance_evidence_packet"
REPLAY_EVIDENCE_COMPATIBILITY = "compatibility_evidence_packet"
REPLAY_EVIDENCE_DEPENDENCY = "dependency_evidence_packet"
REPLAY_EVIDENCE_BLOCKER = "blocker_evidence_packet"
REPLAY_EVIDENCE_UNSUPPORTED = "unsupported_evidence_packet"
REPLAY_EVIDENCE_PROHIBITED = "prohibited_evidence_packet"
REPLAY_EVIDENCE_PREFLIGHT = "preflight_evidence_packet"
REPLAY_EVIDENCE_TRACE = "trace_evidence_packet"
REPLAY_EVIDENCE_PROVENANCE = "provenance_evidence_packet"
REPLAY_EVIDENCE_EXPLAINABILITY = "explainability_evidence_packet"
REPLAY_EVIDENCE_INTEGRITY = "integrity_evidence_packet"
REPLAY_EVIDENCE_TYPES: tuple[str, ...] = (
    REPLAY_EVIDENCE_INTENT,
    REPLAY_EVIDENCE_POLICY_MAPPING,
    REPLAY_EVIDENCE_GOVERNANCE,
    REPLAY_EVIDENCE_COMPATIBILITY,
    REPLAY_EVIDENCE_DEPENDENCY,
    REPLAY_EVIDENCE_BLOCKER,
    REPLAY_EVIDENCE_UNSUPPORTED,
    REPLAY_EVIDENCE_PROHIBITED,
    REPLAY_EVIDENCE_PREFLIGHT,
    REPLAY_EVIDENCE_TRACE,
    REPLAY_EVIDENCE_PROVENANCE,
    REPLAY_EVIDENCE_EXPLAINABILITY,
    REPLAY_EVIDENCE_INTEGRITY,
)

REPLAY_CLASSIFICATION_GOVERNANCE = "governance_replay_evidence"
REPLAY_CLASSIFICATION_COMPATIBILITY = "compatibility_replay_evidence"
REPLAY_CLASSIFICATION_DEPENDENCY = "dependency_replay_evidence"
REPLAY_CLASSIFICATION_BLOCKER = "blocker_replay_evidence"
REPLAY_CLASSIFICATION_UNSUPPORTED = "unsupported_replay_evidence"
REPLAY_CLASSIFICATION_PROHIBITED = "prohibited_replay_evidence"
REPLAY_CLASSIFICATION_PREFLIGHT = "preflight_replay_evidence"
REPLAY_CLASSIFICATION_TRACE = "trace_replay_evidence"
REPLAY_CLASSIFICATION_PROVENANCE = "provenance_replay_evidence"
REPLAY_CLASSIFICATION_EXPLAINABILITY = "explainability_replay_evidence"
REPLAY_CLASSIFICATION_INTEGRITY = "integrity_replay_evidence"
REPLAY_CLASSIFICATIONS: tuple[str, ...] = (
    REPLAY_CLASSIFICATION_GOVERNANCE,
    REPLAY_CLASSIFICATION_COMPATIBILITY,
    REPLAY_CLASSIFICATION_DEPENDENCY,
    REPLAY_CLASSIFICATION_BLOCKER,
    REPLAY_CLASSIFICATION_UNSUPPORTED,
    REPLAY_CLASSIFICATION_PROHIBITED,
    REPLAY_CLASSIFICATION_PREFLIGHT,
    REPLAY_CLASSIFICATION_TRACE,
    REPLAY_CLASSIFICATION_PROVENANCE,
    REPLAY_CLASSIFICATION_EXPLAINABILITY,
    REPLAY_CLASSIFICATION_INTEGRITY,
)

REPLAY_SUPPORTED = "replay_packet_supported"
REPLAY_UNSUPPORTED = "replay_packet_unsupported"
REPLAY_PROHIBITED = "replay_packet_prohibited"
REPLAY_GOVERNANCE_BLOCKED = "replay_packet_governance_blocked"
REPLAY_COMPATIBILITY_BLOCKED = "replay_packet_compatibility_blocked"
REPLAY_DEPENDENCY_BLOCKED = "replay_packet_dependency_blocked"
REPLAY_STATES: tuple[str, ...] = (
    REPLAY_SUPPORTED,
    REPLAY_UNSUPPORTED,
    REPLAY_PROHIBITED,
    REPLAY_GOVERNANCE_BLOCKED,
    REPLAY_COMPATIBILITY_BLOCKED,
    REPLAY_DEPENDENCY_BLOCKED,
)

REPLAY_CLASSIFIED_AS_SUPPORTED = "replay_packet_classified_as_supported"
REPLAY_CLASSIFIED_AS_UNSUPPORTED = "replay_packet_classified_as_unsupported"
REPLAY_CLASSIFIED_AS_PROHIBITED = "replay_packet_classified_as_prohibited"
REPLAY_CLASSIFIED_AS_GOVERNANCE_BLOCKED = "replay_packet_classified_as_governance_blocked"
REPLAY_CLASSIFIED_AS_COMPATIBILITY_BLOCKED = "replay_packet_classified_as_compatibility_blocked"
REPLAY_CLASSIFIED_AS_DEPENDENCY_BLOCKED = "replay_packet_classified_as_dependency_blocked"
REPLAY_INTENT_EVIDENCE_VISIBLE = "replay_intent_evidence_visible"
REPLAY_POLICY_MAPPING_VISIBLE = "replay_policy_mapping_visible"
REPLAY_GOVERNANCE_EVIDENCE_VISIBLE = "replay_governance_evidence_visible"
REPLAY_COMPATIBILITY_EVIDENCE_VISIBLE = "replay_compatibility_evidence_visible"
REPLAY_DEPENDENCY_EVIDENCE_VISIBLE = "replay_dependency_evidence_visible"
REPLAY_BLOCKER_EVIDENCE_VISIBLE = "replay_blocker_evidence_visible"
REPLAY_UNSUPPORTED_EVIDENCE_VISIBLE = "replay_unsupported_evidence_visible"
REPLAY_PROHIBITED_EVIDENCE_VISIBLE = "replay_prohibited_evidence_visible"
REPLAY_PREFLIGHT_EVIDENCE_VISIBLE = "replay_preflight_evidence_visible"
REPLAY_TRACE_EVIDENCE_VISIBLE = "replay_trace_evidence_visible"
REPLAY_REASONING_CHAIN_VISIBLE = "replay_reasoning_chain_visible"
REPLAY_PROVENANCE_EVIDENCE_VISIBLE = "replay_provenance_evidence_visible"
REPLAY_EXPLAINABILITY_EVIDENCE_VISIBLE = "replay_explainability_evidence_visible"
REPLAY_INTEGRITY_EVIDENCE_VISIBLE = "replay_integrity_evidence_visible"
REPLAY_SUPPORTED_DOMAIN_VISIBLE = "replay_supported_domain_visible"
REPLAY_PROVENANCE_GAP = "replay_provenance_gap"
REPLAY_EXPLAINABILITY_GAP = "replay_explainability_gap"
REPLAY_INTEGRITY_GAP = "replay_integrity_gap"
REPLAY_HASH_MISMATCH = "replay_hash_mismatch"
REPLAY_GOVERNANCE_BOUNDARY_GAP = "replay_governance_boundary_gap"
REPLAY_EVIDENCE_GAP = "replay_evidence_gap"
REPLAY_INTENT_GAP = "replay_intent_gap"
REPLAY_POLICY_MAPPING_GAP = "replay_policy_mapping_gap"
REPLAY_TRACE_GAP = "replay_trace_gap"

REPLAY_CONTINUITY_PRESERVED = "replay_continuity_preserved"
REPLAY_CONTINUITY_GAP = "replay_continuity_gap"

REPLAY_BUILD_STABLE = "replay_build_stable"
REPLAY_BUILD_STABLE_WITH_VISIBLE_FINDINGS = "replay_build_stable_with_visible_findings"
REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP = "replay_build_blocked_by_continuity_gap"

REPLAY_EXPLAINABILITY_STABLE = "replay_explainability_stable"
REPLAY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "replay_explainability_blocked_by_visibility_gap"

REPLAY_INTEGRITY_STABLE = "replay_integrity_stable"
REPLAY_INTEGRITY_BLOCKED_BY_REGISTRY_GAP = "replay_integrity_blocked_by_registry_gap"
REPLAY_INTEGRITY_BLOCKED_BY_HASH_GAP = "replay_integrity_blocked_by_hash_gap"
REPLAY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP = "replay_integrity_blocked_by_provenance_gap"
REPLAY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "replay_integrity_blocked_by_explainability_gap"
REPLAY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP = "replay_integrity_blocked_by_governance_gap"
REPLAY_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP = "replay_integrity_blocked_by_compatibility_gap"
REPLAY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP = "replay_integrity_blocked_by_dependency_gap"
REPLAY_INTEGRITY_BLOCKED_BY_BLOCKER_GAP = "replay_integrity_blocked_by_blocker_gap"
REPLAY_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP = "replay_integrity_blocked_by_supported_domain_gap"
REPLAY_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP = "replay_integrity_blocked_by_evidence_gap"
REPLAY_INTEGRITY_BLOCKED_BY_INTENT_GAP = "replay_integrity_blocked_by_intent_gap"
REPLAY_INTEGRITY_BLOCKED_BY_POLICY_MAPPING_GAP = "replay_integrity_blocked_by_policy_mapping_gap"
REPLAY_INTEGRITY_BLOCKED_BY_TRACE_GAP = "replay_integrity_blocked_by_trace_gap"


@dataclass(frozen=True)
class OrchestrationEvaluationReplayIdentifier:
    packet_id: str
    trace_id: str
    preflight_id: str
    intent_id: str
    mapping_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationEvaluationReplayEvidence:
    evidence_id: str
    evidence_type: str
    source_id: str
    source_hash: str
    description: str
    reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationReplayProvenance:
    source_phase: str
    source_artifact: str
    packet_id: str
    trace_id: str
    preflight_id: str
    intent_id: str
    mapping_id: str
    policy_ids: tuple[str, ...]
    compatibility_relationship_ids: tuple[str, ...]
    trace_reference_ids: tuple[str, ...]
    preflight_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationReplayPacket:
    identifier: OrchestrationEvaluationReplayIdentifier
    replay_state: str
    replay_classifications: tuple[str, ...]
    intent_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    policy_mapping_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    governance_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    compatibility_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    dependency_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    blocker_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    unsupported_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    prohibited_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    preflight_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    trace_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    provenance_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    explainability_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    integrity_evidence: tuple[OrchestrationEvaluationReplayEvidence, ...]
    reasoning_chain: tuple[str, ...]
    policy_ids: tuple[str, ...]
    governance_boundaries: tuple[str, ...]
    compatibility_domains: tuple[str, ...]
    dependency_domains: tuple[str, ...]
    blocker_domains: tuple[str, ...]
    unsupported_domains: tuple[str, ...]
    prohibited_domains: tuple[str, ...]
    supported_domains: tuple[str, ...]
    provenance: OrchestrationEvaluationReplayProvenance
    governance_metadata: Mapping[str, Any]
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
    replay_execution_enabled: bool = False
    persistent_write_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationEvaluationReplayRegistry:
    registry_id: str
    schema_version: str
    packets: tuple[OrchestrationEvaluationReplayPacket, ...]
    registry_metadata: Mapping[str, Any]
    planning_only: bool = True
    non_production: bool = True


@dataclass(frozen=True)
class OrchestrationEvaluationReplayFinding:
    packet_id: str
    trace_id: str
    classification: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationReplayBuildRecord:
    packet_id: str
    trace_id: str
    replay_state: str
    packet_hash: str
    evidence_count: int
    intent_evidence_count: int
    policy_mapping_evidence_count: int
    governance_evidence_count: int
    compatibility_evidence_count: int
    dependency_evidence_count: int
    blocker_evidence_count: int
    unsupported_evidence_count: int
    prohibited_evidence_count: int
    preflight_evidence_count: int
    trace_evidence_count: int
    reasoning_step_count: int
    provenance_continuity_state: str
    explainability_continuity_state: str
    integrity_continuity_state: str
    governance_continuity_state: str
    findings: tuple[OrchestrationEvaluationReplayFinding, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationReplayBuildInput:
    replay_registry: OrchestrationEvaluationReplayRegistry
    expected_registry_hash: str | None = None
    expected_packet_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationEvaluationReplayBuildResult:
    registry_id: str
    replay_build_status: str
    planning_only: bool
    build_records: tuple[OrchestrationEvaluationReplayBuildRecord, ...]
    registered_replay_packet_count: int
    governance_evidence_count: int
    compatibility_evidence_count: int
    dependency_evidence_count: int
    blocker_evidence_count: int
    unsupported_replay_count: int
    prohibited_replay_count: int
    preflight_evidence_count: int
    trace_evidence_count: int
    intent_evidence_count: int
    policy_mapping_evidence_count: int
    reasoning_step_count: int
    provenance_continuity_status: str
    explainability_continuity_status: str
    integrity_continuity_status: str
    governance_continuity_status: str
    finding_summary: tuple[OrchestrationEvaluationReplayFinding, ...]
    deterministic_registry_hash: str
    deterministic_replay_build_hash: str
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
    replay_execution_enabled: bool = False
    persistent_write_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationEvaluationReplayExplanationRecord:
    packet_id: str
    trace_id: str
    replay_state: str
    explanation_status: str
    evaluation_state_visibility: tuple[str, ...]
    evidence_visibility: tuple[str, ...]
    governance_boundary_visibility: tuple[str, ...]
    compatibility_domain_visibility: tuple[str, ...]
    dependency_domain_visibility: tuple[str, ...]
    blocker_domain_visibility: tuple[str, ...]
    unsupported_domain_visibility: tuple[str, ...]
    prohibited_domain_visibility: tuple[str, ...]
    supported_domain_visibility: tuple[str, ...]
    reasoning_chain_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    build_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationReplayExplainabilityResult:
    registry_id: str
    replay_explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationEvaluationReplayExplanationRecord, ...]
    governance_explanation_count: int
    compatibility_explanation_count: int
    dependency_explanation_count: int
    blocker_explanation_count: int
    unsupported_explanation_count: int
    prohibited_explanation_count: int
    evidence_visibility_count: int
    reasoning_chain_visibility_count: int
    deterministic_replay_explainability_hash: str
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
    replay_execution_enabled: bool = False
    persistent_write_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationEvaluationReplayIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationReplayIntegrityInput:
    replay_registry: OrchestrationEvaluationReplayRegistry
    build_result: OrchestrationEvaluationReplayBuildResult
    explainability_result: OrchestrationEvaluationReplayExplainabilityResult
    expected_registry_hash: str | None = None
    expected_build_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationEvaluationReplayIntegrityResult:
    registry_id: str
    replay_integrity_status: str
    planning_only: bool
    registry_integrity: OrchestrationEvaluationReplayIntegritySummary
    replay_hash_integrity: OrchestrationEvaluationReplayIntegritySummary
    provenance_integrity: OrchestrationEvaluationReplayIntegritySummary
    explainability_integrity: OrchestrationEvaluationReplayIntegritySummary
    governance_integrity: OrchestrationEvaluationReplayIntegritySummary
    compatibility_integrity: OrchestrationEvaluationReplayIntegritySummary
    dependency_integrity: OrchestrationEvaluationReplayIntegritySummary
    blocker_integrity: OrchestrationEvaluationReplayIntegritySummary
    supported_domain_integrity: OrchestrationEvaluationReplayIntegritySummary
    evidence_integrity: OrchestrationEvaluationReplayIntegritySummary
    intent_integrity: OrchestrationEvaluationReplayIntegritySummary
    policy_mapping_integrity: OrchestrationEvaluationReplayIntegritySummary
    trace_integrity: OrchestrationEvaluationReplayIntegritySummary
    deterministic_serialization_integrity: OrchestrationEvaluationReplayIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_replay_integrity_hash: str
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
    replay_execution_enabled: bool = False
    persistent_write_enabled: bool = False


def export_replay_evidence(evidence: OrchestrationEvaluationReplayEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    data["reference_ids"] = sorted(data["reference_ids"])
    return data


def export_replay_provenance(provenance: OrchestrationEvaluationReplayProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field in (
        "policy_ids",
        "compatibility_relationship_ids",
        "trace_reference_ids",
        "preflight_reference_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
        "governance_reference_ids",
    ):
        data[field] = sorted(data[field])
    return data


def export_replay_packet(packet: OrchestrationEvaluationReplayPacket) -> dict[str, Any]:
    data = _export_replay_packet_base(packet)
    data["deterministic_replay_packet_hash"] = hash_replay_packet(packet)
    return data


def serialize_replay_packet(packet: OrchestrationEvaluationReplayPacket) -> str:
    return stable_serialize(export_replay_packet(packet))


def hash_replay_packet(packet: OrchestrationEvaluationReplayPacket) -> str:
    return deterministic_hash(_export_replay_packet_base(packet))


def export_replay_registry(registry: OrchestrationEvaluationReplayRegistry) -> dict[str, Any]:
    data = asdict(registry)
    data["packets"] = [
        export_replay_packet(packet)
        for packet in sorted(registry.packets, key=lambda item: item.identifier.packet_id)
    ]
    data["registry_metadata"] = dict(sorted(registry.registry_metadata.items()))
    data["deterministic_replay_registry_hash"] = hash_replay_registry(registry)
    return data


def serialize_replay_registry(registry: OrchestrationEvaluationReplayRegistry) -> str:
    return stable_serialize(export_replay_registry(registry))


def hash_replay_registry(registry: OrchestrationEvaluationReplayRegistry) -> str:
    return deterministic_hash(
        {
            "registry_id": registry.registry_id,
            "schema_version": registry.schema_version,
            "packets": [
                export_replay_packet(packet)
                for packet in sorted(registry.packets, key=lambda item: item.identifier.packet_id)
            ],
            "registry_metadata": dict(sorted(registry.registry_metadata.items())),
            "planning_only": registry.planning_only,
            "non_production": registry.non_production,
        }
    )


def export_replay_finding(finding: OrchestrationEvaluationReplayFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_replay_build_record(record: OrchestrationEvaluationReplayBuildRecord) -> dict[str, Any]:
    data = asdict(record)
    data["findings"] = [export_replay_finding(finding) for finding in sorted(record.findings, key=_finding_sort_key)]
    return data


def export_replay_build_result(result: OrchestrationEvaluationReplayBuildResult) -> dict[str, Any]:
    data = asdict(result)
    data["build_records"] = [
        export_replay_build_record(record)
        for record in sorted(result.build_records, key=lambda item: item.packet_id)
    ]
    data["finding_summary"] = [export_replay_finding(finding) for finding in sorted(result.finding_summary, key=_finding_sort_key)]
    return data


def serialize_replay_build_result(result: OrchestrationEvaluationReplayBuildResult) -> str:
    return stable_serialize(export_replay_build_result(result))


def hash_replay_build_result(result: OrchestrationEvaluationReplayBuildResult) -> str:
    data = export_replay_build_result(result)
    data.pop("deterministic_replay_build_hash", None)
    return deterministic_hash(data)


def export_replay_explanation_record(record: OrchestrationEvaluationReplayExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "evaluation_state_visibility",
        "evidence_visibility",
        "governance_boundary_visibility",
        "compatibility_domain_visibility",
        "dependency_domain_visibility",
        "blocker_domain_visibility",
        "unsupported_domain_visibility",
        "prohibited_domain_visibility",
        "supported_domain_visibility",
        "reasoning_chain_visibility",
        "provenance_visibility",
        "build_visibility",
        "integrity_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_replay_explainability_result(result: OrchestrationEvaluationReplayExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_replay_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.packet_id)
    ]
    return data


def serialize_replay_explainability_result(result: OrchestrationEvaluationReplayExplainabilityResult) -> str:
    return stable_serialize(export_replay_explainability_result(result))


def hash_replay_explainability_result(result: OrchestrationEvaluationReplayExplainabilityResult) -> str:
    data = export_replay_explainability_result(result)
    data.pop("deterministic_replay_explainability_hash", None)
    return deterministic_hash(data)


def export_replay_integrity_summary(summary: OrchestrationEvaluationReplayIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_replay_integrity_result(result: OrchestrationEvaluationReplayIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "registry_integrity",
        "replay_hash_integrity",
        "provenance_integrity",
        "explainability_integrity",
        "governance_integrity",
        "compatibility_integrity",
        "dependency_integrity",
        "blocker_integrity",
        "supported_domain_integrity",
        "evidence_integrity",
        "intent_integrity",
        "policy_mapping_integrity",
        "trace_integrity",
        "deterministic_serialization_integrity",
    ):
        data[field] = export_replay_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_replay_integrity_result(result: OrchestrationEvaluationReplayIntegrityResult) -> str:
    return stable_serialize(export_replay_integrity_result(result))


def hash_replay_integrity_result(result: OrchestrationEvaluationReplayIntegrityResult) -> str:
    data = export_replay_integrity_result(result)
    data.pop("deterministic_replay_integrity_hash", None)
    return deterministic_hash(data)


def _export_replay_packet_base(packet: OrchestrationEvaluationReplayPacket) -> dict[str, Any]:
    data = asdict(packet)
    data["identifier"] = asdict(packet.identifier)
    for field in _evidence_fields():
        data[field] = [
            export_replay_evidence(evidence)
            for evidence in sorted(getattr(packet, field), key=lambda item: item.evidence_id)
        ]
    data["provenance"] = export_replay_provenance(packet.provenance)
    data["governance_metadata"] = dict(sorted(packet.governance_metadata.items()))
    for field in (
        "replay_classifications",
        "reasoning_chain",
        "policy_ids",
        "governance_boundaries",
        "compatibility_domains",
        "dependency_domains",
        "blocker_domains",
        "unsupported_domains",
        "prohibited_domains",
        "supported_domains",
    ):
        data[field] = sorted(data[field])
    return data


def _evidence_fields() -> tuple[str, ...]:
    return (
        "intent_evidence",
        "policy_mapping_evidence",
        "governance_evidence",
        "compatibility_evidence",
        "dependency_evidence",
        "blocker_evidence",
        "unsupported_evidence",
        "prohibited_evidence",
        "preflight_evidence",
        "trace_evidence",
        "provenance_evidence",
        "explainability_evidence",
        "integrity_evidence",
    )


def _finding_sort_key(finding: OrchestrationEvaluationReplayFinding) -> tuple[str, str, str, str]:
    return (finding.packet_id, finding.trace_id, finding.classification, finding.reason)
