"""Patch lifecycle identity normalization for v4.0 foundations.

Normalization is deterministic field representation only. It does not infer,
correct, authorize, transition, or mutate lifecycle state.
"""

from __future__ import annotations

from .lifecycle_models import PatchIdentity, default_patch_identity
from .lifecycle_serialization import export_patch_identity


def lifecycle_identity_key(identity: PatchIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.lifecycle_generation,
            identity.patch_version,
            identity.extraction_version,
            identity.provenance_reference,
            identity.lineage_reference,
        )
    )


def normalize_patch_identity(identity: PatchIdentity) -> PatchIdentity:
    exported = export_patch_identity(identity)
    return PatchIdentity(**exported)


def patch_identity_normalization_report(identity: PatchIdentity) -> dict[str, object]:
    normalized = normalize_patch_identity(identity)
    return {
        "normalization_scope": "deterministic_field_representation_only",
        "identity_key": lifecycle_identity_key(normalized),
        "normalized_identity": export_patch_identity(normalized),
        "field_count": len(export_patch_identity(normalized)),
        "omitted_field_count": 0,
        "silent_correction_enabled": False,
        "hidden_fallback_enabled": False,
        "runtime_mutation_enabled": normalized.runtime_mutation_enabled,
        "lifecycle_execution_enabled": normalized.lifecycle_execution_enabled,
    }


def build_default_patch_identity() -> PatchIdentity:
    return default_patch_identity()
