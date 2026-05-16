"""Deterministic orchestration policy resolution registry for v3.6 Phase 3."""

from __future__ import annotations

from typing import Iterable

from .orchestration_policy_compatibility_models import (
    COMPATIBILITY_DEPENDENCY_BLOCKED,
    COMPATIBILITY_GOVERNANCE_BLOCKED,
    COMPATIBILITY_INCOMPATIBLE,
    COMPATIBILITY_PROHIBITED,
    COMPATIBILITY_UNSUPPORTED,
    OrchestrationPolicyCompatibilityRelationship,
)
from .orchestration_policy_compatibility_registry import (
    default_orchestration_policy_compatibility_registry,
    get_registered_compatibility_relationship,
)
from .orchestration_policy_resolution_models import (
    RESOLUTION_DEPENDENCY_CONFLICT,
    RESOLUTION_EVIDENCE_INCOMPLETE,
    RESOLUTION_FUTURE_CANDIDATE,
    RESOLUTION_GOVERNANCE_CONFLICT,
    RESOLUTION_INTENTIONAL_BLOCK,
    RESOLUTION_UNSUPPORTED_BY_DESIGN,
    OrchestrationPolicyResolutionEvidenceGap,
    OrchestrationPolicyResolutionIdentifier,
    OrchestrationPolicyResolutionProvenance,
    OrchestrationPolicyResolutionRecord,
    OrchestrationPolicyResolutionRegistry,
    export_resolution_registry,
    hash_resolution_registry,
    serialize_resolution_registry,
)


DEFAULT_RESOLUTION_REGISTRY_ID = "v3_6_orchestration_policy_resolution_registry"
DEFAULT_RESOLUTION_SCHEMA_VERSION = "v3_6.orchestration_policy_resolution_registry.1"

_BLOCKED_RELATIONSHIP_IDS: tuple[str, ...] = (
    "v3_6.compat.autonomy-execution.unsupported",
    "v3_6.compat.autonomy-routing.unsupported",
    "v3_6.compat.execution-production-runtime.prohibited",
    "v3_6.compat.execution-routing.prohibited",
    "v3_6.compat.explainability-routing.incompatible",
    "v3_6.compat.governance-production-runtime.governance-blocked",
    "v3_6.compat.integrity-execution.dependency-blocked",
    "v3_6.compat.routing-production-runtime.prohibited",
)


def default_orchestration_policy_resolution_registry() -> OrchestrationPolicyResolutionRegistry:
    return build_orchestration_policy_resolution_registry(default_orchestration_policy_resolution_records())


def build_orchestration_policy_resolution_registry(
    records: Iterable[OrchestrationPolicyResolutionRecord],
    registry_id: str = DEFAULT_RESOLUTION_REGISTRY_ID,
) -> OrchestrationPolicyResolutionRegistry:
    ordered = tuple(sorted(records, key=lambda item: item.identifier.resolution_id))
    resolution_ids = [record.identifier.resolution_id for record in ordered]
    if len(resolution_ids) != len(set(resolution_ids)):
        duplicates = sorted({resolution_id for resolution_id in resolution_ids if resolution_ids.count(resolution_id) > 1})
        raise ValueError(f"Duplicate resolution ids are not allowed: {', '.join(duplicates)}")
    relationship_ids = [record.identifier.relationship_id for record in ordered]
    if len(relationship_ids) != len(set(relationship_ids)):
        duplicates = sorted({relationship_id for relationship_id in relationship_ids if relationship_ids.count(relationship_id) > 1})
        raise ValueError(f"Duplicate resolution relationship ids are not allowed: {', '.join(duplicates)}")
    return OrchestrationPolicyResolutionRegistry(
        registry_id=registry_id,
        schema_version=DEFAULT_RESOLUTION_SCHEMA_VERSION,
        records=ordered,
        registry_metadata={
            "phase": "v3.6.phase_3",
            "purpose": "deterministic_orchestration_policy_resolution_audit",
            "planning_only": True,
            "non_production": True,
            "resolution_audit_only": True,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "automatic_resolution_enabled": False,
            "autonomous_behavior_enabled": False,
            "production_runtime_behavior_enabled": False,
        },
    )


