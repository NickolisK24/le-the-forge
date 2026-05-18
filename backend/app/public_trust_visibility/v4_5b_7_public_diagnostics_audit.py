"""Audit for deterministic v4.5B.7 public diagnostics visibility."""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5b_7_public_diagnostics_hashing import (
    deterministic_v4_5b_7_public_diagnostics_hash,
    hash_blocker_warning_summary_record,
    hash_coverage_confidence_diagnostics_record,
    hash_diagnostics_summary_record,
    hash_evidence_panel_diagnostics_record,
    hash_explainability_diagnostics_record,
    hash_fail_visible_public_diagnostic_record,
    hash_inherited_limitation_visibility_record,
    hash_provenance_lineage_diagnostics_record,
    hash_public_diagnostics_identity,
    hash_public_diagnostics_visibility_record,
    hash_support_diagnostics_record,
    hash_unsupported_public_diagnostics_operational_state_visibility,
    hash_v4_5b_7_public_diagnostics,
)
from .v4_5b_7_public_diagnostics_models import (
    BLOCKER_WARNING_SUMMARY_TYPES,
    COVERAGE_CONFIDENCE_DIAGNOSTIC_TYPES,
    DIAGNOSTICS_SUMMARY_TYPES,
    DIAGNOSTICS_VISIBILITY_NON_AUTHORITY_STATEMENT,
    EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
    EXPLAINABILITY_DIAGNOSTIC_TYPES,
    FAIL_VISIBLE_PUBLIC_DIAGNOSTIC_TYPES,
    INHERITED_LIMITATION_VISIBILITY_TYPES,
    PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
    PUBLIC_DIAGNOSTICS_STATEMENT,
    PUBLIC_DIAGNOSTICS_VISIBILITY_TYPES,
    SUPPORT_DIAGNOSTIC_TYPES,
    UNSUPPORTED_PUBLIC_DIAGNOSTICS_OPERATIONAL_STATES,
    V4_5B_7_PUBLIC_DIAGNOSTICS_DISABLED_COUNTER_NAMES,
    V4_5B_7_PUBLIC_DIAGNOSTICS_GENERATED_AT,
    V4_5B_7_PUBLIC_DIAGNOSTICS_PHASE_ID,
    V4_5B_7_PUBLIC_DIAGNOSTICS_PURPOSE,
    V4_5B_7_PUBLIC_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_5B_7_PUBLIC_DIAGNOSTICS_STATUS_BLOCKED,
    V4_5B_7_PUBLIC_DIAGNOSTICS_STATUS_STABLE,
    PublicDiagnosticsIntelligence,
    default_v4_5b_7_public_diagnostics,
)
from .v4_5b_7_public_diagnostics_serialization import (
    export_v4_5b_7_public_diagnostics,
    serialize_v4_5b_7_public_diagnostics,
)
from .v4_5b_7_public_diagnostics_visibility import (
    blocker_warning_summary,
    coverage_confidence_diagnostics_summary,
    descriptive_only_public_diagnostics_summary,
    diagnostics_summary_visibility,
    evidence_panel_diagnostics_summary,
    explainability_diagnostics_summary,
    fail_visible_public_diagnostics_summary,
    inherited_limitation_summary,
    provenance_lineage_diagnostics_summary,
    public_diagnostics_summary,
    support_diagnostics_summary,
    unsupported_operational_state_summary,
    validate_required_public_diagnostics_visibility,
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
    "enabled_diagnostics_authorization_count": (
        "diagnostics_authorization_enabled",
        "authorization_enabled",
    ),
    "enabled_diagnostics_approval_count": (
        "diagnostics_approval_enabled",
        "approval_enabled",
    ),
    "enabled_diagnostics_ranking_count": (
        "diagnostics_ranking_enabled",
        "ranking_enabled",
        "prioritization_enabled",
    ),
    "enabled_diagnostics_recommendation_count": (
        "diagnostics_recommendation_enabled",
        "recommendation_enabled",
    ),
    "enabled_scoring_count": (
        "scoring_enabled",
        "trust_scoring_enabled",
    ),
    "enabled_triage_count": (
        "diagnostics_triage_enabled",
        "triage_enabled",
    ),
    "enabled_remediation_count": (
        "remediation_enabled",
        "evidence_repair_enabled",
    ),
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


def build_v4_5b_7_public_diagnostics() -> PublicDiagnosticsIntelligence:
    return default_v4_5b_7_public_diagnostics()


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
        getattr(item, "diagnostics_record_id", None)
        or getattr(item, "support_diagnostics_id", None)
        or getattr(item, "explainability_diagnostics_id", None)
        or getattr(item, "provenance_lineage_diagnostics_id", None)
        or getattr(item, "evidence_diagnostics_id", None)
        or getattr(item, "coverage_confidence_diagnostics_id", None)
        or getattr(item, "inherited_limitation_id", None)
        or getattr(item, "blocker_warning_id", None)
        or getattr(item, "summary_record_id", None)
        or getattr(item, "diagnostic_id", None)
        or getattr(item, "state_id", None)
        or getattr(item, "public_diagnostics_id", item.__class__.__name__)
    )


