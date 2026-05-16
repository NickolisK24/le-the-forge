"""Deterministic orchestration evaluation trace building."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_trace_models import (
    TRACE_BLOCKER_DOMAIN_VISIBLE,
    TRACE_BUILD_BLOCKED_BY_CONTINUITY_GAP,
    TRACE_BUILD_STABLE,
    TRACE_BUILD_STABLE_WITH_VISIBLE_FINDINGS,
    TRACE_CLASSIFIED_AS_COMPATIBILITY_BLOCKED,
    TRACE_CLASSIFIED_AS_DEPENDENCY_BLOCKED,
    TRACE_CLASSIFIED_AS_GOVERNANCE_BLOCKED,
    TRACE_CLASSIFIED_AS_PROHIBITED,
    TRACE_CLASSIFIED_AS_SUPPORTED,
    TRACE_CLASSIFIED_AS_UNSUPPORTED,
    TRACE_COMPATIBILITY_BLOCKED,
    TRACE_COMPATIBILITY_DOMAIN_VISIBLE,
    TRACE_CONTINUITY_GAP,
    TRACE_CONTINUITY_PRESERVED,
    TRACE_DEPENDENCY_BLOCKED,
    TRACE_DEPENDENCY_DOMAIN_VISIBLE,
    TRACE_EXPLAINABILITY_GAP,
    TRACE_GOVERNANCE_BLOCKED,
    TRACE_GOVERNANCE_BOUNDARY_GAP,
    TRACE_GOVERNANCE_BOUNDARY_VISIBLE,
    TRACE_HASH_MISMATCH,
    TRACE_INTEGRITY_GAP,
    TRACE_POLICY_GAP,
    TRACE_POLICY_VISIBLE,
    TRACE_PROHIBITED,
    TRACE_PROHIBITED_DOMAIN_VISIBLE,
    TRACE_PROVENANCE_GAP,
    TRACE_REASONING_CHAIN_VISIBLE,
    TRACE_STEP_BLOCKER,
    TRACE_STEP_COMPATIBILITY,
    TRACE_STEP_DEPENDENCY,
    TRACE_STEP_EXPLAINABILITY,
    TRACE_STEP_GOVERNANCE,
    TRACE_STEP_GAP,
    TRACE_STEP_INTEGRITY,
    TRACE_STEP_PROHIBITED_DOMAIN,
    TRACE_STEP_PROVENANCE,
    TRACE_STEP_TYPES,
    TRACE_STEP_UNSUPPORTED_DOMAIN,
    TRACE_STEP_VISIBLE,
    TRACE_SUPPORTED,
    TRACE_SUPPORTED_DOMAIN_VISIBLE,
    TRACE_UNSUPPORTED,
    TRACE_UNSUPPORTED_DOMAIN_VISIBLE,
    OrchestrationEvaluationTraceBuildInput,
    OrchestrationEvaluationTraceBuildRecord,
    OrchestrationEvaluationTraceBuildResult,
    OrchestrationEvaluationTraceFinding,
    OrchestrationEvaluationTraceRecord,
    export_trace_build_result,
    hash_trace_build_result,
    hash_trace_record,
    hash_trace_registry,
    serialize_trace_build_result,
)
from .orchestration_evaluation_trace_registry import default_orchestration_evaluation_trace_registry


STRUCTURAL_TRACE_FINDINGS: frozenset[str] = frozenset(
    {
        TRACE_PROVENANCE_GAP,
        TRACE_EXPLAINABILITY_GAP,
        TRACE_INTEGRITY_GAP,
        TRACE_HASH_MISMATCH,
        TRACE_GOVERNANCE_BOUNDARY_GAP,
        TRACE_STEP_GAP,
        TRACE_POLICY_GAP,
    }
)


def default_orchestration_evaluation_trace_build_input() -> OrchestrationEvaluationTraceBuildInput:
    return OrchestrationEvaluationTraceBuildInput(
        trace_registry=default_orchestration_evaluation_trace_registry()
    )


def build_orchestration_evaluation_trace(
    build_input: OrchestrationEvaluationTraceBuildInput | None = None,
) -> OrchestrationEvaluationTraceBuildResult:
    source = build_input or default_orchestration_evaluation_trace_build_input()
    registry_hash = hash_trace_registry(source.trace_registry)
    records = tuple(_build_record(record, source) for record in source.trace_registry.records)
    findings = tuple(sorted((finding for record in records for finding in record.findings), key=_finding_sort_key))
    registry_hash_finding = _registry_hash_finding(source, registry_hash)
    if registry_hash_finding is not None:
        findings = tuple(sorted(findings + (registry_hash_finding,), key=_finding_sort_key))
    status = _build_status(records, findings)
    result = OrchestrationEvaluationTraceBuildResult(
        registry_id=source.trace_registry.registry_id,
        trace_build_status=status,
        planning_only=True,
        build_records=records,
        registered_trace_count=len(records),
        governance_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_GOVERNANCE),
        compatibility_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_COMPATIBILITY),
        dependency_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_DEPENDENCY),
        blocker_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_BLOCKER),
        unsupported_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_UNSUPPORTED_DOMAIN),
        prohibited_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_PROHIBITED_DOMAIN),
        provenance_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_PROVENANCE),
        explainability_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_EXPLAINABILITY),
        integrity_trace_count=_trace_count(source.trace_registry.records, TRACE_STEP_INTEGRITY),
        trace_step_count=sum(len(record.trace_steps) for record in source.trace_registry.records),
        reasoning_step_count=sum(len(record.reasoning_chain) for record in source.trace_registry.records),
        provenance_continuity_status=_continuity_status(records, "provenance_continuity_state"),
        explainability_continuity_status=_continuity_status(records, "explainability_continuity_state"),
        integrity_continuity_status=_continuity_status(records, "integrity_continuity_state"),
        governance_continuity_status=_continuity_status(records, "governance_continuity_state"),
        finding_summary=findings,
        deterministic_registry_hash=registry_hash,
        deterministic_trace_build_hash="",
        deterministic_explanation_summary=_summary(status, findings),
    )
    return replace(result, deterministic_trace_build_hash=hash_trace_build_result(result))


def build_orchestration_evaluation_traces(
    build_input: OrchestrationEvaluationTraceBuildInput | None = None,
) -> OrchestrationEvaluationTraceBuildResult:
    return build_orchestration_evaluation_trace(build_input)


def export_orchestration_evaluation_trace_build_result(result: OrchestrationEvaluationTraceBuildResult) -> dict[str, object]:
    return export_trace_build_result(result)


def serialize_orchestration_evaluation_trace_build_result(result: OrchestrationEvaluationTraceBuildResult) -> str:
    return serialize_trace_build_result(result)


def hash_orchestration_evaluation_trace_build_result(result: OrchestrationEvaluationTraceBuildResult) -> str:
    return hash_trace_build_result(result)


def _build_record(
    record: OrchestrationEvaluationTraceRecord,
    source: OrchestrationEvaluationTraceBuildInput,
) -> OrchestrationEvaluationTraceBuildRecord:
    trace_hash = hash_trace_record(record)
    findings = _trace_findings(record)
    expected_hash = source.expected_trace_hashes.get(record.identifier.trace_id) if source.expected_trace_hashes else None
    if expected_hash is not None and expected_hash != trace_hash:
        findings.append(
            OrchestrationEvaluationTraceFinding(
                trace_id=record.identifier.trace_id,
                preflight_id=record.identifier.preflight_id,
                classification=TRACE_HASH_MISMATCH,
                reason="evaluation trace hash does not match expected deterministic hash",
                evidence_ids=(trace_hash, expected_hash),
            )
        )
    provenance_continuity = TRACE_CONTINUITY_GAP if any(finding.classification == TRACE_PROVENANCE_GAP for finding in findings) else TRACE_CONTINUITY_PRESERVED
    explainability_continuity = TRACE_CONTINUITY_GAP if any(finding.classification == TRACE_EXPLAINABILITY_GAP for finding in findings) else TRACE_CONTINUITY_PRESERVED
    integrity_continuity = TRACE_CONTINUITY_GAP if any(finding.classification in (TRACE_INTEGRITY_GAP, TRACE_HASH_MISMATCH, TRACE_STEP_GAP) for finding in findings) else TRACE_CONTINUITY_PRESERVED
    governance_continuity = TRACE_CONTINUITY_GAP if any(finding.classification == TRACE_GOVERNANCE_BOUNDARY_GAP for finding in findings) else TRACE_CONTINUITY_PRESERVED
    return OrchestrationEvaluationTraceBuildRecord(
        trace_id=record.identifier.trace_id,
        preflight_id=record.identifier.preflight_id,
        trace_state=record.trace_state,
        trace_hash=trace_hash,
        trace_step_count=len(record.trace_steps),
        reasoning_step_count=len(record.reasoning_chain),
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


def _trace_findings(record: OrchestrationEvaluationTraceRecord) -> list[OrchestrationEvaluationTraceFinding]:
    findings = [_state_finding(record)]
    findings.append(_finding(record, TRACE_STEP_VISIBLE, "evaluation trace steps are visible", tuple(step.step_id for step in record.trace_steps)))
    findings.append(_finding(record, TRACE_REASONING_CHAIN_VISIBLE, "evaluation reasoning chain is visible", record.reasoning_chain))
    for classification, values, reason in (
        (TRACE_POLICY_VISIBLE, record.policy_ids, "applicable policy references are visible"),
        (TRACE_GOVERNANCE_BOUNDARY_VISIBLE, record.governance_boundaries, "governance boundaries are visible"),
        (TRACE_COMPATIBILITY_DOMAIN_VISIBLE, record.compatibility_domains, "compatibility domains are visible"),
        (TRACE_DEPENDENCY_DOMAIN_VISIBLE, record.dependency_domains, "dependency domains are visible"),
        (TRACE_BLOCKER_DOMAIN_VISIBLE, record.blocker_domains, "blocker domains are visible"),
        (TRACE_UNSUPPORTED_DOMAIN_VISIBLE, record.unsupported_domains, "unsupported domains are visible"),
        (TRACE_PROHIBITED_DOMAIN_VISIBLE, record.prohibited_domains, "prohibited domains are visible"),
        (TRACE_SUPPORTED_DOMAIN_VISIBLE, record.supported_domains, "supported domains are visible"),
    ):
        if values:
            findings.append(_finding(record, classification, reason, values))
    findings.extend(_continuity_findings(record))
    return findings


def _state_finding(record: OrchestrationEvaluationTraceRecord) -> OrchestrationEvaluationTraceFinding:
    state_map = {
        TRACE_SUPPORTED: (TRACE_CLASSIFIED_AS_SUPPORTED, "trace models a supported theoretical preflight result", record.supported_domains),
        TRACE_UNSUPPORTED: (TRACE_CLASSIFIED_AS_UNSUPPORTED, "trace models an unsupported fail-visible preflight result", record.unsupported_domains),
        TRACE_PROHIBITED: (TRACE_CLASSIFIED_AS_PROHIBITED, "trace models a prohibited fail-visible preflight result", record.prohibited_domains),
        TRACE_GOVERNANCE_BLOCKED: (TRACE_CLASSIFIED_AS_GOVERNANCE_BLOCKED, "trace models a governance-blocked preflight result", record.governance_boundaries),
        TRACE_COMPATIBILITY_BLOCKED: (TRACE_CLASSIFIED_AS_COMPATIBILITY_BLOCKED, "trace models a compatibility-blocked preflight result", record.compatibility_domains),
        TRACE_DEPENDENCY_BLOCKED: (TRACE_CLASSIFIED_AS_DEPENDENCY_BLOCKED, "trace models a dependency-blocked preflight result", record.dependency_domains),
    }
    classification, reason, evidence = state_map.get(
        record.trace_state,
        (TRACE_GOVERNANCE_BOUNDARY_GAP, "trace state is not recognized", (record.trace_state,)),
    )
    return _finding(record, classification, reason, evidence)


def _continuity_findings(record: OrchestrationEvaluationTraceRecord) -> list[OrchestrationEvaluationTraceFinding]:
    findings: list[OrchestrationEvaluationTraceFinding] = []
    missing_provenance = _missing_provenance(record)
    if missing_provenance:
        findings.append(_finding(record, TRACE_PROVENANCE_GAP, "evaluation trace provenance continuity gap", missing_provenance))
    if not record.policy_ids:
        findings.append(_finding(record, TRACE_POLICY_GAP, "evaluation trace has no applicable policy references", (record.identifier.trace_id,)))
    if not record.trace_steps or not record.reasoning_chain:
        findings.append(_finding(record, TRACE_STEP_GAP, "evaluation trace step or reasoning chain is missing", (record.identifier.trace_id,)))
    if any(step.step_type not in TRACE_STEP_TYPES for step in record.trace_steps):
        findings.append(_finding(record, TRACE_STEP_GAP, "evaluation trace step type is not recognized", tuple(step.step_type for step in record.trace_steps)))
    if not record.explainability_reference_ids:
        findings.append(_finding(record, TRACE_EXPLAINABILITY_GAP, "evaluation trace explainability reference is missing", (record.identifier.trace_id,)))
    if not record.integrity_reference_ids:
        findings.append(_finding(record, TRACE_INTEGRITY_GAP, "evaluation trace integrity reference is missing", (record.identifier.trace_id,)))
    if _governance_boundary_gap(record):
        findings.append(_finding(record, TRACE_GOVERNANCE_BOUNDARY_GAP, "evaluation trace governance boundary is not planning-only", (record.identifier.trace_id,)))
    return findings


def _finding(
    record: OrchestrationEvaluationTraceRecord,
    classification: str,
    reason: str,
    evidence_ids: tuple[str, ...],
) -> OrchestrationEvaluationTraceFinding:
    return OrchestrationEvaluationTraceFinding(
        trace_id=record.identifier.trace_id,
        preflight_id=record.identifier.preflight_id,
        classification=classification,
        reason=reason,
        evidence_ids=tuple(sorted(evidence_ids)),
    )


def _missing_provenance(record: OrchestrationEvaluationTraceRecord) -> tuple[str, ...]:
    provenance = record.provenance
    missing: list[str] = []
    if not provenance.source_phase:
        missing.append("source_phase")
    if not provenance.source_artifact:
        missing.append("source_artifact")
    if not provenance.preflight_id:
        missing.append("preflight_id")
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


def _governance_boundary_gap(record: OrchestrationEvaluationTraceRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "evaluation_trace_modeling_only")
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
            record.trace_execution_enabled,
        )
    )


def _registry_hash_finding(
    source: OrchestrationEvaluationTraceBuildInput,
    registry_hash: str,
) -> OrchestrationEvaluationTraceFinding | None:
    if source.expected_registry_hash is None or source.expected_registry_hash == registry_hash:
        return None
    return OrchestrationEvaluationTraceFinding(
        trace_id=source.trace_registry.registry_id,
        preflight_id=source.trace_registry.registry_id,
        classification=TRACE_HASH_MISMATCH,
        reason="evaluation trace registry hash does not match expected deterministic hash",
        evidence_ids=(registry_hash, source.expected_registry_hash),
    )


def _trace_count(records: tuple[OrchestrationEvaluationTraceRecord, ...], step_type: str) -> int:
    return sum(1 for record in records if any(step.step_type == step_type for step in record.trace_steps))


def _continuity_status(records: tuple[OrchestrationEvaluationTraceBuildRecord, ...], field: str) -> str:
    return TRACE_CONTINUITY_PRESERVED if all(getattr(record, field) == TRACE_CONTINUITY_PRESERVED for record in records) else TRACE_CONTINUITY_GAP


def _build_status(
    records: tuple[OrchestrationEvaluationTraceBuildRecord, ...],
    findings: tuple[OrchestrationEvaluationTraceFinding, ...],
) -> str:
    if any(finding.classification in STRUCTURAL_TRACE_FINDINGS for finding in findings):
        return TRACE_BUILD_BLOCKED_BY_CONTINUITY_GAP
    if any(record.findings for record in records):
        return TRACE_BUILD_STABLE_WITH_VISIBLE_FINDINGS
    return TRACE_BUILD_STABLE


def _summary(status: str, findings: tuple[OrchestrationEvaluationTraceFinding, ...]) -> str:
    if status == TRACE_BUILD_STABLE:
        return "Evaluation trace building is stable; no trace records require fail-visible classification."
    if status == TRACE_BUILD_STABLE_WITH_VISIBLE_FINDINGS:
        return (
            "Evaluation trace building is stable with visible governance, compatibility, dependency, blocker, "
            "unsupported, prohibited, provenance, explainability, integrity, and reasoning-chain findings."
        )
    visible = tuple(sorted({f"{finding.trace_id}:{finding.classification}" for finding in findings}))
    return f"Evaluation trace building is {status}; visible trace entries: {', '.join(visible)}."


def _finding_sort_key(finding: OrchestrationEvaluationTraceFinding) -> tuple[str, str, str, str]:
    return (finding.trace_id, finding.preflight_id, finding.classification, finding.reason)
