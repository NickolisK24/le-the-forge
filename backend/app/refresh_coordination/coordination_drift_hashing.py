"""Deterministic hashing for v4.2 coordination drift certification."""

from __future__ import annotations

import hashlib
from typing import Any

from .coordination_drift_models import (
    CoordinationDriftCertification,
    CoordinationDriftIdentity,
    CoordinationDriftRecord,
    CrossLayerDriftVisibility,
    DependencyGraphDriftReference,
    DriftStateVisibility,
    LineageDriftReference,
    ManifestDriftReference,
    RoutingDriftReference,
    SequencingDriftReference,
)
from .coordination_drift_serialization import (
    export_coordination_drift_certification,
    export_coordination_drift_identity,
    export_coordination_drift_record,
    export_cross_layer_drift_visibility,
    export_dependency_graph_drift_reference,
    export_drift_state_visibility,
    export_lineage_drift_reference,
    export_manifest_drift_reference,
    export_routing_drift_reference,
    export_sequencing_drift_reference,
    stable_serialize,
)


def deterministic_coordination_drift_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_drift_identity(identity: CoordinationDriftIdentity) -> str:
    return deterministic_coordination_drift_hash(export_coordination_drift_identity(identity))


def hash_manifest_drift_reference(reference: ManifestDriftReference) -> str:
    return deterministic_coordination_drift_hash(export_manifest_drift_reference(reference))


def hash_dependency_graph_drift_reference(reference: DependencyGraphDriftReference) -> str:
    return deterministic_coordination_drift_hash(export_dependency_graph_drift_reference(reference))


def hash_lineage_drift_reference(reference: LineageDriftReference) -> str:
    return deterministic_coordination_drift_hash(export_lineage_drift_reference(reference))


def hash_sequencing_drift_reference(reference: SequencingDriftReference) -> str:
    return deterministic_coordination_drift_hash(export_sequencing_drift_reference(reference))


def hash_routing_drift_reference(reference: RoutingDriftReference) -> str:
    return deterministic_coordination_drift_hash(export_routing_drift_reference(reference))


def hash_coordination_drift_record(record: CoordinationDriftRecord) -> str:
    return deterministic_coordination_drift_hash(export_coordination_drift_record(record))


def hash_drift_state_visibility(visibility: DriftStateVisibility) -> str:
    return deterministic_coordination_drift_hash(export_drift_state_visibility(visibility))


def hash_cross_layer_drift_visibility(visibility: CrossLayerDriftVisibility) -> str:
    return deterministic_coordination_drift_hash(export_cross_layer_drift_visibility(visibility))


def hash_coordination_drift_certification(certification: CoordinationDriftCertification) -> str:
    return deterministic_coordination_drift_hash(export_coordination_drift_certification(certification))
