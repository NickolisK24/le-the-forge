"""Audit for deterministic v4.4 blocker resolution closeout preparation."""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_boundary_blocker_resolution_hashing import (
    deterministic_boundary_blocker_resolution_hash,
    hash_blocker_classification_identity,
    hash_blocker_classification_record,
    hash_blocker_resolution_lineage,
    hash_blocker_resolution_provenance,
    hash_blocker_resolution_replay_rollback,
    hash_boundary_blocker_resolution_closeout_preparation,
    hash_closeout_eligibility_identity,
    hash_closeout_eligibility_record,
    hash_closeout_preparation_summary,
    hash_escalation_record,
    hash_fail_visible_explanation_record,
    hash_inherited_constraint_record,
    hash_inherited_prohibition_record,
    hash_non_operational_blocker_certification,
    hash_phase8_readiness_evidence_reference,
    hash_unresolved_limitation_record,
    hash_v4_5_inherited_planning_boundary_identity,
    hash_v4_5_inherited_planning_boundary_record,
    hash_warning_classification_identity,
    hash_warning_classification_record,
)
from .v4_4_boundary_blocker_resolution_models import (
    V4_4_BOUNDARY_BLOCKER_RESOLUTION_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_BLOCKER_RESOLUTION_REPORT_SCHEMA_VERSION,
    V4_4_BOUNDARY_BLOCKER_RESOLUTION_STATUS_BLOCKED,
    V4_4_BOUNDARY_BLOCKER_RESOLUTION_STATUS_STABLE,
    BoundaryBlockerResolutionCloseoutPreparation,
    default_boundary_blocker_resolution_closeout_preparation,
)
from .v4_4_boundary_blocker_resolution_serialization import (
    export_blocker_classification_record,
    export_boundary_blocker_resolution_closeout_preparation,
    export_warning_classification_record,
    serialize_boundary_blocker_resolution_closeout_preparation,
)
from .v4_4_boundary_blocker_resolution_visibility import (
    blocker_resolution_summaries,
    closeout_eligibility_summaries,
    closeout_summary_visibility,
    count_combined_blocker_resolution_states,
    escalation_summaries,
    fail_visible_blocker_summaries,
    governance_safe_closeout_explainability,
    inherited_constraint_summaries,
    inherited_prohibition_summaries,
    lineage_continuity_visibility,
    provenance_continuity_visibility,
    unresolved_limitation_summaries,
    v4_5_planning_boundary_summaries,
    validate_required_blocker_resolution_visibility,
    warning_classification_summaries,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_runtime_behavior_enabled",
        "orchestration_execution_enabled",
        "execution_enabled",
        "runtime_activation_enabled",
        "runtime_readiness_inferred",
        "runtime_activation_signal_enabled",
    ),
    "enabled_orchestration_authorization_count": (
        "orchestration_authorization_enabled",
        "authorization_enabled",
    ),
    "enabled_orchestration_approval_count": (
        "orchestration_approval_enabled",
        "approval_enabled",
        "readiness_approval_enabled",
    ),
    "enabled_orchestration_activation_count": (
        "orchestration_activation_enabled",
        "activation_enabled",
        "transition_activation_enabled",
    ),
    "enabled_dispatch_execution_count": (
        "dispatch_execution_enabled",
        "dispatch_enabled",
        "orchestration_dispatch_enabled",
    ),
    "enabled_routing_execution_count": (
        "routing_execution_enabled",
        "routing_enabled",
        "orchestration_routing_enabled",
    ),
    "enabled_scheduling_execution_count": (
        "scheduling_execution_enabled",
        "scheduling_enabled",
        "orchestration_scheduling_enabled",
    ),
    "enabled_recommendation_count": (
        "recommendation_enabled",
        "orchestration_recommendation_enabled",
    ),
    "enabled_decision_count": (
        "decision_enabled",
        "orchestration_decision_enabled",
    ),
    "enabled_blocker_authorization_count": (
        "blocker_authorization_enabled",
        "blocker_authorization_signal_enabled",
        "readiness_authorization_enabled",
    ),
    "enabled_closeout_activation_count": (
        "closeout_activation_enabled",
        "closeout_activation_signal_enabled",
        "v4_5_activation_enabled",
        "v4_5_runtime_activation_enabled",
        "v4_5_activation_signal_enabled",
    ),
    "enabled_operational_mutation_count": (
        "operational_mutation_enabled",
        "runtime_mutation_enabled",
        "mutation_enabled",
    ),
}
PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_4_boundary_blocker_resolution() -> (
    BoundaryBlockerResolutionCloseoutPreparation
):
    return default_boundary_blocker_resolution_closeout_preparation()


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


