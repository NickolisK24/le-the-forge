"""Deterministic integrity auditing for v3.6 evaluation chains."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_chain_auditor import audit_orchestration_evaluation_chain_integrity
from .orchestration_evaluation_chain_explainability import explain_orchestration_evaluation_chain_integrity
from .orchestration_evaluation_chain_models import (
    CHAIN_CONTINUITY_GAP,
    CHAIN_CONTINUITY_PRESERVED,
    CHAIN_EXPLAINABILITY_STABLE,
    CHAIN_INTEGRITY_BLOCKED_BY_CONTINUITY_GAP,
    CHAIN_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    CHAIN_INTEGRITY_BLOCKED_BY_HASH_GAP,
    CHAIN_INTEGRITY_BLOCKED_BY_SOURCE_GAP,
    CHAIN_INTEGRITY_STABLE,
    CHAIN_LINK_BLOCKER,
    CHAIN_LINK_COMPATIBILITY,
    CHAIN_LINK_GOVERNANCE,
    CHAIN_LINK_INTENT,
    CHAIN_LINK_MAPPING,
    CHAIN_LINK_POLICY,
    CHAIN_LINK_PREFLIGHT,
    CHAIN_LINK_PROVENANCE,
    CHAIN_LINK_REPLAY,
    CHAIN_LINK_REPLAY_SAFETY,
    CHAIN_LINK_RESOLUTION,
    CHAIN_LINK_ROLLBACK_SAFETY,
    CHAIN_LINK_TRACE,
    CHAIN_VALID,
    OrchestrationEvaluationChainAuditResult,
    OrchestrationEvaluationChainExplainabilityResult,
    OrchestrationEvaluationChainIntegrityInput,
    OrchestrationEvaluationChainIntegrityResult,
    OrchestrationEvaluationChainIntegritySummary,
    export_chain_integrity_result,
    hash_chain_audit_record,
    hash_chain_integrity_result,
    serialize_chain_audit_record,
    serialize_chain_audit_result,
    serialize_chain_explainability_result,
    serialize_chain_integrity_result,
)


def default_orchestration_evaluation_chain_integrity_input() -> OrchestrationEvaluationChainIntegrityInput:
    audit = audit_orchestration_evaluation_chain_integrity()
    explainability = explain_orchestration_evaluation_chain_integrity(audit)
    return OrchestrationEvaluationChainIntegrityInput(
        audit_result=audit,
        explainability_result=explainability,
    )


def audit_orchestration_evaluation_chain_integrity_result(
    integrity_input: OrchestrationEvaluationChainIntegrityInput | None = None,
) -> OrchestrationEvaluationChainIntegrityResult:
    source = integrity_input or default_orchestration_evaluation_chain_integrity_input()
    source_evidence = _source_evidence_integrity(source.audit_result)
    chain_hash = _chain_hash_integrity(source)
    replay = _link_integrity(source.audit_result, CHAIN_LINK_REPLAY, "replay_packet")
    trace = _link_integrity(source.audit_result, CHAIN_LINK_TRACE, "trace")
    preflight = _link_integrity(source.audit_result, CHAIN_LINK_PREFLIGHT, "preflight")
    mapping = _link_integrity(source.audit_result, CHAIN_LINK_MAPPING, "mapping")
    intent = _link_integrity(source.audit_result, CHAIN_LINK_INTENT, "intent")
    policy = _link_integrity(source.audit_result, CHAIN_LINK_POLICY, "policy")
    compatibility = _link_integrity(source.audit_result, CHAIN_LINK_COMPATIBILITY, "compatibility")
    resolution = _link_integrity(source.audit_result, CHAIN_LINK_RESOLUTION, "resolution")
    blocker = _link_integrity(source.audit_result, CHAIN_LINK_BLOCKER, "blocker")
    governance = _link_integrity(source.audit_result, CHAIN_LINK_GOVERNANCE, "governance")
    provenance = _link_integrity(source.audit_result, CHAIN_LINK_PROVENANCE, "provenance")
    explainability = _explainability_integrity(source)
    replay_safety = _link_integrity(source.audit_result, CHAIN_LINK_REPLAY_SAFETY, "replay_safety")
    rollback_safety = _link_integrity(source.audit_result, CHAIN_LINK_ROLLBACK_SAFETY, "rollback_safety")
    serialization = _serialization_integrity(source.audit_result, source.explainability_result)
    failures = _failure_summary(
        source_evidence,
        chain_hash,
        replay,
        trace,
        preflight,
        mapping,
        intent,
        policy,
        compatibility,
        resolution,
        blocker,
        governance,
        provenance,
        explainability,
        replay_safety,
        rollback_safety,
        serialization,
    )
    status = _integrity_status(source_evidence, chain_hash, explainability, failures)
    result = OrchestrationEvaluationChainIntegrityResult(
        audit_id=source.audit_result.audit_id,
        chain_integrity_status=status,
        planning_only=True,
        source_evidence_integrity=source_evidence,
        chain_hash_integrity=chain_hash,
        replay_packet_integrity=replay,
        trace_integrity=trace,
        preflight_integrity=preflight,
        mapping_integrity=mapping,
        intent_integrity=intent,
        policy_integrity=policy,
        compatibility_integrity=compatibility,
        resolution_integrity=resolution,
        blocker_integrity=blocker,
        governance_integrity=governance,
        provenance_integrity=provenance,
        explainability_integrity=explainability,
        replay_safety_integrity=replay_safety,
        rollback_safety_integrity=rollback_safety,
        deterministic_serialization_integrity=serialization,
        failure_classification_summary=failures,
        manual_review_summary=tuple(sorted(set(source.manual_review_reasons))),
        deterministic_chain_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_chain_integrity_hash=hash_chain_integrity_result(result))


def audit_orchestration_evaluation_chain_integrity_audit(
    integrity_input: OrchestrationEvaluationChainIntegrityInput | None = None,
) -> OrchestrationEvaluationChainIntegrityResult:
    return audit_orchestration_evaluation_chain_integrity_result(integrity_input)


def export_orchestration_evaluation_chain_integrity_result(
    result: OrchestrationEvaluationChainIntegrityResult,
) -> dict[str, object]:
    return export_chain_integrity_result(result)


def serialize_orchestration_evaluation_chain_integrity_result(
    result: OrchestrationEvaluationChainIntegrityResult,
) -> str:
    return serialize_chain_integrity_result(result)


def hash_orchestration_evaluation_chain_integrity_result(
    result: OrchestrationEvaluationChainIntegrityResult,
) -> str:
    return hash_chain_integrity_result(result)


def _source_evidence_integrity(
    audit: OrchestrationEvaluationChainAuditResult,
) -> OrchestrationEvaluationChainIntegritySummary:
    references = tuple(f"{key}:{value}" for key, value in sorted(audit.deterministic_source_hashes.items()))
    required = (
        "policy_registry",
        "compatibility_registry",
        "resolution_registry",
        "intent_registry",
        "mapping_registry",
        "preflight_registry",
        "trace_registry",
        "replay_registry",
        "replay_build",
        "replay_explainability",
        "replay_integrity",
    )
    failures = tuple(sorted(f"missing_source_hash:{key}" for key in required if key not in audit.deterministic_source_hashes))
    return OrchestrationEvaluationChainIntegritySummary("source_evidence", references, failures)


def _chain_hash_integrity(
    source: OrchestrationEvaluationChainIntegrityInput,
) -> OrchestrationEvaluationChainIntegritySummary:
    references = tuple(
        sorted(
            f"{record.identifier.chain_id}:{hash_chain_audit_record(record)}"
            for record in source.audit_result.audit_records
        )
    )
    ids = [record.identifier.chain_id for record in source.audit_result.audit_records]
    duplicates = tuple(sorted({chain_id for chain_id in ids if ids.count(chain_id) > 1}))
    failures = [f"duplicate_chain_id:{chain_id}" for chain_id in duplicates]
    if source.expected_audit_hash is not None and source.expected_audit_hash != source.audit_result.deterministic_chain_audit_hash:
        failures.append("chain_audit_hash_mismatch")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_chain_explainability_hash:
        failures.append("chain_explainability_hash_mismatch")
    return OrchestrationEvaluationChainIntegritySummary("chain_hash", references, tuple(sorted(failures)))


def _link_integrity(
    audit: OrchestrationEvaluationChainAuditResult,
    link_type: str,
    area: str,
) -> OrchestrationEvaluationChainIntegritySummary:
    references = tuple(sorted(f"{record.identifier.chain_id}:{link_type}" for record in audit.audit_records))
    failures = tuple(
        sorted(
            f"{record.identifier.chain_id}:{link_type}:continuity_gap"
            for record in audit.audit_records
            if record.link_continuity.get(link_type) != CHAIN_CONTINUITY_PRESERVED
        )
    )
    return OrchestrationEvaluationChainIntegritySummary(area, references, failures)


def _explainability_integrity(
    source: OrchestrationEvaluationChainIntegrityInput,
) -> OrchestrationEvaluationChainIntegritySummary:
    references = (
        source.audit_result.deterministic_chain_audit_hash,
        source.explainability_result.deterministic_chain_explainability_hash,
    )
    failures: list[str] = []
    if source.explainability_result.chain_explainability_status != CHAIN_EXPLAINABILITY_STABLE:
        failures.append(f"chain_explainability_status:{source.explainability_result.chain_explainability_status}")
    if source.audit_result.explainability_continuity_status != CHAIN_CONTINUITY_PRESERVED:
        failures.append(f"chain_explainability_continuity:{source.audit_result.explainability_continuity_status}")
    return OrchestrationEvaluationChainIntegritySummary("explainability", references, tuple(sorted(failures)))


def _serialization_integrity(
    audit: OrchestrationEvaluationChainAuditResult,
    explainability: OrchestrationEvaluationChainExplainabilityResult,
) -> OrchestrationEvaluationChainIntegritySummary:
    audit_serialized = serialize_chain_audit_result(audit)
    explainability_serialized = serialize_chain_explainability_result(explainability)
    record_serializations = tuple(serialize_chain_audit_record(record) for record in audit.audit_records)
    failures: list[str] = []
    if audit_serialized != serialize_chain_audit_result(audit):
        failures.append("chain_audit_serialization_not_stable")
    if explainability_serialized != serialize_chain_explainability_result(explainability):
        failures.append("chain_explainability_serialization_not_stable")
    if not all(serialized == serialize_chain_audit_record(record) for serialized, record in zip(record_serializations, audit.audit_records)):
        failures.append("chain_record_serialization_not_stable")
    return OrchestrationEvaluationChainIntegritySummary(
        "deterministic_serialization",
        (audit_serialized, explainability_serialized, *record_serializations),
        tuple(sorted(failures)),
    )


def _failure_summary(*summaries: OrchestrationEvaluationChainIntegritySummary) -> tuple[str, ...]:
    return tuple(
        sorted(
            f"{summary.area}:{failure}"
            for summary in summaries
            for failure in summary.failures
        )
    )


def _integrity_status(
    source_evidence: OrchestrationEvaluationChainIntegritySummary,
    chain_hash: OrchestrationEvaluationChainIntegritySummary,
    explainability: OrchestrationEvaluationChainIntegritySummary,
    failures: tuple[str, ...],
) -> str:
    if not failures:
        return CHAIN_INTEGRITY_STABLE
    if source_evidence.failures:
        return CHAIN_INTEGRITY_BLOCKED_BY_SOURCE_GAP
    if chain_hash.failures:
        return CHAIN_INTEGRITY_BLOCKED_BY_HASH_GAP
    if explainability.failures:
        return CHAIN_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    return CHAIN_INTEGRITY_BLOCKED_BY_CONTINUITY_GAP


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == CHAIN_INTEGRITY_STABLE:
        return (
            "Evaluation chain integrity is stable across source evidence, replay packets, traces, "
            "preflight records, mappings, intents, policies, compatibility relationships, resolution records, "
            "blockers, governance, provenance, explainability, replay safety, and rollback safety."
        )
    return f"Evaluation chain integrity has fail-visible findings: {', '.join(failures)}."
