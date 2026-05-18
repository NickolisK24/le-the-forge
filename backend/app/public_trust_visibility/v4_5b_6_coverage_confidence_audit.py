"""Audit for deterministic v4.5B.6 coverage and confidence visibility."""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5b_6_coverage_confidence_hashing import (
    deterministic_v4_5b_6_coverage_confidence_hash,
    hash_confidence_visibility_record,
    hash_coverage_confidence_identity,
    hash_coverage_confidence_summary_record,
    hash_coverage_diagnostic_record,
    hash_coverage_visibility_record,
    hash_evidence_coverage_record,
    hash_explainability_coverage_record,
    hash_incomplete_unknown_coverage_record,
    hash_provenance_lineage_coverage_record,
    hash_support_coverage_record,
    hash_unsupported_coverage_confidence_operational_state_visibility,
    hash_v4_5b_6_coverage_confidence,
)
from .v4_5b_6_coverage_confidence_models import (
    CONFIDENCE_VISIBILITY_TYPES,
    COVERAGE_CONFIDENCE_NON_AUTHORITY_STATEMENT,
    COVERAGE_CONFIDENCE_STATEMENT,
    COVERAGE_CONFIDENCE_SUMMARY_TYPES,
    COVERAGE_DIAGNOSTIC_TYPES,
    COVERAGE_VISIBILITY_TYPES,
    EVIDENCE_COVERAGE_TYPES,
    EXPLAINABILITY_COVERAGE_TYPES,
    INCOMPLETE_UNKNOWN_COVERAGE_TYPES,
    PROVENANCE_LINEAGE_COVERAGE_TYPES,
    SUPPORT_COVERAGE_TYPES,
    UNSUPPORTED_COVERAGE_CONFIDENCE_OPERATIONAL_STATES,
    V4_5B_6_COVERAGE_CONFIDENCE_DISABLED_COUNTER_NAMES,
    V4_5B_6_COVERAGE_CONFIDENCE_GENERATED_AT,
    V4_5B_6_COVERAGE_CONFIDENCE_PHASE_ID,
    V4_5B_6_COVERAGE_CONFIDENCE_PURPOSE,
    V4_5B_6_COVERAGE_CONFIDENCE_REPORT_SCHEMA_VERSION,
    V4_5B_6_COVERAGE_CONFIDENCE_STATUS_BLOCKED,
    V4_5B_6_COVERAGE_CONFIDENCE_STATUS_STABLE,
    CoverageConfidenceIntelligence,
    default_v4_5b_6_coverage_confidence,
)
from .v4_5b_6_coverage_confidence_serialization import (
    export_v4_5b_6_coverage_confidence,
    serialize_v4_5b_6_coverage_confidence,
)
from .v4_5b_6_coverage_confidence_visibility import (
    confidence_visibility_summary,
    coverage_confidence_summary_visibility,
    coverage_diagnostic_summary,
    coverage_visibility_summary,
    descriptive_only_coverage_confidence_summary,
    evidence_coverage_summary,
    explainability_coverage_summary,
    incomplete_unknown_coverage_summary,
    provenance_lineage_coverage_summary,
    support_coverage_summary,
    unsupported_operational_state_summary,
    validate_required_coverage_confidence_visibility,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "planner_execution_enabled",
        "execution_enablement_enabled",
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
    "enabled_confidence_authorization_count": (
        "confidence_authorization_enabled",
        "authorization_enabled",
    ),
    "enabled_confidence_approval_count": (
        "confidence_approval_enabled",
        "approval_enabled",
    ),
    "enabled_coverage_ranking_count": (
        "coverage_ranking_enabled",
        "ranking_enabled",
        "evidence_ranking_enabled",
    ),
    "enabled_confidence_recommendation_count": (
        "confidence_recommendation_enabled",
        "recommendation_enabled",
    ),
    "enabled_scoring_count": (
        "trust_scoring_enabled",
        "evidence_scoring_enabled",
        "scoring_enabled",
        "source_authority_enabled",
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
        "operational_readiness_enabled",
    ),
}

PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_5b_6_coverage_confidence() -> CoverageConfidenceIntelligence:
    return default_v4_5b_6_coverage_confidence()


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
        getattr(item, "coverage_record_id", None)
        or getattr(item, "support_coverage_id", None)
        or getattr(item, "evidence_coverage_id", None)
        or getattr(item, "explainability_coverage_id", None)
        or getattr(item, "provenance_lineage_coverage_id", None)
        or getattr(item, "confidence_record_id", None)
        or getattr(item, "incomplete_unknown_id", None)
        or getattr(item, "summary_record_id", None)
        or getattr(item, "diagnostic_id", None)
        or getattr(item, "state_id", None)
        or getattr(item, "coverage_visibility_id", item.__class__.__name__)
    )


def enabled_coverage_confidence_capability_flags(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(_record_id(item), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def coverage_confidence_capability_counter_values(
    intelligence: CoverageConfidenceIntelligence,
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


def coverage_confidence_equal(
    left: CoverageConfidenceIntelligence,
    right: CoverageConfidenceIntelligence,
) -> bool:
    return serialize_v4_5b_6_coverage_confidence(
        left
    ) == serialize_v4_5b_6_coverage_confidence(right)


def validate_coverage_confidence_ordering_stability(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    reordered = replace(
        intelligence,
        coverage_visibility_records=tuple(
            reversed(intelligence.coverage_visibility_records)
        ),
        support_coverage_records=tuple(reversed(intelligence.support_coverage_records)),
        evidence_coverage_records=tuple(reversed(intelligence.evidence_coverage_records)),
        explainability_coverage_records=tuple(
            reversed(intelligence.explainability_coverage_records)
        ),
        provenance_lineage_coverage_records=tuple(
            reversed(intelligence.provenance_lineage_coverage_records)
        ),
        confidence_visibility_records=tuple(
            reversed(intelligence.confidence_visibility_records)
        ),
        incomplete_unknown_coverage_records=tuple(
            reversed(intelligence.incomplete_unknown_coverage_records)
        ),
        summary_records=tuple(reversed(intelligence.summary_records)),
        diagnostic_records=tuple(reversed(intelligence.diagnostic_records)),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )
    serialization_stable = serialize_v4_5b_6_coverage_confidence(
        intelligence
    ) == serialize_v4_5b_6_coverage_confidence(reordered)
    hashing_stable = hash_v4_5b_6_coverage_confidence(
        intelligence
    ) == hash_v4_5b_6_coverage_confidence(reordered)
    return {
        "valid": serialization_stable and hashing_stable,
        "serialization_stable": serialization_stable,
        "hashing_stable": hashing_stable,
    }


def validate_coverage_confidence_identity_integrity(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    identity = intelligence.identity
    required_fields = (
        "coverage_visibility_id",
        "confidence_visibility_id",
        "coverage_summary_id",
        "confidence_summary_id",
        "support_status_reference_id",
        "explainability_surface_reference_id",
        "provenance_visibility_reference_id",
        "lineage_visibility_reference_id",
        "evidence_panel_reference_id",
        "diagnostics_reference_id",
        "continuity_reference_id",
        "lineage_reference_id",
        "provenance_reference_id",
        "source_evidence_panel_report_reference",
        "source_evidence_panel_hash_reference",
    )
    missing_fields = [field for field in required_fields if not getattr(identity, field)]
    source_report_exists = _relative_path_exists(
        identity.source_evidence_panel_report_reference
    )
    source_hash_matches = _report_hash_matches(
        identity.source_evidence_panel_report_reference,
        identity.source_evidence_panel_hash_reference,
    )
    phase_valid = identity.phase_id == V4_5B_6_COVERAGE_CONFIDENCE_PHASE_ID
    generated_at_valid = identity.generated_at == V4_5B_6_COVERAGE_CONFIDENCE_GENERATED_AT
    return {
        "valid": (
            not missing_fields
            and source_report_exists
            and source_hash_matches
            and phase_valid
            and generated_at_valid
            and bool(identity.schema_version)
        ),
        "missing_fields": missing_fields,
        "source_report_exists": source_report_exists,
        "source_hash_matches": source_hash_matches,
        "phase_valid": phase_valid,
        "generated_at_valid": generated_at_valid,
    }


def _validate_required_types(
    records: Iterable[Any],
    *,
    type_field: str,
    expected_types: tuple[str, ...],
    prohibited_fields: tuple[str, ...],
    required_reference_fields: tuple[str, ...] = (),
    require_fail_visible: bool = False,
) -> dict[str, Any]:
    records_tuple = tuple(records)
    observed = {str(getattr(record, type_field)) for record in records_tuple}
    missing_types = sorted(set(expected_types) - observed)
    non_descriptive_records = sorted(
        _record_id(record)
        for record in records_tuple
        if not bool(getattr(record, "descriptive_only", True))
    )
    non_fail_visible_records = sorted(
        _record_id(record)
        for record in records_tuple
        if require_fail_visible and not bool(getattr(record, "fail_visible", True))
    )
    missing_reference_records = sorted(
        _record_id(record)
        for record in records_tuple
        if any(not str(getattr(record, field, "")) for field in required_reference_fields)
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
            and not non_fail_visible_records
            and not missing_reference_records
            and not prohibited_enabled_records
        ),
        "missing_types": missing_types,
        "non_descriptive_records": non_descriptive_records,
        "non_fail_visible_records": non_fail_visible_records,
        "missing_reference_records": missing_reference_records,
        "prohibited_enabled_records": prohibited_enabled_records,
    }


def validate_coverage_visibility_stability(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.coverage_visibility_records,
        type_field="coverage_type",
        expected_types=COVERAGE_VISIBILITY_TYPES,
        prohibited_fields=(
            "recommendation_enabled",
            "ranking_enabled",
            "scoring_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
        required_reference_fields=("coverage_reference_id", "evidence_panel_reference_id"),
    )


def validate_support_coverage_stability(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.support_coverage_records,
        type_field="support_coverage_type",
        expected_types=SUPPORT_COVERAGE_TYPES,
        prohibited_fields=(
            "recommendation_enabled",
            "approval_enabled",
            "operational_enabled",
        ),
        required_reference_fields=(
            "support_status_reference_id",
            "evidence_panel_reference_id",
        ),
    )


def validate_evidence_coverage_stability(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.evidence_coverage_records,
        type_field="evidence_coverage_type",
        expected_types=EVIDENCE_COVERAGE_TYPES,
        prohibited_fields=(
            "trust_scoring_enabled",
            "evidence_ranking_enabled",
            "scoring_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
        required_reference_fields=("evidence_panel_reference_id",),
    )


def validate_explainability_coverage_stability(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.explainability_coverage_records,
        type_field="explainability_coverage_type",
        expected_types=EXPLAINABILITY_COVERAGE_TYPES,
        prohibited_fields=(
            "recommendation_enabled",
            "operational_semantics_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
        required_reference_fields=(
            "explainability_surface_reference_id",
            "continuity_reference_id",
            "diagnostics_reference_id",
        ),
    )


def validate_provenance_lineage_coverage_stability(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.provenance_lineage_coverage_records,
        type_field="provenance_lineage_coverage_type",
        expected_types=PROVENANCE_LINEAGE_COVERAGE_TYPES,
        prohibited_fields=(
            "source_authority_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "scoring_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
        required_reference_fields=(
            "provenance_visibility_reference_id",
            "lineage_visibility_reference_id",
            "evidence_panel_reference_id",
        ),
    )


def validate_confidence_visibility_stability(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.confidence_visibility_records,
        type_field="confidence_type",
        expected_types=CONFIDENCE_VISIBILITY_TYPES,
        prohibited_fields=(
            "trust_scoring_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "authorization_enabled",
            "approval_enabled",
            "execution_enablement_enabled",
        ),
        required_reference_fields=("coverage_reference_id", "evidence_panel_reference_id"),
    )


def validate_incomplete_unknown_coverage_visibility_preservation(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.incomplete_unknown_coverage_records,
        type_field="incomplete_unknown_type",
        expected_types=INCOMPLETE_UNKNOWN_COVERAGE_TYPES,
        prohibited_fields=(
            "suppression_enabled",
            "hidden_fallback_enabled",
            "authorization_enabled",
            "approval_enabled",
            "remediation_enabled",
        ),
        required_reference_fields=("coverage_reference_id", "evidence_panel_reference_id"),
        require_fail_visible=True,
    )


def validate_summary_stability(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.summary_records,
        type_field="summary_type",
        expected_types=COVERAGE_CONFIDENCE_SUMMARY_TYPES,
        prohibited_fields=(
            "authorization_enabled",
            "approval_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "scoring_enabled",
            "execution_enablement_enabled",
            "production_enablement_enabled",
        ),
        required_reference_fields=("coverage_reference_id", "confidence_reference_id"),
    )


def validate_lineage_and_provenance_preservation(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    identity = intelligence.identity
    missing_identity_lineage = not identity.lineage_reference_id
    missing_identity_provenance = not identity.provenance_reference_id
    missing_provenance = sorted(
        record.provenance_lineage_coverage_id
        for record in intelligence.provenance_lineage_coverage_records
        if not record.provenance_visibility_reference_id
    )
    missing_lineage = sorted(
        record.provenance_lineage_coverage_id
        for record in intelligence.provenance_lineage_coverage_records
        if not record.lineage_visibility_reference_id
    )
    missing_evidence_panels = sorted(
        _record_id(record)
        for record in _iter_dataclass_objects(intelligence)
        if hasattr(record, "evidence_panel_reference_id")
        and not str(getattr(record, "evidence_panel_reference_id", ""))
    )
    return {
        "valid": not any(
            (
                missing_identity_lineage,
                missing_identity_provenance,
                missing_provenance,
                missing_lineage,
                missing_evidence_panels,
            )
        ),
        "lineage_continuity_preserved": not missing_identity_lineage
        and not missing_lineage,
        "provenance_continuity_preserved": not missing_identity_provenance
        and not missing_provenance,
        "evidence_panel_continuity_preserved": not missing_evidence_panels,
        "missing_identity_lineage": missing_identity_lineage,
        "missing_identity_provenance": missing_identity_provenance,
        "missing_provenance": missing_provenance,
        "missing_lineage": missing_lineage,
        "missing_evidence_panels": missing_evidence_panels,
    }


def validate_coverage_confidence_serialization_and_hashing(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    serialization_one = serialize_v4_5b_6_coverage_confidence(intelligence)
    serialization_two = serialize_v4_5b_6_coverage_confidence(
        default_v4_5b_6_coverage_confidence()
    )
    hash_one = hash_v4_5b_6_coverage_confidence(intelligence)
    hash_two = hash_v4_5b_6_coverage_confidence(
        default_v4_5b_6_coverage_confidence()
    )
    ordering = validate_coverage_confidence_ordering_stability(intelligence)
    return {
        "valid": (
            serialization_one == serialization_two
            and hash_one == hash_two
            and ordering["valid"]
        ),
        "coverage_serialization_stable": serialization_one == serialization_two,
        "confidence_serialization_stable": serialization_one == serialization_two,
        "coverage_hashing_stable": hash_one == hash_two,
        "confidence_hashing_stable": hash_one == hash_two,
        "ordering_stable": ordering["valid"],
        "serialized_length": len(serialization_one),
        "deterministic_hash": hash_one,
    }


def validate_fail_visible_coverage_diagnostics(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    diagnostics = _validate_required_types(
        intelligence.diagnostic_records,
        type_field="diagnostic_type",
        expected_types=COVERAGE_DIAGNOSTIC_TYPES,
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
        required_reference_fields=("coverage_reference_id", "confidence_reference_id"),
        require_fail_visible=True,
    )
    unsupported = _validate_required_types(
        intelligence.unsupported_operational_state_visibility,
        type_field="unsupported_state",
        expected_types=UNSUPPORTED_COVERAGE_CONFIDENCE_OPERATIONAL_STATES,
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
        required_reference_fields=("coverage_reference_id", "confidence_reference_id"),
        require_fail_visible=True,
    )
    missing_explicit_reasons = sorted(
        record.state_id
        for record in intelligence.unsupported_operational_state_visibility
        if not record.explicit_reason
    )
    return {
        "valid": diagnostics["valid"] and unsupported["valid"] and not missing_explicit_reasons,
        "diagnostic_visibility": diagnostics,
        "unsupported_operational_visibility": unsupported,
        "missing_explicit_reasons": missing_explicit_reasons,
    }


def validate_descriptive_only_coverage_confidence_guarantees(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    counters = coverage_confidence_capability_counter_values(intelligence)
    enabled_flags = enabled_coverage_confidence_capability_flags(intelligence)
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
        for counter_name in V4_5B_6_COVERAGE_CONFIDENCE_DISABLED_COUNTER_NAMES
    )
    statements_valid = (
        intelligence.coverage_confidence_statement == COVERAGE_CONFIDENCE_STATEMENT
        and intelligence.coverage_confidence_non_authority_statement
        == COVERAGE_CONFIDENCE_NON_AUTHORITY_STATEMENT
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
        "coverage_confidence_statement": intelligence.coverage_confidence_statement,
        "coverage_confidence_non_authority_statement": (
            intelligence.coverage_confidence_non_authority_statement
        ),
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "explicit_limitation_count": len(intelligence.explicit_limitations),
    }


def validate_v4_5b_6_coverage_confidence(
    intelligence: CoverageConfidenceIntelligence | None = None,
) -> dict[str, Any]:
    if intelligence is None:
        intelligence = build_v4_5b_6_coverage_confidence()
    validations = {
        "identity_integrity": validate_coverage_confidence_identity_integrity(
            intelligence
        ),
        "required_visibility": validate_required_coverage_confidence_visibility(
            intelligence
        ),
        "coverage_visibility": validate_coverage_visibility_stability(intelligence),
        "support_coverage": validate_support_coverage_stability(intelligence),
        "evidence_coverage": validate_evidence_coverage_stability(intelligence),
        "explainability_coverage": validate_explainability_coverage_stability(
            intelligence
        ),
        "provenance_lineage_coverage": (
            validate_provenance_lineage_coverage_stability(intelligence)
        ),
        "confidence_visibility": validate_confidence_visibility_stability(
            intelligence
        ),
        "incomplete_unknown_coverage": (
            validate_incomplete_unknown_coverage_visibility_preservation(
                intelligence
            )
        ),
        "summary_stability": validate_summary_stability(intelligence),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_and_hashing": (
            validate_coverage_confidence_serialization_and_hashing(intelligence)
        ),
        "fail_visible_coverage_diagnostics": (
            validate_fail_visible_coverage_diagnostics(intelligence)
        ),
        "descriptive_only_guarantees": (
            validate_descriptive_only_coverage_confidence_guarantees(intelligence)
        ),
    }
    errors = sorted(name for name, result in validations.items() if not result["valid"])
    return {
        "valid": not errors,
        "foundation_status": (
            V4_5B_6_COVERAGE_CONFIDENCE_STATUS_STABLE
            if not errors
            else V4_5B_6_COVERAGE_CONFIDENCE_STATUS_BLOCKED
        ),
        "validation_error_count": len(errors),
        "validation_errors": errors,
        "validations": validations,
    }


def build_v4_5b_6_coverage_confidence_report() -> dict[str, Any]:
    intelligence = build_v4_5b_6_coverage_confidence()
    validation = validate_v4_5b_6_coverage_confidence(intelligence)
    exported = export_v4_5b_6_coverage_confidence(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_and_hashing"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_coverage_diagnostics"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "coverage_confidence_identity_hash": hash_coverage_confidence_identity(
            intelligence.identity
        ),
        "coverage_confidence_visibility_hash": hash_v4_5b_6_coverage_confidence(
            intelligence
        ),
        "coverage_visibility_hashes": {
            record.coverage_record_id: hash_coverage_visibility_record(record)
            for record in sorted(
                intelligence.coverage_visibility_records,
                key=lambda item: (item.deterministic_order, item.coverage_record_id),
            )
        },
        "support_coverage_hashes": {
            record.support_coverage_id: hash_support_coverage_record(record)
            for record in sorted(
                intelligence.support_coverage_records,
                key=lambda item: (item.deterministic_order, item.support_coverage_id),
            )
        },
        "evidence_coverage_hashes": {
            record.evidence_coverage_id: hash_evidence_coverage_record(record)
            for record in sorted(
                intelligence.evidence_coverage_records,
                key=lambda item: (item.deterministic_order, item.evidence_coverage_id),
            )
        },
        "explainability_coverage_hashes": {
            record.explainability_coverage_id: hash_explainability_coverage_record(
                record
            )
            for record in sorted(
                intelligence.explainability_coverage_records,
                key=lambda item: (
                    item.deterministic_order,
                    item.explainability_coverage_id,
                ),
            )
        },
        "provenance_lineage_coverage_hashes": {
            record.provenance_lineage_coverage_id: (
                hash_provenance_lineage_coverage_record(record)
            )
            for record in sorted(
                intelligence.provenance_lineage_coverage_records,
                key=lambda item: (
                    item.deterministic_order,
                    item.provenance_lineage_coverage_id,
                ),
            )
        },
        "confidence_visibility_hashes": {
            record.confidence_record_id: hash_confidence_visibility_record(record)
            for record in sorted(
                intelligence.confidence_visibility_records,
                key=lambda item: (item.deterministic_order, item.confidence_record_id),
            )
        },
        "incomplete_unknown_coverage_hashes": {
            record.incomplete_unknown_id: hash_incomplete_unknown_coverage_record(
                record
            )
            for record in sorted(
                intelligence.incomplete_unknown_coverage_records,
                key=lambda item: (item.deterministic_order, item.incomplete_unknown_id),
            )
        },
        "summary_hashes": {
            record.summary_record_id: hash_coverage_confidence_summary_record(record)
            for record in sorted(
                intelligence.summary_records,
                key=lambda item: (item.deterministic_order, item.summary_record_id),
            )
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_coverage_diagnostic_record(record)
            for record in sorted(
                intelligence.diagnostic_records,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_operational_hashes": {
            record.state_id: (
                hash_unsupported_coverage_confidence_operational_state_visibility(
                    record
                )
            )
            for record in sorted(
                intelligence.unsupported_operational_state_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "coverage_visibility_record_count": len(intelligence.coverage_visibility_records),
        "support_coverage_record_count": len(intelligence.support_coverage_records),
        "evidence_coverage_record_count": len(intelligence.evidence_coverage_records),
        "explainability_coverage_record_count": len(
            intelligence.explainability_coverage_records
        ),
        "provenance_lineage_coverage_record_count": len(
            intelligence.provenance_lineage_coverage_records
        ),
        "confidence_visibility_record_count": len(
            intelligence.confidence_visibility_records
        ),
        "incomplete_unknown_coverage_record_count": len(
            intelligence.incomplete_unknown_coverage_records
        ),
        "summary_record_count": len(intelligence.summary_records),
        "diagnostic_record_count": len(intelligence.diagnostic_records),
        "unsupported_operational_state_count": len(
            intelligence.unsupported_operational_state_visibility
        ),
        "coverage_counts": required_visibility["coverage_counts"],
        "support_counts": required_visibility["support_counts"],
        "evidence_counts": required_visibility["evidence_counts"],
        "explainability_counts": required_visibility["explainability_counts"],
        "provenance_lineage_counts": required_visibility[
            "provenance_lineage_counts"
        ],
        "confidence_counts": required_visibility["confidence_counts"],
        "incomplete_unknown_counts": required_visibility[
            "incomplete_unknown_counts"
        ],
        "summary_counts": required_visibility["summary_counts"],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_coverage_serialization_verified": serialization_hashing[
            "coverage_serialization_stable"
        ],
        "deterministic_confidence_serialization_verified": serialization_hashing[
            "confidence_serialization_stable"
        ],
        "deterministic_coverage_hashing_verified": serialization_hashing[
            "coverage_hashing_stable"
        ],
        "deterministic_confidence_hashing_verified": serialization_hashing[
            "confidence_hashing_stable"
        ],
        "coverage_visibility_stable": validation["validations"][
            "coverage_visibility"
        ]["valid"],
        "support_coverage_stable": validation["validations"]["support_coverage"][
            "valid"
        ],
        "evidence_coverage_stable": validation["validations"]["evidence_coverage"][
            "valid"
        ],
        "explainability_coverage_stable": validation["validations"][
            "explainability_coverage"
        ]["valid"],
        "provenance_lineage_coverage_stable": validation["validations"][
            "provenance_lineage_coverage"
        ]["valid"],
        "confidence_visibility_stable": validation["validations"][
            "confidence_visibility"
        ]["valid"],
        "incomplete_unknown_coverage_visibility_preserved": validation[
            "validations"
        ]["incomplete_unknown_coverage"]["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "evidence_panel_continuity_preserved": lineage_provenance[
            "evidence_panel_continuity_preserved"
        ],
        "fail_visible_coverage_diagnostics_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "publicly_transparent": descriptive_only["publicly_transparent"],
        "coverage_confidence_statement": descriptive_only[
            "coverage_confidence_statement"
        ],
        "coverage_confidence_non_authority_statement": descriptive_only[
            "coverage_confidence_non_authority_statement"
        ],
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
        "phase_id": V4_5B_6_COVERAGE_CONFIDENCE_PHASE_ID,
        "schema_version": V4_5B_6_COVERAGE_CONFIDENCE_REPORT_SCHEMA_VERSION,
        "generated_at": V4_5B_6_COVERAGE_CONFIDENCE_GENERATED_AT,
        "purpose": V4_5B_6_COVERAGE_CONFIDENCE_PURPOSE,
        "foundation_status": validation["foundation_status"],
        "summary": summary,
        "visibility": {
            "coverage": coverage_visibility_summary(
                intelligence.coverage_visibility_records
            ),
            "confidence": confidence_visibility_summary(
                intelligence.confidence_visibility_records
            ),
            "support_coverage": support_coverage_summary(
                intelligence.support_coverage_records
            ),
            "evidence_coverage": evidence_coverage_summary(
                intelligence.evidence_coverage_records
            ),
            "explainability_coverage": explainability_coverage_summary(
                intelligence.explainability_coverage_records
            ),
            "provenance_lineage_coverage": provenance_lineage_coverage_summary(
                intelligence.provenance_lineage_coverage_records
            ),
            "incomplete_unknown_coverage": incomplete_unknown_coverage_summary(
                intelligence.incomplete_unknown_coverage_records
            ),
            "summaries": coverage_confidence_summary_visibility(
                intelligence.summary_records
            ),
            "diagnostics": coverage_diagnostic_summary(
                intelligence.diagnostic_records
            ),
            "unsupported_operational_states": unsupported_operational_state_summary(
                intelligence.unsupported_operational_state_visibility
            ),
            "descriptive_only": descriptive_only_coverage_confidence_summary(
                intelligence
            ),
        },
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "validation": validation,
        "exported_intelligence": exported,
    }
    report["deterministic_report_hash"] = (
        deterministic_v4_5b_6_coverage_confidence_hash(report)
    )
    return report


def contaminate_v4_5b_6_coverage_confidence_for_non_operational_validation(
    intelligence: CoverageConfidenceIntelligence | None = None,
) -> CoverageConfidenceIntelligence:
    if intelligence is None:
        intelligence = build_v4_5b_6_coverage_confidence()
    return replace(
        intelligence,
        runtime_execution_enabled=True,
        confidence_authorization_enabled=True,
        confidence_approval_enabled=True,
        coverage_ranking_enabled=True,
        confidence_recommendation_enabled=True,
        trust_scoring_enabled=True,
        evidence_scoring_enabled=True,
        remediation_enabled=True,
        planner_integration_enabled=True,
    )
