"""Deterministic continuity references for v3.9 transition foundations.

Continuity references are immutable evidence chains only. They do not traverse,
dispatch, route, schedule, select, authorize, mutate, or execute transitions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_CONTINUITY_PRESERVED = "transition_continuity_preserved"
V3_9_TRANSITION_CONTINUITY_REFERENCE_SCOPE = "coordination_transition_continuity_reference_only"
V3_9_TRANSITION_CONTINUITY_CHAIN_SCOPE = "coordination_transition_continuity_chain_only"

CONTINUITY_TYPE_REPLAY = "replay_continuity"
CONTINUITY_TYPE_ROLLBACK = "rollback_continuity"
CONTINUITY_TYPE_PROVENANCE = "provenance_continuity"
CONTINUITY_TYPE_EXPLAINABILITY = "explainability_continuity"
CONTINUITY_TYPE_EVIDENCE = "evidence_continuity"
TRANSITION_CONTINUITY_TYPES: tuple[str, ...] = (
    CONTINUITY_TYPE_REPLAY,
    CONTINUITY_TYPE_ROLLBACK,
    CONTINUITY_TYPE_PROVENANCE,
    CONTINUITY_TYPE_EXPLAINABILITY,
    CONTINUITY_TYPE_EVIDENCE,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionContinuityReference:
    continuity_reference_id: str
    continuity_type: str
    preserved_reference_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    evidence_reference_ids: tuple[str, ...]
    deterministic_hash_reference: str
    continuity_status: str = V3_9_TRANSITION_CONTINUITY_PRESERVED
    continuity_scope: str = V3_9_TRANSITION_CONTINUITY_REFERENCE_SCOPE
    immutable_chain: bool = True
    continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    runtime_replay_enabled: bool = False
    rollback_execution_enabled: bool = False
    fail_visible_gap_ids: tuple[str, ...] = ()
    fail_visible: bool = True
    hidden: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "preserved_reference_ids",
            "provenance_reference_ids",
            "evidence_reference_ids",
            "fail_visible_gap_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionContinuityChain:
    continuity_chain_id: str
    chain_purpose: str
    continuity_reference_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    deterministic_order: int
    chain_scope: str = V3_9_TRANSITION_CONTINUITY_CHAIN_SCOPE
    immutable_chain: bool = True
    chain_executable: bool = False
    traversal_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    hidden_transition_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "continuity_reference_ids",
            "provenance_reference_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


def transition_continuity_reference_key(reference: TransitionContinuityReference) -> str:
    return "|".join(
        (
            reference.continuity_scope,
            reference.continuity_type,
            reference.continuity_reference_id,
        )
    )


def transition_continuity_chain_key(chain: TransitionContinuityChain) -> str:
    return "|".join((chain.chain_scope, chain.continuity_chain_id, str(chain.deterministic_order)))


def export_transition_continuity_reference(
    reference: TransitionContinuityReference,
) -> dict[str, Any]:
    data = asdict(reference)
    for field_name in (
        "preserved_reference_ids",
        "provenance_reference_ids",
        "evidence_reference_ids",
        "fail_visible_gap_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_continuity_chain(chain: TransitionContinuityChain) -> dict[str, Any]:
    data = asdict(chain)
    for field_name in (
        "continuity_reference_ids",
        "provenance_reference_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data
