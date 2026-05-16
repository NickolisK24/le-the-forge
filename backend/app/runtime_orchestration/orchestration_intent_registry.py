"""Deterministic orchestration intent registry for v3.6 Phase 4."""

from __future__ import annotations

from typing import Iterable

from .orchestration_intent_models import (
    INTENT_COMPATIBILITY_CHECK,
    INTENT_CONTINUITY_ANALYSIS,
    INTENT_DEPENDENCY_ANALYSIS,
    INTENT_GOVERNANCE_REVIEW,
    INTENT_INFORMATIONAL,
    INTENT_ORCHESTRATION_SIMULATION,
    INTENT_POLICY_BOUNDARY,
    INTENT_PROHIBITED,
    INTENT_PROHIBITED_DOMAIN,
    INTENT_SUPPORTED,
    INTENT_UNSUPPORTED,
    INTENT_UNSUPPORTED_DOMAIN,
    OrchestrationIntentIdentifier,
    OrchestrationIntentProvenance,
    OrchestrationIntentRecord,
    OrchestrationIntentRegistry,
    export_intent_registry,
    hash_intent_registry,
    serialize_intent_registry,
)


DEFAULT_INTENT_REGISTRY_ID = "v3_6_orchestration_intent_registry"
DEFAULT_INTENT_SCHEMA_VERSION = "v3_6.orchestration_intent_registry.1"


def default_orchestration_intent_registry() -> OrchestrationIntentRegistry:
    return build_orchestration_intent_registry(default_orchestration_intent_records())


def build_orchestration_intent_registry(
    records: Iterable[OrchestrationIntentRecord],
    registry_id: str = DEFAULT_INTENT_REGISTRY_ID,
) -> OrchestrationIntentRegistry:
    ordered = tuple(sorted(records, key=lambda item: item.identifier.intent_id))
    intent_ids = [record.identifier.intent_id for record in ordered]
    if len(intent_ids) != len(set(intent_ids)):
        duplicates = sorted({intent_id for intent_id in intent_ids if intent_ids.count(intent_id) > 1})
        raise ValueError(f"Duplicate orchestration intent ids are not allowed: {', '.join(duplicates)}")
    return OrchestrationIntentRegistry(
        registry_id=registry_id,
        schema_version=DEFAULT_INTENT_SCHEMA_VERSION,
        records=ordered,
        registry_metadata={
            "phase": "v3.6.phase_4",
            "purpose": "deterministic_orchestration_intent_modeling",
            "planning_only": True,
            "non_production": True,
            "intent_modeling_only": True,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "recommendation_behavior_enabled": False,
            "optimization_behavior_enabled": False,
            "autonomous_behavior_enabled": False,
            "production_runtime_behavior_enabled": False,
        },
    )


