"""Audit for deterministic v4.5B.3 explainability surfaces.

The audit validates descriptive public explainability surfaces only. It does
not authorize, approve, execute, dispatch, route, traverse, schedule, sequence,
decide, recommend, rank, remediate, repair, mitigate, correct, integrate
planners, consume production paths, or mutate runtime or operational state.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5b_3_explainability_surface_hashing import (
    deterministic_v4_5b_3_explainability_surface_hash,
    hash_continuity_explanation_visibility,
    hash_evidence_to_explanation_mapping,
    hash_explainability_surface_identity,
    hash_explainability_surface_record,
    hash_explanation_diagnostic_record,
    hash_explanation_summary_record,
    hash_limitation_explanation_visibility,
    hash_public_trust_explanation_visibility,
    hash_support_state_explanation_surface,
    hash_unsupported_explanation_operational_state_visibility,
    hash_unsupported_state_explanation_visibility,
    hash_v4_5b_3_explainability_surfaces,
)
from .v4_5b_3_explainability_surface_models import (
    CONTINUITY_EXPLANATION_TYPES,
    EVIDENCE_TO_EXPLANATION_MAPPING_TYPES,
    EXPLANATION_DIAGNOSTIC_TYPES,
    EXPLANATION_SUMMARY_TYPES,
    EXPLAINABILITY_SURFACE_STATEMENT,
    EXPLAINABILITY_VISIBILITY_NON_AUTHORITY_STATEMENT,
    LIMITATION_EXPLANATION_TYPES,
    SUPPORT_STATE_EXPLANATION_TYPES,
    TRUST_EXPLANATION_TYPES,
    UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_EXPLANATION_TYPES,
    V4_5B_3_EXPLAINABILITY_SURFACE_DISABLED_COUNTER_NAMES,
    V4_5B_3_EXPLAINABILITY_SURFACE_GENERATED_AT,
    V4_5B_3_EXPLAINABILITY_SURFACE_PHASE_ID,
    V4_5B_3_EXPLAINABILITY_SURFACE_PURPOSE,
    V4_5B_3_EXPLAINABILITY_SURFACE_REPORT_SCHEMA_VERSION,
    V4_5B_3_EXPLAINABILITY_SURFACE_STATUS_BLOCKED,
    V4_5B_3_EXPLAINABILITY_SURFACE_STATUS_STABLE,
    ExplainabilitySurfaceIntelligence,
    default_v4_5b_3_explainability_surfaces,
)
from .v4_5b_3_explainability_surface_serialization import (
    export_v4_5b_3_explainability_surfaces,
    serialize_v4_5b_3_explainability_surfaces,
)
from .v4_5b_3_explainability_surface_visibility import (
    continuity_explanation_summary,
    descriptive_only_explainability_surface_summary,
    evidence_to_explanation_mapping_summary,
    explanation_diagnostic_summary,
    explanation_summary_visibility,
    explanation_surface_summary,
    limitation_explanation_summary,
    support_state_explanation_summary,
    trust_explanation_summary,
    unsupported_operational_state_summary,
    unsupported_state_explanation_summary,
    validate_required_explainability_surfaces,
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
    "enabled_explainability_authorization_count": (
        "explainability_authorization_enabled",
        "explainability_authority_enabled",
        "authorization_enabled",
    ),
    "enabled_explainability_approval_count": (
        "explainability_approval_enabled",
        "approval_enabled",
        "operational_approval_enabled",
    ),
    "enabled_explainability_ranking_count": (
        "explainability_ranking_enabled",
        "ranking_enabled",
        "trust_scoring_enabled",
    ),
    "enabled_explainability_recommendation_count": (
        "explainability_recommendation_enabled",
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


def build_v4_5b_3_explainability_surfaces() -> ExplainabilitySurfaceIntelligence:
    return default_v4_5b_3_explainability_surfaces()


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
        getattr(item, "surface_record_id", None)
        or getattr(item, "support_state_explanation_id", None)
        or getattr(item, "evidence_mapping_id", None)
        or getattr(item, "limitation_explanation_id", None)
        or getattr(item, "trust_explanation_id", None)
        or getattr(item, "continuity_explanation_id", None)
        or getattr(item, "unsupported_explanation_id", None)
        or getattr(item, "explanation_summary_record_id", None)
        or getattr(item, "diagnostic_id", None)
        or getattr(item, "state_id", None)
        or getattr(item, "explainability_surface_id", item.__class__.__name__)
    )


def enabled_explainability_surface_capability_flags(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(_record_id(item), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def explainability_surface_capability_counter_values(
    intelligence: ExplainabilitySurfaceIntelligence,
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


def explainability_surface_equal(
    left: ExplainabilitySurfaceIntelligence,
    right: ExplainabilitySurfaceIntelligence,
) -> bool:
    return serialize_v4_5b_3_explainability_surfaces(
        left
    ) == serialize_v4_5b_3_explainability_surfaces(right)


def validate_explainability_surface_ordering_stability(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "surface_records": tuple(
            record.deterministic_order for record in intelligence.surface_records
        ),
        "support_state_explanations": tuple(
            record.deterministic_order
            for record in intelligence.support_state_explanations
        ),
        "evidence_to_explanation_mappings": tuple(
            record.deterministic_order
            for record in intelligence.evidence_to_explanation_mappings
        ),
        "limitation_explanations": tuple(
            record.deterministic_order
            for record in intelligence.limitation_explanations
        ),
        "trust_explanations": tuple(
            record.deterministic_order for record in intelligence.trust_explanations
        ),
        "continuity_explanations": tuple(
            record.deterministic_order
            for record in intelligence.continuity_explanations
        ),
        "unsupported_state_explanations": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_state_explanations
        ),
        "explanation_summaries": tuple(
            record.deterministic_order for record in intelligence.explanation_summaries
        ),
        "explanation_diagnostics": tuple(
            record.deterministic_order for record in intelligence.explanation_diagnostics
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


def validate_explainability_identity_integrity(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    identity = intelligence.surface_identity
    required_values = {
        "explainability_surface_id": identity.explainability_surface_id,
        "explanation_summary_id": identity.explanation_summary_id,
        "support_visibility_reference_id": identity.support_visibility_reference_id,
        "evidence_reference_id": identity.evidence_reference_id,
        "continuity_reference_id": identity.continuity_reference_id,
        "trust_summary_reference_id": identity.trust_summary_reference_id,
        "diagnostics_reference_id": identity.diagnostics_reference_id,
        "lineage_reference_id": identity.lineage_reference_id,
        "provenance_reference_id": identity.provenance_reference_id,
    }
    missing_fields = sorted(key for key, value in required_values.items() if not value)
    source_report_present = _relative_path_exists(
        identity.source_support_status_report_reference
    )
    source_report_hash_matches = _report_hash_matches(
        identity.source_support_status_report_reference,
        identity.source_support_status_hash_reference,
    )
    return {
        "valid": not missing_fields
        and identity.phase_id == V4_5B_3_EXPLAINABILITY_SURFACE_PHASE_ID
        and source_report_present
        and source_report_hash_matches,
        "missing_identity_fields": missing_fields,
        "phase_id": identity.phase_id,
        "schema_version": identity.schema_version,
        "source_report_present": source_report_present,
        "source_report_hash_matches": source_report_hash_matches,
    }


def validate_support_state_explanation_visibility(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    records = intelligence.support_state_explanations
    present = {record.explanation_type for record in records}
    missing_types = sorted(set(SUPPORT_STATE_EXPLANATION_TYPES) - present)
    unsafe_ids = sorted(
        record.support_state_explanation_id
        for record in records
        if (
            not record.descriptive_only
            or record.recommendation_enabled
            or record.ranking_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.correctness_guarantee_enabled
            or record.operational_readiness_enabled
            or record.execution_safety_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "support_state_explanation_count": len(records),
        "missing_support_state_explanation_types": missing_types,
        "unsafe_support_state_explanation_ids": unsafe_ids,
    }


def validate_evidence_to_explanation_mapping_stability(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    records = intelligence.evidence_to_explanation_mappings
    present = {record.mapping_type for record in records}
    missing_types = sorted(set(EVIDENCE_TO_EXPLANATION_MAPPING_TYPES) - present)
    unsafe_ids = sorted(
        record.evidence_mapping_id
        for record in records
        if (
            not record.descriptive_only
            or not record.replay_safe
            or not record.provenance_safe
            or not record.evidence_reference_ids
            or not record.explanation_reference_ids
            or record.trust_scoring_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "evidence_mapping_count": len(records),
        "missing_evidence_mapping_types": missing_types,
        "unsafe_evidence_mapping_ids": unsafe_ids,
    }


def validate_limitation_explanation_preservation(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    records = intelligence.limitation_explanations
    present = {record.limitation_type for record in records}
    missing_types = sorted(set(LIMITATION_EXPLANATION_TYPES) - present)
    unsafe_ids = sorted(
        record.limitation_explanation_id
        for record in records
        if (
            not record.descriptive_only
            or record.operational_fallback_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.recommendation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "limitation_explanation_count": len(records),
        "missing_limitation_explanation_types": missing_types,
        "unsafe_limitation_explanation_ids": unsafe_ids,
    }


def validate_trust_explanation_visibility(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    records = intelligence.trust_explanations
    present = {record.trust_explanation_type for record in records}
    missing_types = sorted(set(TRUST_EXPLANATION_TYPES) - present)
    unsafe_ids = sorted(
        record.trust_explanation_id
        for record in records
        if (
            not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.execution_semantics_enabled
            or record.operational_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "trust_explanation_count": len(records),
        "missing_trust_explanation_types": missing_types,
        "unsafe_trust_explanation_ids": unsafe_ids,
    }


def validate_continuity_explanation_visibility(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    records = intelligence.continuity_explanations
    present = {record.continuity_explanation_type for record in records}
    missing_types = sorted(set(CONTINUITY_EXPLANATION_TYPES) - present)
    unsafe_ids = sorted(
        record.continuity_explanation_id
        for record in records
        if (
            not record.continuity_reference_id
            or not record.descriptive_only
            or record.restoration_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.authorization_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "continuity_explanation_count": len(records),
        "missing_continuity_explanation_types": missing_types,
        "unsafe_continuity_explanation_ids": unsafe_ids,
    }


def validate_unsupported_state_explanation_preservation(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    records = intelligence.unsupported_state_explanations
    present = {record.unsupported_state_type for record in records}
    missing_types = sorted(set(UNSUPPORTED_STATE_EXPLANATION_TYPES) - present)
    unsafe_ids = sorted(
        record.unsupported_explanation_id
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
        "unsupported_state_explanation_count": len(records),
        "missing_unsupported_state_explanation_types": missing_types,
        "unsafe_unsupported_state_explanation_ids": unsafe_ids,
    }


def validate_explanation_summary_stability(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    records = intelligence.explanation_summaries
    present = {record.summary_type for record in records}
    missing_types = sorted(set(EXPLANATION_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.explanation_summary_record_id
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
        "explanation_summary_count": len(records),
        "missing_explanation_summary_types": missing_types,
        "unsafe_explanation_summary_ids": unsafe_ids,
    }


def validate_lineage_and_provenance_preservation(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    identity = intelligence.surface_identity
    records_with_evidence = (
        intelligence.support_state_explanations
        + intelligence.evidence_to_explanation_mappings
        + intelligence.limitation_explanations
        + intelligence.trust_explanations
        + intelligence.continuity_explanations
        + intelligence.unsupported_state_explanations
        + intelligence.explanation_summaries
        + intelligence.explanation_diagnostics
        + intelligence.unsupported_operational_state_visibility
    )
    records_missing_evidence = sorted(
        _record_id(record)
        for record in records_with_evidence
        if not getattr(record, "evidence_reference_ids", ())
    )
    continuity_missing = sorted(
        record.continuity_explanation_id
        for record in intelligence.continuity_explanations
        if not record.continuity_reference_id
    )
    return {
        "valid": not records_missing_evidence
        and not continuity_missing
        and bool(identity.lineage_reference_id)
        and bool(identity.provenance_reference_id)
        and bool(identity.evidence_reference_id)
        and bool(identity.continuity_reference_id),
        "lineage_continuity_preserved": bool(identity.lineage_reference_id),
        "provenance_continuity_preserved": bool(identity.provenance_reference_id),
        "evidence_continuity_preserved": not records_missing_evidence,
        "continuity_reference_preserved": not continuity_missing,
        "records_missing_evidence": records_missing_evidence,
        "continuity_records_missing_references": continuity_missing,
    }


def validate_explainability_surface_serialization_and_hashing(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    first_serialization = serialize_v4_5b_3_explainability_surfaces(intelligence)
    second_serialization = serialize_v4_5b_3_explainability_surfaces(intelligence)
    first_hash = hash_v4_5b_3_explainability_surfaces(intelligence)
    second_hash = hash_v4_5b_3_explainability_surfaces(intelligence)
    return {
        "valid": first_serialization == second_serialization
        and first_hash == second_hash
        and len(first_hash) == 64,
        "serialization_stable": first_serialization == second_serialization,
        "hashing_stable": first_hash == second_hash,
        "explainability_surface_hash": first_hash,
    }


def validate_fail_visible_explanation_diagnostics(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    diagnostics = intelligence.explanation_diagnostics
    unsupported = intelligence.unsupported_operational_state_visibility
    diagnostic_types = {record.diagnostic_type for record in diagnostics}
    unsupported_states = {record.unsupported_state for record in unsupported}
    missing_diagnostic_types = sorted(set(EXPLANATION_DIAGNOSTIC_TYPES) - diagnostic_types)
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES) - unsupported_states
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
        "explanation_diagnostic_count": len(diagnostics),
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


def validate_descriptive_only_explainability_guarantees(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    counters = explainability_surface_capability_counter_values(intelligence)
    enabled_flags = enabled_explainability_surface_capability_flags(intelligence)
    descriptive_failures = sorted(
        _record_id(item)
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5B_3_EXPLAINABILITY_SURFACE_DISABLED_COUNTER_NAMES) - set(counters)
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
        intelligence.explainability_surface_statement
        == EXPLAINABILITY_SURFACE_STATEMENT
        and intelligence.explainability_visibility_non_authority_statement
        == EXPLAINABILITY_VISIBILITY_NON_AUTHORITY_STATEMENT
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
        "explainability_surface_statement": (
            intelligence.explainability_surface_statement
        ),
        "explainability_visibility_non_authority_statement": (
            intelligence.explainability_visibility_non_authority_statement
        ),
        "statement_valid": statement_valid,
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "explicit_limitation_count": len(intelligence.explicit_limitations),
    }


def validate_v4_5b_3_explainability_surfaces(
    intelligence: ExplainabilitySurfaceIntelligence | None = None,
) -> dict[str, Any]:
    if intelligence is None:
        intelligence = build_v4_5b_3_explainability_surfaces()
    validations = {
        "required_visibility": validate_required_explainability_surfaces(intelligence),
        "ordering_stability": validate_explainability_surface_ordering_stability(
            intelligence
        ),
        "identity_integrity": validate_explainability_identity_integrity(intelligence),
        "support_state_explanations": validate_support_state_explanation_visibility(
            intelligence
        ),
        "evidence_to_explanation_mapping": (
            validate_evidence_to_explanation_mapping_stability(intelligence)
        ),
        "limitation_explanations": validate_limitation_explanation_preservation(
            intelligence
        ),
        "trust_explanations": validate_trust_explanation_visibility(intelligence),
        "continuity_explanations": validate_continuity_explanation_visibility(
            intelligence
        ),
        "unsupported_state_explanations": (
            validate_unsupported_state_explanation_preservation(intelligence)
        ),
        "explanation_summary": validate_explanation_summary_stability(intelligence),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_hashing": (
            validate_explainability_surface_serialization_and_hashing(intelligence)
        ),
        "fail_visible_explanations": validate_fail_visible_explanation_diagnostics(
            intelligence
        ),
        "descriptive_only_guarantees": (
            validate_descriptive_only_explainability_guarantees(intelligence)
        ),
    }
    failed_validations = sorted(
        name for name, result in validations.items() if not result["valid"]
    )
    return {
        "valid": not failed_validations,
        "foundation_status": (
            V4_5B_3_EXPLAINABILITY_SURFACE_STATUS_STABLE
            if not failed_validations
            else V4_5B_3_EXPLAINABILITY_SURFACE_STATUS_BLOCKED
        ),
        "validation_error_count": len(failed_validations),
        "failed_validations": failed_validations,
        "validations": validations,
    }


def build_v4_5b_3_explainability_surfaces_report() -> dict[str, Any]:
    intelligence = build_v4_5b_3_explainability_surfaces()
    exported = export_v4_5b_3_explainability_surfaces(intelligence)
    validation = validate_v4_5b_3_explainability_surfaces(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    support = validation["validations"]["support_state_explanations"]
    mapping = validation["validations"]["evidence_to_explanation_mapping"]
    limitation = validation["validations"]["limitation_explanations"]
    trust = validation["validations"]["trust_explanations"]
    continuity = validation["validations"]["continuity_explanations"]
    unsupported = validation["validations"]["unsupported_state_explanations"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_explanations"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "surface_identity_hash": hash_explainability_surface_identity(
            intelligence.surface_identity
        ),
        "explainability_surface_hash": hash_v4_5b_3_explainability_surfaces(
            intelligence
        ),
        "surface_record_hashes": {
            record.surface_record_id: hash_explainability_surface_record(record)
            for record in sorted(
                intelligence.surface_records,
                key=lambda item: (item.deterministic_order, item.surface_record_id),
            )
        },
        "support_state_explanation_hashes": {
            record.support_state_explanation_id: (
                hash_support_state_explanation_surface(record)
            )
            for record in sorted(
                intelligence.support_state_explanations,
                key=lambda item: (
                    item.deterministic_order,
                    item.support_state_explanation_id,
                ),
            )
        },
        "evidence_to_explanation_mapping_hashes": {
            record.evidence_mapping_id: hash_evidence_to_explanation_mapping(record)
            for record in sorted(
                intelligence.evidence_to_explanation_mappings,
                key=lambda item: (item.deterministic_order, item.evidence_mapping_id),
            )
        },
        "limitation_explanation_hashes": {
            record.limitation_explanation_id: hash_limitation_explanation_visibility(
                record
            )
            for record in sorted(
                intelligence.limitation_explanations,
                key=lambda item: (item.deterministic_order, item.limitation_explanation_id),
            )
        },
        "trust_explanation_hashes": {
            record.trust_explanation_id: hash_public_trust_explanation_visibility(
                record
            )
            for record in sorted(
                intelligence.trust_explanations,
                key=lambda item: (item.deterministic_order, item.trust_explanation_id),
            )
        },
        "continuity_explanation_hashes": {
            record.continuity_explanation_id: hash_continuity_explanation_visibility(
                record
            )
            for record in sorted(
                intelligence.continuity_explanations,
                key=lambda item: (
                    item.deterministic_order,
                    item.continuity_explanation_id,
                ),
            )
        },
        "unsupported_state_explanation_hashes": {
            record.unsupported_explanation_id: (
                hash_unsupported_state_explanation_visibility(record)
            )
            for record in sorted(
                intelligence.unsupported_state_explanations,
                key=lambda item: (
                    item.deterministic_order,
                    item.unsupported_explanation_id,
                ),
            )
        },
        "explanation_summary_hashes": {
            record.explanation_summary_record_id: hash_explanation_summary_record(record)
            for record in sorted(
                intelligence.explanation_summaries,
                key=lambda item: (
                    item.deterministic_order,
                    item.explanation_summary_record_id,
                ),
            )
        },
        "explanation_diagnostic_hashes": {
            record.diagnostic_id: hash_explanation_diagnostic_record(record)
            for record in sorted(
                intelligence.explanation_diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_operational_hashes": {
            record.state_id: hash_unsupported_explanation_operational_state_visibility(
                record
            )
            for record in sorted(
                intelligence.unsupported_operational_state_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "surface_record_count": len(intelligence.surface_records),
        "support_state_explanation_count": len(
            intelligence.support_state_explanations
        ),
        "evidence_to_explanation_mapping_count": len(
            intelligence.evidence_to_explanation_mappings
        ),
        "limitation_explanation_count": len(intelligence.limitation_explanations),
        "trust_explanation_count": len(intelligence.trust_explanations),
        "continuity_explanation_count": len(intelligence.continuity_explanations),
        "unsupported_state_explanation_count": len(
            intelligence.unsupported_state_explanations
        ),
        "explanation_summary_count": len(intelligence.explanation_summaries),
        "explanation_diagnostic_count": len(intelligence.explanation_diagnostics),
        "unsupported_operational_state_count": len(
            intelligence.unsupported_operational_state_visibility
        ),
        "support_counts": required_visibility["support_counts"],
        "mapping_counts": required_visibility["mapping_counts"],
        "limitation_counts": required_visibility["limitation_counts"],
        "trust_counts": required_visibility["trust_counts"],
        "continuity_counts": required_visibility["continuity_counts"],
        "unsupported_counts": required_visibility["unsupported_counts"],
        "summary_counts": required_visibility["summary_counts"],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "support_state_explanations_stable": support["valid"],
        "evidence_to_explanation_mapping_stable": mapping["valid"],
        "limitation_explanation_preserved": limitation["valid"],
        "trust_explanation_visibility_stable": trust["valid"],
        "continuity_explanation_visibility_stable": continuity["valid"],
        "unsupported_state_explanation_preserved": unsupported["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "evidence_continuity_preserved": lineage_provenance[
            "evidence_continuity_preserved"
        ],
        "fail_visible_explanation_diagnostics_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "publicly_transparent": descriptive_only["publicly_transparent"],
        "explainability_surface_statement": (
            descriptive_only["explainability_surface_statement"]
        ),
        "explainability_visibility_non_authority_statement": (
            descriptive_only["explainability_visibility_non_authority_statement"]
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
        "phase_id": V4_5B_3_EXPLAINABILITY_SURFACE_PHASE_ID,
        "schema_version": V4_5B_3_EXPLAINABILITY_SURFACE_REPORT_SCHEMA_VERSION,
        "generated_at": V4_5B_3_EXPLAINABILITY_SURFACE_GENERATED_AT,
        "purpose": V4_5B_3_EXPLAINABILITY_SURFACE_PURPOSE,
        "foundation_status": validation["foundation_status"],
        "summary": summary,
        "visibility": {
            "explainability_surfaces": explanation_surface_summary(
                intelligence.surface_records
            ),
            "support_state_explanations": support_state_explanation_summary(
                intelligence.support_state_explanations
            ),
            "evidence_to_explanation_mappings": (
                evidence_to_explanation_mapping_summary(
                    intelligence.evidence_to_explanation_mappings
                )
            ),
            "limitation_explanations": limitation_explanation_summary(
                intelligence.limitation_explanations
            ),
            "trust_explanations": trust_explanation_summary(
                intelligence.trust_explanations
            ),
            "continuity_explanations": continuity_explanation_summary(
                intelligence.continuity_explanations
            ),
            "unsupported_state_explanations": unsupported_state_explanation_summary(
                intelligence.unsupported_state_explanations
            ),
            "explanation_summaries": explanation_summary_visibility(
                intelligence.explanation_summaries
            ),
            "explanation_diagnostics": explanation_diagnostic_summary(
                intelligence.explanation_diagnostics
            ),
            "unsupported_operational_states": unsupported_operational_state_summary(
                intelligence.unsupported_operational_state_visibility
            ),
            "descriptive_only": descriptive_only_explainability_surface_summary(
                intelligence
            ),
        },
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "validation": validation,
        "exported_intelligence": exported,
    }
    report["deterministic_report_hash"] = (
        deterministic_v4_5b_3_explainability_surface_hash(report)
    )
    return report


def contaminate_v4_5b_3_explainability_surfaces_for_non_operational_validation(
    intelligence: ExplainabilitySurfaceIntelligence | None = None,
) -> ExplainabilitySurfaceIntelligence:
    if intelligence is None:
        intelligence = build_v4_5b_3_explainability_surfaces()
    return replace(
        intelligence,
        runtime_execution_enabled=True,
        explainability_authorization_enabled=True,
        explainability_approval_enabled=True,
        explainability_ranking_enabled=True,
        explainability_recommendation_enabled=True,
        remediation_enabled=True,
        planner_integration_enabled=True,
    )
