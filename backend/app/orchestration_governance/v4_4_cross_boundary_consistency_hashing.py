"""Deterministic hashing for v4.4 cross-boundary consistency."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_cross_boundary_consistency_models import (
    CompatibilityConsistencySummary,
    ConsistencyEvidenceMetadata,
    ConsistencyExplainabilityRecord,
    ConsistencyRecord,
    ContinuityConsistencySummary,
    CrossBoundaryConsistencyIdentity,
    CrossBoundaryConsistencyIntelligence,
    CrossBoundaryDiagnosticRecord,
    GovernanceConsistencyClassification,
    LineageConsistencySummary,
    MultiBoundaryRelationshipRecord,
    ProvenanceConsistencySummary,
)
from .v4_4_cross_boundary_consistency_serialization import (
    export_compatibility_consistency,
    export_consistency_evidence_metadata,
    export_consistency_explainability,
    export_consistency_record,
    export_continuity_consistency,
    export_cross_boundary_consistency_identity,
    export_cross_boundary_consistency_intelligence,
    export_cross_boundary_diagnostic,
    export_governance_consistency_classification,
    export_lineage_consistency,
    export_multi_boundary_relationship_record,
    export_provenance_consistency,
    stable_serialize_cross_boundary_consistency,
)


def deterministic_cross_boundary_consistency_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_cross_boundary_consistency(payload).encode("utf-8")
    ).hexdigest()


def hash_cross_boundary_consistency_identity(identity: CrossBoundaryConsistencyIdentity) -> str:
    return deterministic_cross_boundary_consistency_hash(
        export_cross_boundary_consistency_identity(identity)
    )


def hash_governance_consistency_classification(
    classification: GovernanceConsistencyClassification,
) -> str:
    return deterministic_cross_boundary_consistency_hash(
        export_governance_consistency_classification(classification)
    )


def hash_consistency_record(record: ConsistencyRecord) -> str:
    return deterministic_cross_boundary_consistency_hash(export_consistency_record(record))


def hash_multi_boundary_relationship_record(record: MultiBoundaryRelationshipRecord) -> str:
    return deterministic_cross_boundary_consistency_hash(
        export_multi_boundary_relationship_record(record)
    )


def hash_cross_boundary_diagnostic(record: CrossBoundaryDiagnosticRecord) -> str:
    return deterministic_cross_boundary_consistency_hash(export_cross_boundary_diagnostic(record))


def hash_compatibility_consistency(summary: CompatibilityConsistencySummary) -> str:
    return deterministic_cross_boundary_consistency_hash(export_compatibility_consistency(summary))


def hash_continuity_consistency(summary: ContinuityConsistencySummary) -> str:
    return deterministic_cross_boundary_consistency_hash(export_continuity_consistency(summary))


def hash_provenance_consistency(summary: ProvenanceConsistencySummary) -> str:
    return deterministic_cross_boundary_consistency_hash(export_provenance_consistency(summary))


def hash_lineage_consistency(summary: LineageConsistencySummary) -> str:
    return deterministic_cross_boundary_consistency_hash(export_lineage_consistency(summary))


def hash_consistency_explainability(record: ConsistencyExplainabilityRecord) -> str:
    return deterministic_cross_boundary_consistency_hash(export_consistency_explainability(record))


def hash_consistency_evidence_metadata(metadata: ConsistencyEvidenceMetadata) -> str:
    return deterministic_cross_boundary_consistency_hash(export_consistency_evidence_metadata(metadata))


def hash_cross_boundary_consistency_intelligence(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> str:
    return deterministic_cross_boundary_consistency_hash(
        export_cross_boundary_consistency_intelligence(intelligence)
    )
