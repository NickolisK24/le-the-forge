"""Audit for deterministic v4.5A.5 cross-boundary drift continuity.

The audit validates descriptive cross-boundary drift continuity intelligence
only. It does not execute, authorize, approve, dispatch, route, traverse,
schedule, sequence, decide, recommend, restore continuity, remediate, repair,
mitigate, correct, integrate planners, consume production paths, or mutate
runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_5a_5_cross_boundary_drift_continuity_hashing import (
    deterministic_v4_5a_5_cross_boundary_drift_continuity_hash,
    hash_boundary_pair_continuity_record,
    hash_cross_boundary_continuity_diagnostic,
    hash_cross_boundary_continuity_identity,
    hash_cross_boundary_continuity_record,
    hash_cross_boundary_evidence_continuity,
    hash_degradation_continuity_preservation,
    hash_drift_continuity_preservation,
    hash_explanation_continuity_preservation,
    hash_propagation_continuity_preservation,
    hash_unsupported_cross_boundary_visibility,
    hash_v4_5a_5_cross_boundary_drift_continuity,
)
from .v4_5a_5_cross_boundary_drift_continuity_models import (
    BOUNDARY_CONTINUITY_TYPES,
    CROSS_BOUNDARY_DIAGNOSTIC_TYPES,
    CROSS_BOUNDARY_EVIDENCE_CONTINUITY_TYPES,
    DEGRADATION_CONTINUITY_PRESERVATION_TYPES,
    DRIFT_CONTINUITY_PRESERVATION_TYPES,
    EXPLANATION_CONTINUITY_PRESERVATION_TYPES,
    PROPAGATION_CONTINUITY_PRESERVATION_TYPES,
    UNSUPPORTED_CROSS_BOUNDARY_OPERATIONAL_STATES,
    V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_HASH_REFERENCE,
    V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_REFERENCE,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_DISABLED_COUNTER_NAMES,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_GENERATED_AT,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_PHASE_ID,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_PURPOSE,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_STATUS_BLOCKED,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_STATUS_STABLE,
    CrossBoundaryDriftContinuityIntelligence,
    default_v4_5a_5_cross_boundary_drift_continuity,
)
from .v4_5a_5_cross_boundary_drift_continuity_serialization import (
    export_v4_5a_5_cross_boundary_drift_continuity,
    serialize_v4_5a_5_cross_boundary_drift_continuity,
)
from .v4_5a_5_cross_boundary_drift_continuity_visibility import (
    boundary_pair_summary_visibility,
    cross_boundary_continuity_summary_visibility,
    degradation_continuity_summary_visibility,
    descriptive_only_cross_boundary_continuity_summary,
    drift_continuity_summary_visibility,
    evidence_continuity_summary_visibility,
    explanation_continuity_summary_visibility,
    fail_visible_cross_boundary_diagnostic_summaries,
    propagation_continuity_summary_visibility,
    unsupported_cross_boundary_visibility_summaries,
    validate_required_cross_boundary_continuity_visibility,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "planner_execution_enabled",
        "execution_enabled",
        "operational_behavior_enabled",
    ),
    "enabled_orchestration_authorization_count": (
        "orchestration_authorization_enabled",
        "authorization_behavior_enabled",
        "authorization_enabled",
    ),
    "enabled_orchestration_approval_count": (
        "orchestration_approval_enabled",
        "approval_enabled",
    ),
    "enabled_orchestration_dispatch_count": (
        "orchestration_dispatch_enabled",
        "dispatch_enabled",
    ),
    "enabled_orchestration_routing_count": (
        "orchestration_routing_enabled",
        "routing_enabled",
    ),
    "enabled_orchestration_traversal_count": (
        "orchestration_traversal_enabled",
        "traversal_enabled",
    ),
    "enabled_orchestration_scheduling_count": (
        "orchestration_scheduling_enabled",
        "scheduling_enabled",
    ),
    "enabled_orchestration_sequencing_count": (
        "orchestration_sequencing_enabled",
        "sequencing_enabled",
    ),
    "enabled_orchestration_decision_count": (
        "orchestration_decision_enabled",
        "decision_enabled",
    ),
    "enabled_orchestration_recommendation_count": (
        "orchestration_recommendation_enabled",
        "recommendation_enabled",
    ),
    "enabled_boundary_traversal_count": (
        "boundary_traversal_enabled",
        "boundary_traversal_behavior_enabled",
    ),
    "enabled_continuity_restoration_count": (
        "continuity_restoration_enabled",
        "restoration_enabled",
    ),
    "enabled_remediation_count": (
        "remediation_enabled",
        "auto_remediation_enabled",
    ),
    "enabled_repair_count": ("repair_enabled",),
    "enabled_mitigation_count": ("mitigation_enabled",),
    "enabled_auto_correction_count": (
        "auto_correction_enabled",
        "automated_correction_enabled",
        "correction_enabled",
    ),
    "enabled_runtime_mutation_count": (
        "runtime_mutation_enabled",
        "mutation_enabled",
    ),
    "enabled_operational_mutation_count": ("operational_mutation_enabled",),
    "enabled_planner_integration_count": ("planner_integration_enabled",),
    "enabled_production_consumption_count": ("production_consumption_enabled",),
}

PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_5a_5_cross_boundary_drift_continuity() -> (
    CrossBoundaryDriftContinuityIntelligence
):
    return default_v4_5a_5_cross_boundary_drift_continuity()


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


def enabled_cross_boundary_continuity_capability_flags(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "cross_boundary_continuity_id", None)
            or getattr(item, "boundary_pair_record_id", None)
            or getattr(item, "drift_continuity_id", None)
            or getattr(item, "propagation_continuity_id", None)
            or getattr(item, "degradation_continuity_id", None)
            or getattr(item, "explanation_continuity_id", None)
            or getattr(item, "evidence_continuity_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(
                item,
                "cross_boundary_drift_continuity_id",
                item.__class__.__name__,
            )
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def cross_boundary_continuity_capability_counter_values(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
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


def cross_boundary_drift_continuity_equal(
    left: CrossBoundaryDriftContinuityIntelligence,
    right: CrossBoundaryDriftContinuityIntelligence,
) -> bool:
    return serialize_v4_5a_5_cross_boundary_drift_continuity(
        left
    ) == serialize_v4_5a_5_cross_boundary_drift_continuity(right)


def validate_cross_boundary_ordering_stability(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "cross_boundary_continuity": tuple(
            record.deterministic_order
            for record in intelligence.cross_boundary_continuity
        ),
        "boundary_pair_continuity": tuple(
            record.deterministic_order
            for record in intelligence.boundary_pair_continuity
        ),
        "drift_continuity": tuple(
            record.deterministic_order for record in intelligence.drift_continuity
        ),
        "propagation_continuity": tuple(
            record.deterministic_order
            for record in intelligence.propagation_continuity
        ),
        "degradation_continuity": tuple(
            record.deterministic_order
            for record in intelligence.degradation_continuity
        ),
        "explanation_continuity": tuple(
            record.deterministic_order
            for record in intelligence.explanation_continuity
        ),
        "evidence_continuity": tuple(
            record.deterministic_order for record in intelligence.evidence_continuity
        ),
        "diagnostics": tuple(
            record.deterministic_order for record in intelligence.diagnostics
        ),
        "unsupported_cross_boundary_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_cross_boundary_visibility
        ),
    }
    unordered_groups = [
        name for name, orders in order_groups.items() if tuple(sorted(orders)) != orders
    ]
    duplicate_groups = [
        name for name, orders in order_groups.items() if len(set(orders)) != len(orders)
    ]
    return {
        "valid": not (unordered_groups or duplicate_groups),
        "order_groups": order_groups,
        "unordered_groups": unordered_groups,
        "duplicate_groups": duplicate_groups,
    }


def validate_cross_boundary_continuity_identity_integrity(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    identity = intelligence.continuity_identity
    continuity_ids = [
        record.cross_boundary_continuity_id
        for record in intelligence.cross_boundary_continuity
    ]
    boundary_pair_ids = [
        record.boundary_pair_id for record in intelligence.cross_boundary_continuity
    ]
    empty_identity_fields = [
        field_name
        for field_name in (
            "cross_boundary_drift_continuity_id",
            "phase_id",
            "schema_version",
            "generated_at",
            "classification",
            "source_explainability_report_reference",
            "source_explainability_hash_reference",
        )
        if not getattr(identity, field_name)
    ]
    same_boundary_pairs = sorted(
        record.cross_boundary_continuity_id
        for record in intelligence.cross_boundary_continuity
        if record.source_boundary_id == record.target_boundary_id
    )
    return {
        "valid": not (
            empty_identity_fields
            or len(set(continuity_ids)) != len(continuity_ids)
            or len(set(boundary_pair_ids)) != len(boundary_pair_ids)
            or same_boundary_pairs
            or identity.source_explainability_report_reference
            != V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_REFERENCE
            or identity.source_explainability_hash_reference
            != V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_HASH_REFERENCE
        ),
        "cross_boundary_continuity_count": len(intelligence.cross_boundary_continuity),
        "unique_cross_boundary_continuity_count": len(set(continuity_ids)),
        "unique_boundary_pair_count": len(set(boundary_pair_ids)),
        "empty_identity_fields": empty_identity_fields,
        "same_boundary_pairs": same_boundary_pairs,
        "source_report_reference": identity.source_explainability_report_reference,
        "source_hash_reference": identity.source_explainability_hash_reference,
    }


def validate_boundary_to_boundary_continuity_preservation(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    visibility = validate_required_cross_boundary_continuity_visibility(intelligence)
    pair_by_id = {
        record.boundary_pair_id: record
        for record in intelligence.boundary_pair_continuity
    }
    missing_pair_records = sorted(
        record.boundary_pair_id
        for record in intelligence.cross_boundary_continuity
        if record.boundary_pair_id not in pair_by_id
    )
    unsafe_boundary_ids = sorted(
        record.cross_boundary_continuity_id
        for record in intelligence.cross_boundary_continuity
        if (
            record.routing_enabled
            or record.traversal_enabled
            or record.boundary_traversal_enabled
            or record.continuity_restoration_enabled
        )
    )
    unsafe_pair_ids = sorted(
        record.boundary_pair_record_id
        for record in intelligence.boundary_pair_continuity
        if (
            record.routing_enabled
            or record.traversal_enabled
            or record.boundary_traversal_enabled
            or not record.no_routing_behavior
            or not record.no_traversal_behavior
        )
    )
    return {
        "valid": not (
            visibility["missing_boundary_types"]
            or visibility["missing_boundary_pair_types"]
            or missing_pair_records
            or unsafe_boundary_ids
            or unsafe_pair_ids
        ),
        "boundary_continuity_count": len(intelligence.cross_boundary_continuity),
        "boundary_pair_count": len(intelligence.boundary_pair_continuity),
        "missing_boundary_types": visibility["missing_boundary_types"],
        "missing_boundary_pair_types": visibility["missing_boundary_pair_types"],
        "missing_pair_records": missing_pair_records,
        "unsafe_boundary_ids": unsafe_boundary_ids,
        "unsafe_pair_ids": unsafe_pair_ids,
        "routing_enabled_count": sum(
            1 for record in intelligence.cross_boundary_continuity if record.routing_enabled
        ),
        "traversal_enabled_count": sum(
            1 for record in intelligence.cross_boundary_continuity if record.traversal_enabled
        ),
        "continuity_restoration_enabled_count": sum(
            1
            for record in intelligence.cross_boundary_continuity
            if record.continuity_restoration_enabled
        ),
    }


def _validate_record_continuity(
    records: Iterable[Any],
    type_attribute: str,
    required_types: tuple[str, ...],
    id_attribute: str,
) -> dict[str, Any]:
    records_tuple = tuple(records)
    present = {str(getattr(record, type_attribute)) for record in records_tuple}
    missing_types = sorted(set(required_types) - present)
    records_missing_evidence = sorted(
        str(getattr(record, id_attribute))
        for record in records_tuple
        if not tuple(getattr(record, "evidence_reference_ids", ()))
    )
    records_missing_continuity = sorted(
        str(getattr(record, id_attribute))
        for record in records_tuple
        if not getattr(record, "continuity_reference_id", "")
    )
    unsafe_record_ids = sorted(
        str(getattr(record, id_attribute))
        for record in records_tuple
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES
        if bool(getattr(record, field_name, False))
    )
    return {
        "valid": not (
            missing_types
            or records_missing_evidence
            or records_missing_continuity
            or unsafe_record_ids
        ),
        "record_count": len(records_tuple),
        "missing_types": missing_types,
        "records_missing_evidence": records_missing_evidence,
        "records_missing_continuity": records_missing_continuity,
        "unsafe_record_ids": sorted(set(unsafe_record_ids)),
    }


def validate_drift_continuity_preservation(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    return _validate_record_continuity(
        intelligence.drift_continuity,
        "drift_continuity_type",
        DRIFT_CONTINUITY_PRESERVATION_TYPES,
        "drift_continuity_id",
    )


def validate_propagation_continuity_preservation(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    return _validate_record_continuity(
        intelligence.propagation_continuity,
        "propagation_continuity_type",
        PROPAGATION_CONTINUITY_PRESERVATION_TYPES,
        "propagation_continuity_id",
    )


def validate_degradation_continuity_preservation(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    return _validate_record_continuity(
        intelligence.degradation_continuity,
        "degradation_continuity_type",
        DEGRADATION_CONTINUITY_PRESERVATION_TYPES,
        "degradation_continuity_id",
    )


def validate_explanation_continuity_preservation(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    return _validate_record_continuity(
        intelligence.explanation_continuity,
        "explanation_continuity_type",
        EXPLANATION_CONTINUITY_PRESERVATION_TYPES,
        "explanation_continuity_id",
    )


def validate_cross_boundary_evidence_continuity(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    evidence = intelligence.evidence_continuity
    present = {record.evidence_type for record in evidence}
    missing_types = sorted(set(CROSS_BOUNDARY_EVIDENCE_CONTINUITY_TYPES) - present)
    unsafe_evidence_ids = sorted(
        record.evidence_continuity_id
        for record in evidence
        if (
            not record.replay_safe
            or not record.rollback_safe
            or not record.provenance_safe
            or not record.lineage_safe
            or not record.integrity_safe
            or record.hidden_assumption_used
            or record.production_consumption_enabled
            or record.runtime_mutation_enabled
            or record.source_hash_reference
            != V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_HASH_REFERENCE
        )
    )
    return {
        "valid": not (missing_types or unsafe_evidence_ids),
        "evidence_count": len(evidence),
        "missing_evidence_types": missing_types,
        "unsafe_evidence_ids": unsafe_evidence_ids,
        "replay_safe_evidence_count": sum(1 for record in evidence if record.replay_safe),
        "rollback_safe_evidence_count": sum(
            1 for record in evidence if record.rollback_safe
        ),
        "provenance_safe_evidence_count": sum(
            1 for record in evidence if record.provenance_safe
        ),
        "lineage_safe_evidence_count": sum(1 for record in evidence if record.lineage_safe),
        "integrity_safe_evidence_count": sum(
            1 for record in evidence if record.integrity_safe
        ),
        "production_consumption_enabled_count": sum(
            1 for record in evidence if record.production_consumption_enabled
        ),
        "runtime_mutation_enabled_count": sum(
            1 for record in evidence if record.runtime_mutation_enabled
        ),
    }


def validate_lineage_and_provenance_preservation(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    continuity_missing_lineage = sorted(
        record.cross_boundary_continuity_id
        for record in intelligence.cross_boundary_continuity
        if not record.lineage_reference_id
    )
    continuity_missing_provenance = sorted(
        record.cross_boundary_continuity_id
        for record in intelligence.cross_boundary_continuity
        if not record.provenance_reference_id
    )
    evidence_missing_lineage = sorted(
        record.evidence_continuity_id
        for record in intelligence.evidence_continuity
        if not record.lineage_reference_id
    )
    evidence_missing_provenance = sorted(
        record.evidence_continuity_id
        for record in intelligence.evidence_continuity
        if not record.provenance_reference_id
    )
    return {
        "valid": not (
            continuity_missing_lineage
            or continuity_missing_provenance
            or evidence_missing_lineage
            or evidence_missing_provenance
        ),
        "lineage_continuity_preserved": not (
            continuity_missing_lineage or evidence_missing_lineage
        ),
        "provenance_continuity_preserved": not (
            continuity_missing_provenance or evidence_missing_provenance
        ),
        "continuity_missing_lineage": continuity_missing_lineage,
        "continuity_missing_provenance": continuity_missing_provenance,
        "evidence_missing_lineage": evidence_missing_lineage,
        "evidence_missing_provenance": evidence_missing_provenance,
    }


def validate_cross_boundary_serialization_and_hashing(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    second = build_v4_5a_5_cross_boundary_drift_continuity()
    serialization_one = serialize_v4_5a_5_cross_boundary_drift_continuity(intelligence)
    serialization_two = serialize_v4_5a_5_cross_boundary_drift_continuity(second)
    hash_one = hash_v4_5a_5_cross_boundary_drift_continuity(intelligence)
    hash_two = hash_v4_5a_5_cross_boundary_drift_continuity(second)
    hash_lengths_valid = all(
        len(value) == 64
        for value in (
            hash_cross_boundary_continuity_identity(intelligence.continuity_identity),
            hash_cross_boundary_continuity_record(
                intelligence.cross_boundary_continuity[0]
            ),
            hash_boundary_pair_continuity_record(
                intelligence.boundary_pair_continuity[0]
            ),
            hash_drift_continuity_preservation(intelligence.drift_continuity[0]),
            hash_propagation_continuity_preservation(
                intelligence.propagation_continuity[0]
            ),
            hash_degradation_continuity_preservation(
                intelligence.degradation_continuity[0]
            ),
            hash_explanation_continuity_preservation(
                intelligence.explanation_continuity[0]
            ),
            hash_cross_boundary_evidence_continuity(
                intelligence.evidence_continuity[0]
            ),
            hash_cross_boundary_continuity_diagnostic(intelligence.diagnostics[0]),
            hash_unsupported_cross_boundary_visibility(
                intelligence.unsupported_cross_boundary_visibility[0]
            ),
            hash_one,
            hash_two,
        )
    )
    return {
        "valid": (
            serialization_one == serialization_two
            and hash_one == hash_two
            and hash_lengths_valid
        ),
        "serialization_stable": serialization_one == serialization_two,
        "hashing_stable": hash_one == hash_two,
        "hash_lengths_valid": hash_lengths_valid,
        "serialization_length": len(serialization_one),
        "cross_boundary_drift_continuity_hash": hash_one,
    }


def validate_fail_visible_unsupported_cross_boundary_visibility(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    diagnostic_types = {record.diagnostic_type for record in intelligence.diagnostics}
    unsupported_states = {
        record.unsupported_state
        for record in intelligence.unsupported_cross_boundary_visibility
    }
    missing_diagnostic_types = sorted(set(CROSS_BOUNDARY_DIAGNOSTIC_TYPES) - diagnostic_types)
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_CROSS_BOUNDARY_OPERATIONAL_STATES) - unsupported_states
    )
    unsafe_diagnostic_ids = sorted(
        record.diagnostic_id
        for record in intelligence.diagnostics
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.hidden_assumption_used
            or record.silent_fallback_enabled
            or record.routing_enabled
            or record.traversal_enabled
            or record.boundary_traversal_enabled
            or record.continuity_restoration_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.mitigation_enabled
            or record.auto_correction_enabled
            or record.orchestration_response_enabled
        )
    )
    unsafe_unsupported_state_ids = sorted(
        record.state_id
        for record in intelligence.unsupported_cross_boundary_visibility
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.operational_enabled
            or record.authorization_enabled
            or record.routing_enabled
            or record.traversal_enabled
            or record.boundary_traversal_enabled
            or record.continuity_restoration_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.mitigation_enabled
            or record.automated_correction_enabled
        )
    )
    return {
        "valid": not (
            missing_diagnostic_types
            or missing_unsupported_states
            or unsafe_diagnostic_ids
            or unsafe_unsupported_state_ids
        ),
        "diagnostic_count": len(intelligence.diagnostics),
        "unsupported_state_count": len(intelligence.unsupported_cross_boundary_visibility),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_state_ids": unsafe_unsupported_state_ids,
        "fail_visible": all(record.fail_visible for record in intelligence.diagnostics)
        and all(
            record.fail_visible
            for record in intelligence.unsupported_cross_boundary_visibility
        ),
        "silent_fallback_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.silent_fallback_enabled
        ),
        "routing_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.routing_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_cross_boundary_visibility
            if record.routing_enabled
        ),
        "traversal_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.traversal_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_cross_boundary_visibility
            if record.traversal_enabled
        ),
        "continuity_restoration_enabled_count": sum(
            1
            for record in intelligence.diagnostics
            if record.continuity_restoration_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_cross_boundary_visibility
            if record.continuity_restoration_enabled
        ),
        "remediation_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.remediation_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_cross_boundary_visibility
            if record.remediation_enabled
        ),
    }


def validate_descriptive_only_cross_boundary_guarantees(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    counters = cross_boundary_continuity_capability_counter_values(intelligence)
    enabled_flags = enabled_cross_boundary_continuity_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "cross_boundary_continuity_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(
                item,
                "cross_boundary_drift_continuity_id",
                item.__class__.__name__,
            )
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_DISABLED_COUNTER_NAMES)
        - set(counters)
    )
    required_repository_states = {
        "NON-operational": intelligence.non_operational,
        "NON-authorizing": intelligence.non_authorizing,
        "NON-executing": intelligence.non_executing,
        "NON-remediating": intelligence.non_remediating,
        "NON-runtime-mutating": intelligence.non_runtime_mutating,
    }
    missing_repository_states = sorted(
        state for state, preserved in required_repository_states.items() if not preserved
    )
    return {
        "valid": not (
            any(counters.values())
            or enabled_flags
            or descriptive_failures
            or missing_disabled_counters
            or missing_repository_states
        ),
        "counters": counters,
        "enabled_flags": enabled_flags,
        "descriptive_failures": descriptive_failures,
        "missing_disabled_counters": missing_disabled_counters,
        "required_repository_states": required_repository_states,
        "missing_repository_states": missing_repository_states,
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "explicit_limitation_count": len(intelligence.explicit_limitations),
    }


def validate_v4_5a_5_cross_boundary_drift_continuity(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_cross_boundary_ordering_stability(intelligence),
        "identity_integrity": validate_cross_boundary_continuity_identity_integrity(
            intelligence
        ),
        "boundary_to_boundary_continuity": validate_boundary_to_boundary_continuity_preservation(
            intelligence
        ),
        "drift_continuity": validate_drift_continuity_preservation(intelligence),
        "propagation_continuity": validate_propagation_continuity_preservation(
            intelligence
        ),
        "degradation_continuity": validate_degradation_continuity_preservation(
            intelligence
        ),
        "explanation_continuity": validate_explanation_continuity_preservation(
            intelligence
        ),
        "evidence_continuity": validate_cross_boundary_evidence_continuity(
            intelligence
        ),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_hashing": validate_cross_boundary_serialization_and_hashing(
            intelligence
        ),
        "required_visibility": validate_required_cross_boundary_continuity_visibility(
            intelligence
        ),
        "fail_visible_unsupported_cross_boundary": validate_fail_visible_unsupported_cross_boundary_visibility(
            intelligence
        ),
        "descriptive_only_guarantees": validate_descriptive_only_cross_boundary_guarantees(
            intelligence
        ),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_5a_5_cross_boundary_drift_continuity_report() -> dict[str, Any]:
    intelligence = build_v4_5a_5_cross_boundary_drift_continuity()
    exported = export_v4_5a_5_cross_boundary_drift_continuity(intelligence)
    validation = validate_v4_5a_5_cross_boundary_drift_continuity(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    boundary_continuity = validation["validations"]["boundary_to_boundary_continuity"]
    drift_continuity = validation["validations"]["drift_continuity"]
    propagation_continuity = validation["validations"]["propagation_continuity"]
    degradation_continuity = validation["validations"]["degradation_continuity"]
    explanation_continuity = validation["validations"]["explanation_continuity"]
    evidence_continuity = validation["validations"]["evidence_continuity"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_unsupported_cross_boundary"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "continuity_identity_hash": hash_cross_boundary_continuity_identity(
            intelligence.continuity_identity
        ),
        "cross_boundary_drift_continuity_hash": hash_v4_5a_5_cross_boundary_drift_continuity(
            intelligence
        ),
        "cross_boundary_continuity_hashes": {
            record.cross_boundary_continuity_id: hash_cross_boundary_continuity_record(
                record
            )
            for record in sorted(
                intelligence.cross_boundary_continuity,
                key=lambda item: (item.deterministic_order, item.cross_boundary_continuity_id),
            )
        },
        "boundary_pair_hashes": {
            record.boundary_pair_record_id: hash_boundary_pair_continuity_record(record)
            for record in sorted(
                intelligence.boundary_pair_continuity,
                key=lambda item: (item.deterministic_order, item.boundary_pair_record_id),
            )
        },
        "drift_continuity_hashes": {
            record.drift_continuity_id: hash_drift_continuity_preservation(record)
            for record in sorted(
                intelligence.drift_continuity,
                key=lambda item: (item.deterministic_order, item.drift_continuity_id),
            )
        },
        "propagation_continuity_hashes": {
            record.propagation_continuity_id: hash_propagation_continuity_preservation(
                record
            )
            for record in sorted(
                intelligence.propagation_continuity,
                key=lambda item: (item.deterministic_order, item.propagation_continuity_id),
            )
        },
        "degradation_continuity_hashes": {
            record.degradation_continuity_id: hash_degradation_continuity_preservation(
                record
            )
            for record in sorted(
                intelligence.degradation_continuity,
                key=lambda item: (item.deterministic_order, item.degradation_continuity_id),
            )
        },
        "explanation_continuity_hashes": {
            record.explanation_continuity_id: hash_explanation_continuity_preservation(
                record
            )
            for record in sorted(
                intelligence.explanation_continuity,
                key=lambda item: (item.deterministic_order, item.explanation_continuity_id),
            )
        },
        "evidence_continuity_hashes": {
            record.evidence_continuity_id: hash_cross_boundary_evidence_continuity(
                record
            )
            for record in sorted(
                intelligence.evidence_continuity,
                key=lambda item: (item.deterministic_order, item.evidence_continuity_id),
            )
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_cross_boundary_continuity_diagnostic(record)
            for record in sorted(
                intelligence.diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_state_hashes": {
            record.state_id: hash_unsupported_cross_boundary_visibility(record)
            for record in sorted(
                intelligence.unsupported_cross_boundary_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "cross_boundary_continuity_count": len(intelligence.cross_boundary_continuity),
        "boundary_pair_continuity_count": len(intelligence.boundary_pair_continuity),
        "drift_continuity_count": len(intelligence.drift_continuity),
        "propagation_continuity_count": len(intelligence.propagation_continuity),
        "degradation_continuity_count": len(intelligence.degradation_continuity),
        "explanation_continuity_count": len(intelligence.explanation_continuity),
        "evidence_continuity_count": len(intelligence.evidence_continuity),
        "cross_boundary_diagnostic_count": len(intelligence.diagnostics),
        "unsupported_cross_boundary_state_count": len(
            intelligence.unsupported_cross_boundary_visibility
        ),
        "boundary_type_counts": required_visibility["boundary_counts"],
        "boundary_pair_type_counts": required_visibility["boundary_pair_counts"],
        "drift_type_counts": required_visibility["drift_counts"],
        "propagation_type_counts": required_visibility["propagation_counts"],
        "degradation_type_counts": required_visibility["degradation_counts"],
        "explanation_type_counts": required_visibility["explanation_counts"],
        "evidence_type_counts": required_visibility["evidence_counts"],
        "diagnostic_type_counts": required_visibility["diagnostic_counts"],
        "unsupported_state_counts": required_visibility["unsupported_state_counts"],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "boundary_to_boundary_continuity_preserved": boundary_continuity["valid"],
        "drift_continuity_preserved": drift_continuity["valid"],
        "propagation_continuity_preserved": propagation_continuity["valid"],
        "degradation_continuity_preserved": degradation_continuity["valid"],
        "explanation_continuity_preserved": explanation_continuity["valid"],
        "evidence_continuity_stable": evidence_continuity["valid"],
        "replay_safe_evidence_verified": evidence_continuity[
            "replay_safe_evidence_count"
        ]
        == len(intelligence.evidence_continuity),
        "rollback_safe_evidence_verified": evidence_continuity[
            "rollback_safe_evidence_count"
        ]
        == len(intelligence.evidence_continuity),
        "provenance_safe_evidence_verified": evidence_continuity[
            "provenance_safe_evidence_count"
        ]
        == len(intelligence.evidence_continuity),
        "lineage_safe_evidence_verified": evidence_continuity[
            "lineage_safe_evidence_count"
        ]
        == len(intelligence.evidence_continuity),
        "integrity_safe_evidence_verified": evidence_continuity[
            "integrity_safe_evidence_count"
        ]
        == len(intelligence.evidence_continuity),
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "fail_visible_unsupported_cross_boundary_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "inherited_prohibition_count": descriptive_only["inherited_prohibition_count"],
        "inherited_constraint_count": descriptive_only["inherited_constraint_count"],
        "explicit_limitation_count": descriptive_only["explicit_limitation_count"],
        "validation_error_count": validation["validation_error_count"],
        "repository_remains": [
            "NON-operational",
            "NON-authorizing",
            "NON-executing",
            "NON-remediating",
            "NON-runtime-mutating",
        ],
        "repository_state": descriptive_only["required_repository_states"],
        **counters,
    }
    visibility = {
        "cross_boundary_continuity_summaries": cross_boundary_continuity_summary_visibility(
            intelligence.cross_boundary_continuity
        ),
        "boundary_pair_summaries": boundary_pair_summary_visibility(
            intelligence.boundary_pair_continuity
        ),
        "drift_continuity_summaries": drift_continuity_summary_visibility(
            intelligence.drift_continuity
        ),
        "propagation_continuity_summaries": propagation_continuity_summary_visibility(
            intelligence.propagation_continuity
        ),
        "degradation_continuity_summaries": degradation_continuity_summary_visibility(
            intelligence.degradation_continuity
        ),
        "explanation_continuity_summaries": explanation_continuity_summary_visibility(
            intelligence.explanation_continuity
        ),
        "evidence_continuity_summaries": evidence_continuity_summary_visibility(
            intelligence.evidence_continuity
        ),
        "fail_visible_cross_boundary_diagnostics": fail_visible_cross_boundary_diagnostic_summaries(
            intelligence.diagnostics
        ),
        "unsupported_cross_boundary_visibility": unsupported_cross_boundary_visibility_summaries(
            intelligence.unsupported_cross_boundary_visibility
        ),
        "descriptive_only_summary": descriptive_only_cross_boundary_continuity_summary(
            intelligence
        ),
    }
    report_without_hash = {
        "schema_version": V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_REPORT_SCHEMA_VERSION,
        "phase_id": V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_PHASE_ID,
        "generated_at": V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_GENERATED_AT,
        "purpose": V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_PURPOSE,
        "foundation_status": (
            V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_STATUS_STABLE
            if validation["valid"]
            else V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_STATUS_BLOCKED
        ),
        "summary": summary,
        "visibility": visibility,
        "validation": validation,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "cross_boundary_drift_continuity_intelligence": exported,
    }
    return {
        **report_without_hash,
        "deterministic_report_hash": deterministic_v4_5a_5_cross_boundary_drift_continuity_hash(
            report_without_hash
        ),
    }


def contaminate_v4_5a_5_cross_boundary_drift_continuity_for_non_operational_validation(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> CrossBoundaryDriftContinuityIntelligence:
    contaminated_boundary = replace(
        intelligence.cross_boundary_continuity[0],
        routing_enabled=True,
        traversal_enabled=True,
        boundary_traversal_enabled=True,
        continuity_restoration_enabled=True,
    )
    contaminated_diagnostic = replace(
        intelligence.diagnostics[0],
        remediation_enabled=True,
        mitigation_enabled=True,
        silent_fallback_enabled=True,
        continuity_restoration_enabled=True,
    )
    contaminated_state = replace(
        intelligence.unsupported_cross_boundary_visibility[0],
        operational_enabled=True,
        routing_enabled=True,
        boundary_traversal_enabled=True,
        continuity_restoration_enabled=True,
    )
    return replace(
        intelligence,
        cross_boundary_continuity=(contaminated_boundary,)
        + intelligence.cross_boundary_continuity[1:],
        diagnostics=(contaminated_diagnostic,) + intelligence.diagnostics[1:],
        unsupported_cross_boundary_visibility=(contaminated_state,)
        + intelligence.unsupported_cross_boundary_visibility[1:],
        orchestration_routing_enabled=True,
        boundary_traversal_enabled=True,
        continuity_restoration_enabled=True,
        remediation_enabled=True,
        runtime_mutation_enabled=True,
    )
