"""Deterministic orchestration intent-policy mapping registry for v3.6 Phase 5."""

from __future__ import annotations

from typing import Iterable

from .orchestration_intent_models import INTENT_PROHIBITED, INTENT_SUPPORTED, INTENT_UNSUPPORTED, OrchestrationIntentRecord
from .orchestration_intent_registry import default_orchestration_intent_registry
from .orchestration_intent_policy_mapping_models import (
    MAPPING_INTENT_TO_BLOCKER,
    MAPPING_INTENT_TO_COMPATIBILITY,
    MAPPING_INTENT_TO_DEPENDENCY,
    MAPPING_INTENT_TO_GOVERNANCE,
    MAPPING_INTENT_TO_POLICY,
    MAPPING_INTENT_TO_PROHIBITED_DOMAIN,
    MAPPING_INTENT_TO_SUPPORTED_DOMAIN,
    MAPPING_INTENT_TO_UNSUPPORTED_DOMAIN,
    MAPPING_PROHIBITED,
    MAPPING_SUPPORTED,
    MAPPING_UNSUPPORTED,
    OrchestrationIntentPolicyMappingIdentifier,
    OrchestrationIntentPolicyMappingProvenance,
    OrchestrationIntentPolicyMappingRecord,
    OrchestrationIntentPolicyMappingRegistry,
    export_mapping_registry,
    hash_mapping_registry,
    serialize_mapping_registry,
)


DEFAULT_MAPPING_REGISTRY_ID = "v3_6_orchestration_intent_policy_mapping_registry"
DEFAULT_MAPPING_SCHEMA_VERSION = "v3_6.orchestration_intent_policy_mapping_registry.1"

POLICY_MODELING_ALLOWED = "v3_6.policy.modeling.allowed"
POLICY_GOVERNANCE_BOUNDARY_ALLOWED = "v3_6.policy.governance-boundary.allowed"
POLICY_EXPLAINABILITY_ALLOWED = "v3_6.policy.explainability.allowed"
POLICY_INTEGRITY_ALLOWED = "v3_6.policy.integrity.allowed"
POLICY_EXECUTION_PROHIBITED = "v3_6.policy.execution.prohibited"
POLICY_ROUTING_PROHIBITED = "v3_6.policy.routing.prohibited"
POLICY_AUTONOMY_UNSUPPORTED = "v3_6.policy.autonomy.unsupported"
POLICY_PRODUCTION_RUNTIME_PROHIBITED = "v3_6.policy.production-runtime.prohibited"


def default_orchestration_intent_policy_mapping_registry() -> OrchestrationIntentPolicyMappingRegistry:
    return build_orchestration_intent_policy_mapping_registry(default_orchestration_intent_policy_mapping_records())


def build_orchestration_intent_policy_mapping_registry(
    records: Iterable[OrchestrationIntentPolicyMappingRecord],
    registry_id: str = DEFAULT_MAPPING_REGISTRY_ID,
) -> OrchestrationIntentPolicyMappingRegistry:
    ordered = tuple(sorted(records, key=lambda item: item.identifier.mapping_id))
    mapping_ids = [record.identifier.mapping_id for record in ordered]
    if len(mapping_ids) != len(set(mapping_ids)):
        duplicates = sorted({mapping_id for mapping_id in mapping_ids if mapping_ids.count(mapping_id) > 1})
        raise ValueError(f"Duplicate orchestration intent-policy mapping ids are not allowed: {', '.join(duplicates)}")
    return OrchestrationIntentPolicyMappingRegistry(
        registry_id=registry_id,
        schema_version=DEFAULT_MAPPING_SCHEMA_VERSION,
        records=ordered,
        registry_metadata={
            "phase": "v3.6.phase_5",
            "purpose": "deterministic_orchestration_intent_policy_mapping",
            "planning_only": True,
            "non_production": True,
            "intent_policy_mapping_only": True,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "recommendation_behavior_enabled": False,
            "optimization_behavior_enabled": False,
            "autonomous_behavior_enabled": False,
            "production_runtime_behavior_enabled": False,
        },
    )


def default_orchestration_intent_policy_mapping_records() -> tuple[OrchestrationIntentPolicyMappingRecord, ...]:
    intent_registry = default_orchestration_intent_registry()
    return tuple(_mapping_record(intent) for intent in intent_registry.records)


def registered_mapping_ids(registry: OrchestrationIntentPolicyMappingRegistry) -> tuple[str, ...]:
    return tuple(sorted(record.identifier.mapping_id for record in registry.records))


