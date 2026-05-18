"""Audit for deterministic v4.4 closeout and v4.5 readiness certification."""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_closeout_readiness_hashing import (
    deterministic_v4_4_closeout_readiness_hash,
    hash_closeout_certification_record,
    hash_closeout_identity,
    hash_closeout_readiness_lineage,
    hash_closeout_readiness_provenance,
    hash_closeout_readiness_replay_rollback,
    hash_closeout_readiness_summary,
    hash_inherited_constraint_record,
    hash_inherited_prohibition_record,
    hash_non_operational_closeout_certification,
    hash_phase_chain_evidence_identity,
    hash_phase_chain_evidence_record,
    hash_preserved_blocker_record,
    hash_preserved_limitation_record,
    hash_preserved_warning_record,
    hash_readiness_identity,
    hash_v4_4_closeout_readiness_certification,
    hash_v4_5_inherited_limitation,
    hash_v4_5_planning_boundary,
    hash_v4_5_readiness_certification_record,
)
from .v4_4_closeout_readiness_models import (
    V4_4_CLOSEOUT_READINESS_DISABLED_COUNTER_NAMES,
    V4_4_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
    V4_4_CLOSEOUT_READINESS_STATUS_BLOCKED,
    V4_4_CLOSEOUT_READINESS_STATUS_STABLE,
    V44CloseoutAndV45ReadinessCertification,
    default_v4_4_closeout_readiness_certification,
)
from .v4_4_closeout_readiness_serialization import (
    export_closeout_certification_record,
    export_preserved_blocker_record,
    export_preserved_limitation_record,
    export_preserved_warning_record,
    export_v4_4_closeout_readiness_certification,
    serialize_v4_4_closeout_readiness_certification,
)
from .v4_4_closeout_readiness_visibility import (
    closeout_readiness_summary_visibility,
    count_combined_closeout_readiness_states,
    governance_safe_closeout_explainability,
    inherited_constraint_summaries,
    inherited_prohibition_summaries,
    lineage_continuity_visibility,
    non_operational_certification_summaries,
    phase_chain_evidence_summaries,
    preserved_blocker_summaries,
    preserved_limitation_summaries,
    preserved_warning_summaries,
    provenance_continuity_visibility,
    v4_4_closeout_summaries,
    v4_5_inherited_limitation_summaries,
    v4_5_planning_boundary_summaries,
    v4_5_readiness_summaries,
    validate_required_closeout_readiness_visibility,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_runtime_behavior_enabled",
        "orchestration_execution_enabled",
        "execution_enabled",
        "runtime_activation_enabled",
        "runtime_readiness_inferred",
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
    "enabled_closeout_authorization_count": (
        "closeout_authorization_enabled",
        "closeout_authorization_signal_enabled",
    ),
    "enabled_readiness_activation_count": (
        "readiness_activation_enabled",
        "readiness_activation_signal_enabled",
    ),
    "enabled_v4_5_runtime_behavior_count": (
        "v4_5_runtime_behavior_enabled",
        "v4_5_runtime_enabled",
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


def build_v4_4_closeout_readiness() -> V44CloseoutAndV45ReadinessCertification:
    return default_v4_4_closeout_readiness_certification()


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


def enabled_closeout_readiness_capability_flags(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(certification):
        item_id = (
            getattr(item, "closeout_certification_id", None)
            or getattr(item, "readiness_certification_id", None)
            or getattr(item, "phase_chain_evidence_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "closeout_id", None)
            or getattr(item, "readiness_id", None)
            or getattr(item, "limitation_id", None)
            or getattr(item, "blocker_id", None)
            or getattr(item, "warning_id", None)
            or getattr(item, "prohibition_id", None)
            or getattr(item, "constraint_id", None)
            or getattr(item, "planning_boundary_id", None)
            or getattr(item, "inherited_limitation_id", None)
            or getattr(item, "certification_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "summary_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def closeout_readiness_capability_counter_values(
    certification: V44CloseoutAndV45ReadinessCertification,
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


def closeout_readiness_equal(
    left: V44CloseoutAndV45ReadinessCertification,
    right: V44CloseoutAndV45ReadinessCertification,
) -> bool:
    return serialize_v4_4_closeout_readiness_certification(
        left
    ) == serialize_v4_4_closeout_readiness_certification(right)


def validate_closeout_readiness_ordering_stability(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    order_groups = {
        "phase_chain_evidence_records": tuple(
            item.deterministic_order for item in certification.phase_chain_evidence_records
        ),
        "closeout_records": tuple(item.deterministic_order for item in certification.closeout_records),
        "readiness_records": tuple(item.deterministic_order for item in certification.readiness_records),
        "preserved_limitation_records": tuple(
            item.deterministic_order for item in certification.preserved_limitation_records
        ),
        "preserved_blocker_records": tuple(
            item.deterministic_order for item in certification.preserved_blocker_records
        ),
        "preserved_warning_records": tuple(
            item.deterministic_order for item in certification.preserved_warning_records
        ),
        "inherited_prohibition_records": tuple(
            item.deterministic_order for item in certification.inherited_prohibition_records
        ),
        "inherited_constraint_records": tuple(
            item.deterministic_order for item in certification.inherited_constraint_records
        ),
        "planning_boundary_records": tuple(
            item.deterministic_order for item in certification.planning_boundary_records
        ),
        "inherited_limitation_records": tuple(
            item.deterministic_order for item in certification.inherited_limitation_records
        ),
        "non_operational_certifications": tuple(
            item.deterministic_order for item in certification.non_operational_certifications
        ),
        "closeout_readiness_summaries": tuple(
            item.deterministic_order for item in certification.closeout_readiness_summaries
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


def validate_closeout_readiness_serialization_and_hashing(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    rebuilt = build_v4_4_closeout_readiness()
    serialized = serialize_v4_4_closeout_readiness_certification(certification)
    rebuilt_serialized = serialize_v4_4_closeout_readiness_certification(rebuilt)
    certification_hash = hash_v4_4_closeout_readiness_certification(certification)
    rebuilt_hash = hash_v4_4_closeout_readiness_certification(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and certification_hash == rebuilt_hash,
        "closeout_serialization_stable": serialized == rebuilt_serialized,
        "readiness_serialization_stable": serialized == rebuilt_serialized,
        "closeout_hashing_stable": certification_hash == rebuilt_hash,
        "readiness_hashing_stable": certification_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "certification_hash": certification_hash,
        "rebuilt_certification_hash": rebuilt_hash,
    }


def validate_closeout_readiness_visibility(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    required = validate_required_closeout_readiness_visibility(certification)
    phase_chain = phase_chain_evidence_summaries(certification)
    closeout = v4_4_closeout_summaries(certification)
    readiness = v4_5_readiness_summaries(certification)
    limitations = preserved_limitation_summaries(certification)
    blockers = preserved_blocker_summaries(certification)
    warnings = preserved_warning_summaries(certification)
    prohibitions = inherited_prohibition_summaries(certification)
    constraints = inherited_constraint_summaries(certification)
    planning_boundary = v4_5_planning_boundary_summaries(certification)
    inherited_limitations = v4_5_inherited_limitation_summaries(certification)
    non_operational = non_operational_certification_summaries(certification)
    summary = closeout_readiness_summary_visibility(certification)
    explainability = governance_safe_closeout_explainability(certification)
    return {
        "valid": (
            required["valid"]
            and phase_chain["phase_chain_evidence_reference_count"] == 9
            and phase_chain["phase_evidence_coverage_count"] == 9
            and phase_chain["generated_report_coverage_count"] == 9
            and phase_chain["migration_doc_coverage_count"] == 9
            and phase_chain["production_consumption_enabled_count"] == 0
            and closeout["closeout_authorization_enabled_count"] == 0
            and closeout["activation_enabled_count"] == 0
            and closeout["runtime_readiness_inferred_count"] == 0
            and readiness["readiness_activation_enabled_count"] == 0
            and readiness["v4_5_runtime_behavior_enabled_count"] == 0
            and readiness["planner_integration_enabled_count"] == 0
            and readiness["production_consumption_enabled_count"] == 0
            and readiness["recommendation_enabled_count"] == 0
            and readiness["decision_enabled_count"] == 0
            and readiness["runtime_readiness_inferred_count"] == 0
            and limitations["automatic_remediation_enabled_count"] == 0
            and limitations["automatic_repair_enabled_count"] == 0
            and blockers["blocker_authorization_enabled_count"] == 0
            and blockers["approval_enabled_count"] == 0
            and blockers["activation_enabled_count"] == 0
            and blockers["recommendation_enabled_count"] == 0
            and blockers["decision_enabled_count"] == 0
            and warnings["warning_suppression_enabled_count"] == 0
            and warnings["recommendation_enabled_count"] == 0
            and warnings["decision_enabled_count"] == 0
            and prohibitions["runtime_execution_enabled_count"] == 0
            and prohibitions["orchestration_authorization_enabled_count"] == 0
            and prohibitions["orchestration_approval_enabled_count"] == 0
            and prohibitions["orchestration_activation_enabled_count"] == 0
            and prohibitions["planner_integration_enabled_count"] == 0
            and prohibitions["production_consumption_enabled_count"] == 0
            and prohibitions["v4_5_runtime_behavior_enabled_count"] == 0
            and constraints["planner_integration_enabled_count"] == 0
            and constraints["production_consumption_enabled_count"] == 0
            and constraints["readiness_activation_enabled_count"] == 0
            and constraints["v4_5_runtime_behavior_enabled_count"] == 0
            and planning_boundary["readiness_activation_enabled_count"] == 0
            and planning_boundary["v4_5_runtime_behavior_enabled_count"] == 0
            and planning_boundary["planner_integration_enabled_count"] == 0
            and planning_boundary["production_consumption_enabled_count"] == 0
            and inherited_limitations["automatic_remediation_enabled_count"] == 0
            and inherited_limitations["readiness_activation_enabled_count"] == 0
            and non_operational["runtime_execution_enabled_count"] == 0
            and non_operational["orchestration_authorization_enabled_count"] == 0
            and non_operational["orchestration_approval_enabled_count"] == 0
            and non_operational["orchestration_activation_enabled_count"] == 0
            and non_operational["dispatch_execution_enabled_count"] == 0
            and non_operational["routing_execution_enabled_count"] == 0
            and non_operational["scheduling_execution_enabled_count"] == 0
            and non_operational["recommendation_enabled_count"] == 0
            and non_operational["decision_enabled_count"] == 0
            and non_operational["closeout_authorization_enabled_count"] == 0
            and non_operational["readiness_activation_enabled_count"] == 0
            and non_operational["v4_5_runtime_behavior_enabled_count"] == 0
            and non_operational["operational_mutation_enabled_count"] == 0
            and summary["closeout_authorization_signal_enabled_count"] == 0
            and summary["readiness_activation_signal_enabled_count"] == 0
            and summary["runtime_readiness_inferred_count"] == 0
            and explainability["descriptive_only"]
            and explainability["non_operational"]
            and explainability["runtime_readiness_inference_disabled"]
        ),
        "combined_counts": count_combined_closeout_readiness_states(certification),
        "missing_states": required["missing_states"],
        "missing_fail_visible_states": required["missing_fail_visible_states"],
        "phase_chain": phase_chain,
        "closeout": closeout,
        "readiness": readiness,
        "limitations": limitations,
        "blockers": blockers,
        "warnings": warnings,
        "prohibitions": prohibitions,
        "constraints": constraints,
        "planning_boundary": planning_boundary,
        "inherited_limitations": inherited_limitations,
        "non_operational_summary": non_operational,
        "closeout_readiness_summary": summary,
        "explainability": explainability,
    }


def validate_closeout_readiness_replay_rollback_evidence(
    certification: V44CloseoutAndV45ReadinessCertification,
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


def validate_closeout_readiness_provenance_lineage(
    certification: V44CloseoutAndV45ReadinessCertification,
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


def validate_closeout_readiness_non_operational(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    counters = closeout_readiness_capability_counter_values(certification)
    enabled_flags = enabled_closeout_readiness_capability_flags(certification)
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
        "v4_5_runtime_behavior_disabled": not certification.v4_5_runtime_behavior_enabled,
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_v4_4_closeout_readiness(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_closeout_readiness_ordering_stability(certification),
        "serialization_hashing": validate_closeout_readiness_serialization_and_hashing(
            certification
        ),
        "visibility": validate_closeout_readiness_visibility(certification),
        "replay_rollback": validate_closeout_readiness_replay_rollback_evidence(
            certification
        ),
        "provenance_lineage": validate_closeout_readiness_provenance_lineage(
            certification
        ),
        "non_operational": validate_closeout_readiness_non_operational(certification),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_4_closeout_readiness_report() -> dict[str, Any]:
    certification = build_v4_4_closeout_readiness()
    exported = export_v4_4_closeout_readiness_certification(certification)
    validation = validate_v4_4_closeout_readiness(certification)
    visibility = validation["validations"]["visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    replay_rollback = validation["validations"]["replay_rollback"]
    provenance_lineage = validation["validations"]["provenance_lineage"]
    non_operational = validation["validations"]["non_operational"]
    phase_chain = visibility["phase_chain"]
    closeout = visibility["closeout"]
    readiness = visibility["readiness"]
    limitations = visibility["limitations"]
    blockers = visibility["blockers"]
    warnings = visibility["warnings"]
    prohibitions = visibility["prohibitions"]
    constraints = visibility["constraints"]
    deterministic_hash_evidence = {
        "closeout_identity_hash": hash_closeout_identity(certification.closeout_identity),
        "readiness_identity_hash": hash_readiness_identity(certification.readiness_identity),
        "phase_chain_identity_hash": hash_phase_chain_evidence_identity(
            certification.phase_chain_identity
        ),
        "certification_hash": hash_v4_4_closeout_readiness_certification(certification),
        "provenance_hash": hash_closeout_readiness_provenance(
            certification.provenance_record
        ),
        "lineage_hash": hash_closeout_readiness_lineage(certification.lineage_record),
        "replay_rollback_hash": hash_closeout_readiness_replay_rollback(
            certification.replay_rollback_record
        ),
        "phase_chain_evidence_hashes": {
            record.evidence_id: hash_phase_chain_evidence_record(record)
            for record in sorted(
                certification.phase_chain_evidence_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "closeout_hashes": {
            record.closeout_id: hash_closeout_certification_record(record)
            for record in sorted(
                certification.closeout_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "readiness_hashes": {
            record.readiness_id: hash_v4_5_readiness_certification_record(record)
            for record in sorted(
                certification.readiness_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "limitation_hashes": {
            record.limitation_id: hash_preserved_limitation_record(record)
            for record in sorted(
                certification.preserved_limitation_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "blocker_hashes": {
            record.blocker_id: hash_preserved_blocker_record(record)
            for record in sorted(
                certification.preserved_blocker_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "warning_hashes": {
            record.warning_id: hash_preserved_warning_record(record)
            for record in sorted(
                certification.preserved_warning_records,
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
        "planning_boundary_hashes": {
            record.planning_boundary_id: hash_v4_5_planning_boundary(record)
            for record in sorted(
                certification.planning_boundary_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "inherited_limitation_hashes": {
            record.inherited_limitation_id: hash_v4_5_inherited_limitation(record)
            for record in sorted(
                certification.inherited_limitation_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "non_operational_hashes": {
            record.certification_id: hash_non_operational_closeout_certification(record)
            for record in sorted(
                certification.non_operational_certifications,
                key=lambda item: item.deterministic_order,
            )
        },
        "summary_hashes": {
            record.summary_id: hash_closeout_readiness_summary(record)
            for record in sorted(
                certification.closeout_readiness_summaries,
                key=lambda item: item.deterministic_order,
            )
        },
    }
    summary = {
        "v4_4_closeout_certification_count": closeout["v4_4_closeout_certification_count"],
        "v4_5_readiness_certification_count": readiness["v4_5_readiness_certification_count"],
        "phase_chain_evidence_reference_count": phase_chain[
            "phase_chain_evidence_reference_count"
        ],
        "phase_evidence_coverage_count": phase_chain["phase_evidence_coverage_count"],
        "generated_report_coverage_count": phase_chain["generated_report_coverage_count"],
        "migration_doc_coverage_count": phase_chain["migration_doc_coverage_count"],
        "preserved_limitation_count": limitations["preserved_limitation_count"],
        "preserved_blocker_count": blockers["preserved_blocker_count"],
        "preserved_warning_count": warnings["preserved_warning_count"],
        "inherited_prohibition_count": prohibitions["inherited_prohibition_count"],
        "inherited_constraint_count": constraints["inherited_constraint_count"],
        "closeout_classification": certification.closeout_classification,
        "v4_5_readiness_classification": certification.v4_5_readiness_classification,
        "combined_state_counts": visibility["combined_counts"],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "closeout_serialization_verified": (
            serialization_hashing["closeout_serialization_stable"]
        ),
        "readiness_serialization_verified": (
            serialization_hashing["readiness_serialization_stable"]
        ),
        "closeout_hashing_verified": serialization_hashing["closeout_hashing_stable"],
        "readiness_hashing_verified": serialization_hashing["readiness_hashing_stable"],
        "phase_chain_evidence_reference_stability_verified": (
            phase_chain["phase_chain_evidence_reference_count"] == 9
        ),
        "preserved_limitation_visibility_preserved": (
            limitations["preserved_limitation_count"] > 0
        ),
        "preserved_blocker_visibility_preserved": blockers["preserved_blocker_count"] > 0,
        "preserved_warning_visibility_preserved": warnings["preserved_warning_count"] > 0,
        "inherited_prohibition_preserved": prohibitions["inherited_prohibition_count"] > 0,
        "inherited_constraint_preserved": constraints["inherited_constraint_count"] > 0,
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
        "v4_5_runtime_behavior_enabled": False,
        "runtime_readiness_inferred": False,
        "validation_error_count": validation["validation_error_count"],
        "remaining_fail_visible_warning_count": warnings["fail_visible_warning_count"],
        "remaining_fail_visible_blocker_count": blockers["fail_visible_blocker_count"],
        "remaining_unclassified_warning_count": 0,
        "remaining_unclassified_blocker_count": 0,
        **non_operational["counters"],
        "planner_integration_enabled": certification.planner_integration_enabled,
        "production_consumption_enabled": certification.production_consumption_enabled,
        "runtime_mutation_enabled": certification.runtime_mutation_enabled,
        "operational_mutation_enabled": certification.operational_mutation_enabled,
    }
    for counter_name in V4_4_CLOSEOUT_READINESS_DISABLED_COUNTER_NAMES:
        summary.setdefault(counter_name, 0)
    report: dict[str, Any] = {
        "report_schema_version": V4_4_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
        "phase_id": certification.closeout_identity.phase_id,
        "foundation_status": (
            V4_4_CLOSEOUT_READINESS_STATUS_STABLE
            if validation["valid"]
            else V4_4_CLOSEOUT_READINESS_STATUS_BLOCKED
        ),
        "summary": summary,
        "v4_4_closeout_v4_5_readiness_certification": exported,
        "v4_4_closeout_visibility": closeout,
        "v4_5_readiness_visibility": readiness,
        "phase_chain_evidence_visibility": phase_chain,
        "preserved_limitation_visibility": limitations,
        "preserved_blocker_visibility": blockers,
        "preserved_warning_visibility": warnings,
        "inherited_prohibition_visibility": prohibitions,
        "inherited_constraint_visibility": constraints,
        "v4_5_planning_boundary_visibility": visibility["planning_boundary"],
        "v4_5_inherited_limitation_visibility": visibility["inherited_limitations"],
        "non_operational_certification_visibility": visibility["non_operational_summary"],
        "closeout_readiness_summary_visibility": visibility["closeout_readiness_summary"],
        "provenance_continuity_evidence": provenance_continuity_visibility(certification),
        "lineage_continuity_evidence": lineage_continuity_visibility(certification),
        "governance_safe_closeout_explainability": visibility["explainability"],
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": {
            "closeout_serialization_stable": (
                serialization_hashing["closeout_serialization_stable"]
            ),
            "readiness_serialization_stable": (
                serialization_hashing["readiness_serialization_stable"]
            ),
            "closeout_hashing_stable": serialization_hashing["closeout_hashing_stable"],
            "readiness_hashing_stable": serialization_hashing["readiness_hashing_stable"],
            "serialization_length": serialization_hashing["serialization_length"],
            "certification_hash": serialization_hashing["certification_hash"],
        },
        "replay_safe_evidence": replay_rollback,
        "rollback_safe_evidence": replay_rollback,
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "preserved_limitations": [
            export_preserved_limitation_record(record)
            for record in certification.preserved_limitation_records
        ],
        "preserved_blockers": [
            export_preserved_blocker_record(record)
            for record in certification.preserved_blocker_records
        ],
        "preserved_warnings": [
            export_preserved_warning_record(record)
            for record in certification.preserved_warning_records
        ],
        "closeout_certifications": [
            export_closeout_certification_record(record)
            for record in certification.closeout_records
        ],
    }
    report["deterministic_report_hash"] = deterministic_v4_4_closeout_readiness_hash(
        report
    )
    return report


def contaminate_v4_4_closeout_readiness_for_non_operational_validation(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> V44CloseoutAndV45ReadinessCertification:
    contaminated_closeout = replace(
        certification.closeout_records[0],
        closeout_authorization_enabled=True,
        activation_enabled=True,
        runtime_readiness_inferred=True,
    )
    contaminated_readiness = replace(
        certification.readiness_records[0],
        readiness_activation_enabled=True,
        v4_5_runtime_behavior_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
        runtime_readiness_inferred=True,
    )
    contaminated_blocker = replace(
        certification.preserved_blocker_records[0],
        blocker_authorization_enabled=True,
        approval_enabled=True,
        activation_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
    )
    return replace(
        certification,
        closeout_records=(contaminated_closeout,) + certification.closeout_records[1:],
        readiness_records=(contaminated_readiness,) + certification.readiness_records[1:],
        preserved_blocker_records=(contaminated_blocker,)
        + certification.preserved_blocker_records[1:],
        runtime_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        orchestration_activation_enabled=True,
        dispatch_execution_enabled=True,
        routing_execution_enabled=True,
        scheduling_execution_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
        closeout_authorization_enabled=True,
        readiness_activation_enabled=True,
        v4_5_runtime_behavior_enabled=True,
        operational_mutation_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        runtime_mutation_enabled=True,
        automatic_remediation_enabled=True,
        automatic_repair_enabled=True,
    )
