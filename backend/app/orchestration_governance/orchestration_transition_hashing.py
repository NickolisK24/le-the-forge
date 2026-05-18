"""Deterministic hashing for v4.3 orchestration transition visibility."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_transition_models import (
    OrchestrationTransitionVisibility,
    TransitionDiagnostic,
    TransitionExplainability,
    TransitionRecord,
    TransitionRelationship,
    TransitionVisibilityIdentity,
)
from .orchestration_transition_serialization import (
    export_orchestration_transition_visibility,
    export_transition_diagnostic,
    export_transition_explainability,
    export_transition_record,
    export_transition_relationship,
    export_transition_visibility_identity,
    stable_serialize,
)


def deterministic_transition_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_transition_visibility_identity(identity: TransitionVisibilityIdentity) -> str:
    return deterministic_transition_hash(export_transition_visibility_identity(identity))


def hash_transition_record(transition: TransitionRecord) -> str:
    return deterministic_transition_hash(export_transition_record(transition))


def hash_transition_relationship(relationship: TransitionRelationship) -> str:
    return deterministic_transition_hash(export_transition_relationship(relationship))


def hash_transition_diagnostic(diagnostic: TransitionDiagnostic) -> str:
    return deterministic_transition_hash(export_transition_diagnostic(diagnostic))


def hash_transition_explainability(summary: TransitionExplainability) -> str:
    return deterministic_transition_hash(export_transition_explainability(summary))


def hash_orchestration_transition_visibility(visibility: OrchestrationTransitionVisibility) -> str:
    return deterministic_transition_hash(export_orchestration_transition_visibility(visibility))