def default_orchestration_policy_resolution_records() -> tuple[OrchestrationPolicyResolutionRecord, ...]:
    compatibility_registry = default_orchestration_policy_compatibility_registry()
    relationships = tuple(
        relationship
        for relationship_id in _BLOCKED_RELATIONSHIP_IDS
        if (relationship := get_registered_compatibility_relationship(compatibility_registry, relationship_id)) is not None
    )
    return tuple(_resolution_record(relationship) for relationship in relationships)


def registered_resolution_ids(registry: OrchestrationPolicyResolutionRegistry) -> tuple[str, ...]:
    return tuple(sorted(record.identifier.resolution_id for record in registry.records))


def get_registered_resolution_record(
    registry: OrchestrationPolicyResolutionRegistry,
    resolution_id: str,
) -> OrchestrationPolicyResolutionRecord | None:
    for record in registry.records:
        if record.identifier.resolution_id == resolution_id:
            return record
    return None


def get_registered_resolution_record_for_relationship(
    registry: OrchestrationPolicyResolutionRegistry,
    relationship_id: str,
) -> OrchestrationPolicyResolutionRecord | None:
    for record in registry.records:
        if record.identifier.relationship_id == relationship_id:
            return record
    return None


def export_default_orchestration_policy_resolution_registry() -> dict[str, object]:
    return export_resolution_registry(default_orchestration_policy_resolution_registry())


def serialize_default_orchestration_policy_resolution_registry() -> str:
    return serialize_resolution_registry(default_orchestration_policy_resolution_registry())


def hash_default_orchestration_policy_resolution_registry() -> str:
    return hash_resolution_registry(default_orchestration_policy_resolution_registry())


def _resolution_record(relationship: OrchestrationPolicyCompatibilityRelationship) -> OrchestrationPolicyResolutionRecord:
    relationship_id = relationship.identifier.relationship_id
    resolution_id = relationship_id.replace("v3_6.compat.", "v3_6.resolution.")
    classifications = _classifications(relationship)
    evidence_gaps = _evidence_gaps(relationship)
    governance_constraints = _governance_constraints(relationship)
    dependency_gaps = _dependency_gaps(relationship)
    continuity_gaps = ()
    blocker_chain_ids = tuple(sorted(chain.blocker_chain_id for chain in relationship.blocker_chains))
    return OrchestrationPolicyResolutionRecord(
        identifier=OrchestrationPolicyResolutionIdentifier(
            resolution_id=resolution_id,
            relationship_id=relationship_id,
            namespace="v3_6.orchestration_policy_resolution",
            version="1",
        ),
        compatibility_state=relationship.compatibility_state,
        resolution_classifications=classifications,
        block_intentional=RESOLUTION_INTENTIONAL_BLOCK in classifications or RESOLUTION_UNSUPPORTED_BY_DESIGN in classifications,
        future_support_possible=RESOLUTION_FUTURE_CANDIDATE in classifications,
        evidence_gaps=evidence_gaps,
        governance_constraints=governance_constraints,
        dependency_gaps=dependency_gaps,
        continuity_gaps=continuity_gaps,
        blocker_chain_ids=blocker_chain_ids,
        compatibility_evidence_ids=(
            relationship.compatibility_state,
            relationship.compatibility_classification,
            *relationship.policy_ids,
        ),
        provenance=OrchestrationPolicyResolutionProvenance(
            source_phase="v3.6_phase_3_deterministic_orchestration_policy_resolution_audit",
            source_artifact="backend/app/runtime_orchestration/orchestration_policy_resolution_registry.py",
            compatibility_relationship_id=relationship_id,
            replay_reference_ids=(f"{resolution_id}.replay",),
            rollback_reference_ids=(f"{resolution_id}.rollback",),
            governance_reference_ids=("v3_6_policy_compatibility_integrity_stable", "v3_6_resolution_governance_first"),
        ),
        governance_metadata={
            "planning_only": True,
            "non_production": True,
            "deterministic_only": True,
            "governance_first": True,
            "resolution_audit_only": True,
            "execution_enabled": False,
            "routing_enabled": False,
            "mutation_enabled": False,
            "autonomy_enabled": False,
            "automatic_resolution_enabled": False,
            "production_runtime_reads_enabled": False,
            "production_runtime_writes_enabled": False,
            "persistent_writes_enabled": False,
        },
        support_rationale=_support_rationale(relationship, classifications),
        resolution_explainability_ids=(f"{resolution_id}.explainability",),
        resolution_integrity_ids=(f"{resolution_id}.integrity",),
    )


