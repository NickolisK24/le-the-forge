"""Deterministic equality helpers for v4.0 patch lifecycle foundations."""

from __future__ import annotations

from typing import Any

from .lifecycle_models import PatchIdentity, PatchLifecycleFoundation
from .lifecycle_serialization import (
    export_patch_identity,
    export_patch_lifecycle_foundation,
    stable_serialize,
)


def lifecycle_payloads_equal(left: Any, right: Any) -> bool:
    return stable_serialize(left) == stable_serialize(right)


def patch_identities_equal(left: PatchIdentity, right: PatchIdentity) -> bool:
    return stable_serialize(export_patch_identity(left)) == stable_serialize(export_patch_identity(right))


def patch_lifecycle_foundations_equal(left: PatchLifecycleFoundation, right: PatchLifecycleFoundation) -> bool:
    return stable_serialize(export_patch_lifecycle_foundation(left)) == stable_serialize(
        export_patch_lifecycle_foundation(right)
    )
