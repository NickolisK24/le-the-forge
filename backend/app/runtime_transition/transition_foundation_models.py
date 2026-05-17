"""Deterministic v3.9 coordination transition foundation models.

The transition foundation layer models deterministic transition identity,
state, provenance, continuity, and immutable evidence records. It does not
execute orchestration, traverse graphs, route work, schedule work, dispatch
work, mutate runtime state, optimize, recommend, rank, score, select,
authorize execution, or create callable orchestration flows.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .transition_foundation_continuity import (
    CONTINUITY_TYPE_EVIDENCE,
    CONTINUITY_TYPE_EXPLAINABILITY,
    CONTINUITY_TYPE_PROVENANCE,
    CONTINUITY_TYPE_REPLAY,
    CONTINUITY_TYPE_ROLLBACK,
    TransitionContinuityChain,
    TransitionContinuityReference,
    export_transition_continuity_chain,
    export_transition_continuity_reference,
)
from .transition_foundation_provenance import (
    TransitionProvenanceReference,
    export_transition_provenance_reference,
)
from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_FOUNDATION_PHASE_ID = "v3_9_transition_foundations"
V3_9_TRANSITION_SCHEMA_VERSION = (
    "v3_9.orchestration_planning_coordination_transition_foundations.1"
)
V3_9_TRANSITION_FOUNDATION_STATUS_STABLE = "v3_9_transition_foundation_stable"
V3_9_TRANSITION_FOUNDATION_STATUS_BLOCKED = "v3_9_transition_foundation_blocked"
V3_9_TRANSITION_PURPOSE = "deterministic_orchestration_planning_coordination_transition_only"
V3_9_TRANSITION_REFERENCE_SCOPE = "coordination_transition_reference_only"
V3_9_TRANSITION_STATE_SCOPE = "coordination_transition_state_reference_only"
V3_9_TRANSITION_EVIDENCE_SCOPE = "coordination_transition_foundation_evidence_only"

TRANSITION_CLASSIFICATION_SUPPORTED = "supported"
TRANSITION_CLASSIFICATION_UNSUPPORTED = "unsupported"
TRANSITION_CLASSIFICATION_PROHIBITED = "prohibited"
TRANSITION_CLASSIFICATION_UNKNOWN = "unknown"
TRANSITION_CLASSIFICATION_INCOMPLETE = "incomplete"
TRANSITION_CLASSIFICATION_BLOCKED = "blocked"
TRANSITION_CLASSIFICATIONS: tuple[str, ...] = (
    TRANSITION_CLASSIFICATION_SUPPORTED,
    TRANSITION_CLASSIFICATION_UNSUPPORTED,
    TRANSITION_CLASSIFICATION_PROHIBITED,
    TRANSITION_CLASSIFICATION_UNKNOWN,
    TRANSITION_CLASSIFICATION_INCOMPLETE,
    TRANSITION_CLASSIFICATION_BLOCKED,
)
FAIL_VISIBLE_TRANSITION_CLASSIFICATIONS: tuple[str, ...] = (
    TRANSITION_CLASSIFICATION_UNSUPPORTED,
    TRANSITION_CLASSIFICATION_PROHIBITED,
    TRANSITION_CLASSIFICATION_UNKNOWN,
    TRANSITION_CLASSIFICATION_INCOMPLETE,
    TRANSITION_CLASSIFICATION_BLOCKED,
)

TRANSITION_VISIBILITY_VISIBLE = "visible"
TRANSITION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
TRANSITION_SEVERITY_INFO = "info"
TRANSITION_SEVERITY_WARNING = "warning"
TRANSITION_SEVERITY_BLOCKED = "blocked"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionIdentity:
    transition_id: str
    schema_version: str = V3_9_TRANSITION_SCHEMA_VERSION
    phase_id: str = V3_9_TRANSITION_FOUNDATION_PHASE_ID
    transition_version: str = "v3.9"
    transition_purpose: str = V3_9_TRANSITION_PURPOSE


@dataclass(frozen=True)
class TransitionReference:
    reference_id: str
    reference_type: str
    subject_id: str
    source_transition_id: str
    artifact_id: str
    deterministic_hash_reference: str
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    reference_scope: str = V3_9_TRANSITION_REFERENCE_SCOPE
    provenance_safe_reference: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_reference_ids",
            "continuity_reference_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionStateReference:
    state_reference_id: str
    classification: str
    state_type: str
    visibility_status: str
    severity: str
    explanation: str
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    evidence_reference_ids: tuple[str, ...]
    state_scope: str = V3_9_TRANSITION_STATE_SCOPE
    fail_visible: bool = True
    hidden: bool = False
    silently_coerced: bool = False
    fallback_applied: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_reference_ids",
            "continuity_reference_ids",
            "evidence_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionEvidenceRecord:
    evidence_record_id: str
    evidence_type: str
    subject_id: str
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = V3_9_TRANSITION_EVIDENCE_SCOPE
    immutable_evidence_record: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    non_executable: bool = True
    runtime_mutation_enabled: bool = False
    execution_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_reference_ids",
            "continuity_reference_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionFoundation:
    identity: TransitionIdentity
    transition_references: tuple[TransitionReference, ...]
    state_references: tuple[TransitionStateReference, ...]
    provenance_references: tuple[TransitionProvenanceReference, ...]
    continuity_references: tuple[TransitionContinuityReference, ...]
    continuity_chains: tuple[TransitionContinuityChain, ...]
    evidence_records: tuple[TransitionEvidenceRecord, ...]
    non_executable: bool = True
    transition_modeling_only: bool = True
    coordination_transition_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    runtime_orchestration_engine_enabled: bool = False
    runtime_state_machine_enabled: bool = False
    transition_execution_handler_enabled: bool = False
    dispatch_pipeline_enabled: bool = False
    orchestration_evaluator_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    authorization_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    hidden_mutation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    implicit_transition_approval_enabled: bool = False
    silent_fallback_enabled: bool = False
    hidden_correction_enabled: bool = False
    inferred_orchestration_action_enabled: bool = False
    production_execution_pathway_enabled: bool = False
    callable_orchestration_flow_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "transition_references",
            "state_references",
            "provenance_references",
            "continuity_references",
            "continuity_chains",
            "evidence_records",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def build_transition_identity(
    transition_id: str = "v3-9-deterministic-coordination-transition-foundation",
    transition_version: str = "v3.9",
) -> TransitionIdentity:
    return TransitionIdentity(transition_id=transition_id, transition_version=transition_version)


def transition_identity_key(identity: TransitionIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.phase_id,
            identity.transition_version,
            identity.transition_id,
        )
    )


def transition_reference_key(reference: TransitionReference) -> str:
    return "|".join(
        (
            reference.reference_scope,
            reference.reference_type,
            reference.subject_id,
            reference.reference_id,
        )
    )


def transition_state_reference_key(reference: TransitionStateReference) -> str:
    return "|".join(
        (
            reference.state_scope,
            reference.classification,
            reference.state_type,
            reference.state_reference_id,
        )
    )


def identity_values_are_unique(values: tuple[str, ...] | list[str]) -> bool:
    return len(values) == len(set(values))


def default_v3_9_transition_foundation() -> TransitionFoundation:
    identity = build_transition_identity()
    provenance = _default_provenance_references()
    continuity = _default_continuity_references(provenance)
    chains = _default_continuity_chains(continuity, provenance)
    evidence = _default_evidence_records(provenance, continuity)
    references = _default_transition_references(identity, provenance, continuity, evidence)
    states = _default_state_references(provenance, continuity, evidence)
    return TransitionFoundation(
        identity=identity,
        transition_references=references,
        state_references=states,
        provenance_references=provenance,
        continuity_references=continuity,
        continuity_chains=chains,
        evidence_records=evidence,
    )


def export_transition_identity(identity: TransitionIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_transition_reference(reference: TransitionReference) -> dict[str, Any]:
    data = asdict(reference)
    for field_name in (
        "provenance_reference_ids",
        "continuity_reference_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_state_reference(reference: TransitionStateReference) -> dict[str, Any]:
    data = asdict(reference)
    for field_name in (
        "provenance_reference_ids",
        "continuity_reference_ids",
        "evidence_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_evidence_record(record: TransitionEvidenceRecord) -> dict[str, Any]:
    data = asdict(record)
    for field_name in (
        "provenance_reference_ids",
        "continuity_reference_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_v3_9_transition_foundation(foundation: TransitionFoundation) -> dict[str, Any]:
    return {
        "identity": export_transition_identity(foundation.identity),
        "transition_references": [
            export_transition_reference(reference)
            for reference in sorted(foundation.transition_references, key=lambda item: item.reference_id)
        ],
        "state_references": [
            export_transition_state_reference(reference)
            for reference in sorted(
                foundation.state_references,
                key=lambda item: (_classification_order(item.classification), item.state_reference_id),
            )
        ],
        "provenance_references": [
            export_transition_provenance_reference(reference)
            for reference in sorted(
                foundation.provenance_references,
                key=lambda item: item.provenance_reference_id,
            )
        ],
        "continuity_references": [
            export_transition_continuity_reference(reference)
            for reference in sorted(
                foundation.continuity_references,
                key=lambda item: item.continuity_reference_id,
            )
        ],
        "continuity_chains": [
            export_transition_continuity_chain(chain)
            for chain in sorted(
                foundation.continuity_chains,
                key=lambda item: (item.deterministic_order, item.continuity_chain_id),
            )
        ],
        "evidence_records": [
            export_transition_evidence_record(record)
            for record in sorted(foundation.evidence_records, key=lambda item: item.evidence_record_id)
        ],
        "non_executable": foundation.non_executable,
        "transition_modeling_only": foundation.transition_modeling_only,
        "coordination_transition_execution_enabled": foundation.coordination_transition_execution_enabled,
        "orchestration_execution_enabled": foundation.orchestration_execution_enabled,
        "orchestration_traversal_enabled": foundation.orchestration_traversal_enabled,
        "routing_enabled": foundation.routing_enabled,
        "scheduling_enabled": foundation.scheduling_enabled,
        "dispatch_enabled": foundation.dispatch_enabled,
        "runtime_orchestration_engine_enabled": foundation.runtime_orchestration_engine_enabled,
        "runtime_state_machine_enabled": foundation.runtime_state_machine_enabled,
        "transition_execution_handler_enabled": foundation.transition_execution_handler_enabled,
        "dispatch_pipeline_enabled": foundation.dispatch_pipeline_enabled,
        "orchestration_evaluator_enabled": foundation.orchestration_evaluator_enabled,
        "optimization_enabled": foundation.optimization_enabled,
        "recommendation_enabled": foundation.recommendation_enabled,
        "ranking_enabled": foundation.ranking_enabled,
        "scoring_enabled": foundation.scoring_enabled,
        "selection_enabled": foundation.selection_enabled,
        "authorization_enabled": foundation.authorization_enabled,
        "autonomous_orchestration_enabled": foundation.autonomous_orchestration_enabled,
        "hidden_mutation_enabled": foundation.hidden_mutation_enabled,
        "runtime_mutation_enabled": foundation.runtime_mutation_enabled,
        "implicit_transition_approval_enabled": foundation.implicit_transition_approval_enabled,
        "silent_fallback_enabled": foundation.silent_fallback_enabled,
        "hidden_correction_enabled": foundation.hidden_correction_enabled,
        "inferred_orchestration_action_enabled": foundation.inferred_orchestration_action_enabled,
        "production_execution_pathway_enabled": foundation.production_execution_pathway_enabled,
        "callable_orchestration_flow_enabled": foundation.callable_orchestration_flow_enabled,
    }


def _classification_order(classification: str) -> int:
    try:
        return TRANSITION_CLASSIFICATIONS.index(classification)
    except ValueError:
        return len(TRANSITION_CLASSIFICATIONS)


def _default_provenance_references() -> tuple[TransitionProvenanceReference, ...]:
    return (
        TransitionProvenanceReference(
            provenance_reference_id="v3_9_transition_foundation_provenance",
            source_coordination_state_id="v3_8_coordination_closeout_ready_for_v3_9",
            destination_coordination_state_id=V3_9_TRANSITION_FOUNDATION_PHASE_ID,
            originating_evidence_ids=(
                "docs/generated/v3_8_closeout_and_v3_9_readiness_report.json",
                "docs/generated/v3_8_coordination_foundations_report.json",
                "docs/generated/v3_8_coordination_continuity_certification_report.json",
            ),
            transition_lineage_ids=(
                "v3_8_coordination_foundations",
                "v3_8_coordination_integrity_enforcement",
                "v3_8_coordination_continuity_certification",
                V3_9_TRANSITION_FOUNDATION_PHASE_ID,
            ),
            continuity_chain_reference_ids=("v3_9_transition_foundation_continuity_chain",),
            deterministic_hash_reference="v3_9_transition_foundation_hash",
        ),
    )


def _default_continuity_references(
    provenance_references: tuple[TransitionProvenanceReference, ...],
) -> tuple[TransitionContinuityReference, ...]:
    provenance_ids = tuple(reference.provenance_reference_id for reference in provenance_references)
    preserved = (
        "v3_8_coordination_foundations_report",
        "v3_8_coordination_closeout_report",
        "v3_9_transition_identity",
        "v3_9_transition_state_modeling",
        "v3_9_transition_provenance",
        "v3_9_transition_continuity",
    )
    specs = (
        (
            "v3_9_transition_replay_continuity",
            CONTINUITY_TYPE_REPLAY,
            ("v3_9_transition_replay_evidence",),
        ),
        (
            "v3_9_transition_rollback_continuity",
            CONTINUITY_TYPE_ROLLBACK,
            ("v3_9_transition_rollback_evidence",),
        ),
        (
            "v3_9_transition_provenance_continuity",
            CONTINUITY_TYPE_PROVENANCE,
            ("v3_9_transition_provenance_evidence",),
        ),
        (
            "v3_9_transition_explainability_continuity",
            CONTINUITY_TYPE_EXPLAINABILITY,
            ("v3_9_transition_explainability_evidence",),
        ),
        (
            "v3_9_transition_evidence_continuity",
            CONTINUITY_TYPE_EVIDENCE,
            ("v3_9_transition_foundation_evidence",),
        ),
    )
    return tuple(
        TransitionContinuityReference(
            continuity_reference_id=reference_id,
            continuity_type=continuity_type,
            preserved_reference_ids=preserved,
            provenance_reference_ids=provenance_ids,
            evidence_reference_ids=evidence_ids,
            deterministic_hash_reference="v3_9_transition_foundation_hash",
        )
        for reference_id, continuity_type, evidence_ids in specs
    )


def _default_continuity_chains(
    continuity_references: tuple[TransitionContinuityReference, ...],
    provenance_references: tuple[TransitionProvenanceReference, ...],
) -> tuple[TransitionContinuityChain, ...]:
    continuity_ids = tuple(reference.continuity_reference_id for reference in continuity_references)
    provenance_ids = tuple(reference.provenance_reference_id for reference in provenance_references)
    return (
        TransitionContinuityChain(
            continuity_chain_id="v3_9_transition_foundation_continuity_chain",
            chain_purpose=(
                "source coordination state to transition identity to state classification "
                "to provenance, replay, rollback, explainability, and evidence continuity"
            ),
            continuity_reference_ids=continuity_ids,
            provenance_reference_ids=provenance_ids,
            replay_reference_ids=("v3_9_transition_replay_continuity",),
            rollback_reference_ids=("v3_9_transition_rollback_continuity",),
            deterministic_order=1,
        ),
    )


def _default_evidence_records(
    provenance_references: tuple[TransitionProvenanceReference, ...],
    continuity_references: tuple[TransitionContinuityReference, ...],
) -> tuple[TransitionEvidenceRecord, ...]:
    provenance_ids = tuple(reference.provenance_reference_id for reference in provenance_references)
    continuity_ids = tuple(reference.continuity_reference_id for reference in continuity_references)
    replay_ids = ("v3_9_transition_replay_continuity",)
    rollback_ids = ("v3_9_transition_rollback_continuity",)
    specs = (
        ("v3_9_transition_identity_evidence", "transition_identity", "v3_9_transition_identity"),
        (
            "v3_9_transition_state_classification_evidence",
            "transition_state_classification",
            "v3_9_transition_state_modeling",
        ),
        (
            "v3_9_transition_provenance_evidence",
            "transition_provenance",
            "v3_9_transition_provenance",
        ),
        (
            "v3_9_transition_continuity_evidence",
            "transition_continuity",
            "v3_9_transition_continuity",
        ),
    )
    return tuple(
        TransitionEvidenceRecord(
            evidence_record_id=evidence_id,
            evidence_type=evidence_type,
            subject_id=subject_id,
            provenance_reference_ids=provenance_ids,
            continuity_reference_ids=continuity_ids,
            replay_reference_ids=replay_ids,
            rollback_reference_ids=rollback_ids,
            deterministic_hash_reference="v3_9_transition_foundation_hash",
        )
        for evidence_id, evidence_type, subject_id in specs
    )


def _default_transition_references(
    identity: TransitionIdentity,
    provenance_references: tuple[TransitionProvenanceReference, ...],
    continuity_references: tuple[TransitionContinuityReference, ...],
    evidence_records: tuple[TransitionEvidenceRecord, ...],
) -> tuple[TransitionReference, ...]:
    provenance_ids = tuple(reference.provenance_reference_id for reference in provenance_references)
    continuity_ids = tuple(reference.continuity_reference_id for reference in continuity_references)
    evidence_ids = tuple(record.evidence_record_id for record in evidence_records)
    specs = (
        (
            "v3_9_transition_ref_v3_8_closeout",
            "source_coordination_state",
            "v3_8_closeout_and_v3_9_readiness",
            "docs/generated/v3_8_closeout_and_v3_9_readiness_report.json",
        ),
        (
            "v3_9_transition_ref_coordination_foundations",
            "source_coordination_foundation",
            "v3_8_coordination_foundations",
            "docs/generated/v3_8_coordination_foundations_report.json",
        ),
        (
            "v3_9_transition_ref_continuity_certification",
            "source_continuity_certification",
            "v3_8_coordination_continuity_certification",
            "docs/generated/v3_8_coordination_continuity_certification_report.json",
        ),
        (
            "v3_9_transition_ref_foundation_evidence",
            "transition_foundation_evidence",
            "v3_9_transition_foundation_evidence_records",
            "backend/app/runtime_transition/transition_foundation_models.py",
        ),
    )
    return tuple(
        TransitionReference(
            reference_id=reference_id,
            reference_type=reference_type,
            subject_id=subject_id,
            source_transition_id=identity.transition_id,
            artifact_id=artifact_id,
            deterministic_hash_reference="v3_9_transition_foundation_hash",
            provenance_reference_ids=provenance_ids,
            continuity_reference_ids=continuity_ids,
            replay_reference_ids=("v3_9_transition_replay_continuity", *evidence_ids),
            rollback_reference_ids=("v3_9_transition_rollback_continuity", *evidence_ids),
        )
        for reference_id, reference_type, subject_id, artifact_id in specs
    )


def _default_state_references(
    provenance_references: tuple[TransitionProvenanceReference, ...],
    continuity_references: tuple[TransitionContinuityReference, ...],
    evidence_records: tuple[TransitionEvidenceRecord, ...],
) -> tuple[TransitionStateReference, ...]:
    provenance_ids = tuple(reference.provenance_reference_id for reference in provenance_references)
    continuity_ids = tuple(reference.continuity_reference_id for reference in continuity_references)
    evidence_ids = tuple(record.evidence_record_id for record in evidence_records)
    specs = (
        (
            "v3_9_transition_state_supported_identity_modeling",
            TRANSITION_CLASSIFICATION_SUPPORTED,
            "deterministic_transition_identity_modeling",
            TRANSITION_VISIBILITY_VISIBLE,
            TRANSITION_SEVERITY_INFO,
            "deterministic transition identities are modeled as immutable evidence",
        ),
        (
            "v3_9_transition_state_unsupported_runtime_coordination_execution",
            TRANSITION_CLASSIFICATION_UNSUPPORTED,
            "runtime_coordination_execution",
            TRANSITION_VISIBILITY_FAIL_VISIBLE,
            TRANSITION_SEVERITY_WARNING,
            "runtime coordination execution is unsupported in v3.9 Phase 1",
        ),
        (
            "v3_9_transition_state_prohibited_orchestration_execution",
            TRANSITION_CLASSIFICATION_PROHIBITED,
            "orchestration_execution",
            TRANSITION_VISIBILITY_FAIL_VISIBLE,
            TRANSITION_SEVERITY_BLOCKED,
            "orchestration execution is prohibited in v3.9 Phase 1",
        ),
        (
            "v3_9_transition_state_unknown_transition_execution_semantics",
            TRANSITION_CLASSIFICATION_UNKNOWN,
            "unknown_transition_execution_semantics",
            TRANSITION_VISIBILITY_FAIL_VISIBLE,
            TRANSITION_SEVERITY_WARNING,
            "unknown transition execution semantics must remain fail-visible",
        ),
        (
            "v3_9_transition_state_incomplete_provenance_reference",
            TRANSITION_CLASSIFICATION_INCOMPLETE,
            "incomplete_provenance_reference",
            TRANSITION_VISIBILITY_FAIL_VISIBLE,
            TRANSITION_SEVERITY_BLOCKED,
            "missing provenance references block transition foundation readiness",
        ),
        (
            "v3_9_transition_state_blocked_hidden_fallback",
            TRANSITION_CLASSIFICATION_BLOCKED,
            "hidden_fallback_or_implicit_transition_approval",
            TRANSITION_VISIBILITY_FAIL_VISIBLE,
            TRANSITION_SEVERITY_BLOCKED,
            "hidden fallback and implicit transition approval remain blocked",
        ),
    )
    return tuple(
        TransitionStateReference(
            state_reference_id=state_reference_id,
            classification=classification,
            state_type=state_type,
            visibility_status=visibility,
            severity=severity,
            explanation=explanation,
            provenance_reference_ids=provenance_ids,
            continuity_reference_ids=continuity_ids,
            evidence_reference_ids=evidence_ids,
        )
        for state_reference_id, classification, state_type, visibility, severity, explanation in specs
    )
