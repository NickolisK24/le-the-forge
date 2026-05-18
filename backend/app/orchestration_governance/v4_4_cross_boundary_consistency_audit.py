"""Audit for deterministic v4.4 cross-boundary consistency intelligence."""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_cross_boundary_consistency_hashing import (
    deterministic_cross_boundary_consistency_hash,
    hash_compatibility_consistency,
    hash_consistency_evidence_metadata,
    hash_consistency_explainability,
    hash_consistency_record,
    hash_continuity_consistency,
    hash_cross_boundary_consistency_identity,
    hash_cross_boundary_consistency_intelligence,
    hash_cross_boundary_diagnostic,
    hash_lineage_consistency,
    hash_multi_boundary_relationship_record,
    hash_provenance_consistency,
)
from .v4_4_cross_boundary_consistency_models import (
    CONSISTENCY_STATE_AMBIGUOUS,
    CONSISTENCY_STATE_COMPATIBLE,
    CONSISTENCY_STATE_CONSISTENT,
    CONSISTENCY_STATE_DEGRADED,
    CONSISTENCY_STATE_INCOMPATIBLE,
    CONSISTENCY_STATE_INCONSISTENT,
    CONSISTENCY_STATE_PARTIALLY_CONSISTENT,
    CROSS_BOUNDARY_CONSISTENCY_STATES,
    V4_4_CROSS_BOUNDARY_CONSISTENCY_REPORT_SCHEMA_VERSION,
    V4_4_CROSS_BOUNDARY_CONSISTENCY_STATUS_BLOCKED,
    V4_4_CROSS_BOUNDARY_CONSISTENCY_STATUS_STABLE,
    CrossBoundaryConsistencyIntelligence,
    default_cross_boundary_consistency_intelligence,
)
from .v4_4_cross_boundary_consistency_serialization import (
    export_cross_boundary_consistency_intelligence,
    serialize_cross_boundary_consistency_intelligence,
)
from .v4_4_cross_boundary_consistency_visibility import (
    aggregate_cross_boundary_diagnostics,
    compatibility_consistency_visibility,
    count_combined_consistency_states,
    count_compatibility_consistency_states,
    count_consistency_record_states,
    count_continuity_consistency_states,
    count_relationship_states,
    cross_boundary_consistency_summaries,
    degraded_consistency_visibility,
    fail_visible_consistency_ambiguity_summaries,
    governance_safe_consistency_explainability,
    incompatibility_visibility,
    lineage_consistency_visibility,
    provenance_consistency_visibility,
    relationship_consistency_visibility,
    validate_required_consistency_visibility,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_runtime_behavior_enabled",
        "orchestration_execution_enabled",
        "execution_enabled",
    ),
    "enabled_orchestration_authorization_count": (
        "orchestration_authorization_enabled",
        "authorization_enabled",
    ),
    "enabled_orchestration_approval_count": (
        "orchestration_approval_enabled",
        "approval_enabled",
        "readiness_approval_enabled",
    ),
    "enabled_dispatch_execution_count": (
        "dispatch_execution_enabled",
        "orchestration_dispatch_enabled",
        "dispatch_enabled",
    ),
    "enabled_routing_execution_count": (
        "routing_execution_enabled",
        "orchestration_routing_enabled",
        "routing_enabled",
    ),
    "enabled_operational_mutation_count": (
        "operational_mutation_enabled",
        "runtime_mutation_enabled",
        "mutation_enabled",
    ),
}
PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_4_cross_boundary_consistency() -> CrossBoundaryConsistencyIntelligence:
    return default_cross_boundary_consistency_intelligence()


