"""Deterministic orchestration intent-policy mapping analysis."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_intent_policy_mapping_models import (
    MAPPING_ANALYSIS_BLOCKED_BY_CONTINUITY_GAP,
    MAPPING_ANALYSIS_STABLE,
    MAPPING_ANALYSIS_STABLE_WITH_VISIBLE_FINDINGS,
    MAPPING_BLOCKER_DOMAIN_VISIBLE,
    MAPPING_CLASSIFIED_AS_PROHIBITED,
    MAPPING_CLASSIFIED_AS_SUPPORTED,
    MAPPING_CLASSIFIED_AS_UNSUPPORTED,
    MAPPING_COMPATIBILITY_DOMAIN_VISIBLE,
    MAPPING_CONTINUITY_GAP,
    MAPPING_CONTINUITY_PRESERVED,
    MAPPING_DEPENDENCY_DOMAIN_VISIBLE,
    MAPPING_EXPLAINABILITY_GAP,
    MAPPING_GOVERNANCE_BOUNDARY_GAP,
    MAPPING_GOVERNANCE_BOUNDARY_VISIBLE,
    MAPPING_HASH_MISMATCH,
    MAPPING_INTEGRITY_GAP,
    MAPPING_POLICY_APPLICABILITY_GAP,
    MAPPING_POLICY_APPLICABILITY_VISIBLE,
    MAPPING_PROHIBITED,
    MAPPING_PROHIBITED_DOMAIN_VISIBLE,
    MAPPING_PROVENANCE_GAP,
    MAPPING_SUPPORT_STATES,
    MAPPING_SUPPORTED,
    MAPPING_SUPPORTED_DOMAIN_VISIBLE,
    MAPPING_UNSUPPORTED,
    MAPPING_UNSUPPORTED_DOMAIN_VISIBLE,
    OrchestrationIntentPolicyMappingAnalysisRecord,
    OrchestrationIntentPolicyMappingFinding,
    OrchestrationIntentPolicyMappingInput,
    OrchestrationIntentPolicyMappingRecord,
    OrchestrationIntentPolicyMappingResult,
    export_mapping_result,
    hash_mapping_record,
    hash_mapping_registry,
    hash_mapping_result,
    serialize_mapping_result,
)
from .orchestration_intent_policy_mapping_registry import default_orchestration_intent_policy_mapping_registry


STRUCTURAL_MAPPING_FINDINGS: frozenset[str] = frozenset(
    {
        MAPPING_PROVENANCE_GAP,
        MAPPING_EXPLAINABILITY_GAP,
        MAPPING_INTEGRITY_GAP,
        MAPPING_HASH_MISMATCH,
        MAPPING_GOVERNANCE_BOUNDARY_GAP,
        MAPPING_POLICY_APPLICABILITY_GAP,
    }
)


def default_orchestration_intent_policy_mapping_input() -> OrchestrationIntentPolicyMappingInput:
    return OrchestrationIntentPolicyMappingInput(
        mapping_registry=default_orchestration_intent_policy_mapping_registry()
    )


def map_orchestration_intent_policies(
    mapping_input: OrchestrationIntentPolicyMappingInput | None = None,
) -> OrchestrationIntentPolicyMappingResult:
    source = mapping_input or default_orchestration_intent_policy_mapping_input()
    registry_hash = hash_mapping_registry(source.mapping_registry)
    records = tuple(_map_record(record, source) for record in source.mapping_registry.records)
    findings = tuple(sorted((finding for record in records for finding in record.findings), key=_finding_sort_key))
    registry_hash_finding = _registry_hash_finding(source, registry_hash)
    if registry_hash_finding is not None:
        findings = tuple(sorted(findings + (registry_hash_finding,), key=_finding_sort_key))
    status = _analysis_status(records, findings)
    result = OrchestrationIntentPolicyMappingResult(
        registry_id=source.mapping_registry.registry_id,
        mapping_analysis_status=status,
        planning_only=True,
        analysis_records=records,
        registered_mapping_count=len(records),
        supported_mapping_count=sum(1 for record in records if record.mapping_state == MAPPING_SUPPORTED),
        unsupported_mapping_count=sum(1 for record in records if record.mapping_state == MAPPING_UNSUPPORTED),
        prohibited_mapping_count=sum(1 for record in records if record.mapping_state == MAPPING_PROHIBITED),
        policy_count=_unique_count(source.mapping_registry.records, "policy_ids"),
        governance_boundary_count=_unique_count(source.mapping_registry.records, "governance_boundaries"),
        compatibility_domain_count=_unique_count(source.mapping_registry.records, "compatibility_domains"),
        dependency_domain_count=_unique_count(source.mapping_registry.records, "dependency_domains"),
        blocker_domain_count=_unique_count(source.mapping_registry.records, "blocker_domains"),
        unsupported_domain_count=_unique_count(source.mapping_registry.records, "unsupported_domains"),
        prohibited_domain_count=_unique_count(source.mapping_registry.records, "prohibited_domains"),
        supported_domain_count=_unique_count(source.mapping_registry.records, "supported_domains"),
        provenance_continuity_status=_continuity_status(records, "provenance_continuity_state"),
        explainability_continuity_status=_continuity_status(records, "explainability_continuity_state"),
        integrity_continuity_status=_continuity_status(records, "integrity_continuity_state"),
        governance_continuity_status=_continuity_status(records, "governance_continuity_state"),
        finding_summary=findings,
        deterministic_registry_hash=registry_hash,
        deterministic_mapping_analysis_hash="",
        deterministic_explanation_summary=_summary(status, findings),
    )
    return replace(result, deterministic_mapping_analysis_hash=hash_mapping_result(result))


def export_orchestration_intent_policy_mapping_result(
    result: OrchestrationIntentPolicyMappingResult,
) -> dict[str, object]:
    return export_mapping_result(result)


def serialize_orchestration_intent_policy_mapping_result(
    result: OrchestrationIntentPolicyMappingResult,
) -> str:
    return serialize_mapping_result(result)


def hash_orchestration_intent_policy_mapping_result(
    result: OrchestrationIntentPolicyMappingResult,
) -> str:
    return hash_mapping_result(result)


def _map_record(
    record: OrchestrationIntentPolicyMappingRecord,
    source: OrchestrationIntentPolicyMappingInput,
) -> OrchestrationIntentPolicyMappingAnalysisRecord:
    mapping_hash = hash_mapping_record(record)
    findings = _mapping_findings(record)
    expected_hash = source.expected_mapping_hashes.get(record.identifier.mapping_id) if source.expected_mapping_hashes else None
    if expected_hash is not None and expected_hash != mapping_hash:
        findings.append(
            OrchestrationIntentPolicyMappingFinding(
                mapping_id=record.identifier.mapping_id,
                intent_id=record.identifier.intent_id,
                classification=MAPPING_HASH_MISMATCH,
                reason="intent-policy mapping hash does not match expected deterministic hash",
                evidence_ids=(mapping_hash, expected_hash),
            )
        )
    provenance_continuity = MAPPING_CONTINUITY_GAP if any(finding.classification == MAPPING_PROVENANCE_GAP for finding in findings) else MAPPING_CONTINUITY_PRESERVED
    explainability_continuity = MAPPING_CONTINUITY_GAP if any(finding.classification == MAPPING_EXPLAINABILITY_GAP for finding in findings) else MAPPING_CONTINUITY_PRESERVED
    integrity_continuity = MAPPING_CONTINUITY_GAP if any(finding.classification in (MAPPING_INTEGRITY_GAP, MAPPING_HASH_MISMATCH) for finding in findings) else MAPPING_CONTINUITY_PRESERVED
    governance_continuity = MAPPING_CONTINUITY_GAP if any(finding.classification == MAPPING_GOVERNANCE_BOUNDARY_GAP for finding in findings) else MAPPING_CONTINUITY_PRESERVED
    return OrchestrationIntentPolicyMappingAnalysisRecord(
        mapping_id=record.identifier.mapping_id,
        intent_id=record.identifier.intent_id,
        mapping_state=record.mapping_state,
        mapping_hash=mapping_hash,
        policy_count=len(record.policy_ids),
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


def _mapping_findings(record: OrchestrationIntentPolicyMappingRecord) -> list[OrchestrationIntentPolicyMappingFinding]:
    findings: list[OrchestrationIntentPolicyMappingFinding] = []
    if record.mapping_state == MAPPING_SUPPORTED:
        findings.append(_finding(record, MAPPING_CLASSIFIED_AS_SUPPORTED, "mapping is supported for planning-only policy applicability", record.supported_domains))
    elif record.mapping_state == MAPPING_UNSUPPORTED:
        findings.append(_finding(record, MAPPING_CLASSIFIED_AS_UNSUPPORTED, "mapping is unsupported and remains fail-visible", record.unsupported_domains))
    elif record.mapping_state == MAPPING_PROHIBITED:
        findings.append(_finding(record, MAPPING_CLASSIFIED_AS_PROHIBITED, "mapping is prohibited and remains fail-visible", record.prohibited_domains))
    else:
        findings.append(_finding(record, MAPPING_GOVERNANCE_BOUNDARY_GAP, "mapping support state is not recognized", (record.mapping_state,)))
    for classification, values, reason in (
        (MAPPING_POLICY_APPLICABILITY_VISIBLE, record.policy_ids, "applicable policies are visible"),
        (MAPPING_GOVERNANCE_BOUNDARY_VISIBLE, record.governance_boundaries, "governance boundaries are visible"),
        (MAPPING_COMPATIBILITY_DOMAIN_VISIBLE, record.compatibility_domains, "compatibility domains are visible"),
        (MAPPING_DEPENDENCY_DOMAIN_VISIBLE, record.dependency_domains, "dependency domains are visible"),
        (MAPPING_BLOCKER_DOMAIN_VISIBLE, record.blocker_domains, "blocker domains are visible"),
        (MAPPING_UNSUPPORTED_DOMAIN_VISIBLE, record.unsupported_domains, "unsupported domains are visible"),
        (MAPPING_PROHIBITED_DOMAIN_VISIBLE, record.prohibited_domains, "prohibited domains are visible"),
        (MAPPING_SUPPORTED_DOMAIN_VISIBLE, record.supported_domains, "supported domains are visible"),
    ):
        if values:
            findings.append(_finding(record, classification, reason, values))
    findings.extend(_continuity_findings(record))
    return findings


def _continuity_findings(record: OrchestrationIntentPolicyMappingRecord) -> list[OrchestrationIntentPolicyMappingFinding]:
    findings: list[OrchestrationIntentPolicyMappingFinding] = []
    missing_provenance = _missing_provenance(record)
    if missing_provenance:
        findings.append(_finding(record, MAPPING_PROVENANCE_GAP, "intent-policy mapping provenance continuity gap", missing_provenance))
    if not record.policy_ids:
        findings.append(_finding(record, MAPPING_POLICY_APPLICABILITY_GAP, "intent-policy mapping has no applicable policies", (record.identifier.mapping_id,)))
    if not record.explainability_reference_ids:
        findings.append(_finding(record, MAPPING_EXPLAINABILITY_GAP, "intent-policy mapping explainability reference is missing", (record.identifier.mapping_id,)))
    if not record.integrity_reference_ids:
        findings.append(_finding(record, MAPPING_INTEGRITY_GAP, "intent-policy mapping integrity reference is missing", (record.identifier.mapping_id,)))
    if _governance_boundary_gap(record):
        findings.append(_finding(record, MAPPING_GOVERNANCE_BOUNDARY_GAP, "intent-policy mapping governance boundary is not planning-only", (record.identifier.mapping_id,)))
    if record.mapping_state not in MAPPING_SUPPORT_STATES:
        findings.append(_finding(record, MAPPING_GOVERNANCE_BOUNDARY_GAP, "intent-policy mapping support state is not recognized", (record.mapping_state,)))
    return findings


def _finding(
    record: OrchestrationIntentPolicyMappingRecord,
    classification: str,
    reason: str,
    evidence_ids: tuple[str, ...],
) -> OrchestrationIntentPolicyMappingFinding:
    return OrchestrationIntentPolicyMappingFinding(
        mapping_id=record.identifier.mapping_id,
        intent_id=record.identifier.intent_id,
        classification=classification,
        reason=reason,
        evidence_ids=tuple(sorted(evidence_ids)),
    )


def _missing_provenance(record: OrchestrationIntentPolicyMappingRecord) -> tuple[str, ...]:
    provenance = record.provenance
    missing: list[str] = []
    if not provenance.source_phase:
        missing.append("source_phase")
    if not provenance.source_artifact:
        missing.append("source_artifact")
    if not provenance.intent_id:
        missing.append("intent_id")
    if not provenance.policy_ids:
        missing.append("policy_ids")
    if not provenance.replay_reference_ids:
        missing.append("replay_reference_ids")
    if not provenance.rollback_reference_ids:
        missing.append("rollback_reference_ids")
    if not provenance.governance_reference_ids:
        missing.append("governance_reference_ids")
    return tuple(sorted(missing))


def _governance_boundary_gap(record: OrchestrationIntentPolicyMappingRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "intent_policy_mapping_only")
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
            record.mapping_execution_enabled,
        )
    )


def _registry_hash_finding(
    source: OrchestrationIntentPolicyMappingInput,
    registry_hash: str,
) -> OrchestrationIntentPolicyMappingFinding | None:
    if source.expected_registry_hash is None or source.expected_registry_hash == registry_hash:
        return None
    return OrchestrationIntentPolicyMappingFinding(
        mapping_id=source.mapping_registry.registry_id,
        intent_id=source.mapping_registry.registry_id,
        classification=MAPPING_HASH_MISMATCH,
        reason="intent-policy mapping registry hash does not match expected deterministic hash",
        evidence_ids=(registry_hash, source.expected_registry_hash),
    )


def _unique_count(records: tuple[OrchestrationIntentPolicyMappingRecord, ...], field: str) -> int:
    return len({value for record in records for value in getattr(record, field)})


def _continuity_status(records: tuple[OrchestrationIntentPolicyMappingAnalysisRecord, ...], field: str) -> str:
    return MAPPING_CONTINUITY_PRESERVED if all(getattr(record, field) == MAPPING_CONTINUITY_PRESERVED for record in records) else MAPPING_CONTINUITY_GAP


def _analysis_status(
    records: tuple[OrchestrationIntentPolicyMappingAnalysisRecord, ...],
    findings: tuple[OrchestrationIntentPolicyMappingFinding, ...],
) -> str:
    if any(finding.classification in STRUCTURAL_MAPPING_FINDINGS for finding in findings):
        return MAPPING_ANALYSIS_BLOCKED_BY_CONTINUITY_GAP
    if any(record.findings for record in records):
        return MAPPING_ANALYSIS_STABLE_WITH_VISIBLE_FINDINGS
    return MAPPING_ANALYSIS_STABLE


def _summary(status: str, findings: tuple[OrchestrationIntentPolicyMappingFinding, ...]) -> str:
    if status == MAPPING_ANALYSIS_STABLE:
        return "Intent-policy mapping analysis is stable; no mappings require fail-visible classification."
    if status == MAPPING_ANALYSIS_STABLE_WITH_VISIBLE_FINDINGS:
        return (
            "Intent-policy mapping analysis is stable with visible policy applicability, governance, compatibility, "
            "dependency, blocker, supported, unsupported, and prohibited-domain findings."
        )
    visible = tuple(sorted({f"{finding.mapping_id}:{finding.classification}" for finding in findings}))
    return f"Intent-policy mapping analysis is {status}; visible mapping entries: {', '.join(visible)}."


def _finding_sort_key(finding: OrchestrationIntentPolicyMappingFinding) -> tuple[str, str, str, str]:
    return (finding.mapping_id, finding.intent_id, finding.classification, finding.reason)
