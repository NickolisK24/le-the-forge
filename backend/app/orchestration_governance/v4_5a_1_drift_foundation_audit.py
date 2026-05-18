"""Audit for deterministic v4.5A.1 drift foundations.

This audit verifies governance-safe drift foundation visibility only. It never
executes, authorizes, approves, routes, dispatches, schedules, sequences,
recommends, decides, remediates, repairs, corrects, integrates planners,
consumes production bundles, or mutates runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_5a_1_drift_foundation_hashing import (
    deterministic_v4_5a_1_drift_foundation_hash,
    hash_drift_classification_record,
    hash_drift_continuity_visibility,
    hash_drift_diagnostic_record,
    hash_drift_evidence_reference,
    hash_drift_foundation_identity,
    hash_drift_identity_record,
    hash_drift_severity_visibility,
    hash_unsupported_drift_state_visibility,
    hash_v4_5a_1_drift_foundations,
)
from .v4_5a_1_drift_foundation_models import (
    DRIFT_CLASSIFICATION_CATEGORIES,
    DRIFT_CONTINUITY_LINEAGE,
    DRIFT_CONTINUITY_PROVENANCE,
    DRIFT_CONTINUITY_TYPES,
    DRIFT_DIAGNOSTIC_TYPES,
    DRIFT_EVIDENCE_TYPES,
    DRIFT_SEVERITY_LEVELS,
    UNSUPPORTED_DRIFT_OPERATIONAL_STATES,
    V4_5A_1_DRIFT_FOUNDATION_DISABLED_COUNTER_NAMES,
    V4_5A_1_DRIFT_FOUNDATION_GENERATED_AT,
    V4_5A_1_DRIFT_FOUNDATION_PHASE_ID,
    V4_5A_1_DRIFT_FOUNDATION_PURPOSE,
    V4_5A_1_DRIFT_FOUNDATION_REPORT_SCHEMA_VERSION,
    V4_5A_1_DRIFT_FOUNDATION_STATUS_BLOCKED,
    V4_5A_1_DRIFT_FOUNDATION_STATUS_STABLE,
    DriftFoundationIntelligence,
    default_v4_5a_1_drift_foundations,
)
from .v4_5a_1_drift_foundation_serialization import (
    export_v4_5a_1_drift_foundations,
    serialize_v4_5a_1_drift_foundations,
)
from .v4_5a_1_drift_foundation_visibility import (
    continuity_summary_visibility,
    descriptive_only_visibility_summary,
    drift_summary_visibility,
    evidence_summary_visibility,
    fail_visible_diagnostic_summaries,
    severity_summary_visibility,
    unsupported_state_visibility_summaries,
    validate_required_drift_visibility,
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
    "enabled_orchestration_routing_count": (
        "orchestration_routing_enabled",
        "routing_enabled",
    ),
    "enabled_orchestration_dispatch_count": (
        "orchestration_dispatch_enabled",
        "dispatch_execution_enabled",
        "dispatch_enabled",
    ),
    "enabled_orchestration_scheduling_count": (
        "orchestration_scheduling_enabled",
        "scheduling_execution_enabled",
        "scheduling_enabled",
    ),
    "enabled_orchestration_sequencing_count": (
        "orchestration_sequencing_enabled",
        "sequencing_execution_enabled",
        "sequencing_enabled",
    ),
    "enabled_orchestration_recommendation_count": (
        "orchestration_recommendation_enabled",
        "recommendation_enabled",
    ),
    "enabled_orchestration_decision_count": (
        "orchestration_decision_enabled",
        "decision_enabled",
    ),
    "enabled_remediation_count": (
        "remediation_enabled",
        "auto_remediation_enabled",
    ),
    "enabled_repair_count": (
        "repair_enabled",
    ),
    "enabled_auto_correction_count": (
        "auto_correction_enabled",
        "automated_correction_enabled",
    ),
    "enabled_runtime_mutation_count": (
        "runtime_mutation_enabled",
        "mutation_enabled",
    ),
    "enabled_operational_mutation_count": (
        "operational_mutation_enabled",
    ),
    "enabled_planner_integration_count": (
        "planner_integration_enabled",
    ),
    "enabled_production_consumption_count": (
        "production_consumption_enabled",
    ),
}

PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_5a_1_drift_foundations() -> DriftFoundationIntelligence:
    return default_v4_5a_1_drift_foundations()


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


def enabled_drift_foundation_capability_flags(
    foundations: DriftFoundationIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(foundations):
        item_id = (
            getattr(item, "drift_id", None)
            or getattr(item, "classification_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "continuity_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "severity_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "foundation_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def drift_foundation_capability_counter_values(
    foundations: DriftFoundationIntelligence,
) -> dict[str, int]:
    objects = tuple(_iter_dataclass_objects(foundations))
    counters: dict[str, int] = {}
    for counter_name, field_names in CAPABILITY_COUNTER_FIELD_MAP.items():
        counters[counter_name] = sum(
            1
            for item in objects
            for field_name in field_names
            if bool(getattr(item, field_name, False))
        )
    return counters


def drift_foundations_equal(
    left: DriftFoundationIntelligence,
    right: DriftFoundationIntelligence,
) -> bool:
    return serialize_v4_5a_1_drift_foundations(left) == serialize_v4_5a_1_drift_foundations(right)


def validate_drift_ordering_stability(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "drift_identities": tuple(
            record.deterministic_order for record in foundations.drift_identities
        ),
        "classifications": tuple(
            record.deterministic_order for record in foundations.classifications
        ),
        "evidence_references": tuple(
            record.deterministic_order for record in foundations.evidence_references
        ),
        "continuity_visibility": tuple(
            record.deterministic_order for record in foundations.continuity_visibility
        ),
        "diagnostics": tuple(
            record.deterministic_order for record in foundations.diagnostics
        ),
        "severity_visibility": tuple(
            record.deterministic_order for record in foundations.severity_visibility
        ),
        "unsupported_state_visibility": tuple(
            record.deterministic_order for record in foundations.unsupported_state_visibility
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


def validate_drift_identity_integrity(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    drift_ids = [record.drift_id for record in foundations.drift_identities]
    classification_drift_ids = {record.drift_id for record in foundations.classifications}
    missing_identity_fields = [
        record.drift_id
        for record in foundations.drift_identities
        if not all(
            (
                record.drift_id,
                record.boundary_id,
                record.source_boundary_id,
                record.inherited_boundary_id,
                record.refinement_boundary_id,
                record.governance_scope_id,
                record.continuity_chain_id,
            )
        )
    ]
    duplicate_drift_ids = sorted(
        {drift_id for drift_id in drift_ids if drift_ids.count(drift_id) > 1}
    )
    identity_classification_gaps = sorted(set(drift_ids) - classification_drift_ids)
    unknown_classification_drift_ids = sorted(classification_drift_ids - set(drift_ids))
    observed_categories = {record.category for record in foundations.classifications}
    missing_categories = sorted(set(DRIFT_CLASSIFICATION_CATEGORIES) - observed_categories)
    unknown_categories = sorted(observed_categories - set(DRIFT_CLASSIFICATION_CATEGORIES))
    return {
        "valid": not (
            missing_identity_fields
            or duplicate_drift_ids
            or identity_classification_gaps
            or unknown_classification_drift_ids
            or missing_categories
            or unknown_categories
        ),
        "drift_identity_count": len(drift_ids),
        "classification_count": len(foundations.classifications),
        "missing_identity_fields": missing_identity_fields,
        "duplicate_drift_ids": duplicate_drift_ids,
        "identity_classification_gaps": identity_classification_gaps,
        "unknown_classification_drift_ids": unknown_classification_drift_ids,
        "missing_categories": missing_categories,
        "unknown_categories": unknown_categories,
    }


def validate_drift_evidence_continuity(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    drift_ids = {record.drift_id for record in foundations.drift_identities}
    evidence_by_drift: dict[str, list[str]] = {drift_id: [] for drift_id in drift_ids}
    evidence_ids = {record.evidence_id for record in foundations.evidence_references}
    for record in foundations.evidence_references:
        evidence_by_drift.setdefault(record.drift_id, []).append(record.evidence_id)
    diagnostic_evidence_ids = {
        evidence_id
        for diagnostic in foundations.diagnostics
        for evidence_id in diagnostic.evidence_reference_ids
    }
    unsupported_evidence_ids = {
        evidence_id
        for state in foundations.unsupported_state_visibility
        for evidence_id in state.evidence_reference_ids
    }
    missing_evidence_drift_ids = sorted(
        drift_id for drift_id in drift_ids if not evidence_by_drift.get(drift_id)
    )
    unknown_evidence_drift_ids = sorted(set(evidence_by_drift) - drift_ids)
    missing_diagnostic_evidence_ids = sorted(diagnostic_evidence_ids - evidence_ids)
    missing_unsupported_evidence_ids = sorted(unsupported_evidence_ids - evidence_ids)
    missing_evidence_types = sorted(
        set(DRIFT_EVIDENCE_TYPES)
        - {record.evidence_type for record in foundations.evidence_references}
    )
    unsafe_evidence_ids = sorted(
        record.evidence_id
        for record in foundations.evidence_references
        if not (
            record.replay_safe
            and record.rollback_safe
            and record.provenance_safe
            and record.lineage_safe
            and record.integrity_safe
            and record.descriptive_only
            and not record.hidden_inference_used
            and not record.production_consumption_enabled
            and bool(record.source_hash_reference)
        )
    )
    return {
        "valid": not (
            missing_evidence_drift_ids
            or unknown_evidence_drift_ids
            or missing_diagnostic_evidence_ids
            or missing_unsupported_evidence_ids
            or missing_evidence_types
            or unsafe_evidence_ids
        ),
        "evidence_reference_count": len(foundations.evidence_references),
        "replay_safe_evidence_count": sum(
            1 for record in foundations.evidence_references if record.replay_safe
        ),
        "provenance_safe_evidence_count": sum(
            1 for record in foundations.evidence_references if record.provenance_safe
        ),
        "missing_evidence_drift_ids": missing_evidence_drift_ids,
        "unknown_evidence_drift_ids": unknown_evidence_drift_ids,
        "missing_diagnostic_evidence_ids": missing_diagnostic_evidence_ids,
        "missing_unsupported_evidence_ids": missing_unsupported_evidence_ids,
        "missing_evidence_types": missing_evidence_types,
        "unsafe_evidence_ids": unsafe_evidence_ids,
    }


def validate_drift_lineage_continuity(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    identity_chain_ids = {
        record.continuity_chain_id for record in foundations.drift_identities
    }
    continuity_chain_ids = {
        record.continuity_chain_id for record in foundations.continuity_visibility
    }
    observed_types = {record.continuity_type for record in foundations.continuity_visibility}
    missing_continuity_types = sorted(set(DRIFT_CONTINUITY_TYPES) - observed_types)
    missing_identity_chain_ids = sorted(identity_chain_ids - continuity_chain_ids)
    unsafe_continuity_ids = sorted(
        record.continuity_id
        for record in foundations.continuity_visibility
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
            and not record.runtime_mutation_enabled
        )
    )
    lineage_continuity_visible = any(
        record.continuity_type == DRIFT_CONTINUITY_LINEAGE
        and record.continuity_preserved
        for record in foundations.continuity_visibility
    )
    provenance_continuity_visible = any(
        record.continuity_type == DRIFT_CONTINUITY_PROVENANCE
        and record.continuity_preserved
        for record in foundations.continuity_visibility
    )
    return {
        "valid": not (
            missing_continuity_types
            or missing_identity_chain_ids
            or unsafe_continuity_ids
            or not lineage_continuity_visible
            or not provenance_continuity_visible
        ),
        "continuity_visibility_count": len(foundations.continuity_visibility),
        "missing_continuity_types": missing_continuity_types,
        "missing_identity_chain_ids": missing_identity_chain_ids,
        "unsafe_continuity_ids": unsafe_continuity_ids,
        "lineage_continuity_visible": lineage_continuity_visible,
        "provenance_continuity_visible": provenance_continuity_visible,
        "lineage_continuity_preserved": lineage_continuity_visible,
        "provenance_continuity_preserved": provenance_continuity_visible,
    }


def validate_drift_serialization_and_hashing(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    rebuilt = build_v4_5a_1_drift_foundations()
    serialized = serialize_v4_5a_1_drift_foundations(foundations)
    rebuilt_serialized = serialize_v4_5a_1_drift_foundations(rebuilt)
    foundation_hash = hash_v4_5a_1_drift_foundations(foundations)
    rebuilt_hash = hash_v4_5a_1_drift_foundations(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and foundation_hash == rebuilt_hash,
        "serialization_stable": serialized == rebuilt_serialized,
        "hashing_stable": foundation_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "foundation_hash": foundation_hash,
        "rebuilt_foundation_hash": rebuilt_hash,
    }


def validate_fail_visible_unsupported_state_visibility(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    observed_diagnostic_types = {record.diagnostic_type for record in foundations.diagnostics}
    observed_unsupported_states = {
        record.unsupported_state for record in foundations.unsupported_state_visibility
    }
    missing_diagnostic_types = sorted(set(DRIFT_DIAGNOSTIC_TYPES) - observed_diagnostic_types)
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_DRIFT_OPERATIONAL_STATES) - observed_unsupported_states
    )
    unsafe_diagnostic_ids = sorted(
        record.diagnostic_id
        for record in foundations.diagnostics
        if not (
            record.fail_visible
            and record.descriptive_only
            and not record.hidden_fallback_used
            and not record.remediation_enabled
            and not record.repair_enabled
            and not record.auto_correction_enabled
            and not record.orchestration_response_enabled
            and not record.authorization_behavior_enabled
        )
    )
    unsafe_unsupported_state_ids = sorted(
        record.state_id
        for record in foundations.unsupported_state_visibility
        if not (
            record.fail_visible
            and record.descriptive_only
            and not record.operational_enabled
            and not record.remediation_enabled
            and not record.repair_enabled
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
        "diagnostic_count": len(foundations.diagnostics),
        "unsupported_state_count": len(foundations.unsupported_state_visibility),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_state_ids": unsafe_unsupported_state_ids,
        "fail_visible": all(record.fail_visible for record in foundations.diagnostics)
        and all(record.fail_visible for record in foundations.unsupported_state_visibility),
        "hidden_fallback_used_count": sum(
            1 for record in foundations.diagnostics if record.hidden_fallback_used
        ),
        "remediation_enabled_count": sum(
            1
            for record in foundations.diagnostics
            if record.remediation_enabled
        )
        + sum(
            1
            for record in foundations.unsupported_state_visibility
            if record.remediation_enabled
        ),
    }


def validate_descriptive_only_drift_guarantees(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    counters = drift_foundation_capability_counter_values(foundations)
    enabled_flags = enabled_drift_foundation_capability_flags(foundations)
    descriptive_failures = sorted(
        str(
            getattr(item, "drift_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "foundation_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(foundations)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5A_1_DRIFT_FOUNDATION_DISABLED_COUNTER_NAMES) - set(counters)
    )
    required_repository_states = {
        "NON-operational": foundations.non_operational,
        "NON-authorizing": foundations.non_authorizing,
        "NON-executing": foundations.non_executing,
        "NON-remediating": foundations.non_remediating,
        "NON-runtime-mutating": foundations.non_runtime_mutating,
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
        "inherited_prohibition_count": len(foundations.inherited_prohibitions),
        "inherited_constraint_count": len(foundations.inherited_constraints),
        "explicit_limitation_count": len(foundations.explicit_limitations),
    }


def validate_v4_5a_1_drift_foundations(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_drift_ordering_stability(foundations),
        "identity_integrity": validate_drift_identity_integrity(foundations),
        "evidence_continuity": validate_drift_evidence_continuity(foundations),
        "lineage_continuity": validate_drift_lineage_continuity(foundations),
        "serialization_hashing": validate_drift_serialization_and_hashing(foundations),
        "required_visibility": validate_required_drift_visibility(foundations),
        "fail_visible_unsupported_states": validate_fail_visible_unsupported_state_visibility(
            foundations
        ),
        "descriptive_only_guarantees": validate_descriptive_only_drift_guarantees(
            foundations
        ),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_5a_1_drift_foundations_report() -> dict[str, Any]:
    foundations = build_v4_5a_1_drift_foundations()
    exported = export_v4_5a_1_drift_foundations(foundations)
    validation = validate_v4_5a_1_drift_foundations(foundations)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    evidence_continuity = validation["validations"]["evidence_continuity"]
    lineage_continuity = validation["validations"]["lineage_continuity"]
    fail_visible = validation["validations"]["fail_visible_unsupported_states"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "foundation_identity_hash": hash_drift_foundation_identity(
            foundations.foundation_identity
        ),
        "foundation_hash": hash_v4_5a_1_drift_foundations(foundations),
        "drift_identity_hashes": {
            record.drift_id: hash_drift_identity_record(record)
            for record in sorted(
                foundations.drift_identities,
                key=lambda item: (item.deterministic_order, item.drift_id),
            )
        },
        "classification_hashes": {
            record.classification_id: hash_drift_classification_record(record)
            for record in sorted(
                foundations.classifications,
                key=lambda item: (item.deterministic_order, item.classification_id),
            )
        },
        "evidence_hashes": {
            record.evidence_id: hash_drift_evidence_reference(record)
            for record in sorted(
                foundations.evidence_references,
                key=lambda item: (item.deterministic_order, item.evidence_id),
            )
        },
        "continuity_hashes": {
            record.continuity_id: hash_drift_continuity_visibility(record)
            for record in sorted(
                foundations.continuity_visibility,
                key=lambda item: (item.deterministic_order, item.continuity_id),
            )
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_drift_diagnostic_record(record)
            for record in sorted(
                foundations.diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "severity_hashes": {
            record.severity_id: hash_drift_severity_visibility(record)
            for record in sorted(
                foundations.severity_visibility,
                key=lambda item: (item.deterministic_order, item.severity_id),
            )
        },
        "unsupported_state_hashes": {
            record.state_id: hash_unsupported_drift_state_visibility(record)
            for record in sorted(
                foundations.unsupported_state_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "drift_identity_count": len(foundations.drift_identities),
        "drift_classification_count": len(foundations.classifications),
        "evidence_reference_count": len(foundations.evidence_references),
        "continuity_visibility_count": len(foundations.continuity_visibility),
        "diagnostic_count": len(foundations.diagnostics),
        "severity_visibility_count": len(foundations.severity_visibility),
        "unsupported_state_visibility_count": len(foundations.unsupported_state_visibility),
        "drift_category_counts": required_visibility["category_counts"],
        "severity_counts": required_visibility["severity_counts"],
        "evidence_type_counts": required_visibility["evidence_counts"],
        "continuity_type_counts": required_visibility["continuity_counts"],
        "diagnostic_type_counts": required_visibility["diagnostic_counts"],
        "unsupported_state_counts": required_visibility["unsupported_state_counts"],
        "deterministic_serialization_verified": serialization_hashing["serialization_stable"],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "replay_safe_evidence_verified": evidence_continuity["replay_safe_evidence_count"]
        == len(foundations.evidence_references),
        "provenance_safe_evidence_verified": evidence_continuity[
            "provenance_safe_evidence_count"
        ]
        == len(foundations.evidence_references),
        "lineage_continuity_preserved": lineage_continuity[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_continuity[
            "provenance_continuity_preserved"
        ],
        "fail_visible_unsupported_state_visibility_verified": fail_visible["valid"],
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
        "drift_summaries": drift_summary_visibility(foundations),
        "severity_summaries": severity_summary_visibility(foundations.severity_visibility),
        "evidence_summaries": evidence_summary_visibility(foundations.evidence_references),
        "continuity_summaries": continuity_summary_visibility(
            foundations.continuity_visibility
        ),
        "fail_visible_diagnostics": fail_visible_diagnostic_summaries(
            foundations.diagnostics
        ),
        "unsupported_state_visibility": unsupported_state_visibility_summaries(
            foundations.unsupported_state_visibility
        ),
        "descriptive_only_summary": descriptive_only_visibility_summary(foundations),
    }
    report_without_hash = {
        "schema_version": V4_5A_1_DRIFT_FOUNDATION_REPORT_SCHEMA_VERSION,
        "phase_id": V4_5A_1_DRIFT_FOUNDATION_PHASE_ID,
        "generated_at": V4_5A_1_DRIFT_FOUNDATION_GENERATED_AT,
        "purpose": V4_5A_1_DRIFT_FOUNDATION_PURPOSE,
        "foundation_status": (
            V4_5A_1_DRIFT_FOUNDATION_STATUS_STABLE
            if validation["valid"]
            else V4_5A_1_DRIFT_FOUNDATION_STATUS_BLOCKED
        ),
        "summary": summary,
        "visibility": visibility,
        "validation": validation,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "drift_foundations": exported,
    }
    return {
        **report_without_hash,
        "deterministic_report_hash": deterministic_v4_5a_1_drift_foundation_hash(
            report_without_hash
        ),
    }


def contaminate_v4_5a_1_drift_foundations_for_non_operational_validation(
    foundations: DriftFoundationIntelligence,
) -> DriftFoundationIntelligence:
    contaminated_identity = replace(
        foundations.drift_identities[0],
        runtime_execution_enabled=True,
        operational_mutation_enabled=True,
    )
    contaminated_diagnostic = replace(
        foundations.diagnostics[0],
        remediation_enabled=True,
        auto_correction_enabled=True,
        orchestration_response_enabled=True,
    )
    contaminated_state = replace(
        foundations.unsupported_state_visibility[0],
        operational_enabled=True,
        authorization_enabled=True,
    )
    return replace(
        foundations,
        drift_identities=(contaminated_identity,) + foundations.drift_identities[1:],
        diagnostics=(contaminated_diagnostic,) + foundations.diagnostics[1:],
        unsupported_state_visibility=(contaminated_state,)
        + foundations.unsupported_state_visibility[1:],
        orchestration_authorization_enabled=True,
        remediation_enabled=True,
        runtime_mutation_enabled=True,
    )