def default_orchestration_intent_records() -> tuple[OrchestrationIntentRecord, ...]:
    return (
        _intent_record(
            intent_id="v3_6.intent.informational",
            intent_type=INTENT_INFORMATIONAL,
            support_state=INTENT_SUPPORTED,
            intent_goal="inspect deterministic policy state without requesting compatibility or execution behavior",
            policy_domains=("policy_modeling", "policy_explainability"),
            supported_domains=("informational_visibility", "policy_state_inspection"),
            compatibility_relationship_ids=("v3_6.compat.modeling-explainability.compatible",),
            resolution_record_ids=(),
        ),
        _intent_record(
            intent_id="v3_6.intent.compatibility-check",
            intent_type=INTENT_COMPATIBILITY_CHECK,
            support_state=INTENT_SUPPORTED,
            intent_goal="pre-analyze which policy compatibility domains a future request would touch",
            policy_domains=("policy_modeling", "policy_compatibility"),
            compatibility_domains=("compatibility_matrix", "multi_policy_compatibility", "pairwise_compatibility"),
            blocker_domains=("compatibility_blocker_visibility",),
            supported_domains=("compatibility_pre_analysis",),
            governance_boundaries=("compatibility_pre_analysis_only",),
            compatibility_relationship_ids=("v3_6.compat.modeling-governance.compatible",),
            resolution_record_ids=(),
        ),
        _intent_record(
            intent_id="v3_6.intent.governance-review",
            intent_type=INTENT_GOVERNANCE_REVIEW,
            support_state=INTENT_SUPPORTED,
            intent_goal="identify governance boundaries and governance conflict visibility for a future request",
            policy_domains=("governance_boundary", "policy_provenance"),
            compatibility_domains=("governance_blocked_compatibility",),
            blocker_domains=("governance_conflict_visibility",),
            supported_domains=("governance_review",),
            governance_boundaries=("governance_first",),
            compatibility_relationship_ids=("v3_6.compat.governance-production-runtime.governance-blocked",),
            resolution_record_ids=("v3_6.resolution.governance-production-runtime.governance-blocked",),
        ),
        _intent_record(
            intent_id="v3_6.intent.dependency-analysis",
            intent_type=INTENT_DEPENDENCY_ANALYSIS,
            support_state=INTENT_SUPPORTED,
            intent_goal="identify dependency domains and dependency blockers before compatibility analysis",
            policy_domains=("policy_dependency",),
            compatibility_domains=("dependency_blocked_compatibility",),
            dependency_domains=("dependency_chain", "dependency_conflict"),
            blocker_domains=("dependency_blocker_visibility",),
            supported_domains=("dependency_analysis",),
            governance_boundaries=("dependency_visibility",),
            compatibility_relationship_ids=("v3_6.compat.integrity-execution.dependency-blocked",),
            resolution_record_ids=("v3_6.resolution.integrity-execution.dependency-blocked",),
        ),
        _intent_record(
            intent_id="v3_6.intent.continuity-analysis",
            intent_type=INTENT_CONTINUITY_ANALYSIS,
            support_state=INTENT_SUPPORTED,
            intent_goal="identify provenance, hash, replay, and rollback continuity domains before compatibility analysis",
            policy_domains=("policy_continuity", "policy_provenance"),
            compatibility_domains=("compatibility_continuity",),
            dependency_domains=("hash_continuity", "registry_continuity"),
            blocker_domains=("continuity_gap_visibility",),
            supported_domains=("continuity_analysis",),
            governance_boundaries=("continuity_visibility",),
            compatibility_relationship_ids=("v3_6.compat.explainability-integrity.compatible",),
            resolution_record_ids=(),
        ),
        _intent_record(
            intent_id="v3_6.intent.policy-boundary",
            intent_type=INTENT_POLICY_BOUNDARY,
            support_state=INTENT_SUPPORTED,
            intent_goal="identify allowed, unsupported, and prohibited policy boundaries without changing policy state",
            policy_domains=("allowed_policy_boundary", "prohibited_policy_boundary", "unsupported_policy_boundary"),
            compatibility_domains=("policy_boundary_compatibility",),
            blocker_domains=("policy_boundary_blocker_visibility",),
            unsupported_domains=("unsupported_policy_state",),
            prohibited_domains=("prohibited_policy_state",),
            supported_domains=("policy_boundary_review",),
            governance_boundaries=("policy_boundary_visibility",),
            compatibility_relationship_ids=("v3_6.compat.execution-routing.prohibited",),
            resolution_record_ids=("v3_6.resolution.execution-routing.prohibited",),
        ),
        _intent_record(
            intent_id="v3_6.intent.orchestration-simulation",
            intent_type=INTENT_ORCHESTRATION_SIMULATION,
            support_state=INTENT_SUPPORTED,
            intent_goal="model planning-only simulation intent as evidence without executing or routing behavior",
            policy_domains=("simulation_boundary",),
            compatibility_domains=("planning_simulation_compatibility",),
            dependency_domains=("simulation_evidence_dependency",),
            blocker_domains=("simulation_execution_blocker_visibility",),
            unsupported_domains=("runtime_simulation",),
            prohibited_domains=("execution_simulation",),
            supported_domains=("planning_only_simulation",),
            governance_boundaries=("simulation_planning_only",),
            compatibility_relationship_ids=("v3_6.compat.explainability-routing.incompatible",),
            resolution_record_ids=("v3_6.resolution.explainability-routing.incompatible",),
        ),
        _intent_record(
            intent_id="v3_6.intent.unsupported-domain",
            intent_type=INTENT_UNSUPPORTED_DOMAIN,
            support_state=INTENT_UNSUPPORTED,
            intent_goal="surface unsupported orchestration domains before compatibility or governance review",
            policy_domains=("unsupported_orchestration_domain",),
            compatibility_domains=("unsupported_combination",),
            blocker_domains=("autonomy_blocker", "unsupported_domain_blocker"),
            unsupported_domains=("autonomous_orchestration", "unsupported_domain_expansion"),
            supported_domains=(),
            governance_boundaries=("unsupported_fail_visible",),
            compatibility_relationship_ids=("v3_6.compat.autonomy-routing.unsupported",),
            resolution_record_ids=("v3_6.resolution.autonomy-routing.unsupported",),
        ),
        _intent_record(
            intent_id="v3_6.intent.prohibited-domain",
            intent_type=INTENT_PROHIBITED_DOMAIN,
            support_state=INTENT_PROHIBITED,
            intent_goal="surface prohibited orchestration domains before compatibility or governance review",
            policy_domains=("prohibited_orchestration_domain",),
            compatibility_domains=("prohibited_pairing",),
            blocker_domains=("prohibited_execution_blocker", "production_runtime_blocker", "routing_blocker"),
            prohibited_domains=("orchestration_execution", "orchestration_routing", "production_runtime_reads"),
            supported_domains=(),
            governance_boundaries=("prohibited_fail_visible",),
            compatibility_relationship_ids=("v3_6.compat.execution-production-runtime.prohibited", "v3_6.compat.routing-production-runtime.prohibited"),
            resolution_record_ids=("v3_6.resolution.execution-production-runtime.prohibited", "v3_6.resolution.routing-production-runtime.prohibited"),
        ),
    )


