"""Deterministic orchestration intent classification."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_intent_models import (
    INTENT_BLOCKER_DOMAIN_VISIBLE,
    INTENT_CLASSIFICATION_BLOCKED_BY_CONTINUITY_GAP,
    INTENT_CLASSIFICATION_STABLE,
    INTENT_CLASSIFICATION_STABLE_WITH_VISIBLE_FINDINGS,
    INTENT_CLASSIFIED_AS_PROHIBITED,
    INTENT_CLASSIFIED_AS_SUPPORTED,
    INTENT_CLASSIFIED_AS_TYPE,
    INTENT_CLASSIFIED_AS_UNSUPPORTED,
    INTENT_COMPATIBILITY_DOMAIN_VISIBLE,
    INTENT_CONTINUITY_GAP,
    INTENT_CONTINUITY_PRESERVED,
    INTENT_DEPENDENCY_DOMAIN_VISIBLE,
    INTENT_EXPLAINABILITY_GAP,
    INTENT_GOVERNANCE_BOUNDARY_GAP,
    INTENT_GOVERNANCE_BOUNDARY_VISIBLE,
    INTENT_HASH_MISMATCH,
    INTENT_INTEGRITY_GAP,
    INTENT_PROHIBITED,
    INTENT_PROHIBITED_DOMAIN_VISIBLE,
    INTENT_PROVENANCE_GAP,
    INTENT_SUPPORT_STATES,
    INTENT_SUPPORTED,
    INTENT_TYPES,
    INTENT_UNSUPPORTED,
    INTENT_UNSUPPORTED_DOMAIN_VISIBLE,
    OrchestrationIntentClassificationInput,
    OrchestrationIntentClassificationRecord,
    OrchestrationIntentClassificationResult,
    OrchestrationIntentFinding,
    OrchestrationIntentRecord,
    export_intent_classification_result,
    hash_intent_classification_result,
    hash_intent_record,
    hash_intent_registry,
    serialize_intent_classification_result,
)
from .orchestration_intent_registry import default_orchestration_intent_registry


STRUCTURAL_INTENT_FINDINGS: frozenset[str] = frozenset(
    {
        INTENT_PROVENANCE_GAP,
        INTENT_EXPLAINABILITY_GAP,
        INTENT_INTEGRITY_GAP,
        INTENT_HASH_MISMATCH,
        INTENT_GOVERNANCE_BOUNDARY_GAP,
    }
)


def default_orchestration_intent_classification_input() -> OrchestrationIntentClassificationInput:
    return OrchestrationIntentClassificationInput(
        intent_registry=default_orchestration_intent_registry()
    )


def classify_orchestration_intents(
    classification_input: OrchestrationIntentClassificationInput | None = None,
) -> OrchestrationIntentClassificationResult:
    source = classification_input or default_orchestration_intent_classification_input()
    registry_hash = hash_intent_registry(source.intent_registry)
    records = tuple(_classify_record(record, source) for record in source.intent_registry.records)
    findings = tuple(sorted((finding for record in records for finding in record.findings), key=_finding_sort_key))
    registry_hash_finding = _registry_hash_finding(source, registry_hash)
    if registry_hash_finding is not None:
        findings = tuple(sorted(findings + (registry_hash_finding,), key=_finding_sort_key))
    status = _classification_status(records, findings)
    result = OrchestrationIntentClassificationResult(
        registry_id=source.intent_registry.registry_id,
        intent_classification_status=status,
        planning_only=True,
        classification_records=records,
        registered_intent_count=len(records),
        supported_intent_count=sum(1 for record in records if record.support_state == INTENT_SUPPORTED),
        unsupported_intent_count=sum(1 for record in records if record.support_state == INTENT_UNSUPPORTED),
        prohibited_intent_count=sum(1 for record in records if record.support_state == INTENT_PROHIBITED),
        governance_boundary_count=_unique_count(source.intent_registry.records, "governance_boundaries"),
        compatibility_domain_count=_unique_count(source.intent_registry.records, "compatibility_domains"),
        dependency_domain_count=_unique_count(source.intent_registry.records, "dependency_domains"),
        blocker_domain_count=_unique_count(source.intent_registry.records, "blocker_domains"),
        unsupported_domain_count=_unique_count(source.intent_registry.records, "unsupported_domains"),
        prohibited_domain_count=_unique_count(source.intent_registry.records, "prohibited_domains"),
        supported_domain_count=_unique_count(source.intent_registry.records, "supported_domains"),
        provenance_continuity_status=_continuity_status(records, "provenance_continuity_state"),
        explainability_continuity_status=_continuity_status(records, "explainability_continuity_state"),
        integrity_continuity_status=_continuity_status(records, "integrity_continuity_state"),
        governance_continuity_status=_continuity_status(records, "governance_continuity_state"),
        finding_summary=findings,
        deterministic_registry_hash=registry_hash,
        deterministic_intent_classification_hash="",
        deterministic_explanation_summary=_summary(status, findings),
    )
    return replace(result, deterministic_intent_classification_hash=hash_intent_classification_result(result))


def export_orchestration_intent_classification_result(
    result: OrchestrationIntentClassificationResult,
) -> dict[str, object]:
    return export_intent_classification_result(result)


def serialize_orchestration_intent_classification_result(
    result: OrchestrationIntentClassificationResult,
) -> str:
    return serialize_intent_classification_result(result)


def hash_orchestration_intent_classification_result(
    result: OrchestrationIntentClassificationResult,
) -> str:
    return hash_intent_classification_result(result)


def _classify_record(
    record: OrchestrationIntentRecord,
    source: OrchestrationIntentClassificationInput,
) -> OrchestrationIntentClassificationRecord:
    intent_hash = hash_intent_record(record)
    findings = _intent_findings(record)
    expected_hash = source.expected_intent_hashes.get(record.identifier.intent_id) if source.expected_intent_hashes else None
    if expected_hash is not None and expected_hash != intent_hash:
        findings.append(
            OrchestrationIntentFinding(
                intent_id=record.identifier.intent_id,
                classification=INTENT_HASH_MISMATCH,
                reason="intent record hash does not match expected deterministic hash",
                evidence_ids=(intent_hash, expected_hash),
            )
        )
    provenance_continuity = INTENT_CONTINUITY_GAP if any(finding.classification == INTENT_PROVENANCE_GAP for finding in findings) else INTENT_CONTINUITY_PRESERVED
    explainability_continuity = INTENT_CONTINUITY_GAP if any(finding.classification == INTENT_EXPLAINABILITY_GAP for finding in findings) else INTENT_CONTINUITY_PRESERVED
    integrity_continuity = INTENT_CONTINUITY_GAP if any(finding.classification in (INTENT_INTEGRITY_GAP, INTENT_HASH_MISMATCH) for finding in findings) else INTENT_CONTINUITY_PRESERVED
    governance_continuity = INTENT_CONTINUITY_GAP if any(finding.classification == INTENT_GOVERNANCE_BOUNDARY_GAP for finding in findings) else INTENT_CONTINUITY_PRESERVED
    return OrchestrationIntentClassificationRecord(
        intent_id=record.identifier.intent_id,
        intent_type=record.intent_type,
        support_state=record.support_state,
        intent_hash=intent_hash,
        governance_boundary_count=len(record.governance_boundaries),
        compatibility_domain_count=len(record.compatibility_domains),
        dependency_domain_count=len(record.dependency_domains),
        blocker_domain_count=len(record.blocker_domains),
        unsupported_domain_count=len(record.unsupported_domains),
        prohibited_domain_count=len(record.prohibited_domains),
        supported_domain_count=len(record.supported_domains),
        provenance_continuity_state=provenance_continuity,
        explainability_continuity_state=explainability_continuity,
        integrity_continuity_state=integrity_continuity,
        governance_continuity_state=governance_continuity,
        findings=tuple(sorted(findings, key=_finding_sort_key)),
    )


def _intent_findings(record: OrchestrationIntentRecord) -> list[OrchestrationIntentFinding]:
    findings = [
        OrchestrationIntentFinding(
            intent_id=record.identifier.intent_id,
            classification=INTENT_CLASSIFIED_AS_TYPE,
            reason="intent type is deterministically classified",
            evidence_ids=(record.intent_type,),
        )
    ]
    if record.support_state == INTENT_SUPPORTED:
        findings.append(_finding(record, INTENT_CLASSIFIED_AS_SUPPORTED, "intent is supported for planning-only modeling", record.supported_domains))
    elif record.support_state == INTENT_UNSUPPORTED:
        findings.append(_finding(record, INTENT_CLASSIFIED_AS_UNSUPPORTED, "intent is unsupported and remains fail-visible", record.unsupported_domains))
    elif record.support_state == INTENT_PROHIBITED:
        findings.append(_finding(record, INTENT_CLASSIFIED_AS_PROHIBITED, "intent is prohibited and remains fail-visible", record.prohibited_domains))
    else:
        findings.append(_finding(record, INTENT_GOVERNANCE_BOUNDARY_GAP, "intent support state is not recognized", (record.support_state,)))
    for classification, values, reason in (
        (INTENT_GOVERNANCE_BOUNDARY_VISIBLE, record.governance_boundaries, "governance boundaries are visible"),
        (INTENT_COMPATIBILITY_DOMAIN_VISIBLE, record.compatibility_domains, "compatibility domains are visible"),
        (INTENT_DEPENDENCY_DOMAIN_VISIBLE, record.dependency_domains, "dependency domains are visible"),
        (INTENT_BLOCKER_DOMAIN_VISIBLE, record.blocker_domains, "blocker domains are visible"),
        (INTENT_UNSUPPORTED_DOMAIN_VISIBLE, record.unsupported_domains, "unsupported domains are visible"),
        (INTENT_PROHIBITED_DOMAIN_VISIBLE, record.prohibited_domains, "prohibited domains are visible"),
    ):
        if values:
            findings.append(_finding(record, classification, reason, values))
    findings.extend(_continuity_findings(record))
    return findings


def _continuity_findings(record: OrchestrationIntentRecord) -> list[OrchestrationIntentFinding]:
    findings: list[OrchestrationIntentFinding] = []
    missing_provenance = _missing_provenance(record)
    if missing_provenance:
        findings.append(_finding(record, INTENT_PROVENANCE_GAP, "intent provenance continuity gap", missing_provenance))
    if not record.explainability_reference_ids:
        findings.append(_finding(record, INTENT_EXPLAINABILITY_GAP, "intent explainability reference is missing", (record.identifier.intent_id,)))
    if not record.integrity_reference_ids:
        findings.append(_finding(record, INTENT_INTEGRITY_GAP, "intent integrity reference is missing", (record.identifier.intent_id,)))
    if _governance_boundary_gap(record):
        findings.append(_finding(record, INTENT_GOVERNANCE_BOUNDARY_GAP, "intent governance boundary is not planning-only", (record.identifier.intent_id,)))
    if record.intent_type not in INTENT_TYPES:
        findings.append(_finding(record, INTENT_GOVERNANCE_BOUNDARY_GAP, "intent type is not recognized", (record.intent_type,)))
    if record.support_state not in INTENT_SUPPORT_STATES:
        findings.append(_finding(record, INTENT_GOVERNANCE_BOUNDARY_GAP, "intent support state is not recognized", (record.support_state,)))
    return findings


def _finding(
    record: OrchestrationIntentRecord,
    classification: str,
    reason: str,
    evidence_ids: tuple[str, ...],
) -> OrchestrationIntentFinding:
    return OrchestrationIntentFinding(
        intent_id=record.identifier.intent_id,
        classification=classification,
        reason=reason,
        evidence_ids=tuple(sorted(evidence_ids)),
    )


def _missing_provenance(record: OrchestrationIntentRecord) -> tuple[str, ...]:
    provenance = record.provenance
    missing: list[str] = []
    if not provenance.source_phase:
        missing.append("source_phase")
    if not provenance.source_artifact:
        missing.append("source_artifact")
    if not provenance.replay_reference_ids:
        missing.append("replay_reference_ids")
    if not provenance.rollback_reference_ids:
        missing.append("rollback_reference_ids")
    if not provenance.governance_reference_ids:
        missing.append("governance_reference_ids")
    return tuple(sorted(missing))


def _governance_boundary_gap(record: OrchestrationIntentRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "intent_modeling_only")
    required_false = (
        "execution_enabled",
        "routing_enabled",
        "mutation_enabled",
        "recommendation_enabled",
        "optimization_enabled",
        "autonomy_enabled",
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
            record.runtime_execution_enabled,
            record.orchestration_execution_enabled,
            record.routing_behavior_enabled,
            record.mutation_behavior_enabled,
            record.production_consumption_enabled,
            record.background_processing_enabled,
            record.recommendation_behavior_enabled,
            record.optimization_behavior_enabled,
            record.autonomous_behavior_enabled,
            record.graph_execution_enabled,
        )
    )


def _registry_hash_finding(
    source: OrchestrationIntentClassificationInput,
    registry_hash: str,
) -> OrchestrationIntentFinding | None:
    if source.expected_registry_hash is None or source.expected_registry_hash == registry_hash:
        return None
    return OrchestrationIntentFinding(
        intent_id=source.intent_registry.registry_id,
        classification=INTENT_HASH_MISMATCH,
        reason="intent registry hash does not match expected deterministic hash",
        evidence_ids=(registry_hash, source.expected_registry_hash),
    )


def _unique_count(records: tuple[OrchestrationIntentRecord, ...], field: str) -> int:
    return len({value for record in records for value in getattr(record, field)})


def _continuity_status(records: tuple[OrchestrationIntentClassificationRecord, ...], field: str) -> str:
    return INTENT_CONTINUITY_PRESERVED if all(getattr(record, field) == INTENT_CONTINUITY_PRESERVED for record in records) else INTENT_CONTINUITY_GAP


def _classification_status(
    records: tuple[OrchestrationIntentClassificationRecord, ...],
    findings: tuple[OrchestrationIntentFinding, ...],
) -> str:
    if any(finding.classification in STRUCTURAL_INTENT_FINDINGS for finding in findings):
        return INTENT_CLASSIFICATION_BLOCKED_BY_CONTINUITY_GAP
    if any(record.findings for record in records):
        return INTENT_CLASSIFICATION_STABLE_WITH_VISIBLE_FINDINGS
    return INTENT_CLASSIFICATION_STABLE


def _summary(status: str, findings: tuple[OrchestrationIntentFinding, ...]) -> str:
    if status == INTENT_CLASSIFICATION_STABLE:
        return "Intent classification is stable; no intent records require fail-visible classification."
    if status == INTENT_CLASSIFICATION_STABLE_WITH_VISIBLE_FINDINGS:
        return (
            "Intent classification is stable with visible supported, unsupported, prohibited, governance, "
            "compatibility, dependency, and blocker-domain findings."
        )
    visible = tuple(sorted({f"{finding.intent_id}:{finding.classification}" for finding in findings}))
    return f"Intent classification is {status}; visible intent entries: {', '.join(visible)}."


def _finding_sort_key(finding: OrchestrationIntentFinding) -> tuple[str, str, str]:
    return (finding.intent_id, finding.classification, finding.reason)
