"""Audit for deterministic v4.5A.7 integrity certification.

The audit validates descriptive integrity certification only. It does not
authorize, approve, execute, dispatch, route, traverse, schedule, sequence,
decide, recommend, rank, remediate, repair, mitigate, correct, integrate
planners, consume production paths, or mutate runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_5a_7_integrity_certification_hashing import (
    deterministic_v4_5a_7_integrity_certification_hash,
    hash_certification_diagnostic_record,
    hash_continuity_integrity_certification,
    hash_coverage_certification_visibility,
    hash_diagnostics_integrity_certification,
    hash_hashing_serialization_integrity_certification,
    hash_inherited_prohibition_preservation_certification,
    hash_integrity_certification_identity,
    hash_integrity_certification_record,
    hash_unsupported_certification_visibility,
    hash_unsupported_state_preservation_certification,
    hash_v4_5a_7_integrity_certification,
)
from .v4_5a_7_integrity_certification_models import (
    CERTIFICATION_DIAGNOSTIC_TYPES,
    CONTINUITY_INTEGRITY_CERTIFICATION_TYPES,
    COVERAGE_CERTIFICATION_TYPES,
    DIAGNOSTICS_INTEGRITY_CERTIFICATION_TYPES,
    HASH_SERIALIZATION_CERTIFICATION_TYPES,
    INHERITED_PROHIBITION_CERTIFICATION_TYPES,
    SOURCE_REPORTS,
    UNSUPPORTED_CERTIFICATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_PRESERVATION_TYPES,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_REPORT_HASH_REFERENCE,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_REPORT_REFERENCE,
    V4_5A_7_INTEGRITY_CERTIFICATION_DISABLED_COUNTER_NAMES,
    V4_5A_7_INTEGRITY_CERTIFICATION_GENERATED_AT,
    V4_5A_7_INTEGRITY_CERTIFICATION_PHASE_ID,
    V4_5A_7_INTEGRITY_CERTIFICATION_PURPOSE,
    V4_5A_7_INTEGRITY_CERTIFICATION_REPORT_SCHEMA_VERSION,
    V4_5A_7_INTEGRITY_CERTIFICATION_STATUS_BLOCKED,
    V4_5A_7_INTEGRITY_CERTIFICATION_STATUS_STABLE,
    IntegrityCertificationIntelligence,
    default_v4_5a_7_integrity_certification,
)
from .v4_5a_7_integrity_certification_serialization import (
    export_v4_5a_7_integrity_certification,
    serialize_v4_5a_7_integrity_certification,
)
from .v4_5a_7_integrity_certification_visibility import (
    certification_summary_visibility,
    continuity_certification_summary_visibility,
    coverage_certification_summary_visibility,
    descriptive_only_integrity_certification_summary,
    diagnostics_certification_summary_visibility,
    fail_visible_certification_diagnostic_summaries,
    hashing_serialization_certification_summary_visibility,
    inherited_prohibition_certification_summary_visibility,
    unsupported_certification_visibility_summaries,
    unsupported_state_certification_summary_visibility,
    validate_required_integrity_certification_visibility,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "planner_execution_enabled",
        "execution_enabled",
        "operational_behavior_enabled",
        "operational_readiness_enabled",
        "operational_semantics_enabled",
        "operational_enabled",
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
        "orchestration_response_enabled",
    ),
    "enabled_authorization_semantics_count": (
        "authorization_semantics_enabled",
        "runtime_authority_enabled",
    ),
    "enabled_approval_semantics_count": ("approval_semantics_enabled",),
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
    "enabled_ranking_count": (
        "ranking_enabled",
        "scoring_enabled",
        "prioritization_enabled",
    ),
    "enabled_recommendation_count": (
        "recommendation_enabled",
        "recommendation_behavior_enabled",
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


def build_v4_5a_7_integrity_certification() -> IntegrityCertificationIntelligence:
    return default_v4_5a_7_integrity_certification()


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


def enabled_integrity_certification_capability_flags(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "certification_record_id", None)
            or getattr(item, "coverage_id", None)
            or getattr(item, "unsupported_certification_id", None)
            or getattr(item, "prohibition_certification_id", None)
            or getattr(item, "hash_serialization_certification_id", None)
            or getattr(item, "continuity_certification_id", None)
            or getattr(item, "diagnostics_certification_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "certification_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def integrity_certification_capability_counter_values(
    intelligence: IntegrityCertificationIntelligence,
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


def integrity_certification_equal(
    left: IntegrityCertificationIntelligence,
    right: IntegrityCertificationIntelligence,
) -> bool:
    return serialize_v4_5a_7_integrity_certification(
        left
    ) == serialize_v4_5a_7_integrity_certification(right)


def validate_certification_ordering_stability(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "certification_records": tuple(
            record.deterministic_order for record in intelligence.certification_records
        ),
        "coverage_certifications": tuple(
            record.deterministic_order for record in intelligence.coverage_certifications
        ),
        "unsupported_state_certifications": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_state_certifications
        ),
        "inherited_prohibition_certifications": tuple(
            record.deterministic_order
            for record in intelligence.inherited_prohibition_certifications
        ),
        "hashing_serialization_certifications": tuple(
            record.deterministic_order
            for record in intelligence.hashing_serialization_certifications
        ),
        "continuity_certifications": tuple(
            record.deterministic_order
            for record in intelligence.continuity_certifications
        ),
        "diagnostics_certifications": tuple(
            record.deterministic_order
            for record in intelligence.diagnostics_certifications
        ),
        "certification_diagnostics": tuple(
            record.deterministic_order
            for record in intelligence.certification_diagnostics
        ),
        "unsupported_certification_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_certification_visibility
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


def validate_certification_identity_integrity(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    identity = intelligence.certification_identity
    record_ids = [
        record.certification_record_id for record in intelligence.certification_records
    ]
    certification_ids = [
        record.certification_id for record in intelligence.certification_records
    ]
    empty_identity_fields = [
        field_name
        for field_name in (
            "certification_id",
            "certification_chain_id",
            "drift_foundation_reference_id",
            "propagation_reference_id",
            "degradation_reference_id",
            "explainability_reference_id",
            "continuity_reference_id",
            "diagnostics_aggregation_reference_id",
            "evidence_reference_id",
            "lineage_reference_id",
            "provenance_reference_id",
            "phase_id",
            "schema_version",
            "generated_at",
            "classification",
            "source_diagnostics_aggregation_report_reference",
            "source_diagnostics_aggregation_hash_reference",
        )
        if not getattr(identity, field_name)
    ]
    mismatched_records = sorted(
        record.certification_record_id
        for record in intelligence.certification_records
        if (
            record.certification_id != identity.certification_id
            or record.certification_chain_id != identity.certification_chain_id
            or record.drift_foundation_reference_id
            != identity.drift_foundation_reference_id
            or record.propagation_reference_id != identity.propagation_reference_id
            or record.degradation_reference_id != identity.degradation_reference_id
            or record.explainability_reference_id != identity.explainability_reference_id
            or record.continuity_reference_id != identity.continuity_reference_id
            or record.diagnostics_aggregation_reference_id
            != identity.diagnostics_aggregation_reference_id
            or record.evidence_reference_id != identity.evidence_reference_id
            or record.lineage_reference_id != identity.lineage_reference_id
            or record.provenance_reference_id != identity.provenance_reference_id
        )
    )
    return {
        "valid": not (
            empty_identity_fields
            or mismatched_records
            or len(set(record_ids)) != len(record_ids)
            or len(set(certification_ids)) != len(certification_ids)
            or identity.source_diagnostics_aggregation_report_reference
            != V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_REPORT_REFERENCE
            or identity.source_diagnostics_aggregation_hash_reference
            != V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_REPORT_HASH_REFERENCE
        ),
        "certification_record_count": len(intelligence.certification_records),
        "unique_certification_record_count": len(set(record_ids)),
        "unique_certification_count": len(set(certification_ids)),
        "empty_identity_fields": empty_identity_fields,
        "mismatched_records": mismatched_records,
        "source_diagnostics_aggregation_report_reference": (
            identity.source_diagnostics_aggregation_report_reference
        ),
        "source_diagnostics_aggregation_hash_reference": (
            identity.source_diagnostics_aggregation_hash_reference
        ),
    }


def validate_certification_coverage_stability(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    records = intelligence.coverage_certifications
    present = {record.coverage_type for record in records}
    missing_types = sorted(set(COVERAGE_CERTIFICATION_TYPES) - present)
    unknown_types = sorted(present - set(COVERAGE_CERTIFICATION_TYPES))
    bad_source_references = sorted(
        record.coverage_id
        for record in records
        if SOURCE_REPORTS.get(record.coverage_type)
        != (
            record.source_reference.split("#", 1)[0],
            record.source_hash_reference,
        )
    )
    unsafe_ids = sorted(
        record.coverage_id
        for record in records
        if (
            not record.coverage_preserved
            or not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.operational_semantics_enabled
        )
    )
    return {
        "valid": not (
            missing_types or unknown_types or bad_source_references or unsafe_ids
        ),
        "coverage_certification_count": len(records),
        "missing_coverage_types": missing_types,
        "unknown_coverage_types": unknown_types,
        "bad_source_references": bad_source_references,
        "unsafe_coverage_ids": unsafe_ids,
    }


def validate_unsupported_state_preservation_visibility(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    records = intelligence.unsupported_state_certifications
    present = {record.preservation_type for record in records}
    missing_types = sorted(set(UNSUPPORTED_STATE_PRESERVATION_TYPES) - present)
    unsafe_ids = sorted(
        record.unsupported_certification_id
        for record in records
        if (
            not record.preservation_certified
            or not record.descriptive_only
            or not record.fail_visible
            or record.suppression_enabled
            or record.remediation_enabled
            or record.authorization_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "unsupported_state_certification_count": len(records),
        "missing_unsupported_state_preservation_types": missing_types,
        "unsafe_unsupported_state_certification_ids": unsafe_ids,
    }


def validate_inherited_prohibition_preservation_visibility(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    records = intelligence.inherited_prohibition_certifications
    present = {record.preservation_type for record in records}
    missing_types = sorted(set(INHERITED_PROHIBITION_CERTIFICATION_TYPES) - present)
    unsafe_ids = sorted(
        record.prohibition_certification_id
        for record in records
        if (
            not record.preservation_certified
            or not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.operational_behavior_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "inherited_prohibition_certification_count": len(records),
        "missing_inherited_prohibition_certification_types": missing_types,
        "unsafe_prohibition_certification_ids": unsafe_ids,
    }


def validate_hashing_serialization_certification_stability(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    records = intelligence.hashing_serialization_certifications
    present = {record.certification_type for record in records}
    missing_types = sorted(set(HASH_SERIALIZATION_CERTIFICATION_TYPES) - present)
    unsafe_ids = sorted(
        record.hash_serialization_certification_id
        for record in records
        if (
            not record.certification_preserved
            or not record.replay_safe
            or not record.lineage_safe
            or not record.provenance_safe
            or not record.descriptive_only
            or record.runtime_authority_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "hashing_serialization_certification_count": len(records),
        "missing_hashing_serialization_certification_types": missing_types,
        "unsafe_hashing_serialization_certification_ids": unsafe_ids,
        "replay_safe_count": sum(1 for record in records if record.replay_safe),
        "lineage_safe_count": sum(1 for record in records if record.lineage_safe),
        "provenance_safe_count": sum(1 for record in records if record.provenance_safe),
    }


def validate_continuity_certification_stability(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    records = intelligence.continuity_certifications
    present = {record.continuity_type for record in records}
    missing_types = sorted(set(CONTINUITY_INTEGRITY_CERTIFICATION_TYPES) - present)
    missing_references = sorted(
        record.continuity_certification_id
        for record in records
        if not record.continuity_reference_id
    )
    unsafe_ids = sorted(
        record.continuity_certification_id
        for record in records
        if (
            not record.continuity_certified
            or not record.descriptive_only
            or record.restoration_enabled
            or record.repair_enabled
            or record.remediation_enabled
        )
    )
    return {
        "valid": not (missing_types or missing_references or unsafe_ids),
        "continuity_certification_count": len(records),
        "missing_continuity_certification_types": missing_types,
        "missing_continuity_references": missing_references,
        "unsafe_continuity_certification_ids": unsafe_ids,
    }


def validate_diagnostics_certification_stability(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    records = intelligence.diagnostics_certifications
    present = {record.diagnostics_type for record in records}
    missing_types = sorted(set(DIAGNOSTICS_INTEGRITY_CERTIFICATION_TYPES) - present)
    unsafe_ids = sorted(
        record.diagnostics_certification_id
        for record in records
        if (
            not record.diagnostics_certified
            or not record.descriptive_only
            or record.automated_triage_enabled
            or record.prioritization_enabled
            or record.ranking_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "diagnostics_certification_count": len(records),
        "missing_diagnostics_certification_types": missing_types,
        "unsafe_diagnostics_certification_ids": unsafe_ids,
    }


def validate_lineage_and_provenance_preservation(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    missing_lineage = sorted(
        record.certification_record_id
        for record in intelligence.certification_records
        if not record.lineage_reference_id
    )
    missing_provenance = sorted(
        record.certification_record_id
        for record in intelligence.certification_records
        if not record.provenance_reference_id
    )
    missing_evidence = sorted(
        record.certification_record_id
        for record in intelligence.certification_records
        if not record.evidence_reference_id
    )
    missing_certification_evidence = sorted(
        str(
            getattr(item, "coverage_id", None)
            or getattr(item, "unsupported_certification_id", None)
            or getattr(item, "prohibition_certification_id", None)
            or getattr(item, "hash_serialization_certification_id", None)
            or getattr(item, "continuity_certification_id", None)
            or getattr(item, "diagnostics_certification_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", "")
        )
        for item in (
            intelligence.coverage_certifications
            + intelligence.unsupported_state_certifications
            + intelligence.inherited_prohibition_certifications
            + intelligence.hashing_serialization_certifications
            + intelligence.continuity_certifications
            + intelligence.diagnostics_certifications
            + intelligence.certification_diagnostics
            + intelligence.unsupported_certification_visibility
        )
        if hasattr(item, "evidence_reference_ids")
        and not tuple(getattr(item, "evidence_reference_ids"))
    )
    return {
        "valid": not (
            missing_lineage
            or missing_provenance
            or missing_evidence
            or missing_certification_evidence
        ),
        "missing_lineage_reference_ids": missing_lineage,
        "missing_provenance_reference_ids": missing_provenance,
        "missing_evidence_reference_ids": missing_evidence,
        "missing_certification_evidence_ids": missing_certification_evidence,
        "lineage_continuity_preserved": not missing_lineage,
        "provenance_continuity_preserved": not missing_provenance,
        "evidence_continuity_preserved": not (
            missing_evidence or missing_certification_evidence
        ),
    }


def validate_integrity_certification_serialization_and_hashing(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    first_serialization = serialize_v4_5a_7_integrity_certification(intelligence)
    second_serialization = serialize_v4_5a_7_integrity_certification(intelligence)
    first_hash = hash_v4_5a_7_integrity_certification(intelligence)
    second_hash = hash_v4_5a_7_integrity_certification(intelligence)
    rebuilt = build_v4_5a_7_integrity_certification()
    rebuilt_hash = hash_v4_5a_7_integrity_certification(rebuilt)
    return {
        "valid": (
            first_serialization == second_serialization
            and first_hash == second_hash
            and first_hash == rebuilt_hash
        ),
        "serialization_stable": first_serialization == second_serialization,
        "hashing_stable": first_hash == second_hash == rebuilt_hash,
        "integrity_certification_hash": first_hash,
        "rebuilt_integrity_certification_hash": rebuilt_hash,
        "serialization_length": len(first_serialization),
    }


def validate_fail_visible_certification_diagnostics(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    diagnostic_records = intelligence.certification_diagnostics
    unsupported_records = intelligence.unsupported_certification_visibility
    present_diagnostics = {record.diagnostic_type for record in diagnostic_records}
    present_unsupported = {record.unsupported_state for record in unsupported_records}
    missing_diagnostic_types = sorted(
        set(CERTIFICATION_DIAGNOSTIC_TYPES) - present_diagnostics
    )
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_CERTIFICATION_OPERATIONAL_STATES) - present_unsupported
    )
    unsafe_diagnostic_ids = sorted(
        record.diagnostic_id
        for record in diagnostic_records
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.silent_fallback_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.mitigation_enabled
            or record.auto_correction_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
            or record.orchestration_response_enabled
        )
    )
    unsafe_unsupported_ids = sorted(
        record.state_id
        for record in unsupported_records
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.operational_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.mitigation_enabled
            or record.automated_correction_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
        )
    )
    return {
        "valid": not (
            missing_diagnostic_types
            or missing_unsupported_states
            or unsafe_diagnostic_ids
            or unsafe_unsupported_ids
        ),
        "certification_diagnostic_count": len(diagnostic_records),
        "unsupported_certification_state_count": len(unsupported_records),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_ids": unsafe_unsupported_ids,
        "fail_visible": all(record.fail_visible for record in diagnostic_records)
        and all(record.fail_visible for record in unsupported_records),
        "silent_fallback_enabled_count": sum(
            1 for record in diagnostic_records if record.silent_fallback_enabled
        ),
        "authorization_enabled_count": sum(
            1 for record in diagnostic_records if record.authorization_enabled
        )
        + sum(1 for record in unsupported_records if record.authorization_enabled),
        "approval_enabled_count": sum(
            1 for record in diagnostic_records if record.approval_enabled
        )
        + sum(1 for record in unsupported_records if record.approval_enabled),
        "ranking_enabled_count": sum(
            1 for record in diagnostic_records if record.ranking_enabled
        )
        + sum(1 for record in unsupported_records if record.ranking_enabled),
        "recommendation_enabled_count": sum(
            1 for record in diagnostic_records if record.recommendation_enabled
        )
        + sum(1 for record in unsupported_records if record.recommendation_enabled),
    }


def validate_descriptive_only_integrity_certification_guarantees(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    counters = integrity_certification_capability_counter_values(intelligence)
    enabled_flags = enabled_integrity_certification_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "certification_record_id", None)
            or getattr(item, "coverage_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "certification_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5A_7_INTEGRITY_CERTIFICATION_DISABLED_COUNTER_NAMES) - set(counters)
    )
    required_repository_states = {
        "NON-operational": intelligence.non_operational,
        "NON-authorizing": intelligence.non_authorizing,
        "NON-approving": intelligence.non_approving,
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


def validate_v4_5a_7_integrity_certification(
    intelligence: IntegrityCertificationIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_certification_ordering_stability(intelligence),
        "identity_integrity": validate_certification_identity_integrity(intelligence),
        "coverage_certification": validate_certification_coverage_stability(
            intelligence
        ),
        "unsupported_state_preservation": validate_unsupported_state_preservation_visibility(
            intelligence
        ),
        "inherited_prohibition_preservation": validate_inherited_prohibition_preservation_visibility(
            intelligence
        ),
        "hashing_serialization_certification": validate_hashing_serialization_certification_stability(
            intelligence
        ),
        "continuity_certification": validate_continuity_certification_stability(
            intelligence
        ),
        "diagnostics_certification": validate_diagnostics_certification_stability(
            intelligence
        ),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_hashing": validate_integrity_certification_serialization_and_hashing(
            intelligence
        ),
        "required_visibility": validate_required_integrity_certification_visibility(
            intelligence
        ),
        "fail_visible_certification": validate_fail_visible_certification_diagnostics(
            intelligence
        ),
        "descriptive_only_guarantees": validate_descriptive_only_integrity_certification_guarantees(
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


def build_v4_5a_7_integrity_certification_report() -> dict[str, Any]:
    intelligence = build_v4_5a_7_integrity_certification()
    exported = export_v4_5a_7_integrity_certification(intelligence)
    validation = validate_v4_5a_7_integrity_certification(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    coverage = validation["validations"]["coverage_certification"]
    unsupported = validation["validations"]["unsupported_state_preservation"]
    prohibition = validation["validations"]["inherited_prohibition_preservation"]
    hash_serialization = validation["validations"][
        "hashing_serialization_certification"
    ]
    continuity = validation["validations"]["continuity_certification"]
    diagnostics = validation["validations"]["diagnostics_certification"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_certification"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "certification_identity_hash": hash_integrity_certification_identity(
            intelligence.certification_identity
        ),
        "integrity_certification_hash": hash_v4_5a_7_integrity_certification(
            intelligence
        ),
        "certification_record_hashes": {
            record.certification_record_id: hash_integrity_certification_record(record)
            for record in sorted(
                intelligence.certification_records,
                key=lambda item: (item.deterministic_order, item.certification_record_id),
            )
        },
        "coverage_certification_hashes": {
            record.coverage_id: hash_coverage_certification_visibility(record)
            for record in sorted(
                intelligence.coverage_certifications,
                key=lambda item: (item.deterministic_order, item.coverage_id),
            )
        },
        "unsupported_state_certification_hashes": {
            record.unsupported_certification_id: (
                hash_unsupported_state_preservation_certification(record)
            )
            for record in sorted(
                intelligence.unsupported_state_certifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.unsupported_certification_id,
                ),
            )
        },
        "inherited_prohibition_certification_hashes": {
            record.prohibition_certification_id: (
                hash_inherited_prohibition_preservation_certification(record)
            )
            for record in sorted(
                intelligence.inherited_prohibition_certifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.prohibition_certification_id,
                ),
            )
        },
        "hashing_serialization_certification_hashes": {
            record.hash_serialization_certification_id: (
                hash_hashing_serialization_integrity_certification(record)
            )
            for record in sorted(
                intelligence.hashing_serialization_certifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.hash_serialization_certification_id,
                ),
            )
        },
        "continuity_certification_hashes": {
            record.continuity_certification_id: hash_continuity_integrity_certification(
                record
            )
            for record in sorted(
                intelligence.continuity_certifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.continuity_certification_id,
                ),
            )
        },
        "diagnostics_certification_hashes": {
            record.diagnostics_certification_id: hash_diagnostics_integrity_certification(
                record
            )
            for record in sorted(
                intelligence.diagnostics_certifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.diagnostics_certification_id,
                ),
            )
        },
        "certification_diagnostic_hashes": {
            record.diagnostic_id: hash_certification_diagnostic_record(record)
            for record in sorted(
                intelligence.certification_diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_certification_hashes": {
            record.state_id: hash_unsupported_certification_visibility(record)
            for record in sorted(
                intelligence.unsupported_certification_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "certification_record_count": len(intelligence.certification_records),
        "coverage_certification_count": len(intelligence.coverage_certifications),
        "unsupported_state_certification_count": len(
            intelligence.unsupported_state_certifications
        ),
        "inherited_prohibition_certification_count": len(
            intelligence.inherited_prohibition_certifications
        ),
        "hashing_serialization_certification_count": len(
            intelligence.hashing_serialization_certifications
        ),
        "continuity_certification_count": len(intelligence.continuity_certifications),
        "diagnostics_certification_count": len(intelligence.diagnostics_certifications),
        "certification_diagnostic_count": len(intelligence.certification_diagnostics),
        "unsupported_certification_state_count": len(
            intelligence.unsupported_certification_visibility
        ),
        "coverage_counts": required_visibility["coverage_counts"],
        "unsupported_counts": required_visibility["unsupported_counts"],
        "prohibition_counts": required_visibility["prohibition_counts"],
        "hash_serialization_counts": required_visibility["hash_serialization_counts"],
        "continuity_counts": required_visibility["continuity_counts"],
        "diagnostics_counts": required_visibility["diagnostics_counts"],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_state_counts": required_visibility["unsupported_state_counts"],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "certification_coverage_stable": coverage["valid"],
        "unsupported_state_preservation_stable": unsupported["valid"],
        "inherited_prohibition_preservation_stable": prohibition["valid"],
        "hashing_serialization_certification_stable": hash_serialization["valid"],
        "continuity_certification_stable": continuity["valid"],
        "diagnostics_certification_stable": diagnostics["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "evidence_continuity_preserved": lineage_provenance[
            "evidence_continuity_preserved"
        ],
        "fail_visible_certification_diagnostics_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "inherited_prohibition_count": descriptive_only["inherited_prohibition_count"],
        "inherited_constraint_count": descriptive_only["inherited_constraint_count"],
        "explicit_limitation_count": descriptive_only["explicit_limitation_count"],
        "validation_error_count": validation["validation_error_count"],
        "repository_remains": [
            "NON-operational",
            "NON-authorizing",
            "NON-approving",
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
        "certification_summaries": certification_summary_visibility(
            intelligence.certification_records
        ),
        "coverage_certification_summaries": coverage_certification_summary_visibility(
            intelligence.coverage_certifications
        ),
        "unsupported_state_certification_summaries": (
            unsupported_state_certification_summary_visibility(
                intelligence.unsupported_state_certifications
            )
        ),
        "inherited_prohibition_certification_summaries": (
            inherited_prohibition_certification_summary_visibility(
                intelligence.inherited_prohibition_certifications
            )
        ),
        "hashing_serialization_certification_summaries": (
            hashing_serialization_certification_summary_visibility(
                intelligence.hashing_serialization_certifications
            )
        ),
        "continuity_certification_summaries": (
            continuity_certification_summary_visibility(
                intelligence.continuity_certifications
            )
        ),
        "diagnostics_certification_summaries": (
            diagnostics_certification_summary_visibility(
                intelligence.diagnostics_certifications
            )
        ),
        "fail_visible_certification_diagnostics": (
            fail_visible_certification_diagnostic_summaries(
                intelligence.certification_diagnostics
            )
        ),
        "unsupported_certification_visibility": (
            unsupported_certification_visibility_summaries(
                intelligence.unsupported_certification_visibility
            )
        ),
        "descriptive_only_summary": descriptive_only_integrity_certification_summary(
            intelligence
        ),
    }
    report_without_hash = {
        "schema_version": V4_5A_7_INTEGRITY_CERTIFICATION_REPORT_SCHEMA_VERSION,
        "phase_id": V4_5A_7_INTEGRITY_CERTIFICATION_PHASE_ID,
        "generated_at": V4_5A_7_INTEGRITY_CERTIFICATION_GENERATED_AT,
        "purpose": V4_5A_7_INTEGRITY_CERTIFICATION_PURPOSE,
        "foundation_status": (
            V4_5A_7_INTEGRITY_CERTIFICATION_STATUS_STABLE
            if validation["valid"]
            else V4_5A_7_INTEGRITY_CERTIFICATION_STATUS_BLOCKED
        ),
        "summary": summary,
        "visibility": visibility,
        "validation": validation,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "integrity_certification_intelligence": exported,
    }
    return {
        **report_without_hash,
        "deterministic_report_hash": deterministic_v4_5a_7_integrity_certification_hash(
            report_without_hash
        ),
    }


def contaminate_v4_5a_7_integrity_certification_for_non_operational_validation(
    intelligence: IntegrityCertificationIntelligence,
) -> IntegrityCertificationIntelligence:
    contaminated_record = replace(
        intelligence.certification_records[0],
        authorization_enabled=True,
        approval_enabled=True,
        operational_readiness_enabled=True,
    )
    contaminated_coverage = replace(
        intelligence.coverage_certifications[0],
        authorization_enabled=True,
        approval_enabled=True,
        operational_semantics_enabled=True,
    )
    contaminated_unsupported = replace(
        intelligence.unsupported_state_certifications[0],
        suppression_enabled=True,
        remediation_enabled=True,
        authorization_enabled=True,
    )
    contaminated_diagnostic = replace(
        intelligence.certification_diagnostics[0],
        authorization_enabled=True,
        approval_enabled=True,
        remediation_enabled=True,
        mitigation_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
        silent_fallback_enabled=True,
    )
    contaminated_state = replace(
        intelligence.unsupported_certification_visibility[0],
        authorization_enabled=True,
        approval_enabled=True,
        operational_enabled=True,
        remediation_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
    )
    return replace(
        intelligence,
        certification_records=(contaminated_record,)
        + intelligence.certification_records[1:],
        coverage_certifications=(contaminated_coverage,)
        + intelligence.coverage_certifications[1:],
        unsupported_state_certifications=(contaminated_unsupported,)
        + intelligence.unsupported_state_certifications[1:],
        certification_diagnostics=(contaminated_diagnostic,)
        + intelligence.certification_diagnostics[1:],
        unsupported_certification_visibility=(contaminated_state,)
        + intelligence.unsupported_certification_visibility[1:],
        runtime_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        authorization_semantics_enabled=True,
        approval_semantics_enabled=True,
        remediation_enabled=True,
        mitigation_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
        runtime_mutation_enabled=True,
    )
