"""Visibility helpers for v4.4 boundary inheritance refinement."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_boundary_inheritance_refinement_models import (
    BOUNDARY_INHERITANCE_STATES,
    FAIL_VISIBLE_INHERITANCE_STATES,
    INHERITANCE_STATE_AMBIGUOUS,
    INHERITANCE_STATE_CONFLICTING,
    INHERITANCE_STATE_PROHIBITED,
    INHERITANCE_STATE_STALE,
    INHERITANCE_STATE_UNSUPPORTED,
    BoundaryAncestryVisibility,
    BoundaryInheritanceRefinementIntelligence,
    InheritanceFailVisibleFinding,
    InheritanceRelationshipRecord,
    RefinementDiagnosticRecord,
    RefinementExplainabilityRecord,
    RefinementRelationshipRecord,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_inheritance_relationship_states(
    relationships: Iterable[InheritanceRelationshipRecord],
) -> dict[str, int]:
    counts = Counter(relationship.visibility_state for relationship in relationships)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_INHERITANCE_STATES}


def count_refinement_relationship_states(
    relationships: Iterable[RefinementRelationshipRecord],
) -> dict[str, int]:
    counts = Counter(relationship.visibility_state for relationship in relationships)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_INHERITANCE_STATES}


def count_combined_relationship_states(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, int]:
    counts = Counter()
    counts.update(
        relationship.visibility_state for relationship in intelligence.inheritance_relationships
    )
    counts.update(
        relationship.visibility_state for relationship in intelligence.refinement_relationships
    )
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_INHERITANCE_STATES}


def inheritance_chain_summaries(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "inheritance_id": relationship.inheritance_id,
            "parent_boundary_id": relationship.parent_boundary_id,
            "child_boundary_id": relationship.child_boundary_id,
            "relationship_type": relationship.relationship_type,
            "visibility_state": relationship.visibility_state,
            "ancestry_depth": relationship.ancestry_depth,
            "fail_visible": relationship.fail_visible,
            "descriptive_only": relationship.descriptive_only,
            "non_authoritative": relationship.non_authoritative,
            "operational_authority": relationship.operational_authority,
        }
        for relationship in sorted(
            intelligence.inheritance_relationships,
            key=lambda item: (item.deterministic_order, item.inheritance_id),
        )
    ]


def refinement_ancestry_summaries(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "refinement_id": relationship.refinement_id,
            "source_boundary_id": relationship.source_boundary_id,
            "refined_boundary_id": relationship.refined_boundary_id,
            "relationship_type": relationship.relationship_type,
            "visibility_state": relationship.visibility_state,
            "refinement_depth": relationship.refinement_depth,
            "fail_visible": relationship.fail_visible,
            "descriptive_only": relationship.descriptive_only,
            "non_authoritative": relationship.non_authoritative,
            "execution_capability": relationship.execution_capability,
        }
        for relationship in sorted(
            intelligence.refinement_relationships,
            key=lambda item: (item.deterministic_order, item.refinement_id),
        )
    ]


def ancestry_depth_visibility(
    ancestry: Iterable[BoundaryAncestryVisibility],
) -> dict[str, Any]:
    ancestry_tuple = tuple(ancestry)
    max_depth = max((item.ancestry_depth for item in ancestry_tuple), default=0)
    return {
        "ancestry_visibility_count": len(ancestry_tuple),
        "max_ancestry_depth": max_depth,
        "ancestry_ids": _ordered_ids(item.ancestry_id for item in ancestry_tuple),
        "multi_level_ancestry_count": sum(1 for item in ancestry_tuple if item.ancestry_depth > 1),
        "descriptive_only": all(item.descriptive_only for item in ancestry_tuple),
        "non_authoritative": all(item.non_authoritative for item in ancestry_tuple),
        "operational_authority_count": sum(
            1 for item in ancestry_tuple if item.operational_authority
        ),
    }


def governance_safe_refinement_explainability(
    explainability: Iterable[RefinementExplainabilityRecord],
) -> dict[str, Any]:
    explainability_tuple = tuple(explainability)
    by_state = Counter(record.visibility_state for record in explainability_tuple)
    return {
        "explainability_count": len(explainability_tuple),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_INHERITANCE_STATES
        },
        "explainability_ids": _ordered_ids(
            record.explainability_id for record in explainability_tuple
        ),
        "explainability_first": all(record.explainability_first for record in explainability_tuple),
        "descriptive_only": all(record.descriptive_only for record in explainability_tuple),
        "recommendation_enabled_count": sum(
            1 for record in explainability_tuple if record.recommendation_enabled
        ),
        "decision_enabled_count": sum(1 for record in explainability_tuple if record.decision_enabled),
    }


def aggregate_refinement_diagnostics(
    diagnostics: Iterable[RefinementDiagnosticRecord],
) -> dict[str, Any]:
    diagnostics_tuple = tuple(diagnostics)
    by_state = Counter(record.visibility_state for record in diagnostics_tuple)
    by_severity = Counter(record.severity for record in diagnostics_tuple)
    return {
        "diagnostic_count": len(diagnostics_tuple),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_INHERITANCE_STATES
        },
        "severity_counts": {
            severity: int(by_severity[severity]) for severity in sorted(by_severity)
        },
        "diagnostic_ids": _ordered_ids(record.diagnostic_id for record in diagnostics_tuple),
        "fail_visible": all(record.fail_visible for record in diagnostics_tuple),
        "descriptive_only": all(record.descriptive_only for record in diagnostics_tuple),
        "automatic_repair_enabled_count": sum(
            1 for record in diagnostics_tuple if record.automatic_repair_enabled
        ),
        "automatic_remediation_enabled_count": sum(
            1 for record in diagnostics_tuple if record.automatic_remediation_enabled
        ),
    }


def _findings_for_state(
    findings: Iterable[InheritanceFailVisibleFinding],
    state: str,
) -> list[dict[str, Any]]:
    return [
        {
            "finding_id": finding.finding_id,
            "relationship_id": finding.relationship_id,
            "finding_type": finding.finding_type,
            "visibility_state": finding.visibility_state,
            "finding_message": finding.finding_message,
            "evidence_reference_ids": _ordered_ids(finding.evidence_reference_ids),
            "fail_visible": finding.fail_visible,
            "hidden_inference_used": finding.hidden_inference_used,
            "automatic_repair_enabled": finding.automatic_repair_enabled,
            "automatic_remediation_enabled": finding.automatic_remediation_enabled,
        }
        for finding in sorted(
            (item for item in findings if item.visibility_state == state),
            key=lambda item: (item.deterministic_order, item.finding_id),
        )
    ]


def inheritance_conflict_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> list[dict[str, Any]]:
    return _findings_for_state(intelligence.fail_visible_findings, INHERITANCE_STATE_CONFLICTING)


def refinement_drift_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> list[dict[str, Any]]:
    return _findings_for_state(intelligence.fail_visible_findings, INHERITANCE_STATE_STALE)


def prohibited_inheritance_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> list[dict[str, Any]]:
    return _findings_for_state(intelligence.fail_visible_findings, INHERITANCE_STATE_PROHIBITED)


def unsupported_inheritance_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> list[dict[str, Any]]:
    return _findings_for_state(intelligence.fail_visible_findings, INHERITANCE_STATE_UNSUPPORTED)


def fail_visible_ambiguity_summaries(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> list[dict[str, Any]]:
    return _findings_for_state(intelligence.fail_visible_findings, INHERITANCE_STATE_AMBIGUOUS)


def fail_visible_inheritance_summary(
    findings: Iterable[InheritanceFailVisibleFinding],
) -> dict[str, Any]:
    findings_tuple = tuple(findings)
    by_state = Counter(finding.visibility_state for finding in findings_tuple)
    return {
        "finding_count": len(findings_tuple),
        "state_counts": {
            state: int(by_state.get(state, 0)) for state in BOUNDARY_INHERITANCE_STATES
        },
        "finding_ids": _ordered_ids(finding.finding_id for finding in findings_tuple),
        "fail_visible": all(finding.fail_visible for finding in findings_tuple),
        "descriptive_only": all(finding.descriptive_only for finding in findings_tuple),
        "hidden_inference_used_count": sum(
            1 for finding in findings_tuple if finding.hidden_inference_used
        ),
        "automatic_repair_enabled_count": sum(
            1 for finding in findings_tuple if finding.automatic_repair_enabled
        ),
        "automatic_remediation_enabled_count": sum(
            1 for finding in findings_tuple if finding.automatic_remediation_enabled
        ),
    }


def continuity_propagation_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    continuity = intelligence.continuity_propagation_metadata
    return {
        "continuity_id": continuity.continuity_id,
        "propagated_relationship_count": len(continuity.propagated_relationship_ids),
        "replay_evidence_count": len(continuity.replay_evidence_ids),
        "rollback_evidence_count": len(continuity.rollback_evidence_ids),
        "continuity_propagation_preserved": continuity.continuity_propagation_preserved,
        "replay_safe": continuity.replay_safe,
        "rollback_safe": continuity.rollback_safe,
        "runtime_mutation_enabled": continuity.runtime_mutation_enabled,
        "operational_mutation_enabled": continuity.operational_mutation_enabled,
    }


def provenance_propagation_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_propagation_metadata
    return {
        "provenance_id": provenance.provenance_id,
        "source_reference_ids": _ordered_ids(provenance.source_reference_ids),
        "source_hash_references": _ordered_ids(provenance.source_hash_references),
        "propagated_relationship_count": len(provenance.propagated_relationship_ids),
        "provenance_continuity_preserved": provenance.provenance_continuity_preserved,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "production_consumption_enabled": provenance.production_consumption_enabled,
    }


def lineage_propagation_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    lineage = intelligence.lineage_propagation_metadata
    return {
        "lineage_id": lineage.lineage_id,
        "lineage_reference_ids": _ordered_ids(lineage.lineage_reference_ids),
        "lineage_hash_references": _ordered_ids(lineage.lineage_hash_references),
        "propagated_relationship_count": len(lineage.propagated_relationship_ids),
        "lineage_continuity_preserved": lineage.lineage_continuity_preserved,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
        "operational_mutation_enabled": lineage.operational_mutation_enabled,
    }


def validate_required_state_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    counts = count_combined_relationship_states(intelligence)
    missing_states = [state for state in BOUNDARY_INHERITANCE_STATES if counts[state] <= 0]
    fail_visible = fail_visible_inheritance_summary(intelligence.fail_visible_findings)
    missing_fail_visible_states = [
        state for state in FAIL_VISIBLE_INHERITANCE_STATES if fail_visible["state_counts"][state] <= 0
    ]
    return {
        "valid": not missing_states and not missing_fail_visible_states,
        "relationship_state_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": missing_fail_visible_states,
        "fail_visible_summary": fail_visible,
    }
