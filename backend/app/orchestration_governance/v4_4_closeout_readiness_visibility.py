"""Visibility helpers for v4.4 closeout and v4.5 readiness certification."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_closeout_readiness_models import (
    BOUNDARY_CLOSEOUT_READINESS_STATES,
    CLOSEOUT_STATE_CERTIFIED,
    CLOSEOUT_STATE_CLOSED_OUT,
    CLOSEOUT_STATE_CLOSED_OUT_WITH_LIMITATIONS,
    CLOSEOUT_STATE_CLOSED_OUT_WITH_WARNINGS,
    CLOSEOUT_STATE_CLOSEOUT_BLOCKED,
    CLOSEOUT_STATE_INHERITED,
    CLOSEOUT_STATE_INFORMATIONAL,
    CLOSEOUT_STATE_PARTIALLY_CERTIFIED,
    CLOSEOUT_STATE_PRESERVED,
    CLOSEOUT_STATE_PROHIBITED,
    CLOSEOUT_STATE_RESOLVED,
    CLOSEOUT_STATE_V4_5_PLANNING_BLOCKED,
    CLOSEOUT_STATE_V4_5_PLANNING_READY,
    CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_LIMITATIONS,
    CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_WARNINGS,
    CLOSEOUT_STATE_WARNING,
    FAIL_VISIBLE_CLOSEOUT_READINESS_STATES,
    CloseoutCertificationRecord,
    CloseoutInheritedConstraintRecord,
    CloseoutInheritedProhibitionRecord,
    CloseoutReadinessSummaryRecord,
    NonOperationalCloseoutCertificationRecord,
    PhaseChainEvidenceRecord,
    PreservedBlockerRecord,
    PreservedLimitationRecord,
    PreservedWarningRecord,
    V44CloseoutAndV45ReadinessCertification,
    V45InheritedLimitationRecord,
    V45PlanningBoundaryRecord,
    V45ReadinessCertificationRecord,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _state_count(values: Iterable[str]) -> dict[str, int]:
    counts = Counter(values)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_CLOSEOUT_READINESS_STATES}


def count_phase_chain_evidence_states(
    records: Iterable[PhaseChainEvidenceRecord],
) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (
            record.report_state,
            record.migration_doc_state,
            record.validation_state,
            record.certification_state,
        )
    )


def count_closeout_record_states(records: Iterable[CloseoutCertificationRecord]) -> dict[str, int]:
    return _state_count(
        state for record in records for state in (record.closeout_state, record.certification_state)
    )


def count_readiness_record_states(
    records: Iterable[V45ReadinessCertificationRecord],
) -> dict[str, int]:
    return _state_count(
        state for record in records for state in (record.readiness_state, record.certification_state)
    )


def count_preserved_limitation_states(
    records: Iterable[PreservedLimitationRecord],
) -> dict[str, int]:
    return _state_count(
        state for record in records for state in (record.limitation_state, record.preservation_state)
    )


def count_preserved_blocker_states(records: Iterable[PreservedBlockerRecord]) -> dict[str, int]:
    return _state_count(
        state for record in records for state in (record.blocker_state, record.preservation_state)
    )


def count_preserved_warning_states(records: Iterable[PreservedWarningRecord]) -> dict[str, int]:
    return _state_count(
        state for record in records for state in (record.warning_state, record.preservation_state)
    )


def count_inherited_prohibition_states(
    records: Iterable[CloseoutInheritedProhibitionRecord],
) -> dict[str, int]:
    return _state_count(record.prohibition_state for record in records)


def count_inherited_constraint_states(
    records: Iterable[CloseoutInheritedConstraintRecord],
) -> dict[str, int]:
    return _state_count(record.constraint_state for record in records)


def count_planning_boundary_states(records: Iterable[V45PlanningBoundaryRecord]) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (record.planning_boundary_state, record.readiness_state)
    )


def count_inherited_limitation_states(
    records: Iterable[V45InheritedLimitationRecord],
) -> dict[str, int]:
    return _state_count(
        state for record in records for state in (record.limitation_state, record.inherited_state)
    )


def count_non_operational_states(
    records: Iterable[NonOperationalCloseoutCertificationRecord],
) -> dict[str, int]:
    return _state_count(record.certification_state for record in records)


def count_summary_states(records: Iterable[CloseoutReadinessSummaryRecord]) -> dict[str, int]:
    return _state_count(
        state
        for record in records
        for state in (
            record.closeout_state,
            record.readiness_state,
            record.certification_state,
            record.limitation_state,
            record.warning_state,
        )
    )


def count_combined_closeout_readiness_states(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, int]:
    states: list[str] = [
        certification.phase_chain_identity.phase_chain_state,
        certification.phase_chain_identity.certification_state,
        certification.provenance_record.provenance_state,
        certification.lineage_record.lineage_state,
        certification.replay_rollback_record.replay_state,
        certification.replay_rollback_record.rollback_state,
        certification.closeout_classification,
        certification.v4_5_readiness_classification,
    ]
    for record in certification.phase_chain_evidence_records:
        states.extend(
            (
                record.report_state,
                record.migration_doc_state,
                record.validation_state,
                record.certification_state,
            )
        )
    for record in certification.closeout_records:
        states.extend((record.closeout_state, record.certification_state))
    for record in certification.readiness_records:
        states.extend((record.readiness_state, record.certification_state))
    for record in certification.preserved_limitation_records:
        states.extend((record.limitation_state, record.preservation_state))
    for record in certification.preserved_blocker_records:
        states.extend((record.blocker_state, record.preservation_state))
    for record in certification.preserved_warning_records:
        states.extend((record.warning_state, record.preservation_state))
    states.extend(record.prohibition_state for record in certification.inherited_prohibition_records)
    states.extend(record.constraint_state for record in certification.inherited_constraint_records)
    for record in certification.planning_boundary_records:
        states.extend((record.planning_boundary_state, record.readiness_state))
    for record in certification.inherited_limitation_records:
        states.extend((record.limitation_state, record.inherited_state))
    states.extend(
        record.certification_state for record in certification.non_operational_certifications
    )
    for record in certification.closeout_readiness_summaries:
        states.extend(
            (
                record.closeout_state,
                record.readiness_state,
                record.certification_state,
                record.limitation_state,
                record.warning_state,
            )
        )
    return _state_count(states)


def phase_chain_evidence_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.phase_chain_evidence_records)
    counts = count_phase_chain_evidence_states(records)
    return {
        "phase_chain_id": certification.phase_chain_identity.phase_chain_evidence_id,
        "phase_chain_evidence_reference_count": len(records),
        "phase_evidence_coverage_count": sum(1 for record in records if record.validation_covered),
        "generated_report_coverage_count": sum(1 for record in records if record.report_available),
        "migration_doc_coverage_count": sum(1 for record in records if record.migration_doc_available),
        "phase_ids": _ordered_ids(record.phase_id for record in records),
        "report_references": _ordered_ids(record.report_reference for record in records),
        "migration_doc_references": _ordered_ids(record.migration_doc_reference for record in records),
        "test_references": _ordered_ids(record.test_reference for record in records),
        "phase_chain_state_counts": counts,
        "certified_count": counts[CLOSEOUT_STATE_CERTIFIED],
        "partially_certified_count": counts[CLOSEOUT_STATE_PARTIALLY_CERTIFIED],
        "fail_visible_phase_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
    }


def v4_4_closeout_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.closeout_records)
    counts = count_closeout_record_states(records)
    return {
        "v4_4_closeout_certification_count": len(records),
        "closeout_ids": _ordered_ids(record.closeout_id for record in records),
        "closeout_state_counts": counts,
        "closed_out_count": counts[CLOSEOUT_STATE_CLOSED_OUT],
        "closed_out_with_limitations_count": counts[CLOSEOUT_STATE_CLOSED_OUT_WITH_LIMITATIONS],
        "closed_out_with_warnings_count": counts[CLOSEOUT_STATE_CLOSED_OUT_WITH_WARNINGS],
        "closeout_blocked_count": counts[CLOSEOUT_STATE_CLOSEOUT_BLOCKED],
        "fail_visible_closeout_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "closeout_authorization_enabled_count": sum(
            1 for record in records if record.closeout_authorization_enabled
        ),
        "activation_enabled_count": sum(1 for record in records if record.activation_enabled),
        "runtime_readiness_inferred_count": sum(
            1 for record in records if record.runtime_readiness_inferred
        ),
        "closeout_classification": certification.closeout_classification,
    }


def v4_5_readiness_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.readiness_records)
    counts = count_readiness_record_states(records)
    return {
        "v4_5_readiness_certification_count": len(records),
        "readiness_ids": _ordered_ids(record.readiness_id for record in records),
        "readiness_state_counts": counts,
        "v4_5_planning_ready_count": counts[CLOSEOUT_STATE_V4_5_PLANNING_READY],
        "v4_5_planning_ready_with_limitations_count": counts[
            CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_LIMITATIONS
        ],
        "v4_5_planning_ready_with_warnings_count": counts[
            CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_WARNINGS
        ],
        "v4_5_planning_blocked_count": counts[CLOSEOUT_STATE_V4_5_PLANNING_BLOCKED],
        "fail_visible_readiness_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "readiness_activation_enabled_count": sum(
            1 for record in records if record.readiness_activation_enabled
        ),
        "v4_5_runtime_behavior_enabled_count": sum(
            1 for record in records if record.v4_5_runtime_behavior_enabled
        ),
        "planner_integration_enabled_count": sum(
            1 for record in records if record.planner_integration_enabled
        ),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "runtime_readiness_inferred_count": sum(
            1 for record in records if record.runtime_readiness_inferred
        ),
        "v4_5_readiness_classification": certification.v4_5_readiness_classification,
    }


def preserved_limitation_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.preserved_limitation_records)
    counts = count_preserved_limitation_states(records)
    return {
        "preserved_limitation_count": len(records),
        "limitation_ids": _ordered_ids(record.limitation_id for record in records),
        "limitation_state_counts": counts,
        "preserved_count": counts[CLOSEOUT_STATE_PRESERVED],
        "inherited_by_v4_5_count": sum(1 for record in records if record.inherited_by_v4_5),
        "fail_visible_limitation_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(
            1 for record in records if record.automatic_repair_enabled
        ),
    }


def preserved_blocker_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.preserved_blocker_records)
    counts = count_preserved_blocker_states(records)
    severity_counts = Counter(record.severity for record in records)
    return {
        "preserved_blocker_count": len(records),
        "blocker_ids": _ordered_ids(record.blocker_id for record in records),
        "blocker_state_counts": counts,
        "blocker_severity_counts": {
            severity: int(severity_counts[severity]) for severity in sorted(severity_counts)
        },
        "resolved_count": counts[CLOSEOUT_STATE_RESOLVED],
        "preserved_count": counts[CLOSEOUT_STATE_PRESERVED],
        "fail_visible_blocker_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "blocker_authorization_enabled_count": sum(
            1 for record in records if record.blocker_authorization_enabled
        ),
        "approval_enabled_count": sum(1 for record in records if record.approval_enabled),
        "activation_enabled_count": sum(1 for record in records if record.activation_enabled),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def preserved_warning_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.preserved_warning_records)
    counts = count_preserved_warning_states(records)
    severity_counts = Counter(record.severity for record in records)
    return {
        "preserved_warning_count": len(records),
        "warning_ids": _ordered_ids(record.warning_id for record in records),
        "warning_state_counts": counts,
        "warning_severity_counts": {
            severity: int(severity_counts[severity]) for severity in sorted(severity_counts)
        },
        "warning_count": int(severity_counts[CLOSEOUT_STATE_WARNING]),
        "informational_count": int(severity_counts[CLOSEOUT_STATE_INFORMATIONAL]),
        "preserved_count": counts[CLOSEOUT_STATE_PRESERVED],
        "fail_visible_warning_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "warning_suppression_enabled_count": sum(
            1 for record in records if record.warning_suppression_enabled
        ),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def inherited_prohibition_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.inherited_prohibition_records)
    counts = count_inherited_prohibition_states(records)
    return {
        "inherited_prohibition_count": len(records),
        "prohibition_ids": _ordered_ids(record.prohibition_id for record in records),
        "prohibition_state_counts": counts,
        "is_prohibition_count": sum(1 for record in records if record.is_prohibition),
        "fail_visible_prohibition_count": sum(1 for record in records if record.fail_visible),
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
        "v4_5_runtime_behavior_enabled_count": sum(
            1 for record in records if record.v4_5_runtime_behavior_enabled
        ),
    }


def inherited_constraint_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.inherited_constraint_records)
    counts = count_inherited_constraint_states(records)
    return {
        "inherited_constraint_count": len(records),
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
        "readiness_activation_enabled_count": sum(
            1 for record in records if record.readiness_activation_enabled
        ),
        "v4_5_runtime_behavior_enabled_count": sum(
            1 for record in records if record.v4_5_runtime_behavior_enabled
        ),
    }


def v4_5_planning_boundary_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.planning_boundary_records)
    counts = count_planning_boundary_states(records)
    return {
        "planning_boundary_count": len(records),
        "planning_boundary_ids": _ordered_ids(
            record.planning_boundary_id for record in records
        ),
        "planning_boundary_state_counts": counts,
        "required_evidence_input_count": sum(
            len(record.required_evidence_inputs) for record in records
        ),
        "expected_certification_need_count": sum(
            len(record.expected_certification_needs) for record in records
        ),
        "v4_5_planning_ready_with_limitations_count": counts[
            CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_LIMITATIONS
        ],
        "v4_5_planning_blocked_count": counts[CLOSEOUT_STATE_V4_5_PLANNING_BLOCKED],
        "fail_visible_planning_boundary_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "readiness_activation_enabled_count": sum(
            1 for record in records if record.readiness_activation_enabled
        ),
        "v4_5_runtime_behavior_enabled_count": sum(
            1 for record in records if record.v4_5_runtime_behavior_enabled
        ),
        "planner_integration_enabled_count": sum(
            1 for record in records if record.planner_integration_enabled
        ),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
    }


def v4_5_inherited_limitation_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.inherited_limitation_records)
    counts = count_inherited_limitation_states(records)
    return {
        "v4_5_inherited_limitation_count": len(records),
        "inherited_limitation_ids": _ordered_ids(
            record.inherited_limitation_id for record in records
        ),
        "inherited_limitation_state_counts": counts,
        "inherited_count": counts[CLOSEOUT_STATE_INHERITED],
        "preserved_count": counts[CLOSEOUT_STATE_PRESERVED],
        "fail_visible_inherited_limitation_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "readiness_activation_enabled_count": sum(
            1 for record in records if record.readiness_activation_enabled
        ),
    }


def non_operational_certification_summaries(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.non_operational_certifications)
    counts = count_non_operational_states(records)
    return {
        "non_operational_certification_count": len(records),
        "certification_ids": _ordered_ids(record.certification_id for record in records),
        "certification_state_counts": counts,
        "certified_count": counts[CLOSEOUT_STATE_CERTIFIED],
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
        "dispatch_execution_enabled_count": sum(
            1 for record in records if record.dispatch_execution_enabled
        ),
        "routing_execution_enabled_count": sum(
            1 for record in records if record.routing_execution_enabled
        ),
        "scheduling_execution_enabled_count": sum(
            1 for record in records if record.scheduling_execution_enabled
        ),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "closeout_authorization_enabled_count": sum(
            1 for record in records if record.closeout_authorization_enabled
        ),
        "readiness_activation_enabled_count": sum(
            1 for record in records if record.readiness_activation_enabled
        ),
        "v4_5_runtime_behavior_enabled_count": sum(
            1 for record in records if record.v4_5_runtime_behavior_enabled
        ),
        "operational_mutation_enabled_count": sum(
            1 for record in records if record.operational_mutation_enabled
        ),
    }


def closeout_readiness_summary_visibility(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    records = tuple(certification.closeout_readiness_summaries)
    counts = count_summary_states(records)
    return {
        "summary_count": len(records),
        "summary_ids": _ordered_ids(record.summary_id for record in records),
        "summary_state_counts": counts,
        "closed_out_with_limitations_count": counts[CLOSEOUT_STATE_CLOSED_OUT_WITH_LIMITATIONS],
        "v4_5_planning_ready_with_limitations_count": counts[
            CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_LIMITATIONS
        ],
        "warning_count": counts[CLOSEOUT_STATE_WARNING],
        "informational_count": counts[CLOSEOUT_STATE_INFORMATIONAL],
        "descriptive_only": all(record.descriptive_only for record in records),
        "planning_only": all(record.planning_only for record in records),
        "non_operational": all(record.non_operational for record in records),
        "closeout_authorization_signal_enabled_count": sum(
            1 for record in records if record.closeout_authorization_signal_enabled
        ),
        "readiness_activation_signal_enabled_count": sum(
            1 for record in records if record.readiness_activation_signal_enabled
        ),
        "runtime_readiness_inferred_count": sum(
            1 for record in records if record.runtime_readiness_inferred
        ),
    }


def provenance_continuity_visibility(
    certification: V44CloseoutAndV45ReadinessCertification,
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
    certification: V44CloseoutAndV45ReadinessCertification,
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
    certification: V44CloseoutAndV45ReadinessCertification,
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
        "closeout_classification": certification.closeout_classification,
        "v4_5_readiness_classification": certification.v4_5_readiness_classification,
        "explicit_limitation_count": len(certification.explicit_limitations),
        "explicit_prohibition_count": len(certification.explicit_prohibitions),
    }


def validate_required_closeout_readiness_visibility(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    counts = count_combined_closeout_readiness_states(certification)
    missing_states = [state for state in BOUNDARY_CLOSEOUT_READINESS_STATES if counts[state] <= 0]
    missing_fail_visible_states = [
        state for state in FAIL_VISIBLE_CLOSEOUT_READINESS_STATES if counts[state] <= 0
    ]
    return {
        "valid": not missing_states and not missing_fail_visible_states,
        "combined_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": missing_fail_visible_states,
    }
