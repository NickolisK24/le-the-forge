"""Stable hashing for v4.1 refresh lineage certification evidence."""

from __future__ import annotations

from typing import Any

from operational_lifecycle.lifecycle_hashing import deterministic_lifecycle_hash

from .refresh_lineage_certification_models import (
    RefreshLineageCertification,
    RefreshLineageContinuityMetadata,
    RefreshLineageDiagnostics,
    RefreshLineageIdentity,
)
from .refresh_lineage_certification_serialization import (
    export_continuity_metadata,
    export_diagnostics,
    export_lineage_identity,
    export_refresh_lineage_certification,
)


def deterministic_refresh_lineage_certification_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_lineage_identity(identity: RefreshLineageIdentity) -> str:
    return deterministic_refresh_lineage_certification_hash(export_lineage_identity(identity))


def hash_lineage_continuity(metadata: RefreshLineageContinuityMetadata) -> str:
    return deterministic_refresh_lineage_certification_hash(export_continuity_metadata(metadata))


def hash_lineage_diagnostics(diagnostics: RefreshLineageDiagnostics) -> str:
    return deterministic_refresh_lineage_certification_hash(export_diagnostics(diagnostics))


def hash_refresh_lineage_certification(certification: RefreshLineageCertification) -> str:
    return deterministic_refresh_lineage_certification_hash(export_refresh_lineage_certification(certification))