def registered_intent_ids(registry: OrchestrationIntentRegistry) -> tuple[str, ...]:
    return tuple(sorted(record.identifier.intent_id for record in registry.records))


def get_registered_intent_record(
    registry: OrchestrationIntentRegistry,
    intent_id: str,
) -> OrchestrationIntentRecord | None:
    for record in registry.records:
        if record.identifier.intent_id == intent_id:
            return record
    return None


def export_default_orchestration_intent_registry() -> dict[str, object]:
    return export_intent_registry(default_orchestration_intent_registry())


def serialize_default_orchestration_intent_registry() -> str:
    return serialize_intent_registry(default_orchestration_intent_registry())


def hash_default_orchestration_intent_registry() -> str:
    return hash_intent_registry(default_orchestration_intent_registry())


def _intent_record(
    intent_id: str,
    intent_type: str,
    support_state: str,
    intent_goal: str,
    policy_domains: tuple[str, ...],
    compatibility_domains: tuple[str, ...] = (),
    dependency_domains: tuple[str, ...] = (),
    governance_boundaries: tuple[str, ...] = (),
    blocker_domains: tuple[str, ...] = (),
    unsupported_domains: tuple[str, ...] = (),
    prohibited_domains: tuple[str, ...] = (),
    supported_domains: tuple[str, ...] = (),
    compatibility_relationship_ids: tuple[str, ...] = (),
    resolution_record_ids: tuple[str, ...] = (),
) -> OrchestrationIntentRecord:
    default_governance = ("non_executing", "non_production", "planning_only")
    merged_governance = tuple(sorted({*default_governance, *governance_boundaries}))
    return OrchestrationIntentRecord(
        identifier=OrchestrationIntentIdentifier(
            intent_id=intent_id,
            namespace="v3_6.orchestration_intent",
            version="1",
        ),
        intent_type=intent_type,
        support_state=support_state,
        intent_goal=intent_goal,
        policy_domains=policy_domains,
        compatibility_domains=compatibility_domains,
        dependency_domains=dependency_domains,
        governance_boundaries=merged_governance,
        blocker_domains=blocker_domains,
        unsupported_domains=unsupported_domains,
        prohibited_domains=prohibited_domains,
        supported_domains=supported_domains,
        provenance=OrchestrationIntentProvenance(
            source_phase="v3.6_phase_4_deterministic_orchestration_intent_modeling",
            source_artifact="backend/app/runtime_orchestration/orchestration_intent_registry.py",
            upstream_policy_ids=policy_domains,
            compatibility_relationship_ids=compatibility_relationship_ids,
            resolution_record_ids=resolution_record_ids,
            replay_reference_ids=(f"{intent_id}.replay",),
            rollback_reference_ids=(f"{intent_id}.rollback",),
            governance_reference_ids=("v3_6_policy_resolution_integrity_stable", "v3_6_intent_governance_first"),
        ),
        governance_metadata={
            "planning_only": True,
            "non_production": True,
            "deterministic_only": True,
            "governance_first": True,
            "intent_modeling_only": True,
            "execution_enabled": False,
            "routing_enabled": False,
            "mutation_enabled": False,
            "recommendation_enabled": False,
            "optimization_enabled": False,
            "autonomy_enabled": False,
            "production_runtime_reads_enabled": False,
            "production_runtime_writes_enabled": False,
            "persistent_writes_enabled": False,
        },
        classifier_evidence_ids=(intent_type, support_state, *policy_domains, *compatibility_domains),
        explainability_reference_ids=(f"{intent_id}.explainability",),
        integrity_reference_ids=(f"{intent_id}.integrity",),
    )
