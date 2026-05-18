"""Deterministic hashing for v4.5B.8 trusted UX closeout."""

from __future__ import annotations

import hashlib
from typing import Any

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
from .v4_5b_8_trusted_ux_closeout_serialization import (
    export_frontend_readiness_visibility_record,
    export_generated_report_coverage_record,
    export_inherited_prohibition_certification_record,
    export_migration_document_coverage_record,
    export_phase_coverage_record,
    export_public_trust_continuity_record,
    export_trusted_ux_closeout_diagnostic_record,
    export_trusted_ux_closeout_identity,
    export_trusted_ux_closeout_record,
    export_trusted_ux_readiness_record,
    export_unsupported_state_certification_record,
    export_unsupported_trusted_ux_operational_state_visibility,
    export_v4_5b_8_trusted_ux_closeout,
    stable_serialize_v4_5b_8_trusted_ux_closeout,
)


def deterministic_v4_5b_8_trusted_ux_closeout_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5b_8_trusted_ux_closeout(payload).encode("utf-8")
    ).hexdigest()


def hash_trusted_ux_closeout_identity(identity: TrustedUxCloseoutIdentity) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_trusted_ux_closeout_identity(identity)
    )


def hash_trusted_ux_closeout_record(record: TrustedUxCloseoutRecord) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_trusted_ux_closeout_record(record)
    )


def hash_trusted_ux_readiness_record(record: TrustedUxReadinessRecord) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_trusted_ux_readiness_record(record)
    )


def hash_phase_coverage_record(record: PhaseCoverageRecord) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_phase_coverage_record(record)
    )


def hash_generated_report_coverage_record(
    record: GeneratedReportCoverageRecord,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_generated_report_coverage_record(record)
    )


def hash_migration_document_coverage_record(
    record: MigrationDocumentCoverageRecord,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_migration_document_coverage_record(record)
    )


def hash_public_trust_continuity_record(
    record: PublicTrustContinuityRecord,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_public_trust_continuity_record(record)
    )


def hash_unsupported_state_certification_record(
    record: UnsupportedStateCertificationRecord,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_unsupported_state_certification_record(record)
    )


def hash_inherited_prohibition_certification_record(
    record: InheritedProhibitionCertificationRecord,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_inherited_prohibition_certification_record(record)
    )


def hash_frontend_readiness_visibility_record(
    record: FrontendReadinessVisibilityRecord,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_frontend_readiness_visibility_record(record)
    )


def hash_trusted_ux_closeout_diagnostic_record(
    record: TrustedUxCloseoutDiagnosticRecord,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_trusted_ux_closeout_diagnostic_record(record)
    )


def hash_unsupported_trusted_ux_operational_state_visibility(
    record: UnsupportedTrustedUxOperationalStateVisibility,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_unsupported_trusted_ux_operational_state_visibility(record)
    )


def hash_v4_5b_8_trusted_ux_closeout(
    certification: TrustedUxCloseoutCertification,
) -> str:
    return deterministic_v4_5b_8_trusted_ux_closeout_hash(
        export_v4_5b_8_trusted_ux_closeout(certification)
    )
