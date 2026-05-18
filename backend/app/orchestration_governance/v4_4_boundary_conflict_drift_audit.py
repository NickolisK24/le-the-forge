"""Audit for deterministic v4.4 boundary conflict drift intelligence."""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_boundary_conflict_drift_hashing import (
    deterministic_boundary_conflict_drift_hash,
    hash_boundary_conflict_drift_identity,
    hash_boundary_conflict_drift_intelligence,
    hash_boundary_drift_record,
    hash_compatibility_evidence,
    hash_conflict_diagnostic,
    hash_conflict_explainability,
    hash_degradation_summary,
    hash_drift_evidence_metadata,
    hash_lineage_degradation_metadata,
    hash_provenance_degradation_metadata,
    hash_refinement_divergence_record,
)
from .v4_4_boundary_conflict_drift_models import (
    BOUNDARY_CONFLICT_DRIFT_STATES,
    CONFLICT_DRIFT_STATE_AMBIGUOUS,
    CONFLICT_DRIFT_STATE_COMPATIBLE,
    CONFLICT_DRIFT_STATE_DEGRADED,
    CONFLICT_DRIFT_STATE_DRIFTED,
    CONFLICT_DRIFT_STATE_INCOMPATIBLE,
    CONFLICT_DRIFT_STATE_STALE,
    V4_4_BOUNDARY_CONFLICT_DRIFT_REPORT_SCHEMA_VERSION,
    V4_4_BOUNDARY_CONFLICT_DRIFT_STATUS_BLOCKED,
    V4_4_BOUNDARY_CONFLICT_DRIFT_STATUS_STABLE,
    BoundaryConflictDriftIntelligence,
    default_boundary_conflict_drift_intelligence,
)
from .v4_4_boundary_conflict_drift_serialization import (
    export_boundary_conflict_drift_intelligence,
    serialize_boundary_conflict_drift_intelligence,
)
from .v4_4_boundary_conflict_drift_visibility import (
    aggregate_conflict_diagnostics,
    compatibility_summaries,
    continuity_degradation_summaries,
    count_combined_conflict_drift_states,
    count_divergence_states,
    count_drift_states,
    fail_visible_ambiguity_summaries,
    governance_drift_summaries,
    governance_safe_conflict_explainability,
    incompatibility_summaries,
    lineage_degradation_visibility,
    provenance_degradation_visibility,
    refinement_divergence_summaries,
    validate_required_conflict_drift_visibility,
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


def build_v4_4_boundary_conflict_drift() -> BoundaryConflictDriftIntelligence:
    return default_boundary_conflict_drift_intelligence()


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


def enabled_conflict_drift_capability_flags(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "drift_id", None)
            or getattr(item, "divergence_id", None)
            or getattr(item, "conflict_id", None)
            or getattr(item, "compatibility_id", None)
            or getattr(item, "degradation_id", None)
            or getattr(item, "explainability_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "conflict_drift_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def conflict_drift_capability_counter_values(
    intelligence: BoundaryConflictDriftIntelligence,
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


def boundary_conflict_drift_equal(
    left: BoundaryConflictDriftIntelligence,
    right: BoundaryConflictDriftIntelligence,
) -> bool:
    return serialize_boundary_conflict_drift_intelligence(left) == serialize_boundary_conflict_drift_intelligence(right)


def validate_conflict_drift_ordering_stability(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "classifications": tuple(item.deterministic_order for item in intelligence.classifications),
        "drift_records": tuple(item.deterministic_order for item in intelligence.drift_records),
        "divergence_records": tuple(item.deterministic_order for item in intelligence.divergence_records),
        "conflict_diagnostics": tuple(item.deterministic_order for item in intelligence.conflict_diagnostics),
        "compatibility_evidence": tuple(item.deterministic_order for item in intelligence.compatibility_evidence),
        "degradation_summaries": tuple(item.deterministic_order for item in intelligence.degradation_summaries),
        "explainability": tuple(item.deterministic_order for item in intelligence.explainability),
        "conflict_lineage_visibility": tuple(item.deterministic_order for item in intelligence.conflict_lineage_visibility),
        "conflict_ancestry_visibility": tuple(item.deterministic_order for item in intelligence.conflict_ancestry_visibility),
    }
    unordered_groups = [name for name, orders in order_groups.items() if tuple(sorted(orders)) != orders]
    duplicate_groups = [name for name, orders in order_groups.items() if len(set(orders)) != len(orders)]
    return {
        "valid": not unordered_groups and not duplicate_groups,
        "unordered_groups": unordered_groups,
        "duplicate_order_groups": duplicate_groups,
        "order_groups": {name: list(orders) for name, orders in order_groups.items()},
    }


def validate_conflict_drift_serialization_and_hashing(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    rebuilt = build_v4_4_boundary_conflict_drift()
    serialized = serialize_boundary_conflict_drift_intelligence(intelligence)
    rebuilt_serialized = serialize_boundary_conflict_drift_intelligence(rebuilt)
    intelligence_hash = hash_boundary_conflict_drift_intelligence(intelligence)
    rebuilt_hash = hash_boundary_conflict_drift_intelligence(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and intelligence_hash == rebuilt_hash,
        "serialization_stable": serialized == rebuilt_serialized,
        "hashing_stable": intelligence_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "intelligence_hash": intelligence_hash,
        "rebuilt_intelligence_hash": rebuilt_hash,
    }


def validate_conflict_drift_visibility(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    required = validate_required_conflict_drift_visibility(intelligence)
    combined_counts = count_combined_conflict_drift_states(intelligence)
    diagnostics = aggregate_conflict_diagnostics(intelligence.conflict_diagnostics)
    ambiguity = fail_visible_ambiguity_summaries(intelligence)
    compatibility = compatibility_summaries(intelligence)
    degradation = continuity_degradation_summaries(intelligence.degradation_summaries)
    return {
        "valid": (
            required["valid"]
            and diagnostics["fail_visible"]
            and diagnostics["conflict_auto_resolution_enabled_count"] == 0
            and diagnostics["automatic_remediation_enabled_count"] == 0
            and diagnostics["automatic_repair_enabled_count"] == 0
            and compatibility["authorization_enabled_count"] == 0
            and compatibility["approval_enabled_count"] == 0
            and compatibility["runtime_execution_enabled_count"] == 0
            and degradation["mutation_enabled_count"] == 0
            and len(ambiguity) > 0
        ),
        "combined_counts": combined_counts,
        "drift_counts": count_drift_states(intelligence.drift_records),
        "divergence_counts": count_divergence_states(intelligence.divergence_records),
        "missing_states": required["missing_states"],
        "missing_fail_visible_states": required["missing_fail_visible_states"],
        "diagnostics": diagnostics,
        "compatibility": compatibility,
        "degradation": degradation,
        "ambiguity_count": len(ambiguity),
    }


def validate_replay_rollback_evidence(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    evidence = intelligence.drift_evidence_metadata
    expected = (
        set(evidence.drift_record_ids)
        | set(evidence.divergence_record_ids)
        | set(evidence.compatibility_record_ids)
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


def validate_provenance_lineage_visibility(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_degradation_metadata
    lineage = intelligence.lineage_degradation_metadata
    return {
        "valid": (
            provenance.provenance_continuity_visible
            and lineage.lineage_continuity_visible
            and not provenance.hidden_source_inference_used
            and not lineage.ambiguous_lineage_inferred
        ),
        "provenance_continuity_visible": provenance.provenance_continuity_visible,
        "lineage_continuity_visible": lineage.lineage_continuity_visible,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
    }


def validate_conflict_drift_explainability(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    explainability = governance_safe_conflict_explainability(intelligence.explainability)
    return {
        "valid": (
            explainability["explainability_first"]
            and explainability["descriptive_only"]
            and explainability["recommendation_enabled_count"] == 0
            and explainability["decision_enabled_count"] == 0
        ),
        "explainability": explainability,
    }


def validate_conflict_drift_non_operational(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    counters = conflict_drift_capability_counter_values(intelligence)
    enabled_flags = enabled_conflict_drift_capability_flags(intelligence)
    root_disabled = {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_authoritative": intelligence.non_authoritative,
        "non_remediating": intelligence.non_remediating,
        "non_resolving": intelligence.non_resolving,
        "non_mutating": intelligence.non_mutating,
        "planner_integration_disabled": not intelligence.planner_integration_enabled,
        "production_consumption_disabled": not intelligence.production_consumption_enabled,
        "runtime_mutation_disabled": not intelligence.runtime_mutation_enabled,
        "operational_mutation_disabled": not intelligence.operational_mutation_enabled,
        "conflict_auto_resolution_disabled": not intelligence.conflict_auto_resolution_enabled,
        "automatic_remediation_disabled": not intelligence.automatic_remediation_enabled,
        "automatic_repair_disabled": not intelligence.automatic_repair_enabled,
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_boundary_conflict_drift(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_conflict_drift_ordering_stability(intelligence),
        "serialization_hashing": validate_conflict_drift_serialization_and_hashing(intelligence),
        "visibility": validate_conflict_drift_visibility(intelligence),
        "replay_rollback": validate_replay_rollback_evidence(intelligence),
        "provenance_lineage": validate_provenance_lineage_visibility(intelligence),
        "explainability": validate_conflict_drift_explainability(intelligence),
        "non_operational": validate_conflict_drift_non_operational(intelligence),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_4_boundary_conflict_drift_report() -> dict[str, Any]:
    intelligence = build_v4_4_boundary_conflict_drift()
    exported = export_boundary_conflict_drift_intelligence(intelligence)
    validation = validate_boundary_conflict_drift(intelligence)
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
        "identity_hash": hash_boundary_conflict_drift_identity(intelligence.identity),
        "intelligence_hash": hash_boundary_conflict_drift_intelligence(intelligence),
        "provenance_degradation_hash": hash_provenance_degradation_metadata(
            intelligence.provenance_degradation_metadata
        ),
        "lineage_degradation_hash": hash_lineage_degradation_metadata(
            intelligence.lineage_degradation_metadata
        ),
        "drift_evidence_hash": hash_drift_evidence_metadata(intelligence.drift_evidence_metadata),
        "drift_record_hashes": {
            record.drift_id: hash_boundary_drift_record(record)
            for record in sorted(intelligence.drift_records, key=lambda item: item.deterministic_order)
        },
        "divergence_record_hashes": {
            record.divergence_id: hash_refinement_divergence_record(record)
            for record in sorted(intelligence.divergence_records, key=lambda item: item.deterministic_order)
        },
        "conflict_diagnostic_hashes": {
            record.conflict_id: hash_conflict_diagnostic(record)
            for record in sorted(intelligence.conflict_diagnostics, key=lambda item: item.deterministic_order)
        },
        "compatibility_evidence_hashes": {
            record.compatibility_id: hash_compatibility_evidence(record)
            for record in sorted(intelligence.compatibility_evidence, key=lambda item: item.deterministic_order)
        },
        "degradation_summary_hashes": {
            summary.degradation_id: hash_degradation_summary(summary)
            for summary in sorted(intelligence.degradation_summaries, key=lambda item: item.deterministic_order)
        },
        "explainability_hashes": {
            record.explainability_id: hash_conflict_explainability(record)
            for record in sorted(intelligence.explainability, key=lambda item: item.deterministic_order)
        },
    }
    summary = {
        "drift_record_count": len(intelligence.drift_records),
        "divergence_record_count": len(intelligence.divergence_records),
        "compatibility_evidence_count": len(intelligence.compatibility_evidence),
        "compatibility_count": compatibility["compatible_count"],
        "incompatibility_count": compatibility["incompatible_count"],
        "continuity_degradation_count": degradation["degradation_count"],
        "degraded_visibility_count": combined_counts[CONFLICT_DRIFT_STATE_DEGRADED],
        "drifted_visibility_count": combined_counts[CONFLICT_DRIFT_STATE_DRIFTED],
        "divergent_visibility_count": combined_counts["divergent"],
        "ambiguity_propagation_count": visibility["ambiguity_count"],
        "fail_visible_conflict_count": diagnostics["diagnostic_count"],
        "stale_visibility_count": combined_counts[CONFLICT_DRIFT_STATE_STALE],
        "compatible_visibility_count": combined_counts[CONFLICT_DRIFT_STATE_COMPATIBLE],
        "incompatible_visibility_count": combined_counts[CONFLICT_DRIFT_STATE_INCOMPATIBLE],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "deterministic_serialization_verified": serialization_hashing["serialization_stable"],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "replay_safe_evidence_verified": replay_rollback["replay_safe"],
        "rollback_safe_evidence_verified": replay_rollback["rollback_safe"],
        "deterministic_conflict_visibility_verified": visibility["valid"],
        "deterministic_drift_visibility_verified": visibility["valid"],
        "compatibility_visibility_verified": compatibility["descriptive_only"],
        "provenance_continuity_verified": provenance_lineage["provenance_continuity_visible"],
        "lineage_continuity_verified": provenance_lineage["lineage_continuity_visible"],
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
        "report_schema_version": V4_4_BOUNDARY_CONFLICT_DRIFT_REPORT_SCHEMA_VERSION,
        "phase_id": intelligence.identity.phase_id,
        "foundation_status": (
            V4_4_BOUNDARY_CONFLICT_DRIFT_STATUS_STABLE
            if validation["valid"]
            else V4_4_BOUNDARY_CONFLICT_DRIFT_STATUS_BLOCKED
        ),
        "summary": summary,
        "boundary_conflict_drift_intelligence": exported,
        "governance_drift_visibility": governance_drift_summaries(intelligence),
        "refinement_divergence_visibility": refinement_divergence_summaries(intelligence),
        "compatibility_visibility": compatibility,
        "incompatibility_visibility": incompatibility_summaries(intelligence),
        "continuity_degradation_visibility": degradation,
        "fail_visible_ambiguity_visibility": fail_visible_ambiguity_summaries(intelligence),
        "provenance_degradation_visibility": provenance_degradation_visibility(intelligence),
        "lineage_degradation_visibility": lineage_degradation_visibility(intelligence),
        "conflict_diagnostics_visibility": diagnostics,
        "conflict_explainability_visibility": explainability["explainability"],
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": {
            "serialization_stable": serialization_hashing["serialization_stable"],
            "hashing_stable": serialization_hashing["hashing_stable"],
            "serialization_length": serialization_hashing["serialization_length"],
            "intelligence_hash": serialization_hashing["intelligence_hash"],
        },
        "replay_safe_evidence": replay_rollback,
        "rollback_safe_evidence": replay_rollback,
        "provenance_continuity_evidence": {
            "provenance_metadata": exported["provenance_degradation_metadata"],
            "provenance_continuity_visible": provenance_lineage["provenance_continuity_visible"],
            "hidden_source_inference_used": provenance_lineage["hidden_source_inference_used"],
        },
        "lineage_continuity_evidence": {
            "lineage_metadata": exported["lineage_degradation_metadata"],
            "lineage_continuity_visible": provenance_lineage["lineage_continuity_visible"],
            "ambiguous_lineage_inferred": provenance_lineage["ambiguous_lineage_inferred"],
        },
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "remaining_warnings": [],
        "remaining_blockers": [],
    }
    report["deterministic_report_hash"] = deterministic_boundary_conflict_drift_hash(report)
    return report


def contaminate_conflict_drift_for_non_operational_validation(
    intelligence: BoundaryConflictDriftIntelligence,
) -> BoundaryConflictDriftIntelligence:
    contaminated_drift = replace(
        intelligence.drift_records[0],
        runtime_execution_enabled=True,
        operational_mutation_enabled=True,
    )
    contaminated_diagnostic = replace(
        intelligence.conflict_diagnostics[0],
        conflict_auto_resolution_enabled=True,
        automatic_remediation_enabled=True,
    )
    contaminated_compatibility = replace(
        intelligence.compatibility_evidence[0],
        orchestration_authorization_enabled=True,
    )
    return replace(
        intelligence,
        drift_records=(contaminated_drift,) + intelligence.drift_records[1:],
        conflict_diagnostics=(contaminated_diagnostic,) + intelligence.conflict_diagnostics[1:],
        compatibility_evidence=(contaminated_compatibility,) + intelligence.compatibility_evidence[1:],
        orchestration_approval_enabled=True,
        dispatch_execution_enabled=True,
        routing_execution_enabled=True,
    )
