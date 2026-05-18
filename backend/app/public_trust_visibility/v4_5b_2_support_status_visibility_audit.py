"""Audit for deterministic v4.5B.2 support status visibility.

The audit validates descriptive support status visibility only. It does not
authorize, approve, execute, dispatch, route, traverse, schedule, sequence,
decide, recommend, rank, remediate, repair, mitigate, correct, integrate
planners, consume production paths, or mutate runtime or operational state.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5b_2_support_status_visibility_hashing import (
    deterministic_v4_5b_2_support_status_visibility_hash,
    hash_continuity_support_visibility,
    hash_evidence_based_support_visibility,
    hash_experimental_deprecated_visibility,
    hash_explainability_support_visibility,
    hash_public_support_surface_visibility,
    hash_support_classification_visibility,
    hash_support_diagnostic_record,
    hash_support_status_identity,
    hash_support_summary_record,
    hash_support_visibility_record,
    hash_unsupported_support_operational_state_visibility,
    hash_unsupported_support_state_visibility,
    hash_v4_5b_2_support_status_visibility,
)
from .v4_5b_2_support_status_visibility_models import (
    CONTINUITY_SUPPORT_VISIBILITY_TYPES,
    EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES,
    EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES,
    EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES,
    PUBLIC_SUPPORT_SURFACE_TYPES,
    SUPPORT_CLASSIFICATION_NON_AUTHORITY_STATEMENT,
    SUPPORT_CLASSIFICATION_TYPES,
    SUPPORT_DIAGNOSTIC_TYPES,
    SUPPORT_STATUS_VISIBILITY_STATEMENT,
    SUPPORT_SUMMARY_TYPES,
    UNSUPPORTED_SUPPORT_OPERATIONAL_STATES,
    UNSUPPORTED_SUPPORT_STATE_TYPES,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_DISABLED_COUNTER_NAMES,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_GENERATED_AT,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_PHASE_ID,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_PURPOSE,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_REPORT_SCHEMA_VERSION,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_STATUS_BLOCKED,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_STATUS_STABLE,
    SupportStatusVisibilityIntelligence,
    default_v4_5b_2_support_status_visibility,
)
from .v4_5b_2_support_status_visibility_serialization import (
    export_v4_5b_2_support_status_visibility,
    serialize_v4_5b_2_support_status_visibility,
)
from .v4_5b_2_support_status_visibility_visibility import (
    continuity_support_summary,
    descriptive_only_support_status_summary,
    evidence_based_support_summary,
    experimental_deprecated_summary,
    explainability_support_summary,
    support_classification_summary,
    support_diagnostic_summary,
    support_summary_visibility,
    support_surface_summary,
    support_visibility_summary,
    unsupported_operational_state_summary,
    unsupported_state_summary,
    validate_required_support_status_visibility,
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
    "enabled_support_authorization_count": (
        "support_authorization_enabled",
        "support_authority_enabled",
        "authorization_enabled",
    ),
    "enabled_support_approval_count": (
        "support_approval_enabled",
        "approval_enabled",
        "operational_approval_enabled",
    ),
    "enabled_support_ranking_count": (
        "support_ranking_enabled",
        "ranking_enabled",
        "trust_scoring_enabled",
    ),
    "enabled_support_recommendation_count": (
        "support_recommendation_enabled",
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
    ),
}

PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_5b_2_support_status_visibility() -> SupportStatusVisibilityIntelligence:
    return default_v4_5b_2_support_status_visibility()


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


def enabled_support_status_capability_flags(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "support_record_id", None)
            or getattr(item, "classification_visibility_id", None)
            or getattr(item, "surface_visibility_id", None)
            or getattr(item, "unsupported_visibility_id", None)
            or getattr(item, "experimental_deprecated_id", None)
            or getattr(item, "evidence_support_id", None)
            or getattr(item, "explainability_support_id", None)
            or getattr(item, "continuity_support_id", None)
            or getattr(item, "support_summary_record_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "support_status_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def support_status_capability_counter_values(
    intelligence: SupportStatusVisibilityIntelligence,
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


def support_status_visibility_equal(
    left: SupportStatusVisibilityIntelligence,
    right: SupportStatusVisibilityIntelligence,
) -> bool:
    return serialize_v4_5b_2_support_status_visibility(
        left
    ) == serialize_v4_5b_2_support_status_visibility(right)


def validate_support_status_ordering_stability(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "support_visibility_records": tuple(
            record.deterministic_order for record in intelligence.support_visibility_records
        ),
        "support_classifications": tuple(
            record.deterministic_order for record in intelligence.support_classifications
        ),
        "support_surfaces": tuple(
            record.deterministic_order for record in intelligence.support_surfaces
        ),
        "unsupported_state_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_state_visibility
        ),
        "experimental_deprecated_visibility": tuple(
            record.deterministic_order
            for record in intelligence.experimental_deprecated_visibility
        ),
        "evidence_based_support_visibility": tuple(
            record.deterministic_order
            for record in intelligence.evidence_based_support_visibility
        ),
        "explainability_support_visibility": tuple(
            record.deterministic_order
            for record in intelligence.explainability_support_visibility
        ),
        "continuity_support_visibility": tuple(
            record.deterministic_order
            for record in intelligence.continuity_support_visibility
        ),
        "support_summaries": tuple(
            record.deterministic_order for record in intelligence.support_summaries
        ),
        "support_diagnostics": tuple(
            record.deterministic_order for record in intelligence.support_diagnostics
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


def validate_support_identity_integrity(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    identity = intelligence.support_identity
    required_values = {
        "support_status_id": identity.support_status_id,
        "support_summary_id": identity.support_summary_id,
        "support_scope_id": identity.support_scope_id,
        "support_reference_id": identity.support_reference_id,
        "evidence_reference_id": identity.evidence_reference_id,
        "explainability_reference_id": identity.explainability_reference_id,
        "continuity_reference_id": identity.continuity_reference_id,
        "diagnostics_reference_id": identity.diagnostics_reference_id,
        "lineage_reference_id": identity.lineage_reference_id,
        "provenance_reference_id": identity.provenance_reference_id,
    }
    missing_fields = sorted(key for key, value in required_values.items() if not value)
    source_report_present = _relative_path_exists(
        identity.source_trust_visibility_report_reference
    )
    source_report_hash_matches = _report_hash_matches(
        identity.source_trust_visibility_report_reference,
        identity.source_trust_visibility_hash_reference,
    )
    return {
        "valid": not missing_fields
        and identity.phase_id == V4_5B_2_SUPPORT_STATUS_VISIBILITY_PHASE_ID
        and source_report_present
        and source_report_hash_matches,
        "missing_identity_fields": missing_fields,
        "phase_id": identity.phase_id,
        "schema_version": identity.schema_version,
        "source_report_present": source_report_present,
        "source_report_hash_matches": source_report_hash_matches,
    }


def validate_support_classification_stability(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.support_classifications
    present = {record.support_classification for record in records}
    missing_types = sorted(set(SUPPORT_CLASSIFICATION_TYPES) - present)
    unsafe_ids = sorted(
        record.classification_visibility_id
        for record in records
        if (
            not record.descriptive_only
            or record.operational_approval_enabled
            or record.execution_semantics_enabled
            or record.authorization_enabled
            or record.approval_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "support_classification_count": len(records),
        "missing_classifications": missing_types,
        "unsafe_classification_ids": unsafe_ids,
    }


def validate_public_support_surface_visibility(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.support_surfaces
    present = {record.support_surface for record in records}
    missing_types = sorted(set(PUBLIC_SUPPORT_SURFACE_TYPES) - present)
    unsafe_ids = sorted(
        record.surface_visibility_id
        for record in records
        if (
            record.support_classification not in SUPPORT_CLASSIFICATION_TYPES
            or not record.descriptive_only
            or record.ranking_enabled
            or record.recommendation_enabled
            or record.operational_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "support_surface_count": len(records),
        "missing_surfaces": missing_types,
        "unsafe_surface_ids": unsafe_ids,
    }


def validate_unsupported_state_visibility_preservation(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.unsupported_state_visibility
    present = {record.unsupported_state_type for record in records}
    missing_types = sorted(set(UNSUPPORTED_SUPPORT_STATE_TYPES) - present)
    unsafe_ids = sorted(
        record.unsupported_visibility_id
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
        "unsupported_state_visibility_count": len(records),
        "missing_unsupported_state_types": missing_types,
        "unsafe_unsupported_state_ids": unsafe_ids,
    }


def validate_experimental_deprecated_visibility_preservation(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.experimental_deprecated_visibility
    present = {record.visibility_type for record in records}
    missing_types = sorted(set(EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.experimental_deprecated_id
        for record in records
        if (
            not record.descriptive_only
            or record.automatic_migration_enabled
            or record.operational_fallback_enabled
            or record.authorization_enabled
            or record.approval_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "experimental_deprecated_count": len(records),
        "missing_experimental_deprecated_types": missing_types,
        "unsafe_experimental_deprecated_ids": unsafe_ids,
    }


def validate_evidence_based_support_visibility(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.evidence_based_support_visibility
    present = {record.evidence_support_type for record in records}
    missing_types = sorted(set(EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.evidence_support_id
        for record in records
        if (
            not record.descriptive_only
            or not record.replay_safe
            or not record.provenance_safe
            or record.trust_scoring_enabled
            or record.approval_enabled
            or record.authorization_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "evidence_based_support_count": len(records),
        "missing_evidence_support_types": missing_types,
        "unsafe_evidence_support_ids": unsafe_ids,
    }


def validate_explainability_support_visibility(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.explainability_support_visibility
    present = {record.explainability_support_type for record in records}
    missing_types = sorted(set(EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.explainability_support_id
        for record in records
        if (
            not record.descriptive_only
            or record.recommendation_enabled
            or record.operational_semantics_enabled
            or record.authorization_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "explainability_support_count": len(records),
        "missing_explainability_support_types": missing_types,
        "unsafe_explainability_support_ids": unsafe_ids,
    }


def validate_continuity_support_visibility(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.continuity_support_visibility
    present = {record.continuity_support_type for record in records}
    missing_types = sorted(set(CONTINUITY_SUPPORT_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.continuity_support_id
        for record in records
        if (
            not record.continuity_reference_id
            or not record.descriptive_only
            or record.restoration_enabled
            or record.repair_enabled
            or record.remediation_enabled
            or record.authorization_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "continuity_support_count": len(records),
        "missing_continuity_support_types": missing_types,
        "unsafe_continuity_support_ids": unsafe_ids,
    }


def validate_support_summary_stability(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    records = intelligence.support_summaries
    present = {record.summary_type for record in records}
    missing_types = sorted(set(SUPPORT_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.support_summary_record_id
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
        "support_summary_count": len(records),
        "missing_summary_types": missing_types,
        "unsafe_summary_ids": unsafe_ids,
    }


def validate_lineage_and_provenance_preservation(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    identity = intelligence.support_identity
    missing_lineage = not bool(identity.lineage_reference_id)
    missing_provenance = not bool(identity.provenance_reference_id)
    missing_continuity = not bool(identity.continuity_reference_id)
    missing_evidence = sorted(
        str(
            getattr(item, "classification_visibility_id", None)
            or getattr(item, "surface_visibility_id", None)
            or getattr(item, "unsupported_visibility_id", None)
            or getattr(item, "experimental_deprecated_id", None)
            or getattr(item, "evidence_support_id", None)
            or getattr(item, "explainability_support_id", None)
            or getattr(item, "continuity_support_id", None)
            or getattr(item, "support_summary_record_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", "")
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "evidence_reference_ids")
        and not tuple(getattr(item, "evidence_reference_ids"))
    )
    return {
        "valid": not (
            missing_lineage
            or missing_provenance
            or missing_continuity
            or missing_evidence
        ),
        "lineage_continuity_preserved": not missing_lineage,
        "provenance_continuity_preserved": not missing_provenance,
        "continuity_reference_preserved": not missing_continuity,
        "evidence_continuity_preserved": not missing_evidence,
        "missing_evidence_reference_ids": missing_evidence,
    }


def validate_support_status_serialization_and_hashing(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    first_serialization = serialize_v4_5b_2_support_status_visibility(intelligence)
    second_serialization = serialize_v4_5b_2_support_status_visibility(intelligence)
    first_hash = hash_v4_5b_2_support_status_visibility(intelligence)
    second_hash = hash_v4_5b_2_support_status_visibility(intelligence)
    rebuilt_hash = hash_v4_5b_2_support_status_visibility(
        build_v4_5b_2_support_status_visibility()
    )
    return {
        "valid": (
            first_serialization == second_serialization
            and first_hash == second_hash
            and first_hash == rebuilt_hash
        ),
        "serialization_stable": first_serialization == second_serialization,
        "hashing_stable": first_hash == second_hash == rebuilt_hash,
        "support_status_hash": first_hash,
        "rebuilt_support_status_hash": rebuilt_hash,
        "serialization_length": len(first_serialization),
    }


def validate_fail_visible_support_diagnostics(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    diagnostics = intelligence.support_diagnostics
    unsupported = intelligence.unsupported_operational_state_visibility
    missing_diagnostic_types = sorted(
        set(SUPPORT_DIAGNOSTIC_TYPES) - {record.diagnostic_type for record in diagnostics}
    )
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_SUPPORT_OPERATIONAL_STATES)
        - {record.unsupported_state for record in unsupported}
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
        "support_diagnostic_count": len(diagnostics),
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


def validate_descriptive_only_support_guarantees(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    counters = support_status_capability_counter_values(intelligence)
    enabled_flags = enabled_support_status_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "support_record_id", None)
            or getattr(item, "classification_visibility_id", None)
            or getattr(item, "surface_visibility_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "support_status_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5B_2_SUPPORT_STATUS_VISIBILITY_DISABLED_COUNTER_NAMES) - set(counters)
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
        intelligence.support_status_visibility_statement
        == SUPPORT_STATUS_VISIBILITY_STATEMENT
        and intelligence.support_classification_non_authority_statement
        == SUPPORT_CLASSIFICATION_NON_AUTHORITY_STATEMENT
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
        "support_status_visibility_statement": (
            intelligence.support_status_visibility_statement
        ),
        "support_classification_non_authority_statement": (
            intelligence.support_classification_non_authority_statement
        ),
        "statement_valid": statement_valid,
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "explicit_limitation_count": len(intelligence.explicit_limitations),
    }


def validate_v4_5b_2_support_status_visibility(
    intelligence: SupportStatusVisibilityIntelligence | None = None,
) -> dict[str, Any]:
    if intelligence is None:
        intelligence = build_v4_5b_2_support_status_visibility()
    validations = {
        "required_visibility": validate_required_support_status_visibility(
            intelligence
        ),
        "ordering_stability": validate_support_status_ordering_stability(
            intelligence
        ),
        "identity_integrity": validate_support_identity_integrity(intelligence),
        "support_classification": validate_support_classification_stability(
            intelligence
        ),
        "support_surface": validate_public_support_surface_visibility(intelligence),
        "unsupported_state_visibility": (
            validate_unsupported_state_visibility_preservation(intelligence)
        ),
        "experimental_deprecated": (
            validate_experimental_deprecated_visibility_preservation(intelligence)
        ),
        "evidence_based_support": validate_evidence_based_support_visibility(
            intelligence
        ),
        "explainability_support": validate_explainability_support_visibility(
            intelligence
        ),
        "continuity_support": validate_continuity_support_visibility(intelligence),
        "support_summary": validate_support_summary_stability(intelligence),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_hashing": validate_support_status_serialization_and_hashing(
            intelligence
        ),
        "fail_visible_support": validate_fail_visible_support_diagnostics(
            intelligence
        ),
        "descriptive_only_guarantees": validate_descriptive_only_support_guarantees(
            intelligence
        ),
    }
    failed_validations = sorted(
        name for name, result in validations.items() if not result["valid"]
    )
    return {
        "valid": not failed_validations,
        "foundation_status": (
            V4_5B_2_SUPPORT_STATUS_VISIBILITY_STATUS_STABLE
            if not failed_validations
            else V4_5B_2_SUPPORT_STATUS_VISIBILITY_STATUS_BLOCKED
        ),
        "validation_error_count": len(failed_validations),
        "failed_validations": failed_validations,
        "validations": validations,
    }


def build_v4_5b_2_support_status_visibility_report() -> dict[str, Any]:
    intelligence = build_v4_5b_2_support_status_visibility()
    exported = export_v4_5b_2_support_status_visibility(intelligence)
    validation = validate_v4_5b_2_support_status_visibility(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    classification = validation["validations"]["support_classification"]
    surface = validation["validations"]["support_surface"]
    unsupported = validation["validations"]["unsupported_state_visibility"]
    experimental = validation["validations"]["experimental_deprecated"]
    evidence = validation["validations"]["evidence_based_support"]
    explainability = validation["validations"]["explainability_support"]
    continuity = validation["validations"]["continuity_support"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_support"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "support_identity_hash": hash_support_status_identity(
            intelligence.support_identity
        ),
        "support_status_hash": hash_v4_5b_2_support_status_visibility(intelligence),
        "support_visibility_record_hashes": {
            record.support_record_id: hash_support_visibility_record(record)
            for record in sorted(
                intelligence.support_visibility_records,
                key=lambda item: (item.deterministic_order, item.support_record_id),
            )
        },
        "support_classification_hashes": {
            record.classification_visibility_id: (
                hash_support_classification_visibility(record)
            )
            for record in sorted(
                intelligence.support_classifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.classification_visibility_id,
                ),
            )
        },
        "support_surface_hashes": {
            record.surface_visibility_id: hash_public_support_surface_visibility(record)
            for record in sorted(
                intelligence.support_surfaces,
                key=lambda item: (item.deterministic_order, item.surface_visibility_id),
            )
        },
        "unsupported_state_hashes": {
            record.unsupported_visibility_id: hash_unsupported_support_state_visibility(
                record
            )
            for record in sorted(
                intelligence.unsupported_state_visibility,
                key=lambda item: (
                    item.deterministic_order,
                    item.unsupported_visibility_id,
                ),
            )
        },
        "experimental_deprecated_hashes": {
            record.experimental_deprecated_id: (
                hash_experimental_deprecated_visibility(record)
            )
            for record in sorted(
                intelligence.experimental_deprecated_visibility,
                key=lambda item: (
                    item.deterministic_order,
                    item.experimental_deprecated_id,
                ),
            )
        },
        "evidence_based_support_hashes": {
            record.evidence_support_id: hash_evidence_based_support_visibility(record)
            for record in sorted(
                intelligence.evidence_based_support_visibility,
                key=lambda item: (item.deterministic_order, item.evidence_support_id),
            )
        },
        "explainability_support_hashes": {
            record.explainability_support_id: hash_explainability_support_visibility(
                record
            )
            for record in sorted(
                intelligence.explainability_support_visibility,
                key=lambda item: (
                    item.deterministic_order,
                    item.explainability_support_id,
                ),
            )
        },
        "continuity_support_hashes": {
            record.continuity_support_id: hash_continuity_support_visibility(record)
            for record in sorted(
                intelligence.continuity_support_visibility,
                key=lambda item: (item.deterministic_order, item.continuity_support_id),
            )
        },
        "support_summary_hashes": {
            record.support_summary_record_id: hash_support_summary_record(record)
            for record in sorted(
                intelligence.support_summaries,
                key=lambda item: (item.deterministic_order, item.support_summary_record_id),
            )
        },
        "support_diagnostic_hashes": {
            record.diagnostic_id: hash_support_diagnostic_record(record)
            for record in sorted(
                intelligence.support_diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_operational_hashes": {
            record.state_id: hash_unsupported_support_operational_state_visibility(
                record
            )
            for record in sorted(
                intelligence.unsupported_operational_state_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "support_visibility_record_count": len(intelligence.support_visibility_records),
        "support_classification_count": len(intelligence.support_classifications),
        "support_surface_count": len(intelligence.support_surfaces),
        "unsupported_state_visibility_count": len(
            intelligence.unsupported_state_visibility
        ),
        "experimental_deprecated_count": len(
            intelligence.experimental_deprecated_visibility
        ),
        "evidence_based_support_count": len(
            intelligence.evidence_based_support_visibility
        ),
        "explainability_support_count": len(
            intelligence.explainability_support_visibility
        ),
        "continuity_support_count": len(intelligence.continuity_support_visibility),
        "support_summary_count": len(intelligence.support_summaries),
        "support_diagnostic_count": len(intelligence.support_diagnostics),
        "unsupported_operational_state_count": len(
            intelligence.unsupported_operational_state_visibility
        ),
        "classification_counts": required_visibility["classification_counts"],
        "surface_counts": required_visibility["surface_counts"],
        "unsupported_counts": required_visibility["unsupported_counts"],
        "experimental_counts": required_visibility["experimental_counts"],
        "evidence_counts": required_visibility["evidence_counts"],
        "explainability_counts": required_visibility["explainability_counts"],
        "continuity_counts": required_visibility["continuity_counts"],
        "summary_counts": required_visibility["summary_counts"],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "support_classification_stable": classification["valid"],
        "support_surface_visibility_stable": surface["valid"],
        "unsupported_state_visibility_preserved": unsupported["valid"],
        "experimental_deprecated_visibility_preserved": experimental["valid"],
        "evidence_based_support_visibility_stable": evidence["valid"],
        "explainability_support_visibility_stable": explainability["valid"],
        "continuity_support_visibility_stable": continuity["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "evidence_continuity_preserved": lineage_provenance[
            "evidence_continuity_preserved"
        ],
        "fail_visible_support_diagnostics_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "publicly_transparent": descriptive_only["publicly_transparent"],
        "support_status_visibility_statement": (
            descriptive_only["support_status_visibility_statement"]
        ),
        "support_classification_non_authority_statement": (
            descriptive_only["support_classification_non_authority_statement"]
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
        "phase_id": V4_5B_2_SUPPORT_STATUS_VISIBILITY_PHASE_ID,
        "schema_version": V4_5B_2_SUPPORT_STATUS_VISIBILITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_5B_2_SUPPORT_STATUS_VISIBILITY_GENERATED_AT,
        "purpose": V4_5B_2_SUPPORT_STATUS_VISIBILITY_PURPOSE,
        "foundation_status": validation["foundation_status"],
        "summary": summary,
        "visibility": {
            "support_status": support_visibility_summary(
                intelligence.support_visibility_records
            ),
            "support_classifications": support_classification_summary(
                intelligence.support_classifications
            ),
            "support_surfaces": support_surface_summary(
                intelligence.support_surfaces
            ),
            "unsupported_states": unsupported_state_summary(
                intelligence.unsupported_state_visibility
            ),
            "experimental_deprecated": experimental_deprecated_summary(
                intelligence.experimental_deprecated_visibility
            ),
            "evidence_based_support": evidence_based_support_summary(
                intelligence.evidence_based_support_visibility
            ),
            "explainability_support": explainability_support_summary(
                intelligence.explainability_support_visibility
            ),
            "continuity_support": continuity_support_summary(
                intelligence.continuity_support_visibility
            ),
            "support_summaries": support_summary_visibility(
                intelligence.support_summaries
            ),
            "support_diagnostics": support_diagnostic_summary(
                intelligence.support_diagnostics
            ),
            "unsupported_operational_states": unsupported_operational_state_summary(
                intelligence.unsupported_operational_state_visibility
            ),
            "descriptive_only": descriptive_only_support_status_summary(
                intelligence
            ),
        },
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "validation": validation,
        "exported_intelligence": exported,
    }
    report["deterministic_report_hash"] = (
        deterministic_v4_5b_2_support_status_visibility_hash(report)
    )
    return report


def contaminate_v4_5b_2_support_status_visibility_for_non_operational_validation(
    intelligence: SupportStatusVisibilityIntelligence | None = None,
) -> SupportStatusVisibilityIntelligence:
    if intelligence is None:
        intelligence = build_v4_5b_2_support_status_visibility()
    return replace(
        intelligence,
        runtime_execution_enabled=True,
        support_authorization_enabled=True,
        support_approval_enabled=True,
        support_ranking_enabled=True,
        support_recommendation_enabled=True,
        remediation_enabled=True,
        planner_integration_enabled=True,
    )
