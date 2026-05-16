"""Deterministic orchestration policy registry for v3.6."""

from __future__ import annotations

from typing import Iterable

from .orchestration_policy_models import (
    POLICY_CLASSIFICATION_AUTONOMOUS_ORCHESTRATION,
    POLICY_CLASSIFICATION_GOVERNANCE_BOUNDARY,
    POLICY_CLASSIFICATION_ORCHESTRATION_EXECUTION,
    POLICY_CLASSIFICATION_ORCHESTRATION_ROUTING,
    POLICY_CLASSIFICATION_POLICY_EXPLAINABILITY,
    POLICY_CLASSIFICATION_POLICY_INTEGRITY,
    POLICY_CLASSIFICATION_POLICY_MODELING,
    POLICY_CLASSIFICATION_PRODUCTION_RUNTIME_ACCESS,
    POLICY_PROHIBITED,
    POLICY_SUPPORTED,
    POLICY_UNSUPPORTED,
    OrchestrationPolicyDefinition,
    OrchestrationPolicyDependency,
    OrchestrationPolicyIdentifier,
    OrchestrationPolicyProvenance,
    OrchestrationPolicyRegistry,
    export_policy_registry,
    hash_policy_registry,
    serialize_policy_registry,
)


DEFAULT_POLICY_REGISTRY_ID = "v3_6_orchestration_policy_intelligence_registry"
DEFAULT_POLICY_SCHEMA_VERSION = "v3_6.orchestration_policy_registry.1"


def default_orchestration_policy_registry() -> OrchestrationPolicyRegistry:
    return build_orchestration_policy_registry(default_orchestration_policies())


def build_orchestration_policy_registry(
    policies: Iterable[OrchestrationPolicyDefinition],
    registry_id: str = DEFAULT_POLICY_REGISTRY_ID,
) -> OrchestrationPolicyRegistry:
    ordered = tuple(sorted(policies, key=lambda item: item.identifier.policy_id))
    policy_ids = [policy.identifier.policy_id for policy in ordered]
    if len(policy_ids) != len(set(policy_ids)):
        duplicates = sorted({policy_id for policy_id in policy_ids if policy_ids.count(policy_id) > 1})
        raise ValueError(f"Duplicate orchestration policy ids are not allowed: {', '.join(duplicates)}")
    return OrchestrationPolicyRegistry(
        registry_id=registry_id,
        schema_version=DEFAULT_POLICY_SCHEMA_VERSION,
        policies=ordered,
        registry_metadata={
            "phase": "v3.6",
            "purpose": "deterministic_orchestration_policy_intelligence",
            "planning_only": True,
            "non_production": True,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "autonomous_behavior_enabled": False,
            "production_runtime_behavior_enabled": False,
        },
    )


