"""Audit for deterministic v4.5A.6 drift diagnostics aggregation.

The audit validates descriptive drift diagnostics aggregation only. It does not
execute, authorize, approve, dispatch, route, traverse, schedule, sequence,
decide, recommend, prioritize, triage, rank, remediate, repair, mitigate,
correct, restore continuity, integrate planners, consume production paths, or
mutate runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_5a_6_drift_diagnostics_aggregation_hashing import (
    deterministic_v4_5a_6_drift_diagnostics_aggregation_hash,
    hash_aggregated_diagnostic_record,
    hash_blocker_warning_summary_visibility,
    hash_continuity_gap_summary_visibility,
    hash_diagnostic_aggregation_record,
    hash_diagnostic_severity_summary_visibility,
    hash_diagnostic_source_aggregation,
    hash_drift_diagnostics_aggregation_identity,
    hash_evidence_gap_summary_visibility,
    hash_unsupported_aggregation_visibility,
    hash_unsupported_state_summary_visibility,
    hash_v4_5a_6_drift_diagnostics_aggregation,
)
from .v4_5a_6_drift_diagnostics_aggregation_models import (
    AGGREGATED_DIAGNOSTIC_TYPES,
    BLOCKER_WARNING_SUMMARY_TYPES,
    CONTINUITY_GAP_SUMMARY_TYPES,
    DIAGNOSTIC_SEVERITY_SUMMARY_TYPES,
    DIAGNOSTIC_SOURCE_TYPES,
    EVIDENCE_GAP_SUMMARY_TYPES,
    SOURCE_REPORTS,
    UNSUPPORTED_AGGREGATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_SUMMARY_TYPES,
    V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_HASH_REFERENCE,
    V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_REFERENCE,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_DISABLED_COUNTER_NAMES,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_GENERATED_AT,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_PHASE_ID,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_PURPOSE,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_REPORT_SCHEMA_VERSION,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_STATUS_BLOCKED,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_STATUS_STABLE,
    DriftDiagnosticsAggregationIntelligence,
    default_v4_5a_6_drift_diagnostics_aggregation,
)
from .v4_5a_6_drift_diagnostics_aggregation_serialization import (
    export_v4_5a_6_drift_diagnostics_aggregation,
    serialize_v4_5a_6_drift_diagnostics_aggregation,
)
from .v4_5a_6_drift_diagnostics_aggregation_visibility import (
    aggregation_summary_visibility,
    blocker_warning_summary_visibility,
    continuity_gap_summary_visibility,
    descriptive_only_diagnostics_aggregation_summary,
    diagnostic_source_summary_visibility,
    evidence_gap_summary_visibility,
    fail_visible_aggregated_diagnostic_summaries,
    severity_summary_visibility,
    unsupported_aggregation_visibility_summaries,
    unsupported_state_summary_visibility,
    validate_required_diagnostics_aggregation_visibility,
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
    ),
    "enabled_automated_prioritization_count": (
        "automated_prioritization_enabled",
        "prioritization_enabled",
    ),
    "enabled_automated_triage_count": ("automated_triage_enabled",),
    "enabled_ranking_count": (
        "ranking_enabled",
        "scoring_enabled",
    ),
    "enabled_recommendation_count": (
        "recommendation_enabled",
        "recommendation_behavior_enabled",
    ),
    "enabled_prioritization_action_count": (
        "prioritization_action_enabled",
        "action_logic_enabled",
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
    "enabled_continuity_restoration_count": (
        "continuity_restoration_enabled",
        "restoration_enabled",
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


def build_v4_5a_6_drift_diagnostics_aggregation() -> (
    DriftDiagnosticsAggregationIntelligence
):
    return default_v4_5a_6_drift_diagnostics_aggregation()


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


def enabled_drift_diagnostics_aggregation_capability_flags(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "aggregation_record_id", None)
            or getattr(item, "source_aggregation_id", None)
            or getattr(item, "unsupported_summary_id", None)
            or getattr(item, "evidence_gap_id", None)
            or getattr(item, "continuity_gap_id", None)
            or getattr(item, "severity_summary_id", None)
            or getattr(item, "blocker_warning_id", None)
            or getattr(item, "aggregated_diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "aggregation_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def drift_diagnostics_aggregation_capability_counter_values(
    intelligence: DriftDiagnosticsAggregationIntelligence,
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


def drift_diagnostics_aggregation_equal(
    left: DriftDiagnosticsAggregationIntelligence,
    right: DriftDiagnosticsAggregationIntelligence,
) -> bool:
    return serialize_v4_5a_6_drift_diagnostics_aggregation(
        left
    ) == serialize_v4_5a_6_drift_diagnostics_aggregation(right)


def validate_diagnostics_aggregation_ordering_stability(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "diagnostic_aggregation_records": tuple(
            record.deterministic_order
            for record in intelligence.diagnostic_aggregation_records
        ),
        "diagnostic_source_aggregation": tuple(
            record.deterministic_order
            for record in intelligence.diagnostic_source_aggregation
        ),
        "unsupported_state_summaries": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_state_summaries
        ),
        "evidence_gap_summaries": tuple(
            record.deterministic_order for record in intelligence.evidence_gap_summaries
        ),
        "continuity_gap_summaries": tuple(
            record.deterministic_order
            for record in intelligence.continuity_gap_summaries
        ),
        "severity_summaries": tuple(
            record.deterministic_order for record in intelligence.severity_summaries
        ),
        "blocker_warning_summaries": tuple(
            record.deterministic_order
            for record in intelligence.blocker_warning_summaries
        ),
        "aggregated_diagnostics": tuple(
            record.deterministic_order for record in intelligence.aggregated_diagnostics
        ),
        "unsupported_aggregation_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_aggregation_visibility
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


def validate_diagnostics_aggregation_identity_integrity(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    identity = intelligence.aggregation_identity
    record_ids = [
        record.aggregation_record_id
        for record in intelligence.diagnostic_aggregation_records
    ]
    diagnostic_aggregation_ids = [
        record.diagnostic_aggregation_id
        for record in intelligence.diagnostic_aggregation_records
    ]
    empty_identity_fields = [
        field_name
        for field_name in (
            "aggregation_id",
            "phase_id",
            "schema_version",
            "generated_at",
            "classification",
            "source_cross_boundary_report_reference",
            "source_cross_boundary_hash_reference",
        )
        if not getattr(identity, field_name)
    ]
    return {
        "valid": not (
            empty_identity_fields
            or len(set(record_ids)) != len(record_ids)
            or len(set(diagnostic_aggregation_ids)) != len(diagnostic_aggregation_ids)
            or identity.source_cross_boundary_report_reference
            != V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_REFERENCE
            or identity.source_cross_boundary_hash_reference
            != V4_5A_5_CROSS_BOUNDARY_CONTINUITY_REPORT_HASH_REFERENCE
        ),
        "aggregation_record_count": len(intelligence.diagnostic_aggregation_records),
        "unique_aggregation_record_count": len(set(record_ids)),
        "unique_diagnostic_aggregation_count": len(set(diagnostic_aggregation_ids)),
        "empty_identity_fields": empty_identity_fields,
        "source_cross_boundary_report_reference": (
            identity.source_cross_boundary_report_reference
        ),
        "source_cross_boundary_hash_reference": (
            identity.source_cross_boundary_hash_reference
        ),
    }


def validate_diagnostic_source_aggregation_stability(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    source_records = intelligence.diagnostic_source_aggregation
    present = {record.source_type for record in source_records}
    missing_source_types = sorted(set(DIAGNOSTIC_SOURCE_TYPES) - present)
    bad_source_references = sorted(
        record.source_aggregation_id
        for record in source_records
        if SOURCE_REPORTS[record.source_type]
        != (record.source_report_reference, record.source_hash_reference)
    )
    unsafe_source_ids = sorted(
        record.source_aggregation_id
        for record in source_records
        if (
            not record.descriptive_only
            or not record.no_triage
            or not record.no_prioritization
            or not record.no_ranking
            or not record.no_recommendation
            or record.automated_triage_enabled
            or record.automated_prioritization_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
        )
    )
    return {
        "valid": not (missing_source_types or bad_source_references or unsafe_source_ids),
        "source_count": len(source_records),
        "missing_source_types": missing_source_types,
        "bad_source_references": bad_source_references,
        "unsafe_source_ids": unsafe_source_ids,
        "diagnostic_source_aggregation_stable": True,
    }


def validate_unsupported_state_summary_visibility(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    records = intelligence.unsupported_state_summaries
    present = {record.unsupported_summary_type for record in records}
    missing_types = sorted(set(UNSUPPORTED_STATE_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.unsupported_summary_id
        for record in records
        if (
            not record.descriptive_only
            or not record.fail_visible
            or record.automatic_response_enabled
            or record.remediation_enabled
            or record.recommendation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "unsupported_summary_count": len(records),
        "missing_unsupported_summary_types": missing_types,
        "unsafe_unsupported_summary_ids": unsafe_ids,
    }


def validate_evidence_gap_visibility_preservation(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    records = intelligence.evidence_gap_summaries
    present = {record.evidence_gap_type for record in records}
    missing_types = sorted(set(EVIDENCE_GAP_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.evidence_gap_id
        for record in records
        if (
            not record.replay_safe
            or not record.rollback_safe
            or not record.provenance_safe
            or not record.lineage_safe
            or not record.descriptive_only
            or record.evidence_repair_enabled
            or record.backfill_enabled
            or record.remediation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "evidence_gap_count": len(records),
        "missing_evidence_gap_types": missing_types,
        "unsafe_evidence_gap_ids": unsafe_ids,
        "replay_safe_gap_count": sum(1 for record in records if record.replay_safe),
        "rollback_safe_gap_count": sum(1 for record in records if record.rollback_safe),
        "provenance_safe_gap_count": sum(
            1 for record in records if record.provenance_safe
        ),
        "lineage_safe_gap_count": sum(1 for record in records if record.lineage_safe),
    }


def validate_continuity_gap_visibility_preservation(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    records = intelligence.continuity_gap_summaries
    present = {record.continuity_gap_type for record in records}
    missing_types = sorted(set(CONTINUITY_GAP_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.continuity_gap_id
        for record in records
        if (
            not record.descriptive_only
            or not record.fail_visible
            or record.continuity_restoration_enabled
            or record.remediation_enabled
            or record.repair_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "continuity_gap_count": len(records),
        "missing_continuity_gap_types": missing_types,
        "unsafe_continuity_gap_ids": unsafe_ids,
        "continuity_restoration_enabled_count": sum(
            1 for record in records if record.continuity_restoration_enabled
        ),
    }


def validate_severity_summary_determinism(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    records = intelligence.severity_summaries
    present = {record.severity_type for record in records}
    missing_types = sorted(set(DIAGNOSTIC_SEVERITY_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.severity_summary_id
        for record in records
        if (
            not record.descriptive_only
            or not record.non_ranking
            or not record.non_recommending
            or not record.non_authorizing
            or record.ranking_enabled
            or record.recommendation_enabled
            or record.authorization_enabled
            or record.automated_triage_enabled
            or record.diagnostic_count < 0
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "severity_summary_count": len(records),
        "missing_severity_types": missing_types,
        "unsafe_severity_summary_ids": unsafe_ids,
    }


def validate_blocker_warning_summary_determinism(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    records = intelligence.blocker_warning_summaries
    present = {record.blocker_warning_type for record in records}
    missing_types = sorted(set(BLOCKER_WARNING_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.blocker_warning_id
        for record in records
        if (
            not record.descriptive_only
            or record.action_logic_enabled
            or record.prioritization_enabled
            or record.recommendation_enabled
            or record.remediation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "blocker_warning_summary_count": len(records),
        "missing_blocker_warning_types": missing_types,
        "unsafe_blocker_warning_ids": unsafe_ids,
    }


def validate_lineage_and_provenance_preservation(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    missing_lineage = sorted(
        record.aggregation_record_id
        for record in intelligence.diagnostic_aggregation_records
        if not record.lineage_reference_id
    )
    missing_provenance = sorted(
        record.aggregation_record_id
        for record in intelligence.diagnostic_aggregation_records
        if not record.provenance_reference_id
    )
    missing_continuity = sorted(
        record.aggregation_record_id
        for record in intelligence.diagnostic_aggregation_records
        if not record.continuity_reference_id
    )
    return {
        "valid": not (missing_lineage or missing_provenance or missing_continuity),
        "lineage_continuity_preserved": not missing_lineage,
        "provenance_continuity_preserved": not missing_provenance,
        "continuity_reference_preserved": not missing_continuity,
        "missing_lineage": missing_lineage,
        "missing_provenance": missing_provenance,
        "missing_continuity": missing_continuity,
    }


def validate_diagnostics_aggregation_serialization_and_hashing(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    second = build_v4_5a_6_drift_diagnostics_aggregation()
    serialization_one = serialize_v4_5a_6_drift_diagnostics_aggregation(intelligence)
    serialization_two = serialize_v4_5a_6_drift_diagnostics_aggregation(second)
    hash_one = hash_v4_5a_6_drift_diagnostics_aggregation(intelligence)
    hash_two = hash_v4_5a_6_drift_diagnostics_aggregation(second)
    hash_lengths_valid = all(
        len(value) == 64
        for value in (
            hash_drift_diagnostics_aggregation_identity(
                intelligence.aggregation_identity
            ),
            hash_diagnostic_aggregation_record(
                intelligence.diagnostic_aggregation_records[0]
            ),
            hash_diagnostic_source_aggregation(
                intelligence.diagnostic_source_aggregation[0]
            ),
            hash_unsupported_state_summary_visibility(
                intelligence.unsupported_state_summaries[0]
            ),
            hash_evidence_gap_summary_visibility(intelligence.evidence_gap_summaries[0]),
            hash_continuity_gap_summary_visibility(
                intelligence.continuity_gap_summaries[0]
            ),
            hash_diagnostic_severity_summary_visibility(
                intelligence.severity_summaries[0]
            ),
            hash_blocker_warning_summary_visibility(
                intelligence.blocker_warning_summaries[0]
            ),
            hash_aggregated_diagnostic_record(intelligence.aggregated_diagnostics[0]),
            hash_unsupported_aggregation_visibility(
                intelligence.unsupported_aggregation_visibility[0]
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
        "drift_diagnostics_aggregation_hash": hash_one,
    }


def validate_fail_visible_aggregation_diagnostics(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    diagnostic_types = {
        record.diagnostic_type for record in intelligence.aggregated_diagnostics
    }
    unsupported_states = {
        record.unsupported_state
        for record in intelligence.unsupported_aggregation_visibility
    }
    missing_diagnostic_types = sorted(set(AGGREGATED_DIAGNOSTIC_TYPES) - diagnostic_types)
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_AGGREGATION_OPERATIONAL_STATES) - unsupported_states
    )
    unsafe_diagnostic_ids = sorted(
        record.aggregated_diagnostic_id
        for record in intelligence.aggregated_diagnostics
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.silent_fallback_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.mitigation_enabled
            or record.auto_correction_enabled
            or record.automated_triage_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
            or record.orchestration_response_enabled
        )
    )
    unsafe_unsupported_ids = sorted(
        record.state_id
        for record in intelligence.unsupported_aggregation_visibility
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.operational_enabled
            or record.authorization_enabled
            or record.automated_prioritization_enabled
            or record.automated_triage_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.mitigation_enabled
            or record.automated_correction_enabled
            or record.continuity_restoration_enabled
        )
    )
    return {
        "valid": not (
            missing_diagnostic_types
            or missing_unsupported_states
            or unsafe_diagnostic_ids
            or unsafe_unsupported_ids
        ),
        "aggregated_diagnostic_count": len(intelligence.aggregated_diagnostics),
        "unsupported_state_count": len(intelligence.unsupported_aggregation_visibility),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_ids": unsafe_unsupported_ids,
        "fail_visible": all(
            record.fail_visible for record in intelligence.aggregated_diagnostics
        )
        and all(
            record.fail_visible
            for record in intelligence.unsupported_aggregation_visibility
        ),
        "silent_fallback_enabled_count": sum(
            1
            for record in intelligence.aggregated_diagnostics
            if record.silent_fallback_enabled
        ),
        "ranking_enabled_count": sum(
            1 for record in intelligence.aggregated_diagnostics if record.ranking_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_aggregation_visibility
            if record.ranking_enabled
        ),
        "recommendation_enabled_count": sum(
            1
            for record in intelligence.aggregated_diagnostics
            if record.recommendation_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_aggregation_visibility
            if record.recommendation_enabled
        ),
        "automated_triage_enabled_count": sum(
            1
            for record in intelligence.aggregated_diagnostics
            if record.automated_triage_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_aggregation_visibility
            if record.automated_triage_enabled
        ),
    }


def validate_descriptive_only_diagnostics_aggregation_guarantees(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    counters = drift_diagnostics_aggregation_capability_counter_values(intelligence)
    enabled_flags = enabled_drift_diagnostics_aggregation_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "aggregation_record_id", None)
            or getattr(item, "aggregated_diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "aggregation_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_DISABLED_COUNTER_NAMES)
        - set(counters)
    )
    required_repository_states = {
        "NON-operational": intelligence.non_operational,
        "NON-authorizing": intelligence.non_authorizing,
        "NON-executing": intelligence.non_executing,
        "NON-remediating": intelligence.non_remediating,
        "NON-runtime-mutating": intelligence.non_runtime_mutating,
        "NON-ranking": intelligence.non_ranking,
        "NON-recommending": intelligence.non_recommending,
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


def validate_v4_5a_6_drift_diagnostics_aggregation(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_diagnostics_aggregation_ordering_stability(intelligence),
        "identity_integrity": validate_diagnostics_aggregation_identity_integrity(
            intelligence
        ),
        "diagnostic_source_aggregation": validate_diagnostic_source_aggregation_stability(
            intelligence
        ),
        "unsupported_state_summary": validate_unsupported_state_summary_visibility(
            intelligence
        ),
        "evidence_gap_visibility": validate_evidence_gap_visibility_preservation(
            intelligence
        ),
        "continuity_gap_visibility": validate_continuity_gap_visibility_preservation(
            intelligence
        ),
        "severity_summary": validate_severity_summary_determinism(intelligence),
        "blocker_warning_summary": validate_blocker_warning_summary_determinism(
            intelligence
        ),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_hashing": validate_diagnostics_aggregation_serialization_and_hashing(
            intelligence
        ),
        "required_visibility": validate_required_diagnostics_aggregation_visibility(
            intelligence
        ),
        "fail_visible_aggregation": validate_fail_visible_aggregation_diagnostics(
            intelligence
        ),
        "descriptive_only_guarantees": validate_descriptive_only_diagnostics_aggregation_guarantees(
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


def build_v4_5a_6_drift_diagnostics_aggregation_report() -> dict[str, Any]:
    intelligence = build_v4_5a_6_drift_diagnostics_aggregation()
    exported = export_v4_5a_6_drift_diagnostics_aggregation(intelligence)
    validation = validate_v4_5a_6_drift_diagnostics_aggregation(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    source_validation = validation["validations"]["diagnostic_source_aggregation"]
    unsupported_summary = validation["validations"]["unsupported_state_summary"]
    evidence_gap = validation["validations"]["evidence_gap_visibility"]
    continuity_gap = validation["validations"]["continuity_gap_visibility"]
    severity = validation["validations"]["severity_summary"]
    blocker_warning = validation["validations"]["blocker_warning_summary"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_aggregation"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "aggregation_identity_hash": hash_drift_diagnostics_aggregation_identity(
            intelligence.aggregation_identity
        ),
        "drift_diagnostics_aggregation_hash": hash_v4_5a_6_drift_diagnostics_aggregation(
            intelligence
        ),
        "diagnostic_aggregation_hashes": {
            record.aggregation_record_id: hash_diagnostic_aggregation_record(record)
            for record in sorted(
                intelligence.diagnostic_aggregation_records,
                key=lambda item: (item.deterministic_order, item.aggregation_record_id),
            )
        },
        "diagnostic_source_hashes": {
            record.source_aggregation_id: hash_diagnostic_source_aggregation(record)
            for record in sorted(
                intelligence.diagnostic_source_aggregation,
                key=lambda item: (item.deterministic_order, item.source_aggregation_id),
            )
        },
        "unsupported_summary_hashes": {
            record.unsupported_summary_id: hash_unsupported_state_summary_visibility(
                record
            )
            for record in sorted(
                intelligence.unsupported_state_summaries,
                key=lambda item: (item.deterministic_order, item.unsupported_summary_id),
            )
        },
        "evidence_gap_hashes": {
            record.evidence_gap_id: hash_evidence_gap_summary_visibility(record)
            for record in sorted(
                intelligence.evidence_gap_summaries,
                key=lambda item: (item.deterministic_order, item.evidence_gap_id),
            )
        },
        "continuity_gap_hashes": {
            record.continuity_gap_id: hash_continuity_gap_summary_visibility(record)
            for record in sorted(
                intelligence.continuity_gap_summaries,
                key=lambda item: (item.deterministic_order, item.continuity_gap_id),
            )
        },
        "severity_summary_hashes": {
            record.severity_summary_id: hash_diagnostic_severity_summary_visibility(
                record
            )
            for record in sorted(
                intelligence.severity_summaries,
                key=lambda item: (item.deterministic_order, item.severity_summary_id),
            )
        },
        "blocker_warning_hashes": {
            record.blocker_warning_id: hash_blocker_warning_summary_visibility(record)
            for record in sorted(
                intelligence.blocker_warning_summaries,
                key=lambda item: (item.deterministic_order, item.blocker_warning_id),
            )
        },
        "aggregated_diagnostic_hashes": {
            record.aggregated_diagnostic_id: hash_aggregated_diagnostic_record(record)
            for record in sorted(
                intelligence.aggregated_diagnostics,
                key=lambda item: (item.deterministic_order, item.aggregated_diagnostic_id),
            )
        },
        "unsupported_aggregation_hashes": {
            record.state_id: hash_unsupported_aggregation_visibility(record)
            for record in sorted(
                intelligence.unsupported_aggregation_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "diagnostic_aggregation_record_count": len(
            intelligence.diagnostic_aggregation_records
        ),
        "diagnostic_source_count": len(intelligence.diagnostic_source_aggregation),
        "unsupported_state_summary_count": len(intelligence.unsupported_state_summaries),
        "evidence_gap_summary_count": len(intelligence.evidence_gap_summaries),
        "continuity_gap_summary_count": len(intelligence.continuity_gap_summaries),
        "severity_summary_count": len(intelligence.severity_summaries),
        "blocker_warning_summary_count": len(intelligence.blocker_warning_summaries),
        "aggregated_diagnostic_count": len(intelligence.aggregated_diagnostics),
        "unsupported_aggregation_state_count": len(
            intelligence.unsupported_aggregation_visibility
        ),
        "diagnostic_source_counts": required_visibility["source_counts"],
        "unsupported_summary_counts": required_visibility["unsupported_summary_counts"],
        "evidence_gap_counts": required_visibility["evidence_gap_counts"],
        "continuity_gap_counts": required_visibility["continuity_gap_counts"],
        "severity_counts": required_visibility["severity_counts"],
        "blocker_warning_counts": required_visibility["blocker_warning_counts"],
        "aggregated_diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "diagnostic_source_aggregation_stable": source_validation["valid"],
        "unsupported_state_visibility_preserved": unsupported_summary["valid"],
        "evidence_gap_visibility_preserved": evidence_gap["valid"],
        "continuity_gap_visibility_preserved": continuity_gap["valid"],
        "severity_summary_stable": severity["valid"],
        "blocker_warning_summary_stable": blocker_warning["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "continuity_reference_preserved": lineage_provenance[
            "continuity_reference_preserved"
        ],
        "fail_visible_aggregation_diagnostics_verified": fail_visible["valid"],
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
            "NON-ranking",
            "NON-recommending",
        ],
        "repository_state": descriptive_only["required_repository_states"],
        **counters,
    }
    visibility = {
        "aggregation_summaries": aggregation_summary_visibility(
            intelligence.diagnostic_aggregation_records
        ),
        "diagnostic_source_summaries": diagnostic_source_summary_visibility(
            intelligence.diagnostic_source_aggregation
        ),
        "unsupported_state_summaries": unsupported_state_summary_visibility(
            intelligence.unsupported_state_summaries
        ),
        "evidence_gap_summaries": evidence_gap_summary_visibility(
            intelligence.evidence_gap_summaries
        ),
        "continuity_gap_summaries": continuity_gap_summary_visibility(
            intelligence.continuity_gap_summaries
        ),
        "severity_summaries": severity_summary_visibility(
            intelligence.severity_summaries
        ),
        "blocker_warning_summaries": blocker_warning_summary_visibility(
            intelligence.blocker_warning_summaries
        ),
        "fail_visible_aggregated_diagnostics": fail_visible_aggregated_diagnostic_summaries(
            intelligence.aggregated_diagnostics
        ),
        "unsupported_aggregation_visibility": unsupported_aggregation_visibility_summaries(
            intelligence.unsupported_aggregation_visibility
        ),
        "descriptive_only_summary": descriptive_only_diagnostics_aggregation_summary(
            intelligence
        ),
    }
    report_without_hash = {
        "schema_version": V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_REPORT_SCHEMA_VERSION,
        "phase_id": V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_PHASE_ID,
        "generated_at": V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_GENERATED_AT,
        "purpose": V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_PURPOSE,
        "foundation_status": (
            V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_STATUS_STABLE
            if validation["valid"]
            else V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_STATUS_BLOCKED
        ),
        "summary": summary,
        "visibility": visibility,
        "validation": validation,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "drift_diagnostics_aggregation_intelligence": exported,
    }
    return {
        **report_without_hash,
        "deterministic_report_hash": deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
            report_without_hash
        ),
    }


def contaminate_v4_5a_6_drift_diagnostics_aggregation_for_non_operational_validation(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> DriftDiagnosticsAggregationIntelligence:
    contaminated_source = replace(
        intelligence.diagnostic_source_aggregation[0],
        automated_prioritization_enabled=True,
        automated_triage_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
    )
    contaminated_severity = replace(
        intelligence.severity_summaries[0],
        ranking_enabled=True,
        recommendation_enabled=True,
        automated_triage_enabled=True,
    )
    contaminated_diagnostic = replace(
        intelligence.aggregated_diagnostics[0],
        remediation_enabled=True,
        mitigation_enabled=True,
        silent_fallback_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
    )
    contaminated_state = replace(
        intelligence.unsupported_aggregation_visibility[0],
        automated_prioritization_enabled=True,
        automated_triage_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
        remediation_enabled=True,
    )
    return replace(
        intelligence,
        diagnostic_source_aggregation=(contaminated_source,)
        + intelligence.diagnostic_source_aggregation[1:],
        severity_summaries=(contaminated_severity,)
        + intelligence.severity_summaries[1:],
        aggregated_diagnostics=(contaminated_diagnostic,)
        + intelligence.aggregated_diagnostics[1:],
        unsupported_aggregation_visibility=(contaminated_state,)
        + intelligence.unsupported_aggregation_visibility[1:],
        automated_prioritization_enabled=True,
        automated_triage_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
        remediation_enabled=True,
        runtime_mutation_enabled=True,
    )
