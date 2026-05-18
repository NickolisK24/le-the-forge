"""Deterministic hashing for v4.3 orchestration capability visibility."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_capability_models import (
    CapabilityDiagnostic,
    CapabilityExplainability,
    CapabilityGovernanceBoundary,
    CapabilityRecord,
    CapabilityRelationship,
    CapabilityVisibilityIdentity,
    OrchestrationCapabilityVisibility,
)
from .orchestration_capability_serialization import (
    export_capability_boundary,
    export_capability_diagnostic,
    export_capability_explainability,
    export_capability_record,
    export_capability_relationship,
    export_capability_visibility_identity,
    export_orchestration_capability_visibility,
    stable_serialize,
)


def deterministic_capability_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_capability_visibility_identity(identity: CapabilityVisibilityIdentity) -> str:
    return deterministic_capability_hash(export_capability_visibility_identity(identity))


def hash_capability_record(capability: CapabilityRecord) -> str:
    return deterministic_capability_hash(export_capability_record(capability))


def hash_capability_boundary(boundary: CapabilityGovernanceBoundary) -> str:
    return deterministic_capability_hash(export_capability_boundary(boundary))


def hash_capability_relationship(relationship: CapabilityRelationship) -> str:
    return deterministic_capability_hash(export_capability_relationship(relationship))


def hash_capability_diagnostic(diagnostic: CapabilityDiagnostic) -> str:
    return deterministic_capability_hash(export_capability_diagnostic(diagnostic))


def hash_capability_explainability(summary: CapabilityExplainability) -> str:
    return deterministic_capability_hash(export_capability_explainability(summary))


def hash_orchestration_capability_visibility(visibility: OrchestrationCapabilityVisibility) -> str:
    return deterministic_capability_hash(export_orchestration_capability_visibility(visibility))