def default_orchestration_policies() -> tuple[OrchestrationPolicyDefinition, ...]:
    modeling = _policy(
        policy_id="v3_6.policy.modeling.allowed",
        display_name="Deterministic orchestration policy modeling",
        classification=POLICY_CLASSIFICATION_POLICY_MODELING,
        support_state=POLICY_SUPPORTED,
        allowed_state_ids=("planning_only_policy_modeling", "deterministic_policy_serialization"),
        support_rationale=(
            "policy modeling is declarative",
            "policy modeling does not execute orchestration",
            "policy modeling keeps allowed, prohibited, and unsupported states visible",
        ),
        integrity_reference_ids=("v3_6_policy_modeling_integrity",),
        explainability_reference_ids=("v3_6_policy_modeling_explainability",),
    )
    governance = _policy(
        policy_id="v3_6.policy.governance-boundary.allowed",
        display_name="Governance boundary continuity",
        classification=POLICY_CLASSIFICATION_GOVERNANCE_BOUNDARY,
        support_state=POLICY_SUPPORTED,
        allowed_state_ids=("governance_boundary_modeling", "non_executing_policy_visibility"),
        support_rationale=(
            "governance boundary policy is planning-only",
            "governance boundary policy preserves non-production scope",
        ),
        dependencies=(
            _dependency(
                "v3_6.policy.governance-boundary.depends-on-modeling",
                "v3_6.policy.modeling.allowed",
            ),
        ),
        integrity_reference_ids=("v3_6_governance_boundary_integrity",),
        explainability_reference_ids=("v3_6_governance_boundary_explainability",),
    )
    explainability = _policy(
        policy_id="v3_6.policy.explainability.allowed",
        display_name="Policy explainability visibility",
        classification=POLICY_CLASSIFICATION_POLICY_EXPLAINABILITY,
        support_state=POLICY_SUPPORTED,
        allowed_state_ids=("policy_explainability_generation", "blocker_visibility"),
        support_rationale=(
            "explainability is deterministic evidence generation",
            "explainability does not recommend or route behavior",
        ),
        dependencies=(
            _dependency(
                "v3_6.policy.explainability.depends-on-modeling",
                "v3_6.policy.modeling.allowed",
            ),
            _dependency(
                "v3_6.policy.explainability.depends-on-governance-boundary",
                "v3_6.policy.governance-boundary.allowed",
            ),
        ),
        integrity_reference_ids=("v3_6_policy_explainability_integrity",),
        explainability_reference_ids=("v3_6_policy_explainability_explainability",),
    )
    integrity = _policy(
        policy_id="v3_6.policy.integrity.allowed",
        display_name="Policy integrity auditing",
        classification=POLICY_CLASSIFICATION_POLICY_INTEGRITY,
        support_state=POLICY_SUPPORTED,
        allowed_state_ids=("policy_integrity_auditing", "policy_hash_continuity"),
        support_rationale=(
            "integrity auditing validates deterministic policy evidence",
            "integrity auditing does not persist audit state",
        ),
        dependencies=(
            _dependency(
                "v3_6.policy.integrity.depends-on-modeling",
                "v3_6.policy.modeling.allowed",
            ),
            _dependency(
                "v3_6.policy.integrity.depends-on-explainability",
                "v3_6.policy.explainability.allowed",
            ),
        ),
        integrity_reference_ids=("v3_6_policy_integrity_integrity",),
        explainability_reference_ids=("v3_6_policy_integrity_explainability",),
    )
    execution = _policy(
        policy_id="v3_6.policy.execution.prohibited",
        display_name="Orchestration execution",
        classification=POLICY_CLASSIFICATION_ORCHESTRATION_EXECUTION,
        support_state=POLICY_PROHIBITED,
        prohibited_state_ids=("orchestration_execution", "graph_execution", "runtime_dispatch"),
        blocker_reasons=(
            "orchestration execution is prohibited in v3.6",
            "graph execution and runtime dispatch are outside policy intelligence scope",
        ),
        dependencies=(_dependency("v3_6.policy.execution.depends-on-modeling", "v3_6.policy.modeling.allowed"),),
        integrity_reference_ids=("v3_6_execution_prohibition_integrity",),
        explainability_reference_ids=("v3_6_execution_prohibition_explainability",),
    )
    routing = _policy(
        policy_id="v3_6.policy.routing.prohibited",
        display_name="Orchestration routing",
        classification=POLICY_CLASSIFICATION_ORCHESTRATION_ROUTING,
        support_state=POLICY_PROHIBITED,
        prohibited_state_ids=("orchestration_routing", "runtime_decision_routing"),
        blocker_reasons=(
            "routing behavior is prohibited in v3.6",
            "policy intelligence may model routing prohibition only",
        ),
        dependencies=(_dependency("v3_6.policy.routing.depends-on-modeling", "v3_6.policy.modeling.allowed"),),
        integrity_reference_ids=("v3_6_routing_prohibition_integrity",),
        explainability_reference_ids=("v3_6_routing_prohibition_explainability",),
    )
    autonomy = _policy(
        policy_id="v3_6.policy.autonomy.unsupported",
        display_name="Autonomous orchestration",
        classification=POLICY_CLASSIFICATION_AUTONOMOUS_ORCHESTRATION,
        support_state=POLICY_UNSUPPORTED,
        unsupported_state_ids=("autonomous_orchestration", "self_advancing_policy"),
        blocker_reasons=(
            "autonomous orchestration is unsupported",
            "self-advancing behavior is outside deterministic policy intelligence scope",
        ),
        dependencies=(_dependency("v3_6.policy.autonomy.depends-on-modeling", "v3_6.policy.modeling.allowed"),),
        integrity_reference_ids=("v3_6_autonomy_unsupported_integrity",),
        explainability_reference_ids=("v3_6_autonomy_unsupported_explainability",),
    )
    production_runtime = _policy(
        policy_id="v3_6.policy.production-runtime.prohibited",
        display_name="Production runtime access",
        classification=POLICY_CLASSIFICATION_PRODUCTION_RUNTIME_ACCESS,
        support_state=POLICY_PROHIBITED,
        prohibited_state_ids=("production_runtime_reads", "production_runtime_writes", "production_runtime_consumption"),
        blocker_reasons=(
            "production runtime access is prohibited",
            "v3.6 policy intelligence does not read or write production runtime state",
        ),
        dependencies=(_dependency("v3_6.policy.production-runtime.depends-on-modeling", "v3_6.policy.modeling.allowed"),),
        integrity_reference_ids=("v3_6_production_runtime_prohibition_integrity",),
        explainability_reference_ids=("v3_6_production_runtime_prohibition_explainability",),
    )
    return (modeling, governance, explainability, integrity, execution, routing, autonomy, production_runtime)


