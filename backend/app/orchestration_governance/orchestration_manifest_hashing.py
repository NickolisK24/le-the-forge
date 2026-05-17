"""Deterministic hashing for v4.3 orchestration manifest foundations."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_manifest_models import (
    OrchestrationBoundaryVisibility,
    OrchestrationCapabilityVisibility,
    OrchestrationContinuityMetadata,
    OrchestrationExplainabilitySummary,
    OrchestrationManifest,
    OrchestrationManifestDiagnostic,
    OrchestrationManifestIdentity,
)
from .orchestration_manifest_serialization import (
    export_orchestration_boundary_visibility,
    export_orchestration_capability_visibility,
    export_orchestration_continuity_metadata,
    export_orchestration_explainability_summary,
    export_orchestration_manifest,
    export_orchestration_manifest_diagnostic,
    export_orchestration_manifest_identity,
    stable_serialize,
)


def deterministic_orchestration_manifest_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_orchestration_manifest_identity(identity: OrchestrationManifestIdentity) -> str:
    return deterministic_orchestration_manifest_hash(export_orchestration_manifest_identity(identity))


def hash_orchestration_capability_visibility(visibility: OrchestrationCapabilityVisibility) -> str:
    return deterministic_orchestration_manifest_hash(export_orchestration_capability_visibility(visibility))


def hash_orchestration_boundary_visibility(visibility: OrchestrationBoundaryVisibility) -> str:
    return deterministic_orchestration_manifest_hash(export_orchestration_boundary_visibility(visibility))


def hash_orchestration_continuity_metadata(metadata: OrchestrationContinuityMetadata) -> str:
    return deterministic_orchestration_manifest_hash(export_orchestration_continuity_metadata(metadata))


def hash_orchestration_manifest_diagnostic(diagnostic: OrchestrationManifestDiagnostic) -> str:
    return deterministic_orchestration_manifest_hash(export_orchestration_manifest_diagnostic(diagnostic))


def hash_orchestration_explainability_summary(summary: OrchestrationExplainabilitySummary) -> str:
    return deterministic_orchestration_manifest_hash(export_orchestration_explainability_summary(summary))


def hash_orchestration_manifest(manifest: OrchestrationManifest) -> str:
    return deterministic_orchestration_manifest_hash(export_orchestration_manifest(manifest))
