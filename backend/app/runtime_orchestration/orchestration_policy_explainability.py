"""Deterministic orchestration policy explainability for v3.6."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_evaluator import evaluate_orchestration_policy_compatibility
from .orchestration_policy_models import (
    POLICY_CONTINUITY_GAP,
    POLICY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    POLICY_EXPLAINABILITY_STABLE,
    POLICY_PROHIBITED,
    POLICY_SUPPORTED,
    POLICY_UNSUPPORTED,
    OrchestrationPolicyDefinition,
    OrchestrationPolicyEvaluationInput,
    OrchestrationPolicyEvaluationResult,
    OrchestrationPolicyExplainabilityResult,
    OrchestrationPolicyExplanationRecord,
    OrchestrationPolicyRegistry,
    export_policy_explainability_result,
    hash_policy_explainability_result,
    serialize_policy_explainability_result,
)
from .orchestration_policy_registry import default_orchestration_policy_registry


def explain_orchestration_policy_evaluation(
    registry: OrchestrationPolicyRegistry | None = None,
    evaluation_result: OrchestrationPolicyEvaluationResult | None = None,
) -> OrchestrationPolicyExplainabilityResult:
    source_registry = registry or default_orchestration_policy_registry()
    source_evaluation = evaluation_result or evaluate_orchestration_policy_compatibility(
        OrchestrationPolicyEvaluationInput(registry=source_registry)
    )
    policies_by_id = {policy.identifier.policy_id: policy for policy in source_registry.policies}
    records = tuple(
        _explain_policy(policies_by_id[record.policy_id], record)
        for record in sorted(source_evaluation.policy_records, key=lambda item: item.policy_id)
        if record.policy_id in policies_by_id
    )
    status = POLICY_EXPLAINABILITY_STABLE if all(_record_has_visibility(record) for record in records) else POLICY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    result = OrchestrationPolicyExplainabilityResult(
        registry_id=source_registry.registry_id,
        explainability_status=status,
        planning_only=True,
        explanation_records=records,
        supported_explanation_count=sum(1 for record in records if record.support_state == POLICY_SUPPORTED),
        prohibited_explanation_count=sum(1 for record in records if record.support_state == POLICY_PROHIBITED),
        unsupported_explanation_count=sum(1 for record in records if record.support_state == POLICY_UNSUPPORTED),
        blocked_explanation_count=sum(1 for record in records if record.why_blocked),
        dependency_chain_visibility_count=sum(len(record.dependency_chain_visibility) for record in records),
        governance_chain_visibility_count=sum(len(record.governance_chain_visibility) for record in records),
        continuity_gap_visibility_count=sum(len(record.continuity_gap_visibility) for record in records),
        provenance_visibility_count=sum(len(record.provenance_visibility) for record in records),
        integrity_visibility_count=sum(len(record.integrity_visibility) for record in records),
        deterministic_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(result, deterministic_explainability_hash=hash_policy_explainability_result(result))


def export_orchestration_policy_explainability_result(result: OrchestrationPolicyExplainabilityResult) -> dict[str, object]:
    return export_policy_explainability_result(result)


def serialize_orchestration_policy_explainability_result(result: OrchestrationPolicyExplainabilityResult) -> str:
    return serialize_policy_explainability_result(result)


def hash_orchestration_policy_explainability_result(result: OrchestrationPolicyExplainabilityResult) -> str:
    return hash_policy_explainability_result(result)


def _explain_policy(policy: OrchestrationPolicyDefinition, evaluation_record) -> OrchestrationPolicyExplanationRecord:
    blockers = tuple(sorted({f"{blocker.blocker_state}:{blocker.reason}" for blocker in evaluation_record.blockers}))
    continuity_gaps = _continuity_gaps(evaluation_record)
    return OrchestrationPolicyExplanationRecord(
        policy_id=policy.identifier.policy_id,
        explanation_status=POLICY_EXPLAINABILITY_STABLE if _has_policy_explanation(policy, evaluation_record, blockers, continuity_gaps) else POLICY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
        support_state=policy.support_state,
        classification=policy.classification,
        why_supported=_why_supported(policy, evaluation_record),
        why_blocked=blockers,
        why_prohibited=_why_prohibited(policy),
        why_unsupported=_why_unsupported(policy),
        dependency_chain_visibility=evaluation_record.dependency_chain,
        governance_chain_visibility=_governance_chain(policy),
        continuity_gap_visibility=continuity_gaps,
        provenance_visibility=_provenance_visibility(policy),
        integrity_visibility=tuple(sorted(policy.integrity_reference_ids)),
        blocker_visibility=blockers,
    )


def _why_supported(policy: OrchestrationPolicyDefinition, evaluation_record) -> tuple[str, ...]:
    if policy.support_state != POLICY_SUPPORTED or evaluation_record.blockers:
        return ()
    return tuple(sorted(policy.support_rationale)) or (
        "policy is supported because deterministic governance, provenance, dependency, integrity, and explainability continuity are preserved",
    )


def _why_prohibited(policy: OrchestrationPolicyDefinition) -> tuple[str, ...]:
    if policy.support_state != POLICY_PROHIBITED:
        return ()
    return tuple(sorted(policy.blocker_reasons)) or ("policy is prohibited by orchestration governance boundary",)


def _why_unsupported(policy: OrchestrationPolicyDefinition) -> tuple[str, ...]:
    if policy.support_state != POLICY_UNSUPPORTED:
        return ()
    return tuple(sorted(policy.blocker_reasons)) or ("policy state is unsupported by v3.6 policy intelligence",)


def _governance_chain(policy: OrchestrationPolicyDefinition) -> tuple[str, ...]:
    return tuple(f"{key}={value}" for key, value in sorted(policy.governance_metadata.items()))


def _provenance_visibility(policy: OrchestrationPolicyDefinition) -> tuple[str, ...]:
    provenance = policy.provenance
    return tuple(
        sorted(
            (
                provenance.source_phase,
                provenance.source_artifact,
                *provenance.upstream_policy_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            )
        )
    )


def _continuity_gaps(evaluation_record) -> tuple[str, ...]:
    gaps: list[str] = []
    if evaluation_record.dependency_state != "policy_dependency_satisfied":
        gaps.append(f"dependency:{evaluation_record.dependency_state}")
    for field in (
        "governance_continuity_state",
        "provenance_continuity_state",
        "integrity_continuity_state",
        "explainability_continuity_state",
    ):
        value = getattr(evaluation_record, field)
        if value == POLICY_CONTINUITY_GAP:
            gaps.append(f"{field}:{value}")
    return tuple(sorted(gaps))


def _record_has_visibility(record: OrchestrationPolicyExplanationRecord) -> bool:
    return bool(
        record.why_supported
        or record.why_blocked
        or record.why_prohibited
        or record.why_unsupported
        or record.continuity_gap_visibility
    )


def _has_policy_explanation(policy, evaluation_record, blockers: tuple[str, ...], continuity_gaps: tuple[str, ...]) -> bool:
    return bool(_why_supported(policy, evaluation_record) or blockers or _why_prohibited(policy) or _why_unsupported(policy) or continuity_gaps)


def _summary(status: str, records: tuple[OrchestrationPolicyExplanationRecord, ...]) -> str:
    if status == POLICY_EXPLAINABILITY_STABLE:
        return (
            "Policy explainability is stable; supported, blocked, prohibited, unsupported, dependency, governance, provenance, "
            "and integrity visibility are deterministic and planning-only."
        )
    missing = tuple(sorted(record.policy_id for record in records if record.explanation_status != POLICY_EXPLAINABILITY_STABLE))
    return f"Policy explainability has visibility gaps for: {', '.join(missing)}."
