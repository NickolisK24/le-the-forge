"""Deterministic hashing for v4.4 boundary inheritance refinement."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_boundary_inheritance_refinement_models import (
    BoundaryAncestryVisibility,
    BoundaryInheritanceIdentity,
    BoundaryInheritanceRefinementIntelligence,
    ContinuityPropagationMetadata,
    InheritanceFailVisibleFinding,
    InheritanceRelationshipRecord,
    LineagePropagationMetadata,
    ParentChildRefinementVisibility,
    ProvenancePropagationMetadata,
    RefinementDiagnosticRecord,
    RefinementExplainabilityRecord,
    RefinementLineageContinuity,
    RefinementRelationshipRecord,
)
from .v4_4_boundary_inheritance_refinement_serialization import (
    export_boundary_ancestry_visibility,
    export_boundary_inheritance_identity,
    export_boundary_inheritance_refinement_intelligence,
    export_continuity_propagation_metadata,
    export_inheritance_fail_visible_finding,
    export_inheritance_relationship,
    export_lineage_propagation_metadata,
    export_parent_child_refinement_visibility,
    export_provenance_propagation_metadata,
    export_refinement_diagnostic,
    export_refinement_explainability,
    export_refinement_lineage_continuity,
    export_refinement_relationship,
    stable_serialize_boundary_inheritance,
)


def deterministic_boundary_inheritance_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize_boundary_inheritance(payload).encode("utf-8")).hexdigest()


def hash_boundary_inheritance_identity(identity: BoundaryInheritanceIdentity) -> str:
    return deterministic_boundary_inheritance_hash(export_boundary_inheritance_identity(identity))


def hash_inheritance_relationship(record: InheritanceRelationshipRecord) -> str:
    return deterministic_boundary_inheritance_hash(export_inheritance_relationship(record))


def hash_refinement_relationship(record: RefinementRelationshipRecord) -> str:
    return deterministic_boundary_inheritance_hash(export_refinement_relationship(record))


def hash_boundary_ancestry_visibility(ancestry: BoundaryAncestryVisibility) -> str:
    return deterministic_boundary_inheritance_hash(export_boundary_ancestry_visibility(ancestry))


def hash_parent_child_refinement_visibility(visibility: ParentChildRefinementVisibility) -> str:
    return deterministic_boundary_inheritance_hash(
        export_parent_child_refinement_visibility(visibility)
    )


def hash_refinement_lineage_continuity(continuity: RefinementLineageContinuity) -> str:
    return deterministic_boundary_inheritance_hash(export_refinement_lineage_continuity(continuity))


def hash_refinement_diagnostic(diagnostic: RefinementDiagnosticRecord) -> str:
    return deterministic_boundary_inheritance_hash(export_refinement_diagnostic(diagnostic))


def hash_refinement_explainability(explainability: RefinementExplainabilityRecord) -> str:
    return deterministic_boundary_inheritance_hash(export_refinement_explainability(explainability))


def hash_inheritance_fail_visible_finding(finding: InheritanceFailVisibleFinding) -> str:
    return deterministic_boundary_inheritance_hash(export_inheritance_fail_visible_finding(finding))


def hash_continuity_propagation_metadata(metadata: ContinuityPropagationMetadata) -> str:
    return deterministic_boundary_inheritance_hash(export_continuity_propagation_metadata(metadata))


def hash_provenance_propagation_metadata(metadata: ProvenancePropagationMetadata) -> str:
    return deterministic_boundary_inheritance_hash(export_provenance_propagation_metadata(metadata))


def hash_lineage_propagation_metadata(metadata: LineagePropagationMetadata) -> str:
    return deterministic_boundary_inheritance_hash(export_lineage_propagation_metadata(metadata))


def hash_boundary_inheritance_refinement_intelligence(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> str:
    return deterministic_boundary_inheritance_hash(
        export_boundary_inheritance_refinement_intelligence(intelligence)
    )
