"""Deterministic hashing for v4.4 boundary segmentation scope."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_boundary_segmentation_scope_models import (
    BoundaryScopeRecord,
    BoundarySegmentRecord,
    BoundarySegmentationScopeIdentity,
    BoundarySegmentationScopeIntelligence,
    ScopeClassification,
    ScopeDiagnosticRecord,
    ScopeLineageVisibility,
    ScopeProvenanceVisibility,
    ScopedBoundaryMembershipRecord,
    SegmentContinuityVisibility,
    SegmentRelationshipRecord,
    SegmentationClassification,
    SegmentationDiagnosticRecord,
    SegmentationExplainabilityRecord,
    SegmentationScopeEvidenceMetadata,
)
from .v4_4_boundary_segmentation_scope_serialization import (
    export_boundary_scope_record,
    export_boundary_segment_record,
    export_boundary_segmentation_scope_identity,
    export_boundary_segmentation_scope_intelligence,
    export_scope_classification,
    export_scope_diagnostic,
    export_scope_lineage_visibility,
    export_scope_provenance_visibility,
    export_scoped_boundary_membership,
    export_segment_continuity_visibility,
    export_segment_relationship,
    export_segmentation_classification,
    export_segmentation_diagnostic,
    export_segmentation_explainability,
    export_segmentation_scope_evidence_metadata,
    stable_serialize_boundary_segmentation_scope,
)


def deterministic_boundary_segmentation_scope_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_boundary_segmentation_scope(payload).encode("utf-8")
    ).hexdigest()


def hash_boundary_segmentation_scope_identity(identity: BoundarySegmentationScopeIdentity) -> str:
    return deterministic_boundary_segmentation_scope_hash(
        export_boundary_segmentation_scope_identity(identity)
    )


def hash_segmentation_classification(classification: SegmentationClassification) -> str:
    return deterministic_boundary_segmentation_scope_hash(
        export_segmentation_classification(classification)
    )


def hash_scope_classification(classification: ScopeClassification) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_scope_classification(classification))


def hash_boundary_segment_record(record: BoundarySegmentRecord) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_boundary_segment_record(record))


def hash_boundary_scope_record(record: BoundaryScopeRecord) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_boundary_scope_record(record))


def hash_scoped_boundary_membership(record: ScopedBoundaryMembershipRecord) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_scoped_boundary_membership(record))


def hash_segment_relationship(record: SegmentRelationshipRecord) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_segment_relationship(record))


def hash_segment_continuity_visibility(record: SegmentContinuityVisibility) -> str:
    return deterministic_boundary_segmentation_scope_hash(
        export_segment_continuity_visibility(record)
    )


def hash_scope_diagnostic(record: ScopeDiagnosticRecord) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_scope_diagnostic(record))


def hash_segmentation_diagnostic(record: SegmentationDiagnosticRecord) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_segmentation_diagnostic(record))


def hash_scope_provenance_visibility(record: ScopeProvenanceVisibility) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_scope_provenance_visibility(record))


def hash_scope_lineage_visibility(record: ScopeLineageVisibility) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_scope_lineage_visibility(record))


def hash_segmentation_explainability(record: SegmentationExplainabilityRecord) -> str:
    return deterministic_boundary_segmentation_scope_hash(export_segmentation_explainability(record))


def hash_segmentation_scope_evidence_metadata(
    metadata: SegmentationScopeEvidenceMetadata,
) -> str:
    return deterministic_boundary_segmentation_scope_hash(
        export_segmentation_scope_evidence_metadata(metadata)
    )


def hash_boundary_segmentation_scope_intelligence(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> str:
    return deterministic_boundary_segmentation_scope_hash(
        export_boundary_segmentation_scope_intelligence(intelligence)
    )
