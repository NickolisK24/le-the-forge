"""Audit for deterministic v4.5A.4 drift explainability intelligence.

The audit validates descriptive drift explainability intelligence only. It does
not execute, authorize, approve, dispatch, route, traverse, schedule, sequence,
decide, recommend, rank, act, remediate, repair, mitigate, correct, integrate
planners, consume production bundles, or mutate runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_5a_4_drift_explainability_hashing import (
    deterministic_v4_5a_4_drift_explainability_hash,
    hash_drift_cause_visibility,
    hash_drift_explainability_identity,
    hash_evidence_explanation_mapping,
    hash_explanation_completeness_visibility,
    hash_explanation_confidence_visibility,
    hash_explanation_diagnostic,
    hash_explanation_record,
    hash_integrity_degradation_explanation,
    hash_propagation_explanation_chain,
    hash_unsupported_explanation_visibility,
    hash_v4_5a_4_drift_explainability_intelligence,
)
from .v4_5a_4_drift_explainability_models import (
    DEGRADATION_EXPLANATION_TYPES,
    DRIFT_CAUSE_TYPES,
    EVIDENCE_MAPPING_TYPES,
    EXPLANATION_COMPLETENESS_TYPES,
    EXPLANATION_CONFIDENCE_TYPES,
    EXPLANATION_DIAGNOSTIC_TYPES,
    PROPAGATION_EXPLANATION_TYPES,
    UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
    V4_5A_4_DRIFT_EXPLAINABILITY_DISABLED_COUNTER_NAMES,
    V4_5A_4_DRIFT_EXPLAINABILITY_GENERATED_AT,
    V4_5A_4_DRIFT_EXPLAINABILITY_PHASE_ID,
    V4_5A_4_DRIFT_EXPLAINABILITY_PURPOSE,
    V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_SCHEMA_VERSION,
    V4_5A_4_DRIFT_EXPLAINABILITY_STATUS_BLOCKED,
    V4_5A_4_DRIFT_EXPLAINABILITY_STATUS_STABLE,
    DriftExplainabilityIntelligence,
    default_v4_5a_4_drift_explainability_intelligence,
)
from .v4_5a_4_drift_explainability_serialization import (
    export_v4_5a_4_drift_explainability_intelligence,
    serialize_v4_5a_4_drift_explainability_intelligence,
)
from .v4_5a_4_drift_explainability_visibility import (
    cause_summary_visibility,
    completeness_summary_visibility,
    confidence_summary_visibility,
    degradation_explanation_summary_visibility,
    descriptive_only_explanation_summary,
    evidence_mapping_summary_visibility,
    explanation_summary_visibility,
    fail_visible_explanation_diagnostic_summaries,
    propagation_explanation_summary_visibility,
    unsupported_explanation_visibility_summaries,
    validate_required_explanation_visibility,
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
        "correction_enabled",
    ),
    "enabled_explanation_action_count": (
        "explanation_action_enabled",
        "action_enabled",
    ),
    "enabled_explanation_ranking_count": (
        "explanation_ranking_enabled",
        "ranking_enabled",
        "scoring_enabled",
    ),
    "enabled_explanation_authorization_count": (
        "explanation_authorization_enabled",
        "authorization_enabled",
    ),
    "enabled_explanation_decision_count": ("explanation_decision_enabled",),
    "enabled_explanation_recommendation_count": (
        "explanation_recommendation_enabled",
        "recommendation_enabled",
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


def build_v4_5a_4_drift_explainability_intelligence() -> DriftExplainabilityIntelligence:
    return default_v4_5a_4_drift_explainability_intelligence()


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


def enabled_drift_explainability_capability_flags(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "explanation_id", None)
            or getattr(item, "cause_id", None)
            or getattr(item, "propagation_explanation_id", None)
            or getattr(item, "degradation_explanation_id", None)
            or getattr(item, "mapping_id", None)
            or getattr(item, "completeness_id", None)
            or getattr(item, "confidence_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "drift_explainability_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def drift_explainability_capability_counter_values(
    intelligence: DriftExplainabilityIntelligence,
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


def drift_explainability_equal(
    left: DriftExplainabilityIntelligence,
    right: DriftExplainabilityIntelligence,
) -> bool:
    return serialize_v4_5a_4_drift_explainability_intelligence(
        left
    ) == serialize_v4_5a_4_drift_explainability_intelligence(right)


def validate_explanation_ordering_stability(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "explanation_records": tuple(
            record.deterministic_order for record in intelligence.explanation_records
        ),
        "cause_visibility": tuple(
            record.deterministic_order for record in intelligence.cause_visibility
        ),
        "propagation_explanations": tuple(
            record.deterministic_order
            for record in intelligence.propagation_explanations
        ),
        "degradation_explanations": tuple(
            record.deterministic_order
            for record in intelligence.degradation_explanations
        ),
        "evidence_mappings": tuple(
            record.deterministic_order for record in intelligence.evidence_mappings
        ),
        "completeness_visibility": tuple(
            record.deterministic_order
            for record in intelligence.completeness_visibility
        ),
        "confidence_visibility": tuple(
            record.deterministic_order for record in intelligence.confidence_visibility
        ),
        "diagnostics": tuple(
            record.deterministic_order for record in intelligence.diagnostics
        ),
        "unsupported_explanation_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_explanation_visibility
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


def validate_explanation_identity_integrity(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    explanation_ids = [record.explanation_id for record in intelligence.explanation_records]
    explanation_id_set = set(explanation_ids)
    cause_explanation_ids = {record.explanation_id for record in intelligence.cause_visibility}
    missing_fields = [
        record.explanation_id
        for record in intelligence.explanation_records
        if not all(
            (
                record.explanation_id,
                record.explanation_chain_id,
                record.source_drift_id,
                record.propagation_chain_id,
                record.degradation_chain_id,
                record.evidence_chain_id,
                record.continuity_reference_id,
                record.lineage_reference_id,
                record.provenance_reference_id,
            )
        )
    ]
    duplicate_explanation_ids = sorted(
        {item for item in explanation_ids if explanation_ids.count(item) > 1}
    )
    missing_cause_explanation_ids = sorted(explanation_id_set - cause_explanation_ids)
    unknown_cause_explanation_ids = sorted(cause_explanation_ids - explanation_id_set)
    observed_cause_types = {record.cause_type for record in intelligence.cause_visibility}
    missing_cause_types = sorted(set(DRIFT_CAUSE_TYPES) - observed_cause_types)
    unknown_cause_types = sorted(observed_cause_types - set(DRIFT_CAUSE_TYPES))
    return {
        "valid": not (
            missing_fields
            or duplicate_explanation_ids
            or missing_cause_explanation_ids
            or unknown_cause_explanation_ids
            or missing_cause_types
            or unknown_cause_types
        ),
        "explanation_record_count": len(explanation_ids),
        "cause_visibility_count": len(intelligence.cause_visibility),
        "missing_fields": missing_fields,
        "duplicate_explanation_ids": duplicate_explanation_ids,
        "missing_cause_explanation_ids": missing_cause_explanation_ids,
        "unknown_cause_explanation_ids": unknown_cause_explanation_ids,
        "missing_cause_types": missing_cause_types,
        "unknown_cause_types": unknown_cause_types,
    }


def validate_explanation_chain_continuity(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    explanation_ids = {record.explanation_id for record in intelligence.explanation_records}
    mapping_ids = {record.mapping_id for record in intelligence.evidence_mappings}
    chain_lineage_ids = {
        record.lineage_reference_id for record in intelligence.explanation_records
    }
    chain_provenance_ids = {
        record.provenance_reference_id for record in intelligence.explanation_records
    }
    referenced_mapping_ids = {
        mapping_id
        for record in (
            tuple(intelligence.propagation_explanations)
            + tuple(intelligence.degradation_explanations)
            + tuple(intelligence.completeness_visibility)
            + tuple(intelligence.confidence_visibility)
        )
        for mapping_id in record.evidence_reference_ids
    }
    unknown_referenced_mapping_ids = sorted(referenced_mapping_ids - mapping_ids)
    related_explanation_ids = (
        {record.explanation_id for record in intelligence.propagation_explanations}
        | {record.explanation_id for record in intelligence.degradation_explanations}
        | {record.explanation_id for record in intelligence.completeness_visibility}
        | {record.explanation_id for record in intelligence.confidence_visibility}
    )
    unknown_related_explanation_ids = sorted(related_explanation_ids - explanation_ids)
    unsafe_chain_ids = sorted(
        record.explanation_id
        for record in intelligence.explanation_records
        if not (
            record.replay_safe
            and record.rollback_safe
            and record.lineage_safe
            and record.provenance_safe
            and record.integrity_safe
            and record.explainability_first
            and record.descriptive_only
            and not record.explanation_action_enabled
            and not record.explanation_ranking_enabled
            and not record.runtime_execution_enabled
            and not record.operational_mutation_enabled
        )
    )
    return {
        "valid": not (
            unknown_referenced_mapping_ids
            or unknown_related_explanation_ids
            or unsafe_chain_ids
        ),
        "unknown_referenced_mapping_ids": unknown_referenced_mapping_ids,
        "unknown_related_explanation_ids": unknown_related_explanation_ids,
        "unsafe_chain_ids": unsafe_chain_ids,
        "lineage_continuity_preserved": bool(chain_lineage_ids)
        and all(record.lineage_safe for record in intelligence.explanation_records),
        "provenance_continuity_preserved": bool(chain_provenance_ids)
        and all(record.provenance_safe for record in intelligence.explanation_records),
        "explanation_chain_count": len(intelligence.explanation_records),
    }


def validate_evidence_to_explanation_continuity(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    explanation_ids = {record.explanation_id for record in intelligence.explanation_records}
    mapping_ids = {record.mapping_id for record in intelligence.evidence_mappings}
    diagnostic_mapping_ids = {
        mapping_id
        for record in intelligence.diagnostics
        for mapping_id in record.evidence_reference_ids
    }
    unsupported_mapping_ids = {
        mapping_id
        for record in intelligence.unsupported_explanation_visibility
        for mapping_id in record.evidence_reference_ids
    }
    unknown_mapping_explanation_ids = sorted(
        {record.explanation_id for record in intelligence.evidence_mappings}
        - explanation_ids
    )
    missing_diagnostic_mapping_ids = sorted(diagnostic_mapping_ids - mapping_ids)
    missing_unsupported_mapping_ids = sorted(unsupported_mapping_ids - mapping_ids)
    missing_evidence_types = sorted(
        set(EVIDENCE_MAPPING_TYPES)
        - {record.evidence_type for record in intelligence.evidence_mappings}
    )
    unsafe_mapping_ids = sorted(
        record.mapping_id
        for record in intelligence.evidence_mappings
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
            unknown_mapping_explanation_ids
            or missing_diagnostic_mapping_ids
            or missing_unsupported_mapping_ids
            or missing_evidence_types
            or unsafe_mapping_ids
        ),
        "evidence_mapping_count": len(intelligence.evidence_mappings),
        "replay_safe_mapping_count": sum(
            1 for record in intelligence.evidence_mappings if record.replay_safe
        ),
        "provenance_safe_mapping_count": sum(
            1 for record in intelligence.evidence_mappings if record.provenance_safe
        ),
        "lineage_safe_mapping_count": sum(
            1 for record in intelligence.evidence_mappings if record.lineage_safe
        ),
        "unknown_mapping_explanation_ids": unknown_mapping_explanation_ids,
        "missing_diagnostic_mapping_ids": missing_diagnostic_mapping_ids,
        "missing_unsupported_mapping_ids": missing_unsupported_mapping_ids,
        "missing_evidence_types": missing_evidence_types,
        "unsafe_mapping_ids": unsafe_mapping_ids,
    }


def validate_explanation_serialization_and_hashing(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    rebuilt = build_v4_5a_4_drift_explainability_intelligence()
    serialized = serialize_v4_5a_4_drift_explainability_intelligence(intelligence)
    rebuilt_serialized = serialize_v4_5a_4_drift_explainability_intelligence(rebuilt)
    explanation_hash = hash_v4_5a_4_drift_explainability_intelligence(intelligence)
    rebuilt_hash = hash_v4_5a_4_drift_explainability_intelligence(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and explanation_hash == rebuilt_hash,
        "serialization_stable": serialized == rebuilt_serialized,
        "hashing_stable": explanation_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "explanation_hash": explanation_hash,
        "rebuilt_explanation_hash": rebuilt_hash,
    }


def validate_explanation_visibility_integrity(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    missing_propagation_types = sorted(
        set(PROPAGATION_EXPLANATION_TYPES)
        - {record.propagation_type for record in intelligence.propagation_explanations}
    )
    missing_degradation_types = sorted(
        set(DEGRADATION_EXPLANATION_TYPES)
        - {record.degradation_type for record in intelligence.degradation_explanations}
    )
    missing_completeness_types = sorted(
        set(EXPLANATION_COMPLETENESS_TYPES)
        - {record.completeness_type for record in intelligence.completeness_visibility}
    )
    missing_confidence_types = sorted(
        set(EXPLANATION_CONFIDENCE_TYPES)
        - {record.confidence_type for record in intelligence.confidence_visibility}
    )
    unsafe_propagation_ids = sorted(
        record.propagation_explanation_id
        for record in intelligence.propagation_explanations
        if not (
            record.descriptive_only
            and record.replay_safe
            and record.provenance_safe
            and record.lineage_safe
            and not record.correction_enabled
            and not record.suppression_enabled
            and not record.mitigation_enabled
            and not record.orchestration_response_enabled
            and not record.recommendation_enabled
        )
    )
    unsafe_degradation_ids = sorted(
        record.degradation_explanation_id
        for record in intelligence.degradation_explanations
        if not (
            record.descriptive_only
            and record.replay_safe
            and record.provenance_safe
            and record.lineage_safe
            and record.integrity_safe
            and not record.remediation_enabled
            and not record.repair_enabled
            and not record.mitigation_enabled
            and not record.correction_enabled
            and not record.orchestration_response_enabled
        )
    )
    unsafe_completeness_ids = sorted(
        record.completeness_id
        for record in intelligence.completeness_visibility
        if not (
            record.descriptive_only
            and record.non_scoring
            and record.non_ranking
            and record.non_authorizing
            and not record.scoring_enabled
            and not record.ranking_enabled
            and not record.authorization_enabled
            and not record.recommendation_enabled
        )
    )
    unsafe_confidence_ids = sorted(
        record.confidence_id
        for record in intelligence.confidence_visibility
        if not (
            record.descriptive_only
            and record.non_authorizing
            and record.non_ranking
            and record.non_recommending
            and not record.authorization_enabled
            and not record.ranking_enabled
            and not record.recommendation_enabled
            and not record.execution_enabled
            and not record.suppression_enabled
        )
    )
    return {
        "valid": not (
            missing_propagation_types
            or missing_degradation_types
            or missing_completeness_types
            or missing_confidence_types
            or unsafe_propagation_ids
            or unsafe_degradation_ids
            or unsafe_completeness_ids
            or unsafe_confidence_ids
        ),
        "missing_propagation_types": missing_propagation_types,
        "missing_degradation_types": missing_degradation_types,
        "missing_completeness_types": missing_completeness_types,
        "missing_confidence_types": missing_confidence_types,
        "unsafe_propagation_ids": unsafe_propagation_ids,
        "unsafe_degradation_ids": unsafe_degradation_ids,
        "unsafe_completeness_ids": unsafe_completeness_ids,
        "unsafe_confidence_ids": unsafe_confidence_ids,
    }


def validate_fail_visible_unsupported_explanation_visibility(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    observed_diagnostic_types = {record.diagnostic_type for record in intelligence.diagnostics}
    observed_unsupported_states = {
        record.unsupported_state for record in intelligence.unsupported_explanation_visibility
    }
    missing_diagnostic_types = sorted(set(EXPLANATION_DIAGNOSTIC_TYPES) - observed_diagnostic_types)
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES) - observed_unsupported_states
    )
    unsafe_diagnostic_ids = sorted(
        record.diagnostic_id
        for record in intelligence.diagnostics
        if not (
            record.fail_visible
            and record.descriptive_only
            and not record.hidden_assumption_used
            and not record.silent_fallback_enabled
            and not record.remediation_enabled
            and not record.repair_enabled
            and not record.mitigation_enabled
            and not record.auto_correction_enabled
            and not record.explanation_action_enabled
            and not record.explanation_ranking_enabled
            and not record.explanation_authorization_enabled
            and not record.orchestration_response_enabled
        )
    )
    unsafe_unsupported_state_ids = sorted(
        record.state_id
        for record in intelligence.unsupported_explanation_visibility
        if not (
            record.fail_visible
            and record.descriptive_only
            and not record.operational_enabled
            and not record.remediation_enabled
            and not record.repair_enabled
            and not record.mitigation_enabled
            and not record.automated_correction_enabled
            and not record.explanation_action_enabled
            and not record.explanation_ranking_enabled
            and not record.explanation_authorization_enabled
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
        "unsupported_state_count": len(intelligence.unsupported_explanation_visibility),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_state_ids": unsafe_unsupported_state_ids,
        "fail_visible": all(record.fail_visible for record in intelligence.diagnostics)
        and all(record.fail_visible for record in intelligence.unsupported_explanation_visibility),
        "silent_fallback_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.silent_fallback_enabled
        ),
        "remediation_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.remediation_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_explanation_visibility
            if record.remediation_enabled
        ),
        "explanation_action_enabled_count": sum(
            1 for record in intelligence.diagnostics if record.explanation_action_enabled
        )
        + sum(
            1
            for record in intelligence.unsupported_explanation_visibility
            if record.explanation_action_enabled
        ),
    }


def validate_descriptive_only_explanation_guarantees(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    counters = drift_explainability_capability_counter_values(intelligence)
    enabled_flags = enabled_drift_explainability_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "explanation_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "drift_explainability_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5A_4_DRIFT_EXPLAINABILITY_DISABLED_COUNTER_NAMES) - set(counters)
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


def validate_v4_5a_4_drift_explainability_intelligence(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_explanation_ordering_stability(intelligence),
        "identity_integrity": validate_explanation_identity_integrity(intelligence),
        "chain_continuity": validate_explanation_chain_continuity(intelligence),
        "evidence_to_explanation": validate_evidence_to_explanation_continuity(
            intelligence
        ),
        "serialization_hashing": validate_explanation_serialization_and_hashing(
            intelligence
        ),
        "required_visibility": validate_required_explanation_visibility(intelligence),
        "explanation_visibility_integrity": validate_explanation_visibility_integrity(
            intelligence
        ),
        "fail_visible_unsupported_explanation": validate_fail_visible_unsupported_explanation_visibility(
            intelligence
        ),
        "descriptive_only_guarantees": validate_descriptive_only_explanation_guarantees(
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


def build_v4_5a_4_drift_explainability_intelligence_report() -> dict[str, Any]:
    intelligence = build_v4_5a_4_drift_explainability_intelligence()
    exported = export_v4_5a_4_drift_explainability_intelligence(intelligence)
    validation = validate_v4_5a_4_drift_explainability_intelligence(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    chain_continuity = validation["validations"]["chain_continuity"]
    evidence_continuity = validation["validations"]["evidence_to_explanation"]
    fail_visible = validation["validations"]["fail_visible_unsupported_explanation"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    visibility_integrity = validation["validations"]["explanation_visibility_integrity"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "explainability_identity_hash": hash_drift_explainability_identity(
            intelligence.explainability_identity
        ),
        "drift_explainability_intelligence_hash": hash_v4_5a_4_drift_explainability_intelligence(
            intelligence
        ),
        "explanation_record_hashes": {
            record.explanation_id: hash_explanation_record(record)
            for record in sorted(
                intelligence.explanation_records,
                key=lambda item: (item.deterministic_order, item.explanation_id),
            )
        },
        "cause_visibility_hashes": {
            record.cause_id: hash_drift_cause_visibility(record)
            for record in sorted(
                intelligence.cause_visibility,
                key=lambda item: (item.deterministic_order, item.cause_id),
            )
        },
        "propagation_explanation_hashes": {
            record.propagation_explanation_id: hash_propagation_explanation_chain(
                record
            )
            for record in sorted(
                intelligence.propagation_explanations,
                key=lambda item: (item.deterministic_order, item.propagation_explanation_id),
            )
        },
        "degradation_explanation_hashes": {
            record.degradation_explanation_id: hash_integrity_degradation_explanation(
                record
            )
            for record in sorted(
                intelligence.degradation_explanations,
                key=lambda item: (item.deterministic_order, item.degradation_explanation_id),
            )
        },
        "evidence_mapping_hashes": {
            record.mapping_id: hash_evidence_explanation_mapping(record)
            for record in sorted(
                intelligence.evidence_mappings,
                key=lambda item: (item.deterministic_order, item.mapping_id),
            )
        },
        "completeness_hashes": {
            record.completeness_id: hash_explanation_completeness_visibility(record)
            for record in sorted(
                intelligence.completeness_visibility,
                key=lambda item: (item.deterministic_order, item.completeness_id),
            )
        },
        "confidence_hashes": {
            record.confidence_id: hash_explanation_confidence_visibility(record)
            for record in sorted(
                intelligence.confidence_visibility,
                key=lambda item: (item.deterministic_order, item.confidence_id),
            )
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_explanation_diagnostic(record)
            for record in sorted(
                intelligence.diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_state_hashes": {
            record.state_id: hash_unsupported_explanation_visibility(record)
            for record in sorted(
                intelligence.unsupported_explanation_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "explanation_record_count": len(intelligence.explanation_records),
        "cause_visibility_count": len(intelligence.cause_visibility),
        "propagation_explanation_count": len(intelligence.propagation_explanations),
        "degradation_explanation_count": len(intelligence.degradation_explanations),
        "evidence_mapping_count": len(intelligence.evidence_mappings),
        "completeness_visibility_count": len(intelligence.completeness_visibility),
        "confidence_visibility_count": len(intelligence.confidence_visibility),
        "explanation_diagnostic_count": len(intelligence.diagnostics),
        "unsupported_explanation_state_count": len(
            intelligence.unsupported_explanation_visibility
        ),
        "cause_type_counts": required_visibility["cause_counts"],
        "propagation_type_counts": required_visibility["propagation_counts"],
        "degradation_type_counts": required_visibility["degradation_counts"],
        "evidence_type_counts": required_visibility["evidence_counts"],
        "completeness_type_counts": required_visibility["completeness_counts"],
        "confidence_type_counts": required_visibility["confidence_counts"],
        "diagnostic_type_counts": required_visibility["diagnostic_counts"],
        "unsupported_state_counts": required_visibility["unsupported_state_counts"],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "explanation_chain_continuity_preserved": chain_continuity["valid"],
        "lineage_continuity_preserved": chain_continuity[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": chain_continuity[
            "provenance_continuity_preserved"
        ],
        "evidence_to_explanation_mapping_stable": evidence_continuity["valid"],
        "replay_safe_mapping_verified": evidence_continuity[
            "replay_safe_mapping_count"
        ]
        == len(intelligence.evidence_mappings),
        "provenance_safe_mapping_verified": evidence_continuity[
            "provenance_safe_mapping_count"
        ]
        == len(intelligence.evidence_mappings),
        "lineage_safe_mapping_verified": evidence_continuity[
            "lineage_safe_mapping_count"
        ]
        == len(intelligence.evidence_mappings),
        "explanation_visibility_verified": visibility_integrity["valid"],
        "fail_visible_unsupported_explanation_verified": fail_visible["valid"],
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
        "explanation_summaries": explanation_summary_visibility(intelligence),
        "cause_summaries": cause_summary_visibility(intelligence.cause_visibility),
        "propagation_explanation_summaries": propagation_explanation_summary_visibility(
            intelligence.propagation_explanations
        ),
        "degradation_explanation_summaries": degradation_explanation_summary_visibility(
            intelligence.degradation_explanations
        ),
        "evidence_mapping_summaries": evidence_mapping_summary_visibility(
            intelligence.evidence_mappings
        ),
        "completeness_summaries": completeness_summary_visibility(
            intelligence.completeness_visibility
        ),
        "confidence_summaries": confidence_summary_visibility(
            intelligence.confidence_visibility
        ),
        "fail_visible_explanation_diagnostics": fail_visible_explanation_diagnostic_summaries(
            intelligence.diagnostics
        ),
        "unsupported_explanation_visibility": unsupported_explanation_visibility_summaries(
            intelligence.unsupported_explanation_visibility
        ),
        "descriptive_only_summary": descriptive_only_explanation_summary(intelligence),
    }
    report_without_hash = {
        "schema_version": V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_SCHEMA_VERSION,
        "phase_id": V4_5A_4_DRIFT_EXPLAINABILITY_PHASE_ID,
        "generated_at": V4_5A_4_DRIFT_EXPLAINABILITY_GENERATED_AT,
        "purpose": V4_5A_4_DRIFT_EXPLAINABILITY_PURPOSE,
        "foundation_status": (
            V4_5A_4_DRIFT_EXPLAINABILITY_STATUS_STABLE
            if validation["valid"]
            else V4_5A_4_DRIFT_EXPLAINABILITY_STATUS_BLOCKED
        ),
        "summary": summary,
        "visibility": visibility,
        "validation": validation,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "drift_explainability_intelligence": exported,
    }
    return {
        **report_without_hash,
        "deterministic_report_hash": deterministic_v4_5a_4_drift_explainability_hash(
            report_without_hash
        ),
    }


def contaminate_v4_5a_4_drift_explainability_for_non_operational_validation(
    intelligence: DriftExplainabilityIntelligence,
) -> DriftExplainabilityIntelligence:
    contaminated_explanation = replace(
        intelligence.explanation_records[0],
        runtime_execution_enabled=True,
        orchestration_routing_enabled=True,
        explanation_action_enabled=True,
    )
    contaminated_diagnostic = replace(
        intelligence.diagnostics[0],
        remediation_enabled=True,
        mitigation_enabled=True,
        silent_fallback_enabled=True,
        explanation_ranking_enabled=True,
    )
    contaminated_state = replace(
        intelligence.unsupported_explanation_visibility[0],
        operational_enabled=True,
        explanation_action_enabled=True,
        explanation_authorization_enabled=True,
    )
    return replace(
        intelligence,
        explanation_records=(contaminated_explanation,)
        + intelligence.explanation_records[1:],
        diagnostics=(contaminated_diagnostic,) + intelligence.diagnostics[1:],
        unsupported_explanation_visibility=(contaminated_state,)
        + intelligence.unsupported_explanation_visibility[1:],
        orchestration_authorization_enabled=True,
        remediation_enabled=True,
        explanation_ranking_enabled=True,
        runtime_mutation_enabled=True,
    )
