"""Deterministic explainability for v3.6 evaluation chain integrity audits."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_chain_auditor import audit_orchestration_evaluation_chain_integrity
from .orchestration_evaluation_chain_models import (
    CHAIN_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    CHAIN_EXPLAINABILITY_STABLE,
    CHAIN_LINK_VALID,
    OrchestrationEvaluationChainAuditInput,
    OrchestrationEvaluationChainAuditRecord,
    OrchestrationEvaluationChainAuditResult,
    OrchestrationEvaluationChainExplainabilityResult,
    OrchestrationEvaluationChainExplanationRecord,
    export_chain_explainability_result,
    hash_chain_explainability_result,
    serialize_chain_explainability_result,
)


def explain_orchestration_evaluation_chain_integrity(
    audit_result: OrchestrationEvaluationChainAuditResult | None = None,
    audit_input: OrchestrationEvaluationChainAuditInput | None = None,
) -> OrchestrationEvaluationChainExplainabilityResult:
    audit = audit_result or audit_orchestration_evaluation_chain_integrity(audit_input)
    records = tuple(_explain_record(record) for record in audit.audit_records)
    status = (
        CHAIN_EXPLAINABILITY_STABLE
        if all(record.explanation_status == CHAIN_EXPLAINABILITY_STABLE for record in records)
        else CHAIN_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    result = OrchestrationEvaluationChainExplainabilityResult(
        audit_id=audit.audit_id,
        chain_explainability_status=status,
        planning_only=True,
        explanation_records=records,
        valid_link_count=sum(len(record.valid_link_visibility) for record in records),
        missing_link_count=sum(len(record.missing_link_visibility) for record in records),
        blocker_visibility_count=sum(len(record.blocker_visibility) for record in records),
        unsupported_visibility_count=sum(len(record.unsupported_visibility) for record in records),
        prohibited_visibility_count=sum(len(record.prohibited_visibility) for record in records),
        provenance_visibility_count=sum(len(record.provenance_visibility) for record in records),
        explainability_visibility_count=sum(len(record.explainability_visibility) for record in records),
        integrity_visibility_count=sum(len(record.integrity_visibility) for record in records),
        deterministic_chain_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(
        result,
        deterministic_chain_explainability_hash=hash_chain_explainability_result(result),
    )


def explain_orchestration_evaluation_chain(
    audit_result: OrchestrationEvaluationChainAuditResult | None = None,
    audit_input: OrchestrationEvaluationChainAuditInput | None = None,
) -> OrchestrationEvaluationChainExplainabilityResult:
    return explain_orchestration_evaluation_chain_integrity(audit_result, audit_input)


def export_orchestration_evaluation_chain_explainability_result(
    result: OrchestrationEvaluationChainExplainabilityResult,
) -> dict[str, object]:
    return export_chain_explainability_result(result)


def serialize_orchestration_evaluation_chain_explainability_result(
    result: OrchestrationEvaluationChainExplainabilityResult,
) -> str:
    return serialize_chain_explainability_result(result)


def hash_orchestration_evaluation_chain_explainability_result(
    result: OrchestrationEvaluationChainExplainabilityResult,
) -> str:
    return hash_chain_explainability_result(result)


def _explain_record(record: OrchestrationEvaluationChainAuditRecord) -> OrchestrationEvaluationChainExplanationRecord:
    valid_links = tuple(
        sorted(
            f"{finding.link_type}:{finding.reason}"
            for finding in record.findings
            if finding.classification == CHAIN_LINK_VALID
        )
    )
    missing_links = tuple(
        sorted(
            f"{finding.link_type}:{finding.classification}:{finding.reason}"
            for finding in record.findings
            if finding.classification != CHAIN_LINK_VALID
        )
    )
    status = CHAIN_EXPLAINABILITY_STABLE if _has_visibility(record, valid_links, missing_links) else CHAIN_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    return OrchestrationEvaluationChainExplanationRecord(
        chain_id=record.identifier.chain_id,
        packet_id=record.identifier.packet_id,
        explanation_status=status,
        audited_chain_visibility=(
            record.identifier.intent_id,
            record.identifier.mapping_id,
            record.identifier.preflight_id,
            record.identifier.trace_id,
            record.identifier.packet_id,
            record.chain_state,
        ),
        valid_link_visibility=valid_links,
        missing_link_visibility=missing_links,
        blocker_visibility=tuple(sorted((*record.blocker_domains, *record.blocker_visibility))),
        unsupported_visibility=tuple(sorted((*record.unsupported_domains,))),
        prohibited_visibility=tuple(sorted((*record.prohibited_domains,))),
        provenance_visibility=record.provenance_evidence,
        explainability_visibility=record.explainability_evidence,
        integrity_visibility=record.integrity_evidence,
        replay_safety_visibility=record.replay_visibility,
        rollback_safety_visibility=record.rollback_visibility,
    )


def _has_visibility(
    record: OrchestrationEvaluationChainAuditRecord,
    valid_links: tuple[str, ...],
    missing_links: tuple[str, ...],
) -> bool:
    return bool(
        record.identifier.chain_id
        and record.identifier.packet_id
        and record.identifier.trace_id
        and record.identifier.preflight_id
        and record.identifier.mapping_id
        and record.identifier.intent_id
        and valid_links
        and record.provenance_evidence
        and record.explainability_evidence
        and record.integrity_evidence
        and record.governance_visibility
        and record.replay_visibility
        and record.rollback_visibility
        and (record.chain_state != "evaluation_chain_invalid" or missing_links)
    )


def _summary(
    status: str,
    records: tuple[OrchestrationEvaluationChainExplanationRecord, ...],
) -> str:
    if status == CHAIN_EXPLAINABILITY_STABLE:
        return (
            "Evaluation chain explainability is stable; valid links, fail-visible missing links, blockers, "
            "unsupported and prohibited states, provenance, integrity, replay safety, and rollback safety are visible."
        )
    missing = tuple(sorted(record.chain_id for record in records if record.explanation_status != CHAIN_EXPLAINABILITY_STABLE))
    return f"Evaluation chain explainability has visibility gaps for: {', '.join(missing)}."
