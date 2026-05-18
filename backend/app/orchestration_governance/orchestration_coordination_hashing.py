"""Deterministic hashing for v4.3 orchestration coordination visibility."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_coordination_models import (
    CoordinationDiagnostic,
    CoordinationExplainability,
    CoordinationParticipant,
    CoordinationRecord,
    CoordinationRelationship,
    CoordinationVisibilityIdentity,
    OrchestrationCoordinationVisibility,
)
from .orchestration_coordination_serialization import (
    export_coordination_diagnostic,
    export_coordination_explainability,
    export_coordination_participant,
    export_coordination_record,
    export_coordination_relationship,
    export_coordination_visibility_identity,
    export_orchestration_coordination_visibility,
    stable_serialize,
)


def deterministic_coordination_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_visibility_identity(identity: CoordinationVisibilityIdentity) -> str:
    return deterministic_coordination_hash(export_coordination_visibility_identity(identity))


def hash_coordination_record(coordination: CoordinationRecord) -> str:
    return deterministic_coordination_hash(export_coordination_record(coordination))


def hash_coordination_participant(participant: CoordinationParticipant) -> str:
    return deterministic_coordination_hash(export_coordination_participant(participant))


def hash_coordination_relationship(relationship: CoordinationRelationship) -> str:
    return deterministic_coordination_hash(export_coordination_relationship(relationship))


def hash_coordination_diagnostic(diagnostic: CoordinationDiagnostic) -> str:
    return deterministic_coordination_hash(export_coordination_diagnostic(diagnostic))


def hash_coordination_explainability(summary: CoordinationExplainability) -> str:
    return deterministic_coordination_hash(export_coordination_explainability(summary))


def hash_orchestration_coordination_visibility(visibility: OrchestrationCoordinationVisibility) -> str:
    return deterministic_coordination_hash(export_orchestration_coordination_visibility(visibility))
