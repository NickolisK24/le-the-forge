"""Audit for deterministic v4.5B.5 public evidence panels.

The audit validates descriptive public evidence panel visibility only. It does
not authorize, approve, execute, dispatch, route, traverse, schedule, sequence,
decide, recommend, rank, score, remediate, repair, mitigate, correct, integrate
planners, consume production paths, or mutate runtime or operational state.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5b_5_evidence_panel_hashing import (
    deterministic_v4_5b_5_evidence_panel_hash,
    hash_evidence_freshness_visibility,
    hash_evidence_group_record,
    hash_evidence_item_record,
    hash_evidence_panel_diagnostic_record,
    hash_evidence_panel_identity,
    hash_evidence_panel_record,
    hash_evidence_panel_summary_record,
    hash_evidence_source_visibility,
    hash_explainability_evidence_panel,
    hash_provenance_lineage_evidence_panel,
    hash_support_status_evidence_panel,
    hash_unsupported_evidence_panel_operational_state_visibility,
    hash_unsupported_missing_evidence_visibility,
    hash_v4_5b_5_evidence_panels,
)
from .v4_5b_5_evidence_panel_models import (
    EVIDENCE_FRESHNESS_VISIBILITY_TYPES,
    EVIDENCE_GROUPING_TYPES,
    EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
    EVIDENCE_PANEL_STATEMENT,
    EVIDENCE_PANEL_SUMMARY_TYPES,
    EVIDENCE_SOURCE_VISIBILITY_TYPES,
    EVIDENCE_VISIBILITY_NON_AUTHORITY_STATEMENT,
    EXPLAINABILITY_EVIDENCE_PANEL_TYPES,
    PROVENANCE_LINEAGE_EVIDENCE_PANEL_TYPES,
    SUPPORT_STATUS_EVIDENCE_PANEL_TYPES,
    UNSUPPORTED_EVIDENCE_PANEL_OPERATIONAL_STATES,
    UNSUPPORTED_MISSING_EVIDENCE_TYPES,
    V4_5B_5_EVIDENCE_PANEL_DISABLED_COUNTER_NAMES,
    V4_5B_5_EVIDENCE_PANEL_GENERATED_AT,
    V4_5B_5_EVIDENCE_PANEL_PHASE_ID,
    V4_5B_5_EVIDENCE_PANEL_PURPOSE,
    V4_5B_5_EVIDENCE_PANEL_REPORT_SCHEMA_VERSION,
    V4_5B_5_EVIDENCE_PANEL_STATUS_BLOCKED,
    V4_5B_5_EVIDENCE_PANEL_STATUS_STABLE,
    EvidencePanelIntelligence,
    default_v4_5b_5_evidence_panels,
)
from .v4_5b_5_evidence_panel_serialization import (
    export_v4_5b_5_evidence_panels,
    serialize_v4_5b_5_evidence_panels,
)
from .v4_5b_5_evidence_panel_visibility import (
    descriptive_only_evidence_panel_summary,
    evidence_freshness_summary,
    evidence_grouping_summary,
    evidence_item_summary,
    evidence_panel_diagnostic_summary,
    evidence_panel_summary,
    evidence_panel_summary_visibility,
    evidence_source_summary,
    explainability_evidence_summary,
    provenance_lineage_evidence_summary,
    support_status_evidence_summary,
    unsupported_missing_evidence_summary,
    unsupported_operational_state_summary,
    validate_required_evidence_panel_visibility,
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
    "enabled_evidence_authorization_count": (
        "evidence_authorization_enabled",
        "evidence_authority_enabled",
        "source_authority_enabled",
        "authorization_enabled",
    ),
    "enabled_evidence_approval_count": (
        "evidence_approval_enabled",
        "approval_enabled",
        "operational_approval_enabled",
    ),
    "enabled_evidence_ranking_count": (
        "evidence_ranking_enabled",
        "ranking_enabled",
        "prioritization_enabled",
    ),
    "enabled_evidence_recommendation_count": (
        "evidence_recommendation_enabled",
        "recommendation_enabled",
    ),
    "enabled_scoring_count": (
        "evidence_scoring_enabled",
        "trust_scoring_enabled",
        "source_scoring_enabled",
        "scoring_enabled",
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


def build_v4_5b_5_evidence_panels() -> EvidencePanelIntelligence:
    return default_v4_5b_5_evidence_panels()


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
        getattr(item, "panel_record_id", None)
        or getattr(item, "group_record_id", None)
        or getattr(item, "item_record_id", None)
        or getattr(item, "source_visibility_id", None)
        or getattr(item, "freshness_visibility_id", None)
        or getattr(item, "support_panel_id", None)
        or getattr(item, "explainability_panel_id", None)
        or getattr(item, "provenance_lineage_panel_id", None)
        or getattr(item, "unsupported_missing_id", None)
        or getattr(item, "summary_record_id", None)
        or getattr(item, "diagnostic_id", None)
        or getattr(item, "state_id", None)
        or getattr(item, "evidence_panel_id", item.__class__.__name__)
    )


def enabled_evidence_panel_capability_flags(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(_record_id(item), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def evidence_panel_capability_counter_values(
    intelligence: EvidencePanelIntelligence,
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


def evidence_panels_equal(
    left: EvidencePanelIntelligence,
    right: EvidencePanelIntelligence,
) -> bool:
    return serialize_v4_5b_5_evidence_panels(
        left
    ) == serialize_v4_5b_5_evidence_panels(right)


def validate_evidence_panel_ordering_stability(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    reordered = replace(
        intelligence,
        evidence_panel_records=tuple(reversed(intelligence.evidence_panel_records)),
        evidence_group_records=tuple(reversed(intelligence.evidence_group_records)),
        evidence_item_records=tuple(reversed(intelligence.evidence_item_records)),
        evidence_source_visibility=tuple(
            reversed(intelligence.evidence_source_visibility)
        ),
        evidence_freshness_visibility=tuple(
            reversed(intelligence.evidence_freshness_visibility)
        ),
        support_status_evidence_panels=tuple(
            reversed(intelligence.support_status_evidence_panels)
        ),
        explainability_evidence_panels=tuple(
            reversed(intelligence.explainability_evidence_panels)
        ),
        provenance_lineage_evidence_panels=tuple(
            reversed(intelligence.provenance_lineage_evidence_panels)
        ),
        unsupported_missing_evidence_visibility=tuple(
            reversed(intelligence.unsupported_missing_evidence_visibility)
        ),
        evidence_panel_summaries=tuple(
            reversed(intelligence.evidence_panel_summaries)
        ),
        evidence_panel_diagnostics=tuple(
            reversed(intelligence.evidence_panel_diagnostics)
        ),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )
    serialization_stable = serialize_v4_5b_5_evidence_panels(
        intelligence
    ) == serialize_v4_5b_5_evidence_panels(reordered)
    hashing_stable = hash_v4_5b_5_evidence_panels(
        intelligence
    ) == hash_v4_5b_5_evidence_panels(reordered)
    return {
        "valid": serialization_stable and hashing_stable,
        "serialization_stable": serialization_stable,
        "hashing_stable": hashing_stable,
    }


def validate_evidence_panel_identity_integrity(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    identity = intelligence.evidence_identity
    required_fields = (
        "evidence_panel_id",
        "evidence_group_id",
        "evidence_item_id",
        "trust_summary_reference_id",
        "support_status_reference_id",
        "explainability_surface_reference_id",
        "provenance_visibility_reference_id",
        "lineage_visibility_reference_id",
        "diagnostics_reference_id",
        "continuity_reference_id",
        "lineage_reference_id",
        "provenance_reference_id",
        "source_provenance_lineage_report_reference",
        "source_provenance_lineage_hash_reference",
    )
    missing_fields = [field for field in required_fields if not getattr(identity, field)]
    source_report_exists = _relative_path_exists(
        identity.source_provenance_lineage_report_reference
    )
    source_hash_matches = _report_hash_matches(
        identity.source_provenance_lineage_report_reference,
        identity.source_provenance_lineage_hash_reference,
    )
    phase_valid = identity.phase_id == V4_5B_5_EVIDENCE_PANEL_PHASE_ID
    generated_at_valid = identity.generated_at == V4_5B_5_EVIDENCE_PANEL_GENERATED_AT
    schema_valid = bool(identity.schema_version)
    return {
        "valid": (
            not missing_fields
            and source_report_exists
            and source_hash_matches
            and phase_valid
            and generated_at_valid
            and schema_valid
        ),
        "missing_fields": missing_fields,
        "source_report_exists": source_report_exists,
        "source_hash_matches": source_hash_matches,
        "phase_valid": phase_valid,
        "generated_at_valid": generated_at_valid,
        "schema_valid": schema_valid,
    }


def _validate_required_types(
    records: Iterable[Any],
    *,
    type_field: str,
    expected_types: tuple[str, ...],
    prohibited_fields: tuple[str, ...],
    require_evidence: bool = True,
    require_fail_visible: bool = False,
    require_source: bool = False,
    require_lineage: bool = False,
    require_provenance: bool = False,
) -> dict[str, Any]:
    records_tuple = tuple(records)
    observed = {str(getattr(record, type_field)) for record in records_tuple}
    missing_types = sorted(set(expected_types) - observed)
    non_descriptive_records = sorted(
        _record_id(record)
        for record in records_tuple
        if not bool(getattr(record, "descriptive_only", True))
    )
    missing_evidence_records = sorted(
        _record_id(record)
        for record in records_tuple
        if require_evidence and not tuple(getattr(record, "evidence_reference_ids", ()))
    )
    non_fail_visible_records = sorted(
        _record_id(record)
        for record in records_tuple
        if require_fail_visible and not bool(getattr(record, "fail_visible", True))
    )
    missing_source_records = sorted(
        _record_id(record)
        for record in records_tuple
        if require_source and not str(getattr(record, "source_reference_id", ""))
    )
    missing_lineage_records = sorted(
        _record_id(record)
        for record in records_tuple
        if require_lineage and not str(getattr(record, "lineage_reference_id", ""))
    )
    missing_provenance_records = sorted(
        _record_id(record)
        for record in records_tuple
        if require_provenance and not str(getattr(record, "provenance_reference_id", ""))
    )
    prohibited_enabled_records = {
        _record_id(record): sorted(
            field
            for field in prohibited_fields
            if bool(getattr(record, field, False))
        )
        for record in records_tuple
        if any(bool(getattr(record, field, False)) for field in prohibited_fields)
    }
    return {
        "valid": (
            not missing_types
            and not non_descriptive_records
            and not missing_evidence_records
            and not non_fail_visible_records
            and not missing_source_records
            and not missing_lineage_records
            and not missing_provenance_records
            and not prohibited_enabled_records
        ),
        "missing_types": missing_types,
        "non_descriptive_records": non_descriptive_records,
        "missing_evidence_records": missing_evidence_records,
        "non_fail_visible_records": non_fail_visible_records,
        "missing_source_records": missing_source_records,
        "missing_lineage_records": missing_lineage_records,
        "missing_provenance_records": missing_provenance_records,
        "prohibited_enabled_records": prohibited_enabled_records,
    }


def validate_evidence_grouping_stability(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.evidence_group_records,
        type_field="grouping_type",
        expected_types=EVIDENCE_GROUPING_TYPES,
        prohibited_fields=(
            "prioritization_enabled",
            "ranking_enabled",
            "recommendation_enabled",
        ),
    )


def validate_evidence_item_stability(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.evidence_item_records,
        type_field="evidence_item_type",
        expected_types=EVIDENCE_GROUPING_TYPES,
        prohibited_fields=(
            "scoring_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
        require_source=True,
    )


def validate_evidence_source_visibility_stability(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.evidence_source_visibility,
        type_field="source_visibility_type",
        expected_types=EVIDENCE_SOURCE_VISIBILITY_TYPES,
        prohibited_fields=(
            "source_authority_enabled",
            "authorization_enabled",
            "approval_enabled",
            "scoring_enabled",
        ),
        require_source=True,
    )


def validate_evidence_freshness_visibility_preservation(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.evidence_freshness_visibility,
        type_field="freshness_type",
        expected_types=EVIDENCE_FRESHNESS_VISIBILITY_TYPES,
        prohibited_fields=(
            "automatic_refresh_enabled",
            "fallback_substitution_enabled",
            "scoring_enabled",
            "authorization_enabled",
        ),
        require_fail_visible=True,
    )


def validate_support_status_evidence_panel_stability(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.support_status_evidence_panels,
        type_field="support_evidence_type",
        expected_types=SUPPORT_STATUS_EVIDENCE_PANEL_TYPES,
        prohibited_fields=(
            "approval_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "operational_enabled",
        ),
    )


def validate_explainability_evidence_panel_stability(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.explainability_evidence_panels,
        type_field="explainability_evidence_type",
        expected_types=EXPLAINABILITY_EVIDENCE_PANEL_TYPES,
        prohibited_fields=(
            "recommendation_enabled",
            "operational_semantics_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
    )


def validate_provenance_lineage_evidence_panel_stability(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.provenance_lineage_evidence_panels,
        type_field="provenance_lineage_evidence_type",
        expected_types=PROVENANCE_LINEAGE_EVIDENCE_PANEL_TYPES,
        prohibited_fields=(
            "trust_scoring_enabled",
            "source_scoring_enabled",
            "authorization_enabled",
            "approval_enabled",
            "ranking_enabled",
        ),
        require_lineage=True,
        require_provenance=True,
    )


def validate_unsupported_missing_evidence_visibility_preservation(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.unsupported_missing_evidence_visibility,
        type_field="unsupported_missing_type",
        expected_types=UNSUPPORTED_MISSING_EVIDENCE_TYPES,
        prohibited_fields=(
            "suppression_enabled",
            "hidden_fallback_enabled",
            "authorization_enabled",
            "approval_enabled",
            "remediation_enabled",
        ),
        require_fail_visible=True,
    )


def validate_evidence_panel_summary_stability(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.evidence_panel_summaries,
        type_field="summary_type",
        expected_types=EVIDENCE_PANEL_SUMMARY_TYPES,
        prohibited_fields=(
            "authorization_enabled",
            "approval_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "scoring_enabled",
            "execution_enablement_enabled",
            "production_enablement_enabled",
        ),
    )


def validate_lineage_and_provenance_preservation(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    identity = intelligence.evidence_identity
    missing_identity_lineage = not identity.lineage_reference_id
    missing_identity_provenance = not identity.provenance_reference_id
    missing_record_evidence = sorted(
        _record_id(record)
        for record in _iter_dataclass_objects(intelligence)
        if hasattr(record, "evidence_reference_ids")
        and not tuple(getattr(record, "evidence_reference_ids", ()))
    )
    missing_item_sources = sorted(
        record.item_record_id
        for record in intelligence.evidence_item_records
        if not record.source_reference_id
    )
    missing_source_references = sorted(
        record.source_visibility_id
        for record in intelligence.evidence_source_visibility
        if not record.source_reference_id
    )
    missing_panel_lineage = sorted(
        record.provenance_lineage_panel_id
        for record in intelligence.provenance_lineage_evidence_panels
        if not record.lineage_reference_id
    )
    missing_panel_provenance = sorted(
        record.provenance_lineage_panel_id
        for record in intelligence.provenance_lineage_evidence_panels
        if not record.provenance_reference_id
    )
    return {
        "valid": not any(
            (
                missing_identity_lineage,
                missing_identity_provenance,
                missing_record_evidence,
                missing_item_sources,
                missing_source_references,
                missing_panel_lineage,
                missing_panel_provenance,
            )
        ),
        "lineage_continuity_preserved": not missing_identity_lineage
        and not missing_panel_lineage,
        "provenance_continuity_preserved": not missing_identity_provenance
        and not missing_panel_provenance,
        "evidence_continuity_preserved": not missing_record_evidence,
        "source_visibility_preserved": not missing_item_sources
        and not missing_source_references,
        "missing_identity_lineage": missing_identity_lineage,
        "missing_identity_provenance": missing_identity_provenance,
        "missing_record_evidence": missing_record_evidence,
        "missing_item_sources": missing_item_sources,
        "missing_source_references": missing_source_references,
        "missing_panel_lineage": missing_panel_lineage,
        "missing_panel_provenance": missing_panel_provenance,
    }


def validate_evidence_panel_serialization_and_hashing(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    serialization_one = serialize_v4_5b_5_evidence_panels(intelligence)
    serialization_two = serialize_v4_5b_5_evidence_panels(
        default_v4_5b_5_evidence_panels()
    )
    hash_one = hash_v4_5b_5_evidence_panels(intelligence)
    hash_two = hash_v4_5b_5_evidence_panels(default_v4_5b_5_evidence_panels())
    ordering = validate_evidence_panel_ordering_stability(intelligence)
    return {
        "valid": (
            serialization_one == serialization_two
            and hash_one == hash_two
            and ordering["valid"]
        ),
        "serialization_stable": serialization_one == serialization_two,
        "hashing_stable": hash_one == hash_two,
        "ordering_stable": ordering["valid"],
        "serialized_length": len(serialization_one),
        "deterministic_hash": hash_one,
    }


def validate_fail_visible_evidence_panel_diagnostics(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    diagnostic = _validate_required_types(
        intelligence.evidence_panel_diagnostics,
        type_field="diagnostic_type",
        expected_types=EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
        prohibited_fields=(
            "silent_fallback_enabled",
            "hidden_fallback_enabled",
            "authorization_enabled",
            "approval_enabled",
            "remediation_enabled",
            "repair_enabled",
            "mitigation_enabled",
            "auto_correction_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "scoring_enabled",
            "orchestration_response_enabled",
        ),
        require_fail_visible=True,
    )
    unsupported = _validate_required_types(
        intelligence.unsupported_operational_state_visibility,
        type_field="unsupported_state",
        expected_types=UNSUPPORTED_EVIDENCE_PANEL_OPERATIONAL_STATES,
        prohibited_fields=(
            "authorization_enabled",
            "approval_enabled",
            "operational_enabled",
            "remediation_enabled",
            "repair_enabled",
            "mitigation_enabled",
            "automated_correction_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "scoring_enabled",
            "suppression_enabled",
        ),
        require_fail_visible=True,
    )
    missing_explicit_reasons = sorted(
        record.state_id
        for record in intelligence.unsupported_operational_state_visibility
        if not record.explicit_reason
    )
    return {
        "valid": (
            diagnostic["valid"]
            and unsupported["valid"]
            and not missing_explicit_reasons
        ),
        "diagnostic_visibility": diagnostic,
        "unsupported_operational_visibility": unsupported,
        "missing_explicit_reasons": missing_explicit_reasons,
    }


def validate_descriptive_only_evidence_panel_guarantees(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    counters = evidence_panel_capability_counter_values(intelligence)
    enabled_flags = enabled_evidence_panel_capability_flags(intelligence)
    required_boundary_booleans = {
        "descriptive_only": intelligence.descriptive_only,
        "publicly_transparent": intelligence.publicly_transparent,
        "non_operational": intelligence.non_operational,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_executing": intelligence.non_executing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_ranking": intelligence.non_ranking,
        "non_recommending": intelligence.non_recommending,
        "non_scoring": intelligence.non_scoring,
    }
    all_required_true = all(required_boundary_booleans.values())
    all_counters_zero = all(
        counters.get(counter_name, 1) == 0
        for counter_name in V4_5B_5_EVIDENCE_PANEL_DISABLED_COUNTER_NAMES
    )
    statements_valid = (
        intelligence.evidence_panel_statement == EVIDENCE_PANEL_STATEMENT
        and intelligence.evidence_visibility_non_authority_statement
        == EVIDENCE_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    return {
        "valid": all_required_true
        and all_counters_zero
        and not enabled_flags
        and statements_valid,
        "required_boundary_booleans": required_boundary_booleans,
        "counters": counters,
        "enabled_flags": enabled_flags,
        "statements_valid": statements_valid,
        "publicly_transparent": intelligence.publicly_transparent,
        "evidence_panel_statement": intelligence.evidence_panel_statement,
        "evidence_visibility_non_authority_statement": (
            intelligence.evidence_visibility_non_authority_statement
        ),
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "explicit_limitation_count": len(intelligence.explicit_limitations),
    }


def validate_v4_5b_5_evidence_panels(
    intelligence: EvidencePanelIntelligence | None = None,
) -> dict[str, Any]:
    if intelligence is None:
        intelligence = build_v4_5b_5_evidence_panels()
    validations = {
        "identity_integrity": validate_evidence_panel_identity_integrity(intelligence),
        "required_visibility": validate_required_evidence_panel_visibility(intelligence),
        "evidence_grouping": validate_evidence_grouping_stability(intelligence),
        "evidence_items": validate_evidence_item_stability(intelligence),
        "evidence_source_visibility": (
            validate_evidence_source_visibility_stability(intelligence)
        ),
        "evidence_freshness_visibility": (
            validate_evidence_freshness_visibility_preservation(intelligence)
        ),
        "support_status_evidence_panels": (
            validate_support_status_evidence_panel_stability(intelligence)
        ),
        "explainability_evidence_panels": (
            validate_explainability_evidence_panel_stability(intelligence)
        ),
        "provenance_lineage_evidence_panels": (
            validate_provenance_lineage_evidence_panel_stability(intelligence)
        ),
        "unsupported_missing_evidence": (
            validate_unsupported_missing_evidence_visibility_preservation(
                intelligence
            )
        ),
        "evidence_panel_summaries": validate_evidence_panel_summary_stability(
            intelligence
        ),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_and_hashing": validate_evidence_panel_serialization_and_hashing(
            intelligence
        ),
        "fail_visible_evidence_panel": validate_fail_visible_evidence_panel_diagnostics(
            intelligence
        ),
        "descriptive_only_guarantees": (
            validate_descriptive_only_evidence_panel_guarantees(intelligence)
        ),
    }
    errors = sorted(name for name, result in validations.items() if not result["valid"])
    return {
        "valid": not errors,
        "foundation_status": (
            V4_5B_5_EVIDENCE_PANEL_STATUS_STABLE
            if not errors
            else V4_5B_5_EVIDENCE_PANEL_STATUS_BLOCKED
        ),
        "validation_error_count": len(errors),
        "validation_errors": errors,
        "validations": validations,
    }


def build_v4_5b_5_evidence_panels_report() -> dict[str, Any]:
    intelligence = build_v4_5b_5_evidence_panels()
    validation = validate_v4_5b_5_evidence_panels(intelligence)
    exported = export_v4_5b_5_evidence_panels(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_and_hashing"]
    grouping = validation["validations"]["evidence_grouping"]
    source = validation["validations"]["evidence_source_visibility"]
    freshness = validation["validations"]["evidence_freshness_visibility"]
    support = validation["validations"]["support_status_evidence_panels"]
    explainability = validation["validations"]["explainability_evidence_panels"]
    provenance_lineage = validation["validations"][
        "provenance_lineage_evidence_panels"
    ]
    unsupported_missing = validation["validations"]["unsupported_missing_evidence"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_evidence_panel"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "evidence_panel_identity_hash": hash_evidence_panel_identity(
            intelligence.evidence_identity
        ),
        "evidence_panel_visibility_hash": hash_v4_5b_5_evidence_panels(
            intelligence
        ),
        "evidence_panel_record_hashes": {
            record.panel_record_id: hash_evidence_panel_record(record)
            for record in sorted(
                intelligence.evidence_panel_records,
                key=lambda item: (item.deterministic_order, item.panel_record_id),
            )
        },
        "evidence_group_hashes": {
            record.group_record_id: hash_evidence_group_record(record)
            for record in sorted(
                intelligence.evidence_group_records,
                key=lambda item: (item.deterministic_order, item.group_record_id),
            )
        },
        "evidence_item_hashes": {
            record.item_record_id: hash_evidence_item_record(record)
            for record in sorted(
                intelligence.evidence_item_records,
                key=lambda item: (item.deterministic_order, item.item_record_id),
            )
        },
        "evidence_source_hashes": {
            record.source_visibility_id: hash_evidence_source_visibility(record)
            for record in sorted(
                intelligence.evidence_source_visibility,
                key=lambda item: (item.deterministic_order, item.source_visibility_id),
            )
        },
        "evidence_freshness_hashes": {
            record.freshness_visibility_id: hash_evidence_freshness_visibility(record)
            for record in sorted(
                intelligence.evidence_freshness_visibility,
                key=lambda item: (
                    item.deterministic_order,
                    item.freshness_visibility_id,
                ),
            )
        },
        "support_status_evidence_panel_hashes": {
            record.support_panel_id: hash_support_status_evidence_panel(record)
            for record in sorted(
                intelligence.support_status_evidence_panels,
                key=lambda item: (item.deterministic_order, item.support_panel_id),
            )
        },
        "explainability_evidence_panel_hashes": {
            record.explainability_panel_id: hash_explainability_evidence_panel(record)
            for record in sorted(
                intelligence.explainability_evidence_panels,
                key=lambda item: (
                    item.deterministic_order,
                    item.explainability_panel_id,
                ),
            )
        },
        "provenance_lineage_evidence_panel_hashes": {
            record.provenance_lineage_panel_id: (
                hash_provenance_lineage_evidence_panel(record)
            )
            for record in sorted(
                intelligence.provenance_lineage_evidence_panels,
                key=lambda item: (
                    item.deterministic_order,
                    item.provenance_lineage_panel_id,
                ),
            )
        },
        "unsupported_missing_evidence_hashes": {
            record.unsupported_missing_id: (
                hash_unsupported_missing_evidence_visibility(record)
            )
            for record in sorted(
                intelligence.unsupported_missing_evidence_visibility,
                key=lambda item: (item.deterministic_order, item.unsupported_missing_id),
            )
        },
        "evidence_panel_summary_hashes": {
            record.summary_record_id: hash_evidence_panel_summary_record(record)
            for record in sorted(
                intelligence.evidence_panel_summaries,
                key=lambda item: (item.deterministic_order, item.summary_record_id),
            )
        },
        "evidence_panel_diagnostic_hashes": {
            record.diagnostic_id: hash_evidence_panel_diagnostic_record(record)
            for record in sorted(
                intelligence.evidence_panel_diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_operational_hashes": {
            record.state_id: (
                hash_unsupported_evidence_panel_operational_state_visibility(record)
            )
            for record in sorted(
                intelligence.unsupported_operational_state_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "evidence_panel_record_count": len(intelligence.evidence_panel_records),
        "evidence_group_count": len(intelligence.evidence_group_records),
        "evidence_item_count": len(intelligence.evidence_item_records),
        "evidence_source_visibility_count": len(
            intelligence.evidence_source_visibility
        ),
        "evidence_freshness_visibility_count": len(
            intelligence.evidence_freshness_visibility
        ),
        "support_status_evidence_panel_count": len(
            intelligence.support_status_evidence_panels
        ),
        "explainability_evidence_panel_count": len(
            intelligence.explainability_evidence_panels
        ),
        "provenance_lineage_evidence_panel_count": len(
            intelligence.provenance_lineage_evidence_panels
        ),
        "unsupported_missing_evidence_count": len(
            intelligence.unsupported_missing_evidence_visibility
        ),
        "evidence_panel_summary_count": len(intelligence.evidence_panel_summaries),
        "evidence_panel_diagnostic_count": len(
            intelligence.evidence_panel_diagnostics
        ),
        "unsupported_operational_state_count": len(
            intelligence.unsupported_operational_state_visibility
        ),
        "grouping_counts": required_visibility["grouping_counts"],
        "source_counts": required_visibility["source_counts"],
        "freshness_counts": required_visibility["freshness_counts"],
        "support_counts": required_visibility["support_counts"],
        "explainability_counts": required_visibility["explainability_counts"],
        "provenance_lineage_counts": required_visibility[
            "provenance_lineage_counts"
        ],
        "unsupported_counts": required_visibility["unsupported_counts"],
        "summary_counts": required_visibility["summary_counts"],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_evidence_panel_serialization_verified": (
            serialization_hashing["serialization_stable"]
        ),
        "deterministic_evidence_panel_hashing_verified": (
            serialization_hashing["hashing_stable"]
        ),
        "evidence_grouping_stable": grouping["valid"],
        "evidence_source_visibility_stable": source["valid"],
        "evidence_freshness_visibility_preserved": freshness["valid"],
        "support_status_evidence_panel_stable": support["valid"],
        "explainability_evidence_panel_stable": explainability["valid"],
        "provenance_lineage_evidence_panel_stable": provenance_lineage["valid"],
        "unsupported_missing_evidence_visibility_preserved": unsupported_missing[
            "valid"
        ],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "evidence_continuity_preserved": lineage_provenance[
            "evidence_continuity_preserved"
        ],
        "source_visibility_preserved": lineage_provenance[
            "source_visibility_preserved"
        ],
        "fail_visible_evidence_panel_diagnostics_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "publicly_transparent": descriptive_only["publicly_transparent"],
        "evidence_panel_statement": descriptive_only["evidence_panel_statement"],
        "evidence_visibility_non_authority_statement": (
            descriptive_only["evidence_visibility_non_authority_statement"]
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
            "NON-scoring",
        ],
    }
    summary.update(counters)
    report = {
        "phase_id": V4_5B_5_EVIDENCE_PANEL_PHASE_ID,
        "schema_version": V4_5B_5_EVIDENCE_PANEL_REPORT_SCHEMA_VERSION,
        "generated_at": V4_5B_5_EVIDENCE_PANEL_GENERATED_AT,
        "purpose": V4_5B_5_EVIDENCE_PANEL_PURPOSE,
        "foundation_status": validation["foundation_status"],
        "summary": summary,
        "visibility": {
            "evidence_panels": evidence_panel_summary(
                intelligence.evidence_panel_records
            ),
            "evidence_grouping": evidence_grouping_summary(
                intelligence.evidence_group_records
            ),
            "evidence_items": evidence_item_summary(
                intelligence.evidence_item_records
            ),
            "evidence_sources": evidence_source_summary(
                intelligence.evidence_source_visibility
            ),
            "evidence_freshness": evidence_freshness_summary(
                intelligence.evidence_freshness_visibility
            ),
            "support_status_evidence": support_status_evidence_summary(
                intelligence.support_status_evidence_panels
            ),
            "explainability_evidence": explainability_evidence_summary(
                intelligence.explainability_evidence_panels
            ),
            "provenance_lineage_evidence": provenance_lineage_evidence_summary(
                intelligence.provenance_lineage_evidence_panels
            ),
            "unsupported_missing_evidence": unsupported_missing_evidence_summary(
                intelligence.unsupported_missing_evidence_visibility
            ),
            "evidence_panel_summaries": evidence_panel_summary_visibility(
                intelligence.evidence_panel_summaries
            ),
            "evidence_panel_diagnostics": evidence_panel_diagnostic_summary(
                intelligence.evidence_panel_diagnostics
            ),
            "unsupported_operational_states": unsupported_operational_state_summary(
                intelligence.unsupported_operational_state_visibility
            ),
            "descriptive_only": descriptive_only_evidence_panel_summary(
                intelligence
            ),
        },
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "validation": validation,
        "exported_intelligence": exported,
    }
    report["deterministic_report_hash"] = deterministic_v4_5b_5_evidence_panel_hash(
        report
    )
    return report


def contaminate_v4_5b_5_evidence_panels_for_non_operational_validation(
    intelligence: EvidencePanelIntelligence | None = None,
) -> EvidencePanelIntelligence:
    if intelligence is None:
        intelligence = build_v4_5b_5_evidence_panels()
    return replace(
        intelligence,
        runtime_execution_enabled=True,
        evidence_authorization_enabled=True,
        evidence_approval_enabled=True,
        evidence_ranking_enabled=True,
        evidence_recommendation_enabled=True,
        evidence_scoring_enabled=True,
        trust_scoring_enabled=True,
        remediation_enabled=True,
        planner_integration_enabled=True,
    )
