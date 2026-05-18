"""Audit for deterministic v4.5A.2 drift propagation intelligence.

The audit validates descriptive propagation intelligence only. It does not
execute, authorize, approve, dispatch, route, traverse, schedule, sequence,
decide, recommend, remediate, repair, mitigate, suppress, correct, integrate
planners, consume production bundles, or mutate runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_5a_2_drift_propagation_hashing import (
    deterministic_v4_5a_2_drift_propagation_hash,
    hash_cross_boundary_propagation,
    hash_drift_propagation_identity,
    hash_propagation_chain,
    hash_propagation_classification,
    hash_propagation_continuity,
    hash_propagation_diagnostic,
    hash_propagation_evidence_chain,
    hash_propagation_explainability,
    hash_propagation_severity_accumulation,
    hash_unsupported_propagation_visibility,
    hash_v4_5a_2_drift_propagation_intelligence,
)
from .v4_5a_2_drift_propagation_models import (
    CROSS_BOUNDARY_PROPAGATION_TYPES,
    PROPAGATION_ACCUMULATION_TYPES,
    PROPAGATION_CHAIN_TYPES,
    PROPAGATION_DIAGNOSTIC_TYPES,
    PROPAGATION_EVIDENCE_TYPES,
    PROPAGATION_EXPLAINABILITY_TYPES,
    UNSUPPORTED_PROPAGATION_OPERATIONAL_STATES,
    V4_5A_2_DRIFT_PROPAGATION_DISABLED_COUNTER_NAMES,
    V4_5A_2_DRIFT_PROPAGATION_GENERATED_AT,
    V4_5A_2_DRIFT_PROPAGATION_PHASE_ID,
    V4_5A_2_DRIFT_PROPAGATION_PURPOSE,
    V4_5A_2_DRIFT_PROPAGATION_REPORT_SCHEMA_VERSION,
    V4_5A_2_DRIFT_PROPAGATION_STATUS_BLOCKED,
    V4_5A_2_DRIFT_PROPAGATION_STATUS_STABLE,
    DriftPropagationIntelligence,
    default_v4_5a_2_drift_propagation_intelligence,
)
from .v4_5a_2_drift_propagation_serialization import (
    export_v4_5a_2_drift_propagation_intelligence,
    serialize_v4_5a_2_drift_propagation_intelligence,
)
from .v4_5a_2_drift_propagation_visibility import (
    cross_boundary_propagation_summary_visibility,
    descriptive_only_propagation_summary,
    fail_visible_propagation_diagnostic_summaries,
    propagation_continuity_summary_visibility,
    propagation_evidence_summary_visibility,
    propagation_explainability_summary_visibility,
    propagation_severity_summary_visibility,
    propagation_summary_visibility,
    unsupported_propagation_visibility_summaries,
    validate_required_propagation_visibility,
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
    "enabled_auto_correction_count": (
        "auto_correction_enabled",
        "automated_correction_enabled",
    ),
    "enabled_propagation_suppression_count": (
        "propagation_suppression_enabled",
        "silent_suppression_enabled",
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


def build_v4_5a_2_drift_propagation_intelligence() -> DriftPropagationIntelligence:
    return default_v4_5a_2_drift_propagation_intelligence()


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


def enabled_drift_propagation_capability_flags(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "propagation_id", None)
            or getattr(item, "classification_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "continuity_id", None)
            or getattr(item, "severity_id", None)
            or getattr(item, "explainability_id", None)
            or getattr(item, "cross_boundary_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "propagation_foundation_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def drift_propagation_capability_counter_values(
    intelligence: DriftPropagationIntelligence,
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


def drift_propagation_equal(
    left: DriftPropagationIntelligence,
    right: DriftPropagationIntelligence,
) -> bool:
    return serialize_v4_5a_2_drift_propagation_intelligence(
        left
    ) == serialize_v4_5a_2_drift_propagation_intelligence(right)


def validate_propagation_ordering_stability(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "propagation_chains": tuple(
            record.deterministic_order for record in intelligence.propagation_chains
        ),
        "classifications": tuple(
            record.deterministic_order for record in intelligence.classifications
        ),
        "evidence_chains": tuple(
            record.deterministic_order for record in intelligence.evidence_chains
        ),
        "continuity_records": tuple(
            record.deterministic_order for record in intelligence.continuity_records
        ),
        "severity_accumulation": tuple(
            record.deterministic_order for record in intelligence.severity_accumulation
        ),
        "explainability_visibility": tuple(
            record.deterministic_order
            for record in intelligence.explainability_visibility
        ),
        "cross_boundary_visibility": tuple(
            record.deterministic_order for record in intelligence.cross_boundary_visibility
        ),
        "diagnostics": tuple(
            record.deterministic_order for record in intelligence.diagnostics
        ),
        "unsupported_propagation_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_propagation_visibility
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


def validate_propagation_identity_integrity(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    propagation_ids = [record.propagation_id for record in intelligence.propagation_chains]
    propagation_id_set = set(propagation_ids)
    classification_ids = {record.propagation_id for record in intelligence.classifications}
    continuity_ids = {record.propagation_id for record in intelligence.continuity_records}
    missing_fields = [
        record.propagation_id
        for record in intelligence.propagation_chains
        if not all(
            (
                record.propagation_id,
                record.source_drift_id,
                record.inherited_drift_id,
                record.refinement_drift_id,
                record.propagation_chain_id,
                record.propagation_scope_id,
                record.continuity_reference_id,
                record.lineage_reference_id,
            )
        )
    ]
    duplicate_propagation_ids = sorted(
        {item for item in propagation_ids if propagation_ids.count(item) > 1}
    )
    missing_classification_ids = sorted(propagation_id_set - classification_ids)
    unknown_classification_ids = sorted(classification_ids - propagation_id_set)
    missing_continuity_ids = sorted(propagation_id_set - continuity_ids)
    observed_types = {record.propagation_type for record in intelligence.propagation_chains}
    missing_propagation_types = sorted(set(PROPAGATION_CHAIN_TYPES) - observed_types)
    unknown_propagation_types = sorted(observed_types - set(PROPAGATION_CHAIN_TYPES))
    return {
        "valid": not (
            missing_fields
            or duplicate_propagation_ids
            or missing_classification_ids
            or unknown_classification_ids
            or missing_continuity_ids
            or missing_propagation_types
            or unknown_propagation_types
        ),
        "propagation_chain_count": len(propagation_ids),
        "classification_count": len(intelligence.classifications),
        "missing_fields": missing_fields,
        "duplicate_propagation_ids": duplicate_propagation_ids,
        "missing_classification_ids": missing_classification_ids,
        "unknown_classification_ids": unknown_classification_ids,
        "missing_continuity_ids": missing_continuity_ids,
        "missing_propagation_types": missing_propagation_types,
        "unknown_propagation_types": unknown_propagation_types,
    }


def validate_propagation_lineage_continuity(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    chain_ids = {record.propagation_chain_id for record in intelligence.propagation_chains}
    continuity_chain_ids = {
        record.propagation_chain_id for record in intelligence.continuity_records
    }
    lineage_reference_ids = {
        record.lineage_reference_id for record in intelligence.propagation_chains
    }
    continuity_lineage_ids = {
        record.lineage_reference_id for record in intelligence.continuity_records
    }
    missing_chain_ids = sorted(chain_ids - continuity_chain_ids)
    missing_lineage_ids = sorted(lineage_reference_ids - continuity_lineage_ids)
    unsafe_continuity_ids = sorted(
        record.continuity_id
        for record in intelligence.continuity_records
        if not (
            record.continuity_preserved
            and record.replay_safe
            and record.rollback_safe
            and record.lineage_safe
            and record.provenance_safe
            and record.integrity_safe
            and record.descriptive_only
            and not record.repair_enabled
            and not record.remediation_enabled
            and not record.propagation_correction_enabled
            and not record.runtime_mutation_enabled
        )
    )
    return {
        "valid": not (missing_chain_ids or missing_lineage_ids or unsafe_continuity_ids),
        "continuity_record_count": len(intelligence.continuity_records),
        "missing_chain_ids": missing_chain_ids,
        "missing_lineage_ids": missing_lineage_ids,
        "unsafe_continuity_ids": unsafe_continuity_ids,
        "lineage_continuity_preserved": not missing_lineage_ids,
        "provenance_continuity_preserved": all(
            record.provenance_safe for record in intelligence.continuity_records
        ),
    }


def validate_propagation_evidence_continuity(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    propagation_ids = {record.propagation_id for record in intelligence.propagation_chains}
    evidence_ids = {record.evidence_id for record in intelligence.evidence_chains}
    evidence_by_propagation: dict[str, list[str]] = {
        propagation_id: [] for propagation_id in propagation_ids
    }
    for record in intelligence.evidence_chains:
        evidence_by_propagation.setdefault(record.propagation_id, []).append(record.evidence_id)
    diagnostic_evidence_ids = {
        evidence_id
        for record in intelligence.diagnostics
        for evidence_id in record.evidence_reference_ids
    }
    explainability_evidence_ids = {
        evidence_id
        for record in intelligence.explainability_visibility
        for evidence_id in record.evidence_reference_ids
    }
    unsupported_evidence_ids = {
        evidence_id
        for record in intelligence.unsupported_propagation_visibility
        for evidence_id in record.evidence_reference_ids
    }
    missing_evidence_propagation_ids = sorted(
        propagation_id
        for propagation_id in propagation_ids
        if not evidence_by_propagation.get(propagation_id)
    )
    unknown_evidence_propagation_ids = sorted(set(evidence_by_propagation) - propagation_ids)
    missing_diagnostic_evidence_ids = sorted(diagnostic_evidence_ids - evidence_ids)
    missing_explainability_evidence_ids = sorted(explainability_evidence_ids - evidence_ids)
    missing_unsupported_evidence_ids = sorted(unsupported_evidence_ids - evidence_ids)
    missing_evidence_types = sorted(
        set(PROPAGATION_EVIDENCE_TYPES)
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
            missing_evidence_propagation_ids
            or unknown_evidence_propagation_ids
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
        "missing_evidence_propagation_ids": missing_evidence_propagation_ids,
        "unknown_evidence_propagation_ids": unknown_evidence_propagation_ids,
        "missing_diagnostic_evidence_ids": missing_diagnostic_evidence_ids,
        "missing_explainability_evidence_ids": missing_explainability_evidence_ids,
        "missing_unsupported_evidence_ids": missing_unsupported_evidence_ids,
        "missing_evidence_types": missing_evidence_types,
        "unsafe_evidence_ids": unsafe_evidence_ids,
    }


def validate_propagation_serialization_and_hashing(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    rebuilt = build_v4_5a_2_drift_propagation_intelligence()
    serialized = serialize_v4_5a_2_drift_propagation_intelligence(intelligence)
    rebuilt_serialized = serialize_v4_5a_2_drift_propagation_intelligence(rebuilt)
    propagation_hash = hash_v4_5a_2_drift_propagation_intelligence(intelligence)
    rebuilt_hash = hash_v4_5a_2_drift_propagation_intelligence(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and propagation_hash == rebuilt_hash,
        "serialization_stable": serialized == rebuilt_serialized,
        "hashing_stable": propagation_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "propagation_hash": propagation_hash,
        "rebuilt_propagation_hash": rebuilt_hash,
    }


def validate_fail_visible_unsupported_propagation_visibility(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    observed_diagnostic_types = {record.diagnostic_type for record in intelligence.diagnostics}
    observed_unsupported_states = {
        record.unsupported_state for record in intelligence.unsupported_propagation_visibility
    }
    missing_diagnostic_types = sorted(set(PROPAGATION_DIAGNOSTIC_TYPES) - observed_diagnostic_types)
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_PROPAGATION_OPERATIONAL_STATES) - observed_unsupported_states
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
            and not record.propagation_correction_enabled
            and not record.orchestration_response_enabled
            and not record.authorization_behavior_enabled
        )
    )
    unsafe_unsupported_state_ids = sorted(
        record.state_id
        for record in intelligence.unsupported_propagation_visibility
        if not (
            record.fail_visible
            and record.descriptive_only
            and not record.operational_enabled
            and not record.remediation_enabled
            and not record.repair_enabled
            and not record.mitigation_enabled
            and not record.propagation_suppression_enabled
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
        "unsupported_state_count": len(intelligence.unsupported_propagation_visibility),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_state_ids": unsafe_unsupported_state_ids,
        "fail_visible": all(record.fail_visible for record in intelligence.diagnostics)
        and all(record.fail_visible for record in intelligence.unsupported_propagation_visibility),
        "silent_suppression_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.silent_suppression_enabled
        ),
        "remediation_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.remediation_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_propagation_visibility
            if record.remediation_enabled
        ),
    }


def validate_propagation_explainability_and_cross_boundary_visibility(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    observed_explainability_types = {
        record.explainability_type for record in intelligence.explainability_visibility
    }
    observed_boundary_types = {
        record.boundary_type for record in intelligence.cross_boundary_visibility
    }
    missing_explainability_types = sorted(
        set(PROPAGATION_EXPLAINABILITY_TYPES) - observed_explainability_types
    )
    missing_cross_boundary_types = sorted(
        set(CROSS_BOUNDARY_PROPAGATION_TYPES) - observed_boundary_types
    )
    unsafe_explainability_ids = sorted(
        record.explainability_id
        for record in intelligence.explainability_visibility
        if not (
            record.explainability_first
            and record.descriptive_only
            and not record.operational_response_enabled
            and not record.recommendation_enabled
            and not record.decision_enabled
        )
    )
    unsafe_cross_boundary_ids = sorted(
        record.cross_boundary_id
        for record in intelligence.cross_boundary_visibility
        if not (
            record.descriptive_only
            and record.no_runtime_traversal
            and record.no_orchestration_semantics
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
        "explainability_count": len(intelligence.explainability_visibility),
        "cross_boundary_count": len(intelligence.cross_boundary_visibility),
        "missing_explainability_types": missing_explainability_types,
        "missing_cross_boundary_types": missing_cross_boundary_types,
        "unsafe_explainability_ids": unsafe_explainability_ids,
        "unsafe_cross_boundary_ids": unsafe_cross_boundary_ids,
    }


def validate_descriptive_only_propagation_guarantees(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    counters = drift_propagation_capability_counter_values(intelligence)
    enabled_flags = enabled_drift_propagation_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "propagation_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "propagation_foundation_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5A_2_DRIFT_PROPAGATION_DISABLED_COUNTER_NAMES) - set(counters)
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


def validate_v4_5a_2_drift_propagation_intelligence(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_propagation_ordering_stability(intelligence),
        "identity_integrity": validate_propagation_identity_integrity(intelligence),
        "lineage_continuity": validate_propagation_lineage_continuity(intelligence),
        "evidence_continuity": validate_propagation_evidence_continuity(intelligence),
        "serialization_hashing": validate_propagation_serialization_and_hashing(
            intelligence
        ),
        "required_visibility": validate_required_propagation_visibility(intelligence),
        "explainability_cross_boundary": validate_propagation_explainability_and_cross_boundary_visibility(
            intelligence
        ),
        "fail_visible_unsupported_propagation": validate_fail_visible_unsupported_propagation_visibility(
            intelligence
        ),
        "descriptive_only_guarantees": validate_descriptive_only_propagation_guarantees(
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


def build_v4_5a_2_drift_propagation_intelligence_report() -> dict[str, Any]:
    intelligence = build_v4_5a_2_drift_propagation_intelligence()
    exported = export_v4_5a_2_drift_propagation_intelligence(intelligence)
    validation = validate_v4_5a_2_drift_propagation_intelligence(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    lineage_continuity = validation["validations"]["lineage_continuity"]
    evidence_continuity = validation["validations"]["evidence_continuity"]
    fail_visible = validation["validations"]["fail_visible_unsupported_propagation"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    explainability = validation["validations"]["explainability_cross_boundary"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "propagation_identity_hash": hash_drift_propagation_identity(
            intelligence.propagation_identity
        ),
        "propagation_intelligence_hash": hash_v4_5a_2_drift_propagation_intelligence(
            intelligence
        ),
        "propagation_chain_hashes": {
            record.propagation_id: hash_propagation_chain(record)
            for record in sorted(
                intelligence.propagation_chains,
                key=lambda item: (item.deterministic_order, item.propagation_id),
            )
        },
        "classification_hashes": {
            record.classification_id: hash_propagation_classification(record)
            for record in sorted(
                intelligence.classifications,
                key=lambda item: (item.deterministic_order, item.classification_id),
            )
        },
        "evidence_chain_hashes": {
            record.evidence_id: hash_propagation_evidence_chain(record)
            for record in sorted(
                intelligence.evidence_chains,
                key=lambda item: (item.deterministic_order, item.evidence_id),
            )
        },
        "continuity_hashes": {
            record.continuity_id: hash_propagation_continuity(record)
            for record in sorted(
                intelligence.continuity_records,
                key=lambda item: (item.deterministic_order, item.continuity_id),
            )
        },
        "severity_accumulation_hashes": {
            record.severity_id: hash_propagation_severity_accumulation(record)
            for record in sorted(
                intelligence.severity_accumulation,
                key=lambda item: (item.deterministic_order, item.severity_id),
            )
        },
        "explainability_hashes": {
            record.explainability_id: hash_propagation_explainability(record)
            for record in sorted(
                intelligence.explainability_visibility,
                key=lambda item: (item.deterministic_order, item.explainability_id),
            )
        },
        "cross_boundary_hashes": {
            record.cross_boundary_id: hash_cross_boundary_propagation(record)
            for record in sorted(
                intelligence.cross_boundary_visibility,
                key=lambda item: (item.deterministic_order, item.cross_boundary_id),
            )
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_propagation_diagnostic(record)
            for record in sorted(
                intelligence.diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_state_hashes": {
            record.state_id: hash_unsupported_propagation_visibility(record)
            for record in sorted(
                intelligence.unsupported_propagation_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "propagation_chain_count": len(intelligence.propagation_chains),
        "propagation_classification_count": len(intelligence.classifications),
        "propagation_evidence_chain_count": len(intelligence.evidence_chains),
        "propagation_continuity_count": len(intelligence.continuity_records),
        "propagation_severity_accumulation_count": len(intelligence.severity_accumulation),
        "propagation_explainability_count": len(intelligence.explainability_visibility),
        "cross_boundary_visibility_count": len(intelligence.cross_boundary_visibility),
        "propagation_diagnostic_count": len(intelligence.diagnostics),
        "unsupported_propagation_state_count": len(
            intelligence.unsupported_propagation_visibility
        ),
        "propagation_type_counts": required_visibility["propagation_counts"],
        "accumulation_type_counts": required_visibility["accumulation_counts"],
        "evidence_type_counts": required_visibility["evidence_counts"],
        "explainability_type_counts": required_visibility["explainability_counts"],
        "cross_boundary_type_counts": required_visibility["cross_boundary_counts"],
        "diagnostic_type_counts": required_visibility["diagnostic_counts"],
        "unsupported_state_counts": required_visibility["unsupported_state_counts"],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "lineage_continuity_preserved": lineage_continuity[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_continuity[
            "provenance_continuity_preserved"
        ],
        "replay_safe_evidence_verified": evidence_continuity[
            "replay_safe_evidence_count"
        ]
        == len(intelligence.evidence_chains),
        "provenance_safe_evidence_verified": evidence_continuity[
            "provenance_safe_evidence_count"
        ]
        == len(intelligence.evidence_chains),
        "propagation_explainability_verified": explainability["valid"],
        "fail_visible_unsupported_propagation_verified": fail_visible["valid"],
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
        "propagation_summaries": propagation_summary_visibility(intelligence),
        "propagation_severity_summaries": propagation_severity_summary_visibility(
            intelligence.severity_accumulation
        ),
        "propagation_continuity_summaries": propagation_continuity_summary_visibility(
            intelligence.continuity_records
        ),
        "propagation_explainability_summaries": propagation_explainability_summary_visibility(
            intelligence.explainability_visibility
        ),
        "propagation_evidence_summaries": propagation_evidence_summary_visibility(
            intelligence.evidence_chains
        ),
        "cross_boundary_propagation_summaries": cross_boundary_propagation_summary_visibility(
            intelligence.cross_boundary_visibility
        ),
        "fail_visible_propagation_diagnostics": fail_visible_propagation_diagnostic_summaries(
            intelligence.diagnostics
        ),
        "unsupported_propagation_visibility": unsupported_propagation_visibility_summaries(
            intelligence.unsupported_propagation_visibility
        ),
        "descriptive_only_summary": descriptive_only_propagation_summary(intelligence),
    }
    report_without_hash = {
        "schema_version": V4_5A_2_DRIFT_PROPAGATION_REPORT_SCHEMA_VERSION,
        "phase_id": V4_5A_2_DRIFT_PROPAGATION_PHASE_ID,
        "generated_at": V4_5A_2_DRIFT_PROPAGATION_GENERATED_AT,
        "purpose": V4_5A_2_DRIFT_PROPAGATION_PURPOSE,
        "foundation_status": (
            V4_5A_2_DRIFT_PROPAGATION_STATUS_STABLE
            if validation["valid"]
            else V4_5A_2_DRIFT_PROPAGATION_STATUS_BLOCKED
        ),
        "summary": summary,
        "visibility": visibility,
        "validation": validation,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "drift_propagation_intelligence": exported,
    }
    return {
        **report_without_hash,
        "deterministic_report_hash": deterministic_v4_5a_2_drift_propagation_hash(
            report_without_hash
        ),
    }


def contaminate_v4_5a_2_drift_propagation_for_non_operational_validation(
    intelligence: DriftPropagationIntelligence,
) -> DriftPropagationIntelligence:
    contaminated_chain = replace(
        intelligence.propagation_chains[0],
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
        intelligence.unsupported_propagation_visibility[0],
        operational_enabled=True,
        propagation_suppression_enabled=True,
        authorization_enabled=True,
    )
    return replace(
        intelligence,
        propagation_chains=(contaminated_chain,) + intelligence.propagation_chains[1:],
        diagnostics=(contaminated_diagnostic,) + intelligence.diagnostics[1:],
        unsupported_propagation_visibility=(contaminated_state,)
        + intelligence.unsupported_propagation_visibility[1:],
        orchestration_authorization_enabled=True,
        remediation_enabled=True,
        propagation_suppression_enabled=True,
        runtime_mutation_enabled=True,
    )
