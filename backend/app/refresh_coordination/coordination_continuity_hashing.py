"""Deterministic hashing for v4.2 coordination continuity certification."""

from __future__ import annotations

import hashlib
from typing import Any

from .coordination_continuity_models import (
    CoordinationContinuityCertification,
    CoordinationContinuityDiagnostic,
    CoordinationContinuityGovernance,
    CoordinationContinuityIdentity,
    ContinuityStateVisibility,
    CrossLayerContinuitySummary,
    CrossLayerCoordinationContinuityRecord,
    DependencyGraphContinuityReference,
    DiagnosticsContinuityReference,
    DriftContinuityReference,
    ExplainabilityContinuityReference,
    LineageContinuityReference,
    ManifestContinuityReference,
    RoutingContinuityReference,
    SequencingContinuityReference,
)
from .coordination_continuity_serialization import (
    export_continuity_state_visibility,
    export_coordination_continuity_certification,
    export_coordination_continuity_diagnostic,
    export_coordination_continuity_governance,
    export_coordination_continuity_identity,
    export_cross_layer_continuity_summary,
    export_cross_layer_coordination_continuity_record,
    export_dependency_graph_continuity_reference,
    export_diagnostics_continuity_reference,
    export_drift_continuity_reference,
    export_explainability_continuity_reference,
    export_lineage_continuity_reference,
    export_manifest_continuity_reference,
    export_routing_continuity_reference,
    export_sequencing_continuity_reference,
    stable_serialize,
)


def deterministic_coordination_continuity_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_continuity_identity(identity: CoordinationContinuityIdentity) -> str:
    return deterministic_coordination_continuity_hash(export_coordination_continuity_identity(identity))


def hash_manifest_continuity_reference(reference: ManifestContinuityReference) -> str:
    return deterministic_coordination_continuity_hash(export_manifest_continuity_reference(reference))


def hash_dependency_graph_continuity_reference(reference: DependencyGraphContinuityReference) -> str:
    return deterministic_coordination_continuity_hash(export_dependency_graph_continuity_reference(reference))


def hash_lineage_continuity_reference(reference: LineageContinuityReference) -> str:
    return deterministic_coordination_continuity_hash(export_lineage_continuity_reference(reference))


def hash_sequencing_continuity_reference(reference: SequencingContinuityReference) -> str:
    return deterministic_coordination_continuity_hash(export_sequencing_continuity_reference(reference))


def hash_routing_continuity_reference(reference: RoutingContinuityReference) -> str:
    return deterministic_coordination_continuity_hash(export_routing_continuity_reference(reference))


def hash_drift_continuity_reference(reference: DriftContinuityReference) -> str:
    return deterministic_coordination_continuity_hash(export_drift_continuity_reference(reference))


def hash_diagnostics_continuity_reference(reference: DiagnosticsContinuityReference) -> str:
    return deterministic_coordination_continuity_hash(export_diagnostics_continuity_reference(reference))


def hash_explainability_continuity_reference(reference: ExplainabilityContinuityReference) -> str:
    return deterministic_coordination_continuity_hash(export_explainability_continuity_reference(reference))


def hash_cross_layer_coordination_continuity_record(
    record: CrossLayerCoordinationContinuityRecord,
) -> str:
    return deterministic_coordination_continuity_hash(export_cross_layer_coordination_continuity_record(record))


def hash_continuity_state_visibility(visibility: ContinuityStateVisibility) -> str:
    return deterministic_coordination_continuity_hash(export_continuity_state_visibility(visibility))


def hash_cross_layer_continuity_summary(summary: CrossLayerContinuitySummary) -> str:
    return deterministic_coordination_continuity_hash(export_cross_layer_continuity_summary(summary))


def hash_coordination_continuity_diagnostic(diagnostic: CoordinationContinuityDiagnostic) -> str:
    return deterministic_coordination_continuity_hash(export_coordination_continuity_diagnostic(diagnostic))


def hash_coordination_continuity_governance(governance: CoordinationContinuityGovernance) -> str:
    return deterministic_coordination_continuity_hash(export_coordination_continuity_governance(governance))


def hash_coordination_continuity_certification(
    certification: CoordinationContinuityCertification,
) -> str:
    return deterministic_coordination_continuity_hash(export_coordination_continuity_certification(certification))
