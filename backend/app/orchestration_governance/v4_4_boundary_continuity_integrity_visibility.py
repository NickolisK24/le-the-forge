"""Visibility helpers for v4.4 boundary continuity and integrity certification."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_boundary_continuity_integrity_models import (
    BOUNDARY_CONTINUITY_INTEGRITY_STATES,
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_CONTINUOUS,
    CERTIFICATION_STATE_DISCONTINUOUS,
    CERTIFICATION_STATE_INTEGRITY_BLOCKED,
    CERTIFICATION_STATE_INTEGRITY_SAFE,
    CERTIFICATION_STATE_INTEGRITY_WARNING,
    CERTIFICATION_STATE_LINEAGE_SAFE,
    CERTIFICATION_STATE_PARTIALLY_CERTIFIED,
    CERTIFICATION_STATE_PROVENANCE_SAFE,
    CERTIFICATION_STATE_REPLAY_SAFE,
    CERTIFICATION_STATE_ROLLBACK_SAFE,
    CERTIFICATION_STATE_UNCERTIFIED,
    FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES,
    BoundaryContinuityIntegrityCertification,
    CertificationDiagnosticRecord,
    CertificationLimitationRecord,
    CertificationSummaryRecord,
    ContinuityCertificationRecord,
    IntegrityCertificationRecord,
    PhaseEvidenceReference,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _state_count(values: Iterable[str]) -> dict[str, int]:
    counts = Counter(values)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_CONTINUITY_INTEGRITY_STATES}


def count_phase_evidence_states(records: Iterable[PhaseEvidenceReference]) -> dict[str, int]:
    phase_records = tuple(records)
    return _state_count(
        state
        for record in phase_records
        for state in (
            record.certification_state,
            record.continuity_state,
            record.integrity_state,
        )
    )


def count_continuity_record_states(
    records: Iterable[ContinuityCertificationRecord],
) -> dict[str, int]:
    continuity_records = tuple(records)
    return _state_count(
        state
        for record in continuity_records
        for state in (record.continuity_state, record.certification_state)
    )


def count_integrity_record_states(records: Iterable[IntegrityCertificationRecord]) -> dict[str, int]:
    integrity_records = tuple(records)
    return _state_count(
        state
        for record in integrity_records
        for state in (record.integrity_state, record.certification_state)
    )


def count_limitation_states(records: Iterable[CertificationLimitationRecord]) -> dict[str, int]:
    return _state_count(record.limitation_state for record in records)


def count_diagnostic_states(records: Iterable[CertificationDiagnosticRecord]) -> dict[str, int]:
    return _state_count(record.diagnostic_state for record in records)


def count_summary_states(records: Iterable[CertificationSummaryRecord]) -> dict[str, int]:
    summary_records = tuple(records)
    return _state_count(
        state
        for record in summary_records
        for state in (
            record.certification_state,
            record.continuity_state,
            record.integrity_state,
        )
    )


def count_combined_continuity_integrity_states(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, int]:
    states: list[str] = [certification.phase_chain_identity.phase_chain_state]
    for record in certification.phase_evidence_references:
        states.extend(
            (record.certification_state, record.continuity_state, record.integrity_state)
        )
    for record in certification.continuity_records:
        states.extend((record.continuity_state, record.certification_state))
    for record in certification.integrity_records:
        states.extend((record.integrity_state, record.certification_state))
    states.extend(record.limitation_state for record in certification.limitation_records)
    states.extend(record.diagnostic_state for record in certification.diagnostic_records)
    states.append(certification.provenance_record.provenance_state)
    states.append(certification.lineage_record.lineage_state)
    states.append(certification.replay_rollback_record.replay_state)
    states.append(certification.replay_rollback_record.rollback_state)
    for record in certification.certification_summaries:
        states.extend(
            (record.certification_state, record.continuity_state, record.integrity_state)
        )
    return _state_count(states)


def phase_chain_certification_summaries(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    phase_chain = certification.phase_chain_identity
    records = tuple(certification.phase_evidence_references)
    counts = count_phase_evidence_states(records)
    return {
        "phase_chain_id": phase_chain.phase_chain_id,
        "phase_chain_state": phase_chain.phase_chain_state,
        "phase_ids": _ordered_ids(phase_chain.phase_ids),
        "phase_evidence_reference_count": len(records),
        "phase_evidence_ids": _ordered_ids(record.evidence_id for record in records),
        "phase_evidence_state_counts": counts,
        "fail_visible_phase_evidence_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
        "runtime_activation_enabled": phase_chain.runtime_activation_enabled,
    }


def continuity_status_totals(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    records = tuple(certification.continuity_records)
    counts = count_continuity_record_states(records)
    return {
        "continuity_certification_record_count": len(records),
        "continuity_ids": _ordered_ids(record.continuity_id for record in records),
        "continuity_state_counts": counts,
        "continuous_count": counts[CERTIFICATION_STATE_CONTINUOUS],
        "discontinuous_count": counts[CERTIFICATION_STATE_DISCONTINUOUS],
        "replay_safe_count": counts[CERTIFICATION_STATE_REPLAY_SAFE],
        "rollback_safe_count": counts[CERTIFICATION_STATE_ROLLBACK_SAFE],
        "provenance_safe_count": counts[CERTIFICATION_STATE_PROVENANCE_SAFE],
        "lineage_safe_count": counts[CERTIFICATION_STATE_LINEAGE_SAFE],
        "fail_visible_continuity_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "runtime_activation_enabled_count": sum(
            1 for record in records if record.runtime_activation_enabled
        ),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
    }


def integrity_status_totals(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    records = tuple(certification.integrity_records)
    counts = count_integrity_record_states(records)
    return {
        "integrity_certification_record_count": len(records),
        "integrity_ids": _ordered_ids(record.integrity_id for record in records),
        "integrity_state_counts": counts,
        "integrity_safe_count": counts[CERTIFICATION_STATE_INTEGRITY_SAFE],
        "integrity_warning_count": counts[CERTIFICATION_STATE_INTEGRITY_WARNING],
        "integrity_blocked_count": counts[CERTIFICATION_STATE_INTEGRITY_BLOCKED],
        "fail_visible_integrity_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "certification_authorization_enabled_count": sum(
            1 for record in records if record.certification_authorization_enabled
        ),
        "integrity_approval_enabled_count": sum(
            1 for record in records if record.integrity_approval_enabled
        ),
        "production_readiness_inferred_count": sum(
            1 for record in records if record.production_readiness_inferred
        ),
        "planner_integration_enabled_count": sum(
            1 for record in records if record.planner_integration_enabled
        ),
    }


def certification_limitation_summaries(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    records = tuple(certification.limitation_records)
    counts = count_limitation_states(records)
    return {
        "limitation_count": len(records),
        "limitation_ids": _ordered_ids(record.limitation_id for record in records),
        "limitation_state_counts": counts,
        "fail_visible_limitation_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(
            1 for record in records if record.automatic_repair_enabled
        ),
    }


def fail_visible_certification_diagnostics(
    certification: BoundaryContinuityIntegrityCertification,
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "subject_id": record.subject_id,
            "diagnostic_state": record.diagnostic_state,
            "severity": record.severity,
            "fail_visible": record.fail_visible,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
        }
        for record in sorted(
            (
                item
                for item in certification.diagnostic_records
                if item.diagnostic_state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES
            ),
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def certification_diagnostic_summaries(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    records = tuple(certification.diagnostic_records)
    state_counts = count_diagnostic_states(records)
    severity_counts = Counter(record.severity for record in records)
    return {
        "diagnostic_record_count": len(records),
        "diagnostic_ids": _ordered_ids(record.diagnostic_id for record in records),
        "diagnostic_state_counts": state_counts,
        "severity_counts": {
            severity: int(severity_counts[severity]) for severity in sorted(severity_counts)
        },
        "fail_visible_diagnostic_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "authorization_enabled_count": sum(1 for record in records if record.authorization_enabled),
        "approval_enabled_count": sum(1 for record in records if record.approval_enabled),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(
            1 for record in records if record.automatic_repair_enabled
        ),
    }


def certification_summary_visibility(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    records = tuple(certification.certification_summaries)
    counts = count_summary_states(records)
    return {
        "certification_summary_count": len(records),
        "summary_ids": _ordered_ids(record.summary_id for record in records),
        "summary_state_counts": counts,
        "certified_count": counts[CERTIFICATION_STATE_CERTIFIED],
        "partially_certified_count": counts[CERTIFICATION_STATE_PARTIALLY_CERTIFIED],
        "uncertified_count": counts[CERTIFICATION_STATE_UNCERTIFIED],
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_operational": all(record.non_operational for record in records),
        "authorization_signal_enabled_count": sum(
            1 for record in records if record.authorization_signal_enabled
        ),
        "production_readiness_signal_enabled_count": sum(
            1 for record in records if record.production_readiness_signal_enabled
        ),
        "runtime_activation_signal_enabled_count": sum(
            1 for record in records if record.runtime_activation_signal_enabled
        ),
    }


def replay_rollback_safety_visibility(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    record = certification.replay_rollback_record
    return {
        "safety_id": record.safety_id,
        "phase_evidence_ids": _ordered_ids(record.phase_evidence_ids),
        "replay_evidence_ids": _ordered_ids(record.replay_evidence_ids),
        "rollback_evidence_ids": _ordered_ids(record.rollback_evidence_ids),
        "replay_state": record.replay_state,
        "rollback_state": record.rollback_state,
        "replay_safe": record.replay_safe,
        "rollback_safe": record.rollback_safe,
        "runtime_mutation_enabled": record.runtime_mutation_enabled,
        "operational_mutation_enabled": record.operational_mutation_enabled,
    }


def provenance_continuity_visibility(
    certification: BoundaryContinuityIntegrityCertification,
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
    certification: BoundaryContinuityIntegrityCertification,
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


def governance_safe_certification_explainability(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    return {
        "descriptive_only": certification.descriptive_only,
        "non_operational": certification.non_operational,
        "non_authoritative": certification.non_authoritative,
        "non_authorizing": certification.non_authorizing,
        "non_approving": certification.non_approving,
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


def validate_required_continuity_integrity_visibility(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    counts = count_combined_continuity_integrity_states(certification)
    missing_states = [state for state in BOUNDARY_CONTINUITY_INTEGRITY_STATES if counts[state] <= 0]
    fail_visible_missing = [
        state for state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES if counts[state] <= 0
    ]
    return {
        "valid": not missing_states and not fail_visible_missing,
        "combined_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": fail_visible_missing,
    }