def enabled_public_diagnostics_capability_flags(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(_record_id(item), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def public_diagnostics_capability_counter_values(
    intelligence: PublicDiagnosticsIntelligence,
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


def public_diagnostics_equal(
    left: PublicDiagnosticsIntelligence,
    right: PublicDiagnosticsIntelligence,
) -> bool:
    return serialize_v4_5b_7_public_diagnostics(
        left
    ) == serialize_v4_5b_7_public_diagnostics(right)


def validate_public_diagnostics_ordering_stability(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    reordered = replace(
        intelligence,
        public_diagnostics_records=tuple(
            reversed(intelligence.public_diagnostics_records)
        ),
        support_diagnostics_records=tuple(
            reversed(intelligence.support_diagnostics_records)
        ),
        explainability_diagnostics_records=tuple(
            reversed(intelligence.explainability_diagnostics_records)
        ),
        provenance_lineage_diagnostics_records=tuple(
            reversed(intelligence.provenance_lineage_diagnostics_records)
        ),
        evidence_panel_diagnostics_records=tuple(
            reversed(intelligence.evidence_panel_diagnostics_records)
        ),
        coverage_confidence_diagnostics_records=tuple(
            reversed(intelligence.coverage_confidence_diagnostics_records)
        ),
        inherited_limitation_records=tuple(
            reversed(intelligence.inherited_limitation_records)
        ),
        blocker_warning_records=tuple(reversed(intelligence.blocker_warning_records)),
        summary_records=tuple(reversed(intelligence.summary_records)),
        fail_visible_diagnostic_records=tuple(
            reversed(intelligence.fail_visible_diagnostic_records)
        ),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )
    serialization_stable = serialize_v4_5b_7_public_diagnostics(
        intelligence
    ) == serialize_v4_5b_7_public_diagnostics(reordered)
    hashing_stable = hash_v4_5b_7_public_diagnostics(
        intelligence
    ) == hash_v4_5b_7_public_diagnostics(reordered)
    return {
        "valid": serialization_stable and hashing_stable,
        "serialization_stable": serialization_stable,
        "hashing_stable": hashing_stable,
    }


def validate_public_diagnostics_identity_integrity(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    identity = intelligence.identity
    required_fields = (
        "public_diagnostics_id",
        "diagnostics_summary_id",
        "support_diagnostics_reference_id",
        "explainability_diagnostics_reference_id",
        "provenance_diagnostics_reference_id",
        "lineage_diagnostics_reference_id",
        "evidence_panel_diagnostics_reference_id",
        "coverage_diagnostics_reference_id",
        "confidence_diagnostics_reference_id",
        "continuity_reference_id",
        "lineage_reference_id",
        "provenance_reference_id",
        "source_coverage_confidence_report_reference",
        "source_coverage_confidence_hash_reference",
    )
    missing_fields = [field for field in required_fields if not getattr(identity, field)]
    source_report_exists = _relative_path_exists(
        identity.source_coverage_confidence_report_reference
    )
    source_hash_matches = _report_hash_matches(
        identity.source_coverage_confidence_report_reference,
        identity.source_coverage_confidence_hash_reference,
    )
    phase_valid = identity.phase_id == V4_5B_7_PUBLIC_DIAGNOSTICS_PHASE_ID
    generated_at_valid = identity.generated_at == V4_5B_7_PUBLIC_DIAGNOSTICS_GENERATED_AT
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


def validate_public_diagnostics_visibility_stability(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.public_diagnostics_records,
        type_field="diagnostics_type",
        expected_types=PUBLIC_DIAGNOSTICS_VISIBILITY_TYPES,
        prohibited_fields=(
            "authorization_enabled",
            "approval_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "triage_enabled",
            "operational_enabled",
        ),
        required_reference_fields=("diagnostics_reference_id",),
    )


def validate_support_diagnostics_visibility_stability(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.support_diagnostics_records,
        type_field="support_diagnostics_type",
        expected_types=SUPPORT_DIAGNOSTIC_TYPES,
        prohibited_fields=(
            "triage_enabled",
            "recommendation_enabled",
            "approval_enabled",
        ),
        required_reference_fields=("support_diagnostics_reference_id",),
    )


def validate_explainability_diagnostics_visibility_stability(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.explainability_diagnostics_records,
        type_field="explainability_diagnostics_type",
        expected_types=EXPLAINABILITY_DIAGNOSTIC_TYPES,
        prohibited_fields=(
            "operational_semantics_enabled",
            "recommendation_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
        required_reference_fields=(
            "explainability_diagnostics_reference_id",
            "continuity_reference_id",
        ),
    )


def validate_provenance_lineage_diagnostics_visibility_stability(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.provenance_lineage_diagnostics_records,
        type_field="provenance_lineage_diagnostics_type",
        expected_types=PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
        prohibited_fields=(
            "source_authority_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
        required_reference_fields=(
            "provenance_diagnostics_reference_id",
            "lineage_diagnostics_reference_id",
        ),
    )


def validate_evidence_panel_diagnostics_visibility_stability(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.evidence_panel_diagnostics_records,
        type_field="evidence_diagnostics_type",
        expected_types=EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
        prohibited_fields=(
            "evidence_repair_enabled",
            "remediation_enabled",
            "ranking_enabled",
            "recommendation_enabled",
        ),
        required_reference_fields=("evidence_panel_diagnostics_reference_id",),
    )


def validate_coverage_confidence_diagnostics_visibility_stability(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.coverage_confidence_diagnostics_records,
        type_field="coverage_confidence_diagnostics_type",
        expected_types=COVERAGE_CONFIDENCE_DIAGNOSTIC_TYPES,
        prohibited_fields=(
            "scoring_enabled",
            "trust_scoring_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "triage_enabled",
        ),
        required_reference_fields=(
            "coverage_diagnostics_reference_id",
            "confidence_diagnostics_reference_id",
        ),
    )


def validate_inherited_limitation_visibility_preservation(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.inherited_limitation_records,
        type_field="inherited_limitation_type",
        expected_types=INHERITED_LIMITATION_VISIBILITY_TYPES,
        prohibited_fields=(
            "suppression_enabled",
            "hidden_fallback_enabled",
            "remediation_enabled",
        ),
        required_reference_fields=("diagnostics_reference_id",),
        require_fail_visible=True,
    )


def validate_blocker_warning_visibility_preservation(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.blocker_warning_records,
        type_field="blocker_warning_type",
        expected_types=BLOCKER_WARNING_SUMMARY_TYPES,
        prohibited_fields=(
            "prioritization_enabled",
            "triage_enabled",
            "ranking_enabled",
            "recommendation_enabled",
        ),
        required_reference_fields=("diagnostics_reference_id",),
    )


def validate_diagnostics_summary_stability(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return _validate_required_types(
        intelligence.summary_records,
        type_field="summary_type",
        expected_types=DIAGNOSTICS_SUMMARY_TYPES,
        prohibited_fields=(
            "authorization_enabled",
            "approval_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "scoring_enabled",
            "triage_enabled",
            "execution_enablement_enabled",
            "production_enablement_enabled",
        ),
        required_reference_fields=("diagnostics_reference_id",),
    )


def validate_lineage_and_provenance_preservation(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    identity = intelligence.identity
    missing_identity_lineage = not identity.lineage_reference_id
    missing_identity_provenance = not identity.provenance_reference_id
    missing_provenance = sorted(
        record.provenance_lineage_diagnostics_id
        for record in intelligence.provenance_lineage_diagnostics_records
        if not record.provenance_diagnostics_reference_id
    )
    missing_lineage = sorted(
        record.provenance_lineage_diagnostics_id
        for record in intelligence.provenance_lineage_diagnostics_records
        if not record.lineage_diagnostics_reference_id
    )
    missing_diagnostics_references = sorted(
        _record_id(record)
        for record in _iter_dataclass_objects(intelligence)
        if hasattr(record, "diagnostics_reference_id")
        and not str(getattr(record, "diagnostics_reference_id", ""))
    )
    return {
        "valid": not any(
            (
                missing_identity_lineage,
                missing_identity_provenance,
                missing_provenance,
                missing_lineage,
                missing_diagnostics_references,
            )
        ),
        "lineage_continuity_preserved": not missing_identity_lineage
        and not missing_lineage,
        "provenance_continuity_preserved": not missing_identity_provenance
        and not missing_provenance,
        "diagnostics_reference_continuity_preserved": (
            not missing_diagnostics_references
        ),
        "missing_identity_lineage": missing_identity_lineage,
        "missing_identity_provenance": missing_identity_provenance,
        "missing_provenance": missing_provenance,
        "missing_lineage": missing_lineage,
        "missing_diagnostics_references": missing_diagnostics_references,
    }


def validate_public_diagnostics_serialization_and_hashing(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    serialization_one = serialize_v4_5b_7_public_diagnostics(intelligence)
    serialization_two = serialize_v4_5b_7_public_diagnostics(
        default_v4_5b_7_public_diagnostics()
    )
    hash_one = hash_v4_5b_7_public_diagnostics(intelligence)
    hash_two = hash_v4_5b_7_public_diagnostics(
        default_v4_5b_7_public_diagnostics()
    )
    ordering = validate_public_diagnostics_ordering_stability(intelligence)
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


def validate_fail_visible_public_diagnostics(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    diagnostics = _validate_required_types(
        intelligence.fail_visible_diagnostic_records,
        type_field="diagnostic_type",
        expected_types=FAIL_VISIBLE_PUBLIC_DIAGNOSTIC_TYPES,
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
            "triage_enabled",
            "orchestration_response_enabled",
        ),
        required_reference_fields=("diagnostics_reference_id",),
        require_fail_visible=True,
    )
    unsupported = _validate_required_types(
        intelligence.unsupported_operational_state_visibility,
        type_field="unsupported_state",
        expected_types=UNSUPPORTED_PUBLIC_DIAGNOSTICS_OPERATIONAL_STATES,
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
            "triage_enabled",
            "suppression_enabled",
        ),
        required_reference_fields=("diagnostics_reference_id",),
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


def validate_descriptive_only_public_diagnostics_guarantees(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    counters = public_diagnostics_capability_counter_values(intelligence)
    enabled_flags = enabled_public_diagnostics_capability_flags(intelligence)
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
        "non_triaging": intelligence.non_triaging,
    }
    all_required_true = all(required_boundary_booleans.values())
    all_counters_zero = all(
        counters.get(counter_name, 1) == 0
        for counter_name in V4_5B_7_PUBLIC_DIAGNOSTICS_DISABLED_COUNTER_NAMES
    )
    statements_valid = (
        intelligence.public_diagnostics_statement == PUBLIC_DIAGNOSTICS_STATEMENT
        and intelligence.diagnostics_visibility_non_authority_statement
        == DIAGNOSTICS_VISIBILITY_NON_AUTHORITY_STATEMENT
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
        "public_diagnostics_statement": intelligence.public_diagnostics_statement,
        "diagnostics_visibility_non_authority_statement": (
            intelligence.diagnostics_visibility_non_authority_statement
        ),
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "explicit_limitation_count": len(intelligence.explicit_limitations),
    }


def validate_v4_5b_7_public_diagnostics(
    intelligence: PublicDiagnosticsIntelligence | None = None,
) -> dict[str, Any]:
    if intelligence is None:
        intelligence = build_v4_5b_7_public_diagnostics()
    validations = {
        "identity_integrity": validate_public_diagnostics_identity_integrity(
            intelligence
        ),
        "required_visibility": validate_required_public_diagnostics_visibility(
            intelligence
        ),
        "public_diagnostics": validate_public_diagnostics_visibility_stability(
            intelligence
        ),
        "support_diagnostics": validate_support_diagnostics_visibility_stability(
            intelligence
        ),
        "explainability_diagnostics": (
            validate_explainability_diagnostics_visibility_stability(intelligence)
        ),
        "provenance_lineage_diagnostics": (
            validate_provenance_lineage_diagnostics_visibility_stability(
                intelligence
            )
        ),
        "evidence_panel_diagnostics": (
            validate_evidence_panel_diagnostics_visibility_stability(intelligence)
        ),
        "coverage_confidence_diagnostics": (
            validate_coverage_confidence_diagnostics_visibility_stability(
                intelligence
            )
        ),
        "inherited_limitation_visibility": (
            validate_inherited_limitation_visibility_preservation(intelligence)
        ),
        "blocker_warning_visibility": (
            validate_blocker_warning_visibility_preservation(intelligence)
        ),
        "summary_stability": validate_diagnostics_summary_stability(intelligence),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_and_hashing": (
            validate_public_diagnostics_serialization_and_hashing(intelligence)
        ),
        "fail_visible_public_diagnostics": validate_fail_visible_public_diagnostics(
            intelligence
        ),
        "descriptive_only_guarantees": (
            validate_descriptive_only_public_diagnostics_guarantees(intelligence)
        ),
    }
    errors = sorted(name for name, result in validations.items() if not result["valid"])
    return {
        "valid": not errors,
        "foundation_status": (
            V4_5B_7_PUBLIC_DIAGNOSTICS_STATUS_STABLE
            if not errors
            else V4_5B_7_PUBLIC_DIAGNOSTICS_STATUS_BLOCKED
        ),
        "validation_error_count": len(errors),
        "validation_errors": errors,
        "validations": validations,
    }


def build_v4_5b_7_public_diagnostics_report() -> dict[str, Any]:
    intelligence = build_v4_5b_7_public_diagnostics()
    validation = validate_v4_5b_7_public_diagnostics(intelligence)
    exported = export_v4_5b_7_public_diagnostics(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_and_hashing"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_public_diagnostics"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "public_diagnostics_identity_hash": hash_public_diagnostics_identity(
            intelligence.identity
        ),
        "public_diagnostics_visibility_hash": hash_v4_5b_7_public_diagnostics(
            intelligence
        ),
        "public_diagnostics_hashes": {
            record.diagnostics_record_id: hash_public_diagnostics_visibility_record(
                record
            )
            for record in sorted(
                intelligence.public_diagnostics_records,
                key=lambda item: (item.deterministic_order, item.diagnostics_record_id),
            )
        },
        "support_diagnostics_hashes": {
            record.support_diagnostics_id: hash_support_diagnostics_record(record)
            for record in sorted(
                intelligence.support_diagnostics_records,
                key=lambda item: (item.deterministic_order, item.support_diagnostics_id),
            )
        },
        "explainability_diagnostics_hashes": {
            record.explainability_diagnostics_id: (
                hash_explainability_diagnostics_record(record)
            )
            for record in sorted(
                intelligence.explainability_diagnostics_records,
                key=lambda item: (
                    item.deterministic_order,
                    item.explainability_diagnostics_id,
                ),
            )
        },
        "provenance_lineage_diagnostics_hashes": {
            record.provenance_lineage_diagnostics_id: (
                hash_provenance_lineage_diagnostics_record(record)
            )
            for record in sorted(
                intelligence.provenance_lineage_diagnostics_records,
                key=lambda item: (
                    item.deterministic_order,
                    item.provenance_lineage_diagnostics_id,
                ),
            )
        },
        "evidence_panel_diagnostics_hashes": {
            record.evidence_diagnostics_id: hash_evidence_panel_diagnostics_record(
                record
            )
            for record in sorted(
                intelligence.evidence_panel_diagnostics_records,
                key=lambda item: (item.deterministic_order, item.evidence_diagnostics_id),
            )
        },
        "coverage_confidence_diagnostics_hashes": {
            record.coverage_confidence_diagnostics_id: (
                hash_coverage_confidence_diagnostics_record(record)
            )
            for record in sorted(
                intelligence.coverage_confidence_diagnostics_records,
                key=lambda item: (
                    item.deterministic_order,
                    item.coverage_confidence_diagnostics_id,
                ),
            )
        },
        "inherited_limitation_hashes": {
            record.inherited_limitation_id: (
                hash_inherited_limitation_visibility_record(record)
            )
            for record in sorted(
                intelligence.inherited_limitation_records,
                key=lambda item: (item.deterministic_order, item.inherited_limitation_id),
            )
        },
        "blocker_warning_hashes": {
            record.blocker_warning_id: hash_blocker_warning_summary_record(record)
            for record in sorted(
                intelligence.blocker_warning_records,
                key=lambda item: (item.deterministic_order, item.blocker_warning_id),
            )
        },
        "summary_hashes": {
            record.summary_record_id: hash_diagnostics_summary_record(record)
            for record in sorted(
                intelligence.summary_records,
                key=lambda item: (item.deterministic_order, item.summary_record_id),
            )
        },
        "fail_visible_diagnostic_hashes": {
            record.diagnostic_id: hash_fail_visible_public_diagnostic_record(record)
            for record in sorted(
                intelligence.fail_visible_diagnostic_records,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_operational_hashes": {
            record.state_id: (
                hash_unsupported_public_diagnostics_operational_state_visibility(record)
            )
            for record in sorted(
                intelligence.unsupported_operational_state_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "public_diagnostics_record_count": len(intelligence.public_diagnostics_records),
        "support_diagnostics_record_count": len(intelligence.support_diagnostics_records),
        "explainability_diagnostics_record_count": len(
            intelligence.explainability_diagnostics_records
        ),
        "provenance_lineage_diagnostics_record_count": len(
            intelligence.provenance_lineage_diagnostics_records
        ),
        "evidence_panel_diagnostics_record_count": len(
            intelligence.evidence_panel_diagnostics_records
        ),
        "coverage_confidence_diagnostics_record_count": len(
            intelligence.coverage_confidence_diagnostics_records
        ),
        "inherited_limitation_record_count": len(
            intelligence.inherited_limitation_records
        ),
        "blocker_warning_record_count": len(intelligence.blocker_warning_records),
        "summary_record_count": len(intelligence.summary_records),
        "fail_visible_diagnostic_record_count": len(
            intelligence.fail_visible_diagnostic_records
        ),
        "unsupported_operational_state_count": len(
            intelligence.unsupported_operational_state_visibility
        ),
        "public_counts": required_visibility["public_counts"],
        "support_counts": required_visibility["support_counts"],
        "explainability_counts": required_visibility["explainability_counts"],
        "provenance_lineage_counts": required_visibility[
            "provenance_lineage_counts"
        ],
        "evidence_counts": required_visibility["evidence_counts"],
        "coverage_confidence_counts": required_visibility[
            "coverage_confidence_counts"
        ],
        "inherited_counts": required_visibility["inherited_counts"],
        "blocker_warning_counts": required_visibility["blocker_warning_counts"],
        "summary_counts": required_visibility["summary_counts"],
        "fail_visible_counts": required_visibility["fail_visible_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_diagnostics_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_diagnostics_hashing_verified": serialization_hashing[
            "hashing_stable"
        ],
        "diagnostics_visibility_stable": validation["validations"][
            "public_diagnostics"
        ]["valid"],
        "support_diagnostics_stable": validation["validations"][
            "support_diagnostics"
        ]["valid"],
        "explainability_diagnostics_stable": validation["validations"][
            "explainability_diagnostics"
        ]["valid"],
        "provenance_lineage_diagnostics_stable": validation["validations"][
            "provenance_lineage_diagnostics"
        ]["valid"],
        "evidence_diagnostics_stable": validation["validations"][
            "evidence_panel_diagnostics"
        ]["valid"],
        "coverage_confidence_diagnostics_stable": validation["validations"][
            "coverage_confidence_diagnostics"
        ]["valid"],
        "inherited_limitation_visibility_preserved": validation["validations"][
            "inherited_limitation_visibility"
        ]["valid"],
        "blocker_warning_visibility_preserved": validation["validations"][
            "blocker_warning_visibility"
        ]["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "diagnostics_reference_continuity_preserved": lineage_provenance[
            "diagnostics_reference_continuity_preserved"
        ],
        "fail_visible_diagnostics_preserved": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "publicly_transparent": descriptive_only["publicly_transparent"],
        "public_diagnostics_statement": descriptive_only[
            "public_diagnostics_statement"
        ],
        "diagnostics_visibility_non_authority_statement": descriptive_only[
            "diagnostics_visibility_non_authority_statement"
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
            "NON-triaging",
        ],
    }
    summary.update(counters)
    report = {
        "phase_id": V4_5B_7_PUBLIC_DIAGNOSTICS_PHASE_ID,
        "schema_version": V4_5B_7_PUBLIC_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_5B_7_PUBLIC_DIAGNOSTICS_GENERATED_AT,
        "purpose": V4_5B_7_PUBLIC_DIAGNOSTICS_PURPOSE,
        "foundation_status": validation["foundation_status"],
        "summary": summary,
        "visibility": {
            "public_diagnostics": public_diagnostics_summary(
                intelligence.public_diagnostics_records
            ),
            "support_diagnostics": support_diagnostics_summary(
                intelligence.support_diagnostics_records
            ),
            "explainability_diagnostics": explainability_diagnostics_summary(
                intelligence.explainability_diagnostics_records
            ),
            "provenance_lineage_diagnostics": (
                provenance_lineage_diagnostics_summary(
                    intelligence.provenance_lineage_diagnostics_records
                )
            ),
            "evidence_panel_diagnostics": evidence_panel_diagnostics_summary(
                intelligence.evidence_panel_diagnostics_records
            ),
            "coverage_confidence_diagnostics": (
                coverage_confidence_diagnostics_summary(
                    intelligence.coverage_confidence_diagnostics_records
                )
            ),
            "inherited_limitations": inherited_limitation_summary(
                intelligence.inherited_limitation_records
            ),
            "blocker_warnings": blocker_warning_summary(
                intelligence.blocker_warning_records
            ),
            "summaries": diagnostics_summary_visibility(
                intelligence.summary_records
            ),
            "fail_visible_diagnostics": fail_visible_public_diagnostics_summary(
                intelligence.fail_visible_diagnostic_records
            ),
            "unsupported_operational_states": unsupported_operational_state_summary(
                intelligence.unsupported_operational_state_visibility
            ),
            "descriptive_only": descriptive_only_public_diagnostics_summary(
                intelligence
            ),
        },
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "validation": validation,
        "exported_intelligence": exported,
    }
    report["deterministic_report_hash"] = (
        deterministic_v4_5b_7_public_diagnostics_hash(report)
    )
    return report


def contaminate_v4_5b_7_public_diagnostics_for_non_operational_validation(
    intelligence: PublicDiagnosticsIntelligence | None = None,
) -> PublicDiagnosticsIntelligence:
    if intelligence is None:
        intelligence = build_v4_5b_7_public_diagnostics()
    return replace(
        intelligence,
        runtime_execution_enabled=True,
        diagnostics_authorization_enabled=True,
        diagnostics_approval_enabled=True,
        diagnostics_ranking_enabled=True,
        diagnostics_recommendation_enabled=True,
        diagnostics_triage_enabled=True,
        scoring_enabled=True,
        remediation_enabled=True,
        planner_integration_enabled=True,
    )