def _iter_dataclass_objects(value: Any) -> Iterable[Any]:
    if is_dataclass(value) and not isinstance(value, type):
        yield value
        for item in value.__dict__.values():
            yield from _iter_dataclass_objects(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_dataclass_objects(item)
    elif isinstance(value, tuple | list | set):
        for item in value:
            yield from _iter_dataclass_objects(item)


def enabled_cross_boundary_consistency_capability_flags(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "consistency_record_id", None)
            or getattr(item, "relationship_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "compatibility_id", None)
            or getattr(item, "continuity_id", None)
            or getattr(item, "explainability_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "consistency_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def cross_boundary_consistency_capability_counter_values(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, int]:
    objects = tuple(_iter_dataclass_objects(intelligence))
    counters: dict[str, int] = {}
    for counter_name, field_names in CAPABILITY_COUNTER_FIELD_MAP.items():
        counters[counter_name] = sum(
            1
            for item in objects
            for field_name in field_names
            if bool(getattr(item, field_name, False))
        )
    return counters


def cross_boundary_consistency_equal(
    left: CrossBoundaryConsistencyIntelligence,
    right: CrossBoundaryConsistencyIntelligence,
) -> bool:
    return serialize_cross_boundary_consistency_intelligence(left) == serialize_cross_boundary_consistency_intelligence(right)


def validate_cross_boundary_consistency_ordering_stability(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "classifications": tuple(item.deterministic_order for item in intelligence.classifications),
        "consistency_records": tuple(item.deterministic_order for item in intelligence.consistency_records),
        "relationship_records": tuple(item.deterministic_order for item in intelligence.relationship_records),
        "diagnostics": tuple(item.deterministic_order for item in intelligence.diagnostics),
        "compatibility_consistency": tuple(item.deterministic_order for item in intelligence.compatibility_consistency),
        "continuity_consistency": tuple(item.deterministic_order for item in intelligence.continuity_consistency),
        "explainability": tuple(item.deterministic_order for item in intelligence.explainability),
    }
    unordered_groups = [name for name, orders in order_groups.items() if tuple(sorted(orders)) != orders]
    duplicate_groups = [name for name, orders in order_groups.items() if len(set(orders)) != len(orders)]
    return {
        "valid": not unordered_groups and not duplicate_groups,
        "unordered_groups": unordered_groups,
        "duplicate_order_groups": duplicate_groups,
        "order_groups": {name: list(orders) for name, orders in order_groups.items()},
    }


def validate_cross_boundary_consistency_serialization_and_hashing(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    rebuilt = build_v4_4_cross_boundary_consistency()
    serialized = serialize_cross_boundary_consistency_intelligence(intelligence)
    rebuilt_serialized = serialize_cross_boundary_consistency_intelligence(rebuilt)
    intelligence_hash = hash_cross_boundary_consistency_intelligence(intelligence)
    rebuilt_hash = hash_cross_boundary_consistency_intelligence(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and intelligence_hash == rebuilt_hash,
        "serialization_stable": serialized == rebuilt_serialized,
        "hashing_stable": intelligence_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "intelligence_hash": intelligence_hash,
        "rebuilt_intelligence_hash": rebuilt_hash,
    }


def validate_cross_boundary_consistency_visibility(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    required = validate_required_consistency_visibility(intelligence)
    combined_counts = count_combined_consistency_states(intelligence)
    diagnostics = aggregate_cross_boundary_diagnostics(intelligence.diagnostics)
    relationship = relationship_consistency_visibility(intelligence)
    compatibility = compatibility_consistency_visibility(intelligence)
    degradation = degraded_consistency_visibility(intelligence)
    ambiguity = fail_visible_consistency_ambiguity_summaries(intelligence)
    return {
        "valid": (
            required["valid"]
            and diagnostics["fail_visible"]
            and diagnostics["consistency_auto_resolution_enabled_count"] == 0
            and diagnostics["automatic_normalization_enabled_count"] == 0
            and diagnostics["automatic_remediation_enabled_count"] == 0
            and diagnostics["automatic_repair_enabled_count"] == 0
            and relationship["recommendation_enabled_count"] == 0
            and relationship["decision_enabled_count"] == 0
            and relationship["runtime_execution_enabled_count"] == 0
            and compatibility["authorization_enabled_count"] == 0
            and compatibility["approval_enabled_count"] == 0
            and compatibility["runtime_execution_enabled_count"] == 0
            and degradation["mutation_enabled_count"] == 0
            and len(ambiguity) > 0
        ),
        "combined_counts": combined_counts,
        "consistency_record_counts": count_consistency_record_states(intelligence.consistency_records),
        "relationship_counts": count_relationship_states(intelligence.relationship_records),
        "compatibility_counts": count_compatibility_consistency_states(
            intelligence.compatibility_consistency
        ),
        "continuity_counts": count_continuity_consistency_states(intelligence.continuity_consistency),
        "missing_states": required["missing_states"],
        "missing_fail_visible_states": required["missing_fail_visible_states"],
        "diagnostics": diagnostics,
        "relationship": relationship,
        "compatibility": compatibility,
        "degradation": degradation,
        "ambiguity_count": len(ambiguity),
    }


def validate_cross_boundary_replay_rollback_evidence(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    evidence = intelligence.evidence_metadata
    expected = (
        set(evidence.consistency_record_ids)
        | set(evidence.relationship_record_ids)
        | set(evidence.diagnostic_record_ids)
    )
    replay = set(evidence.replay_evidence_ids)
    rollback = set(evidence.rollback_evidence_ids)
    return {
        "valid": evidence.replay_safe and evidence.rollback_safe and replay == expected and rollback == expected,
        "expected_evidence_count": len(expected),
        "replay_safe_evidence_count": len(replay),
        "rollback_safe_evidence_count": len(rollback),
        "missing_replay_evidence_ids": sorted(expected - replay),
        "missing_rollback_evidence_ids": sorted(expected - rollback),
        "replay_safe": evidence.replay_safe,
        "rollback_safe": evidence.rollback_safe,
    }


def validate_cross_boundary_provenance_lineage_consistency(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_consistency
    lineage = intelligence.lineage_consistency
    return {
        "valid": (
            provenance.provenance_consistency_visible
            and lineage.lineage_consistency_visible
            and not provenance.hidden_source_inference_used
            and not lineage.ambiguous_lineage_inferred
        ),
        "provenance_consistency_visible": provenance.provenance_consistency_visible,
        "lineage_consistency_visible": lineage.lineage_consistency_visible,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
    }


def validate_cross_boundary_consistency_explainability(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    explainability = governance_safe_consistency_explainability(intelligence.explainability)
    return {
        "valid": (
            explainability["explainability_first"]
            and explainability["descriptive_only"]
            and explainability["recommendation_enabled_count"] == 0
            and explainability["decision_enabled_count"] == 0
            and explainability["scoring_enabled_count"] == 0
        ),
        "explainability": explainability,
    }


def validate_cross_boundary_consistency_non_operational(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    counters = cross_boundary_consistency_capability_counter_values(intelligence)
    enabled_flags = enabled_cross_boundary_consistency_capability_flags(intelligence)
    root_disabled = {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_authoritative": intelligence.non_authoritative,
        "non_enforcing": intelligence.non_enforcing,
        "non_remediating": intelligence.non_remediating,
        "non_resolving": intelligence.non_resolving,
        "non_normalizing": intelligence.non_normalizing,
        "non_mutating": intelligence.non_mutating,
        "planner_integration_disabled": not intelligence.planner_integration_enabled,
        "production_consumption_disabled": not intelligence.production_consumption_enabled,
        "runtime_mutation_disabled": not intelligence.runtime_mutation_enabled,
        "operational_mutation_disabled": not intelligence.operational_mutation_enabled,
        "consistency_auto_resolution_disabled": not intelligence.consistency_auto_resolution_enabled,
        "automatic_normalization_disabled": not intelligence.automatic_normalization_enabled,
        "automatic_remediation_disabled": not intelligence.automatic_remediation_enabled,
        "automatic_repair_disabled": not intelligence.automatic_repair_enabled,
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_cross_boundary_consistency(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_cross_boundary_consistency_ordering_stability(intelligence),
        "serialization_hashing": validate_cross_boundary_consistency_serialization_and_hashing(intelligence),
        "visibility": validate_cross_boundary_consistency_visibility(intelligence),
        "replay_rollback": validate_cross_boundary_replay_rollback_evidence(intelligence),
        "provenance_lineage": validate_cross_boundary_provenance_lineage_consistency(intelligence),
        "explainability": validate_cross_boundary_consistency_explainability(intelligence),
        "non_operational": validate_cross_boundary_consistency_non_operational(intelligence),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_4_cross_boundary_consistency_report() -> dict[str, Any]:
    intelligence = build_v4_4_cross_boundary_consistency()
    exported = export_cross_boundary_consistency_intelligence(intelligence)
    validation = validate_cross_boundary_consistency(intelligence)
    visibility = validation["validations"]["visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    replay_rollback = validation["validations"]["replay_rollback"]
    provenance_lineage = validation["validations"]["provenance_lineage"]
    explainability = validation["validations"]["explainability"]
    non_operational = validation["validations"]["non_operational"]
    combined_counts = visibility["combined_counts"]
    compatibility = visibility["compatibility"]
    degradation = visibility["degradation"]
    diagnostics = visibility["diagnostics"]
    deterministic_hash_evidence = {
        "identity_hash": hash_cross_boundary_consistency_identity(intelligence.identity),
        "intelligence_hash": hash_cross_boundary_consistency_intelligence(intelligence),
        "provenance_consistency_hash": hash_provenance_consistency(
            intelligence.provenance_consistency
        ),
        "lineage_consistency_hash": hash_lineage_consistency(intelligence.lineage_consistency),
        "evidence_metadata_hash": hash_consistency_evidence_metadata(intelligence.evidence_metadata),
        "consistency_record_hashes": {
            record.consistency_record_id: hash_consistency_record(record)
            for record in sorted(intelligence.consistency_records, key=lambda item: item.deterministic_order)
        },
        "relationship_record_hashes": {
            record.relationship_id: hash_multi_boundary_relationship_record(record)
            for record in sorted(intelligence.relationship_records, key=lambda item: item.deterministic_order)
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_cross_boundary_diagnostic(record)
            for record in sorted(intelligence.diagnostics, key=lambda item: item.deterministic_order)
        },
        "compatibility_consistency_hashes": {
            summary.compatibility_id: hash_compatibility_consistency(summary)
            for summary in sorted(intelligence.compatibility_consistency, key=lambda item: item.deterministic_order)
        },
        "continuity_consistency_hashes": {
            summary.continuity_id: hash_continuity_consistency(summary)
            for summary in sorted(intelligence.continuity_consistency, key=lambda item: item.deterministic_order)
        },
        "explainability_hashes": {
            record.explainability_id: hash_consistency_explainability(record)
            for record in sorted(intelligence.explainability, key=lambda item: item.deterministic_order)
        },
    }
    summary = {
        "consistency_record_count": len(intelligence.consistency_records),
        "cross_boundary_relationship_count": len(intelligence.relationship_records),
        "diagnostic_count": len(intelligence.diagnostics),
        "compatibility_consistency_count": len(intelligence.compatibility_consistency),
        "continuity_consistency_count": len(intelligence.continuity_consistency),
        "consistent_count": combined_counts[CONSISTENCY_STATE_CONSISTENT],
        "inconsistent_count": combined_counts[CONSISTENCY_STATE_INCONSISTENT],
        "partial_consistency_count": combined_counts[CONSISTENCY_STATE_PARTIALLY_CONSISTENT],
        "compatibility_count": compatibility["compatible_count"],
        "incompatibility_count": compatibility["incompatible_count"],
        "compatible_visibility_count": combined_counts[CONSISTENCY_STATE_COMPATIBLE],
        "incompatible_visibility_count": combined_counts[CONSISTENCY_STATE_INCOMPATIBLE],
        "degraded_consistency_count": degradation["degraded_count"],
        "degraded_visibility_count": combined_counts[CONSISTENCY_STATE_DEGRADED],
        "ambiguity_count": visibility["ambiguity_count"],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "deterministic_serialization_verified": serialization_hashing["serialization_stable"],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "replay_safe_evidence_verified": replay_rollback["replay_safe"],
        "rollback_safe_evidence_verified": replay_rollback["rollback_safe"],
        "cross_boundary_consistency_visibility_verified": visibility["valid"],
        "inconsistency_visibility_verified": combined_counts[CONSISTENCY_STATE_INCONSISTENT] > 0,
        "partial_consistency_visibility_verified": (
            combined_counts[CONSISTENCY_STATE_PARTIALLY_CONSISTENT] > 0
        ),
        "compatibility_consistency_verified": compatibility["descriptive_only"],
        "provenance_consistency_verified": provenance_lineage["provenance_consistency_visible"],
        "lineage_consistency_verified": provenance_lineage["lineage_consistency_visible"],
        "governance_safe_certification_verified": validation["valid"],
        "non_operational_certification_verified": non_operational["valid"],
        "explainability_visibility_verified": explainability["valid"],
        "validation_error_count": validation["validation_error_count"],
        "remaining_warning_count": 0,
        "remaining_blocker_count": 0,
        **non_operational["counters"],
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
    report: dict[str, Any] = {
        "report_schema_version": V4_4_CROSS_BOUNDARY_CONSISTENCY_REPORT_SCHEMA_VERSION,
        "phase_id": intelligence.identity.phase_id,
        "foundation_status": (
            V4_4_CROSS_BOUNDARY_CONSISTENCY_STATUS_STABLE
            if validation["valid"]
            else V4_4_CROSS_BOUNDARY_CONSISTENCY_STATUS_BLOCKED
        ),
        "summary": summary,
        "cross_boundary_consistency_intelligence": exported,
        "cross_boundary_consistency_visibility": cross_boundary_consistency_summaries(intelligence),
        "relationship_consistency_visibility": visibility["relationship"],
        "compatibility_consistency_visibility": compatibility,
        "incompatibility_visibility": incompatibility_visibility(intelligence),
        "degraded_consistency_visibility": degradation,
        "fail_visible_ambiguity_visibility": fail_visible_consistency_ambiguity_summaries(intelligence),
        "provenance_consistency_visibility": provenance_consistency_visibility(intelligence),
        "lineage_consistency_visibility": lineage_consistency_visibility(intelligence),
        "cross_boundary_diagnostics_visibility": diagnostics,
        "consistency_explainability_visibility": explainability["explainability"],
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": {
            "serialization_stable": serialization_hashing["serialization_stable"],
            "hashing_stable": serialization_hashing["hashing_stable"],
            "serialization_length": serialization_hashing["serialization_length"],
            "intelligence_hash": serialization_hashing["intelligence_hash"],
        },
        "replay_safe_evidence": replay_rollback,
        "rollback_safe_evidence": replay_rollback,
        "provenance_consistency_evidence": {
            "provenance_consistency": exported["provenance_consistency"],
            "provenance_consistency_visible": provenance_lineage["provenance_consistency_visible"],
            "hidden_source_inference_used": provenance_lineage["hidden_source_inference_used"],
        },
        "lineage_consistency_evidence": {
            "lineage_consistency": exported["lineage_consistency"],
            "lineage_consistency_visible": provenance_lineage["lineage_consistency_visible"],
            "ambiguous_lineage_inferred": provenance_lineage["ambiguous_lineage_inferred"],
        },
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "remaining_warnings": [],
        "remaining_blockers": [],
    }
    report["deterministic_report_hash"] = deterministic_cross_boundary_consistency_hash(report)
    return report


def contaminate_cross_boundary_consistency_for_non_operational_validation(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> CrossBoundaryConsistencyIntelligence:
    contaminated_record = replace(
        intelligence.consistency_records[0],
        runtime_execution_enabled=True,
        operational_mutation_enabled=True,
    )
    contaminated_relationship = replace(
        intelligence.relationship_records[0],
        orchestration_authorization_enabled=True,
        routing_execution_enabled=True,
    )
    contaminated_diagnostic = replace(
        intelligence.diagnostics[0],
        consistency_auto_resolution_enabled=True,
        automatic_normalization_enabled=True,
        automatic_remediation_enabled=True,
    )
    return replace(
        intelligence,
        consistency_records=(contaminated_record,) + intelligence.consistency_records[1:],
        relationship_records=(contaminated_relationship,) + intelligence.relationship_records[1:],
        diagnostics=(contaminated_diagnostic,) + intelligence.diagnostics[1:],
        orchestration_approval_enabled=True,
        dispatch_execution_enabled=True,
    )
