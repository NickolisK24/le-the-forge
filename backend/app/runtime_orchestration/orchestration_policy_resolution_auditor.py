"""Deterministic orchestration compatibility resolution auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_compatibility_models import (
    COMPATIBILITY_DEPENDENCY_BLOCKED,
    COMPATIBILITY_GOVERNANCE_BLOCKED,
    COMPATIBILITY_INCOMPATIBLE,
    COMPATIBILITY_PROHIBITED,
    COMPATIBILITY_UNSUPPORTED,
)
from .orchestration_policy_resolution_models import (
    RESOLUTION_AUDIT_BLOCKED_BY_CONTINUITY_GAP,
    RESOLUTION_AUDIT_STABLE,
    RESOLUTION_AUDIT_STABLE_WITH_VISIBLE_FINDINGS,
    RESOLUTION_CLASSIFICATIONS,
    RESOLUTION_CONTINUITY_CONFLICT,
    RESOLUTION_CONTINUITY_GAP,
    RESOLUTION_CONTINUITY_PRESERVED,
    RESOLUTION_DEPENDENCY_CONFLICT,
    RESOLUTION_EVIDENCE_INCOMPLETE,
    RESOLUTION_EXPLAINABILITY_GAP,
    RESOLUTION_FUTURE_CANDIDATE,
    RESOLUTION_GOVERNANCE_CONFLICT,
    RESOLUTION_INTENTIONAL_BLOCK,
    RESOLUTION_POTENTIAL_MISCLASSIFICATION,
    RESOLUTION_PROVENANCE_GAP,
    RESOLUTION_UNSUPPORTED_BY_DESIGN,
    OrchestrationPolicyResolutionAuditInput,
    OrchestrationPolicyResolutionAuditRecord,
    OrchestrationPolicyResolutionAuditResult,
    OrchestrationPolicyResolutionFinding,
    OrchestrationPolicyResolutionRecord,
    export_resolution_audit_result,
    hash_resolution_audit_result,
    hash_resolution_record,
    hash_resolution_registry,
    serialize_resolution_audit_result,
)
from .orchestration_policy_resolution_registry import default_orchestration_policy_resolution_registry


STRUCTURAL_RESOLUTION_FINDINGS: frozenset[str] = frozenset(
    {
        RESOLUTION_CONTINUITY_CONFLICT,
        RESOLUTION_PROVENANCE_GAP,
        RESOLUTION_EXPLAINABILITY_GAP,
    }
)


def default_orchestration_policy_resolution_audit_input() -> OrchestrationPolicyResolutionAuditInput:
    return OrchestrationPolicyResolutionAuditInput(
        resolution_registry=default_orchestration_policy_resolution_registry()
    )


def audit_orchestration_policy_resolution(
    audit_input: OrchestrationPolicyResolutionAuditInput | None = None,
) -> OrchestrationPolicyResolutionAuditResult:
    source = audit_input or default_orchestration_policy_resolution_audit_input()
    registry_hash = hash_resolution_registry(source.resolution_registry)
    records = tuple(_audit_record(record, source) for record in source.resolution_registry.records)
    findings = tuple(sorted((finding for record in records for finding in record.findings), key=_finding_sort_key))
    registry_hash_finding = _registry_hash_finding(source, registry_hash)
    if registry_hash_finding is not None:
        findings = tuple(sorted(findings + (registry_hash_finding,), key=_finding_sort_key))
    status = _audit_status(records, findings)
    result = OrchestrationPolicyResolutionAuditResult(
        registry_id=source.resolution_registry.registry_id,
        resolution_audit_status=status,
        planning_only=True,
        audit_records=records,
        intentional_block_count=_classification_count(records, RESOLUTION_INTENTIONAL_BLOCK),
        future_candidate_count=_classification_count(records, RESOLUTION_FUTURE_CANDIDATE),
        unsupported_by_design_count=_classification_count(records, RESOLUTION_UNSUPPORTED_BY_DESIGN),
        governance_conflict_count=_classification_count(records, RESOLUTION_GOVERNANCE_CONFLICT),
        dependency_conflict_count=_classification_count(records, RESOLUTION_DEPENDENCY_CONFLICT),
        continuity_conflict_count=_classification_count(records, RESOLUTION_CONTINUITY_CONFLICT),
        evidence_incomplete_count=_classification_count(records, RESOLUTION_EVIDENCE_INCOMPLETE),
        provenance_gap_count=_classification_count(records, RESOLUTION_PROVENANCE_GAP),
        explainability_gap_count=_classification_count(records, RESOLUTION_EXPLAINABILITY_GAP),
        potential_misclassification_count=_classification_count(records, RESOLUTION_POTENTIAL_MISCLASSIFICATION),
        blocker_chain_total=sum(record.blocker_chain_count for record in records),
        provenance_continuity_status=_continuity_status(records, "provenance_continuity_state"),
        explainability_continuity_status=_continuity_status(records, "explainability_continuity_state"),
        integrity_continuity_status=_continuity_status(records, "integrity_continuity_state"),
        finding_summary=findings,
        deterministic_registry_hash=registry_hash,
        deterministic_resolution_audit_hash="",
        deterministic_explanation_summary=_summary(status, findings),
    )
    return replace(result, deterministic_resolution_audit_hash=hash_resolution_audit_result(result))


def export_orchestration_policy_resolution_audit_result(
    result: OrchestrationPolicyResolutionAuditResult,
) -> dict[str, object]:
    return export_resolution_audit_result(result)


def serialize_orchestration_policy_resolution_audit_result(
    result: OrchestrationPolicyResolutionAuditResult,
) -> str:
    return serialize_resolution_audit_result(result)


def hash_orchestration_policy_resolution_audit_result(
    result: OrchestrationPolicyResolutionAuditResult,
) -> str:
    return hash_resolution_audit_result(result)


def _audit_record(
    record: OrchestrationPolicyResolutionRecord,
    source: OrchestrationPolicyResolutionAuditInput,
) -> OrchestrationPolicyResolutionAuditRecord:
    record_hash = hash_resolution_record(record)
    findings = _classification_findings(record)
    findings.extend(_continuity_findings(record))
    expected_hash = source.expected_resolution_hashes.get(record.identifier.resolution_id) if source.expected_resolution_hashes else None
    if expected_hash is not None and expected_hash != record_hash:
        findings.append(
            OrchestrationPolicyResolutionFinding(
                resolution_id=record.identifier.resolution_id,
                classification=RESOLUTION_CONTINUITY_CONFLICT,
                reason="resolution record hash does not match expected deterministic hash",
                evidence_ids=(record_hash, expected_hash),
            )
        )
    classifications = tuple(sorted({*record.resolution_classifications, *(finding.classification for finding in findings)}))
    provenance_continuity = RESOLUTION_CONTINUITY_GAP if any(finding.classification == RESOLUTION_PROVENANCE_GAP for finding in findings) else RESOLUTION_CONTINUITY_PRESERVED
    explainability_continuity = RESOLUTION_CONTINUITY_GAP if any(finding.classification == RESOLUTION_EXPLAINABILITY_GAP for finding in findings) else RESOLUTION_CONTINUITY_PRESERVED
    integrity_continuity = RESOLUTION_CONTINUITY_GAP if any(finding.classification == RESOLUTION_CONTINUITY_CONFLICT for finding in findings) else RESOLUTION_CONTINUITY_PRESERVED
    return OrchestrationPolicyResolutionAuditRecord(
        resolution_id=record.identifier.resolution_id,
        relationship_id=record.identifier.relationship_id,
        compatibility_state=record.compatibility_state,
        resolution_classifications=classifications,
        resolution_hash=record_hash,
        block_intentional=record.block_intentional,
        future_support_possible=record.future_support_possible,
        evidence_gap_count=len(record.evidence_gaps),
        governance_constraint_count=len(record.governance_constraints),
        dependency_gap_count=len(record.dependency_gaps),
        continuity_gap_count=len(record.continuity_gaps),
        blocker_chain_count=len(record.blocker_chain_ids),
        provenance_continuity_state=provenance_continuity,
        explainability_continuity_state=explainability_continuity,
        integrity_continuity_state=integrity_continuity,
        findings=tuple(sorted(findings, key=_finding_sort_key)),
    )


def _classification_findings(record: OrchestrationPolicyResolutionRecord) -> list[OrchestrationPolicyResolutionFinding]:
    findings: list[OrchestrationPolicyResolutionFinding] = []
    for classification in sorted(record.resolution_classifications):
        findings.append(
            OrchestrationPolicyResolutionFinding(
                resolution_id=record.identifier.resolution_id,
                classification=classification,
                reason=_classification_reason(record, classification),
                evidence_ids=_classification_evidence(record, classification),
            )
        )
    findings.extend(_derived_gap_findings(record))
    return findings


def _derived_gap_findings(record: OrchestrationPolicyResolutionRecord) -> list[OrchestrationPolicyResolutionFinding]:
    findings: list[OrchestrationPolicyResolutionFinding] = []
    missing_provenance = _missing_provenance(record)
    if missing_provenance:
        findings.append(
            OrchestrationPolicyResolutionFinding(
                resolution_id=record.identifier.resolution_id,
                classification=RESOLUTION_PROVENANCE_GAP,
                reason="resolution provenance continuity gap",
                evidence_ids=missing_provenance,
            )
        )
    if not record.resolution_explainability_ids:
        findings.append(
            OrchestrationPolicyResolutionFinding(
                resolution_id=record.identifier.resolution_id,
                classification=RESOLUTION_EXPLAINABILITY_GAP,
                reason="resolution explainability reference is missing",
                evidence_ids=(record.identifier.relationship_id,),
            )
        )
    if not record.resolution_integrity_ids:
        findings.append(
            OrchestrationPolicyResolutionFinding(
                resolution_id=record.identifier.resolution_id,
                classification=RESOLUTION_CONTINUITY_CONFLICT,
                reason="resolution integrity reference is missing",
                evidence_ids=(record.identifier.relationship_id,),
            )
        )
    if _potential_misclassification(record):
        findings.append(
            OrchestrationPolicyResolutionFinding(
                resolution_id=record.identifier.resolution_id,
                classification=RESOLUTION_POTENTIAL_MISCLASSIFICATION,
                reason="resolution classification conflicts with compatibility state or required evidence",
                evidence_ids=(record.compatibility_state, *record.resolution_classifications),
            )
        )
    return findings


def _continuity_findings(record: OrchestrationPolicyResolutionRecord) -> list[OrchestrationPolicyResolutionFinding]:
    findings: list[OrchestrationPolicyResolutionFinding] = []
    if record.continuity_gaps:
        findings.append(
            OrchestrationPolicyResolutionFinding(
                resolution_id=record.identifier.resolution_id,
                classification=RESOLUTION_CONTINUITY_CONFLICT,
                reason="explicit resolution continuity gaps are present",
                evidence_ids=record.continuity_gaps,
            )
        )
    if _governance_continuity_gap(record):
        findings.append(
            OrchestrationPolicyResolutionFinding(
                resolution_id=record.identifier.resolution_id,
                classification=RESOLUTION_CONTINUITY_CONFLICT,
                reason="resolution governance boundary is not planning-only",
                evidence_ids=(record.identifier.relationship_id,),
            )
        )
    return findings


def _classification_reason(record: OrchestrationPolicyResolutionRecord, classification: str) -> str:
    if classification == RESOLUTION_INTENTIONAL_BLOCK:
        return "relationship is intentionally blocked by prohibited compatibility governance"
    if classification == RESOLUTION_UNSUPPORTED_BY_DESIGN:
        return "relationship remains unsupported by design"
    if classification == RESOLUTION_FUTURE_CANDIDATE:
        return "relationship may be revisited only after required evidence is supplied"
    if classification == RESOLUTION_EVIDENCE_INCOMPLETE:
        return "relationship has explicit evidence gaps before any status change"
    if classification == RESOLUTION_DEPENDENCY_CONFLICT:
        return "relationship remains blocked by dependency conflict"
    if classification == RESOLUTION_GOVERNANCE_CONFLICT:
        return "relationship remains blocked by governance conflict"
    if classification == RESOLUTION_CONTINUITY_CONFLICT:
        return "relationship has continuity conflict visibility"
    if classification == RESOLUTION_PROVENANCE_GAP:
        return "relationship has provenance continuity gap visibility"
    if classification == RESOLUTION_EXPLAINABILITY_GAP:
        return "relationship has explainability continuity gap visibility"
    if classification == RESOLUTION_POTENTIAL_MISCLASSIFICATION:
        return "relationship may be misclassified and requires deterministic review"
    return "relationship classification is unsupported by the resolution audit registry"


def _classification_evidence(record: OrchestrationPolicyResolutionRecord, classification: str) -> tuple[str, ...]:
    if classification == RESOLUTION_EVIDENCE_INCOMPLETE:
        return tuple(sorted(gap.evidence_gap_id for gap in record.evidence_gaps))
    if classification == RESOLUTION_DEPENDENCY_CONFLICT:
        return tuple(sorted(record.dependency_gaps))
    if classification == RESOLUTION_GOVERNANCE_CONFLICT:
        return tuple(sorted(record.governance_constraints))
    if classification == RESOLUTION_INTENTIONAL_BLOCK:
        return tuple(sorted(record.blocker_chain_ids or record.compatibility_evidence_ids))
    if classification == RESOLUTION_UNSUPPORTED_BY_DESIGN:
        return tuple(sorted(record.blocker_chain_ids or record.compatibility_evidence_ids))
    if classification == RESOLUTION_FUTURE_CANDIDATE:
        return tuple(sorted(gap.evidence_gap_id for gap in record.evidence_gaps))
    return tuple(sorted(record.compatibility_evidence_ids))


def _missing_provenance(record: OrchestrationPolicyResolutionRecord) -> tuple[str, ...]:
    provenance = record.provenance
    missing: list[str] = []
    if not provenance.source_phase:
        missing.append("source_phase")
    if not provenance.source_artifact:
        missing.append("source_artifact")
    if not provenance.compatibility_relationship_id:
        missing.append("compatibility_relationship_id")
    if not provenance.replay_reference_ids:
        missing.append("replay_reference_ids")
    if not provenance.rollback_reference_ids:
        missing.append("rollback_reference_ids")
    if not provenance.governance_reference_ids:
        missing.append("governance_reference_ids")
    return tuple(sorted(missing))


def _potential_misclassification(record: OrchestrationPolicyResolutionRecord) -> bool:
    classifications = set(record.resolution_classifications)
    if classifications - set(RESOLUTION_CLASSIFICATIONS):
        return True
    if record.compatibility_state == COMPATIBILITY_PROHIBITED and record.future_support_possible:
        return True
    if record.compatibility_state == COMPATIBILITY_UNSUPPORTED and RESOLUTION_FUTURE_CANDIDATE in classifications:
        return True
    if record.compatibility_state == COMPATIBILITY_INCOMPATIBLE and RESOLUTION_FUTURE_CANDIDATE in classifications and not record.evidence_gaps:
        return True
    if record.compatibility_state == COMPATIBILITY_DEPENDENCY_BLOCKED and not record.dependency_gaps:
        return True
    if record.compatibility_state == COMPATIBILITY_GOVERNANCE_BLOCKED and not record.governance_constraints:
        return True
    if record.block_intentional and not record.blocker_chain_ids and record.compatibility_state in (COMPATIBILITY_PROHIBITED, COMPATIBILITY_UNSUPPORTED):
        return True
    return False


def _governance_continuity_gap(record: OrchestrationPolicyResolutionRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "resolution_audit_only")
    required_false = (
        "execution_enabled",
        "routing_enabled",
        "mutation_enabled",
        "autonomy_enabled",
        "automatic_resolution_enabled",
        "production_runtime_reads_enabled",
        "production_runtime_writes_enabled",
        "persistent_writes_enabled",
    )
    if any(metadata.get(key) is not True for key in required_true):
        return True
    if any(metadata.get(key) is not False for key in required_false):
        return True
    return any(
        (
            record.status_change_allowed,
            record.automatic_resolution_enabled,
            record.runtime_execution_enabled,
            record.orchestration_execution_enabled,
            record.routing_behavior_enabled,
            record.mutation_behavior_enabled,
            record.production_consumption_enabled,
            record.background_processing_enabled,
        )
    )


def _registry_hash_finding(
    source: OrchestrationPolicyResolutionAuditInput,
    registry_hash: str,
) -> OrchestrationPolicyResolutionFinding | None:
    if source.expected_registry_hash is None or source.expected_registry_hash == registry_hash:
        return None
    return OrchestrationPolicyResolutionFinding(
        resolution_id=source.resolution_registry.registry_id,
        classification=RESOLUTION_CONTINUITY_CONFLICT,
        reason="resolution registry hash does not match expected deterministic hash",
        evidence_ids=(registry_hash, source.expected_registry_hash),
    )


def _classification_count(records: tuple[OrchestrationPolicyResolutionAuditRecord, ...], classification: str) -> int:
    return sum(1 for record in records if classification in record.resolution_classifications)


def _continuity_status(records: tuple[OrchestrationPolicyResolutionAuditRecord, ...], field: str) -> str:
    return RESOLUTION_CONTINUITY_PRESERVED if all(getattr(record, field) == RESOLUTION_CONTINUITY_PRESERVED for record in records) else RESOLUTION_CONTINUITY_GAP


def _audit_status(
    records: tuple[OrchestrationPolicyResolutionAuditRecord, ...],
    findings: tuple[OrchestrationPolicyResolutionFinding, ...],
) -> str:
    if any(finding.classification in STRUCTURAL_RESOLUTION_FINDINGS for finding in findings):
        return RESOLUTION_AUDIT_BLOCKED_BY_CONTINUITY_GAP
    if any(record.findings for record in records):
        return RESOLUTION_AUDIT_STABLE_WITH_VISIBLE_FINDINGS
    return RESOLUTION_AUDIT_STABLE


def _summary(status: str, findings: tuple[OrchestrationPolicyResolutionFinding, ...]) -> str:
    if status == RESOLUTION_AUDIT_STABLE:
        return "Resolution audit is stable; no blocked compatibility relationships require resolution classification."
    if status == RESOLUTION_AUDIT_STABLE_WITH_VISIBLE_FINDINGS:
        return (
            "Resolution audit is stable with visible intentional block, future candidate, unsupported, dependency, "
            "governance, and evidence-gap classifications."
        )
    visible = tuple(sorted({f"{finding.resolution_id}:{finding.classification}" for finding in findings}))
    return f"Resolution audit classified as {status}; visible resolution entries: {', '.join(visible)}."


def _finding_sort_key(finding: OrchestrationPolicyResolutionFinding) -> tuple[str, str, str]:
    return (finding.resolution_id, finding.classification, finding.reason)
