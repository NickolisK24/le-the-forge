"""Stable hashing for v4.1 refresh manifest foundation evidence."""

from __future__ import annotations

from typing import Any

from operational_lifecycle.lifecycle_hashing import deterministic_lifecycle_hash

from .refresh_manifest_models import (
    RefreshManifest,
    RefreshManifestContinuityMetadata,
    RefreshManifestDiagnosticsVisibility,
    RefreshManifestIdentity,
)
from .refresh_manifest_serialization import (
    export_continuity_metadata,
    export_diagnostics_visibility,
    export_refresh_manifest,
    export_refresh_manifest_identity,
)


def deterministic_refresh_manifest_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_refresh_manifest_identity(identity: RefreshManifestIdentity) -> str:
    return deterministic_refresh_manifest_hash(export_refresh_manifest_identity(identity))


def hash_refresh_manifest_continuity(metadata: RefreshManifestContinuityMetadata) -> str:
    return deterministic_refresh_manifest_hash(export_continuity_metadata(metadata))


def hash_refresh_manifest_diagnostics(record: RefreshManifestDiagnosticsVisibility) -> str:
    return deterministic_refresh_manifest_hash(export_diagnostics_visibility(record))


def hash_refresh_manifest(manifest: RefreshManifest) -> str:
    return deterministic_refresh_manifest_hash(export_refresh_manifest(manifest))
