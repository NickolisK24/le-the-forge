"""Deterministic serialization for v4.5A.8 readiness closeout."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5a_8_readiness_closeout_models import (
    CloseoutDiagnosticRecord,
    CloseoutRecord,
    ContinuityCertification,
    GeneratedReportCoverageCertification,
    InheritedProhibitionPreservationCertification,
    MigrationDocumentCoverageCertification,
    PhaseCoverageCertification,
    ReadinessCertificationRecord,
    ReadinessCloseoutIdentity,
    ReadinessCloseoutIntelligence,
    ReadinessVisibility,
    UnsupportedReadinessVisibility,
    UnsupportedStatePreservationCertification,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5a_8_readiness_closeout_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5a_8_readiness_closeout_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5a_8_readiness_closeout_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_v4_5a_8_readiness_closeout_evidence(value) for value in payload]
    return payload


def stable_serialize_v4_5a_8_readiness_closeout(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5a_8_readiness_closeout_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _export_with_sorted_evidence(record: object) -> dict[str, Any]:
    data = asdict(record)
    if "evidence_reference_ids" in data:
        data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_readiness_closeout_identity(
    identity: ReadinessCloseoutIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_closeout_record(record: CloseoutRecord) -> dict[str, Any]:
    return asdict(record)


def export_readiness_certification_record(
    record: ReadinessCertificationRecord,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_phase_coverage_certification(
    record: PhaseCoverageCertification,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_generated_report_coverage_certification(
    record: GeneratedReportCoverageCertification,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_migration_document_coverage_certification(
    record: MigrationDocumentCoverageCertification,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_continuity_certification(
    record: ContinuityCertification,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_state_preservation_certification(
    record: UnsupportedStatePreservationCertification,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_inherited_prohibition_preservation_certification(
    record: InheritedProhibitionPreservationCertification,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_readiness_visibility(record: ReadinessVisibility) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_closeout_diagnostic_record(
    record: CloseoutDiagnosticRecord,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_readiness_visibility(
    record: UnsupportedReadinessVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_v4_5a_8_readiness_closeout(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["closeout_identity"] = export_readiness_closeout_identity(
        intelligence.closeout_identity
    )
    data["closeout_records"] = [
        export_closeout_record(record)
        for record in sorted(
            intelligence.closeout_records,
            key=lambda item: (item.deterministic_order, item.closeout_record_id),
        )
    ]
    data["readiness_certifications"] = [
        export_readiness_certification_record(record)
        for record in sorted(
            intelligence.readiness_certifications,
            key=lambda item: (item.deterministic_order, item.readiness_record_id),
        )
    ]
    data["phase_coverage_certifications"] = [
        export_phase_coverage_certification(record)
        for record in sorted(
            intelligence.phase_coverage_certifications,
            key=lambda item: (item.deterministic_order, item.phase_coverage_id),
        )
    ]
    data["report_coverage_certifications"] = [
        export_generated_report_coverage_certification(record)
        for record in sorted(
            intelligence.report_coverage_certifications,
            key=lambda item: (item.deterministic_order, item.report_coverage_id),
        )
    ]
    data["migration_document_certifications"] = [
        export_migration_document_coverage_certification(record)
        for record in sorted(
            intelligence.migration_document_certifications,
            key=lambda item: (item.deterministic_order, item.document_coverage_id),
        )
    ]
    data["continuity_certifications"] = [
        export_continuity_certification(record)
        for record in sorted(
            intelligence.continuity_certifications,
            key=lambda item: (item.deterministic_order, item.continuity_certification_id),
        )
    ]
    data["unsupported_state_certifications"] = [
        export_unsupported_state_preservation_certification(record)
        for record in sorted(
            intelligence.unsupported_state_certifications,
            key=lambda item: (item.deterministic_order, item.unsupported_certification_id),
        )
    ]
    data["inherited_prohibition_certifications"] = [
        export_inherited_prohibition_preservation_certification(record)
        for record in sorted(
            intelligence.inherited_prohibition_certifications,
            key=lambda item: (item.deterministic_order, item.prohibition_certification_id),
        )
    ]
    data["readiness_visibility"] = [
        export_readiness_visibility(record)
        for record in sorted(
            intelligence.readiness_visibility,
            key=lambda item: (item.deterministic_order, item.readiness_visibility_id),
        )
    ]
    data["closeout_diagnostics"] = [
        export_closeout_diagnostic_record(record)
        for record in sorted(
            intelligence.closeout_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_readiness_visibility"] = [
        export_unsupported_readiness_visibility(record)
        for record in sorted(
            intelligence.unsupported_readiness_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["inherited_limitations"] = _sorted_tuple(data["inherited_limitations"])
    data["inherited_blockers"] = _sorted_tuple(data["inherited_blockers"])
    data["inherited_warnings"] = _sorted_tuple(data["inherited_warnings"])
    return data


def serialize_readiness_closeout_identity(
    identity: ReadinessCloseoutIdentity,
) -> str:
    return stable_serialize_v4_5a_8_readiness_closeout(
        export_readiness_closeout_identity(identity)
    )


def serialize_v4_5a_8_readiness_closeout(
    intelligence: ReadinessCloseoutIntelligence,
) -> str:
    return stable_serialize_v4_5a_8_readiness_closeout(
        export_v4_5a_8_readiness_closeout(intelligence)
    )
