"""Visibility helpers for v4.4 boundary readiness transition certification."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_boundary_readiness_transition_models import (
    BOUNDARY_READINESS_TRANSITION_STATES,
    FAIL_VISIBLE_READINESS_TRANSITION_STATES,
    READINESS_STATE_COMPLETE,
    READINESS_STATE_NOT_READY,
    READINESS_STATE_READY_FOR_CLOSEOUT,
    READINESS_STATE_READY_WITH_WARNINGS,
    READINESS_STATE_TRANSITION_BLOCKED,
    READINESS_STATE_TRANSITION_READY,
    READINESS_STATE_TRANSITION_READY_WITH_WARNINGS,
    BlockerWarningVisibilityRecord,
    BoundaryReadinessTransitionCertification,
    CompletenessSummaryRecord,
    LimitationVisibilityRecord,
    PhaseEvidenceReference,
    ReadinessCertificationRecord,
    TransitionCertificationRecord,
    UnresolvedDiagnosticVisibilityRecord,
    V45PlanningConstraintRecord,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _state_count(values: Iterable[str]) -> dict[str, int]:
    counts = Counter(values)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_READINESS_TRANSITION_STATES}


def count_phase_evidence_states(records: Iterable[PhaseEvidenceReference]) -> dict[str, int]:
    phase_records = tuple(records)
    return _state_count(
        state
        for record in phase_records
        for state in (
            record.readiness_state,
            record.transition_state,
            record.completeness_state,
            record.certification_state,
        )
    )


def count_readiness_states(records: Iterable[ReadinessCertificationRecord]) -> dict[str, int]:
    readiness_records = tuple(records)
    return _state_count(
        state
        for record in readiness_records
        for state in (record.readiness_state, record.certification_state)
    )


def count_transition_states(records: Iterable[TransitionCertificationRecord]) -> dict[str, int]:
    transition_records = tuple(records)
    return _state_count(
        state
        for record in transition_records
        for state in (record.transition_state, record.certification_state)
    )


def count_completeness_states(records: Iterable[CompletenessSummaryRecord]) -> dict[str, int]:
    completeness_records = tuple(records)
    return _state_count(
        state
        for record in completeness_records
        for state in (record.completeness_state, record.certification_state)
    )


def count_diagnostic_states(records: Iterable[UnresolvedDiagnosticVisibilityRecord]) -> dict[str, int]:
    return _state_count(record.diagnostic_state for record in records)


def count_limitation_states(records: Iterable[LimitationVisibilityRecord]) -> dict[str, int]:
    return _state_count(record.limitation_state for record in records)


def count_blocker_warning_states(records: Iterable[BlockerWarningVisibilityRecord]) -> dict[str, int]:
    return _state_count(record.finding_state for record in records)


def count_planning_constraint_states(records: Iterable[V45PlanningConstraintRecord]) -> dict[str, int]:
    return _state_count(record.constraint_state for record in records)


def count_combined_readiness_transition_states(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, int]:
    states: list[str] = [
        certification.completeness_identity.completeness_state,
        certification.completeness_identity.certification_state,
        certification.provenance_record.provenance_state,
        certification.lineage_record.lineage_state,
        certification.replay_rollback_record.replay_state,
        certification.replay_rollback_record.rollback_state,
    ]
    for record in certification.phase_evidence_references:
        states.extend(
            (
                record.readiness_state,
                record.transition_state,
                record.completeness_state,
                record.certification_state,
            )
        )
    for record in certification.readiness_records:
        states.extend((record.readiness_state, record.certification_state))
    for record in certification.transition_records:
        states.extend((record.transition_state, record.certification_state))
    for record in certification.completeness_records:
        states.extend((record.completeness_state, record.certification_state))
    states.extend(record.diagnostic_state for record in certification.diagnostic_records)
    states.extend(record.limitation_state for record in certification.limitation_records)
    states.extend(record.finding_state for record in certification.blocker_warning_records)
    states.extend(record.constraint_state for record in certification.planning_constraint_records)
    states.extend(
        record.preparation_state for record in certification.drift_integrity_preparation_records
    )
    states.extend(
        record.certification_state for record in certification.non_operational_certifications
    )
    for record in certification.transition_summaries:
        states.extend(
            (
                record.readiness_state,
                record.transition_state,
                record.completeness_state,
                record.certification_state,
            )
        )
    return _state_count(states)


def v4_4_readiness_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    records = tuple(certification.readiness_records)
    counts = count_readiness_states(records)
    return {
        "v4_4_readiness_certification_count": len(records),
        "readiness_ids": _ordered_ids(record.readiness_id for record in records),
        "readiness_state_counts": counts,
        "ready_for_closeout_count": counts[READINESS_STATE_READY_FOR_CLOSEOUT],
        "ready_with_warnings_count": counts[READINESS_STATE_READY_WITH_WARNINGS],
        "not_ready_count": counts[READINESS_STATE_NOT_READY],
        "fail_visible_readiness_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "runtime_readiness_inferred_count": sum(
            1 for record in records if record.runtime_readiness_inferred
        ),
        "readiness_authorization_enabled_count": sum(
            1 for record in records if record.readiness_authorization_enabled
        ),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def v4_5_transition_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    records = tuple(certification.transition_records)
    counts = count_transition_states(records)
    return {
        "v4_5_transition_certification_count": len(records),
        "transition_ids": _ordered_ids(record.transition_id for record in records),
        "transition_state_counts": counts,
        "transition_ready_count": counts[READINESS_STATE_TRANSITION_READY],
        "transition_ready_with_warnings_count": counts[
            READINESS_STATE_TRANSITION_READY_WITH_WARNINGS
        ],
        "transition_blocked_count": counts[READINESS_STATE_TRANSITION_BLOCKED],
        "fail_visible_transition_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "transition_approval_enabled_count": sum(
            1 for record in records if record.transition_approval_enabled
        ),
        "v4_5_activation_enabled_count": sum(
            1 for record in records if record.v4_5_activation_enabled
        ),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
        "planner_integration_enabled_count": sum(
            1 for record in records if record.planner_integration_enabled
        ),
    }


def phase_chain_completeness_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    phase_records = tuple(certification.phase_evidence_references)
    completeness_records = tuple(certification.completeness_records)
    counts = count_completeness_states(completeness_records)
    return {
        "phase_chain_id": certification.completeness_identity.phase_chain_id,
        "phase_chain_completeness_state": certification.completeness_identity.completeness_state,
        "phase_ids": _ordered_ids(certification.completeness_identity.phase_ids),
        "phase_evidence_reference_count": len(phase_records),
        "phase_chain_completeness_count": len(completeness_records),
        "phase_evidence_ids": _ordered_ids(record.evidence_id for record in phase_records),
        "completeness_ids": _ordered_ids(record.completeness_id for record in completeness_records),
        "completeness_state_counts": counts,
        "complete_count": counts[READINESS_STATE_COMPLETE],
        "fail_visible_completeness_count": sum(
            1 for record in completeness_records if record.fail_visible
        ),
        "descriptive_only": all(record.descriptive_only for record in completeness_records),
        "runtime_activation_enabled_count": sum(
            1 for record in completeness_records if record.runtime_activation_enabled
        ),
        "phase_production_consumption_enabled_count": sum(
            1 for record in phase_records if record.production_consumption_enabled
        ),
    }


def unresolved_diagnostic_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    records = tuple(certification.diagnostic_records)
    state_counts = count_diagnostic_states(records)
    severity_counts = Counter(record.severity for record in records)
    return {
        "unresolved_diagnostic_count": sum(1 for record in records if record.unresolved),
        "diagnostic_record_count": len(records),
        "diagnostic_ids": _ordered_ids(record.diagnostic_id for record in records),
        "diagnostic_state_counts": state_counts,
        "severity_counts": {
            severity: int(severity_counts[severity]) for severity in sorted(severity_counts)
        },
        "fail_visible_diagnostic_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(
            1 for record in records if record.automatic_repair_enabled
        ),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def limitation_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    records = tuple(certification.limitation_records)
    counts = count_limitation_states(records)
    return {
        "limitation_count": len(records),
        "limitation_ids": _ordered_ids(record.limitation_id for record in records),
        "limitation_state_counts": counts,
        "inherited_limitation_count": sum(1 for record in records if record.inherited_by_v4_5),
        "fail_visible_limitation_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
    }


def blocker_warning_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    records = tuple(certification.blocker_warning_records)
    state_counts = count_blocker_warning_states(records)
    severity_counts = Counter(record.severity for record in records)
    return {
        "finding_count": len(records),
        "finding_ids": _ordered_ids(record.finding_id for record in records),
        "finding_state_counts": state_counts,
        "severity_counts": {
            severity: int(severity_counts[severity]) for severity in sorted(severity_counts)
        },
        "warning_count": int(severity_counts["warning"]),
        "blocker_count": int(severity_counts["blocker"]),
        "fail_visible_finding_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "approval_enabled_count": sum(1 for record in records if record.approval_enabled),
        "activation_enabled_count": sum(1 for record in records if record.activation_enabled),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def inherited_constraint_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    records = tuple(certification.planning_constraint_records)
    counts = count_planning_constraint_states(records)
    return {
        "inherited_v4_5_constraint_count": sum(1 for record in records if record.inherited_by_v4_5),
        "inherited_v4_5_prohibition_count": sum(1 for record in records if record.is_prohibition),
        "constraint_ids": _ordered_ids(record.constraint_id for record in records),
        "constraint_state_counts": counts,
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


def inherited_prohibition_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> list[dict[str, Any]]:
    return [
        {
            "constraint_id": record.constraint_id,
            "constraint_state": record.constraint_state,
            "constraint_type": record.constraint_type,
            "inherited_from_phase_ids": _ordered_ids(record.inherited_from_phase_ids),
            "is_prohibition": record.is_prohibition,
            "v4_5_activation_enabled": record.v4_5_activation_enabled,
        }
        for record in sorted(
            (item for item in certification.planning_constraint_records if item.is_prohibition),
            key=lambda item: (item.deterministic_order, item.constraint_id),
        )
    ]


def drift_integrity_preparation_summaries(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    records = tuple(certification.drift_integrity_preparation_records)
    counts = _state_count(record.preparation_state for record in records)
    return {
        "drift_integrity_preparation_count": len(records),
        "preparation_ids": _ordered_ids(record.preparation_id for record in records),
        "preparation_state_counts": counts,
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "runtime_activation_enabled_count": sum(
            1 for record in records if record.runtime_activation_enabled
        ),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def provenance_continuity_visibility(
    certification: BoundaryReadinessTransitionCertification,
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
    certification: BoundaryReadinessTransitionCertification,
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


def governance_safe_readiness_explainability(
    certification: BoundaryReadinessTransitionCertification,
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


def validate_required_readiness_transition_visibility(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    counts = count_combined_readiness_transition_states(certification)
    missing_states = [state for state in BOUNDARY_READINESS_TRANSITION_STATES if counts[state] <= 0]
    fail_visible_missing = [
        state for state in FAIL_VISIBLE_READINESS_TRANSITION_STATES if counts[state] <= 0
    ]
    return {
        "valid": not missing_states and not fail_visible_missing,
        "combined_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": fail_visible_missing,
    }
