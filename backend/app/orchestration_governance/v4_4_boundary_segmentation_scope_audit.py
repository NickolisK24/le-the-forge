"""Audit for deterministic v4.4 boundary segmentation scope intelligence."""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_boundary_segmentation_scope_hashing import (
    deterministic_boundary_segmentation_scope_hash,
    hash_boundary_scope_record,
    hash_boundary_segment_record,
    hash_boundary_segmentation_scope_identity,
    hash_boundary_segmentation_scope_intelligence,
    hash_scope_diagnostic,
    hash_scope_lineage_visibility,
    hash_scope_provenance_visibility,
    hash_scoped_boundary_membership,
    hash_segment_continuity_visibility,
    hash_segment_relationship,
    hash_segmentation_diagnostic,
    hash_segmentation_explainability,
    hash_segmentation_scope_evidence_metadata,
)
from .v4_4_boundary_segmentation_scope_models import (
    SEGMENTATION_SCOPE_STATE_AMBIGUOUS,
    SEGMENTATION_SCOPE_STATE_CONFLICTING,
    SEGMENTATION_SCOPE_STATE_COUPLED,
    SEGMENTATION_SCOPE_STATE_DEGRADED,
    SEGMENTATION_SCOPE_STATE_ISOLATED,
    SEGMENTATION_SCOPE_STATE_OVERLAPPING,
    SEGMENTATION_SCOPE_STATE_SCOPED,
    SEGMENTATION_SCOPE_STATE_SEGMENTED,
    SEGMENTATION_SCOPE_STATE_UNSCOPED,
    SEGMENTATION_SCOPE_STATE_UNSEGMENTED,
    V4_4_BOUNDARY_SEGMENTATION_SCOPE_REPORT_SCHEMA_VERSION,
    V4_4_BOUNDARY_SEGMENTATION_SCOPE_STATUS_BLOCKED,
    V4_4_BOUNDARY_SEGMENTATION_SCOPE_STATUS_STABLE,
    BoundarySegmentationScopeIntelligence,
    default_boundary_segmentation_scope_intelligence,
)
from .v4_4_boundary_segmentation_scope_serialization import (
    export_boundary_segmentation_scope_intelligence,
    serialize_boundary_segmentation_scope_intelligence,
)
from .v4_4_boundary_segmentation_scope_visibility import (
    aggregate_scope_diagnostics,
    aggregate_segmentation_diagnostics,
    ambiguous_scope_totals,
    count_combined_segmentation_scope_states,
    count_continuity_states,
    count_membership_states,
    count_relationship_states,
    count_scope_states,
    count_segment_states,
    degraded_scope_visibility,
    fail_visible_segmentation_summaries,
    governance_safe_segmentation_explainability,
    isolation_coupling_visibility,
    overlap_visibility,
    scope_lineage_visibility,
    scope_provenance_visibility,
    scope_summaries,
    scoped_boundary_membership_visibility,
    segmentation_summaries,
    validate_required_segmentation_scope_visibility,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_runtime_behavior_enabled",
        "orchestration_execution_enabled",
        "execution_enabled",
        "boundary_group_execution_lane_enabled",
    ),
    "enabled_orchestration_authorization_count": (
        "orchestration_authorization_enabled",
        "authorization_enabled",
        "scope_based_authorization_enabled",
    ),
    "enabled_orchestration_approval_count": (
        "orchestration_approval_enabled",
        "approval_enabled",
        "readiness_approval_enabled",
    ),
    "enabled_dispatch_execution_count": (
        "dispatch_execution_enabled",
        "dispatch_enabled",
        "orchestration_dispatch_enabled",
    ),
    "enabled_routing_execution_count": (
        "routing_execution_enabled",
        "routing_enabled",
        "segmentation_based_routing_enabled",
        "orchestration_routing_enabled",
    ),
    "enabled_scheduling_execution_count": (
        "scheduling_execution_enabled",
        "scheduling_enabled",
        "orchestration_scheduling_enabled",
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


def build_v4_4_boundary_segmentation_scope() -> BoundarySegmentationScopeIntelligence:
    return default_boundary_segmentation_scope_intelligence()


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


def enabled_segmentation_scope_capability_flags(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "segment_id", None)
            or getattr(item, "scope_id", None)
            or getattr(item, "membership_id", None)
            or getattr(item, "relationship_id", None)
            or getattr(item, "continuity_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "explainability_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "segmentation_scope_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def segmentation_scope_capability_counter_values(
    intelligence: BoundarySegmentationScopeIntelligence,
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


def boundary_segmentation_scope_equal(
    left: BoundarySegmentationScopeIntelligence,
    right: BoundarySegmentationScopeIntelligence,
) -> bool:
    return serialize_boundary_segmentation_scope_intelligence(left) == serialize_boundary_segmentation_scope_intelligence(right)


def validate_segmentation_scope_ordering_stability(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "segmentation_classifications": tuple(
            item.deterministic_order for item in intelligence.segmentation_classifications
        ),
        "scope_classifications": tuple(item.deterministic_order for item in intelligence.scope_classifications),
        "segment_records": tuple(item.deterministic_order for item in intelligence.segment_records),
        "scope_records": tuple(item.deterministic_order for item in intelligence.scope_records),
        "membership_records": tuple(item.deterministic_order for item in intelligence.membership_records),
        "relationship_records": tuple(item.deterministic_order for item in intelligence.relationship_records),
        "continuity_visibility": tuple(item.deterministic_order for item in intelligence.continuity_visibility),
        "scope_diagnostics": tuple(item.deterministic_order for item in intelligence.scope_diagnostics),
        "segmentation_diagnostics": tuple(item.deterministic_order for item in intelligence.segmentation_diagnostics),
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


def validate_segmentation_scope_serialization_and_hashing(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    rebuilt = build_v4_4_boundary_segmentation_scope()
    serialized = serialize_boundary_segmentation_scope_intelligence(intelligence)
    rebuilt_serialized = serialize_boundary_segmentation_scope_intelligence(rebuilt)
    intelligence_hash = hash_boundary_segmentation_scope_intelligence(intelligence)
    rebuilt_hash = hash_boundary_segmentation_scope_intelligence(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and intelligence_hash == rebuilt_hash,
        "segmentation_serialization_stable": serialized == rebuilt_serialized,
        "scope_serialization_stable": serialized == rebuilt_serialized,
        "segmentation_hashing_stable": intelligence_hash == rebuilt_hash,
        "scope_hashing_stable": intelligence_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "intelligence_hash": intelligence_hash,
        "rebuilt_intelligence_hash": rebuilt_hash,
    }


def validate_segmentation_scope_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    required = validate_required_segmentation_scope_visibility(intelligence)
    combined_counts = count_combined_segmentation_scope_states(intelligence)
    membership = scoped_boundary_membership_visibility(intelligence)
    isolation_coupling = isolation_coupling_visibility(intelligence)
    degradation = degraded_scope_visibility(intelligence)
    scope_diagnostics = aggregate_scope_diagnostics(intelligence.scope_diagnostics)
    segmentation_diagnostics = aggregate_segmentation_diagnostics(intelligence.segmentation_diagnostics)
    ambiguity = ambiguous_scope_totals(intelligence)
    return {
        "valid": (
            required["valid"]
            and membership["routing_enabled_count"] == 0
            and membership["dispatch_enabled_count"] == 0
            and membership["scheduling_enabled_count"] == 0
            and isolation_coupling["routing_enabled_count"] == 0
            and isolation_coupling["dispatch_enabled_count"] == 0
            and isolation_coupling["scheduling_enabled_count"] == 0
            and isolation_coupling["runtime_execution_enabled_count"] == 0
            and degradation["mutation_enabled_count"] == 0
            and scope_diagnostics["scope_based_authorization_enabled_count"] == 0
            and scope_diagnostics["automatic_remediation_enabled_count"] == 0
            and scope_diagnostics["automatic_repair_enabled_count"] == 0
            and segmentation_diagnostics["segmentation_based_routing_enabled_count"] == 0
            and segmentation_diagnostics["automatic_remediation_enabled_count"] == 0
            and segmentation_diagnostics["automatic_repair_enabled_count"] == 0
            and ambiguity["ambiguous_count"] > 0
            and ambiguity["conflicting_count"] > 0
            and ambiguity["degraded_count"] > 0
        ),
        "combined_counts": combined_counts,
        "segment_counts": count_segment_states(intelligence.segment_records),
        "scope_counts": count_scope_states(intelligence.scope_records),
        "membership_counts": count_membership_states(intelligence.membership_records),
        "relationship_counts": count_relationship_states(intelligence.relationship_records),
        "continuity_counts": count_continuity_states(intelligence.continuity_visibility),
        "missing_states": required["missing_states"],
        "missing_fail_visible_states": required["missing_fail_visible_states"],
        "membership": membership,
        "isolation_coupling": isolation_coupling,
        "degradation": degradation,
        "scope_diagnostics": scope_diagnostics,
        "segmentation_diagnostics": segmentation_diagnostics,
        "ambiguity": ambiguity,
    }


def validate_segmentation_scope_replay_rollback_evidence(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    evidence = intelligence.evidence_metadata
    expected = (
        set(evidence.segment_record_ids)
        | set(evidence.scope_record_ids)
        | set(evidence.membership_record_ids)
        | set(evidence.relationship_record_ids)
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


def validate_segmentation_scope_provenance_lineage_visibility(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_visibility
    lineage = intelligence.lineage_visibility
    return {
        "valid": (
            provenance.provenance_visible
            and lineage.lineage_visible
            and not provenance.hidden_source_inference_used
            and not lineage.ambiguous_lineage_inferred
        ),
        "provenance_visible": provenance.provenance_visible,
        "lineage_visible": lineage.lineage_visible,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
    }


def validate_segmentation_scope_explainability(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    explainability = governance_safe_segmentation_explainability(intelligence.explainability)
    return {
        "valid": (
            explainability["explainability_first"]
            and explainability["descriptive_only"]
            and explainability["recommendation_enabled_count"] == 0
            and explainability["decision_enabled_count"] == 0
            and explainability["routing_enabled_count"] == 0
        ),
        "explainability": explainability,
    }


def validate_segmentation_scope_non_operational(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    counters = segmentation_scope_capability_counter_values(intelligence)
    enabled_flags = enabled_segmentation_scope_capability_flags(intelligence)
    root_disabled = {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_authoritative": intelligence.non_authoritative,
        "non_routing": intelligence.non_routing,
        "non_dispatching": intelligence.non_dispatching,
        "non_scheduling": intelligence.non_scheduling,
        "non_remediating": intelligence.non_remediating,
        "non_mutating": intelligence.non_mutating,
        "planner_integration_disabled": not intelligence.planner_integration_enabled,
        "production_consumption_disabled": not intelligence.production_consumption_enabled,
        "runtime_mutation_disabled": not intelligence.runtime_mutation_enabled,
        "operational_mutation_disabled": not intelligence.operational_mutation_enabled,
        "segmentation_based_routing_disabled": not intelligence.segmentation_based_routing_enabled,
        "scope_based_authorization_disabled": not intelligence.scope_based_authorization_enabled,
        "boundary_group_execution_lane_disabled": not intelligence.boundary_group_execution_lane_enabled,
        "automatic_remediation_disabled": not intelligence.automatic_remediation_enabled,
        "automatic_repair_disabled": not intelligence.automatic_repair_enabled,
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_boundary_segmentation_scope(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_segmentation_scope_ordering_stability(intelligence),
        "serialization_hashing": validate_segmentation_scope_serialization_and_hashing(intelligence),
        "visibility": validate_segmentation_scope_visibility(intelligence),
        "replay_rollback": validate_segmentation_scope_replay_rollback_evidence(intelligence),
        "provenance_lineage": validate_segmentation_scope_provenance_lineage_visibility(intelligence),
        "explainability": validate_segmentation_scope_explainability(intelligence),
        "non_operational": validate_segmentation_scope_non_operational(intelligence),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_4_boundary_segmentation_scope_report() -> dict[str, Any]:
    intelligence = build_v4_4_boundary_segmentation_scope()
    exported = export_boundary_segmentation_scope_intelligence(intelligence)
    validation = validate_boundary_segmentation_scope(intelligence)
    visibility = validation["validations"]["visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    replay_rollback = validation["validations"]["replay_rollback"]
    provenance_lineage = validation["validations"]["provenance_lineage"]
    explainability = validation["validations"]["explainability"]
    non_operational = validation["validations"]["non_operational"]
    combined_counts = visibility["combined_counts"]
    isolation_coupling = visibility["isolation_coupling"]
    degradation = visibility["degradation"]
    ambiguity = visibility["ambiguity"]
    deterministic_hash_evidence = {
        "identity_hash": hash_boundary_segmentation_scope_identity(intelligence.identity),
        "intelligence_hash": hash_boundary_segmentation_scope_intelligence(intelligence),
        "provenance_hash": hash_scope_provenance_visibility(intelligence.provenance_visibility),
        "lineage_hash": hash_scope_lineage_visibility(intelligence.lineage_visibility),
        "evidence_metadata_hash": hash_segmentation_scope_evidence_metadata(
            intelligence.evidence_metadata
        ),
        "segment_record_hashes": {
            record.segment_id: hash_boundary_segment_record(record)
            for record in sorted(intelligence.segment_records, key=lambda item: item.deterministic_order)
        },
        "scope_record_hashes": {
            record.scope_id: hash_boundary_scope_record(record)
            for record in sorted(intelligence.scope_records, key=lambda item: item.deterministic_order)
        },
        "membership_record_hashes": {
            record.membership_id: hash_scoped_boundary_membership(record)
            for record in sorted(intelligence.membership_records, key=lambda item: item.deterministic_order)
        },
        "relationship_record_hashes": {
            record.relationship_id: hash_segment_relationship(record)
            for record in sorted(intelligence.relationship_records, key=lambda item: item.deterministic_order)
        },
        "continuity_hashes": {
            record.continuity_id: hash_segment_continuity_visibility(record)
            for record in sorted(intelligence.continuity_visibility, key=lambda item: item.deterministic_order)
        },
        "scope_diagnostic_hashes": {
            record.diagnostic_id: hash_scope_diagnostic(record)
            for record in sorted(intelligence.scope_diagnostics, key=lambda item: item.deterministic_order)
        },
        "segmentation_diagnostic_hashes": {
            record.diagnostic_id: hash_segmentation_diagnostic(record)
            for record in sorted(intelligence.segmentation_diagnostics, key=lambda item: item.deterministic_order)
        },
        "explainability_hashes": {
            record.explainability_id: hash_segmentation_explainability(record)
            for record in sorted(intelligence.explainability, key=lambda item: item.deterministic_order)
        },
    }
    summary = {
        "segment_record_count": len(intelligence.segment_records),
        "scope_record_count": len(intelligence.scope_records),
        "membership_record_count": len(intelligence.membership_records),
        "segment_relationship_count": len(intelligence.relationship_records),
        "scope_diagnostic_count": len(intelligence.scope_diagnostics),
        "segmentation_diagnostic_count": len(intelligence.segmentation_diagnostics),
        "scoped_count": combined_counts[SEGMENTATION_SCOPE_STATE_SCOPED],
        "unscoped_count": combined_counts[SEGMENTATION_SCOPE_STATE_UNSCOPED],
        "segmented_count": combined_counts[SEGMENTATION_SCOPE_STATE_SEGMENTED],
        "unsegmented_count": combined_counts[SEGMENTATION_SCOPE_STATE_UNSEGMENTED],
        "isolated_count": combined_counts[SEGMENTATION_SCOPE_STATE_ISOLATED],
        "coupled_count": combined_counts[SEGMENTATION_SCOPE_STATE_COUPLED],
        "overlap_count": combined_counts[SEGMENTATION_SCOPE_STATE_OVERLAPPING],
        "ambiguity_count": ambiguity["ambiguous_count"],
        "conflict_count": ambiguity["conflicting_count"],
        "degraded_count": ambiguity["degraded_count"],
        "continuity_degraded_count": degradation["degraded_count"],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "segmentation_serialization_verified": serialization_hashing["segmentation_serialization_stable"],
        "scope_serialization_verified": serialization_hashing["scope_serialization_stable"],
        "segmentation_hashing_verified": serialization_hashing["segmentation_hashing_stable"],
        "scope_hashing_verified": serialization_hashing["scope_hashing_stable"],
        "replay_safe_evidence_verified": replay_rollback["replay_safe"],
        "rollback_safe_evidence_verified": replay_rollback["rollback_safe"],
        "segment_membership_visibility_verified": visibility["membership"]["descriptive_only"],
        "scope_ambiguity_visibility_verified": ambiguity["ambiguous_count"] > 0,
        "overlap_visibility_verified": isolation_coupling["overlap_count"] > 0,
        "isolation_coupling_visibility_verified": (
            isolation_coupling["isolated_count"] > 0 and isolation_coupling["coupled_count"] > 0
        ),
        "provenance_visibility_verified": provenance_lineage["provenance_visible"],
        "lineage_visibility_verified": provenance_lineage["lineage_visible"],
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
        "report_schema_version": V4_4_BOUNDARY_SEGMENTATION_SCOPE_REPORT_SCHEMA_VERSION,
        "phase_id": intelligence.identity.phase_id,
        "foundation_status": (
            V4_4_BOUNDARY_SEGMENTATION_SCOPE_STATUS_STABLE
            if validation["valid"]
            else V4_4_BOUNDARY_SEGMENTATION_SCOPE_STATUS_BLOCKED
        ),
        "summary": summary,
        "boundary_segmentation_scope_intelligence": exported,
        "segmentation_visibility": segmentation_summaries(intelligence),
        "scope_visibility": scope_summaries(intelligence),
        "scoped_boundary_membership_visibility": visibility["membership"],
        "isolation_coupling_visibility": isolation_coupling,
        "overlap_visibility": overlap_visibility(intelligence),
        "degraded_scope_visibility": degradation,
        "fail_visible_segmentation_visibility": fail_visible_segmentation_summaries(intelligence),
        "scope_provenance_visibility": scope_provenance_visibility(intelligence),
        "scope_lineage_visibility": scope_lineage_visibility(intelligence),
        "scope_diagnostics_visibility": visibility["scope_diagnostics"],
        "segmentation_diagnostics_visibility": visibility["segmentation_diagnostics"],
        "segmentation_explainability_visibility": explainability["explainability"],
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": {
            "segmentation_serialization_stable": serialization_hashing["segmentation_serialization_stable"],
            "scope_serialization_stable": serialization_hashing["scope_serialization_stable"],
            "segmentation_hashing_stable": serialization_hashing["segmentation_hashing_stable"],
            "scope_hashing_stable": serialization_hashing["scope_hashing_stable"],
            "serialization_length": serialization_hashing["serialization_length"],
            "intelligence_hash": serialization_hashing["intelligence_hash"],
        },
        "replay_safe_evidence": replay_rollback,
        "rollback_safe_evidence": replay_rollback,
        "provenance_visibility_evidence": {
            "provenance_visibility": exported["provenance_visibility"],
            "provenance_visible": provenance_lineage["provenance_visible"],
            "hidden_source_inference_used": provenance_lineage["hidden_source_inference_used"],
        },
        "lineage_visibility_evidence": {
            "lineage_visibility": exported["lineage_visibility"],
            "lineage_visible": provenance_lineage["lineage_visible"],
            "ambiguous_lineage_inferred": provenance_lineage["ambiguous_lineage_inferred"],
        },
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "remaining_warnings": [],
        "remaining_blockers": [],
    }
    report["deterministic_report_hash"] = deterministic_boundary_segmentation_scope_hash(report)
    return report


def contaminate_segmentation_scope_for_non_operational_validation(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> BoundarySegmentationScopeIntelligence:
    contaminated_segment = replace(
        intelligence.segment_records[0],
        segmentation_based_routing_enabled=True,
        boundary_group_execution_lane_enabled=True,
        operational_mutation_enabled=True,
    )
    contaminated_scope = replace(
        intelligence.scope_records[0],
        scope_based_authorization_enabled=True,
        orchestration_approval_enabled=True,
    )
    contaminated_membership = replace(
        intelligence.membership_records[0],
        routing_enabled=True,
        dispatch_enabled=True,
        scheduling_enabled=True,
    )
    return replace(
        intelligence,
        segment_records=(contaminated_segment,) + intelligence.segment_records[1:],
        scope_records=(contaminated_scope,) + intelligence.scope_records[1:],
        membership_records=(contaminated_membership,) + intelligence.membership_records[1:],
        routing_execution_enabled=True,
        dispatch_execution_enabled=True,
        scheduling_execution_enabled=True,
    )
