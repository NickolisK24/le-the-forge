"""Stable hashing for v4.1 refresh drift certification evidence."""

from __future__ import annotations

from typing import Any

from operational_lifecycle.lifecycle_hashing import deterministic_lifecycle_hash

from .refresh_drift_certification_models import (
    RefreshDriftCertification,
    RefreshDriftCertificationIdentity,
    RefreshDriftContinuityMetadata,
    RefreshDriftDiagnostics,
)
from .refresh_drift_certification_serialization import (
    _export_record,
    export_refresh_drift_certification,
    export_refresh_drift_certification_identity,
)


def deterministic_refresh_drift_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_refresh_drift_certification_identity(identity: RefreshDriftCertificationIdentity) -> str:
    return deterministic_refresh_drift_hash(export_refresh_drift_certification_identity(identity))


def hash_refresh_drift_continuity(metadata: RefreshDriftContinuityMetadata) -> str:
    return deterministic_refresh_drift_hash(_export_record(metadata))


def hash_refresh_drift_diagnostics(diagnostics: RefreshDriftDiagnostics) -> str:
    return deterministic_refresh_drift_hash(_export_record(diagnostics))


def hash_refresh_drift_certification(certification: RefreshDriftCertification) -> str:
    return deterministic_refresh_drift_hash(export_refresh_drift_certification(certification))
