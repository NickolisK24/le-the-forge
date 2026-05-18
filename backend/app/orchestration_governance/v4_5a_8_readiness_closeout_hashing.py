"""Deterministic hashing for v4.5A.8 readiness closeout."""

from __future__ import annotations

import hashlib
from typing import Any

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
from .v4_5a_8_readiness_closeout_serialization import (
    export_closeout_diagnostic_record,
    export_closeout_record,
    export_continuity_certification,
    export_generated_report_coverage_certification,
    export_inherited_prohibition_preservation_certification,
    export_migration_document_coverage_certification,
    export_phase_coverage_certification,
    export_readiness_certification_record,
    export_readiness_closeout_identity,
    export_readiness_visibility,
    export_unsupported_readiness_visibility,
    export_unsupported_state_preservation_certification,
    export_v4_5a_8_readiness_closeout,
    stable_serialize_v4_5a_8_readiness_closeout,
)


def deterministic_v4_5a_8_readiness_closeout_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5a_8_readiness_closeout(payload).encode("utf-8")
    ).hexdigest()


def hash_readiness_closeout_identity(identity: ReadinessCloseoutIdentity) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_readiness_closeout_identity(identity)
    )


def hash_closeout_record(record: CloseoutRecord) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_closeout_record(record)
    )


def hash_readiness_certification_record(
    record: ReadinessCertificationRecord,
) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_readiness_certification_record(record)
    )


def hash_phase_coverage_certification(record: PhaseCoverageCertification) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_phase_coverage_certification(record)
    )


def hash_generated_report_coverage_certification(
    record: GeneratedReportCoverageCertification,
) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_generated_report_coverage_certification(record)
    )


def hash_migration_document_coverage_certification(
    record: MigrationDocumentCoverageCertification,
) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_migration_document_coverage_certification(record)
    )


def hash_continuity_certification(record: ContinuityCertification) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_continuity_certification(record)
    )


def hash_unsupported_state_preservation_certification(
    record: UnsupportedStatePreservationCertification,
) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_unsupported_state_preservation_certification(record)
    )


def hash_inherited_prohibition_preservation_certification(
    record: InheritedProhibitionPreservationCertification,
) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_inherited_prohibition_preservation_certification(record)
    )


def hash_readiness_visibility(record: ReadinessVisibility) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_readiness_visibility(record)
    )


def hash_closeout_diagnostic_record(record: CloseoutDiagnosticRecord) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_closeout_diagnostic_record(record)
    )


def hash_unsupported_readiness_visibility(
    record: UnsupportedReadinessVisibility,
) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_unsupported_readiness_visibility(record)
    )


def hash_v4_5a_8_readiness_closeout(
    intelligence: ReadinessCloseoutIntelligence,
) -> str:
    return deterministic_v4_5a_8_readiness_closeout_hash(
        export_v4_5a_8_readiness_closeout(intelligence)
    )
