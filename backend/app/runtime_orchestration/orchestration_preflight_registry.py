"""Deterministic orchestration preflight registry for v3.6 Phase 6."""

from __future__ import annotations

from typing import Iterable

from .orchestration_intent_policy_mapping_models import OrchestrationIntentPolicyMappingRecord
from .orchestration_intent_policy_mapping_registry import default_orchestration_intent_policy_mapping_registry
from .orchestration_preflight_models import (
    PREFLIGHT_CLASSIFICATION_BLOCKER,
    PREFLIGHT_CLASSIFICATION_COMPATIBILITY,
    PREFLIGHT_CLASSIFICATION_CONTINUITY,
    PREFLIGHT_CLASSIFICATION_DEPENDENCY,
    PREFLIGHT_CLASSIFICATION_GOVERNANCE,
    PREFLIGHT_CLASSIFICATION_PROHIBITED,
    PREFLIGHT_CLASSIFICATION_THEORETICAL_SUPPORT,
    PREFLIGHT_CLASSIFICATION_UNSUPPORTED,
    PREFLIGHT_COMPATIBILITY_BLOCKED,
    PREFLIGHT_DEPENDENCY_BLOCKED,
    PREFLIGHT_GOVERNANCE_BLOCKED,
    PREFLIGHT_PROHIBITED,
    PREFLIGHT_SUPPORTED,
    PREFLIGHT_UNSUPPORTED,
    OrchestrationPreflightIdentifier,
    OrchestrationPreflightProvenance,
    OrchestrationPreflightRecord,
    OrchestrationPreflightRegistry,
    export_preflight_registry,
    hash_preflight_registry,
    serialize_preflight_registry,
)


DEFAULT_PREFLIGHT_REGISTRY_ID = "v3_6_orchestration_preflight_registry"
DEFAULT_PREFLIGHT_SCHEMA_VERSION = "v3_6.orchestration_preflight_registry.1"


def default_orchestration_preflight_registry() -> OrchestrationPreflightRegistry:
    return build_orchestration_preflight_registry(default_orchestration_preflight_records())


def build_orchestration_preflight_registry(
    records: Iterable[OrchestrationPreflightRecord],
    registry_id: str = DEFAULT_PREFLIGHT_REGISTRY_ID,
) -> OrchestrationPreflightRegistry:
    ordered = tuple(sorted(records, key=lambda item: item.identifier.preflight_id))
    preflight_ids = [record.identifier.preflight_id for record in ordered]
    if len(preflight_ids) != len(set(preflight_ids)):
        duplicates = sorted({preflight_id for preflight_id in preflight_ids if preflight_ids.count(preflight_id) > 1})
        raise ValueError(f"Duplicate orchestration preflight ids are not allowed: {', '.join(duplicates)}")
    return OrchestrationPreflightRegistry(
        registry_id=registry_id,
        schema_version=DEFAULT_PREFLIGHT_SCHEMA_VERSION,
        records=ordered,
        registry_metadata={
            "phase": "v3.6.phase_6",
            "purpose": "deterministic_orchestration_preflight_evaluation",
            "planning_only": True,
            "non_production": True,
            "preflight_evaluation_only": True,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "recommendation_behavior_enabled": False,
            "optimization_behavior_enabled": False,
            "autonomous_behavior_enabled": False,
            "production_runtime_behavior_enabled": False,
        },
    )


def default_orchestration_preflight_records() -> tuple[OrchestrationPreflightRecord, ...]:
    mapping_registry = default_orchestration_intent_policy_mapping_registry()
    return tuple(_preflight_record(mapping) for mapping in mapping_registry.records)


def registered_preflight_ids(registry: OrchestrationPreflightRegistry) -> tuple[str, ...]:
    return tuple(sorted(record.identifier.preflight_id for record in registry.records))


def get_registered_preflight_record(
    registry: OrchestrationPreflightRegistry,
    preflight_id: str,
) -> OrchestrationPreflightRecord | None:
    for record in registry.records:
        if record.identifier.preflight_id == preflight_id:
            return record
    return None


def get_registered_preflight_record_for_intent(
    registry: OrchestrationPreflightRegistry,
    intent_id: str,
) -> OrchestrationPreflightRecord | None:
    for record in registry.records:
        if record.identifier.intent_id == intent_id:
            return record
    return None


def export_default_orchestration_preflight_registry() -> dict[str, object]:
    return export_preflight_registry(default_orchestration_preflight_registry())


def serialize_default_orchestration_preflight_registry() -> str:
    return serialize_preflight_registry(default_orchestration_preflight_registry())


def hash_default_orchestration_preflight_registry() -> str:
    return hash_preflight_registry(default_orchestration_preflight_registry())


