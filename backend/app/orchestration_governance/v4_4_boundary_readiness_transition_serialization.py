"""Deterministic serialization for v4.4 boundary readiness transition."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_boundary_readiness_transition_models import (
    BlockerWarningVisibilityRecord,
    BoundaryReadinessCertificationIdentity,
    BoundaryReadinessTransitionCertification,
    CompletenessSummaryRecord,
    LimitationVisibilityRecord,
    NonOperationalCertificationRecord,
    PhaseChainCompletenessIdentity,
    PhaseEvidenceReference,
    ReadinessCertificationRecord,
    ReadinessLineageContinuityRecord,
    ReadinessProvenanceContinuityRecord,
    ReadinessReplayRollbackEvidenceRecord,
    TransitionCertificationRecord,
    TransitionSummaryRecord,
    UnresolvedDiagnosticVisibilityRecord,
    V45DriftIntegrityPreparationRecord,
    V45PlanningConstraintRecord,
    V45TransitionCertificationIdentity,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_boundary_readiness_transition_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_boundary_readiness_transition_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_boundary_readiness_transition_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_boundary_readiness_transition_evidence(value) for value in payload]
    return payload


def stable_serialize_boundary_readiness_transition(payload: Any) -> str:
    return json.dumps(
        canonicalize_boundary_readiness_transition_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_readiness_certification_identity(
    identity: BoundaryReadinessCertificationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_transition_certification_identity(
    identity: V45TransitionCertificationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_phase_chain_completeness_identity(
    identity: PhaseChainCompletenessIdentity,
) -> dict[str, Any]:
    data = asdict(identity)
    data["phase_ids"] = _sorted_tuple(data["phase_ids"])
    return data


def export_phase_evidence_reference(record: PhaseEvidenceReference) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_readiness_certification_record(
    record: ReadinessCertificationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_transition_certification_record(
    record: TransitionCertificationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_completeness_summary(record: CompletenessSummaryRecord) -> dict[str, Any]:
    data = asdict(record)
    data["completeness_reference_ids"] = _sorted_tuple(data["completeness_reference_ids"])
    return data


def export_unresolved_diagnostic_visibility(
    record: UnresolvedDiagnosticVisibilityRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_limitation_visibility(record: LimitationVisibilityRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_blocker_warning_visibility(
    record: BlockerWarningVisibilityRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5_planning_constraint(record: V45PlanningConstraintRecord) -> dict[str, Any]:
    data = asdict(record)
    data["inherited_from_phase_ids"] = _sorted_tuple(data["inherited_from_phase_ids"])
    return data


def export_v4_5_drift_integrity_preparation(
    record: V45DriftIntegrityPreparationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["expected_evidence_inputs"] = _sorted_tuple(data["expected_evidence_inputs"])
    return data


def export_non_operational_certification(
    record: NonOperationalCertificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_readiness_provenance_continuity(
    record: ReadinessProvenanceContinuityRecord,
) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("source_reference_ids", "source_hash_references"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_readiness_lineage_continuity(
    record: ReadinessLineageContinuityRecord,
) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("lineage_reference_ids", "lineage_hash_references"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_readiness_replay_rollback_evidence(
    record: ReadinessReplayRollbackEvidenceRecord,
) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("evidence_reference_ids", "replay_evidence_ids", "rollback_evidence_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_transition_summary(record: TransitionSummaryRecord) -> dict[str, Any]:
    data = asdict(record)
    data["summary_reference_ids"] = _sorted_tuple(data["summary_reference_ids"])
    return data


def export_boundary_readiness_transition_certification(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    data = asdict(certification)
    data["readiness_identity"] = export_readiness_certification_identity(
        certification.readiness_identity
    )
    data["transition_identity"] = export_transition_certification_identity(
        certification.transition_identity
    )
    data["completeness_identity"] = export_phase_chain_completeness_identity(
        certification.completeness_identity
    )
    data["phase_evidence_references"] = [
        export_phase_evidence_reference(record)
        for record in sorted(
            certification.phase_evidence_references,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]
    data["readiness_records"] = [
        export_readiness_certification_record(record)
        for record in sorted(
            certification.readiness_records,
            key=lambda item: (item.deterministic_order, item.readiness_id),
        )
    ]
    data["transition_records"] = [
        export_transition_certification_record(record)
        for record in sorted(
            certification.transition_records,
            key=lambda item: (item.deterministic_order, item.transition_id),
        )
    ]
    data["completeness_records"] = [
        export_completeness_summary(record)
        for record in sorted(
            certification.completeness_records,
            key=lambda item: (item.deterministic_order, item.completeness_id),
        )
    ]
    data["diagnostic_records"] = [
        export_unresolved_diagnostic_visibility(record)
        for record in sorted(
            certification.diagnostic_records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["limitation_records"] = [
        export_limitation_visibility(record)
        for record in sorted(
            certification.limitation_records,
            key=lambda item: (item.deterministic_order, item.limitation_id),
        )
    ]
    data["blocker_warning_records"] = [
        export_blocker_warning_visibility(record)
        for record in sorted(
            certification.blocker_warning_records,
            key=lambda item: (item.deterministic_order, item.finding_id),
        )
    ]
    data["planning_constraint_records"] = [
        export_v4_5_planning_constraint(record)
        for record in sorted(
            certification.planning_constraint_records,
            key=lambda item: (item.deterministic_order, item.constraint_id),
        )
    ]
    data["drift_integrity_preparation_records"] = [
        export_v4_5_drift_integrity_preparation(record)
        for record in sorted(
            certification.drift_integrity_preparation_records,
            key=lambda item: (item.deterministic_order, item.preparation_id),
        )
    ]
    data["non_operational_certifications"] = [
        export_non_operational_certification(record)
        for record in sorted(
            certification.non_operational_certifications,
            key=lambda item: (item.deterministic_order, item.certification_id),
        )
    ]
    data["provenance_record"] = export_readiness_provenance_continuity(
        certification.provenance_record
    )
    data["lineage_record"] = export_readiness_lineage_continuity(
        certification.lineage_record
    )
    data["replay_rollback_record"] = export_readiness_replay_rollback_evidence(
        certification.replay_rollback_record
    )
    data["transition_summaries"] = [
        export_transition_summary(record)
        for record in sorted(
            certification.transition_summaries,
            key=lambda item: (item.deterministic_order, item.summary_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_readiness_certification_identity(
    identity: BoundaryReadinessCertificationIdentity,
) -> str:
    return stable_serialize_boundary_readiness_transition(
        export_readiness_certification_identity(identity)
    )


def serialize_transition_certification_identity(
    identity: V45TransitionCertificationIdentity,
) -> str:
    return stable_serialize_boundary_readiness_transition(
        export_transition_certification_identity(identity)
    )


def serialize_boundary_readiness_transition_certification(
    certification: BoundaryReadinessTransitionCertification,
) -> str:
    return stable_serialize_boundary_readiness_transition(
        export_boundary_readiness_transition_certification(certification)
    )
