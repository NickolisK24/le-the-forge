"""Deterministic orchestration compatibility resolution-audit models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


RESOLUTION_INTENTIONAL_BLOCK = "intentional_block"
RESOLUTION_FUTURE_CANDIDATE = "future_candidate"
RESOLUTION_UNSUPPORTED_BY_DESIGN = "unsupported_by_design"
RESOLUTION_GOVERNANCE_CONFLICT = "governance_conflict"
RESOLUTION_DEPENDENCY_CONFLICT = "dependency_conflict"
RESOLUTION_CONTINUITY_CONFLICT = "continuity_conflict"
RESOLUTION_EVIDENCE_INCOMPLETE = "evidence_incomplete"
RESOLUTION_PROVENANCE_GAP = "provenance_gap"
RESOLUTION_EXPLAINABILITY_GAP = "explainability_gap"
RESOLUTION_POTENTIAL_MISCLASSIFICATION = "potential_misclassification"
RESOLUTION_CLASSIFICATIONS: tuple[str, ...] = (
    RESOLUTION_INTENTIONAL_BLOCK,
    RESOLUTION_FUTURE_CANDIDATE,
    RESOLUTION_UNSUPPORTED_BY_DESIGN,
    RESOLUTION_GOVERNANCE_CONFLICT,
    RESOLUTION_DEPENDENCY_CONFLICT,
    RESOLUTION_CONTINUITY_CONFLICT,
    RESOLUTION_EVIDENCE_INCOMPLETE,
    RESOLUTION_PROVENANCE_GAP,
    RESOLUTION_EXPLAINABILITY_GAP,
    RESOLUTION_POTENTIAL_MISCLASSIFICATION,
)

RESOLUTION_CONTINUITY_PRESERVED = "resolution_continuity_preserved"
RESOLUTION_CONTINUITY_GAP = "resolution_continuity_gap"

RESOLUTION_AUDIT_STABLE = "resolution_audit_stable"
RESOLUTION_AUDIT_STABLE_WITH_VISIBLE_FINDINGS = "resolution_audit_stable_with_visible_findings"
RESOLUTION_AUDIT_BLOCKED_BY_CONTINUITY_GAP = "resolution_audit_blocked_by_continuity_gap"

RESOLUTION_EXPLAINABILITY_STABLE = "resolution_explainability_stable"
RESOLUTION_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP = "resolution_explainability_blocked_by_visibility_gap"

RESOLUTION_INTEGRITY_STABLE = "resolution_integrity_stable"
RESOLUTION_INTEGRITY_BLOCKED_BY_REGISTRY_GAP = "resolution_integrity_blocked_by_registry_gap"
RESOLUTION_INTEGRITY_BLOCKED_BY_HASH_GAP = "resolution_integrity_blocked_by_hash_gap"
RESOLUTION_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP = "resolution_integrity_blocked_by_provenance_gap"
RESOLUTION_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP = "resolution_integrity_blocked_by_explainability_gap"
RESOLUTION_INTEGRITY_BLOCKED_BY_BLOCKER_GAP = "resolution_integrity_blocked_by_blocker_gap"
RESOLUTION_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP = "resolution_integrity_blocked_by_evidence_gap"
RESOLUTION_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP = "resolution_integrity_blocked_by_governance_gap"
RESOLUTION_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP = "resolution_integrity_blocked_by_compatibility_gap"


@dataclass(frozen=True)
class OrchestrationPolicyResolutionIdentifier:
    resolution_id: str
    relationship_id: str
    namespace: str
    version: str


@dataclass(frozen=True)
class OrchestrationPolicyResolutionProvenance:
    source_phase: str
    source_artifact: str
    compatibility_relationship_id: str
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyResolutionEvidenceGap:
    evidence_gap_id: str
    missing_evidence_ids: tuple[str, ...]
    required_before_status_change: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyResolutionRecord:
    identifier: OrchestrationPolicyResolutionIdentifier
    compatibility_state: str
    resolution_classifications: tuple[str, ...]
    block_intentional: bool
    future_support_possible: bool
    evidence_gaps: tuple[OrchestrationPolicyResolutionEvidenceGap, ...]
    governance_constraints: tuple[str, ...]
    dependency_gaps: tuple[str, ...]
    continuity_gaps: tuple[str, ...]
    blocker_chain_ids: tuple[str, ...]
    compatibility_evidence_ids: tuple[str, ...]
    provenance: OrchestrationPolicyResolutionProvenance
    governance_metadata: Mapping[str, Any]
    support_rationale: tuple[str, ...]
    resolution_explainability_ids: tuple[str, ...]
    resolution_integrity_ids: tuple[str, ...]
    status_change_allowed: bool = False
    automatic_resolution_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    background_processing_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyResolutionRegistry:
    registry_id: str
    schema_version: str
    records: tuple[OrchestrationPolicyResolutionRecord, ...]
    registry_metadata: Mapping[str, Any]
    planning_only: bool = True
    non_production: bool = True


@dataclass(frozen=True)
class OrchestrationPolicyResolutionFinding:
    resolution_id: str
    classification: str
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyResolutionAuditRecord:
    resolution_id: str
    relationship_id: str
    compatibility_state: str
    resolution_classifications: tuple[str, ...]
    resolution_hash: str
    block_intentional: bool
    future_support_possible: bool
    evidence_gap_count: int
    governance_constraint_count: int
    dependency_gap_count: int
    continuity_gap_count: int
    blocker_chain_count: int
    provenance_continuity_state: str
    explainability_continuity_state: str
    integrity_continuity_state: str
    findings: tuple[OrchestrationPolicyResolutionFinding, ...]


@dataclass(frozen=True)
class OrchestrationPolicyResolutionAuditInput:
    resolution_registry: OrchestrationPolicyResolutionRegistry
    expected_registry_hash: str | None = None
    expected_resolution_hashes: Mapping[str, str] | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationPolicyResolutionAuditResult:
    registry_id: str
    resolution_audit_status: str
    planning_only: bool
    audit_records: tuple[OrchestrationPolicyResolutionAuditRecord, ...]
    intentional_block_count: int
    future_candidate_count: int
    unsupported_by_design_count: int
    governance_conflict_count: int
    dependency_conflict_count: int
    continuity_conflict_count: int
    evidence_incomplete_count: int
    provenance_gap_count: int
    explainability_gap_count: int
    potential_misclassification_count: int
    blocker_chain_total: int
    provenance_continuity_status: str
    explainability_continuity_status: str
    integrity_continuity_status: str
    finding_summary: tuple[OrchestrationPolicyResolutionFinding, ...]
    deterministic_registry_hash: str
    deterministic_resolution_audit_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    automatic_resolution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyResolutionExplanationRecord:
    resolution_id: str
    relationship_id: str
    resolution_classifications: tuple[str, ...]
    explanation_status: str
    why_blocked: tuple[str, ...]
    block_intent_visibility: tuple[str, ...]
    future_support_visibility: tuple[str, ...]
    evidence_gap_visibility: tuple[str, ...]
    governance_visibility: tuple[str, ...]
    dependency_visibility: tuple[str, ...]
    continuity_visibility: tuple[str, ...]
    provenance_visibility: tuple[str, ...]
    blocker_chain_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyResolutionExplainabilityResult:
    registry_id: str
    resolution_explainability_status: str
    planning_only: bool
    explanation_records: tuple[OrchestrationPolicyResolutionExplanationRecord, ...]
    blocked_explanation_count: int
    future_support_explanation_count: int
    evidence_gap_visibility_count: int
    governance_visibility_count: int
    dependency_visibility_count: int
    continuity_visibility_count: int
    provenance_visibility_count: int
    blocker_chain_visibility_count: int
    deterministic_resolution_explainability_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    automatic_resolution_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationPolicyResolutionIntegritySummary:
    integrity_type: str
    references: tuple[str, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPolicyResolutionIntegrityInput:
    resolution_registry: OrchestrationPolicyResolutionRegistry
    audit_result: OrchestrationPolicyResolutionAuditResult
    explainability_result: OrchestrationPolicyResolutionExplainabilityResult
    expected_registry_hash: str | None = None
    expected_audit_hash: str | None = None
    expected_explainability_hash: str | None = None
    manual_review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrchestrationPolicyResolutionIntegrityResult:
    registry_id: str
    resolution_integrity_status: str
    planning_only: bool
    registry_integrity: OrchestrationPolicyResolutionIntegritySummary
    resolution_hash_integrity: OrchestrationPolicyResolutionIntegritySummary
    provenance_integrity: OrchestrationPolicyResolutionIntegritySummary
    explainability_integrity: OrchestrationPolicyResolutionIntegritySummary
    blocker_integrity: OrchestrationPolicyResolutionIntegritySummary
    evidence_integrity: OrchestrationPolicyResolutionIntegritySummary
    governance_integrity: OrchestrationPolicyResolutionIntegritySummary
    compatibility_integrity: OrchestrationPolicyResolutionIntegritySummary
    deterministic_serialization_integrity: OrchestrationPolicyResolutionIntegritySummary
    failure_classification_summary: tuple[str, ...]
    manual_review_summary: tuple[str, ...]
    deterministic_resolution_integrity_hash: str
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    production_consumption_enabled: bool = False
    automatic_resolution_enabled: bool = False


def export_resolution_evidence_gap(gap: OrchestrationPolicyResolutionEvidenceGap) -> dict[str, Any]:
    data = asdict(gap)
    data["missing_evidence_ids"] = sorted(data["missing_evidence_ids"])
    data["required_before_status_change"] = sorted(data["required_before_status_change"])
    return data


def export_resolution_provenance(provenance: OrchestrationPolicyResolutionProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field in ("replay_reference_ids", "rollback_reference_ids", "governance_reference_ids"):
        data[field] = sorted(data[field])
    return data


def export_resolution_record(record: OrchestrationPolicyResolutionRecord) -> dict[str, Any]:
    data = _export_resolution_record_base(record)
    data["deterministic_resolution_hash"] = hash_resolution_record(record)
    return data


def serialize_resolution_record(record: OrchestrationPolicyResolutionRecord) -> str:
    return stable_serialize(export_resolution_record(record))


def hash_resolution_record(record: OrchestrationPolicyResolutionRecord) -> str:
    return deterministic_hash(_export_resolution_record_base(record))


def export_resolution_registry(registry: OrchestrationPolicyResolutionRegistry) -> dict[str, Any]:
    data = asdict(registry)
    data["records"] = [export_resolution_record(record) for record in sorted(registry.records, key=lambda item: item.identifier.resolution_id)]
    data["registry_metadata"] = dict(sorted(registry.registry_metadata.items()))
    data["deterministic_resolution_registry_hash"] = hash_resolution_registry(registry)
    return data


def serialize_resolution_registry(registry: OrchestrationPolicyResolutionRegistry) -> str:
    return stable_serialize(export_resolution_registry(registry))


def hash_resolution_registry(registry: OrchestrationPolicyResolutionRegistry) -> str:
    return deterministic_hash(
        {
            "registry_id": registry.registry_id,
            "schema_version": registry.schema_version,
            "records": [export_resolution_record(record) for record in sorted(registry.records, key=lambda item: item.identifier.resolution_id)],
            "registry_metadata": dict(sorted(registry.registry_metadata.items())),
            "planning_only": registry.planning_only,
            "non_production": registry.non_production,
        }
    )


def export_resolution_finding(finding: OrchestrationPolicyResolutionFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_ids"] = sorted(data["evidence_ids"])
    return data


def export_resolution_audit_record(record: OrchestrationPolicyResolutionAuditRecord) -> dict[str, Any]:
    data = asdict(record)
    data["resolution_classifications"] = sorted(data["resolution_classifications"])
    data["findings"] = [export_resolution_finding(finding) for finding in sorted(record.findings, key=_finding_sort_key)]
    return data


def export_resolution_audit_result(result: OrchestrationPolicyResolutionAuditResult) -> dict[str, Any]:
    data = asdict(result)
    data["audit_records"] = [export_resolution_audit_record(record) for record in sorted(result.audit_records, key=lambda item: item.resolution_id)]
    data["finding_summary"] = [export_resolution_finding(finding) for finding in sorted(result.finding_summary, key=_finding_sort_key)]
    return data


def serialize_resolution_audit_result(result: OrchestrationPolicyResolutionAuditResult) -> str:
    return stable_serialize(export_resolution_audit_result(result))


def hash_resolution_audit_result(result: OrchestrationPolicyResolutionAuditResult) -> str:
    data = export_resolution_audit_result(result)
    data.pop("deterministic_resolution_audit_hash", None)
    return deterministic_hash(data)


def export_resolution_explanation_record(record: OrchestrationPolicyResolutionExplanationRecord) -> dict[str, Any]:
    data = asdict(record)
    for field in (
        "resolution_classifications",
        "why_blocked",
        "block_intent_visibility",
        "future_support_visibility",
        "evidence_gap_visibility",
        "governance_visibility",
        "dependency_visibility",
        "continuity_visibility",
        "provenance_visibility",
        "blocker_chain_visibility",
        "integrity_visibility",
    ):
        data[field] = sorted(data[field])
    return data


def export_resolution_explainability_result(result: OrchestrationPolicyResolutionExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["explanation_records"] = [
        export_resolution_explanation_record(record)
        for record in sorted(result.explanation_records, key=lambda item: item.resolution_id)
    ]
    return data


def serialize_resolution_explainability_result(result: OrchestrationPolicyResolutionExplainabilityResult) -> str:
    return stable_serialize(export_resolution_explainability_result(result))


def hash_resolution_explainability_result(result: OrchestrationPolicyResolutionExplainabilityResult) -> str:
    data = export_resolution_explainability_result(result)
    data.pop("deterministic_resolution_explainability_hash", None)
    return deterministic_hash(data)


def export_resolution_integrity_summary(summary: OrchestrationPolicyResolutionIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["references"] = sorted(data["references"])
    data["failures"] = sorted(data["failures"])
    return data


def export_resolution_integrity_result(result: OrchestrationPolicyResolutionIntegrityResult) -> dict[str, Any]:
    data = asdict(result)
    for field in (
        "registry_integrity",
        "resolution_hash_integrity",
        "provenance_integrity",
        "explainability_integrity",
        "blocker_integrity",
        "evidence_integrity",
        "governance_integrity",
        "compatibility_integrity",
        "deterministic_serialization_integrity",
    ):
        data[field] = export_resolution_integrity_summary(getattr(result, field))
    data["failure_classification_summary"] = sorted(data["failure_classification_summary"])
    data["manual_review_summary"] = sorted(data["manual_review_summary"])
    return data


def serialize_resolution_integrity_result(result: OrchestrationPolicyResolutionIntegrityResult) -> str:
    return stable_serialize(export_resolution_integrity_result(result))


def hash_resolution_integrity_result(result: OrchestrationPolicyResolutionIntegrityResult) -> str:
    data = export_resolution_integrity_result(result)
    data.pop("deterministic_resolution_integrity_hash", None)
    return deterministic_hash(data)


def _export_resolution_record_base(record: OrchestrationPolicyResolutionRecord) -> dict[str, Any]:
    data = asdict(record)
    data["identifier"] = asdict(record.identifier)
    data["resolution_classifications"] = sorted(data["resolution_classifications"])
    data["evidence_gaps"] = [export_resolution_evidence_gap(gap) for gap in sorted(record.evidence_gaps, key=lambda item: item.evidence_gap_id)]
    data["provenance"] = export_resolution_provenance(record.provenance)
    data["governance_metadata"] = dict(sorted(record.governance_metadata.items()))
    for field in (
        "governance_constraints",
        "dependency_gaps",
        "continuity_gaps",
        "blocker_chain_ids",
        "compatibility_evidence_ids",
        "support_rationale",
        "resolution_explainability_ids",
        "resolution_integrity_ids",
    ):
        data[field] = sorted(data[field])
    return data


def _finding_sort_key(finding: OrchestrationPolicyResolutionFinding) -> tuple[str, str, str]:
    return (finding.resolution_id, finding.classification, finding.reason)
