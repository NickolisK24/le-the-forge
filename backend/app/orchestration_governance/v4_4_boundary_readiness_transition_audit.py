"""Audit for deterministic v4.4 boundary readiness and v4.5 transition."""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_boundary_readiness_transition_hashing import (
    deterministic_boundary_readiness_transition_hash,
    hash_blocker_warning_visibility,
    hash_boundary_readiness_transition_certification,
    hash_completeness_summary,
    hash_limitation_visibility,
    hash_non_operational_certification,
    hash_phase_chain_completeness_identity,
    hash_phase_evidence_reference,
    hash_readiness_certification_identity,
    hash_readiness_certification_record,
    hash_readiness_lineage_continuity,
    hash_readiness_provenance_continuity,
    hash_readiness_replay_rollback_evidence,
    hash_transition_certification_identity,
    hash_transition_certification_record,
    hash_transition_summary,
    hash_unresolved_diagnostic_visibility,
    hash_v4_5_drift_integrity_preparation,
    hash_v4_5_planning_constraint,
)
from .v4_4_boundary_readiness_transition_models import (
    READINESS_STATE_NOT_READY,
    READINESS_STATE_READY_FOR_CLOSEOUT,
    READINESS_STATE_READY_WITH_WARNINGS,
    READINESS_STATE_TRANSITION_BLOCKED,
    READINESS_STATE_TRANSITION_READY,
    READINESS_STATE_TRANSITION_READY_WITH_WARNINGS,
    V4_4_BOUNDARY_READINESS_TRANSITION_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_READINESS_TRANSITION_REPORT_SCHEMA_VERSION,
    V4_4_BOUNDARY_READINESS_TRANSITION_STATUS_BLOCKED,
    V4_4_BOUNDARY_READINESS_TRANSITION_STATUS_STABLE,
    BoundaryReadinessTransitionCertification,
    default_boundary_readiness_transition_certification,
)
from .v4_4_boundary_readiness_transition_serialization import (
    export_blocker_warning_visibility,
    export_boundary_readiness_transition_certification,
    serialize_boundary_readiness_transition_certification,
)
from .v4_4_boundary_readiness_transition_visibility import (
    blocker_warning_summaries,
    count_combined_readiness_transition_states,
    drift_integrity_preparation_summaries,
    governance_safe_readiness_explainability,
    inherited_constraint_summaries,
    inherited_prohibition_summaries,
    limitation_summaries,
    lineage_continuity_visibility,
    phase_chain_completeness_summaries,
    provenance_continuity_visibility,
    unresolved_diagnostic_summaries,
    v4_4_readiness_summaries,
    v4_5_transition_summaries,
    validate_required_readiness_transition_visibility,
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
    "enabled_readiness_authorization_count": (
        "readiness_authorization_enabled",
        "readiness_authorization_signal_enabled",
    ),
    "enabled_transition_approval_count": (
        "transition_approval_enabled",
        "transition_approval_signal_enabled",
    ),
    "enabled_v4_5_activation_count": (
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


def build_v4_4_boundary_readiness_transition() -> BoundaryReadinessTransitionCertification:
    return default_boundary_readiness_transition_certification()


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


def enabled_boundary_readiness_transition_capability_flags(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(certification):
        item_id = (
            getattr(item, "readiness_certification_id", None)
            or getattr(item, "transition_certification_id", None)
            or getattr(item, "phase_chain_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "readiness_id", None)
            or getattr(item, "transition_id", None)
            or getattr(item, "completeness_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "limitation_id", None)
            or getattr(item, "finding_id", None)
            or getattr(item, "constraint_id", None)
            or getattr(item, "preparation_id", None)
            or getattr(item, "certification_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "summary_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def boundary_readiness_transition_capability_counter_values(
    certification: BoundaryReadinessTransitionCertification,
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


def boundary_readiness_transition_equal(
    left: BoundaryReadinessTransitionCertification,
    right: BoundaryReadinessTransitionCertification,
) -> bool:
    return serialize_boundary_readiness_transition_certification(
        left
    ) == serialize_boundary_readiness_transition_certification(right)


def validate_readiness_transition_ordering_stability(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    order_groups = {
        "phase_evidence_references": tuple(
            item.deterministic_order for item in certification.phase_evidence_references
        ),
        "readiness_records": tuple(item.deterministic_order for item in certification.readiness_records),
        "transition_records": tuple(
            item.deterministic_order for item in certification.transition_records
        ),
        "completeness_records": tuple(
            item.deterministic_order for item in certification.completeness_records
        ),
        "diagnostic_records": tuple(
            item.deterministic_order for item in certification.diagnostic_records
        ),
        "limitation_records": tuple(
            item.deterministic_order for item in certification.limitation_records
        ),
        "blocker_warning_records": tuple(
            item.deterministic_order for item in certification.blocker_warning_records
        ),
        "planning_constraint_records": tuple(
            item.deterministic_order for item in certification.planning_constraint_records
        ),
        "drift_integrity_preparation_records": tuple(
            item.deterministic_order
            for item in certification.drift_integrity_preparation_records
        ),
        "non_operational_certifications": tuple(
            item.deterministic_order for item in certification.non_operational_certifications
        ),
        "transition_summaries": tuple(
            item.deterministic_order for item in certification.transition_summaries
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


def validate_readiness_transition_serialization_and_hashing(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    rebuilt = build_v4_4_boundary_readiness_transition()
    serialized = serialize_boundary_readiness_transition_certification(certification)
    rebuilt_serialized = serialize_boundary_readiness_transition_certification(rebuilt)
    certification_hash = hash_boundary_readiness_transition_certification(certification)
    rebuilt_hash = hash_boundary_readiness_transition_certification(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and certification_hash == rebuilt_hash,
        "readiness_serialization_stable": serialized == rebuilt_serialized,
        "transition_serialization_stable": serialized == rebuilt_serialized,
        "readiness_hashing_stable": certification_hash == rebuilt_hash,
        "transition_hashing_stable": certification_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "certification_hash": certification_hash,
        "rebuilt_certification_hash": rebuilt_hash,
    }


def validate_readiness_transition_visibility(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    required = validate_required_readiness_transition_visibility(certification)
    readiness = v4_4_readiness_summaries(certification)
    transition = v4_5_transition_summaries(certification)
    completeness = phase_chain_completeness_summaries(certification)
    diagnostics = unresolved_diagnostic_summaries(certification)
    limitations = limitation_summaries(certification)
    blocker_warning = blocker_warning_summaries(certification)
    constraints = inherited_constraint_summaries(certification)
    preparation = drift_integrity_preparation_summaries(certification)
    explainability = governance_safe_readiness_explainability(certification)
    return {
        "valid": (
            required["valid"]
            and completeness["phase_evidence_reference_count"] == 7
            and completeness["phase_production_consumption_enabled_count"] == 0
            and completeness["runtime_activation_enabled_count"] == 0
            and readiness["runtime_readiness_inferred_count"] == 0
            and readiness["readiness_authorization_enabled_count"] == 0
            and readiness["recommendation_enabled_count"] == 0
            and readiness["decision_enabled_count"] == 0
            and transition["transition_approval_enabled_count"] == 0
            and transition["v4_5_activation_enabled_count"] == 0
            and transition["production_consumption_enabled_count"] == 0
            and transition["planner_integration_enabled_count"] == 0
            and diagnostics["unresolved_diagnostic_count"] > 0
            and diagnostics["automatic_remediation_enabled_count"] == 0
            and diagnostics["automatic_repair_enabled_count"] == 0
            and diagnostics["recommendation_enabled_count"] == 0
            and diagnostics["decision_enabled_count"] == 0
            and limitations["automatic_remediation_enabled_count"] == 0
            and blocker_warning["approval_enabled_count"] == 0
            and blocker_warning["activation_enabled_count"] == 0
            and blocker_warning["recommendation_enabled_count"] == 0
            and blocker_warning["decision_enabled_count"] == 0
            and constraints["planner_integration_enabled_count"] == 0
            and constraints["production_consumption_enabled_count"] == 0
            and constraints["v4_5_activation_enabled_count"] == 0
            and preparation["runtime_activation_enabled_count"] == 0
            and preparation["recommendation_enabled_count"] == 0
            and preparation["decision_enabled_count"] == 0
            and explainability["descriptive_only"]
            and explainability["non_operational"]
            and explainability["runtime_readiness_inference_disabled"]
        ),
        "combined_counts": count_combined_readiness_transition_states(certification),
        "missing_states": required["missing_states"],
        "missing_fail_visible_states": required["missing_fail_visible_states"],
        "readiness": readiness,
        "transition": transition,
        "completeness": completeness,
        "diagnostics": diagnostics,
        "limitations": limitations,
        "blocker_warning": blocker_warning,
        "constraints": constraints,
        "preparation": preparation,
        "explainability": explainability,
    }


def validate_readiness_transition_replay_rollback_evidence(
    certification: BoundaryReadinessTransitionCertification,
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


def validate_readiness_transition_provenance_lineage(
    certification: BoundaryReadinessTransitionCertification,
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


def validate_boundary_readiness_transition_non_operational(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    counters = boundary_readiness_transition_capability_counter_values(certification)
    enabled_flags = enabled_boundary_readiness_transition_capability_flags(certification)
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
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_boundary_readiness_transition(
    certification: BoundaryReadinessTransitionCertification,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_readiness_transition_ordering_stability(certification),
        "serialization_hashing": validate_readiness_transition_serialization_and_hashing(
            certification
        ),
        "visibility": validate_readiness_transition_visibility(certification),
        "replay_rollback": validate_readiness_transition_replay_rollback_evidence(
            certification
        ),
        "provenance_lineage": validate_readiness_transition_provenance_lineage(
            certification
        ),
        "non_operational": validate_boundary_readiness_transition_non_operational(
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


def build_v4_4_boundary_readiness_transition_report() -> dict[str, Any]:
    certification = build_v4_4_boundary_readiness_transition()
    exported = export_boundary_readiness_transition_certification(certification)
    validation = validate_boundary_readiness_transition(certification)
    visibility = validation["validations"]["visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    replay_rollback = validation["validations"]["replay_rollback"]
    provenance_lineage = validation["validations"]["provenance_lineage"]
    non_operational = validation["validations"]["non_operational"]
    readiness = visibility["readiness"]
    transition = visibility["transition"]
    completeness = visibility["completeness"]
    diagnostics = visibility["diagnostics"]
    limitations = visibility["limitations"]
    blocker_warning = visibility["blocker_warning"]
    constraints = visibility["constraints"]
    deterministic_hash_evidence = {
        "readiness_identity_hash": hash_readiness_certification_identity(
            certification.readiness_identity
        ),
        "transition_identity_hash": hash_transition_certification_identity(
            certification.transition_identity
        ),
        "completeness_identity_hash": hash_phase_chain_completeness_identity(
            certification.completeness_identity
        ),
        "certification_hash": hash_boundary_readiness_transition_certification(
            certification
        ),
        "provenance_hash": hash_readiness_provenance_continuity(
            certification.provenance_record
        ),
        "lineage_hash": hash_readiness_lineage_continuity(certification.lineage_record),
        "replay_rollback_hash": hash_readiness_replay_rollback_evidence(
            certification.replay_rollback_record
        ),
        "phase_evidence_hashes": {
            record.evidence_id: hash_phase_evidence_reference(record)
            for record in sorted(
                certification.phase_evidence_references,
                key=lambda item: item.deterministic_order,
            )
        },
        "readiness_hashes": {
            record.readiness_id: hash_readiness_certification_record(record)
            for record in sorted(
                certification.readiness_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "transition_hashes": {
            record.transition_id: hash_transition_certification_record(record)
            for record in sorted(
                certification.transition_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "completeness_hashes": {
            record.completeness_id: hash_completeness_summary(record)
            for record in sorted(
                certification.completeness_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_unresolved_diagnostic_visibility(record)
            for record in sorted(
                certification.diagnostic_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "limitation_hashes": {
            record.limitation_id: hash_limitation_visibility(record)
            for record in sorted(
                certification.limitation_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "blocker_warning_hashes": {
            record.finding_id: hash_blocker_warning_visibility(record)
            for record in sorted(
                certification.blocker_warning_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "constraint_hashes": {
            record.constraint_id: hash_v4_5_planning_constraint(record)
            for record in sorted(
                certification.planning_constraint_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "preparation_hashes": {
            record.preparation_id: hash_v4_5_drift_integrity_preparation(record)
            for record in sorted(
                certification.drift_integrity_preparation_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "non_operational_hashes": {
            record.certification_id: hash_non_operational_certification(record)
            for record in sorted(
                certification.non_operational_certifications,
                key=lambda item: item.deterministic_order,
            )
        },
        "transition_summary_hashes": {
            record.summary_id: hash_transition_summary(record)
            for record in sorted(
                certification.transition_summaries,
                key=lambda item: item.deterministic_order,
            )
        },
    }
    summary = {
        "v4_4_readiness_certification_count": readiness["v4_4_readiness_certification_count"],
        "v4_5_transition_certification_count": transition["v4_5_transition_certification_count"],
        "phase_evidence_reference_count": completeness["phase_evidence_reference_count"],
        "phase_chain_completeness_count": completeness["phase_chain_completeness_count"],
        "ready_for_closeout_count": readiness["ready_for_closeout_count"],
        "ready_with_warnings_count": readiness["ready_with_warnings_count"],
        "not_ready_count": readiness["not_ready_count"],
        "transition_ready_count": transition["transition_ready_count"],
        "transition_warning_count": transition["transition_ready_with_warnings_count"],
        "transition_ready_with_warnings_count": transition["transition_ready_with_warnings_count"],
        "transition_blocked_count": transition["transition_blocked_count"],
        "unresolved_diagnostic_count": diagnostics["unresolved_diagnostic_count"],
        "limitation_count": limitations["limitation_count"],
        "inherited_limitation_count": limitations["inherited_limitation_count"],
        "blocker_count": blocker_warning["blocker_count"],
        "warning_count": blocker_warning["warning_count"],
        "inherited_v4_5_constraint_count": constraints["inherited_v4_5_constraint_count"],
        "inherited_v4_5_prohibition_count": constraints["inherited_v4_5_prohibition_count"],
        "combined_state_counts": visibility["combined_counts"],
        "diagnostic_severity_totals": diagnostics["severity_counts"],
        "finding_severity_totals": blocker_warning["severity_counts"],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "readiness_serialization_verified": (
            serialization_hashing["readiness_serialization_stable"]
        ),
        "transition_serialization_verified": (
            serialization_hashing["transition_serialization_stable"]
        ),
        "readiness_hashing_verified": serialization_hashing["readiness_hashing_stable"],
        "transition_hashing_verified": serialization_hashing["transition_hashing_stable"],
        "phase_evidence_reference_stability_verified": (
            completeness["phase_evidence_reference_count"] == 7
        ),
        "phase_chain_completeness_visibility_preserved": (
            completeness["phase_chain_completeness_count"] >= 8
        ),
        "unresolved_diagnostic_visibility_preserved": (
            diagnostics["unresolved_diagnostic_count"] > 0
        ),
        "limitation_visibility_preserved": limitations["limitation_count"] > 0,
        "blocker_warning_visibility_preserved": blocker_warning["finding_count"] > 0,
        "v4_5_inherited_constraint_visibility_preserved": (
            constraints["inherited_v4_5_constraint_count"] > 0
        ),
        "v4_5_inherited_prohibition_visibility_preserved": (
            constraints["inherited_v4_5_prohibition_count"] > 0
        ),
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
        "remaining_warning_count": blocker_warning["warning_count"],
        "remaining_blocker_count": blocker_warning["blocker_count"],
        **non_operational["counters"],
        "planner_integration_enabled": certification.planner_integration_enabled,
        "production_consumption_enabled": certification.production_consumption_enabled,
        "runtime_mutation_enabled": certification.runtime_mutation_enabled,
        "operational_mutation_enabled": certification.operational_mutation_enabled,
    }
    report: dict[str, Any] = {
        "report_schema_version": V4_4_BOUNDARY_READINESS_TRANSITION_REPORT_SCHEMA_VERSION,
        "phase_id": certification.readiness_identity.phase_id,
        "foundation_status": (
            V4_4_BOUNDARY_READINESS_TRANSITION_STATUS_STABLE
            if validation["valid"]
            else V4_4_BOUNDARY_READINESS_TRANSITION_STATUS_BLOCKED
        ),
        "summary": summary,
        "boundary_readiness_transition_certification": exported,
        "v4_4_readiness_visibility": readiness,
        "v4_5_transition_visibility": transition,
        "phase_chain_completeness_visibility": completeness,
        "unresolved_diagnostic_visibility": diagnostics,
        "limitation_visibility": limitations,
        "blocker_warning_visibility": blocker_warning,
        "v4_5_inherited_constraint_visibility": constraints,
        "v4_5_inherited_prohibition_visibility": inherited_prohibition_summaries(
            certification
        ),
        "v4_5_drift_integrity_preparation_visibility": visibility["preparation"],
        "provenance_continuity_evidence": provenance_continuity_visibility(certification),
        "lineage_continuity_evidence": lineage_continuity_visibility(certification),
        "governance_safe_readiness_explainability": visibility["explainability"],
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": {
            "readiness_serialization_stable": (
                serialization_hashing["readiness_serialization_stable"]
            ),
            "transition_serialization_stable": (
                serialization_hashing["transition_serialization_stable"]
            ),
            "readiness_hashing_stable": serialization_hashing["readiness_hashing_stable"],
            "transition_hashing_stable": serialization_hashing["transition_hashing_stable"],
            "serialization_length": serialization_hashing["serialization_length"],
            "certification_hash": serialization_hashing["certification_hash"],
        },
        "replay_safe_evidence": replay_rollback,
        "rollback_safe_evidence": replay_rollback,
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "remaining_warnings": [
            export_blocker_warning_visibility(record)
            for record in certification.blocker_warning_records
            if record.severity == "warning"
        ],
        "remaining_blockers": [
            export_blocker_warning_visibility(record)
            for record in certification.blocker_warning_records
            if record.severity == "blocker"
        ],
    }
    report["deterministic_report_hash"] = deterministic_boundary_readiness_transition_hash(
        report
    )
    return report


def contaminate_boundary_readiness_transition_for_non_operational_validation(
    certification: BoundaryReadinessTransitionCertification,
) -> BoundaryReadinessTransitionCertification:
    contaminated_readiness = replace(
        certification.readiness_records[0],
        runtime_readiness_inferred=True,
        readiness_authorization_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
    )
    contaminated_transition = replace(
        certification.transition_records[0],
        transition_approval_enabled=True,
        v4_5_activation_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    contaminated_finding = replace(
        certification.blocker_warning_records[0],
        approval_enabled=True,
        activation_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
    )
    return replace(
        certification,
        readiness_records=(contaminated_readiness,) + certification.readiness_records[1:],
        transition_records=(contaminated_transition,) + certification.transition_records[1:],
        blocker_warning_records=(contaminated_finding,)
        + certification.blocker_warning_records[1:],
        runtime_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        orchestration_activation_enabled=True,
        dispatch_execution_enabled=True,
        routing_execution_enabled=True,
        scheduling_execution_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
        readiness_authorization_enabled=True,
        transition_approval_enabled=True,
        v4_5_activation_enabled=True,
        operational_mutation_enabled=True,
    )