def _classifications(relationship: OrchestrationPolicyCompatibilityRelationship) -> tuple[str, ...]:
    if relationship.compatibility_state == COMPATIBILITY_PROHIBITED:
        return (RESOLUTION_INTENTIONAL_BLOCK,)
    if relationship.compatibility_state == COMPATIBILITY_UNSUPPORTED:
        return (RESOLUTION_UNSUPPORTED_BY_DESIGN,)
    if relationship.compatibility_state == COMPATIBILITY_INCOMPATIBLE:
        return (RESOLUTION_FUTURE_CANDIDATE, RESOLUTION_EVIDENCE_INCOMPLETE)
    if relationship.compatibility_state == COMPATIBILITY_DEPENDENCY_BLOCKED:
        return (RESOLUTION_DEPENDENCY_CONFLICT,)
    if relationship.compatibility_state == COMPATIBILITY_GOVERNANCE_BLOCKED:
        return (RESOLUTION_GOVERNANCE_CONFLICT,)
    return (RESOLUTION_EVIDENCE_INCOMPLETE,)


def _evidence_gaps(relationship: OrchestrationPolicyCompatibilityRelationship) -> tuple[OrchestrationPolicyResolutionEvidenceGap, ...]:
    if relationship.compatibility_state != COMPATIBILITY_INCOMPATIBLE:
        return ()
    resolution_id = relationship.identifier.relationship_id.replace("v3_6.compat.", "v3_6.resolution.")
    return (
        OrchestrationPolicyResolutionEvidenceGap(
            evidence_gap_id=f"{resolution_id}.evidence-gap",
            missing_evidence_ids=(
                "non_routing_explainability_proof",
                "future_support_governance_boundary_proof",
            ),
            required_before_status_change=(
                "prove explainability remains non-routing",
                "prove status change preserves planning-only governance",
            ),
        ),
    )


def _governance_constraints(relationship: OrchestrationPolicyCompatibilityRelationship) -> tuple[str, ...]:
    constraints = set(relationship.governance_conflicts)
    if relationship.compatibility_state == COMPATIBILITY_PROHIBITED:
        constraints.add("prohibited_pairing_cannot_be_reclassified_without_governance_revision")
    if relationship.compatibility_state == COMPATIBILITY_UNSUPPORTED:
        constraints.add("unsupported_combination_requires_new_design_evidence_before_review")
    if relationship.compatibility_state == COMPATIBILITY_INCOMPATIBLE:
        constraints.add("future_candidate_requires_non_execution_governance_evidence")
    return tuple(sorted(constraints))


def _dependency_gaps(relationship: OrchestrationPolicyCompatibilityRelationship) -> tuple[str, ...]:
    return tuple(sorted(conflict.conflict_id for conflict in relationship.dependency_conflicts))


def _support_rationale(
    relationship: OrchestrationPolicyCompatibilityRelationship,
    classifications: tuple[str, ...],
) -> tuple[str, ...]:
    if RESOLUTION_INTENTIONAL_BLOCK in classifications:
        return tuple(sorted(relationship.blocker_reasons or ("relationship is intentionally blocked by prohibited compatibility state",)))
    if RESOLUTION_UNSUPPORTED_BY_DESIGN in classifications:
        return tuple(sorted(relationship.blocker_reasons or ("relationship is unsupported by design and remains blocked",)))
    if RESOLUTION_FUTURE_CANDIDATE in classifications:
        return (
            "relationship may be revisited only if missing non-routing and planning-only governance evidence is supplied",
        )
    if RESOLUTION_DEPENDENCY_CONFLICT in classifications:
        return tuple(sorted(conflict.conflict_reason for conflict in relationship.dependency_conflicts))
    if RESOLUTION_GOVERNANCE_CONFLICT in classifications:
        return tuple(sorted(relationship.blocker_reasons or relationship.governance_conflicts))
    return ("relationship requires explicit deterministic evidence before compatibility status can change",)
