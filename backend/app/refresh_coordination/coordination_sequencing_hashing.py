"""Deterministic hashing for v4.2 coordination sequencing intelligence."""

from __future__ import annotations

import hashlib
from typing import Any

from .coordination_sequencing_models import (
    CoordinationSequenceRecord,
    CoordinationSequencingIdentity,
    CoordinationSequencingIntelligence,
    DependencyGraphSequenceReference,
    LineageSequenceReference,
    ManifestSequenceReference,
    NonExecutableSequenceOrderingVisibility,
    SequenceStateVisibility,
    SequenceStepIdentity,
)
from .coordination_sequencing_serialization import (
    export_coordination_sequence_record,
    export_coordination_sequencing_identity,
    export_coordination_sequencing_intelligence,
    export_dependency_graph_sequence_reference,
    export_lineage_sequence_reference,
    export_manifest_sequence_reference,
    export_non_executable_sequence_ordering_visibility,
    export_sequence_state_visibility,
    export_sequence_step_identity,
    stable_serialize,
)


def deterministic_coordination_sequencing_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_sequencing_identity(identity: CoordinationSequencingIdentity) -> str:
    return deterministic_coordination_sequencing_hash(export_coordination_sequencing_identity(identity))


def hash_sequence_step_identity(step: SequenceStepIdentity) -> str:
    return deterministic_coordination_sequencing_hash(export_sequence_step_identity(step))


def hash_manifest_sequence_reference(reference: ManifestSequenceReference) -> str:
    return deterministic_coordination_sequencing_hash(export_manifest_sequence_reference(reference))


def hash_dependency_graph_sequence_reference(reference: DependencyGraphSequenceReference) -> str:
    return deterministic_coordination_sequencing_hash(export_dependency_graph_sequence_reference(reference))


def hash_lineage_sequence_reference(reference: LineageSequenceReference) -> str:
    return deterministic_coordination_sequencing_hash(export_lineage_sequence_reference(reference))


def hash_coordination_sequence_record(record: CoordinationSequenceRecord) -> str:
    return deterministic_coordination_sequencing_hash(export_coordination_sequence_record(record))


def hash_sequence_state_visibility(visibility: SequenceStateVisibility) -> str:
    return deterministic_coordination_sequencing_hash(export_sequence_state_visibility(visibility))


def hash_non_executable_sequence_ordering_visibility(visibility: NonExecutableSequenceOrderingVisibility) -> str:
    return deterministic_coordination_sequencing_hash(export_non_executable_sequence_ordering_visibility(visibility))


def hash_coordination_sequencing_intelligence(sequencing: CoordinationSequencingIntelligence) -> str:
    return deterministic_coordination_sequencing_hash(export_coordination_sequencing_intelligence(sequencing))
