"""Deterministic hashing for v4.2 coordination lineage chain governance."""

from __future__ import annotations

import hashlib
from typing import Any

from .coordination_lineage_chain_models import (
    ConflictingLineageVisibility,
    CoordinationLineageChain,
    CoordinationLineageChainIdentity,
    CoordinationLineageChainRecord,
    DependencyGraphLineageChainReference,
    LineagePredecessorReference,
    LineageSourceReference,
    LineageSuccessorReference,
    ManifestLineageChainReference,
    MissingLineageVisibility,
    ProhibitedLineageMutationVisibility,
    StaleLineageVisibility,
    UnsupportedLineageTransitionVisibility,
)
from .coordination_lineage_chain_serialization import (
    export_conflicting_lineage_visibility,
    export_coordination_lineage_chain,
    export_coordination_lineage_chain_identity,
    export_coordination_lineage_chain_record,
    export_dependency_graph_lineage_chain_reference,
    export_lineage_predecessor_reference,
    export_lineage_source_reference,
    export_lineage_successor_reference,
    export_manifest_lineage_chain_reference,
    export_missing_lineage_visibility,
    export_prohibited_lineage_mutation_visibility,
    export_stale_lineage_visibility,
    export_unsupported_lineage_transition_visibility,
    stable_serialize,
)


def deterministic_coordination_lineage_chain_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_lineage_chain_identity(identity: CoordinationLineageChainIdentity) -> str:
    return deterministic_coordination_lineage_chain_hash(export_coordination_lineage_chain_identity(identity))


def hash_lineage_source_reference(reference: LineageSourceReference) -> str:
    return deterministic_coordination_lineage_chain_hash(export_lineage_source_reference(reference))


def hash_lineage_predecessor_reference(reference: LineagePredecessorReference) -> str:
    return deterministic_coordination_lineage_chain_hash(export_lineage_predecessor_reference(reference))


def hash_lineage_successor_reference(reference: LineageSuccessorReference) -> str:
    return deterministic_coordination_lineage_chain_hash(export_lineage_successor_reference(reference))


def hash_manifest_lineage_chain_reference(reference: ManifestLineageChainReference) -> str:
    return deterministic_coordination_lineage_chain_hash(export_manifest_lineage_chain_reference(reference))


def hash_dependency_graph_lineage_chain_reference(reference: DependencyGraphLineageChainReference) -> str:
    return deterministic_coordination_lineage_chain_hash(export_dependency_graph_lineage_chain_reference(reference))


def hash_coordination_lineage_chain_record(record: CoordinationLineageChainRecord) -> str:
    return deterministic_coordination_lineage_chain_hash(export_coordination_lineage_chain_record(record))


def hash_stale_lineage_visibility(visibility: StaleLineageVisibility) -> str:
    return deterministic_coordination_lineage_chain_hash(export_stale_lineage_visibility(visibility))


def hash_missing_lineage_visibility(visibility: MissingLineageVisibility) -> str:
    return deterministic_coordination_lineage_chain_hash(export_missing_lineage_visibility(visibility))


def hash_conflicting_lineage_visibility(visibility: ConflictingLineageVisibility) -> str:
    return deterministic_coordination_lineage_chain_hash(export_conflicting_lineage_visibility(visibility))


def hash_prohibited_lineage_mutation_visibility(visibility: ProhibitedLineageMutationVisibility) -> str:
    return deterministic_coordination_lineage_chain_hash(export_prohibited_lineage_mutation_visibility(visibility))


def hash_unsupported_lineage_transition_visibility(visibility: UnsupportedLineageTransitionVisibility) -> str:
    return deterministic_coordination_lineage_chain_hash(export_unsupported_lineage_transition_visibility(visibility))


def hash_coordination_lineage_chain(chain: CoordinationLineageChain) -> str:
    return deterministic_coordination_lineage_chain_hash(export_coordination_lineage_chain(chain))
