"""Deterministic hashing for v4.5A.7 integrity certification."""

from __future__ import annotations

import hashlib
from typing import Any

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
from .v4_5a_7_integrity_certification_serialization import (
    export_certification_diagnostic_record,
    export_continuity_integrity_certification,
    export_coverage_certification_visibility,
    export_diagnostics_integrity_certification,
    export_hashing_serialization_integrity_certification,
    export_inherited_prohibition_preservation_certification,
    export_integrity_certification_identity,
    export_integrity_certification_record,
    export_unsupported_certification_visibility,
    export_unsupported_state_preservation_certification,
    export_v4_5a_7_integrity_certification,
    stable_serialize_v4_5a_7_integrity_certification,
)


def deterministic_v4_5a_7_integrity_certification_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5a_7_integrity_certification(payload).encode("utf-8")
    ).hexdigest()


def hash_integrity_certification_identity(
    identity: IntegrityCertificationIdentity,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_integrity_certification_identity(identity)
    )


def hash_integrity_certification_record(record: IntegrityCertificationRecord) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_integrity_certification_record(record)
    )


def hash_coverage_certification_visibility(
    record: CoverageCertificationVisibility,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_coverage_certification_visibility(record)
    )


def hash_unsupported_state_preservation_certification(
    record: UnsupportedStatePreservationCertification,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_unsupported_state_preservation_certification(record)
    )


def hash_inherited_prohibition_preservation_certification(
    record: InheritedProhibitionPreservationCertification,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_inherited_prohibition_preservation_certification(record)
    )


def hash_hashing_serialization_integrity_certification(
    record: HashingSerializationIntegrityCertification,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_hashing_serialization_integrity_certification(record)
    )


def hash_continuity_integrity_certification(
    record: ContinuityIntegrityCertification,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_continuity_integrity_certification(record)
    )


def hash_diagnostics_integrity_certification(
    record: DiagnosticsIntegrityCertification,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_diagnostics_integrity_certification(record)
    )


def hash_certification_diagnostic_record(
    record: CertificationDiagnosticRecord,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_certification_diagnostic_record(record)
    )


def hash_unsupported_certification_visibility(
    record: UnsupportedCertificationVisibility,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_unsupported_certification_visibility(record)
    )


def hash_v4_5a_7_integrity_certification(
    intelligence: IntegrityCertificationIntelligence,
) -> str:
    return deterministic_v4_5a_7_integrity_certification_hash(
        export_v4_5a_7_integrity_certification(intelligence)
    )