def registered_policy_ids(registry: OrchestrationPolicyRegistry) -> tuple[str, ...]:
    return tuple(sorted(policy.identifier.policy_id for policy in registry.policies))


def get_registered_policy(registry: OrchestrationPolicyRegistry, policy_id: str) -> OrchestrationPolicyDefinition | None:
    for policy in registry.policies:
        if policy.identifier.policy_id == policy_id:
            return policy
    return None


def export_default_orchestration_policy_registry() -> dict[str, object]:
    return export_policy_registry(default_orchestration_policy_registry())


def serialize_default_orchestration_policy_registry() -> str:
    return serialize_policy_registry(default_orchestration_policy_registry())


def hash_default_orchestration_policy_registry() -> str:
    return hash_policy_registry(default_orchestration_policy_registry())


def _policy(
    policy_id: str,
    display_name: str,
    classification: str,
    support_state: str,
    allowed_state_ids: tuple[str, ...] = (),
    prohibited_state_ids: tuple[str, ...] = (),
    unsupported_state_ids: tuple[str, ...] = (),
    dependencies: tuple[OrchestrationPolicyDependency, ...] = (),
    support_rationale: tuple[str, ...] = (),
    blocker_reasons: tuple[str, ...] = (),
    integrity_reference_ids: tuple[str, ...] = (),
    explainability_reference_ids: tuple[str, ...] = (),
) -> OrchestrationPolicyDefinition:
    return OrchestrationPolicyDefinition(
        identifier=OrchestrationPolicyIdentifier(
            policy_id=policy_id,
            namespace="v3_6.orchestration_policy_intelligence",
            version="1",
        ),
        display_name=display_name,
        classification=classification,
        support_state=support_state,
        allowed_state_ids=allowed_state_ids,
        prohibited_state_ids=prohibited_state_ids,
        unsupported_state_ids=unsupported_state_ids,
        dependencies=dependencies,
        provenance=OrchestrationPolicyProvenance(
            source_phase="v3.6_phase_1_deterministic_orchestration_policy_intelligence_foundation",
            source_artifact="backend/app/runtime_orchestration/orchestration_policy_registry.py",
            upstream_policy_ids=tuple(dependency.required_policy_id for dependency in dependencies),
            replay_reference_ids=(f"{policy_id}.replay",),
            rollback_reference_ids=(f"{policy_id}.rollback",),
            governance_reference_ids=("v3_5_closeout_ready_for_v3_6_planning", "v3_6_governance_first_policy_intelligence"),
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
        integrity_reference_ids=integrity_reference_ids,
        explainability_reference_ids=explainability_reference_ids,
    )


def _dependency(dependency_id: str, required_policy_id: str) -> OrchestrationPolicyDependency:
    return OrchestrationPolicyDependency(
        dependency_id=dependency_id,
        required_policy_id=required_policy_id,
        required_support_states=(POLICY_SUPPORTED,),
        continuity_reference_id=f"{dependency_id}.continuity",
    )
