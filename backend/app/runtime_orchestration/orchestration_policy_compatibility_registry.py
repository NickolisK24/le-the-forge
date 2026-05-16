"""Deterministic orchestration policy compatibility registry for v3.6 Phase 2."""

from __future__ import annotations

from typing import Iterable

from .orchestration_policy_compatibility_models import (
    COMPATIBILITY_BLOCKED_BY_DEPENDENCY_CONFLICT,
    COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT,
    COMPATIBILITY_BLOCKED_BY_INCOMPATIBILITY,
    COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING,
    COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION,
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_DEPENDENCY_BLOCKED,
    COMPATIBILITY_GOVERNANCE_BLOCKED,
    COMPATIBILITY_INCOMPATIBLE,
    COMPATIBILITY_PROHIBITED,
    COMPATIBILITY_UNSUPPORTED,
    OrchestrationPolicyCompatibilityBlockerChain,
    OrchestrationPolicyCompatibilityIdentifier,
    OrchestrationPolicyCompatibilityProvenance,
    OrchestrationPolicyCompatibilityRegistry,
    OrchestrationPolicyCompatibilityRelationship,
    OrchestrationPolicyDependencyConflict,
    export_compatibility_registry,
    hash_compatibility_registry,
    serialize_compatibility_registry,
)


DEFAULT_COMPATIBILITY_REGISTRY_ID = "v3_6_orchestration_policy_compatibility_registry"
DEFAULT_COMPATIBILITY_SCHEMA_VERSION = "v3_6.orchestration_policy_compatibility_registry.1"


def default_orchestration_policy_compatibility_registry() -> OrchestrationPolicyCompatibilityRegistry:
    return build_orchestration_policy_compatibility_registry(default_orchestration_policy_compatibility_relationships())


def build_orchestration_policy_compatibility_registry(
    relationships: Iterable[OrchestrationPolicyCompatibilityRelationship],
    registry_id: str = DEFAULT_COMPATIBILITY_REGISTRY_ID,
) -> OrchestrationPolicyCompatibilityRegistry:
    ordered = tuple(sorted(relationships, key=lambda item: item.identifier.relationship_id))
    relationship_ids = [relationship.identifier.relationship_id for relationship in ordered]
    if len(relationship_ids) != len(set(relationship_ids)):
        duplicates = sorted({relationship_id for relationship_id in relationship_ids if relationship_ids.count(relationship_id) > 1})
        raise ValueError(f"Duplicate compatibility relationship ids are not allowed: {', '.join(duplicates)}")
    return OrchestrationPolicyCompatibilityRegistry(
        registry_id=registry_id,
        schema_version=DEFAULT_COMPATIBILITY_SCHEMA_VERSION,
        relationships=ordered,
        registry_metadata={
            "phase": "v3.6.phase_2",
            "purpose": "deterministic_orchestration_policy_compatibility_intelligence",
            "planning_only": True,
            "non_production": True,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "autonomous_behavior_enabled": False,
            "production_runtime_behavior_enabled": False,
        },
    )


