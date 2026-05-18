"""Deterministic serialization for v4.4 blocker resolution closeout evidence."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_boundary_blocker_resolution_models import (
    BlockerClassificationIdentity,
    BlockerClassificationRecord,
    BlockerResolutionLineageRecord,
    BlockerResolutionProvenanceRecord,
    BlockerResolutionReplayRollbackRecord,
    BoundaryBlockerResolutionCloseoutPreparation,
    CloseoutEligibilityIdentity,
    CloseoutEligibilityRecord,
    CloseoutPreparationSummaryRecord,
    EscalationRecord,
    FailVisibleExplanationRecord,
    InheritedConstraintRecord,
    InheritedProhibitionRecord,
    NonOperationalBlockerCertificationRecord,
    Phase8ReadinessEvidenceReference,
    UnresolvedLimitationRecord,
    V45InheritedPlanningBoundaryIdentity,
    V45InheritedPlanningBoundaryRecord,
    WarningClassificationIdentity,
    WarningClassificationRecord,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_boundary_blocker_resolution_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_boundary_blocker_resolution_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_boundary_blocker_resolution_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_boundary_blocker_resolution_evidence(value) for value in payload]
    return payload


def stable_serialize_boundary_blocker_resolution(payload: Any) -> str:
    return json.dumps(
        canonicalize_boundary_blocker_resolution_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_blocker_classification_identity(
    identity: BlockerClassificationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_warning_classification_identity(
    identity: WarningClassificationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_closeout_eligibility_identity(
    identity: CloseoutEligibilityIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_v4_5_inherited_planning_boundary_identity(
    identity: V45InheritedPlanningBoundaryIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_phase8_readiness_evidence_reference(
    record: Phase8ReadinessEvidenceReference,
) -> dict[str, Any]:
    return asdict(record)


def export_blocker_classification_record(
    record: BlockerClassificationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_warning_classification_record(
    record: WarningClassificationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_inherited_prohibition_record(
    record: InheritedProhibitionRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["inherited_from_phase_ids"] = _sorted_tuple(data["inherited_from_phase_ids"])
    return data


def export_inherited_constraint_record(record: InheritedConstraintRecord) -> dict[str, Any]:
    data = asdict(record)
    data["inherited_from_phase_ids"] = _sorted_tuple(data["inherited_from_phase_ids"])
    return data


def export_unresolved_limitation_record(record: UnresolvedLimitationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_escalation_record(record: EscalationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["trace_reference_ids"] = _sorted_tuple(data["trace_reference_ids"])
    return data


def export_closeout_eligibility_record(record: CloseoutEligibilityRecord) -> dict[str, Any]:
    data = asdict(record)
    data["limitation_reference_ids"] = _sorted_tuple(data["limitation_reference_ids"])
    return data


def export_v4_5_inherited_planning_boundary_record(
    record: V45InheritedPlanningBoundaryRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["inherited_constraint_ids"] = _sorted_tuple(data["inherited_constraint_ids"])
    data["inherited_prohibition_ids"] = _sorted_tuple(data["inherited_prohibition_ids"])
    return data


def export_fail_visible_explanation_record(
    record: FailVisibleExplanationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_non_operational_blocker_certification(
    record: NonOperationalBlockerCertificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_blocker_resolution_provenance(
    record: BlockerResolutionProvenanceRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["source_reference_ids"] = _sorted_tuple(data["source_reference_ids"])
    data["source_hash_references"] = _sorted_tuple(data["source_hash_references"])
    return data


def export_blocker_resolution_lineage(
    record: BlockerResolutionLineageRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["lineage_reference_ids"] = _sorted_tuple(data["lineage_reference_ids"])
    data["lineage_hash_references"] = _sorted_tuple(data["lineage_hash_references"])
    return data


def export_blocker_resolution_replay_rollback(
    record: BlockerResolutionReplayRollbackRecord,
) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("evidence_reference_ids", "replay_evidence_ids", "rollback_evidence_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_closeout_preparation_summary(
    record: CloseoutPreparationSummaryRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["summary_reference_ids"] = _sorted_tuple(data["summary_reference_ids"])
    return data


def export_boundary_blocker_resolution_closeout_preparation(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    data = asdict(certification)
    data["blocker_identity"] = export_blocker_classification_identity(
        certification.blocker_identity
    )
    data["warning_identity"] = export_warning_classification_identity(
        certification.warning_identity
    )
    data["closeout_identity"] = export_closeout_eligibility_identity(
        certification.closeout_identity
    )
    data["planning_boundary_identity"] = export_v4_5_inherited_planning_boundary_identity(
        certification.planning_boundary_identity
    )
    data["phase8_evidence_references"] = [
        export_phase8_readiness_evidence_reference(record)
        for record in sorted(
            certification.phase8_evidence_references,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]
    data["blocker_records"] = [
        export_blocker_classification_record(record)
        for record in sorted(
            certification.blocker_records,
            key=lambda item: (item.deterministic_order, item.blocker_id),
        )
    ]
    data["warning_records"] = [
        export_warning_classification_record(record)
        for record in sorted(
            certification.warning_records,
            key=lambda item: (item.deterministic_order, item.warning_id),
        )
    ]
    data["inherited_prohibition_records"] = [
        export_inherited_prohibition_record(record)
        for record in sorted(
            certification.inherited_prohibition_records,
            key=lambda item: (item.deterministic_order, item.prohibition_id),
        )
    ]
    data["inherited_constraint_records"] = [
        export_inherited_constraint_record(record)
        for record in sorted(
            certification.inherited_constraint_records,
            key=lambda item: (item.deterministic_order, item.constraint_id),
        )
    ]
    data["limitation_records"] = [
        export_unresolved_limitation_record(record)
        for record in sorted(
            certification.limitation_records,
            key=lambda item: (item.deterministic_order, item.limitation_id),
        )
    ]
    data["escalation_records"] = [
        export_escalation_record(record)
        for record in sorted(
            certification.escalation_records,
            key=lambda item: (item.deterministic_order, item.escalation_id),
        )
    ]
    data["closeout_eligibility_records"] = [
        export_closeout_eligibility_record(record)
        for record in sorted(
            certification.closeout_eligibility_records,
            key=lambda item: (item.deterministic_order, item.eligibility_id),
        )
    ]
    data["planning_boundary_records"] = [
        export_v4_5_inherited_planning_boundary_record(record)
        for record in sorted(
            certification.planning_boundary_records,
            key=lambda item: (item.deterministic_order, item.planning_boundary_id),
        )
    ]
    data["fail_visible_explanations"] = [
        export_fail_visible_explanation_record(record)
        for record in sorted(
            certification.fail_visible_explanations,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    data["non_operational_certifications"] = [
        export_non_operational_blocker_certification(record)
        for record in sorted(
            certification.non_operational_certifications,
            key=lambda item: (item.deterministic_order, item.certification_id),
        )
    ]
    data["provenance_record"] = export_blocker_resolution_provenance(
        certification.provenance_record
    )
    data["lineage_record"] = export_blocker_resolution_lineage(certification.lineage_record)
    data["replay_rollback_record"] = export_blocker_resolution_replay_rollback(
        certification.replay_rollback_record
    )
    data["closeout_summaries"] = [
        export_closeout_preparation_summary(record)
        for record in sorted(
            certification.closeout_summaries,
            key=lambda item: (item.deterministic_order, item.summary_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_blocker_classification_identity(
    identity: BlockerClassificationIdentity,
) -> str:
    return stable_serialize_boundary_blocker_resolution(
        export_blocker_classification_identity(identity)
    )


def serialize_warning_classification_identity(
    identity: WarningClassificationIdentity,
) -> str:
    return stable_serialize_boundary_blocker_resolution(
        export_warning_classification_identity(identity)
    )


def serialize_boundary_blocker_resolution_closeout_preparation(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> str:
    return stable_serialize_boundary_blocker_resolution(
        export_boundary_blocker_resolution_closeout_preparation(certification)
    )
