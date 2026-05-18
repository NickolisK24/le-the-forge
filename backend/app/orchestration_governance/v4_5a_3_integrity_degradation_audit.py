"""Audit for deterministic v4.5A.3 integrity degradation intelligence.

The audit validates descriptive integrity degradation intelligence only. It does
not execute, authorize, approve, dispatch, route, traverse, schedule, sequence,
decide, recommend, remediate, repair, mitigate, suppress, correct, integrate
planners, consume production bundles, or mutate runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_5a_3_integrity_degradation_hashing import (
    deterministic_v4_5a_3_integrity_degradation_hash,
    hash_continuity_degradation,
    hash_cross_boundary_integrity,
    hash_degradation_classification,
    hash_degradation_evidence_chain,
    hash_degradation_record,
    hash_degradation_severity_accumulation,
    hash_explainability_degradation,
    hash_integrity_degradation_diagnostic,
    hash_integrity_degradation_identity,
    hash_unsupported_degradation_visibility,
    hash_v4_5a_3_integrity_degradation_intelligence,
)
from .v4_5a_3_integrity_degradation_models import (
    CONTINUITY_DEGRADATION_TYPES,
    CROSS_BOUNDARY_INTEGRITY_TYPES,
    DEGRADATION_CLASSIFICATION_TYPES,
    DEGRADATION_DIAGNOSTIC_TYPES,
    DEGRADATION_EVIDENCE_TYPES,
    EXPLAINABILITY_DEGRADATION_TYPES,
    UNSUPPORTED_DEGRADATION_OPERATIONAL_STATES,
    V4_5A_3_INTEGRITY_DEGRADATION_DISABLED_COUNTER_NAMES,
    V4_5A_3_INTEGRITY_DEGRADATION_GENERATED_AT,
    V4_5A_3_INTEGRITY_DEGRADATION_PHASE_ID,
    V4_5A_3_INTEGRITY_DEGRADATION_PURPOSE,
    V4_5A_3_INTEGRITY_DEGRADATION_REPORT_SCHEMA_VERSION,
    V4_5A_3_INTEGRITY_DEGRADATION_STATUS_BLOCKED,
    V4_5A_3_INTEGRITY_DEGRADATION_STATUS_STABLE,
    IntegrityDegradationIntelligence,
    default_v4_5a_3_integrity_degradation_intelligence,
)
from .v4_5a_3_integrity_degradation_serialization import (
    export_v4_5a_3_integrity_degradation_intelligence,
    serialize_v4_5a_3_integrity_degradation_intelligence,
)
from .v4_5a_3_integrity_degradation_visibility import (
    continuity_degradation_summary_visibility,
    cross_boundary_integrity_summary_visibility,
    degradation_evidence_summary_visibility,
    degradation_severity_summary_visibility,
    degradation_summary_visibility,
    descriptive_only_degradation_summary,
    explainability_degradation_summary_visibility,
    fail_visible_degradation_diagnostic_summaries,
    unsupported_degradation_visibility_summaries,
    validate_required_degradation_visibility,
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
    "enabled_remediation_count": (
        "remediation_enabled",
        "auto_remediation_enabled",
    ),
    "enabled_repair_count": ("repair_enabled",),
    "enabled_mitigation_count": ("mitigation_enabled",),
    "enabled_degradation_suppression_count": (
        "degradation_suppression_enabled",
        "silent_suppression_enabled",
    ),
    "enabled_auto_correction_count": (
        "auto_correction_enabled",
        "automated_correction_enabled",
        "degradation_correction_enabled",
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


def build_v4_5a_3_integrity_degradation_intelligence() -> IntegrityDegradationIntelligence:
    return default_v4_5a_3_integrity_degradation_intelligence()


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


def enabled_integrity_degradation_capability_flags(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "degradation_id", None)
            or getattr(item, "classification_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "continuity_id", None)
            or getattr(item, "severity_id", None)
            or getattr(item, "explainability_id", None)
            or getattr(item, "cross_boundary_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "integrity_degradation_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def integrity_degradation_capability_counter_values(
    intelligence: IntegrityDegradationIntelligence,
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


def integrity_degradation_equal(
    left: IntegrityDegradationIntelligence,
    right: IntegrityDegradationIntelligence,
) -> bool:
    return serialize_v4_5a_3_integrity_degradation_intelligence(
        left
    ) == serialize_v4_5a_3_integrity_degradation_intelligence(right)


def validate_degradation_ordering_stability(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "degradation_records": tuple(
            record.deterministic_order for record in intelligence.degradation_records
        ),
        "classifications": tuple(
            record.deterministic_order for record in intelligence.classifications
        ),
        "evidence_chains": tuple(
            record.deterministic_order for record in intelligence.evidence_chains
        ),
        "continuity_degradation": tuple(
            record.deterministic_order for record in intelligence.continuity_degradation
        ),
        "severity_accumulation": tuple(
            record.deterministic_order for record in intelligence.severity_accumulation
        ),
        "explainability_degradation": tuple(
            record.deterministic_order
            for record in intelligence.explainability_degradation
        ),
        "cross_boundary_integrity": tuple(
            record.deterministic_order
            for record in intelligence.cross_boundary_integrity
        ),
        "diagnostics": tuple(
            record.deterministic_order for record in intelligence.diagnostics
        ),
        "unsupported_degradation_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_degradation_visibility
        ),
    }
    unordered_groups = [
        name for name, orders in order_groups.items() if tuple(sorted(orders)) != orders
    ]
    duplicate_groups = [
        name for name, orders in order_groups.items() if len(set(orders)) != len(orders)
    ]
    return {
        "valid": not unordered_groups and not duplicate_groups,
        "unordered_groups": unordered_groups,
        "duplicate_order_groups": duplicate_groups,
        "order_groups": {name: list(orders) for name, orders in order_groups.items()},
    }


def validate_degradation_identity_integrity(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    degradation_ids = [record.degradation_id for record in intelligence.degradation_records]
    degradation_id_set = set(degradation_ids)
    classification_ids = {record.degradation_id for record in intelligence.classifications}
    diagnostic_ids = {record.degradation_id for record in intelligence.diagnostics}
    missing_fields = [
        record.degradation_id
        for record in intelligence.degradation_records
        if not all(
            (
                record.degradation_id,
                record.degradation_chain_id,
                record.degradation_scope_id,
                record.source_drift_id,
                record.propagation_chain_id,
                record.continuity_reference_id,
                record.lineage_reference_id,
                record.integrity_reference_id,
            )
        )
    ]
    duplicate_degradation_ids = sorted(
        {item for item in degradation_ids if degradation_ids.count(item) > 1}
    )
    missing_classification_ids = sorted(degradation_id_set - classification_ids)
    unknown_classification_ids = sorted(classification_ids - degradation_id_set)
    unknown_diagnostic_ids = sorted(diagnostic_ids - degradation_id_set)
    observed_types = {record.classification_type for record in intelligence.classifications}
    missing_classification_types = sorted(
        set(DEGRADATION_CLASSIFICATION_TYPES) - observed_types
    )
    unknown_classification_types = sorted(
        observed_types - set(DEGRADATION_CLASSIFICATION_TYPES)
    )
    return {
        "valid": not (
            missing_fields
            or duplicate_degradation_ids
            or missing_classification_ids
            or unknown_classification_ids
            or unknown_diagnostic_ids
            or missing_classification_types
            or unknown_classification_types
        ),
        "degradation_record_count": len(degradation_ids),
        "classification_count": len(intelligence.classifications),
        "missing_fields": missing_fields,
        "duplicate_degradation_ids": duplicate_degradation_ids,
        "missing_classification_ids": missing_classification_ids,
        "unknown_classification_ids": unknown_classification_ids,
        "unknown_diagnostic_ids": unknown_diagnostic_ids,
        "missing_classification_types": missing_classification_types,
        "unknown_classification_types": unknown_classification_types,
    }


def validate_degradation_continuity_preservation(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    degradation_ids = {record.degradation_id for record in intelligence.degradation_records}
    chain_ids = {record.degradation_chain_id for record in intelligence.degradation_records}
    lineage_reference_ids = {
        record.lineage_reference_id for record in intelligence.degradation_records
    }
    continuity_degradation_ids = {
        record.degradation_id for record in intelligence.continuity_degradation
    }
    continuity_chain_ids = {
        record.degradation_chain_id for record in intelligence.continuity_degradation
    }
    continuity_lineage_ids = {
        record.lineage_reference_id for record in intelligence.continuity_degradation
    }
    missing_continuity_types = sorted(
        set(CONTINUITY_DEGRADATION_TYPES)
        - {record.continuity_type for record in intelligence.continuity_degradation}
    )
    unknown_degradation_ids = sorted(continuity_degradation_ids - degradation_ids)
    unknown_chain_ids = sorted(continuity_chain_ids - chain_ids)
    unknown_lineage_ids = sorted(continuity_lineage_ids - lineage_reference_ids)
    unsafe_continuity_ids = sorted(
        record.continuity_id
        for record in intelligence.continuity_degradation
        if not (
            record.continuity_preserved
            and record.replay_safe
            and record.rollback_safe
            and record.lineage_safe
            and record.provenance_safe
            and record.integrity_safe
            and record.descriptive_only
            and not record.restoration_enabled
            and not record.repair_enabled
            and not record.remediation_enabled
            and not record.degradation_correction_enabled
            and not record.runtime_mutation_enabled
        )
    )
    return {
        "valid": not (
            missing_continuity_types
            or unknown_degradation_ids
            or unknown_chain_ids
            or unknown_lineage_ids
            or unsafe_continuity_ids
        ),
        "continuity_degradation_count": len(intelligence.continuity_degradation),
        "missing_continuity_types": missing_continuity_types,
        "unknown_degradation_ids": unknown_degradation_ids,
        "unknown_chain_ids": unknown_chain_ids,
        "unknown_lineage_ids": unknown_lineage_ids,
        "unsafe_continuity_ids": unsafe_continuity_ids,
        "lineage_continuity_preserved": not unknown_lineage_ids,
        "provenance_continuity_preserved": all(
            record.provenance_safe for record in intelligence.continuity_degradation
        ),
        "integrity_continuity_preserved": all(
            record.integrity_safe for record in intelligence.continuity_degradation
        ),
    }


def validate_degradation_evidence_continuity(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    degradation_ids = {record.degradation_id for record in intelligence.degradation_records}
    evidence_ids = {record.evidence_id for record in intelligence.evidence_chains}
    evidence_by_degradation: dict[str, list[str]] = {
        degradation_id: [] for degradation_id in degradation_ids
    }
    for record in intelligence.evidence_chains:
        evidence_by_degradation.setdefault(record.degradation_id, []).append(
            record.evidence_id
        )
    diagnostic_evidence_ids = {
        evidence_id
        for record in intelligence.diagnostics
        for evidence_id in record.evidence_reference_ids
    }
    explainability_evidence_ids = {
        evidence_id
        for record in intelligence.explainability_degradation
        for evidence_id in record.evidence_reference_ids
    }
    unsupported_evidence_ids = {
        evidence_id
        for record in intelligence.unsupported_degradation_visibility
        for evidence_id in record.evidence_reference_ids
    }
    unknown_evidence_degradation_ids = sorted(set(evidence_by_degradation) - degradation_ids)
    missing_diagnostic_evidence_ids = sorted(diagnostic_evidence_ids - evidence_ids)
    missing_explainability_evidence_ids = sorted(explainability_evidence_ids - evidence_ids)
    missing_unsupported_evidence_ids = sorted(unsupported_evidence_ids - evidence_ids)
    missing_evidence_types = sorted(
        set(DEGRADATION_EVIDENCE_TYPES)
        - {record.evidence_type for record in intelligence.evidence_chains}
    )
    unsafe_evidence_ids = sorted(
        record.evidence_id
        for record in intelligence.evidence_chains
        if not (
            record.replay_safe
            and record.rollback_safe
            and record.provenance_safe
            and record.lineage_safe
            and record.integrity_safe
            and record.descriptive_only
            and not record.hidden_assumption_used
            and not record.production_consumption_enabled
            and bool(record.source_hash_reference)
        )
    )
    return {
        "valid": not (
            unknown_evidence_degradation_ids
            or missing_diagnostic_evidence_ids
            or missing_explainability_evidence_ids
            or missing_unsupported_evidence_ids
            or missing_evidence_types
            or unsafe_evidence_ids
        ),
        "evidence_chain_count": len(intelligence.evidence_chains),
        "replay_safe_evidence_count": sum(
            1 for record in intelligence.evidence_chains if record.replay_safe
        ),
        "provenance_safe_evidence_count": sum(
            1 for record in intelligence.evidence_chains if record.provenance_safe
        ),
        "lineage_safe_evidence_count": sum(
            1 for record in intelligence.evidence_chains if record.lineage_safe
        ),
        "unknown_evidence_degradation_ids": unknown_evidence_degradation_ids,
        "missing_diagnostic_evidence_ids": missing_diagnostic_evidence_ids,
        "missing_explainability_evidence_ids": missing_explainability_evidence_ids,
        "missing_unsupported_evidence_ids": missing_unsupported_evidence_ids,
        "missing_evidence_types": missing_evidence_types,
        "unsafe_evidence_ids": unsafe_evidence_ids,
    }


def validate_degradation_serialization_and_hashing(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    rebuilt = build_v4_5a_3_integrity_degradation_intelligence()
    serialized = serialize_v4_5a_3_integrity_degradation_intelligence(intelligence)
    rebuilt_serialized = serialize_v4_5a_3_integrity_degradation_intelligence(rebuilt)
    degradation_hash = hash_v4_5a_3_integrity_degradation_intelligence(intelligence)
    rebuilt_hash = hash_v4_5a_3_integrity_degradation_intelligence(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and degradation_hash == rebuilt_hash,
        "serialization_stable": serialized == rebuilt_serialized,
        "hashing_stable": degradation_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "degradation_hash": degradation_hash,
        "rebuilt_degradation_hash": rebuilt_hash,
    }


def validate_fail_visible_unsupported_degradation_visibility(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    observed_diagnostic_types = {record.diagnostic_type for record in intelligence.diagnostics}
    observed_unsupported_states = {
        record.unsupported_state for record in intelligence.unsupported_degradation_visibility
    }
    missing_diagnostic_types = sorted(set(DEGRADATION_DIAGNOSTIC_TYPES) - observed_diagnostic_types)
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_DEGRADATION_OPERATIONAL_STATES) - observed_unsupported_states
    )
    unsafe_diagnostic_ids = sorted(
        record.diagnostic_id
        for record in intelligence.diagnostics
        if not (
            record.fail_visible
            and record.descriptive_only
            and not record.hidden_assumption_used
            and not record.silent_suppression_enabled
            and not record.remediation_enabled
            and not record.repair_enabled
            and not record.mitigation_enabled
            and not record.auto_correction_enabled
            and not record.degradation_correction_enabled
            and not record.orchestration_response_enabled
            and not record.authorization_behavior_enabled
        )
    )
    unsafe_unsupported_state_ids = sorted(
        record.state_id
        for record in intelligence.unsupported_degradation_visibility
        if not (
            record.fail_visible
            and record.descriptive_only
            and not record.operational_enabled
            and not record.remediation_enabled
            and not record.repair_enabled
            and not record.mitigation_enabled
            and not record.degradation_suppression_enabled
            and not record.authorization_enabled
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
        "unsupported_state_count": len(intelligence.unsupported_degradation_visibility),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_state_ids": unsafe_unsupported_state_ids,
        "fail_visible": all(record.fail_visible for record in intelligence.diagnostics)
        and all(record.fail_visible for record in intelligence.unsupported_degradation_visibility),
        "silent_suppression_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.silent_suppression_enabled
        ),
        "remediation_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.remediation_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_degradation_visibility
            if record.remediation_enabled
        ),
        "degradation_suppression_enabled_count": sum(
            1
            for record in intelligence.unsupported_degradation_visibility
            if record.degradation_suppression_enabled
        ),
    }


def validate_degradation_explainability_and_cross_boundary_visibility(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    observed_explainability_types = {
        record.explainability_type for record in intelligence.explainability_degradation
    }
    observed_boundary_types = {
        record.boundary_type for record in intelligence.cross_boundary_integrity
    }
    missing_explainability_types = sorted(
        set(EXPLAINABILITY_DEGRADATION_TYPES) - observed_explainability_types
    )
    missing_cross_boundary_types = sorted(
        set(CROSS_BOUNDARY_INTEGRITY_TYPES) - observed_boundary_types
    )
    unsafe_explainability_ids = sorted(
        record.explainability_id
        for record in intelligence.explainability_degradation
        if not (
            record.explainability_first
            and record.descriptive_only
            and not record.automated_response_enabled
            and not record.recommendation_enabled
            and not record.decision_enabled
        )
    )
    unsafe_cross_boundary_ids = sorted(
        record.cross_boundary_id
        for record in intelligence.cross_boundary_integrity
        if not (
            record.descriptive_only
            and record.no_orchestration_traversal
            and record.no_operational_routing
            and not record.traversal_enabled
            and not record.routing_enabled
            and not record.dispatch_enabled
        )
    )
    return {
        "valid": not (
            missing_explainability_types
            or missing_cross_boundary_types
            or unsafe_explainability_ids
            or unsafe_cross_boundary_ids
        ),
        "explainability_count": len(intelligence.explainability_degradation),
        "cross_boundary_count": len(intelligence.cross_boundary_integrity),
        "missing_explainability_types": missing_explainability_types,
        "missing_cross_boundary_types": missing_cross_boundary_types,
        "unsafe_explainability_ids": unsafe_explainability_ids,
        "unsafe_cross_boundary_ids": unsafe_cross_boundary_ids,
    }


def validate_descriptive_only_degradation_guarantees(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    counters = integrity_degradation_capability_counter_values(intelligence)
    enabled_flags = enabled_integrity_degradation_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "degradation_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "integrity_degradation_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5A_3_INTEGRITY_DEGRADATION_DISABLED_COUNTER_NAMES) - set(counters)
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


def validate_v4_5a_3_integrity_degradation_intelligence(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_degradation_ordering_stability(intelligence),
        "identity_integrity": validate_degradation_identity_integrity(intelligence),
        "continuity_preservation": validate_degradation_continuity_preservation(
            intelligence
        ),
        "evidence_continuity": validate_degradation_evidence_continuity(intelligence),
        "serialization_hashing": validate_degradation_serialization_and_hashing(
            intelligence
        ),
        "required_visibility": validate_required_degradation_visibility(intelligence),
        "explainability_cross_boundary": validate_degradation_explainability_and_cross_boundary_visibility(
            intelligence
        ),
        "fail_visible_unsupported_degradation": validate_fail_visible_unsupported_degradation_visibility(
            intelligence
        ),
        "descriptive_only_guarantees": validate_descriptive_only_degradation_guarantees(
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


def build_v4_5a_3_integrity_degradation_intelligence_report() -> dict[str, Any]:
    intelligence = build_v4_5a_3_integrity_degradation_intelligence()
    exported = export_v4_5a_3_integrity_degradation_intelligence(intelligence)
    validation = validate_v4_5a_3_integrity_degradation_intelligence(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    continuity = validation["validations"]["continuity_preservation"]
    evidence_continuity = validation["validations"]["evidence_continuity"]
    fail_visible = validation["validations"]["fail_visible_unsupported_degradation"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    explainability = validation["validations"]["explainability_cross_boundary"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "degradation_identity_hash": hash_integrity_degradation_identity(
            intelligence.degradation_identity
        ),
        "integrity_degradation_intelligence_hash": hash_v4_5a_3_integrity_degradation_intelligence(
            intelligence
        ),
        "degradation_record_hashes": {
            record.degradation_id: hash_degradation_record(record)
            for record in sorted(
                intelligence.degradation_records,
                key=lambda item: (item.deterministic_order, item.degradation_id),
            )
        },
        "classification_hashes": {
            record.classification_id: hash_degradation_classification(record)
            for record in sorted(
                intelligence.classifications,
                key=lambda item: (item.deterministic_order, item.classification_id),
            )
        },
        "evidence_chain_hashes": {
            record.evidence_id: hash_degradation_evidence_chain(record)
            for record in sorted(
                intelligence.evidence_chains,
                key=lambda item: (item.deterministic_order, item.evidence_id),
            )
        },
        "continuity_degradation_hashes": {
            record.continuity_id: hash_continuity_degradation(record)
            for record in sorted(
                intelligence.continuity_degradation,
                key=lambda item: (item.deterministic_order, item.continuity_id),
            )
        },
        "severity_accumulation_hashes": {
            record.severity_id: hash_degradation_severity_accumulation(record)
            for record in sorted(
                intelligence.severity_accumulation,
                key=lambda item: (item.deterministic_order, item.severity_id),
            )
        },
        "explainability_degradation_hashes": {
            record.explainability_id: hash_explainability_degradation(record)
            for record in sorted(
                intelligence.explainability_degradation,
                key=lambda item: (item.deterministic_order, item.explainability_id),
            )
        },
        "cross_boundary_integrity_hashes": {
            record.cross_boundary_id: hash_cross_boundary_integrity(record)
            for record in sorted(
                intelligence.cross_boundary_integrity,
                key=lambda item: (item.deterministic_order, item.cross_boundary_id),
            )
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_integrity_degradation_diagnostic(record)
            for record in sorted(
                intelligence.diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_state_hashes": {
            record.state_id: hash_unsupported_degradation_visibility(record)
            for record in sorted(
                intelligence.unsupported_degradation_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "degradation_record_count": len(intelligence.degradation_records),
        "degradation_classification_count": len(intelligence.classifications),
        "degradation_evidence_chain_count": len(intelligence.evidence_chains),
        "continuity_degradation_count": len(intelligence.continuity_degradation),
        "degradation_severity_accumulation_count": len(intelligence.severity_accumulation),
        "explainability_degradation_count": len(intelligence.explainability_degradation),
        "cross_boundary_integrity_count": len(intelligence.cross_boundary_integrity),
        "degradation_diagnostic_count": len(intelligence.diagnostics),
        "unsupported_degradation_state_count": len(
            intelligence.unsupported_degradation_visibility
        ),
        "classification_type_counts": required_visibility["classification_counts"],
        "severity_type_counts": required_visibility["severity_counts"],
        "evidence_type_counts": required_visibility["evidence_counts"],
        "continuity_type_counts": required_visibility["continuity_counts"],
        "explainability_type_counts": required_visibility["explainability_counts"],
        "cross_boundary_type_counts": required_visibility["cross_boundary_counts"],
        "diagnostic_type_counts": required_visibility["diagnostic_counts"],
        "unsupported_state_counts": required_visibility["unsupported_state_counts"],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "lineage_continuity_preserved": continuity["lineage_continuity_preserved"],
        "provenance_continuity_preserved": continuity[
            "provenance_continuity_preserved"
        ],
        "integrity_continuity_preserved": continuity[
            "integrity_continuity_preserved"
        ],
        "replay_safe_evidence_verified": evidence_continuity[
            "replay_safe_evidence_count"
        ]
        == len(intelligence.evidence_chains),
        "provenance_safe_evidence_verified": evidence_continuity[
            "provenance_safe_evidence_count"
        ]
        == len(intelligence.evidence_chains),
        "lineage_safe_evidence_verified": evidence_continuity[
            "lineage_safe_evidence_count"
        ]
        == len(intelligence.evidence_chains),
        "degradation_explainability_verified": explainability["valid"],
        "fail_visible_unsupported_degradation_verified": fail_visible["valid"],
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
        "degradation_summaries": degradation_summary_visibility(intelligence),
        "degradation_severity_summaries": degradation_severity_summary_visibility(
            intelligence.severity_accumulation
        ),
        "continuity_degradation_summaries": continuity_degradation_summary_visibility(
            intelligence.continuity_degradation
        ),
        "explainability_degradation_summaries": explainability_degradation_summary_visibility(
            intelligence.explainability_degradation
        ),
        "degradation_evidence_summaries": degradation_evidence_summary_visibility(
            intelligence.evidence_chains
        ),
        "cross_boundary_integrity_summaries": cross_boundary_integrity_summary_visibility(
            intelligence.cross_boundary_integrity
        ),
        "fail_visible_degradation_diagnostics": fail_visible_degradation_diagnostic_summaries(
            intelligence.diagnostics
        ),
        "unsupported_degradation_visibility": unsupported_degradation_visibility_summaries(
            intelligence.unsupported_degradation_visibility
        ),
        "descriptive_only_summary": descriptive_only_degradation_summary(intelligence),
    }
    report_without_hash = {
        "schema_version": V4_5A_3_INTEGRITY_DEGRADATION_REPORT_SCHEMA_VERSION,
        "phase_id": V4_5A_3_INTEGRITY_DEGRADATION_PHASE_ID,
        "generated_at": V4_5A_3_INTEGRITY_DEGRADATION_GENERATED_AT,
        "purpose": V4_5A_3_INTEGRITY_DEGRADATION_PURPOSE,
        "foundation_status": (
            V4_5A_3_INTEGRITY_DEGRADATION_STATUS_STABLE
            if validation["valid"]
            else V4_5A_3_INTEGRITY_DEGRADATION_STATUS_BLOCKED
        ),
        "summary": summary,
        "visibility": visibility,
        "validation": validation,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "integrity_degradation_intelligence": exported,
    }
    return {
        **report_without_hash,
        "deterministic_report_hash": deterministic_v4_5a_3_integrity_degradation_hash(
            report_without_hash
        ),
    }


def contaminate_v4_5a_3_integrity_degradation_for_non_operational_validation(
    intelligence: IntegrityDegradationIntelligence,
) -> IntegrityDegradationIntelligence:
    contaminated_degradation = replace(
        intelligence.degradation_records[0],
        runtime_execution_enabled=True,
        orchestration_routing_enabled=True,
        operational_mutation_enabled=True,
    )
    contaminated_diagnostic = replace(
        intelligence.diagnostics[0],
        remediation_enabled=True,
        mitigation_enabled=True,
        silent_suppression_enabled=True,
        orchestration_response_enabled=True,
    )
    contaminated_state = replace(
        intelligence.unsupported_degradation_visibility[0],
        operational_enabled=True,
        degradation_suppression_enabled=True,
        authorization_enabled=True,
    )
    return replace(
        intelligence,
        degradation_records=(contaminated_degradation,)
        + intelligence.degradation_records[1:],
        diagnostics=(contaminated_diagnostic,) + intelligence.diagnostics[1:],
        unsupported_degradation_visibility=(contaminated_state,)
        + intelligence.unsupported_degradation_visibility[1:],
        orchestration_authorization_enabled=True,
        remediation_enabled=True,
        degradation_suppression_enabled=True,
        runtime_mutation_enabled=True,
    )