def default_orchestration_policy_compatibility_relationships() -> tuple[OrchestrationPolicyCompatibilityRelationship, ...]:
    return (
        _relationship(
            "v3_6.compat.modeling-governance.compatible",
            ("v3_6.policy.modeling.allowed", "v3_6.policy.governance-boundary.allowed"),
            COMPATIBILITY_COMPATIBLE,
            "compatible_policy_foundation",
            support_rationale=("policy modeling and governance boundary may coexist as planning-only policy intelligence",),
        ),
        _relationship(
            "v3_6.compat.modeling-explainability.compatible",
            ("v3_6.policy.modeling.allowed", "v3_6.policy.explainability.allowed"),
            COMPATIBILITY_COMPATIBLE,
            "compatible_policy_explainability",
            support_rationale=("policy modeling and explainability may coexist because both generate deterministic evidence only",),
        ),
        _relationship(
            "v3_6.compat.governance-explainability.compatible",
            ("v3_6.policy.governance-boundary.allowed", "v3_6.policy.explainability.allowed"),
            COMPATIBILITY_COMPATIBLE,
            "compatible_governance_explainability",
            support_rationale=("governance boundary and explainability may coexist when non-execution guarantees are preserved",),
        ),
        _relationship(
            "v3_6.compat.explainability-integrity.compatible",
            ("v3_6.policy.explainability.allowed", "v3_6.policy.integrity.allowed"),
            COMPATIBILITY_COMPATIBLE,
            "compatible_explainability_integrity",
            support_rationale=("explainability evidence may feed integrity auditing without enabling runtime behavior",),
        ),
        _relationship(
            "v3_6.compat.governance-integrity.compatible",
            ("v3_6.policy.governance-boundary.allowed", "v3_6.policy.integrity.allowed"),
            COMPATIBILITY_COMPATIBLE,
            "compatible_governance_integrity",
            support_rationale=("governance boundary and integrity auditing may coexist as deterministic planning evidence",),
        ),
        _relationship(
            "v3_6.compat.execution-routing.prohibited",
            ("v3_6.policy.execution.prohibited", "v3_6.policy.routing.prohibited"),
            COMPATIBILITY_PROHIBITED,
            "prohibited_execution_routing_pairing",
            blocker_reasons=("execution-capable policy and routing-capable policy may not coexist as allowed behavior",),
            blocker_state=COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING,
        ),
        _relationship(
            "v3_6.compat.execution-production-runtime.prohibited",
            ("v3_6.policy.execution.prohibited", "v3_6.policy.production-runtime.prohibited"),
            COMPATIBILITY_PROHIBITED,
            "prohibited_execution_production_runtime_pairing",
            blocker_reasons=("execution-capable policy may not pair with production runtime access",),
            blocker_state=COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING,
        ),
        _relationship(
            "v3_6.compat.routing-production-runtime.prohibited",
            ("v3_6.policy.routing.prohibited", "v3_6.policy.production-runtime.prohibited"),
            COMPATIBILITY_PROHIBITED,
            "prohibited_routing_production_runtime_pairing",
            blocker_reasons=("routing-capable policy may not pair with production runtime access",),
            blocker_state=COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING,
        ),
        _relationship(
            "v3_6.compat.autonomy-execution.unsupported",
            ("v3_6.policy.autonomy.unsupported", "v3_6.policy.execution.prohibited"),
            COMPATIBILITY_UNSUPPORTED,
            "unsupported_autonomy_execution_combination",
            blocker_reasons=("autonomous orchestration with execution capability is unsupported and remains blocked",),
            blocker_state=COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION,
        ),
        _relationship(
            "v3_6.compat.autonomy-routing.unsupported",
            ("v3_6.policy.autonomy.unsupported", "v3_6.policy.routing.prohibited"),
            COMPATIBILITY_UNSUPPORTED,
            "unsupported_autonomy_routing_combination",
            blocker_reasons=("autonomous orchestration with routing capability is unsupported and remains blocked",),
            blocker_state=COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION,
        ),
        _relationship(
            "v3_6.compat.explainability-routing.incompatible",
            ("v3_6.policy.explainability.allowed", "v3_6.policy.routing.prohibited"),
            COMPATIBILITY_INCOMPATIBLE,
            "incompatible_explainability_routing",
            blocker_reasons=("explainability evidence must not become routing behavior",),
            blocker_state=COMPATIBILITY_BLOCKED_BY_INCOMPATIBILITY,
        ),
        _relationship(
            "v3_6.compat.integrity-execution.dependency-blocked",
            ("v3_6.policy.integrity.allowed", "v3_6.policy.execution.prohibited"),
            COMPATIBILITY_DEPENDENCY_BLOCKED,
            "dependency_blocked_integrity_execution",
            dependency_conflicts=(
                OrchestrationPolicyDependencyConflict(
                    conflict_id="integrity-requires-non-executing-policy-surface",
                    policy_ids=("v3_6.policy.integrity.allowed", "v3_6.policy.execution.prohibited"),
                    dependency_chain=("v3_6.policy.integrity.allowed", "non_executing_policy_surface"),
                    conflict_reason="integrity policy can audit execution prohibition only as blocked evidence, not as executable compatibility",
                ),
            ),
            blocker_reasons=("integrity policy cannot treat execution prohibition as executable dependency compatibility",),
            blocker_state=COMPATIBILITY_BLOCKED_BY_DEPENDENCY_CONFLICT,
        ),
        _relationship(
            "v3_6.compat.governance-production-runtime.governance-blocked",
            ("v3_6.policy.governance-boundary.allowed", "v3_6.policy.production-runtime.prohibited"),
            COMPATIBILITY_GOVERNANCE_BLOCKED,
            "governance_blocked_production_runtime_access",
            governance_conflicts=("production_runtime_access_conflicts_with_non_production_governance",),
            blocker_reasons=("governance boundary prohibits production runtime policy coexistence as allowed behavior",),
            blocker_state=COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT,
        ),
    )


