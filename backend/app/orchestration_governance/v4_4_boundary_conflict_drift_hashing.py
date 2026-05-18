"""Deterministic hashing for v4.4 boundary conflict drift."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_boundary_conflict_drift_models import (
    BoundaryConflictDriftIdentity,
    BoundaryConflictDriftIntelligence,
    BoundaryDriftRecord,
    CompatibilityEvidenceRecord,
    ConflictAncestryVisibility,
    ConflictDiagnosticRecord,
    ConflictExplainabilityRecord,
    ConflictLineageVisibility,
    ContinuityDegradationSummary,
    DriftEvidenceMetadata,
    GovernanceDriftClassification,
    LineageDegradationMetadata,
    ProvenanceDegradationMetadata,
    RefinementDivergenceRecord,
)
from .v4_4_boundary_conflict_drift_serialization import (
    export_boundary_conflict_drift_identity,
    export_boundary_conflict_drift_intelligence,
    export_boundary_drift_record,
    export_compatibility_evidence,
    export_conflict_ancestry_visibility,
    export_conflict_diagnostic,
    export_conflict_explainability,
    export_conflict_lineage_visibility,
    export_degradation_summary,
    export_drift_evidence_metadata,
    export_governance_drift_classification,
    export_lineage_degradation_metadata,
    export_provenance_degradation_metadata,
    export_refinement_divergence_record,
    stable_serialize_boundary_conflict_drift,
)


def deterministic_boundary_conflict_drift_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_boundary_conflict_drift(payload).encode("utf-8")
    ).hexdigest()


def hash_boundary_conflict_drift_identity(identity: BoundaryConflictDriftIdentity) -> str:
    return deterministic_boundary_conflict_drift_hash(
        export_boundary_conflict_drift_identity(identity)
    )


def hash_governance_drift_classification(classification: GovernanceDriftClassification) -> str:
    return deterministic_boundary_conflict_drift_hash(
        export_governance_drift_classification(classification)
    )


def hash_boundary_drift_record(record: BoundaryDriftRecord) -> str:
    return deterministic_boundary_conflict_drift_hash(export_boundary_drift_record(record))


def hash_refinement_divergence_record(record: RefinementDivergenceRecord) -> str:
    return deterministic_boundary_conflict_drift_hash(export_refinement_divergence_record(record))


def hash_conflict_diagnostic(record: ConflictDiagnosticRecord) -> str:
    return deterministic_boundary_conflict_drift_hash(export_conflict_diagnostic(record))


def hash_compatibility_evidence(record: CompatibilityEvidenceRecord) -> str:
    return deterministic_boundary_conflict_drift_hash(export_compatibility_evidence(record))


def hash_degradation_summary(summary: ContinuityDegradationSummary) -> str:
    return deterministic_boundary_conflict_drift_hash(export_degradation_summary(summary))


def hash_conflict_explainability(record: ConflictExplainabilityRecord) -> str:
    return deterministic_boundary_conflict_drift_hash(export_conflict_explainability(record))


def hash_conflict_lineage_visibility(record: ConflictLineageVisibility) -> str:
    return deterministic_boundary_conflict_drift_hash(export_conflict_lineage_visibility(record))


def hash_conflict_ancestry_visibility(record: ConflictAncestryVisibility) -> str:
    return deterministic_boundary_conflict_drift_hash(export_conflict_ancestry_visibility(record))


def hash_provenance_degradation_metadata(metadata: ProvenanceDegradationMetadata) -> str:
    return deterministic_boundary_conflict_drift_hash(export_provenance_degradation_metadata(metadata))


def hash_lineage_degradation_metadata(metadata: LineageDegradationMetadata) -> str:
    return deterministic_boundary_conflict_drift_hash(export_lineage_degradation_metadata(metadata))


def hash_drift_evidence_metadata(metadata: DriftEvidenceMetadata) -> str:
    return deterministic_boundary_conflict_drift_hash(export_drift_evidence_metadata(metadata))


def hash_boundary_conflict_drift_intelligence(
    intelligence: BoundaryConflictDriftIntelligence,
) -> str:
    return deterministic_boundary_conflict_drift_hash(
        export_boundary_conflict_drift_intelligence(intelligence)
    )
