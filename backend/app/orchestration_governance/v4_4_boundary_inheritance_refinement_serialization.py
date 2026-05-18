"""Deterministic serialization for v4.4 boundary inheritance refinement."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

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


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_boundary_inheritance_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_boundary_inheritance_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_boundary_inheritance_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_boundary_inheritance_evidence(value) for value in payload]
    return payload


def stable_serialize_boundary_inheritance(payload: Any) -> str:
    return json.dumps(
        canonicalize_boundary_inheritance_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_boundary_inheritance_identity(identity: BoundaryInheritanceIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_inheritance_relationship(record: InheritanceRelationshipRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_refinement_relationship(record: RefinementRelationshipRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_boundary_ancestry_visibility(ancestry: BoundaryAncestryVisibility) -> dict[str, Any]:
    data = asdict(ancestry)
    data["ancestor_boundary_ids"] = _sorted_tuple(data["ancestor_boundary_ids"])
    return data


def export_parent_child_refinement_visibility(
    visibility: ParentChildRefinementVisibility,
) -> dict[str, Any]:
    return asdict(visibility)


def export_refinement_lineage_continuity(
    continuity: RefinementLineageContinuity,
) -> dict[str, Any]:
    data = asdict(continuity)
    data["lineage_reference_ids"] = _sorted_tuple(data["lineage_reference_ids"])
    return data


def export_refinement_diagnostic(diagnostic: RefinementDiagnosticRecord) -> dict[str, Any]:
    data = asdict(diagnostic)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_refinement_explainability(
    explainability: RefinementExplainabilityRecord,
) -> dict[str, Any]:
    data = asdict(explainability)
    data["explanation_chain_ids"] = _sorted_tuple(data["explanation_chain_ids"])
    return data


def export_inheritance_fail_visible_finding(
    finding: InheritanceFailVisibleFinding,
) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_continuity_propagation_metadata(
    metadata: ContinuityPropagationMetadata,
) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "propagated_relationship_ids",
        "replay_evidence_ids",
        "rollback_evidence_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_provenance_propagation_metadata(
    metadata: ProvenancePropagationMetadata,
) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "source_reference_ids",
        "source_hash_references",
        "propagated_relationship_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_lineage_propagation_metadata(
    metadata: LineagePropagationMetadata,
) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "lineage_reference_ids",
        "lineage_hash_references",
        "propagated_relationship_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_boundary_inheritance_refinement_intelligence(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["identity"] = export_boundary_inheritance_identity(intelligence.identity)
    data["inheritance_relationships"] = [
        export_inheritance_relationship(record)
        for record in sorted(
            intelligence.inheritance_relationships,
            key=lambda item: (item.deterministic_order, item.inheritance_id),
        )
    ]
    data["refinement_relationships"] = [
        export_refinement_relationship(record)
        for record in sorted(
            intelligence.refinement_relationships,
            key=lambda item: (item.deterministic_order, item.refinement_id),
        )
    ]
    data["ancestry_visibility"] = [
        export_boundary_ancestry_visibility(ancestry)
        for ancestry in sorted(
            intelligence.ancestry_visibility,
            key=lambda item: (item.deterministic_order, item.ancestry_id),
        )
    ]
    data["parent_child_refinement_visibility"] = [
        export_parent_child_refinement_visibility(visibility)
        for visibility in sorted(
            intelligence.parent_child_refinement_visibility,
            key=lambda item: (item.deterministic_order, item.parent_child_id),
        )
    ]
    data["refinement_lineage_continuity"] = [
        export_refinement_lineage_continuity(continuity)
        for continuity in sorted(
            intelligence.refinement_lineage_continuity,
            key=lambda item: (item.deterministic_order, item.lineage_id),
        )
    ]
    data["diagnostics"] = [
        export_refinement_diagnostic(diagnostic)
        for diagnostic in sorted(
            intelligence.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["explainability"] = [
        export_refinement_explainability(explainability)
        for explainability in sorted(
            intelligence.explainability,
            key=lambda item: (item.deterministic_order, item.explainability_id),
        )
    ]
    data["fail_visible_findings"] = [
        export_inheritance_fail_visible_finding(finding)
        for finding in sorted(
            intelligence.fail_visible_findings,
            key=lambda item: (item.deterministic_order, item.finding_id),
        )
    ]
    data["continuity_propagation_metadata"] = export_continuity_propagation_metadata(
        intelligence.continuity_propagation_metadata
    )
    data["provenance_propagation_metadata"] = export_provenance_propagation_metadata(
        intelligence.provenance_propagation_metadata
    )
    data["lineage_propagation_metadata"] = export_lineage_propagation_metadata(
        intelligence.lineage_propagation_metadata
    )
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_boundary_inheritance_identity(identity: BoundaryInheritanceIdentity) -> str:
    return stable_serialize_boundary_inheritance(export_boundary_inheritance_identity(identity))


def serialize_boundary_inheritance_refinement_intelligence(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> str:
    return stable_serialize_boundary_inheritance(
        export_boundary_inheritance_refinement_intelligence(intelligence)
    )
