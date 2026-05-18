"""Deterministic serialization for v4.5A.7 integrity certification."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5a_7_integrity_certification_models import (
    CertificationDiagnosticRecord,
    ContinuityIntegrityCertification,
    CoverageCertificationVisibility,
    DiagnosticsIntegrityCertification,
    HashingSerializationIntegrityCertification,
    InheritedProhibitionPreservationCertification,
    IntegrityCertificationIdentity,
    IntegrityCertificationIntelligence,
    IntegrityCertificationRecord,
    UnsupportedCertificationVisibility,
    UnsupportedStatePreservationCertification,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5a_7_integrity_certification_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5a_7_integrity_certification_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5a_7_integrity_certification_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5a_7_integrity_certification_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5a_7_integrity_certification(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5a_7_integrity_certification_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_integrity_certification_identity(
    identity: IntegrityCertificationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_integrity_certification_record(
    record: IntegrityCertificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_coverage_certification_visibility(
    record: CoverageCertificationVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_unsupported_state_preservation_certification(
    record: UnsupportedStatePreservationCertification,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_inherited_prohibition_preservation_certification(
    record: InheritedProhibitionPreservationCertification,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_hashing_serialization_integrity_certification(
    record: HashingSerializationIntegrityCertification,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_continuity_integrity_certification(
    record: ContinuityIntegrityCertification,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_diagnostics_integrity_certification(
    record: DiagnosticsIntegrityCertification,
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


def export_unsupported_certification_visibility(
    record: UnsupportedCertificationVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5a_7_integrity_certification(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["certification_identity"] = export_integrity_certification_identity(
        intelligence.certification_identity
    )
    data["certification_records"] = [
        export_integrity_certification_record(record)
        for record in sorted(
            intelligence.certification_records,
            key=lambda item: (item.deterministic_order, item.certification_record_id),
        )
    ]
    data["coverage_certifications"] = [
        export_coverage_certification_visibility(record)
        for record in sorted(
            intelligence.coverage_certifications,
            key=lambda item: (item.deterministic_order, item.coverage_id),
        )
    ]
    data["unsupported_state_certifications"] = [
        export_unsupported_state_preservation_certification(record)
        for record in sorted(
            intelligence.unsupported_state_certifications,
            key=lambda item: (
                item.deterministic_order,
                item.unsupported_certification_id,
            ),
        )
    ]
    data["inherited_prohibition_certifications"] = [
        export_inherited_prohibition_preservation_certification(record)
        for record in sorted(
            intelligence.inherited_prohibition_certifications,
            key=lambda item: (
                item.deterministic_order,
                item.prohibition_certification_id,
            ),
        )
    ]
    data["hashing_serialization_certifications"] = [
        export_hashing_serialization_integrity_certification(record)
        for record in sorted(
            intelligence.hashing_serialization_certifications,
            key=lambda item: (
                item.deterministic_order,
                item.hash_serialization_certification_id,
            ),
        )
    ]
    data["continuity_certifications"] = [
        export_continuity_integrity_certification(record)
        for record in sorted(
            intelligence.continuity_certifications,
            key=lambda item: (item.deterministic_order, item.continuity_certification_id),
        )
    ]
    data["diagnostics_certifications"] = [
        export_diagnostics_integrity_certification(record)
        for record in sorted(
            intelligence.diagnostics_certifications,
            key=lambda item: (
                item.deterministic_order,
                item.diagnostics_certification_id,
            ),
        )
    ]
    data["certification_diagnostics"] = [
        export_certification_diagnostic_record(record)
        for record in sorted(
            intelligence.certification_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_certification_visibility"] = [
        export_unsupported_certification_visibility(record)
        for record in sorted(
            intelligence.unsupported_certification_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_integrity_certification_identity(
    identity: IntegrityCertificationIdentity,
) -> str:
    return stable_serialize_v4_5a_7_integrity_certification(
        export_integrity_certification_identity(identity)
    )


def serialize_v4_5a_7_integrity_certification(
    intelligence: IntegrityCertificationIntelligence,
) -> str:
    return stable_serialize_v4_5a_7_integrity_certification(
        export_v4_5a_7_integrity_certification(intelligence)
    )
