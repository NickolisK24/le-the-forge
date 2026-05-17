"""Stable hashing for v4.1 refresh sequencing visibility evidence."""

from __future__ import annotations

from typing import Any

from operational_lifecycle.lifecycle_hashing import deterministic_lifecycle_hash

from .refresh_sequencing_visibility_models import (
    RefreshSequencingContinuityMetadata,
    RefreshSequencingDiagnostics,
    RefreshSequencingIdentity,
    RefreshSequencingVisibility,
)
from .refresh_sequencing_visibility_serialization import (
    _export_record,
    export_refresh_sequencing_identity,
    export_refresh_sequencing_visibility,
)


def deterministic_refresh_sequencing_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_refresh_sequencing_identity(identity: RefreshSequencingIdentity) -> str:
    return deterministic_refresh_sequencing_hash(export_refresh_sequencing_identity(identity))


def hash_refresh_sequencing_continuity(metadata: RefreshSequencingContinuityMetadata) -> str:
    return deterministic_refresh_sequencing_hash(_export_record(metadata))


def hash_refresh_sequencing_diagnostics(diagnostics: RefreshSequencingDiagnostics) -> str:
    return deterministic_refresh_sequencing_hash(_export_record(diagnostics))


def hash_refresh_sequencing_visibility(visibility: RefreshSequencingVisibility) -> str:
    return deterministic_refresh_sequencing_hash(export_refresh_sequencing_visibility(visibility))
