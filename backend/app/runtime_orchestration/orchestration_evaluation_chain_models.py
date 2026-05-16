"""Deterministic orchestration evaluation chain integrity models for v3.6 Phase 9."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


CHAIN_LINK_POLICY = "policy_chain"
CHAIN_LINK_COMPATIBILITY = "compatibility_chain"
CHAIN_LINK_RESOLUTION = "resolution_chain"
CHAIN_LINK_INTENT = "intent_chain"
CHAIN_LINK_MAPPING = "mapping_chain"
CHAIN_LINK_PREFLIGHT = "preflight_chain"
CHAIN_LINK_TRACE = "trace_chain"
CHAIN_LINK_REPLAY = "replay_chain"
CHAIN_LINK_BLOCKER = "blocker_chain"
CHAIN_LINK_GOVERNANCE = "governance_boundary_chain"
CHAIN_LINK_PROVENANCE = "provenance_chain"
CHAIN_LINK_EXPLAINABILITY = "explainability_chain"
CHAIN_LINK_INTEGRITY = "integrity_chain"
CHAIN_LINK_REPLAY_SAFETY = "replay_safety_chain"
CHAIN_LINK_ROLLBACK_SAFETY = "rollback_safety_chain"
CHAIN_LINK_TYPES: tuple[str, ...] = (
    CHAIN_LINK_POLICY,
    CHAIN_LINK_COMPATIBILITY,
    CHAIN_LINK_RESOLUTION,
    CHAIN_LINK_INTENT,
    CHAIN_LINK_MAPPING,
    CHAIN_LINK_PREFLIGHT,
    CHAIN_LINK_TRACE,
    CHAIN_LINK_REPLAY,
    CHAIN_LINK_BLOCKER,
    CHAIN_LINK_GOVERNANCE,
    CHAIN_LINK_PROVENANCE,
    CHAIN_LINK_EXPLAINABILITY,
    CHAIN_LINK_INTEGRITY,
    CHAIN_LINK_REPLAY_SAFETY,
    CHAIN_LINK_ROLLBACK_SAFETY,
)

CHAIN_VALID = "evaluation_chain_valid"
CHAIN_INVALID = "evaluation_chain_invalid"
CHAIN_STATES: tuple[str, ...] = (CHAIN_VALID, CHAIN_INVALID)

CHAIN_CONTINUITY_PRESERVED = "evaluation_chain_continuity_preserved"
CHAIN_CONTINUITY_GAP = "evaluation_chain_continuity_gap"

CHAIN_LINK_VALID = "evaluation_chain_link_valid"
CHAIN_LINK_MISSING = "evaluation_chain_link_missing"
CHAIN_HASH_MISMATCH = "evaluation_chain_hash_mismatch"
CHAIN_SOURCE_EVIDENCE_GAP = "evaluation_chain_source_evidence_gap"
CHAIN_BLOCKER_VISIBILITY_GAP = "evaluation_chain_blocker_visibility_gap"
CHAIN_GOVERNANCE_VISIBILITY_GAP = "evaluation_chain_governance_visibility_gap"
CHAIN_UNSUPPORTED_VISIBILITY_GAP = "evaluation_chain_unsupported_visibility_gap"
CHAIN_PROHIBITED_VISIBILITY_GAP = "evaluation_chain_prohibited_visibility_gap"
CHAIN_PROVENANCE_GAP = "evaluation_chain_provenance_gap"
CHAIN_EXPLAINABILITY_GAP = "evaluation_chain_explainability_gap"
CHAIN_INTEGRITY_GAP = "evaluation_chain_integrity_gap"
CHAIN_REPLAY_SAFETY_GAP = "evaluation_chain_replay_safety_gap"
CHAIN_ROLLBACK_SAFETY_GAP = "evaluation_chain_rollback_safety_gap"
CHAIN_NON_EXECUTION_GAP = "evaluation_chain_non_execution_gap"

CHAIN_AUDIT_STABLE = "evaluation_chain_audit_stable"
CHAIN_AUDIT_BLOCKED_BY_CONTINUITY_GAP = "evaluation_chain_audit_blocked_by_continuity_gap"

CHAIN_EXPLAINABILITY_STABLE = "evaluation_chain_explainability_stable"
CHAIN_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "evaluation_chain_explainability_blocked_by_visibility_gap"

CHAIN_INTEGRITY_STABLE = "evaluation_chain_integrity_stable"
CHAIN_INTEGRITY_BLOCKED_BY_SOURCE_GAP = "evaluation_chain_integrity_blocked_by_source_gap"
CHAIN_INTEGRITY_BLOCKED_BY_HASH_GAP = "evaluation_chain_integrity_blocked_by_hash_gap"
CHAIN_INTEGRITY_BLOCKED_BY_CONTINUITY_GAP = "evaluation_chain_integrity_blocked_by_continuity_gap"
CHAIN_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "evaluation_chain_integrity_blocked_by_explainability_gap"


@dataclass(frozen=True)
class OrchestrationEvaluationChainIdentifier:
    chain_id: str
    packet_id: str
    trace_id: str
    preflight_id: str
    mapping_id: str
    intent_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationEvaluationChainFinding:
    chain_id: str
    link_type: str
    classification: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationChainAuditRecord:
    identifier: OrchestrationEvaluationChainIdentifier
    chain_state: str
    policy_ids: tuple[str, ...]
    compatibility_relationship_ids: tuple[str, ...]
    resolution_ids: tuple[str, ...]
    governance_boundaries: tuple[str, ...]
    compatibility_domains: tuple[str, ...]
    dependency_domains: tuple[str, ...]
    blocker_domains: tuple[str, ...]
    unsupported_domains: tuple[str, ...]
    prohibited_domains: tuple[str, ...]
    supported_domains: tuple[str, ...]
    source_hashes: Mapping[str, str]
    link_continuity: Mapping[str, str]
    provenance_evidence: tuple[str, ...]
    explainability_evidence: tuple[str, ...]
    integrity_evidence: tuple[str, ...]
    blocker_visibility: tuple[str, ...]
    governance_visibility: tuple[str, ...]
    compatibility_visibility: tuple[str, ...]
    dependency_visibility: tuple[str, ...]
    replay_visibility: tuple[str, ...]
    rollback_visibility: tuple[str, ...]
    findings: tuple[OrchestrationEvaluationChainFinding, ...]
    replay_safe: bool
    rollback_safe: bool
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
    persistent_write_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationEvaluationChainAuditInput:
    policy_registry: Any
    compatibility_registry: Any
    resolution_registry: Any
    intent_registry: Any
    mapping_registry: Any
    preflight_registry: Any
    trace_registry: Any
    replay_registry: Any
    replay_build_result: Any
    replay_explainability_result: Any
    replay_integrity_result: Any
    expected_source_hashes: Mapping[str, str] | None = None
    expected_chain_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationEvaluationChainAuditResult:
    audit_id: str
    chain_audit_status: str
    planning_only: bool
    audit_records: tuple[OrchestrationEvaluationChainAuditRecord, ...]
    audited_chain_count: int
    valid_chain_count: int
    invalid_chain_count: int
    policy_continuity_status: str
    compatibility_continuity_status: str
    resolution_continuity_status: str
    intent_continuity_status: str
    mapping_continuity_status: str
    preflight_continuity_status: str
    trace_continuity_status: str
    replay_continuity_status: str
    blocker_chain_continuity_status: str
    governance_boundary_continuity_status: str
    provenance_continuity_status: str
    explainability_continuity_status: str
    integrity_continuity_status: str
    replay_safety_status: str
    rollback_safety_status: str
    finding_summary: tuple[OrchestrationEvaluationChainFinding, ...]
    deterministic_source_hashes: Mapping[str, str]
    deterministic_chain_audit_hash: str
    deterministic_explanation_summary: str
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
    persistent_write_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationEvaluationChainExplanationRecord:
    chain_id: str
    packet_id: str
    explanation_status: str
    audited_chain_visibility: tuple[str, ...]
    valid_link_visibility: tuple[str, ...]
    missing_link_visibility: tuple[str, ...]
    blocker_visibility: tuple[str, ...]
    unsupported_visibility: tuple[str, ...]
    prohibited_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    explainability_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]
    replay_safety_visibility: tuple[str, ...]
    rollback_safety_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationChainExplainabilityResult:
    audit_id: str
    chain_explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationEvaluationChainExplanationRecord, ...]
    valid_link_count: int
    missing_link_count: int
    blocker_visibility_count: int
    unsupported_visibility_count: int
    prohibited_visibility_count: int
    provenance_visibility_count: int
    explainability_visibility_count: int
    integrity_visibility_count: int
    deterministic_chain_explainability_hash: str
    deterministic_explanation_summary: str


@dataclass(frozen=True)
class OrchestrationEvaluationChainIntegritySummary:
    area: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationEvaluationChainIntegrityInput:
    audit_result: OrchestrationEvaluationChainAuditResult
    explainability_result: OrchestrationEvaluationChainExplainabilityResult
    expected_audit_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationEvaluationChainIntegrityResult:
    audit_id: str
    chain_integrity_status: str
    planning_only: bool
    source_evidence_integrity: OrchestrationEvaluationChainIntegritySummary
    chain_hash_integrity: OrchestrationEvaluationChainIntegritySummary
    replay_packet_integrity: OrchestrationEvaluationChainIntegritySummary
    trace_integrity: OrchestrationEvaluationChainIntegritySummary
    preflight_integrity: OrchestrationEvaluationChainIntegritySummary
    mapping_integrity: OrchestrationEvaluationChainIntegritySummary
    intent_integrity: OrchestrationEvaluationChainIntegritySummary
    policy_integrity: OrchestrationEvaluationChainIntegritySummary
    compatibility_integrity: OrchestrationEvaluationChainIntegritySummary
    resolution_integrity: OrchestrationEvaluationChainIntegritySummary
    blocker_integrity: OrchestrationEvaluationChainIntegritySummary
    governance_integrity: OrchestrationEvaluationChainIntegritySummary
    provenance_integrity: OrchestrationEvaluationChainIntegritySummary
    explainability_integrity: OrchestrationEvaluationChainIntegritySummary
    replay_safety_integrity: OrchestrationEvaluationChainIntegritySummary
    rollback_safety_integrity: OrchestrationEvaluationChainIntegritySummary
    deterministic_serialization_integrity: OrchestrationEvaluationChainIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_chain_integrity_hash: str
    deterministic_explanation_summary: str
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
    persistent_write_enabled: bool = False


def export_chain_finding(finding: OrchestrationEvaluationChainFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_chain_audit_record(record: OrchestrationEvaluationChainAuditRecord) -> dict[str, Any]:
    data = _export_chain_audit_record_base(record)
    data["deterministic_chain_record_hash"] = hash_chain_audit_record(record)
    return data


def serialize_chain_audit_record(record: OrchestrationEvaluationChainAuditRecord) -> str:
    return stable_serialize(export_chain_audit_record(record))


def hash_chain_audit_record(record: OrchestrationEvaluationChainAuditRecord) -> str:
    return deterministic_hash(_export_chain_audit_record_base(record))


def export_chain_audit_result(result: OrchestrationEvaluationChainAuditResult) -> dict[str, Any]:
    data = asdict(result)
    data["audit_records"] = [
        export_chain_audit_record(record)
        for record in sorted(result.audit_records, key=lambda item: item.identifier.chain_id)
    ]
    data["finding_summary"] = [
        export_chain_finding(finding)
        for finding in sorted(result.finding_summary, key=_finding_sort_key)
    ]
    data["deterministic_source_hashes"] = dict(sorted(result.deterministic_source_hashes.items()))
    return data


def serialize_chain_audit_result(result: OrchestrationEvaluationChainAuditResult) -> str:
    return stable_serialize(export_chain_audit_result(result))


def hash_chain_audit_result(result: OrchestrationEvaluationChainAuditResult) -> str:
    data = export_chain_audit_result(result)
    data.pop("deterministic_chain_audit_hash", None)
    return deterministic_hash(data)


def export_chain_explanation_record(record: OrchestrationEvaluationChainExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "audited_chain_visibility",
        "valid_link_visibility",
        "missing_link_visibility",
        "blocker_visibility",
        "unsupported_visibility",
        "prohibited_visibility",
        "provenance_visibility",
        "explainability_visibility",
        "integrity_visibility",
        "replay_safety_visibility",
        "rollback_safety_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_chain_explainability_result(result: OrchestrationEvaluationChainExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_chain_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.chain_id)
    ]
    return data


def serialize_chain_explainability_result(result: OrchestrationEvaluationChainExplainabilityResult) -> str:
    return stable_serialize(export_chain_explainability_result(result))


def hash_chain_explainability_result(result: OrchestrationEvaluationChainExplainabilityResult) -> str:
    data = export_chain_explainability_result(result)
    data.pop("deterministic_chain_explainability_hash", None)
    return deterministic_hash(data)


def export_chain_integrity_summary(summary: OrchestrationEvaluationChainIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_chain_integrity_result(result: OrchestrationEvaluationChainIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "source_evidence_integrity",
        "chain_hash_integrity",
        "replay_packet_integrity",
        "trace_integrity",
        "preflight_integrity",
        "mapping_integrity",
        "intent_integrity",
        "policy_integrity",
        "compatibility_integrity",
        "resolution_integrity",
        "blocker_integrity",
        "governance_integrity",
        "provenance_integrity",
        "explainability_integrity",
        "replay_safety_integrity",
        "rollback_safety_integrity",
        "deterministic_serialization_integrity",
    ):
        data[field] = export_chain_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_chain_integrity_result(result: OrchestrationEvaluationChainIntegrityResult) -> str:
    return stable_serialize(export_chain_integrity_result(result))


def hash_chain_integrity_result(result: OrchestrationEvaluationChainIntegrityResult) -> str:
    data = export_chain_integrity_result(result)
    data.pop("deterministic_chain_integrity_hash", None)
    return deterministic_hash(data)


def _export_chain_audit_record_base(record: OrchestrationEvaluationChainAuditRecord) -> dict[str, Any]:
    data = asdict(record)
    data["identifier"] = asdict(record.identifier)
    data["source_hashes"] = dict(sorted(record.source_hashes.items()))
    data["link_continuity"] = dict(sorted(record.link_continuity.items()))
    data["findings"] = [
        export_chain_finding(finding)
        for finding in sorted(record.findings, key=_finding_sort_key)
    ]
    for field in (
        "policy_ids",
        "compatibility_relationship_ids",
        "resolution_ids",
        "governance_boundaries",
        "compatibility_domains",
        "dependency_domains",
        "blocker_domains",
        "unsupported_domains",
        "prohibited_domains",
        "supported_domains",
        "provenance_evidence",
        "explainability_evidence",
        "integrity_evidence",
        "blocker_visibility",
        "governance_visibility",
        "compatibility_visibility",
        "dependency_visibility",
        "replay_visibility",
        "rollback_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def _finding_sort_key(finding: OrchestrationEvaluationChainFinding) -> tuple[str, str, str, str]:
    return (finding.chain_id, finding.link_type, finding.classification, finding.reason)
