"""Deterministic serialization for v4.4 closeout and v4.5 readiness."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_closeout_readiness_models import (
    CloseoutCertificationRecord,
    CloseoutInheritedConstraintRecord,
    CloseoutInheritedProhibitionRecord,
    CloseoutReadinessLineageRecord,
    CloseoutReadinessProvenanceRecord,
    CloseoutReadinessReplayRollbackRecord,
    CloseoutReadinessSummaryRecord,
    NonOperationalCloseoutCertificationRecord,
    PhaseChainEvidenceIdentity,
    PhaseChainEvidenceRecord,
    PreservedBlockerRecord,
    PreservedLimitationRecord,
    PreservedWarningRecord,
    V44CloseoutAndV45ReadinessCertification,
    V44CloseoutCertificationIdentity,
    V45InheritedLimitationRecord,
    V45PlanningBoundaryRecord,
    V45ReadinessCertificationIdentity,
    V45ReadinessCertificationRecord,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_4_closeout_readiness_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_4_closeout_readiness_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_4_closeout_readiness_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_v4_4_closeout_readiness_evidence(value) for value in payload]
    return payload


def stable_serialize_v4_4_closeout_readiness(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_4_closeout_readiness_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_closeout_identity(identity: V44CloseoutCertificationIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_readiness_identity(identity: V45ReadinessCertificationIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_phase_chain_evidence_identity(identity: PhaseChainEvidenceIdentity) -> dict[str, Any]:
    data = asdict(identity)
    data["phase_ids"] = _sorted_tuple(data["phase_ids"])
    return data


def export_phase_chain_evidence_record(record: PhaseChainEvidenceRecord) -> dict[str, Any]:
    return asdict(record)


def export_closeout_certification_record(record: CloseoutCertificationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5_readiness_certification_record(
    record: V45ReadinessCertificationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_preserved_limitation_record(record: PreservedLimitationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_preserved_blocker_record(record: PreservedBlockerRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_preserved_warning_record(record: PreservedWarningRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_inherited_prohibition_record(
    record: CloseoutInheritedProhibitionRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["inherited_from_phase_ids"] = _sorted_tuple(data["inherited_from_phase_ids"])
    return data


def export_inherited_constraint_record(
    record: CloseoutInheritedConstraintRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["inherited_from_phase_ids"] = _sorted_tuple(data["inherited_from_phase_ids"])
    return data


def export_v4_5_planning_boundary(record: V45PlanningBoundaryRecord) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("required_evidence_inputs", "expected_certification_needs"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_v4_5_inherited_limitation(record: V45InheritedLimitationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["source_limitation_ids"] = _sorted_tuple(data["source_limitation_ids"])
    return data


def export_non_operational_closeout_certification(
    record: NonOperationalCloseoutCertificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_closeout_readiness_provenance(
    record: CloseoutReadinessProvenanceRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["source_reference_ids"] = _sorted_tuple(data["source_reference_ids"])
    data["source_hash_references"] = _sorted_tuple(data["source_hash_references"])
    return data


def export_closeout_readiness_lineage(record: CloseoutReadinessLineageRecord) -> dict[str, Any]:
    data = asdict(record)
    data["lineage_reference_ids"] = _sorted_tuple(data["lineage_reference_ids"])
    data["lineage_hash_references"] = _sorted_tuple(data["lineage_hash_references"])
    return data


def export_closeout_readiness_replay_rollback(
    record: CloseoutReadinessReplayRollbackRecord,
) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("evidence_reference_ids", "replay_evidence_ids", "rollback_evidence_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_closeout_readiness_summary(record: CloseoutReadinessSummaryRecord) -> dict[str, Any]:
    data = asdict(record)
    data["summary_reference_ids"] = _sorted_tuple(data["summary_reference_ids"])
    return data


def export_v4_4_closeout_readiness_certification(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    data = asdict(certification)
    data["closeout_identity"] = export_closeout_identity(certification.closeout_identity)
    data["readiness_identity"] = export_readiness_identity(certification.readiness_identity)
    data["phase_chain_identity"] = export_phase_chain_evidence_identity(
        certification.phase_chain_identity
    )
    data["phase_chain_evidence_records"] = [
        export_phase_chain_evidence_record(record)
        for record in sorted(
            certification.phase_chain_evidence_records,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]
    data["closeout_records"] = [
        export_closeout_certification_record(record)
        for record in sorted(
            certification.closeout_records,
            key=lambda item: (item.deterministic_order, item.closeout_id),
        )
    ]
    data["readiness_records"] = [
        export_v4_5_readiness_certification_record(record)
        for record in sorted(
            certification.readiness_records,
            key=lambda item: (item.deterministic_order, item.readiness_id),
        )
    ]
    data["preserved_limitation_records"] = [
        export_preserved_limitation_record(record)
        for record in sorted(
            certification.preserved_limitation_records,
            key=lambda item: (item.deterministic_order, item.limitation_id),
        )
    ]
    data["preserved_blocker_records"] = [
        export_preserved_blocker_record(record)
        for record in sorted(
            certification.preserved_blocker_records,
            key=lambda item: (item.deterministic_order, item.blocker_id),
        )
    ]
    data["preserved_warning_records"] = [
        export_preserved_warning_record(record)
        for record in sorted(
            certification.preserved_warning_records,
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
    data["planning_boundary_records"] = [
        export_v4_5_planning_boundary(record)
        for record in sorted(
            certification.planning_boundary_records,
            key=lambda item: (item.deterministic_order, item.planning_boundary_id),
        )
    ]
    data["inherited_limitation_records"] = [
        export_v4_5_inherited_limitation(record)
        for record in sorted(
            certification.inherited_limitation_records,
            key=lambda item: (item.deterministic_order, item.inherited_limitation_id),
        )
    ]
    data["non_operational_certifications"] = [
        export_non_operational_closeout_certification(record)
        for record in sorted(
            certification.non_operational_certifications,
            key=lambda item: (item.deterministic_order, item.certification_id),
        )
    ]
    data["provenance_record"] = export_closeout_readiness_provenance(
        certification.provenance_record
    )
    data["lineage_record"] = export_closeout_readiness_lineage(certification.lineage_record)
    data["replay_rollback_record"] = export_closeout_readiness_replay_rollback(
        certification.replay_rollback_record
    )
    data["closeout_readiness_summaries"] = [
        export_closeout_readiness_summary(record)
        for record in sorted(
            certification.closeout_readiness_summaries,
            key=lambda item: (item.deterministic_order, item.summary_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_closeout_identity(identity: V44CloseoutCertificationIdentity) -> str:
    return stable_serialize_v4_4_closeout_readiness(export_closeout_identity(identity))


def serialize_readiness_identity(identity: V45ReadinessCertificationIdentity) -> str:
    return stable_serialize_v4_4_closeout_readiness(export_readiness_identity(identity))


def serialize_v4_4_closeout_readiness_certification(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> str:
    return stable_serialize_v4_4_closeout_readiness(
        export_v4_4_closeout_readiness_certification(certification)
    )
