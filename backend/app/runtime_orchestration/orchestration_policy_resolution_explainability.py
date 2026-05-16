"""Deterministic orchestration compatibility resolution explainability."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_resolution_auditor import audit_orchestration_policy_resolution
from .orchestration_policy_resolution_models import (
    RESOLUTION_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    RESOLUTION_EXPLAINABILITY_STABLE,
    RESOLUTION_FUTURE_CANDIDATE,
    OrchestrationPolicyResolutionAuditInput,
    OrchestrationPolicyResolutionAuditRecord,
    OrchestrationPolicyResolutionAuditResult,
    OrchestrationPolicyResolutionExplainabilityResult,
    OrchestrationPolicyResolutionExplanationRecord,
    OrchestrationPolicyResolutionRecord,
    OrchestrationPolicyResolutionRegistry,
    export_resolution_explainability_result,
    hash_resolution_explainability_result,
    serialize_resolution_explainability_result,
)
from .orchestration_policy_resolution_registry import default_orchestration_policy_resolution_registry


def explain_orchestration_policy_resolution(
    resolution_registry: OrchestrationPolicyResolutionRegistry | None = None,
    audit_result: OrchestrationPolicyResolutionAuditResult | None = None,
) -> OrchestrationPolicyResolutionExplainabilityResult:
    registry = resolution_registry or default_orchestration_policy_resolution_registry()
    audit = audit_result or audit_orchestration_policy_resolution(
        OrchestrationPolicyResolutionAuditInput(resolution_registry=registry)
    )
    records_by_id = {record.identifier.resolution_id: record for record in registry.records}
    audit_records_by_id = {record.resolution_id: record for record in audit.audit_records}
    records = tuple(
        _explain_record(records_by_id[resolution_id], audit_records_by_id[resolution_id])
        for resolution_id in sorted(records_by_id)
        if resolution_id in audit_records_by_id
    )
    status = (
        RESOLUTION_EXPLAINABILITY_STABLE
        if all(record.explanation_status == RESOLUTION_EXPLAINABILITY_STABLE for record in records)
        else RESOLUTION_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    result = OrchestrationPolicyResolutionExplainabilityResult(
        registry_id=registry.registry_id,
        resolution_explainability_status=status,
        planning_only=True,
        explanation_records=records,
        blocked_explanation_count=len(records),
        future_support_explanation_count=sum(1 for record in records if record.future_support_visibility),
        evidence_gap_visibility_count=sum(len(record.evidence_gap_visibility) for record in records),
        governance_visibility_count=sum(len(record.governance_visibility) for record in records),
        dependency_visibility_count=sum(len(record.dependency_visibility) for record in records),
        continuity_visibility_count=sum(len(record.continuity_visibility) for record in records),
        provenance_visibility_count=sum(len(record.provenance_visibility) for record in records),
        blocker_chain_visibility_count=sum(len(record.blocker_chain_visibility) for record in records),
        deterministic_resolution_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(result, deterministic_resolution_explainability_hash=hash_resolution_explainability_result(result))


def export_orchestration_policy_resolution_explainability_result(
    result: OrchestrationPolicyResolutionExplainabilityResult,
) -> dict[str, object]:
    return export_resolution_explainability_result(result)


def serialize_orchestration_policy_resolution_explainability_result(
    result: OrchestrationPolicyResolutionExplainabilityResult,
) -> str:
    return serialize_resolution_explainability_result(result)


def hash_orchestration_policy_resolution_explainability_result(
    result: OrchestrationPolicyResolutionExplainabilityResult,
) -> str:
    return hash_resolution_explainability_result(result)


def _explain_record(
    record: OrchestrationPolicyResolutionRecord,
    audit_record: OrchestrationPolicyResolutionAuditRecord,
) -> OrchestrationPolicyResolutionExplanationRecord:
    why_blocked = tuple(
        sorted(
            {
                *record.support_rationale,
                *(finding.reason for finding in audit_record.findings),
            }
        )
    )
    future_support = _future_support_visibility(record)
    evidence_gap_visibility = tuple(
        sorted(
            f"{gap.evidence_gap_id}:{'|'.join(sorted(gap.required_before_status_change))}"
            for gap in record.evidence_gaps
        )
    )
    continuity_visibility = tuple(sorted((*record.continuity_gaps, *(_continuity_gaps_from_audit(audit_record)))))
    explanation_status = (
        RESOLUTION_EXPLAINABILITY_STABLE
        if _has_resolution_visibility(record, audit_record, why_blocked, evidence_gap_visibility, continuity_visibility)
        else RESOLUTION_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    return OrchestrationPolicyResolutionExplanationRecord(
        resolution_id=record.identifier.resolution_id,
        relationship_id=record.identifier.relationship_id,
        resolution_classifications=tuple(sorted(audit_record.resolution_classifications)),
        explanation_status=explanation_status,
        why_blocked=why_blocked,
        block_intent_visibility=(
            ("block_intentional:true",) if record.block_intentional else ("block_intentional:false",)
        ),
        future_support_visibility=future_support,
        evidence_gap_visibility=evidence_gap_visibility,
        governance_visibility=tuple(sorted(record.governance_constraints)),
        dependency_visibility=tuple(sorted(record.dependency_gaps)),
        continuity_visibility=continuity_visibility,
        provenance_visibility=_provenance_visibility(record),
        blocker_chain_visibility=tuple(sorted(record.blocker_chain_ids)),
        integrity_visibility=tuple(sorted(record.resolution_integrity_ids)),
    )


def _future_support_visibility(record: OrchestrationPolicyResolutionRecord) -> tuple[str, ...]:
    if not record.future_support_possible and RESOLUTION_FUTURE_CANDIDATE not in record.resolution_classifications:
        return ()
    required = tuple(
        sorted(
            requirement
            for gap in record.evidence_gaps
            for requirement in gap.required_before_status_change
        )
    )
    if not required:
        return ("future_support_blocked_until_evidence_is_declared",)
    return tuple(f"future_support_requires:{requirement}" for requirement in required)


def _continuity_gaps_from_audit(audit_record: OrchestrationPolicyResolutionAuditRecord) -> tuple[str, ...]:
    gaps: list[str] = []
    for field in (
        "provenance_continuity_state",
        "explainability_continuity_state",
        "integrity_continuity_state",
    ):
        value = getattr(audit_record, field)
        if value.endswith("_gap"):
            gaps.append(f"{field}:{value}")
    return tuple(sorted(gaps))


def _provenance_visibility(record: OrchestrationPolicyResolutionRecord) -> tuple[str, ...]:
    provenance = record.provenance
    return tuple(
        sorted(
            (
                provenance.source_phase,
                provenance.source_artifact,
                provenance.compatibility_relationship_id,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            )
        )
    )


def _has_resolution_visibility(
    record: OrchestrationPolicyResolutionRecord,
    audit_record: OrchestrationPolicyResolutionAuditRecord,
    why_blocked: tuple[str, ...],
    evidence_gap_visibility: tuple[str, ...],
    continuity_visibility: tuple[str, ...],
) -> bool:
    return bool(
        why_blocked
        or evidence_gap_visibility
        or record.governance_constraints
        or record.dependency_gaps
        or continuity_visibility
        or record.blocker_chain_ids
        or audit_record.findings
    )


def _summary(
    status: str,
    records: tuple[OrchestrationPolicyResolutionExplanationRecord, ...],
) -> str:
    if status == RESOLUTION_EXPLAINABILITY_STABLE:
        return (
            "Resolution explainability is stable; blocked, intentional, future candidate, evidence-gap, governance, "
            "dependency, continuity, provenance, blocker-chain, and integrity visibility are deterministic."
        )
    missing = tuple(sorted(record.resolution_id for record in records if record.explanation_status != RESOLUTION_EXPLAINABILITY_STABLE))
    return f"Resolution explainability has visibility gaps for: {', '.join(missing)}."
