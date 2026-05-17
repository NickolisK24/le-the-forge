"""Deterministic hashing for v4.2 coordination manifest foundations."""

from __future__ import annotations

import hashlib
from typing import Any

from .coordination_manifest_models import (
    CoordinationContinuityReference,
    CoordinationDependencyReference,
    CoordinationLineageReference,
    CoordinationManifest,
    CoordinationManifestIdentity,
)
from .coordination_manifest_serialization import (
    export_coordination_continuity_reference,
    export_coordination_dependency_reference,
    export_coordination_lineage_reference,
    export_coordination_manifest,
    export_coordination_manifest_identity,
    stable_serialize,
)


def deterministic_coordination_manifest_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_manifest_identity(identity: CoordinationManifestIdentity) -> str:
    return deterministic_coordination_manifest_hash(export_coordination_manifest_identity(identity))


def hash_coordination_dependency(reference: CoordinationDependencyReference) -> str:
    return deterministic_coordination_manifest_hash(export_coordination_dependency_reference(reference))


def hash_coordination_lineage(reference: CoordinationLineageReference) -> str:
    return deterministic_coordination_manifest_hash(export_coordination_lineage_reference(reference))


def hash_coordination_continuity(reference: CoordinationContinuityReference) -> str:
    return deterministic_coordination_manifest_hash(export_coordination_continuity_reference(reference))


def hash_coordination_manifest(manifest: CoordinationManifest) -> str:
    return deterministic_coordination_manifest_hash(export_coordination_manifest(manifest))
