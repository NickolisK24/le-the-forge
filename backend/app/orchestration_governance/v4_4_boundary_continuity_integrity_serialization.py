"""Deterministic serialization for v4.4 boundary continuity and integrity."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_boundary_continuity_integrity_models import (
    BoundaryContinuityCertificationIdentity,
    BoundaryContinuityIntegrityCertification,
    BoundaryIntegrityCertificationIdentity,
    CertificationDiagnosticRecord,
    CertificationLimitationRecord,
    CertificationSummaryRecord,
    ContinuityCertificationRecord,
    IntegrityCertificationRecord,
    LineageContinuityRecord,
    PhaseChainCertificationIdentity,
    PhaseEvidenceReference,
    ProvenanceContinuityRecord,
    ReplayRollbackSafetyRecord,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_boundary_continuity_integrity_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_boundary_continuity_integrity_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_boundary_continuity_integrity_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_boundary_continuity_integrity_evidence(value) for value in payload]
    return payload


def stable_serialize_boundary_continuity_integrity(payload: Any) -> str:
    return json.dumps(
        canonicalize_boundary_continuity_integrity_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_continuity_certification_identity(
    identity: BoundaryContinuityCertificationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_integrity_certification_identity(
    identity: BoundaryIntegrityCertificationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_phase_chain_certification_identity(
    identity: PhaseChainCertificationIdentity,
) -> dict[str, Any]:
    data = asdict(identity)
    data["phase_ids"] = _sorted_tuple(data["phase_ids"])
    return data


def export_phase_evidence_reference(record: PhaseEvidenceReference) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_continuity_certification_record(
    record: ContinuityCertificationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["continuity_reference_ids"] = _sorted_tuple(data["continuity_reference_ids"])
    return data


def export_integrity_certification_record(
    record: IntegrityCertificationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["integrity_reference_ids"] = _sorted_tuple(data["integrity_reference_ids"])
    return data


def export_certification_limitation_record(
    record: CertificationLimitationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_certification_diagnostic_record(
    record: CertificationDiagnosticRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_provenance_continuity_record(record: ProvenanceContinuityRecord) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("source_reference_ids", "source_hash_references"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_lineage_continuity_record(record: LineageContinuityRecord) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("lineage_reference_ids", "lineage_hash_references"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_replay_rollback_safety_record(
    record: ReplayRollbackSafetyRecord,
) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("phase_evidence_ids", "replay_evidence_ids", "rollback_evidence_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_certification_summary_record(record: CertificationSummaryRecord) -> dict[str, Any]:
    data = asdict(record)
    data["summary_reference_ids"] = _sorted_tuple(data["summary_reference_ids"])
    return data


def export_boundary_continuity_integrity_certification(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    data = asdict(certification)
    data["continuity_identity"] = export_continuity_certification_identity(
        certification.continuity_identity
    )
    data["integrity_identity"] = export_integrity_certification_identity(
        certification.integrity_identity
    )
    data["phase_chain_identity"] = export_phase_chain_certification_identity(
        certification.phase_chain_identity
    )
    data["phase_evidence_references"] = [
        export_phase_evidence_reference(record)
        for record in sorted(
            certification.phase_evidence_references,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]
    data["continuity_records"] = [
        export_continuity_certification_record(record)
        for record in sorted(
            certification.continuity_records,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["integrity_records"] = [
        export_integrity_certification_record(record)
        for record in sorted(
            certification.integrity_records,
            key=lambda item: (item.deterministic_order, item.integrity_id),
        )
    ]
    data["limitation_records"] = [
        export_certification_limitation_record(record)
        for record in sorted(
            certification.limitation_records,
            key=lambda item: (item.deterministic_order, item.limitation_id),
        )
    ]
    data["diagnostic_records"] = [
        export_certification_diagnostic_record(record)
        for record in sorted(
            certification.diagnostic_records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["provenance_record"] = export_provenance_continuity_record(
        certification.provenance_record
    )
    data["lineage_record"] = export_lineage_continuity_record(certification.lineage_record)
    data["replay_rollback_record"] = export_replay_rollback_safety_record(
        certification.replay_rollback_record
    )
    data["certification_summaries"] = [
        export_certification_summary_record(record)
        for record in sorted(
            certification.certification_summaries,
            key=lambda item: (item.deterministic_order, item.summary_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_continuity_certification_identity(
    identity: BoundaryContinuityCertificationIdentity,
) -> str:
    return stable_serialize_boundary_continuity_integrity(
        export_continuity_certification_identity(identity)
    )


def serialize_integrity_certification_identity(
    identity: BoundaryIntegrityCertificationIdentity,
) -> str:
    return stable_serialize_boundary_continuity_integrity(
        export_integrity_certification_identity(identity)
    )


def serialize_boundary_continuity_integrity_certification(
    certification: BoundaryContinuityIntegrityCertification,
) -> str:
    return stable_serialize_boundary_continuity_integrity(
        export_boundary_continuity_integrity_certification(certification)
    )
