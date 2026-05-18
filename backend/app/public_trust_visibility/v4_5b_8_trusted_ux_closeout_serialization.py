"""Deterministic serialization for v4.5B.8 trusted UX closeout."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5b_8_trusted_ux_closeout_models import (
    FrontendReadinessVisibilityRecord,
    GeneratedReportCoverageRecord,
    InheritedProhibitionCertificationRecord,
    MigrationDocumentCoverageRecord,
    PhaseCoverageRecord,
    PublicTrustContinuityRecord,
    TrustedUxCloseoutCertification,
    TrustedUxCloseoutDiagnosticRecord,
    TrustedUxCloseoutIdentity,
    TrustedUxCloseoutRecord,
    TrustedUxReadinessRecord,
    UnsupportedStateCertificationRecord,
    UnsupportedTrustedUxOperationalStateVisibility,
)


def canonicalize_v4_5b_8_trusted_ux_closeout_payload(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5b_8_trusted_ux_closeout_payload(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5b_8_trusted_ux_closeout_payload(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5b_8_trusted_ux_closeout_payload(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5b_8_trusted_ux_closeout(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5b_8_trusted_ux_closeout_payload(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def export_trusted_ux_closeout_identity(
    identity: TrustedUxCloseoutIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_trusted_ux_closeout_record(
    record: TrustedUxCloseoutRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_trusted_ux_readiness_record(
    record: TrustedUxReadinessRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_phase_coverage_record(record: PhaseCoverageRecord) -> dict[str, Any]:
    return asdict(record)


def export_generated_report_coverage_record(
    record: GeneratedReportCoverageRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_migration_document_coverage_record(
    record: MigrationDocumentCoverageRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_public_trust_continuity_record(
    record: PublicTrustContinuityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_unsupported_state_certification_record(
    record: UnsupportedStateCertificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_inherited_prohibition_certification_record(
    record: InheritedProhibitionCertificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_frontend_readiness_visibility_record(
    record: FrontendReadinessVisibilityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_trusted_ux_closeout_diagnostic_record(
    record: TrustedUxCloseoutDiagnosticRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_unsupported_trusted_ux_operational_state_visibility(
    record: UnsupportedTrustedUxOperationalStateVisibility,
) -> dict[str, Any]:
    return asdict(record)


def export_v4_5b_8_trusted_ux_closeout(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    data = asdict(certification)
    data["identity"] = export_trusted_ux_closeout_identity(certification.identity)
    data["closeout_records"] = [
        export_trusted_ux_closeout_record(record)
        for record in sorted(
            certification.closeout_records,
            key=lambda item: (item.deterministic_order, item.closeout_record_id),
        )
    ]
    data["readiness_records"] = [
        export_trusted_ux_readiness_record(record)
        for record in sorted(
            certification.readiness_records,
            key=lambda item: (item.deterministic_order, item.readiness_record_id),
        )
    ]
    data["phase_coverage_records"] = [
        export_phase_coverage_record(record)
        for record in sorted(
            certification.phase_coverage_records,
            key=lambda item: (item.deterministic_order, item.phase_coverage_id),
        )
    ]
    data["report_coverage_records"] = [
        export_generated_report_coverage_record(record)
        for record in sorted(
            certification.report_coverage_records,
            key=lambda item: (item.deterministic_order, item.report_coverage_id),
        )
    ]
    data["migration_document_coverage_records"] = [
        export_migration_document_coverage_record(record)
        for record in sorted(
            certification.migration_document_coverage_records,
            key=lambda item: (
                item.deterministic_order,
                item.migration_document_coverage_id,
            ),
        )
    ]
    data["public_trust_continuity_records"] = [
        export_public_trust_continuity_record(record)
        for record in sorted(
            certification.public_trust_continuity_records,
            key=lambda item: (item.deterministic_order, item.continuity_record_id),
        )
    ]
    data["unsupported_state_records"] = [
        export_unsupported_state_certification_record(record)
        for record in sorted(
            certification.unsupported_state_records,
            key=lambda item: (
                item.deterministic_order,
                item.unsupported_state_record_id,
            ),
        )
    ]
    data["inherited_prohibition_records"] = [
        export_inherited_prohibition_certification_record(record)
        for record in sorted(
            certification.inherited_prohibition_records,
            key=lambda item: (
                item.deterministic_order,
                item.inherited_prohibition_record_id,
            ),
        )
    ]
    data["frontend_readiness_records"] = [
        export_frontend_readiness_visibility_record(record)
        for record in sorted(
            certification.frontend_readiness_records,
            key=lambda item: (item.deterministic_order, item.frontend_readiness_id),
        )
    ]
    data["closeout_diagnostic_records"] = [
        export_trusted_ux_closeout_diagnostic_record(record)
        for record in sorted(
            certification.closeout_diagnostic_records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_operational_state_visibility"] = [
        export_unsupported_trusted_ux_operational_state_visibility(record)
        for record in sorted(
            certification.unsupported_operational_state_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_trusted_ux_closeout_identity(
    identity: TrustedUxCloseoutIdentity,
) -> str:
    return stable_serialize_v4_5b_8_trusted_ux_closeout(
        export_trusted_ux_closeout_identity(identity)
    )


def serialize_v4_5b_8_trusted_ux_closeout(
    certification: TrustedUxCloseoutCertification,
) -> str:
    return stable_serialize_v4_5b_8_trusted_ux_closeout(
        export_v4_5b_8_trusted_ux_closeout(certification)
    )
