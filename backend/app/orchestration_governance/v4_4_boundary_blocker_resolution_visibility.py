"""Visibility helpers for v4.4 blocker resolution closeout preparation."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_boundary_blocker_resolution_models import (
    BLOCKER_STATE_BLOCKED,
    BLOCKER_STATE_CLOSEOUT_BLOCKED,
    BLOCKER_STATE_CLOSEOUT_READY,
    BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
    BLOCKER_STATE_ESCALATED,
    BLOCKER_STATE_INFORMATIONAL,
    BLOCKER_STATE_INHERITED_CONSTRAINT,
    BLOCKER_STATE_INHERITED_PROHIBITION,
    BLOCKER_STATE_INTENTIONALLY_PRESERVED,
    BLOCKER_STATE_PROHIBITED,
    BLOCKER_STATE_RESOLVED,
    BLOCKER_STATE_WARNING,
    BOUNDARY_BLOCKER_RESOLUTION_STATES,
    FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES,
    BlockerClassificationRecord,
    BoundaryBlockerResolutionCloseoutPreparation,
    CloseoutEligibilityRecord,
    CloseoutPreparationSummaryRecord,
    EscalationRecord,
    FailVisibleExplanationRecord,
    InheritedConstraintRecord,
    InheritedProhibitionRecord,
    Phase8ReadinessEvidenceReference,
    UnresolvedLimitationRecord,
    V45InheritedPlanningBoundaryRecord,
    WarningClassificationRecord,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _state_count(values: Iterable[str]) -> dict[str, int]:
    counts = Counter(values)
    return {
        state: int(counts.get(state, 0)) for state in BOUNDARY_BLOCKER_RESOLUTION_STATES
    }


def count_phase8_evidence_states(
    records: Iterable[Phase8ReadinessEvidenceReference],
) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (record.readiness_state, record.blocker_state, record.warning_state)
    )


def count_blocker_classification_states(
    records: Iterable[BlockerClassificationRecord],
) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (record.classification_state, record.closeout_state)
    )


def count_warning_classification_states(
    records: Iterable[WarningClassificationRecord],
) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (record.classification_state, record.warning_state)
    )


def count_inherited_prohibition_states(
    records: Iterable[InheritedProhibitionRecord],
) -> dict[str, int]:
    return _state_count(record.prohibition_state for record in records)


def count_inherited_constraint_states(
    records: Iterable[InheritedConstraintRecord],
) -> dict[str, int]:
    return _state_count(record.constraint_state for record in records)


def count_unresolved_limitation_states(
    records: Iterable[UnresolvedLimitationRecord],
) -> dict[str, int]:
    return _state_count(record.limitation_state for record in records)


def count_escalation_states(records: Iterable[EscalationRecord]) -> dict[str, int]:
    return _state_count(record.escalation_state for record in records)


def count_closeout_eligibility_states(
    records: Iterable[CloseoutEligibilityRecord],
) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (record.eligibility_state, record.classification_state)
    )


def count_planning_boundary_states(
    records: Iterable[V45InheritedPlanningBoundaryRecord],
) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (record.boundary_state, record.planning_boundary_state)
    )


def count_explanation_states(
    records: Iterable[FailVisibleExplanationRecord],
) -> dict[str, int]:
    return _state_count(record.explanation_state for record in records)


def count_closeout_summary_states(
    records: Iterable[CloseoutPreparationSummaryRecord],
) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (
            record.closeout_state,
            record.blocker_state,
            record.warning_state,
            record.escalation_state,
            record.certification_state,
        )
    )


def count_combined_blocker_resolution_states(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, int]:
    states: list[str] = [
        certification.provenance_record.provenance_state,
        certification.lineage_record.lineage_state,
        certification.replay_rollback_record.replay_state,
        certification.replay_rollback_record.rollback_state,
    ]
    for record in certification.phase8_evidence_references:
        states.extend((record.readiness_state, record.blocker_state, record.warning_state))
    for record in certification.blocker_records:
        states.extend((record.classification_state, record.closeout_state))
    for record in certification.warning_records:
        states.extend((record.classification_state, record.warning_state))
    states.extend(
        record.prohibition_state for record in certification.inherited_prohibition_records
    )
    states.extend(record.constraint_state for record in certification.inherited_constraint_records)
    states.extend(record.limitation_state for record in certification.limitation_records)
    states.extend(record.escalation_state for record in certification.escalation_records)
    for record in certification.closeout_eligibility_records:
        states.extend((record.eligibility_state, record.classification_state))
    for record in certification.planning_boundary_records:
        states.extend((record.boundary_state, record.planning_boundary_state))
    states.extend(record.explanation_state for record in certification.fail_visible_explanations)
    states.extend(
        record.certification_state for record in certification.non_operational_certifications
    )
    for record in certification.closeout_summaries:
        states.extend(
            (
                record.closeout_state,
                record.blocker_state,
                record.warning_state,
                record.escalation_state,
                record.certification_state,
            )
        )
    return _state_count(states)


def blocker_resolution_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.blocker_records)
    counts = count_blocker_classification_states(records)
    severity_counts = Counter(record.severity for record in records)
    return {
        "blocker_classification_total": len(records),
        "blocker_ids": _ordered_ids(record.blocker_id for record in records),
        "blocker_state_counts": counts,
        "blocker_severity_counts": {
            severity: int(severity_counts[severity]) for severity in sorted(severity_counts)
        },
        "resolved_count": counts[BLOCKER_STATE_RESOLVED],
        "intentionally_preserved_count": counts[BLOCKER_STATE_INTENTIONALLY_PRESERVED],
        "inherited_prohibition_count": counts[BLOCKER_STATE_INHERITED_PROHIBITION],
        "inherited_constraint_count": counts[BLOCKER_STATE_INHERITED_CONSTRAINT],
        "escalated_count": counts[BLOCKER_STATE_ESCALATED],
        "closeout_blocked_count": counts[BLOCKER_STATE_CLOSEOUT_BLOCKED],
        "fail_visible_blocker_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "blocker_authorization_enabled_count": sum(
            1 for record in records if record.blocker_authorization_enabled
        ),
        "approval_enabled_count": sum(1 for record in records if record.approval_enabled),
        "activation_enabled_count": sum(1 for record in records if record.activation_enabled),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "blocker_auto_resolution_enabled_count": sum(
            1 for record in records if record.blocker_auto_resolution_enabled
        ),
    }


def warning_classification_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.warning_records)
    counts = count_warning_classification_states(records)
    severity_counts = Counter(record.severity for record in records)
    return {
        "warning_classification_total": len(records),
        "warning_ids": _ordered_ids(record.warning_id for record in records),
        "warning_state_counts": counts,
        "warning_severity_counts": {
            severity: int(severity_counts[severity]) for severity in sorted(severity_counts)
        },
        "warning_count": int(severity_counts[BLOCKER_STATE_WARNING]),
        "informational_count": int(severity_counts[BLOCKER_STATE_INFORMATIONAL]),
        "intentionally_preserved_count": counts[BLOCKER_STATE_INTENTIONALLY_PRESERVED],
        "inherited_constraint_count": counts[BLOCKER_STATE_INHERITED_CONSTRAINT],
        "escalated_count": counts[BLOCKER_STATE_ESCALATED],
        "fail_visible_warning_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "warning_suppression_enabled_count": sum(
            1 for record in records if record.warning_suppression_enabled
        ),
        "approval_enabled_count": sum(1 for record in records if record.approval_enabled),
        "activation_enabled_count": sum(1 for record in records if record.activation_enabled),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
    }


def inherited_prohibition_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.inherited_prohibition_records)
    counts = count_inherited_prohibition_states(records)
    return {
        "inherited_prohibition_total": len(records),
        "prohibition_ids": _ordered_ids(record.prohibition_id for record in records),
        "prohibition_state_counts": counts,
        "fail_visible_prohibition_count": sum(1 for record in records if record.fail_visible),
        "is_prohibition_count": sum(1 for record in records if record.is_prohibition),
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "runtime_execution_enabled_count": sum(
            1 for record in records if record.runtime_execution_enabled
        ),
        "orchestration_authorization_enabled_count": sum(
            1 for record in records if record.orchestration_authorization_enabled
        ),
        "orchestration_approval_enabled_count": sum(
            1 for record in records if record.orchestration_approval_enabled
        ),
        "orchestration_activation_enabled_count": sum(
            1 for record in records if record.orchestration_activation_enabled
        ),
        "planner_integration_enabled_count": sum(
            1 for record in records if record.planner_integration_enabled
        ),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
    }


def inherited_constraint_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.inherited_constraint_records)
    counts = count_inherited_constraint_states(records)
    return {
        "inherited_constraint_total": len(records),
        "constraint_ids": _ordered_ids(record.constraint_id for record in records),
        "constraint_state_counts": counts,
        "inherited_by_v4_5_count": sum(1 for record in records if record.inherited_by_v4_5),
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "planner_integration_enabled_count": sum(
            1 for record in records if record.planner_integration_enabled
        ),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
        "v4_5_activation_enabled_count": sum(
            1 for record in records if record.v4_5_activation_enabled
        ),
    }


def unresolved_limitation_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.limitation_records)
    counts = count_unresolved_limitation_states(records)
    return {
        "unresolved_limitation_total": len(records),
        "limitation_ids": _ordered_ids(record.limitation_id for record in records),
        "limitation_state_counts": counts,
        "inherited_limitation_count": sum(1 for record in records if record.inherited_by_v4_5),
        "fail_visible_limitation_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(
            1 for record in records if record.automatic_repair_enabled
        ),
    }


def escalation_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.escalation_records)
    counts = count_escalation_states(records)
    return {
        "escalation_total": len(records),
        "escalation_ids": _ordered_ids(record.escalation_id for record in records),
        "escalation_state_counts": counts,
        "escalated_count": counts[BLOCKER_STATE_ESCALATED],
        "fail_visible_escalation_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_actioning": all(record.non_actioning for record in records),
        "closeout_activation_enabled_count": sum(
            1 for record in records if record.closeout_activation_enabled
        ),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def closeout_eligibility_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.closeout_eligibility_records)
    counts = count_closeout_eligibility_states(records)
    return {
        "closeout_eligibility_total": len(records),
        "eligibility_ids": _ordered_ids(record.eligibility_id for record in records),
        "eligibility_state_counts": counts,
        "closeout_ready_count": counts[BLOCKER_STATE_CLOSEOUT_READY],
        "closeout_ready_with_limitations_count": counts[
            BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS
        ],
        "closeout_blocked_count": counts[BLOCKER_STATE_CLOSEOUT_BLOCKED],
        "fail_visible_closeout_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "closeout_activation_enabled_count": sum(
            1 for record in records if record.closeout_activation_enabled
        ),
        "readiness_authorization_enabled_count": sum(
            1 for record in records if record.readiness_authorization_enabled
        ),
        "runtime_readiness_inferred_count": sum(
            1 for record in records if record.runtime_readiness_inferred
        ),
    }


def v4_5_planning_boundary_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.planning_boundary_records)
    counts = count_planning_boundary_states(records)
    return {
        "planning_boundary_total": len(records),
        "planning_boundary_ids": _ordered_ids(
            record.planning_boundary_id for record in records
        ),
        "planning_boundary_state_counts": counts,
        "inherited_constraint_boundary_count": counts[BLOCKER_STATE_INHERITED_CONSTRAINT],
        "inherited_prohibition_boundary_count": counts[BLOCKER_STATE_INHERITED_PROHIBITION],
        "closeout_blocked_boundary_count": counts[BLOCKER_STATE_CLOSEOUT_BLOCKED],
        "fail_visible_planning_boundary_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "v4_5_activation_enabled_count": sum(
            1 for record in records if record.v4_5_activation_enabled
        ),
        "planner_integration_enabled_count": sum(
            1 for record in records if record.planner_integration_enabled
        ),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
        "runtime_readiness_inferred_count": sum(
            1 for record in records if record.runtime_readiness_inferred
        ),
    }


def fail_visible_blocker_summaries(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.fail_visible_explanations)
    counts = count_explanation_states(records)
    return {
        "fail_visible_explanation_total": len(records),
        "explanation_ids": _ordered_ids(record.explanation_id for record in records),
        "explanation_state_counts": counts,
        "fail_visible_explanation_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "approval_enabled_count": sum(1 for record in records if record.approval_enabled),
        "activation_enabled_count": sum(1 for record in records if record.activation_enabled),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def closeout_summary_visibility(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    records = tuple(certification.closeout_summaries)
    counts = count_closeout_summary_states(records)
    return {
        "closeout_summary_total": len(records),
        "summary_ids": _ordered_ids(record.summary_id for record in records),
        "summary_state_counts": counts,
        "closeout_ready_with_limitations_count": counts[
            BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS
        ],
        "closeout_blocked_count": counts[BLOCKER_STATE_CLOSEOUT_BLOCKED],
        "warning_count": counts[BLOCKER_STATE_WARNING],
        "informational_count": counts[BLOCKER_STATE_INFORMATIONAL],
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "non_operational": all(record.non_operational for record in records),
        "closeout_activation_signal_enabled_count": sum(
            1 for record in records if record.closeout_activation_signal_enabled
        ),
        "blocker_authorization_signal_enabled_count": sum(
            1 for record in records if record.blocker_authorization_signal_enabled
        ),
        "runtime_readiness_inferred_count": sum(
            1 for record in records if record.runtime_readiness_inferred
        ),
    }


def provenance_continuity_visibility(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    record = certification.provenance_record
    return {
        "provenance_id": record.provenance_id,
        "source_reference_ids": _ordered_ids(record.source_reference_ids),
        "source_hash_references": _ordered_ids(record.source_hash_references),
        "provenance_state": record.provenance_state,
        "provenance_continuity_preserved": record.provenance_continuity_preserved,
        "hidden_source_inference_used": record.hidden_source_inference_used,
        "production_consumption_enabled": record.production_consumption_enabled,
    }


def lineage_continuity_visibility(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    record = certification.lineage_record
    return {
        "lineage_id": record.lineage_id,
        "lineage_reference_ids": _ordered_ids(record.lineage_reference_ids),
        "lineage_hash_references": _ordered_ids(record.lineage_hash_references),
        "lineage_state": record.lineage_state,
        "lineage_continuity_preserved": record.lineage_continuity_preserved,
        "ambiguous_lineage_inferred": record.ambiguous_lineage_inferred,
        "operational_mutation_enabled": record.operational_mutation_enabled,
    }


def governance_safe_closeout_explainability(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    return {
        "descriptive_only": certification.descriptive_only,
        "non_operational": certification.non_operational,
        "non_authoritative": certification.non_authoritative,
        "non_authorizing": certification.non_authorizing,
        "non_approving": certification.non_approving,
        "non_activating": certification.non_activating,
        "non_recommending": certification.non_recommending,
        "non_deciding": certification.non_deciding,
        "non_remediating": certification.non_remediating,
        "non_mutating": certification.non_mutating,
        "runtime_readiness_inference_disabled": (
            certification.runtime_readiness_inference_disabled
        ),
        "explicit_limitation_count": len(certification.explicit_limitations),
        "explicit_prohibition_count": len(certification.explicit_prohibitions),
    }


def validate_required_blocker_resolution_visibility(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    counts = count_combined_blocker_resolution_states(certification)
    missing_states = [state for state in BOUNDARY_BLOCKER_RESOLUTION_STATES if counts[state] <= 0]
    missing_fail_visible_states = [
        state for state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES if counts[state] <= 0
    ]
    return {
        "valid": not missing_states and not missing_fail_visible_states,
        "combined_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": missing_fail_visible_states,
    }
