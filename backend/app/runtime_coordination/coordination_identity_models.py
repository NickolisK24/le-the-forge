"""Deterministic identity and boundary models for v3.8 coordination foundations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V3_8_COORDINATION_SCHEMA_VERSION = "v3_8.orchestration_planning_coordination_foundations.1"
V3_8_COORDINATION_FOUNDATION_PHASE_ID = "v3_8_coordination_foundations"
V3_8_COORDINATION_PLANNING_ONLY = "deterministic_orchestration_planning_coordination_only"
V3_8_COORDINATION_REFERENCE_SCOPE = "planning_coordination_reference_only"
V3_8_COORDINATION_BOUNDARY_VISIBLE = "visible"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V38CoordinationIdentity:
    coordination_id: str
    schema_version: str = V3_8_COORDINATION_SCHEMA_VERSION
    phase_id: str = V3_8_COORDINATION_FOUNDATION_PHASE_ID
    coordination_version: str = "v3.8"
    coordination_purpose: str = V3_8_COORDINATION_PLANNING_ONLY


@dataclass(frozen=True)
class V38CoordinationReference:
    reference_id: str
    reference_type: str
    subject_id: str
    source_phase_id: str
    artifact_id: str
    deterministic_hash_reference: str
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    reference_scope: str = V3_8_COORDINATION_REFERENCE_SCOPE

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_reference_ids",
            "continuity_reference_ids",
            "explainability_reference_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationBoundary:
    boundary_id: str
    boundary_type: str
    boundary_status: str
    restriction_summary: str
    unsupported_state_ids: tuple[str, ...]
    prohibited_state_ids: tuple[str, ...]
    unknown_state_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    fail_visible: bool = True
    execution_capability_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_state_ids",
            "prohibited_state_ids",
            "unknown_state_ids",
            "provenance_reference_ids",
            "explainability_reference_ids",
        ):
            _set_tuple_field(self, field_name)


def build_v3_8_coordination_identity(
    coordination_id: str = "v3-8-deterministic-coordination-foundation",
    coordination_version: str = "v3.8",
) -> V38CoordinationIdentity:
    return V38CoordinationIdentity(
        coordination_id=coordination_id,
        coordination_version=coordination_version,
    )


def coordination_identity_key(identity: V38CoordinationIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.phase_id,
            identity.coordination_version,
            identity.coordination_id,
        )
    )


def coordination_reference_key(reference: V38CoordinationReference) -> str:
    return "|".join(
        (
            reference.reference_scope,
            reference.reference_type,
            reference.subject_id,
            reference.reference_id,
        )
    )


def coordination_boundary_key(boundary: V38CoordinationBoundary) -> str:
    return "|".join((boundary.boundary_type, boundary.boundary_status, boundary.boundary_id))


def identity_values_are_unique(values: tuple[str, ...] | list[str]) -> bool:
    return len(values) == len(set(values))
