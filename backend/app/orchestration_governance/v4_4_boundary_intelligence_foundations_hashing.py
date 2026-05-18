"""Deterministic hashing for v4.4 boundary intelligence foundations."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_boundary_intelligence_foundations_models import (
    BoundaryContinuityMetadata,
    BoundaryDiagnosticRecord,
    BoundaryExplainabilityRecord,
    BoundaryFailVisibleFinding,
    BoundaryGovernanceVisibilitySummary,
    BoundaryIntegrityVisibility,
    BoundaryIntelligenceClassification,
    BoundaryIntelligenceFoundations,
    BoundaryIntelligenceIdentity,
    BoundaryIntelligenceRecord,
    BoundaryLineageMetadata,
    BoundaryProvenanceMetadata,
)
from .v4_4_boundary_intelligence_foundations_serialization import (
    export_boundary_continuity_metadata,
    export_boundary_diagnostic_record,
    export_boundary_explainability_record,
    export_boundary_fail_visible_finding,
    export_boundary_governance_visibility_summary,
    export_boundary_integrity_visibility,
    export_boundary_intelligence_classification,
    export_boundary_intelligence_foundations,
    export_boundary_intelligence_identity,
    export_boundary_intelligence_record,
    export_boundary_lineage_metadata,
    export_boundary_provenance_metadata,
    stable_serialize_boundary_intelligence,
)


def deterministic_boundary_intelligence_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_boundary_intelligence(payload).encode("utf-8")
    ).hexdigest()


def hash_boundary_intelligence_identity(identity: BoundaryIntelligenceIdentity) -> str:
    return deterministic_boundary_intelligence_hash(export_boundary_intelligence_identity(identity))


def hash_boundary_intelligence_classification(
    classification: BoundaryIntelligenceClassification,
) -> str:
    return deterministic_boundary_intelligence_hash(
        export_boundary_intelligence_classification(classification)
    )


def hash_boundary_intelligence_record(record: BoundaryIntelligenceRecord) -> str:
    return deterministic_boundary_intelligence_hash(export_boundary_intelligence_record(record))


def hash_boundary_diagnostic_record(diagnostic: BoundaryDiagnosticRecord) -> str:
    return deterministic_boundary_intelligence_hash(export_boundary_diagnostic_record(diagnostic))


def hash_boundary_explainability_record(explainability: BoundaryExplainabilityRecord) -> str:
    return deterministic_boundary_intelligence_hash(
        export_boundary_explainability_record(explainability)
    )


def hash_boundary_integrity_visibility(integrity: BoundaryIntegrityVisibility) -> str:
    return deterministic_boundary_intelligence_hash(export_boundary_integrity_visibility(integrity))


def hash_boundary_governance_visibility_summary(
    summary: BoundaryGovernanceVisibilitySummary,
) -> str:
    return deterministic_boundary_intelligence_hash(
        export_boundary_governance_visibility_summary(summary)
    )


def hash_boundary_fail_visible_finding(finding: BoundaryFailVisibleFinding) -> str:
    return deterministic_boundary_intelligence_hash(export_boundary_fail_visible_finding(finding))


def hash_boundary_continuity_metadata(metadata: BoundaryContinuityMetadata) -> str:
    return deterministic_boundary_intelligence_hash(export_boundary_continuity_metadata(metadata))


def hash_boundary_provenance_metadata(metadata: BoundaryProvenanceMetadata) -> str:
    return deterministic_boundary_intelligence_hash(export_boundary_provenance_metadata(metadata))


def hash_boundary_lineage_metadata(metadata: BoundaryLineageMetadata) -> str:
    return deterministic_boundary_intelligence_hash(export_boundary_lineage_metadata(metadata))


def hash_boundary_intelligence_foundations(
    foundations: BoundaryIntelligenceFoundations,
) -> str:
    return deterministic_boundary_intelligence_hash(
        export_boundary_intelligence_foundations(foundations)
    )
