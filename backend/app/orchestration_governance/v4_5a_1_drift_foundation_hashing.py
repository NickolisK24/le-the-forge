"""Deterministic hashing for v4.5A.1 drift foundations."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5a_1_drift_foundation_models import (
    DriftClassificationRecord,
    DriftContinuityVisibility,
    DriftDiagnosticRecord,
    DriftEvidenceReference,
    DriftFoundationIdentity,
    DriftFoundationIntelligence,
    DriftIdentityRecord,
    DriftSeverityVisibility,
    UnsupportedDriftStateVisibility,
)
from .v4_5a_1_drift_foundation_serialization import (
    export_drift_classification_record,
    export_drift_continuity_visibility,
    export_drift_diagnostic_record,
    export_drift_evidence_reference,
    export_drift_foundation_identity,
    export_drift_identity_record,
    export_drift_severity_visibility,
    export_unsupported_drift_state_visibility,
    export_v4_5a_1_drift_foundations,
    stable_serialize_v4_5a_1_drift_foundation,
)


def deterministic_v4_5a_1_drift_foundation_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5a_1_drift_foundation(payload).encode("utf-8")
    ).hexdigest()


def hash_drift_foundation_identity(identity: DriftFoundationIdentity) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_drift_foundation_identity(identity)
    )


def hash_drift_identity_record(record: DriftIdentityRecord) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_drift_identity_record(record)
    )


def hash_drift_classification_record(record: DriftClassificationRecord) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_drift_classification_record(record)
    )


def hash_drift_evidence_reference(record: DriftEvidenceReference) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_drift_evidence_reference(record)
    )


def hash_drift_continuity_visibility(record: DriftContinuityVisibility) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_drift_continuity_visibility(record)
    )


def hash_drift_diagnostic_record(record: DriftDiagnosticRecord) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_drift_diagnostic_record(record)
    )


def hash_drift_severity_visibility(record: DriftSeverityVisibility) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_drift_severity_visibility(record)
    )


def hash_unsupported_drift_state_visibility(
    record: UnsupportedDriftStateVisibility,
) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_unsupported_drift_state_visibility(record)
    )


def hash_v4_5a_1_drift_foundations(
    foundations: DriftFoundationIntelligence,
) -> str:
    return deterministic_v4_5a_1_drift_foundation_hash(
        export_v4_5a_1_drift_foundations(foundations)
    )
