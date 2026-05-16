"""Deterministic relationship models for v3.8 coordination foundations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V3_8_COORDINATION_RELATIONSHIP_STRUCTURAL_ONLY = "structural_coordination_relationship_only"
V3_8_COORDINATION_CHAIN_STRUCTURAL_ONLY = "structural_coordination_chain_only"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V38CoordinationRelationship:
    relationship_id: str
    relationship_type: str
    source_coordination_id: str
    target_coordination_id: str
    relationship_purpose: str
    continuity_reference_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    unsupported_state_ids: tuple[str, ...]
    prohibited_state_ids: tuple[str, ...]
    deterministic_order: int
    relationship_scope: str = V3_8_COORDINATION_RELATIONSHIP_STRUCTURAL_ONLY
    relationship_executable: bool = False
    traversal_enabled: bool = False
    dispatch_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "continuity_reference_ids",
            "provenance_reference_ids",
            "explainability_reference_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
            "unsupported_state_ids",
            "prohibited_state_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationRelationshipChain:
    chain_id: str
    chain_purpose: str
    relationship_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    provenance_lineage_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    deterministic_order: int
    chain_scope: str = V3_8_COORDINATION_CHAIN_STRUCTURAL_ONLY
    chain_executable: bool = False
    traversal_execution_enabled: bool = False
    hidden_transition_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "relationship_ids",
            "continuity_reference_ids",
            "provenance_lineage_ids",
            "explainability_reference_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


def coordination_relationship_key(relationship: V38CoordinationRelationship) -> str:
    return "|".join(
        (
            relationship.relationship_type,
            relationship.source_coordination_id,
            relationship.target_coordination_id,
            relationship.relationship_id,
        )
    )


def coordination_relationship_chain_key(chain: V38CoordinationRelationshipChain) -> str:
    return "|".join((chain.chain_scope, chain.chain_id, str(chain.deterministic_order)))
