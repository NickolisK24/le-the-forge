"""Deterministic provenance references for v3.9 transition foundations.

The provenance model stores immutable source and lineage references only. It
does not infer provenance, correct missing provenance, approve transitions, or
execute orchestration behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_PROVENANCE_PRESERVED = "transition_provenance_preserved"
V3_9_TRANSITION_PROVENANCE_SCOPE = "coordination_transition_provenance_reference_only"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionProvenanceReference:
    provenance_reference_id: str
    source_coordination_state_id: str
    destination_coordination_state_id: str
    originating_evidence_ids: tuple[str, ...]
    transition_lineage_ids: tuple[str, ...]
    continuity_chain_reference_ids: tuple[str, ...]
    deterministic_hash_reference: str
    provenance_status: str = V3_9_TRANSITION_PROVENANCE_PRESERVED
    provenance_scope: str = V3_9_TRANSITION_PROVENANCE_SCOPE
    provenance_preserved: bool = True
    inferred_provenance_allowed: bool = False
    no_inferred_provenance: bool = True
    fail_visible: bool = True
    hidden: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "originating_evidence_ids",
            "transition_lineage_ids",
            "continuity_chain_reference_ids",
        ):
            _set_tuple_field(self, field_name)


def transition_provenance_key(reference: TransitionProvenanceReference) -> str:
    return "|".join(
        (
            reference.provenance_scope,
            reference.source_coordination_state_id,
            reference.destination_coordination_state_id,
            reference.provenance_reference_id,
        )
    )


def export_transition_provenance_reference(
    reference: TransitionProvenanceReference,
) -> dict[str, Any]:
    data = asdict(reference)
    for field_name in (
        "originating_evidence_ids",
        "transition_lineage_ids",
        "continuity_chain_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data