def get_registered_mapping_record(
    registry: OrchestrationIntentPolicyMappingRegistry,
    mapping_id: str,
) -> OrchestrationIntentPolicyMappingRecord | None:
    for record in registry.records:
        if record.identifier.mapping_id == mapping_id:
            return record
    return None


def get_registered_mapping_record_for_intent(
    registry: OrchestrationIntentPolicyMappingRegistry,
    intent_id: str,
) -> OrchestrationIntentPolicyMappingRecord | None:
    for record in registry.records:
        if record.identifier.intent_id == intent_id:
            return record
    return None


def export_default_orchestration_intent_policy_mapping_registry() -> dict[str, object]:
    return export_mapping_registry(default_orchestration_intent_policy_mapping_registry())


def serialize_default_orchestration_intent_policy_mapping_registry() -> str:
    return serialize_mapping_registry(default_orchestration_intent_policy_mapping_registry())


def hash_default_orchestration_intent_policy_mapping_registry() -> str:
    return hash_mapping_registry(default_orchestration_intent_policy_mapping_registry())


def _mapping_record(intent: OrchestrationIntentRecord) -> OrchestrationIntentPolicyMappingRecord:
    spec = _mapping_spec_for_intent(intent.identifier.intent_id)
    mapping_id = intent.identifier.intent_id.replace("v3_6.intent.", "v3_6.mapping.")
    mapping_state = _mapping_state(intent.support_state)
    classifications = _mapping_classifications(intent)
    return OrchestrationIntentPolicyMappingRecord(
        identifier=OrchestrationIntentPolicyMappingIdentifier(
            mapping_id=mapping_id,
            intent_id=intent.identifier.intent_id,
            namespace="v3_6.orchestration_intent_policy_mapping",
            version="1",
        ),
        mapping_state=mapping_state,
        mapping_classifications=classifications,
        policy_ids=tuple(sorted(spec["policy_ids"])),
        governance_boundaries=intent.governance_boundaries,
        compatibility_domains=intent.compatibility_domains,
        dependency_domains=intent.dependency_domains,
        blocker_domains=intent.blocker_domains,
        unsupported_domains=intent.unsupported_domains,
        prohibited_domains=intent.prohibited_domains,
        supported_domains=intent.supported_domains,
        mapping_rationale=tuple(sorted(spec["mapping_rationale"])),
        provenance=OrchestrationIntentPolicyMappingProvenance(
            source_phase="v3.6_phase_5_deterministic_orchestration_intent_policy_mapping",
            source_artifact="backend/app/runtime_orchestration/orchestration_intent_policy_mapping_registry.py",
            intent_id=intent.identifier.intent_id,
            policy_ids=tuple(sorted(spec["policy_ids"])),
            compatibility_relationship_ids=intent.provenance.compatibility_relationship_ids,
            replay_reference_ids=(f"{mapping_id}.replay",),
            rollback_reference_ids=(f"{mapping_id}.rollback",),
            governance_reference_ids=(
                "v3_6_intent_integrity_stable",
                "v3_6_policy_foundation_integrity_stable",
                "v3_6_mapping_governance_first",
            ),
        ),
        governance_metadata={
            "planning_only": True,
            "non_production": True,
            "deterministic_only": True,
            "governance_first": True,
            "intent_policy_mapping_only": True,
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
        explainability_reference_ids=(f"{mapping_id}.explainability",),
        integrity_reference_ids=(f"{mapping_id}.integrity",),
    )


def _mapping_state(intent_support_state: str) -> str:
    if intent_support_state == INTENT_SUPPORTED:
        return MAPPING_SUPPORTED
    if intent_support_state == INTENT_UNSUPPORTED:
        return MAPPING_UNSUPPORTED
    if intent_support_state == INTENT_PROHIBITED:
        return MAPPING_PROHIBITED
    return MAPPING_UNSUPPORTED


def _mapping_classifications(intent: OrchestrationIntentRecord) -> tuple[str, ...]:
    classifications = {MAPPING_INTENT_TO_POLICY, MAPPING_INTENT_TO_GOVERNANCE}
    if intent.compatibility_domains:
        classifications.add(MAPPING_INTENT_TO_COMPATIBILITY)
    if intent.dependency_domains:
        classifications.add(MAPPING_INTENT_TO_DEPENDENCY)
    if intent.blocker_domains:
        classifications.add(MAPPING_INTENT_TO_BLOCKER)
    if intent.unsupported_domains:
        classifications.add(MAPPING_INTENT_TO_UNSUPPORTED_DOMAIN)
    if intent.prohibited_domains:
        classifications.add(MAPPING_INTENT_TO_PROHIBITED_DOMAIN)
    if intent.supported_domains:
        classifications.add(MAPPING_INTENT_TO_SUPPORTED_DOMAIN)
    return tuple(sorted(classifications))


def _mapping_spec_for_intent(intent_id: str) -> dict[str, tuple[str, ...]]:
    specs: dict[str, dict[str, tuple[str, ...]]] = {
        "v3_6.intent.informational": {
            "policy_ids": (POLICY_MODELING_ALLOWED, POLICY_EXPLAINABILITY_ALLOWED),
            "mapping_rationale": (
                "informational intent maps to deterministic policy modeling",
                "informational intent maps to explainability visibility",
            ),
        },
        "v3_6.intent.compatibility-check": {
            "policy_ids": (
                POLICY_MODELING_ALLOWED,
                POLICY_GOVERNANCE_BOUNDARY_ALLOWED,
                POLICY_EXPLAINABILITY_ALLOWED,
                POLICY_INTEGRITY_ALLOWED,
            ),
            "mapping_rationale": (
                "compatibility-check intent maps to policy modeling before compatibility evaluation",
                "compatibility-check intent maps to governance and integrity boundaries",
            ),
        },
        "v3_6.intent.governance-review": {
            "policy_ids": (
                POLICY_GOVERNANCE_BOUNDARY_ALLOWED,
                POLICY_EXPLAINABILITY_ALLOWED,
                POLICY_INTEGRITY_ALLOWED,
                POLICY_PRODUCTION_RUNTIME_PROHIBITED,
            ),
            "mapping_rationale": (
                "governance-review intent maps to governance boundary policy",
                "governance-review intent surfaces production runtime prohibition without reading runtime state",
            ),
        },
        "v3_6.intent.dependency-analysis": {
            "policy_ids": (POLICY_MODELING_ALLOWED, POLICY_INTEGRITY_ALLOWED, POLICY_EXECUTION_PROHIBITED),
            "mapping_rationale": (
                "dependency-analysis intent maps to deterministic policy integrity",
                "dependency-analysis intent preserves execution prohibition visibility",
            ),
        },
        "v3_6.intent.continuity-analysis": {
            "policy_ids": (POLICY_MODELING_ALLOWED, POLICY_EXPLAINABILITY_ALLOWED, POLICY_INTEGRITY_ALLOWED),
            "mapping_rationale": (
                "continuity-analysis intent maps to provenance and integrity continuity policies",
                "continuity-analysis intent maps to explainability continuity",
            ),
        },
        "v3_6.intent.policy-boundary": {
            "policy_ids": (
                POLICY_MODELING_ALLOWED,
                POLICY_GOVERNANCE_BOUNDARY_ALLOWED,
                POLICY_EXECUTION_PROHIBITED,
                POLICY_ROUTING_PROHIBITED,
                POLICY_AUTONOMY_UNSUPPORTED,
                POLICY_PRODUCTION_RUNTIME_PROHIBITED,
            ),
            "mapping_rationale": (
                "policy-boundary intent maps to allowed, unsupported, and prohibited policy boundaries",
                "policy-boundary intent keeps execution, routing, autonomy, and production runtime limits visible",
            ),
        },
        "v3_6.intent.orchestration-simulation": {
            "policy_ids": (
                POLICY_MODELING_ALLOWED,
                POLICY_EXPLAINABILITY_ALLOWED,
                POLICY_ROUTING_PROHIBITED,
                POLICY_EXECUTION_PROHIBITED,
            ),
            "mapping_rationale": (
                "orchestration-simulation intent maps only to planning visibility",
                "orchestration-simulation intent preserves routing and execution prohibitions",
            ),
        },
        "v3_6.intent.unsupported-domain": {
            "policy_ids": (POLICY_AUTONOMY_UNSUPPORTED, POLICY_EXECUTION_PROHIBITED),
            "mapping_rationale": (
                "unsupported-domain intent maps to unsupported autonomy policy",
                "unsupported-domain intent keeps execution prohibition visible",
            ),
        },
        "v3_6.intent.prohibited-domain": {
            "policy_ids": (
                POLICY_EXECUTION_PROHIBITED,
                POLICY_ROUTING_PROHIBITED,
                POLICY_PRODUCTION_RUNTIME_PROHIBITED,
            ),
            "mapping_rationale": (
                "prohibited-domain intent maps to execution, routing, and production runtime prohibitions",
                "prohibited-domain intent remains fail-visible before compatibility evaluation",
            ),
        },
    }
    return specs[intent_id]