def enabled_boundary_blocker_resolution_capability_flags(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(certification):
        item_id = (
            getattr(item, "blocker_classification_id", None)
            or getattr(item, "warning_classification_id", None)
            or getattr(item, "closeout_eligibility_id", None)
            or getattr(item, "planning_boundary_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "blocker_id", None)
            or getattr(item, "warning_id", None)
            or getattr(item, "prohibition_id", None)
            or getattr(item, "constraint_id", None)
            or getattr(item, "limitation_id", None)
            or getattr(item, "escalation_id", None)
            or getattr(item, "eligibility_id", None)
            or getattr(item, "explanation_id", None)
            or getattr(item, "certification_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "summary_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def boundary_blocker_resolution_capability_counter_values(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, int]:
    objects = tuple(_iter_dataclass_objects(certification))
    counters: dict[str, int] = {}
    for counter_name, field_names in CAPABILITY_COUNTER_FIELD_MAP.items():
        counters[counter_name] = sum(
            1
            for item in objects
            for field_name in field_names
            if bool(getattr(item, field_name, False))
        )
    return counters


def boundary_blocker_resolution_equal(
    left: BoundaryBlockerResolutionCloseoutPreparation,
    right: BoundaryBlockerResolutionCloseoutPreparation,
) -> bool:
    return serialize_boundary_blocker_resolution_closeout_preparation(
        left
    ) == serialize_boundary_blocker_resolution_closeout_preparation(right)


def validate_blocker_resolution_ordering_stability(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    order_groups = {
        "phase8_evidence_references": tuple(
            item.deterministic_order for item in certification.phase8_evidence_references
        ),
        "blocker_records": tuple(item.deterministic_order for item in certification.blocker_records),
        "warning_records": tuple(item.deterministic_order for item in certification.warning_records),
        "inherited_prohibition_records": tuple(
            item.deterministic_order for item in certification.inherited_prohibition_records
        ),
        "inherited_constraint_records": tuple(
            item.deterministic_order for item in certification.inherited_constraint_records
        ),
        "limitation_records": tuple(item.deterministic_order for item in certification.limitation_records),
        "escalation_records": tuple(item.deterministic_order for item in certification.escalation_records),
        "closeout_eligibility_records": tuple(
            item.deterministic_order for item in certification.closeout_eligibility_records
        ),
        "planning_boundary_records": tuple(
            item.deterministic_order for item in certification.planning_boundary_records
        ),
        "fail_visible_explanations": tuple(
            item.deterministic_order for item in certification.fail_visible_explanations
        ),
        "non_operational_certifications": tuple(
            item.deterministic_order for item in certification.non_operational_certifications
        ),
        "closeout_summaries": tuple(
            item.deterministic_order for item in certification.closeout_summaries
        ),
    }
    unordered_groups = [name for name, orders in order_groups.items() if tuple(sorted(orders)) != orders]
    duplicate_groups = [name for name, orders in order_groups.items() if len(set(orders)) != len(orders)]
    return {
        "valid": not unordered_groups and not duplicate_groups,
        "unordered_groups": unordered_groups,
        "duplicate_order_groups": duplicate_groups,
        "order_groups": {name: list(orders) for name, orders in order_groups.items()},
    }


def validate_blocker_resolution_serialization_and_hashing(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    rebuilt = build_v4_4_boundary_blocker_resolution()
    serialized = serialize_boundary_blocker_resolution_closeout_preparation(certification)
    rebuilt_serialized = serialize_boundary_blocker_resolution_closeout_preparation(rebuilt)
    certification_hash = hash_boundary_blocker_resolution_closeout_preparation(
        certification
    )
    rebuilt_hash = hash_boundary_blocker_resolution_closeout_preparation(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and certification_hash == rebuilt_hash,
        "blocker_serialization_stable": serialized == rebuilt_serialized,
        "warning_serialization_stable": serialized == rebuilt_serialized,
        "escalation_hashing_stable": certification_hash == rebuilt_hash,
        "closeout_hashing_stable": certification_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "certification_hash": certification_hash,
        "rebuilt_certification_hash": rebuilt_hash,
    }


def validate_blocker_resolution_visibility(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    required = validate_required_blocker_resolution_visibility(certification)
    blockers = blocker_resolution_summaries(certification)
    warnings = warning_classification_summaries(certification)
    prohibitions = inherited_prohibition_summaries(certification)
    constraints = inherited_constraint_summaries(certification)
    limitations = unresolved_limitation_summaries(certification)
    escalations = escalation_summaries(certification)
    closeout = closeout_eligibility_summaries(certification)
    planning_boundary = v4_5_planning_boundary_summaries(certification)
    fail_visible = fail_visible_blocker_summaries(certification)
    summary = closeout_summary_visibility(certification)
    explainability = governance_safe_closeout_explainability(certification)
    return {
        "valid": (
            required["valid"]
            and blockers["blocker_authorization_enabled_count"] == 0
            and blockers["approval_enabled_count"] == 0
            and blockers["activation_enabled_count"] == 0
            and blockers["recommendation_enabled_count"] == 0
            and blockers["decision_enabled_count"] == 0
            and blockers["automatic_remediation_enabled_count"] == 0
            and blockers["blocker_auto_resolution_enabled_count"] == 0
            and warnings["warning_suppression_enabled_count"] == 0
            and warnings["approval_enabled_count"] == 0
            and warnings["activation_enabled_count"] == 0
            and warnings["recommendation_enabled_count"] == 0
            and warnings["decision_enabled_count"] == 0
            and warnings["automatic_remediation_enabled_count"] == 0
            and prohibitions["runtime_execution_enabled_count"] == 0
            and prohibitions["orchestration_authorization_enabled_count"] == 0
            and prohibitions["orchestration_approval_enabled_count"] == 0
            and prohibitions["orchestration_activation_enabled_count"] == 0
            and prohibitions["planner_integration_enabled_count"] == 0
            and prohibitions["production_consumption_enabled_count"] == 0
            and constraints["planner_integration_enabled_count"] == 0
            and constraints["production_consumption_enabled_count"] == 0
            and constraints["v4_5_activation_enabled_count"] == 0
            and limitations["automatic_remediation_enabled_count"] == 0
            and limitations["automatic_repair_enabled_count"] == 0
            and escalations["closeout_activation_enabled_count"] == 0
            and escalations["automatic_remediation_enabled_count"] == 0
            and escalations["recommendation_enabled_count"] == 0
            and escalations["decision_enabled_count"] == 0
            and closeout["closeout_activation_enabled_count"] == 0
            and closeout["readiness_authorization_enabled_count"] == 0
            and closeout["runtime_readiness_inferred_count"] == 0
            and planning_boundary["v4_5_activation_enabled_count"] == 0
            and planning_boundary["planner_integration_enabled_count"] == 0
            and planning_boundary["production_consumption_enabled_count"] == 0
            and planning_boundary["runtime_readiness_inferred_count"] == 0
            and fail_visible["approval_enabled_count"] == 0
            and fail_visible["activation_enabled_count"] == 0
            and fail_visible["recommendation_enabled_count"] == 0
            and fail_visible["decision_enabled_count"] == 0
            and summary["closeout_activation_signal_enabled_count"] == 0
            and summary["blocker_authorization_signal_enabled_count"] == 0
            and summary["runtime_readiness_inferred_count"] == 0
            and explainability["descriptive_only"]
            and explainability["non_operational"]
            and explainability["runtime_readiness_inference_disabled"]
        ),
        "combined_counts": count_combined_blocker_resolution_states(certification),
        "missing_states": required["missing_states"],
        "missing_fail_visible_states": required["missing_fail_visible_states"],
        "blockers": blockers,
        "warnings": warnings,
        "prohibitions": prohibitions,
        "constraints": constraints,
        "limitations": limitations,
        "escalations": escalations,
        "closeout": closeout,
        "planning_boundary": planning_boundary,
        "fail_visible": fail_visible,
        "closeout_summary": summary,
        "explainability": explainability,
    }


def validate_blocker_resolution_replay_rollback_evidence(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    evidence = certification.replay_rollback_record
    expected = set(evidence.evidence_reference_ids)
    replay = set(evidence.replay_evidence_ids)
    rollback = set(evidence.rollback_evidence_ids)
    return {
        "valid": evidence.replay_safe and evidence.rollback_safe and replay == expected and rollback == expected,
        "expected_evidence_count": len(expected),
        "replay_safe_evidence_count": len(replay),
        "rollback_safe_evidence_count": len(rollback),
        "missing_replay_evidence_ids": sorted(expected - replay),
        "missing_rollback_evidence_ids": sorted(expected - rollback),
        "replay_safe": evidence.replay_safe,
        "rollback_safe": evidence.rollback_safe,
    }


def validate_blocker_resolution_provenance_lineage(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    provenance = certification.provenance_record
    lineage = certification.lineage_record
    return {
        "valid": (
            provenance.provenance_continuity_preserved
            and lineage.lineage_continuity_preserved
            and not provenance.hidden_source_inference_used
            and not lineage.ambiguous_lineage_inferred
            and not provenance.production_consumption_enabled
            and not lineage.operational_mutation_enabled
        ),
        "provenance_continuity_preserved": provenance.provenance_continuity_preserved,
        "lineage_continuity_preserved": lineage.lineage_continuity_preserved,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
        "production_consumption_enabled": provenance.production_consumption_enabled,
        "operational_mutation_enabled": lineage.operational_mutation_enabled,
    }


def validate_boundary_blocker_resolution_non_operational(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    counters = boundary_blocker_resolution_capability_counter_values(certification)
    enabled_flags = enabled_boundary_blocker_resolution_capability_flags(certification)
    root_disabled = {
        "descriptive_only": certification.descriptive_only,
        "non_operational": certification.non_operational,
        "non_authoritative": certification.non_authoritative,
        "non_authorizing": certification.non_authorizing,
        "non_approving": certification.non_approving,
        "non_activating": certification.non_activating,
        "non_recommending": certification.non_recommending,
        "non_deciding": certification.non_deciding,
        "non_remediating": certification.non_remediating,
        "non_mutating": certification.non_mutating,
        "runtime_readiness_inference_disabled": certification.runtime_readiness_inference_disabled,
        "planner_integration_disabled": not certification.planner_integration_enabled,
        "production_consumption_disabled": not certification.production_consumption_enabled,
        "runtime_mutation_disabled": not certification.runtime_mutation_enabled,
        "operational_mutation_disabled": not certification.operational_mutation_enabled,
        "traversal_execution_disabled": not certification.traversal_execution_enabled,
        "sequencing_execution_disabled": not certification.sequencing_execution_enabled,
        "ranking_disabled": not certification.ranking_enabled,
        "scoring_disabled": not certification.scoring_enabled,
        "selection_disabled": not certification.selection_enabled,
        "optimization_disabled": not certification.optimization_enabled,
        "automatic_remediation_disabled": not certification.automatic_remediation_enabled,
        "automatic_repair_disabled": not certification.automatic_repair_enabled,
        "blocker_auto_resolution_disabled": not certification.blocker_auto_resolution_enabled,
        "warning_suppression_disabled": not certification.warning_suppression_enabled,
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_boundary_blocker_resolution(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_blocker_resolution_ordering_stability(certification),
        "serialization_hashing": validate_blocker_resolution_serialization_and_hashing(
            certification
        ),
        "visibility": validate_blocker_resolution_visibility(certification),
        "replay_rollback": validate_blocker_resolution_replay_rollback_evidence(
            certification
        ),
        "provenance_lineage": validate_blocker_resolution_provenance_lineage(
            certification
        ),
        "non_operational": validate_boundary_blocker_resolution_non_operational(
            certification
        ),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_4_boundary_blocker_resolution_report() -> dict[str, Any]:
    certification = build_v4_4_boundary_blocker_resolution()
    exported = export_boundary_blocker_resolution_closeout_preparation(certification)
    validation = validate_boundary_blocker_resolution(certification)
    visibility = validation["validations"]["visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    replay_rollback = validation["validations"]["replay_rollback"]
    provenance_lineage = validation["validations"]["provenance_lineage"]
    non_operational = validation["validations"]["non_operational"]
    blockers = visibility["blockers"]
    warnings = visibility["warnings"]
    prohibitions = visibility["prohibitions"]
    constraints = visibility["constraints"]
    limitations = visibility["limitations"]
    escalations = visibility["escalations"]
    closeout = visibility["closeout"]
    fail_visible = visibility["fail_visible"]
    deterministic_hash_evidence = {
        "blocker_identity_hash": hash_blocker_classification_identity(
            certification.blocker_identity
        ),
        "warning_identity_hash": hash_warning_classification_identity(
            certification.warning_identity
        ),
        "closeout_identity_hash": hash_closeout_eligibility_identity(
            certification.closeout_identity
        ),
        "planning_boundary_identity_hash": hash_v4_5_inherited_planning_boundary_identity(
            certification.planning_boundary_identity
        ),
        "certification_hash": hash_boundary_blocker_resolution_closeout_preparation(
            certification
        ),
        "provenance_hash": hash_blocker_resolution_provenance(
            certification.provenance_record
        ),
        "lineage_hash": hash_blocker_resolution_lineage(certification.lineage_record),
        "replay_rollback_hash": hash_blocker_resolution_replay_rollback(
            certification.replay_rollback_record
        ),
        "phase8_evidence_hashes": {
            record.evidence_id: hash_phase8_readiness_evidence_reference(record)
            for record in sorted(
                certification.phase8_evidence_references,
                key=lambda item: item.deterministic_order,
            )
        },
        "blocker_hashes": {
            record.blocker_id: hash_blocker_classification_record(record)
            for record in sorted(
                certification.blocker_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "warning_hashes": {
            record.warning_id: hash_warning_classification_record(record)
            for record in sorted(
                certification.warning_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "prohibition_hashes": {
            record.prohibition_id: hash_inherited_prohibition_record(record)
            for record in sorted(
                certification.inherited_prohibition_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "constraint_hashes": {
            record.constraint_id: hash_inherited_constraint_record(record)
            for record in sorted(
                certification.inherited_constraint_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "limitation_hashes": {
            record.limitation_id: hash_unresolved_limitation_record(record)
            for record in sorted(
                certification.limitation_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "escalation_hashes": {
            record.escalation_id: hash_escalation_record(record)
            for record in sorted(
                certification.escalation_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "closeout_hashes": {
            record.eligibility_id: hash_closeout_eligibility_record(record)
            for record in sorted(
                certification.closeout_eligibility_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "planning_boundary_hashes": {
            record.planning_boundary_id: hash_v4_5_inherited_planning_boundary_record(
                record
            )
            for record in sorted(
                certification.planning_boundary_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "explanation_hashes": {
            record.explanation_id: hash_fail_visible_explanation_record(record)
            for record in sorted(
                certification.fail_visible_explanations,
                key=lambda item: item.deterministic_order,
            )
        },
        "non_operational_hashes": {
            record.certification_id: hash_non_operational_blocker_certification(record)
            for record in sorted(
                certification.non_operational_certifications,
                key=lambda item: item.deterministic_order,
            )
        },
        "closeout_summary_hashes": {
            record.summary_id: hash_closeout_preparation_summary(record)
            for record in sorted(
                certification.closeout_summaries,
                key=lambda item: item.deterministic_order,
            )
        },
    }
    summary = {
        "blocker_classification_total": blockers["blocker_classification_total"],
        "warning_classification_total": warnings["warning_classification_total"],
        "resolved_count": blockers["resolved_count"],
        "intentionally_preserved_count": blockers["intentionally_preserved_count"]
        + warnings["intentionally_preserved_count"],
        "inherited_prohibition_count": prohibitions["inherited_prohibition_total"],
        "inherited_constraint_count": constraints["inherited_constraint_total"],
        "escalation_total": escalations["escalation_total"],
        "closeout_eligibility_total": closeout["closeout_eligibility_total"],
        "closeout_ready_count": closeout["closeout_ready_count"],
        "closeout_ready_with_limitations_count": closeout[
            "closeout_ready_with_limitations_count"
        ],
        "closeout_blocked_count": closeout["closeout_blocked_count"],
        "unresolved_limitation_total": limitations["unresolved_limitation_total"],
        "fail_visible_blocker_total": blockers["fail_visible_blocker_count"],
        "fail_visible_explanation_total": fail_visible["fail_visible_explanation_total"],
        "combined_state_counts": visibility["combined_counts"],
        "blocker_severity_totals": blockers["blocker_severity_counts"],
        "warning_severity_totals": warnings["warning_severity_counts"],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "blocker_serialization_verified": (
            serialization_hashing["blocker_serialization_stable"]
        ),
        "warning_serialization_verified": (
            serialization_hashing["warning_serialization_stable"]
        ),
        "escalation_hashing_verified": serialization_hashing["escalation_hashing_stable"],
        "closeout_hashing_verified": serialization_hashing["closeout_hashing_stable"],
        "fail_visible_blocker_preserved": blockers["fail_visible_blocker_count"] > 0,
        "inherited_prohibition_preserved": prohibitions["inherited_prohibition_total"] > 0,
        "inherited_constraint_preserved": constraints["inherited_constraint_total"] > 0,
        "unresolved_limitation_visibility_preserved": (
            limitations["unresolved_limitation_total"] > 0
        ),
        "escalation_trace_visibility_preserved": escalations["escalation_total"] > 0,
        "replay_safe_evidence_verified": replay_rollback["replay_safe"],
        "rollback_safe_evidence_verified": replay_rollback["rollback_safe"],
        "provenance_continuity_verified": (
            provenance_lineage["provenance_continuity_preserved"]
        ),
        "lineage_continuity_verified": provenance_lineage["lineage_continuity_preserved"],
        "governance_safe_certification_verified": validation["valid"],
        "non_operational_certification_verified": non_operational["valid"],
        "authorization_behavior_enabled": False,
        "approval_behavior_enabled": False,
        "activation_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "decision_behavior_enabled": False,
        "runtime_readiness_inferred": False,
        "validation_error_count": validation["validation_error_count"],
        "remaining_unclassified_warning_count": 0,
        "remaining_unclassified_blocker_count": 0,
        "remaining_fail_visible_warning_count": warnings["fail_visible_warning_count"],
        "remaining_fail_visible_blocker_count": blockers["fail_visible_blocker_count"],
        **non_operational["counters"],
        "planner_integration_enabled": certification.planner_integration_enabled,
        "production_consumption_enabled": certification.production_consumption_enabled,
        "runtime_mutation_enabled": certification.runtime_mutation_enabled,
        "operational_mutation_enabled": certification.operational_mutation_enabled,
    }
    for counter_name in V4_4_BOUNDARY_BLOCKER_RESOLUTION_DISABLED_COUNTER_NAMES:
        summary.setdefault(counter_name, 0)
    report: dict[str, Any] = {
        "report_schema_version": V4_4_BOUNDARY_BLOCKER_RESOLUTION_REPORT_SCHEMA_VERSION,
        "phase_id": certification.blocker_identity.phase_id,
        "foundation_status": (
            V4_4_BOUNDARY_BLOCKER_RESOLUTION_STATUS_STABLE
            if validation["valid"]
            else V4_4_BOUNDARY_BLOCKER_RESOLUTION_STATUS_BLOCKED
        ),
        "summary": summary,
        "boundary_blocker_resolution_closeout_preparation": exported,
        "blocker_resolution_visibility": blockers,
        "warning_classification_visibility": warnings,
        "inherited_prohibition_visibility": prohibitions,
        "inherited_constraint_visibility": constraints,
        "unresolved_limitation_visibility": limitations,
        "escalation_visibility": escalations,
        "closeout_eligibility_visibility": closeout,
        "v4_5_planning_boundary_visibility": visibility["planning_boundary"],
        "fail_visible_blocker_explainability": fail_visible,
        "closeout_summary_visibility": visibility["closeout_summary"],
        "provenance_continuity_evidence": provenance_continuity_visibility(certification),
        "lineage_continuity_evidence": lineage_continuity_visibility(certification),
        "governance_safe_closeout_explainability": visibility["explainability"],
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": {
            "blocker_serialization_stable": (
                serialization_hashing["blocker_serialization_stable"]
            ),
            "warning_serialization_stable": (
                serialization_hashing["warning_serialization_stable"]
            ),
            "escalation_hashing_stable": serialization_hashing["escalation_hashing_stable"],
            "closeout_hashing_stable": serialization_hashing["closeout_hashing_stable"],
            "serialization_length": serialization_hashing["serialization_length"],
            "certification_hash": serialization_hashing["certification_hash"],
        },
        "replay_safe_evidence": replay_rollback,
        "rollback_safe_evidence": replay_rollback,
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "classified_warnings": [
            export_warning_classification_record(record)
            for record in certification.warning_records
        ],
        "classified_blockers": [
            export_blocker_classification_record(record)
            for record in certification.blocker_records
        ],
    }
    report["deterministic_report_hash"] = deterministic_boundary_blocker_resolution_hash(
        report
    )
    return report


def contaminate_boundary_blocker_resolution_for_non_operational_validation(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> BoundaryBlockerResolutionCloseoutPreparation:
    contaminated_blocker = replace(
        certification.blocker_records[0],
        blocker_authorization_enabled=True,
        approval_enabled=True,
        activation_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
        automatic_remediation_enabled=True,
        blocker_auto_resolution_enabled=True,
    )
    contaminated_warning = replace(
        certification.warning_records[0],
        warning_suppression_enabled=True,
        approval_enabled=True,
        activation_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
    )
    contaminated_escalation = replace(
        certification.escalation_records[0],
        closeout_activation_enabled=True,
        automatic_remediation_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
    )
    return replace(
        certification,
        blocker_records=(contaminated_blocker,) + certification.blocker_records[1:],
        warning_records=(contaminated_warning,) + certification.warning_records[1:],
        escalation_records=(contaminated_escalation,) + certification.escalation_records[1:],
        runtime_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        orchestration_activation_enabled=True,
        dispatch_execution_enabled=True,
        routing_execution_enabled=True,
        scheduling_execution_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
        blocker_authorization_enabled=True,
        closeout_activation_enabled=True,
        operational_mutation_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        runtime_mutation_enabled=True,
        automatic_remediation_enabled=True,
        automatic_repair_enabled=True,
        blocker_auto_resolution_enabled=True,
        warning_suppression_enabled=True,
    )
