"""Deterministic hashing helpers for v4.0 patch lifecycle foundations."""

from __future__ import annotations

import hashlib
from typing import Any

from .lifecycle_models import (
    LifecycleLineageRecord,
    LifecycleProvenanceRecord,
    LifecycleState,
    LifecycleVisibilityRecord,
    PatchIdentity,
    PatchLifecycleFoundation,
    PatchOperationalMetadata,
)
from .lifecycle_serialization import (
    export_lifecycle_lineage_record,
    export_lifecycle_provenance_record,
    export_lifecycle_state,
    export_lifecycle_visibility_record,
    export_patch_identity,
    export_patch_lifecycle_foundation,
    export_patch_operational_metadata,
    stable_serialize,
)


def deterministic_lifecycle_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_lifecycle_payload(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_patch_identity(identity: PatchIdentity) -> str:
    return deterministic_lifecycle_hash(export_patch_identity(identity))


def hash_lifecycle_state(state: LifecycleState) -> str:
    return deterministic_lifecycle_hash(export_lifecycle_state(state))


def hash_lifecycle_provenance_record(record: LifecycleProvenanceRecord) -> str:
    return deterministic_lifecycle_hash(export_lifecycle_provenance_record(record))


def hash_lifecycle_lineage_record(record: LifecycleLineageRecord) -> str:
    return deterministic_lifecycle_hash(export_lifecycle_lineage_record(record))


def hash_lifecycle_visibility_record(record: LifecycleVisibilityRecord) -> str:
    return deterministic_lifecycle_hash(export_lifecycle_visibility_record(record))


def hash_patch_operational_metadata(metadata: PatchOperationalMetadata) -> str:
    return deterministic_lifecycle_hash(export_patch_operational_metadata(metadata))


def hash_patch_lifecycle_foundation(foundation: PatchLifecycleFoundation) -> str:
    return deterministic_lifecycle_hash(export_patch_lifecycle_foundation(foundation))