def _preflight_record(mapping: OrchestrationIntentPolicyMappingRecord) -> OrchestrationPreflightRecord:
    preflight_state, rationale = _preflight_spec_for_mapping(mapping.identifier.mapping_id)
    preflight_id = mapping.identifier.mapping_id.replace("v3_6.mapping.", "v3_6.preflight.")
    classifications = _preflight_classifications(mapping, preflight_state)
    return OrchestrationPreflightRecord(
        identifier=OrchestrationPreflightIdentifier(
            preflight_id=preflight_id,
            intent_id=mapping.identifier.intent_id,
            mapping_id=mapping.identifier.mapping_id,
            namespace="v3_6.orchestration_preflight",
            version="1",
        ),
        preflight_state=preflight_state,
        preflight_classifications=classifications,
        theoretically_supportable=preflight_state == PREFLIGHT_SUPPORTED,
        policy_ids=mapping.policy_ids,
        governance_boundaries=mapping.governance_boundaries,
        compatibility_domains=mapping.compatibility_domains,
        dependency_domains=mapping.dependency_domains,
        blocker_domains=mapping.blocker_domains,
        unsupported_domains=mapping.unsupported_domains,
        prohibited_domains=mapping.prohibited_domains,
        supported_domains=mapping.supported_domains,
        preflight_rationale=tuple(sorted(rationale)),
        provenance=OrchestrationPreflightProvenance(
            source_phase="v3.6_phase_6_deterministic_orchestration_preflight_evaluation",
            source_artifact="backend/app/runtime_orchestration/orchestration_preflight_registry.py",
            intent_id=mapping.identifier.intent_id,
            mapping_id=mapping.identifier.mapping_id,
            policy_ids=mapping.policy_ids,
            compatibility_relationship_ids=mapping.provenance.compatibility_relationship_ids,
            replay_reference_ids=(f"{preflight_id}.replay",),
            rollback_reference_ids=(f"{preflight_id}.rollback",),
            governance_reference_ids=(
                "v3_6_mapping_integrity_stable",
                "v3_6_preflight_governance_first",
                "v3_6_preflight_planning_only",
            ),
        ),
        governance_metadata={
            "planning_only": True,
            "non_production": True,
            "deterministic_only": True,
            "governance_first": True,
            "preflight_evaluation_only": True,
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
        explainability_reference_ids=(f"{preflight_id}.explainability",),
        integrity_reference_ids=(f"{preflight_id}.integrity",),
    )


def _preflight_spec_for_mapping(mapping_id: str) -> tuple[str, tuple[str, ...]]:
    specs: dict[str, tuple[str, tuple[str, ...]]] = {
        "v3_6.mapping.informational": (
            PREFLIGHT_SUPPORTED,
            (
                "informational intent is theoretically supportable for planning-only preflight visibility",
                "policy state inspection has no preflight blocker",
            ),
        ),
        "v3_6.mapping.compatibility-check": (
            PREFLIGHT_SUPPORTED,
            (
                "compatibility-check intent is theoretically supportable as preflight analysis",
                "compatibility domains are visible before compatibility evaluation",
            ),
        ),
        "v3_6.mapping.governance-review": (
            PREFLIGHT_GOVERNANCE_BLOCKED,
            (
                "governance-review intent exposes production runtime governance boundaries",
                "theoretical preflight remains blocked by governance visibility until production runtime constraints stay prohibited",
            ),
        ),
        "v3_6.mapping.dependency-analysis": (
            PREFLIGHT_DEPENDENCY_BLOCKED,
            (
                "dependency-analysis intent exposes dependency-blocked compatibility domains",
                "theoretical preflight remains blocked by unresolved execution dependency visibility",
            ),
        ),
        "v3_6.mapping.continuity-analysis": (
            PREFLIGHT_SUPPORTED,
            (
                "continuity-analysis intent is theoretically supportable for deterministic preflight continuity inspection",
                "provenance, replay, and rollback chains are visible",
            ),
        ),
        "v3_6.mapping.policy-boundary": (
            PREFLIGHT_COMPATIBILITY_BLOCKED,
            (
                "policy-boundary intent exposes prohibited and unsupported policy pairings",
                "theoretical preflight remains compatibility-blocked by execution and routing boundaries",
            ),
        ),
        "v3_6.mapping.orchestration-simulation": (
            PREFLIGHT_PROHIBITED,
            (
                "orchestration-simulation intent is planning-only but includes prohibited execution-simulation domains",
                "theoretical preflight remains prohibited from execution-capable simulation",
            ),
        ),
        "v3_6.mapping.unsupported-domain": (
            PREFLIGHT_UNSUPPORTED,
            (
                "unsupported-domain intent remains unsupported and fail-visible",
                "autonomous orchestration domains are not supportable in preflight evaluation",
            ),
        ),
        "v3_6.mapping.prohibited-domain": (
            PREFLIGHT_PROHIBITED,
            (
                "prohibited-domain intent remains prohibited and fail-visible",
                "execution, routing, and production runtime domains cannot become preflight execution paths",
            ),
        ),
    }
    return specs[mapping_id]


def _preflight_classifications(
    mapping: OrchestrationIntentPolicyMappingRecord,
    preflight_state: str,
) -> tuple[str, ...]:
    classifications = {
        PREFLIGHT_CLASSIFICATION_THEORETICAL_SUPPORT,
        PREFLIGHT_CLASSIFICATION_GOVERNANCE,
        PREFLIGHT_CLASSIFICATION_CONTINUITY,
    }
    if mapping.compatibility_domains:
        classifications.add(PREFLIGHT_CLASSIFICATION_COMPATIBILITY)
    if mapping.dependency_domains:
        classifications.add(PREFLIGHT_CLASSIFICATION_DEPENDENCY)
    if mapping.blocker_domains:
        classifications.add(PREFLIGHT_CLASSIFICATION_BLOCKER)
    if mapping.unsupported_domains or preflight_state == PREFLIGHT_UNSUPPORTED:
        classifications.add(PREFLIGHT_CLASSIFICATION_UNSUPPORTED)
    if mapping.prohibited_domains or preflight_state == PREFLIGHT_PROHIBITED:
        classifications.add(PREFLIGHT_CLASSIFICATION_PROHIBITED)
    return tuple(sorted(classifications))
