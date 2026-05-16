"""Deterministic orchestration preflight evaluation."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_preflight_models import (
    PREFLIGHT_BLOCKER_DOMAIN_VISIBLE,
    PREFLIGHT_CLASSIFIED_AS_COMPATIBILITY_BLOCKED,
    PREFLIGHT_CLASSIFIED_AS_CONTINUITY_BLOCKED,
    PREFLIGHT_CLASSIFIED_AS_DEPENDENCY_BLOCKED,
    PREFLIGHT_CLASSIFIED_AS_EXPLAINABILITY_BLOCKED,
    PREFLIGHT_CLASSIFIED_AS_GOVERNANCE_BLOCKED,
    PREFLIGHT_CLASSIFIED_AS_PROHIBITED,
    PREFLIGHT_CLASSIFIED_AS_PROVENANCE_BLOCKED,
    PREFLIGHT_CLASSIFIED_AS_SUPPORTED,
    PREFLIGHT_CLASSIFIED_AS_UNSUPPORTED,
    PREFLIGHT_COMPATIBILITY_BLOCKED,
    PREFLIGHT_COMPATIBILITY_DOMAIN_VISIBLE,
    PREFLIGHT_CONTINUITY_BLOCKED,
    PREFLIGHT_CONTINUITY_GAP,
    PREFLIGHT_CONTINUITY_PRESERVED,
    PREFLIGHT_DEPENDENCY_BLOCKED,
    PREFLIGHT_DEPENDENCY_DOMAIN_VISIBLE,
    PREFLIGHT_EVALUATION_BLOCKED_BY_CONTINUITY_GAP,
    PREFLIGHT_EVALUATION_STABLE,
    PREFLIGHT_EVALUATION_STABLE_WITH_VISIBLE_FINDINGS,
    PREFLIGHT_EXPLAINABILITY_BLOCKED,
    PREFLIGHT_EXPLAINABILITY_GAP,
    PREFLIGHT_GOVERNANCE_BLOCKED,
    PREFLIGHT_GOVERNANCE_BOUNDARY_GAP,
    PREFLIGHT_GOVERNANCE_BOUNDARY_VISIBLE,
    PREFLIGHT_HASH_MISMATCH,
    PREFLIGHT_INTEGRITY_GAP,
    PREFLIGHT_POLICY_GAP,
    PREFLIGHT_POLICY_VISIBLE,
    PREFLIGHT_PROHIBITED,
    PREFLIGHT_PROHIBITED_DOMAIN_VISIBLE,
    PREFLIGHT_PROVENANCE_BLOCKED,
    PREFLIGHT_PROVENANCE_GAP,
    PREFLIGHT_STATES,
    PREFLIGHT_SUPPORTED,
    PREFLIGHT_SUPPORTED_DOMAIN_VISIBLE,
    PREFLIGHT_UNSUPPORTED,
    PREFLIGHT_UNSUPPORTED_DOMAIN_VISIBLE,
    OrchestrationPreflightEvaluationInput,
    OrchestrationPreflightEvaluationRecord,
    OrchestrationPreflightEvaluationResult,
    OrchestrationPreflightFinding,
    OrchestrationPreflightRecord,
    export_preflight_evaluation_result,
    hash_preflight_evaluation_result,
    hash_preflight_record,
    hash_preflight_registry,
    serialize_preflight_evaluation_result,
)
from .orchestration_preflight_registry import default_orchestration_preflight_registry


STRUCTURAL_PREFLIGHT_FINDINGS: frozenset[str] = frozenset(
    {
        PREFLIGHT_PROVENANCE_GAP,
        PREFLIGHT_EXPLAINABILITY_GAP,
        PREFLIGHT_INTEGRITY_GAP,
        PREFLIGHT_HASH_MISMATCH,
        PREFLIGHT_GOVERNANCE_BOUNDARY_GAP,
        PREFLIGHT_POLICY_GAP,
    }
)


def default_orchestration_preflight_evaluation_input() -> OrchestrationPreflightEvaluationInput:
    return OrchestrationPreflightEvaluationInput(preflight_registry=default_orchestration_preflight_registry())


def evaluate_orchestration_preflight(
    evaluation_input: OrchestrationPreflightEvaluationInput | None = None,
) -> OrchestrationPreflightEvaluationResult:
    source = evaluation_input or default_orchestration_preflight_evaluation_input()
    registry_hash = hash_preflight_registry(source.preflight_registry)
    records = tuple(_evaluate_record(record, source) for record in source.preflight_registry.records)
    findings = tuple(sorted((finding for record in records for finding in record.findings), key=_finding_sort_key))
    registry_hash_finding = _registry_hash_finding(source, registry_hash)
    if registry_hash_finding is not None:
        findings = tuple(sorted(findings + (registry_hash_finding,), key=_finding_sort_key))
    status = _evaluation_status(records, findings)
    result = OrchestrationPreflightEvaluationResult(
        registry_id=source.preflight_registry.registry_id,
        preflight_evaluation_status=status,
        planning_only=True,
        evaluation_records=records,
        registered_preflight_count=len(records),
        supported_preflight_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_SUPPORTED),
        unsupported_preflight_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_UNSUPPORTED),
        prohibited_preflight_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_PROHIBITED),
        governance_blocked_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_GOVERNANCE_BLOCKED),
        compatibility_blocked_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_COMPATIBILITY_BLOCKED),
        dependency_blocked_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_DEPENDENCY_BLOCKED),
        continuity_blocked_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_CONTINUITY_BLOCKED),
        provenance_blocked_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_PROVENANCE_BLOCKED),
        explainability_blocked_count=sum(1 for record in records if record.preflight_state == PREFLIGHT_EXPLAINABILITY_BLOCKED),
        policy_count=_unique_count(source.preflight_registry.records, "policy_ids"),
        governance_boundary_count=_unique_count(source.preflight_registry.records, "governance_boundaries"),
        compatibility_domain_count=_unique_count(source.preflight_registry.records, "compatibility_domains"),
        dependency_domain_count=_unique_count(source.preflight_registry.records, "dependency_domains"),
        blocker_domain_count=_unique_count(source.preflight_registry.records, "blocker_domains"),
        unsupported_domain_count=_unique_count(source.preflight_registry.records, "unsupported_domains"),
        prohibited_domain_count=_unique_count(source.preflight_registry.records, "prohibited_domains"),
        supported_domain_count=_unique_count(source.preflight_registry.records, "supported_domains"),
        provenance_continuity_status=_continuity_status(records, "provenance_continuity_state"),
        explainability_continuity_status=_continuity_status(records, "explainability_continuity_state"),
        integrity_continuity_status=_continuity_status(records, "integrity_continuity_state"),
        governance_continuity_status=_continuity_status(records, "governance_continuity_state"),
        finding_summary=findings,
        deterministic_registry_hash=registry_hash,
        deterministic_preflight_evaluation_hash="",
        deterministic_explanation_summary=_summary(status, findings),
    )
    return replace(result, deterministic_preflight_evaluation_hash=hash_preflight_evaluation_result(result))


def export_orchestration_preflight_evaluation_result(result: OrchestrationPreflightEvaluationResult) -> dict[str, object]:
    return export_preflight_evaluation_result(result)


def serialize_orchestration_preflight_evaluation_result(result: OrchestrationPreflightEvaluationResult) -> str:
    return serialize_preflight_evaluation_result(result)


def hash_orchestration_preflight_evaluation_result(result: OrchestrationPreflightEvaluationResult) -> str:
    return hash_preflight_evaluation_result(result)


def _evaluate_record(
    record: OrchestrationPreflightRecord,
    source: OrchestrationPreflightEvaluationInput,
) -> OrchestrationPreflightEvaluationRecord:
    preflight_hash = hash_preflight_record(record)
    findings = _preflight_findings(record)
    expected_hash = source.expected_preflight_hashes.get(record.identifier.preflight_id) if source.expected_preflight_hashes else None
    if expected_hash is not None and expected_hash != preflight_hash:
        findings.append(
            OrchestrationPreflightFinding(
                preflight_id=record.identifier.preflight_id,
                intent_id=record.identifier.intent_id,
                classification=PREFLIGHT_HASH_MISMATCH,
                reason="preflight record hash does not match expected deterministic hash",
                evidence_ids=(preflight_hash, expected_hash),
            )
        )
    provenance_continuity = PREFLIGHT_CONTINUITY_GAP if any(finding.classification == PREFLIGHT_PROVENANCE_GAP for finding in findings) else PREFLIGHT_CONTINUITY_PRESERVED
    explainability_continuity = PREFLIGHT_CONTINUITY_GAP if any(finding.classification == PREFLIGHT_EXPLAINABILITY_GAP for finding in findings) else PREFLIGHT_CONTINUITY_PRESERVED
    integrity_continuity = PREFLIGHT_CONTINUITY_GAP if any(finding.classification in (PREFLIGHT_INTEGRITY_GAP, PREFLIGHT_HASH_MISMATCH) for finding in findings) else PREFLIGHT_CONTINUITY_PRESERVED
    governance_continuity = PREFLIGHT_CONTINUITY_GAP if any(finding.classification == PREFLIGHT_GOVERNANCE_BOUNDARY_GAP for finding in findings) else PREFLIGHT_CONTINUITY_PRESERVED
    return OrchestrationPreflightEvaluationRecord(
        preflight_id=record.identifier.preflight_id,
        intent_id=record.identifier.intent_id,
        preflight_state=record.preflight_state,
        preflight_hash=preflight_hash,
        theoretically_supportable=record.theoretically_supportable,
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


def _preflight_findings(record: OrchestrationPreflightRecord) -> list[OrchestrationPreflightFinding]:
    findings = [_state_finding(record)]
    for classification, values, reason in (
        (PREFLIGHT_POLICY_VISIBLE, record.policy_ids, "applicable policy references are visible"),
        (PREFLIGHT_GOVERNANCE_BOUNDARY_VISIBLE, record.governance_boundaries, "governance boundaries are visible"),
        (PREFLIGHT_COMPATIBILITY_DOMAIN_VISIBLE, record.compatibility_domains, "compatibility domains are visible"),
        (PREFLIGHT_DEPENDENCY_DOMAIN_VISIBLE, record.dependency_domains, "dependency domains are visible"),
        (PREFLIGHT_BLOCKER_DOMAIN_VISIBLE, record.blocker_domains, "blocker domains are visible"),
        (PREFLIGHT_UNSUPPORTED_DOMAIN_VISIBLE, record.unsupported_domains, "unsupported domains are visible"),
        (PREFLIGHT_PROHIBITED_DOMAIN_VISIBLE, record.prohibited_domains, "prohibited domains are visible"),
        (PREFLIGHT_SUPPORTED_DOMAIN_VISIBLE, record.supported_domains, "supported domains are visible"),
    ):
        if values:
            findings.append(_finding(record, classification, reason, values))
    findings.extend(_continuity_findings(record))
    return findings


def _state_finding(record: OrchestrationPreflightRecord) -> OrchestrationPreflightFinding:
    state_map = {
        PREFLIGHT_SUPPORTED: (PREFLIGHT_CLASSIFIED_AS_SUPPORTED, "preflight state is theoretically supportable for planning-only analysis", record.supported_domains),
        PREFLIGHT_UNSUPPORTED: (PREFLIGHT_CLASSIFIED_AS_UNSUPPORTED, "preflight state is unsupported and remains fail-visible", record.unsupported_domains),
        PREFLIGHT_PROHIBITED: (PREFLIGHT_CLASSIFIED_AS_PROHIBITED, "preflight state is prohibited and remains fail-visible", record.prohibited_domains),
        PREFLIGHT_GOVERNANCE_BLOCKED: (PREFLIGHT_CLASSIFIED_AS_GOVERNANCE_BLOCKED, "preflight state is blocked by governance boundaries", record.governance_boundaries),
        PREFLIGHT_COMPATIBILITY_BLOCKED: (PREFLIGHT_CLASSIFIED_AS_COMPATIBILITY_BLOCKED, "preflight state is blocked by compatibility domains", record.compatibility_domains),
        PREFLIGHT_DEPENDENCY_BLOCKED: (PREFLIGHT_CLASSIFIED_AS_DEPENDENCY_BLOCKED, "preflight state is blocked by dependency domains", record.dependency_domains),
        PREFLIGHT_CONTINUITY_BLOCKED: (PREFLIGHT_CLASSIFIED_AS_CONTINUITY_BLOCKED, "preflight state is blocked by continuity gaps", record.provenance.governance_reference_ids),
        PREFLIGHT_PROVENANCE_BLOCKED: (PREFLIGHT_CLASSIFIED_AS_PROVENANCE_BLOCKED, "preflight state is blocked by provenance gaps", record.provenance.replay_reference_ids),
        PREFLIGHT_EXPLAINABILITY_BLOCKED: (PREFLIGHT_CLASSIFIED_AS_EXPLAINABILITY_BLOCKED, "preflight state is blocked by explainability gaps", record.explainability_reference_ids),
    }
    classification, reason, evidence = state_map.get(
        record.preflight_state,
        (PREFLIGHT_GOVERNANCE_BOUNDARY_GAP, "preflight state is not recognized", (record.preflight_state,)),
    )
    return _finding(record, classification, reason, evidence)


def _continuity_findings(record: OrchestrationPreflightRecord) -> list[OrchestrationPreflightFinding]:
    findings: list[OrchestrationPreflightFinding] = []
    missing_provenance = _missing_provenance(record)
    if missing_provenance:
        findings.append(_finding(record, PREFLIGHT_PROVENANCE_GAP, "preflight provenance continuity gap", missing_provenance))
    if not record.policy_ids:
        findings.append(_finding(record, PREFLIGHT_POLICY_GAP, "preflight has no applicable policy references", (record.identifier.preflight_id,)))
    if not record.explainability_reference_ids:
        findings.append(_finding(record, PREFLIGHT_EXPLAINABILITY_GAP, "preflight explainability reference is missing", (record.identifier.preflight_id,)))
    if not record.integrity_reference_ids:
        findings.append(_finding(record, PREFLIGHT_INTEGRITY_GAP, "preflight integrity reference is missing", (record.identifier.preflight_id,)))
    if _governance_boundary_gap(record):
        findings.append(_finding(record, PREFLIGHT_GOVERNANCE_BOUNDARY_GAP, "preflight governance boundary is not planning-only", (record.identifier.preflight_id,)))
    if record.preflight_state not in PREFLIGHT_STATES:
        findings.append(_finding(record, PREFLIGHT_GOVERNANCE_BOUNDARY_GAP, "preflight state is not recognized", (record.preflight_state,)))
    return findings


def _finding(
    record: OrchestrationPreflightRecord,
    classification: str,
    reason: str,
    evidence_ids: tuple[str, ...],
) -> OrchestrationPreflightFinding:
    return OrchestrationPreflightFinding(
        preflight_id=record.identifier.preflight_id,
        intent_id=record.identifier.intent_id,
        classification=classification,
        reason=reason,
        evidence_ids=tuple(sorted(evidence_ids)),
    )


def _missing_provenance(record: OrchestrationPreflightRecord) -> tuple[str, ...]:
    provenance = record.provenance
    missing: list[str] = []
    if not provenance.source_phase:
        missing.append("source_phase")
    if not provenance.source_artifact:
        missing.append("source_artifact")
    if not provenance.intent_id:
        missing.append("intent_id")
    if not provenance.mapping_id:
        missing.append("mapping_id")
    if not provenance.policy_ids:
        missing.append("policy_ids")
    if not provenance.replay_reference_ids:
        missing.append("replay_reference_ids")
    if not provenance.rollback_reference_ids:
        missing.append("rollback_reference_ids")
    if not provenance.governance_reference_ids:
        missing.append("governance_reference_ids")
    return tuple(sorted(missing))


def _governance_boundary_gap(record: OrchestrationPreflightRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "preflight_evaluation_only")
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
            record.preflight_execution_enabled,
        )
    )


def _registry_hash_finding(
    source: OrchestrationPreflightEvaluationInput,
    registry_hash: str,
) -> OrchestrationPreflightFinding | None:
    if source.expected_registry_hash is None or source.expected_registry_hash == registry_hash:
        return None
    return OrchestrationPreflightFinding(
        preflight_id=source.preflight_registry.registry_id,
        intent_id=source.preflight_registry.registry_id,
        classification=PREFLIGHT_HASH_MISMATCH,
        reason="preflight registry hash does not match expected deterministic hash",
        evidence_ids=(registry_hash, source.expected_registry_hash),
    )


def _unique_count(records: tuple[OrchestrationPreflightRecord, ...], field: str) -> int:
    return len({value for record in records for value in getattr(record, field)})


def _continuity_status(records: tuple[OrchestrationPreflightEvaluationRecord, ...], field: str) -> str:
    return PREFLIGHT_CONTINUITY_PRESERVED if all(getattr(record, field) == PREFLIGHT_CONTINUITY_PRESERVED for record in records) else PREFLIGHT_CONTINUITY_GAP


def _evaluation_status(
    records: tuple[OrchestrationPreflightEvaluationRecord, ...],
    findings: tuple[OrchestrationPreflightFinding, ...],
) -> str:
    if any(finding.classification in STRUCTURAL_PREFLIGHT_FINDINGS for finding in findings):
        return PREFLIGHT_EVALUATION_BLOCKED_BY_CONTINUITY_GAP
    if any(record.findings for record in records):
        return PREFLIGHT_EVALUATION_STABLE_WITH_VISIBLE_FINDINGS
    return PREFLIGHT_EVALUATION_STABLE


def _summary(status: str, findings: tuple[OrchestrationPreflightFinding, ...]) -> str:
    if status == PREFLIGHT_EVALUATION_STABLE:
        return "Preflight evaluation is stable; no preflight records require fail-visible classification."
    if status == PREFLIGHT_EVALUATION_STABLE_WITH_VISIBLE_FINDINGS:
        return (
            "Preflight evaluation is stable with visible theoretical supportability, governance, compatibility, "
            "dependency, blocker, supported, unsupported, prohibited, and continuity findings."
        )
    visible = tuple(sorted({f"{finding.preflight_id}:{finding.classification}" for finding in findings}))
    return f"Preflight evaluation is {status}; visible preflight entries: {', '.join(visible)}."


def _finding_sort_key(finding: OrchestrationPreflightFinding) -> tuple[str, str, str, str]:
    return (finding.preflight_id, finding.intent_id, finding.classification, finding.reason)