def registered_compatibility_relationship_ids(registry: OrchestrationPolicyCompatibilityRegistry) -> tuple[str, ...]:
    return tuple(sorted(relationship.identifier.relationship_id for relationship in registry.relationships))


def get_registered_compatibility_relationship(
    registry: OrchestrationPolicyCompatibilityRegistry,
    relationship_id: str,
) -> OrchestrationPolicyCompatibilityRelationship | None:
    for relationship in registry.relationships:
        if relationship.identifier.relationship_id == relationship_id:
            return relationship
    return None


def export_default_orchestration_policy_compatibility_registry() -> dict[str, object]:
    return export_compatibility_registry(default_orchestration_policy_compatibility_registry())


def serialize_default_orchestration_policy_compatibility_registry() -> str:
    return serialize_compatibility_registry(default_orchestration_policy_compatibility_registry())


def hash_default_orchestration_policy_compatibility_registry() -> str:
    return hash_compatibility_registry(default_orchestration_policy_compatibility_registry())


def _relationship(
    relationship_id: str,
    policy_ids: tuple[str, ...],
    compatibility_state: str,
    compatibility_classification: str,
    dependency_conflicts: tuple[OrchestrationPolicyDependencyConflict, ...] = (),
    governance_conflicts: tuple[str, ...] = (),
    support_rationale: tuple[str, ...] = (),
    blocker_reasons: tuple[str, ...] = (),
    blocker_state: str | None = None,
) -> OrchestrationPolicyCompatibilityRelationship:
    blocker_chains = ()
    if blocker_state is not None:
        blocker_chains = (
            OrchestrationPolicyCompatibilityBlockerChain(
                blocker_chain_id=f"{relationship_id}.blocker-chain",
                blocker_states=(blocker_state,),
                policy_ids=policy_ids,
                evidence_ids=(compatibility_state, compatibility_classification),
            ),
        )
    return OrchestrationPolicyCompatibilityRelationship(
        identifier=OrchestrationPolicyCompatibilityIdentifier(
            relationship_id=relationship_id,
            namespace="v3_6.orchestration_policy_compatibility",
            version="1",
        ),
        policy_ids=policy_ids,
        compatibility_state=compatibility_state,
        compatibility_classification=compatibility_classification,
        dependency_conflicts=dependency_conflicts,
        governance_conflicts=governance_conflicts,
        blocker_chains=blocker_chains,
        provenance=OrchestrationPolicyCompatibilityProvenance(
            source_phase="v3.6_phase_2_deterministic_orchestration_policy_compatibility_matrix",
            source_artifact="backend/app/runtime_orchestration/orchestration_policy_compatibility_registry.py",
            upstream_policy_ids=policy_ids,
            replay_reference_ids=(f"{relationship_id}.replay",),
            rollback_reference_ids=(f"{relationship_id}.rollback",),
            governance_reference_ids=("v3_6_policy_foundation_integrity_stable", "v3_6_compatibility_governance_first"),
        ),
        governance_metadata={
            "planning_only": True,
            "non_production": True,
            "deterministic_only": True,
            "governance_first": True,
            "execution_enabled": False,
            "routing_enabled": False,
            "mutation_enabled": False,
            "autonomy_enabled": False,
            "production_runtime_reads_enabled": False,
            "production_runtime_writes_enabled": False,
            "persistent_writes_enabled": False,
        },
        support_rationale=support_rationale,
        blocker_reasons=blocker_reasons,
        integrity_reference_ids=(f"{relationship_id}.integrity",),
        explainability_reference_ids=(f"{relationship_id}.explainability",),
    )
