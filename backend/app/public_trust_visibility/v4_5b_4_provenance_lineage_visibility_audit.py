"""Audit for deterministic v4.5B.4 provenance and lineage visibility.

The audit validates descriptive public provenance and lineage visibility only.
It does not authorize, approve, execute, dispatch, route, traverse, schedule,
sequence, decide, recommend, rank, remediate, repair, mitigate, correct,
integrate planners, consume production paths, or mutate runtime or operational
state.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5b_4_provenance_lineage_visibility_hashing import (
    deterministic_v4_5b_4_provenance_lineage_visibility_hash,
    hash_evidence_origin_visibility,
    hash_explainability_lineage_visibility,
    hash_lineage_visibility_record,
    hash_provenance_lineage_diagnostic_record,
    hash_provenance_lineage_summary_record,
    hash_provenance_lineage_visibility_identity,
    hash_provenance_visibility_record,
    hash_source_to_surface_visibility,
    hash_stale_unknown_provenance_visibility,
    hash_support_status_lineage_visibility,
    hash_trust_summary_lineage_visibility,
    hash_unsupported_provenance_lineage_operational_state_visibility,
    hash_v4_5b_4_provenance_lineage_visibility,
)
from .v4_5b_4_provenance_lineage_visibility_models import (
    EVIDENCE_ORIGIN_VISIBILITY_TYPES,
    EXPLAINABILITY_LINEAGE_TYPES,
    PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
    PROVENANCE_LINEAGE_SUMMARY_TYPES,
    PROVENANCE_LINEAGE_VISIBILITY_STATEMENT,
    SOURCE_TO_SURFACE_VISIBILITY_TYPES,
    SOURCE_VISIBILITY_NON_AUTHORITY_STATEMENT,
    STALE_UNKNOWN_PROVENANCE_TYPES,
    SUPPORT_STATUS_LINEAGE_TYPES,
    TRUST_SUMMARY_LINEAGE_TYPES,
    UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_DISABLED_COUNTER_NAMES,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_GENERATED_AT,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PHASE_ID,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PURPOSE,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_REPORT_SCHEMA_VERSION,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_STATUS_BLOCKED,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_STATUS_STABLE,
    ProvenanceLineageVisibilityIntelligence,
    default_v4_5b_4_provenance_lineage_visibility,
)
from .v4_5b_4_provenance_lineage_visibility_serialization import (
    export_v4_5b_4_provenance_lineage_visibility,
    serialize_v4_5b_4_provenance_lineage_visibility,
)
from .v4_5b_4_provenance_lineage_visibility_visibility import (
    descriptive_only_provenance_lineage_summary,
    evidence_origin_summary,
    explainability_lineage_summary,
    lineage_visibility_summary,
    provenance_lineage_diagnostic_summary,
    provenance_lineage_summary_visibility,
    provenance_visibility_summary,
    source_to_surface_summary,
    stale_unknown_provenance_summary,
    support_status_lineage_summary,
    trust_summary_lineage_summary,
    unsupported_operational_state_summary,
    validate_required_provenance_lineage_visibility,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "planner_execution_enabled",
        "execution_enabled",
        "execution_enablement_enabled",
        "execution_semantics_enabled",
        "execution_safety_enabled",
    ),
    "enabled_orchestration_authorization_count": (
        "orchestration_authorization_enabled",
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
    "enabled_source_authorization_count": (
        "source_authorization_enabled",
        "source_authority_enabled",
        "authorization_enabled",
    ),
    "enabled_source_approval_count": (
        "source_approval_enabled",
        "approval_enabled",
        "operational_approval_enabled",
    ),
    "enabled_provenance_ranking_count": (
        "provenance_ranking_enabled",
        "ranking_enabled",
        "trust_scoring_enabled",
    ),
    "enabled_lineage_recommendation_count": (
        "lineage_recommendation_enabled",
        "recommendation_enabled",
    ),
    "enabled_remediation_count": ("remediation_enabled",),
    "enabled_repair_count": ("repair_enabled",),
    "enabled_mitigation_count": ("mitigation_enabled",),
    "enabled_auto_correction_count": (
        "auto_correction_enabled",
        "automated_correction_enabled",
    ),
    "enabled_planner_integration_count": ("planner_integration_enabled",),
    "enabled_production_consumption_count": (
        "production_consumption_enabled",
        "production_enablement_enabled",
    ),
    "enabled_runtime_mutation_count": (
        "runtime_mutation_enabled",
        "runtime_enablement_enabled",
    ),
    "enabled_operational_mutation_count": (
        "operational_mutation_enabled",
        "operational_behavior_enabled",
        "operational_semantics_enabled",
        "operational_enabled",
        "operational_fallback_enabled",
        "operational_readiness_enabled",
    ),
}

PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_5b_4_provenance_lineage_visibility() -> (
    ProvenanceLineageVisibilityIntelligence
):
    return default_v4_5b_4_provenance_lineage_visibility()


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


def _relative_path_exists(reference: str) -> bool:
    return (REPO_ROOT / reference).exists()


def _report_hash_matches(reference: str, expected_hash: str) -> bool:
    path = REPO_ROOT / reference
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return payload.get("deterministic_report_hash") == expected_hash


def _record_id(item: object) -> str:
    return str(
        getattr(item, "provenance_record_id", None)
        or getattr(item, "lineage_record_id", None)
        or getattr(item, "source_surface_id", None)
        or getattr(item, "evidence_origin_id", None)
        or getattr(item, "support_lineage_id", None)
        or getattr(item, "explainability_lineage_id", None)
        or getattr(item, "trust_lineage_id", None)
        or getattr(item, "stale_unknown_id", None)
        or getattr(item, "summary_record_id", None)
        or getattr(item, "diagnostic_id", None)
        or getattr(item, "state_id", None)
        or getattr(item, "provenance_visibility_id", item.__class__.__name__)
    )


def enabled_provenance_lineage_capability_flags(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(_record_id(item), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def provenance_lineage_capability_counter_values(
    intelligence: ProvenanceLineageVisibilityIntelligence,
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


def provenance_lineage_visibility_equal(
    left: ProvenanceLineageVisibilityIntelligence,
    right: ProvenanceLineageVisibilityIntelligence,
) -> bool:
    return serialize_v4_5b_4_provenance_lineage_visibility(
        left
    ) == serialize_v4_5b_4_provenance_lineage_visibility(right)


def validate_provenance_lineage_ordering_stability(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "provenance_visibility_records": tuple(
            record.deterministic_order
            for record in intelligence.provenance_visibility_records
        ),
        "lineage_visibility_records": tuple(
            record.deterministic_order
            for record in intelligence.lineage_visibility_records
        ),
        "source_to_surface_visibility": tuple(
            record.deterministic_order
            for record in intelligence.source_to_surface_visibility
        ),
        "evidence_origin_visibility": tuple(
            record.deterministic_order
            for record in intelligence.evidence_origin_visibility
        ),
        "support_status_lineage_visibility": tuple(
            record.deterministic_order
            for record in intelligence.support_status_lineage_visibility
        ),
        "explainability_lineage_visibility": tuple(
            record.deterministic_order
            for record in intelligence.explainability_lineage_visibility
        ),
        "trust_summary_lineage_visibility": tuple(
            record.deterministic_order
            for record in intelligence.trust_summary_lineage_visibility
        ),
        "stale_unknown_provenance_visibility": tuple(
            record.deterministic_order
            for record in intelligence.stale_unknown_provenance_visibility
        ),
        "provenance_lineage_summaries": tuple(
            record.deterministic_order
            for record in intelligence.provenance_lineage_summaries
        ),
        "provenance_lineage_diagnostics": tuple(
            record.deterministic_order
            for record in intelligence.provenance_lineage_diagnostics
        ),
        "unsupported_operational_state_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_operational_state_visibility
        ),
    }
    unordered_groups = sorted(
        key for key, values in order_groups.items() if tuple(sorted(values)) != values
    )
    return {
        "valid": not unordered_groups,
        "order_groups": {key: list(values) for key, values in order_groups.items()},
        "unordered_groups": unordered_groups,
    }


def validate_provenance_identity_integrity(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    identity = intelligence.visibility_identity
    required_values = {
        "provenance_visibility_id": identity.provenance_visibility_id,
        "source_reference_id": identity.source_reference_id,
        "evidence_reference_id": identity.evidence_reference_id,
        "provenance_reference_id": identity.provenance_reference_id,
    }
    missing_fields = sorted(key for key, value in required_values.items() if not value)
    source_report_present = _relative_path_exists(
        identity.source_explainability_report_reference
    )
    source_report_hash_matches = _report_hash_matches(
        identity.source_explainability_report_reference,
        identity.source_explainability_hash_reference,
    )
    return {
        "valid": not missing_fields
        and identity.phase_id == V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PHASE_ID
        and source_report_present
        and source_report_hash_matches,
        "missing_identity_fields": missing_fields,
        "phase_id": identity.phase_id,
        "schema_version": identity.schema_version,
        "source_report_present": source_report_present,
        "source_report_hash_matches": source_report_hash_matches,
    }


def validate_lineage_identity_integrity(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    identity = intelligence.visibility_identity
    required_values = {
        "lineage_visibility_id": identity.lineage_visibility_id,
        "support_status_reference_id": identity.support_status_reference_id,
        "explainability_surface_reference_id": (
            identity.explainability_surface_reference_id
        ),
        "trust_summary_reference_id": identity.trust_summary_reference_id,
        "diagnostics_reference_id": identity.diagnostics_reference_id,
        "continuity_reference_id": identity.continuity_reference_id,
        "lineage_reference_id": identity.lineage_reference_id,
    }
    missing_fields = sorted(key for key, value in required_values.items() if not value)
    return {
        "valid": not missing_fields
        and identity.phase_id == V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PHASE_ID,
        "missing_identity_fields": missing_fields,
        "phase_id": identity.phase_id,
        "schema_version": identity.schema_version,
    }


def validate_source_to_surface_visibility_stability(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.source_to_surface_visibility
    present = {record.visibility_type for record in records}
    missing_types = sorted(set(SOURCE_TO_SURFACE_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.source_surface_id
        for record in records
        if (
            not record.descriptive_only
            or not record.source_reference_id
            or not record.surface_reference_id
            or not record.evidence_reference_ids
            or record.source_authority_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.recommendation_enabled
            or record.ranking_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "source_to_surface_count": len(records),
        "missing_source_to_surface_types": missing_types,
        "unsafe_source_to_surface_ids": unsafe_ids,
    }


def validate_evidence_origin_visibility_preservation(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.evidence_origin_visibility
    present = {record.evidence_origin_type for record in records}
    missing_types = sorted(set(EVIDENCE_ORIGIN_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.evidence_origin_id
        for record in records
        if (
            not record.descriptive_only
            or not record.replay_safe
            or not record.provenance_safe
            or not record.source_reference_id
            or not record.evidence_reference_ids
            or not record.provenance_reference_id
            or not record.lineage_reference_id
            or record.trust_scoring_enabled
            or record.ranking_enabled
            or record.authorization_enabled
            or record.approval_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "evidence_origin_count": len(records),
        "missing_evidence_origin_types": missing_types,
        "unsafe_evidence_origin_ids": unsafe_ids,
    }


def validate_support_status_lineage_preservation(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.support_status_lineage_visibility
    present = {record.support_lineage_type for record in records}
    missing_types = sorted(set(SUPPORT_STATUS_LINEAGE_TYPES) - present)
    unsafe_ids = sorted(
        record.support_lineage_id
        for record in records
        if (
            not record.descriptive_only
            or not record.support_status_reference_id
            or not record.lineage_reference_id
            or record.recommendation_enabled
            or record.operational_semantics_enabled
            or record.authorization_enabled
            or record.approval_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "support_status_lineage_count": len(records),
        "missing_support_status_lineage_types": missing_types,
        "unsafe_support_status_lineage_ids": unsafe_ids,
    }


def validate_explainability_lineage_preservation(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.explainability_lineage_visibility
    present = {record.explainability_lineage_type for record in records}
    missing_types = sorted(set(EXPLAINABILITY_LINEAGE_TYPES) - present)
    unsafe_ids = sorted(
        record.explainability_lineage_id
        for record in records
        if (
            not record.descriptive_only
            or not record.explainability_surface_reference_id
            or not record.lineage_reference_id
            or record.explanation_approval_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "explainability_lineage_count": len(records),
        "missing_explainability_lineage_types": missing_types,
        "unsafe_explainability_lineage_ids": unsafe_ids,
    }


def validate_trust_summary_lineage_preservation(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.trust_summary_lineage_visibility
    present = {record.trust_lineage_type for record in records}
    missing_types = sorted(set(TRUST_SUMMARY_LINEAGE_TYPES) - present)
    unsafe_ids = sorted(
        record.trust_lineage_id
        for record in records
        if (
            not record.descriptive_only
            or not record.trust_summary_reference_id
            or not record.lineage_reference_id
            or record.trust_scoring_enabled
            or record.operational_readiness_enabled
            or record.authorization_enabled
            or record.approval_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "trust_summary_lineage_count": len(records),
        "missing_trust_summary_lineage_types": missing_types,
        "unsafe_trust_summary_lineage_ids": unsafe_ids,
    }


def validate_stale_unknown_provenance_visibility_preservation(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.stale_unknown_provenance_visibility
    present = {record.provenance_state_type for record in records}
    missing_types = sorted(set(STALE_UNKNOWN_PROVENANCE_TYPES) - present)
    unsafe_ids = sorted(
        record.stale_unknown_id
        for record in records
        if (
            not record.descriptive_only
            or not record.fail_visible
            or record.suppression_enabled
            or record.hidden_fallback_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.remediation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "stale_unknown_provenance_count": len(records),
        "missing_stale_unknown_provenance_types": missing_types,
        "unsafe_stale_unknown_provenance_ids": unsafe_ids,
    }


def validate_provenance_lineage_summary_stability(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.provenance_lineage_summaries
    present = {record.summary_type for record in records}
    missing_types = sorted(set(PROVENANCE_LINEAGE_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.summary_record_id
        for record in records
        if (
            not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
            or record.execution_enablement_enabled
            or record.production_enablement_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "provenance_lineage_summary_count": len(records),
        "missing_summary_types": missing_types,
        "unsafe_summary_ids": unsafe_ids,
    }


def validate_lineage_and_provenance_preservation(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    identity = intelligence.visibility_identity
    records_with_evidence = (
        intelligence.source_to_surface_visibility
        + intelligence.evidence_origin_visibility
        + intelligence.support_status_lineage_visibility
        + intelligence.explainability_lineage_visibility
        + intelligence.trust_summary_lineage_visibility
        + intelligence.stale_unknown_provenance_visibility
        + intelligence.provenance_lineage_summaries
        + intelligence.provenance_lineage_diagnostics
        + intelligence.unsupported_operational_state_visibility
    )
    records_missing_evidence = sorted(
        _record_id(record)
        for record in records_with_evidence
        if not getattr(record, "evidence_reference_ids", ())
    )
    lineage_missing = sorted(
        _record_id(record)
        for record in (
            intelligence.evidence_origin_visibility
            + intelligence.support_status_lineage_visibility
            + intelligence.explainability_lineage_visibility
            + intelligence.trust_summary_lineage_visibility
        )
        if not getattr(record, "lineage_reference_id", "")
    )
    provenance_missing = sorted(
        record.evidence_origin_id
        for record in intelligence.evidence_origin_visibility
        if not record.provenance_reference_id
    )
    return {
        "valid": not records_missing_evidence
        and not lineage_missing
        and not provenance_missing
        and bool(identity.lineage_reference_id)
        and bool(identity.provenance_reference_id),
        "lineage_continuity_preserved": bool(identity.lineage_reference_id)
        and not lineage_missing,
        "provenance_continuity_preserved": bool(identity.provenance_reference_id)
        and not provenance_missing,
        "evidence_continuity_preserved": not records_missing_evidence,
        "records_missing_evidence": records_missing_evidence,
        "records_missing_lineage": lineage_missing,
        "records_missing_provenance": provenance_missing,
    }


def validate_provenance_lineage_serialization_and_hashing(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    first_serialization = serialize_v4_5b_4_provenance_lineage_visibility(
        intelligence
    )
    second_serialization = serialize_v4_5b_4_provenance_lineage_visibility(
        intelligence
    )
    first_hash = hash_v4_5b_4_provenance_lineage_visibility(intelligence)
    second_hash = hash_v4_5b_4_provenance_lineage_visibility(intelligence)
    identity_hash = hash_provenance_lineage_visibility_identity(
        intelligence.visibility_identity
    )
    return {
        "valid": first_serialization == second_serialization
        and first_hash == second_hash
        and len(first_hash) == 64
        and len(identity_hash) == 64,
        "provenance_serialization_stable": first_serialization == second_serialization,
        "lineage_serialization_stable": first_serialization == second_serialization,
        "provenance_hashing_stable": first_hash == second_hash,
        "lineage_hashing_stable": first_hash == second_hash,
        "provenance_lineage_visibility_hash": first_hash,
        "provenance_lineage_identity_hash": identity_hash,
    }


def validate_fail_visible_provenance_lineage_diagnostics(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    diagnostics = intelligence.provenance_lineage_diagnostics
    unsupported = intelligence.unsupported_operational_state_visibility
    diagnostic_types = {record.diagnostic_type for record in diagnostics}
    unsupported_states = {record.unsupported_state for record in unsupported}
    missing_diagnostic_types = sorted(
        set(PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES) - diagnostic_types
    )
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES) - unsupported_states
    )
    unsafe_diagnostic_ids = sorted(
        record.diagnostic_id
        for record in diagnostics
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.silent_fallback_enabled
            or record.hidden_fallback_enabled
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
        for record in unsupported
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
            or record.suppression_enabled
        )
    )
    return {
        "valid": not (
            missing_diagnostic_types
            or missing_unsupported_states
            or unsafe_diagnostic_ids
            or unsafe_unsupported_ids
        ),
        "provenance_lineage_diagnostic_count": len(diagnostics),
        "unsupported_operational_state_count": len(unsupported),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_ids": unsafe_unsupported_ids,
        "fail_visible": all(record.fail_visible for record in diagnostics)
        and all(record.fail_visible for record in unsupported),
        "silent_fallback_enabled_count": sum(
            1 for record in diagnostics if record.silent_fallback_enabled
        ),
        "hidden_fallback_enabled_count": sum(
            1 for record in diagnostics if record.hidden_fallback_enabled
        ),
        "authorization_enabled_count": sum(
            1 for record in diagnostics if record.authorization_enabled
        )
        + sum(1 for record in unsupported if record.authorization_enabled),
        "approval_enabled_count": sum(
            1 for record in diagnostics if record.approval_enabled
        )
        + sum(1 for record in unsupported if record.approval_enabled),
        "ranking_enabled_count": sum(
            1 for record in diagnostics if record.ranking_enabled
        )
        + sum(1 for record in unsupported if record.ranking_enabled),
        "recommendation_enabled_count": sum(
            1 for record in diagnostics if record.recommendation_enabled
        )
        + sum(1 for record in unsupported if record.recommendation_enabled),
    }


def validate_descriptive_only_provenance_lineage_guarantees(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    counters = provenance_lineage_capability_counter_values(intelligence)
    enabled_flags = enabled_provenance_lineage_capability_flags(intelligence)
    descriptive_failures = sorted(
        _record_id(item)
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_DISABLED_COUNTER_NAMES)
        - set(counters)
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
    statement_valid = (
        intelligence.provenance_lineage_visibility_statement
        == PROVENANCE_LINEAGE_VISIBILITY_STATEMENT
        and intelligence.source_visibility_non_authority_statement
        == SOURCE_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    return {
        "valid": (
            not enabled_flags
            and all(value == 0 for value in counters.values())
            and not descriptive_failures
            and not missing_disabled_counters
            and all(required_repository_states.values())
            and intelligence.publicly_transparent
            and statement_valid
        ),
        "enabled_flags": enabled_flags,
        "counters": counters,
        "descriptive_failures": descriptive_failures,
        "missing_disabled_counters": missing_disabled_counters,
        "repository_remains": required_repository_states,
        "publicly_transparent": intelligence.publicly_transparent,
        "provenance_lineage_visibility_statement": (
            intelligence.provenance_lineage_visibility_statement
        ),
        "source_visibility_non_authority_statement": (
            intelligence.source_visibility_non_authority_statement
        ),
        "statement_valid": statement_valid,
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "explicit_limitation_count": len(intelligence.explicit_limitations),
    }


def validate_v4_5b_4_provenance_lineage_visibility(
    intelligence: ProvenanceLineageVisibilityIntelligence | None = None,
) -> dict[str, Any]:
    if intelligence is None:
        intelligence = build_v4_5b_4_provenance_lineage_visibility()
    validations = {
        "required_visibility": validate_required_provenance_lineage_visibility(
            intelligence
        ),
        "ordering_stability": validate_provenance_lineage_ordering_stability(
            intelligence
        ),
        "provenance_identity_integrity": validate_provenance_identity_integrity(
            intelligence
        ),
        "lineage_identity_integrity": validate_lineage_identity_integrity(
            intelligence
        ),
        "source_to_surface": validate_source_to_surface_visibility_stability(
            intelligence
        ),
        "evidence_origin": validate_evidence_origin_visibility_preservation(
            intelligence
        ),
        "support_status_lineage": validate_support_status_lineage_preservation(
            intelligence
        ),
        "explainability_lineage": validate_explainability_lineage_preservation(
            intelligence
        ),
        "trust_summary_lineage": validate_trust_summary_lineage_preservation(
            intelligence
        ),
        "stale_unknown_provenance": (
            validate_stale_unknown_provenance_visibility_preservation(intelligence)
        ),
        "provenance_lineage_summary": validate_provenance_lineage_summary_stability(
            intelligence
        ),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_hashing": validate_provenance_lineage_serialization_and_hashing(
            intelligence
        ),
        "fail_visible_provenance_lineage": (
            validate_fail_visible_provenance_lineage_diagnostics(intelligence)
        ),
        "descriptive_only_guarantees": (
            validate_descriptive_only_provenance_lineage_guarantees(intelligence)
        ),
    }
    failed_validations = sorted(
        name for name, result in validations.items() if not result["valid"]
    )
    return {
        "valid": not failed_validations,
        "foundation_status": (
            V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_STATUS_STABLE
            if not failed_validations
            else V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_STATUS_BLOCKED
        ),
        "validation_error_count": len(failed_validations),
        "failed_validations": failed_validations,
        "validations": validations,
    }


def build_v4_5b_4_provenance_lineage_visibility_report() -> dict[str, Any]:
    intelligence = build_v4_5b_4_provenance_lineage_visibility()
    exported = export_v4_5b_4_provenance_lineage_visibility(intelligence)
    validation = validate_v4_5b_4_provenance_lineage_visibility(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    source = validation["validations"]["source_to_surface"]
    evidence = validation["validations"]["evidence_origin"]
    support = validation["validations"]["support_status_lineage"]
    explainability = validation["validations"]["explainability_lineage"]
    trust = validation["validations"]["trust_summary_lineage"]
    stale_unknown = validation["validations"]["stale_unknown_provenance"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_provenance_lineage"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "provenance_lineage_identity_hash": hash_provenance_lineage_visibility_identity(
            intelligence.visibility_identity
        ),
        "provenance_lineage_visibility_hash": (
            hash_v4_5b_4_provenance_lineage_visibility(intelligence)
        ),
        "provenance_visibility_hashes": {
            record.provenance_record_id: hash_provenance_visibility_record(record)
            for record in sorted(
                intelligence.provenance_visibility_records,
                key=lambda item: (item.deterministic_order, item.provenance_record_id),
            )
        },
        "lineage_visibility_hashes": {
            record.lineage_record_id: hash_lineage_visibility_record(record)
            for record in sorted(
                intelligence.lineage_visibility_records,
                key=lambda item: (item.deterministic_order, item.lineage_record_id),
            )
        },
        "source_to_surface_hashes": {
            record.source_surface_id: hash_source_to_surface_visibility(record)
            for record in sorted(
                intelligence.source_to_surface_visibility,
                key=lambda item: (item.deterministic_order, item.source_surface_id),
            )
        },
        "evidence_origin_hashes": {
            record.evidence_origin_id: hash_evidence_origin_visibility(record)
            for record in sorted(
                intelligence.evidence_origin_visibility,
                key=lambda item: (item.deterministic_order, item.evidence_origin_id),
            )
        },
        "support_status_lineage_hashes": {
            record.support_lineage_id: hash_support_status_lineage_visibility(record)
            for record in sorted(
                intelligence.support_status_lineage_visibility,
                key=lambda item: (item.deterministic_order, item.support_lineage_id),
            )
        },
        "explainability_lineage_hashes": {
            record.explainability_lineage_id: (
                hash_explainability_lineage_visibility(record)
            )
            for record in sorted(
                intelligence.explainability_lineage_visibility,
                key=lambda item: (
                    item.deterministic_order,
                    item.explainability_lineage_id,
                ),
            )
        },
        "trust_summary_lineage_hashes": {
            record.trust_lineage_id: hash_trust_summary_lineage_visibility(record)
            for record in sorted(
                intelligence.trust_summary_lineage_visibility,
                key=lambda item: (item.deterministic_order, item.trust_lineage_id),
            )
        },
        "stale_unknown_provenance_hashes": {
            record.stale_unknown_id: hash_stale_unknown_provenance_visibility(record)
            for record in sorted(
                intelligence.stale_unknown_provenance_visibility,
                key=lambda item: (item.deterministic_order, item.stale_unknown_id),
            )
        },
        "provenance_lineage_summary_hashes": {
            record.summary_record_id: hash_provenance_lineage_summary_record(record)
            for record in sorted(
                intelligence.provenance_lineage_summaries,
                key=lambda item: (item.deterministic_order, item.summary_record_id),
            )
        },
        "provenance_lineage_diagnostic_hashes": {
            record.diagnostic_id: hash_provenance_lineage_diagnostic_record(record)
            for record in sorted(
                intelligence.provenance_lineage_diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_operational_hashes": {
            record.state_id: (
                hash_unsupported_provenance_lineage_operational_state_visibility(record)
            )
            for record in sorted(
                intelligence.unsupported_operational_state_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "provenance_visibility_record_count": len(
            intelligence.provenance_visibility_records
        ),
        "lineage_visibility_record_count": len(intelligence.lineage_visibility_records),
        "source_to_surface_count": len(intelligence.source_to_surface_visibility),
        "evidence_origin_count": len(intelligence.evidence_origin_visibility),
        "support_status_lineage_count": len(
            intelligence.support_status_lineage_visibility
        ),
        "explainability_lineage_count": len(
            intelligence.explainability_lineage_visibility
        ),
        "trust_summary_lineage_count": len(
            intelligence.trust_summary_lineage_visibility
        ),
        "stale_unknown_provenance_count": len(
            intelligence.stale_unknown_provenance_visibility
        ),
        "provenance_lineage_summary_count": len(
            intelligence.provenance_lineage_summaries
        ),
        "provenance_lineage_diagnostic_count": len(
            intelligence.provenance_lineage_diagnostics
        ),
        "unsupported_operational_state_count": len(
            intelligence.unsupported_operational_state_visibility
        ),
        "source_counts": required_visibility["source_counts"],
        "evidence_counts": required_visibility["evidence_counts"],
        "support_counts": required_visibility["support_counts"],
        "explainability_counts": required_visibility["explainability_counts"],
        "trust_counts": required_visibility["trust_counts"],
        "stale_unknown_counts": required_visibility["stale_unknown_counts"],
        "summary_counts": required_visibility["summary_counts"],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_provenance_serialization_verified": serialization_hashing[
            "provenance_serialization_stable"
        ],
        "deterministic_lineage_serialization_verified": serialization_hashing[
            "lineage_serialization_stable"
        ],
        "deterministic_provenance_hashing_verified": serialization_hashing[
            "provenance_hashing_stable"
        ],
        "deterministic_lineage_hashing_verified": serialization_hashing[
            "lineage_hashing_stable"
        ],
        "source_to_surface_visibility_stable": source["valid"],
        "evidence_origin_visibility_preserved": evidence["valid"],
        "support_status_lineage_preserved": support["valid"],
        "explainability_lineage_preserved": explainability["valid"],
        "trust_summary_lineage_preserved": trust["valid"],
        "stale_unknown_provenance_visibility_preserved": stale_unknown["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "evidence_continuity_preserved": lineage_provenance[
            "evidence_continuity_preserved"
        ],
        "fail_visible_provenance_diagnostics_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "publicly_transparent": descriptive_only["publicly_transparent"],
        "provenance_lineage_visibility_statement": (
            descriptive_only["provenance_lineage_visibility_statement"]
        ),
        "source_visibility_non_authority_statement": (
            descriptive_only["source_visibility_non_authority_statement"]
        ),
        "inherited_prohibition_count": descriptive_only[
            "inherited_prohibition_count"
        ],
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
    }
    summary.update(counters)
    report = {
        "phase_id": V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PHASE_ID,
        "schema_version": V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_GENERATED_AT,
        "purpose": V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PURPOSE,
        "foundation_status": validation["foundation_status"],
        "summary": summary,
        "visibility": {
            "provenance": provenance_visibility_summary(
                intelligence.provenance_visibility_records
            ),
            "lineage": lineage_visibility_summary(
                intelligence.lineage_visibility_records
            ),
            "source_to_surface": source_to_surface_summary(
                intelligence.source_to_surface_visibility
            ),
            "evidence_origin": evidence_origin_summary(
                intelligence.evidence_origin_visibility
            ),
            "support_status_lineage": support_status_lineage_summary(
                intelligence.support_status_lineage_visibility
            ),
            "explainability_lineage": explainability_lineage_summary(
                intelligence.explainability_lineage_visibility
            ),
            "trust_summary_lineage": trust_summary_lineage_summary(
                intelligence.trust_summary_lineage_visibility
            ),
            "stale_unknown_provenance": stale_unknown_provenance_summary(
                intelligence.stale_unknown_provenance_visibility
            ),
            "provenance_lineage_summaries": provenance_lineage_summary_visibility(
                intelligence.provenance_lineage_summaries
            ),
            "provenance_lineage_diagnostics": provenance_lineage_diagnostic_summary(
                intelligence.provenance_lineage_diagnostics
            ),
            "unsupported_operational_states": unsupported_operational_state_summary(
                intelligence.unsupported_operational_state_visibility
            ),
            "descriptive_only": descriptive_only_provenance_lineage_summary(
                intelligence
            ),
        },
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "validation": validation,
        "exported_intelligence": exported,
    }
    report["deterministic_report_hash"] = (
        deterministic_v4_5b_4_provenance_lineage_visibility_hash(report)
    )
    return report


def contaminate_v4_5b_4_provenance_lineage_visibility_for_non_operational_validation(
    intelligence: ProvenanceLineageVisibilityIntelligence | None = None,
) -> ProvenanceLineageVisibilityIntelligence:
    if intelligence is None:
        intelligence = build_v4_5b_4_provenance_lineage_visibility()
    return replace(
        intelligence,
        runtime_execution_enabled=True,
        source_authorization_enabled=True,
        source_approval_enabled=True,
        provenance_ranking_enabled=True,
        lineage_recommendation_enabled=True,
        remediation_enabled=True,
        planner_integration_enabled=True,
    )
