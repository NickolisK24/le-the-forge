"""Deterministic continuity evidence models for v3.8 coordination foundations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V3_8_COORDINATION_CONTINUITY_PRESERVED = "coordination_continuity_preserved"
V3_8_COORDINATION_PROVENANCE_PRESERVED = "coordination_provenance_preserved"
V3_8_COORDINATION_EXPLAINABILITY_VISIBLE = "coordination_explainability_visible"
V3_8_COORDINATION_INTEGRITY_PRESERVED = "coordination_integrity_preserved"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V38CoordinationContinuityState:
    continuity_id: str
    continuity_status: str
    preserved_reference_ids: tuple[str, ...]
    relationship_chain_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    fail_visible_gap_ids: tuple[str, ...] = ()
    continuity_preserved: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "preserved_reference_ids",
            "relationship_chain_ids",
            "replay_evidence_ids",
            "rollback_evidence_ids",
            "provenance_reference_ids",
            "explainability_reference_ids",
            "deterministic_hash_references",
            "fail_visible_gap_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationProvenanceState:
    provenance_id: str
    provenance_status: str
    source_phase_id: str
    source_artifact_id: str
    lineage_reference_ids: tuple[str, ...]
    prior_phase_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    deterministic_lineage_hash_reference: str
    provenance_preserved: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "lineage_reference_ids",
            "prior_phase_reference_ids",
            "continuity_reference_ids",
            "explainability_reference_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationExplainabilityState:
    explainability_id: str
    explainability_status: str
    subject_id: str
    visibility_chain_ids: tuple[str, ...]
    unsupported_state_ids: tuple[str, ...]
    prohibited_state_ids: tuple[str, ...]
    unknown_state_ids: tuple[str, ...]
    explanation: str
    provenance_reference_ids: tuple[str, ...]
    fail_visible: bool = True
    hidden_state: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "visibility_chain_ids",
            "unsupported_state_ids",
            "prohibited_state_ids",
            "unknown_state_ids",
            "provenance_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationIntegrityState:
    integrity_id: str
    integrity_status: str
    unsupported_state_ids: tuple[str, ...]
    prohibited_state_ids: tuple[str, ...]
    unknown_state_ids: tuple[str, ...]
    execution_boundary_violation_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    explainability_reference_ids: tuple[str, ...]
    silent_fallback_detected: bool = False
    hidden_transition_detected: bool = False
    integrity_preserved: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_state_ids",
            "prohibited_state_ids",
            "unknown_state_ids",
            "execution_boundary_violation_ids",
            "provenance_reference_ids",
            "explainability_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationReplayEvidence:
    replay_evidence_id: str
    subject_id: str
    replay_scope: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    replay_safe: bool = True
    runtime_replay_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_reference_ids",
            "deterministic_hash_references",
            "continuity_reference_ids",
            "provenance_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationRollbackEvidence:
    rollback_evidence_id: str
    subject_id: str
    rollback_scope: str
    rollback_reference_ids: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    rollback_safe: bool = True
    rollback_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "rollback_reference_ids",
            "deterministic_hash_references",
            "continuity_reference_ids",
            "provenance_reference_ids",
        ):
            _set_tuple_field(self, field_name)
