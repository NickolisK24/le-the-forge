"""Deterministic visibility models for v3.5 orchestration governance planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


@dataclass(frozen=True)
class OrchestrationVisibilityModel:
    visibility_id: str
    orchestration_status_visible: bool
    unsupported_state_visible: bool
    governance_dependency_visible: bool
    authorization_visible: bool
    replay_lineage_visible: bool
    rollback_lineage_visible: bool
    compatibility_visible: bool
    orchestration_limitation_visible: bool
    explanation_required: bool
    auditability_required: bool


def default_orchestration_visibility_model() -> OrchestrationVisibilityModel:
    return OrchestrationVisibilityModel(
        visibility_id="v3-5-governance-consumption-visibility",
        orchestration_status_visible=True,
        unsupported_state_visible=True,
        governance_dependency_visible=True,
        authorization_visible=True,
        replay_lineage_visible=True,
        rollback_lineage_visible=True,
        compatibility_visible=True,
        orchestration_limitation_visible=True,
        explanation_required=True,
        auditability_required=True,
    )


def export_orchestration_visibility(visibility: OrchestrationVisibilityModel) -> dict[str, Any]:
    return asdict(visibility)


def serialize_orchestration_visibility(visibility: OrchestrationVisibilityModel) -> str:
    return stable_serialize(export_orchestration_visibility(visibility))


def hash_orchestration_visibility(visibility: OrchestrationVisibilityModel) -> str:
    return deterministic_hash(export_orchestration_visibility(visibility))
