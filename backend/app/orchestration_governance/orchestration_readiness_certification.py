"""Certification for v4.3 orchestration readiness.

The readiness layer validates descriptive governance evidence across Phases 1
through 8. It certifies architectural closeout planning readiness without
approving operational readiness, authorizing orchestration, deciding,
executing, activating, repairing, inferring, routing, traversing, scheduling,
sequencing, integrating with planners, or consuming production bundles.
"""

from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
from typing import Any, Iterable

from .orchestration_continuity_certification import (
    build_continuity_integrity_certification_diagnostics,
    default_orchestration_continuity_integrity_certification,
    validate_continuity_non_execution_authorization_decision,
    validate_integrity_certifications,
    validate_state_certification_visibility,
)
from .orchestration_continuity_hashing import (
    hash_orchestration_continuity_integrity_certification,
)
from .orchestration_readiness_hashing import (
    hash_orchestration_readiness_certification,
    hash_readiness_certification_record,
    hash_readiness_diagnostic,
    hash_readiness_explainability,
    hash_readiness_state_summary,
)
from .orchestration_readiness_models import (
    EXPLICIT_ORCHESTRATION_READINESS_PROHIBITIONS,
    READINESS_CERTIFICATION_TYPES,
    READINESS_CLASSIFICATION_ARCHITECTURAL_CLOSEOUT_PLANNING_READY,
    READINESS_CLASSIFICATION_BLOCKED,
    READINESS_LAYER_CAPABILITY,
    READINESS_LAYER_CONTINUITY,
    READINESS_LAYER_COORDINATION,
    READINESS_LAYER_DIAGNOSTICS,
    READINESS_LAYER_IDS,
    READINESS_LAYER_MANIFEST,
    READINESS_LAYER_POLICY,
    READINESS_LAYER_TOPOLOGY,
    READINESS_LAYER_TRANSITION,
    READINESS_STATE_BLOCKED,
    READINESS_STATE_CONFLICTING,
    READINESS_STATE_PROHIBITED,
    READINESS_STATE_STALE,
    READINESS_STATE_TYPES,
    READINESS_STATE_UNSUPPORTED,
    OrchestrationReadinessCertification,
    ReadinessCertificationRecord,
    ReadinessDiagnostic,
    ReadinessExplainability,
    ReadinessStateSummary,
    default_readiness_certification_identity,
    default_readiness_certification_metadata,
)
from .orchestration_readiness_serialization import (
    serialize_orchestration_readiness_certification,
)


READINESS_CERTIFICATION_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "readiness_approved",
    "orchestration_execution_enabled",
    "orchestration_authorization_enabled",
    "orchestration_approval_enabled",
    "readiness_approval_enabled",
    "orchestration_decision_enabled",
    "orchestration_recommendation_enabled",
    "orchestration_routing_enabled",
    "orchestration_traversal_enabled",
    "orchestration_scheduling_enabled",
    "orchestration_sequencing_enabled",
    "orchestration_activation_enabled",
    "orchestration_coordination_execution_enabled",
    "orchestration_dispatch_enabled",
    "orchestration_runtime_behavior_enabled",
    "orchestration_planning_engine_enabled",
    "orchestration_decision_engine_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "runtime_mutation_enabled",
    "operational_mutation_enabled",
    "hidden_orchestration_pathway_enabled",
    "implicit_authorization_enabled",
    "dependency_resolution_enabled",
    "authorization_enabled",
    "approval_enabled",
    "execution_enabled",
    "activation_enabled",
    "decision_enabled",
    "recommendation_enabled",
    "mutation_enabled",
)

REQUIRED_EXPLAINABILITY_CATEGORIES: tuple[str, ...] = (
    "orchestration_non_executable",
    "orchestration_authorization_unavailable",
    "orchestration_approval_unavailable",
    "governance_readiness_matters",
    "continuity_readiness_matters",
    "integrity_readiness_matters",
    "replay_safe_evidence_matters",
    "rollback_safe_evidence_matters",
    "fail_visible_readiness_states_exist",
    "operational_orchestration_prohibited",
)


def _sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({value for value in values if value}))


@lru_cache(maxsize=1)
def _default_continuity_source():
    return default_orchestration_continuity_integrity_certification()


@lru_cache(maxsize=1)
def _default_sources() -> dict[str, tuple[str, str]]:
    continuity = _default_continuity_source()
    identity = continuity.identity
    return {
        READINESS_LAYER_MANIFEST: (
            identity.source_manifest_reference,
            identity.source_manifest_hash_reference,
        ),
        READINESS_LAYER_TOPOLOGY: (
            identity.source_topology_reference,
            identity.source_topology_hash_reference,
        ),
        READINESS_LAYER_CAPABILITY: (
            identity.source_capability_reference,
            identity.source_capability_hash_reference,
        ),
        READINESS_LAYER_POLICY: (
            identity.source_policy_reference,
            identity.source_policy_hash_reference,
        ),
        READINESS_LAYER_TRANSITION: (
            identity.source_transition_reference,
            identity.source_transition_hash_reference,
        ),
        READINESS_LAYER_COORDINATION: (
            identity.source_coordination_reference,
            identity.source_coordination_hash_reference,
        ),
        READINESS_LAYER_DIAGNOSTICS: (
            identity.source_diagnostics_reference,
            identity.source_diagnostics_hash_reference,
        ),
        READINESS_LAYER_CONTINUITY: (
            identity.certification_id,
            hash_orchestration_continuity_integrity_certification(continuity),
        ),
    }


def default_readiness_certifications() -> tuple[ReadinessCertificationRecord, ...]:
    sources = _default_sources()
    evidence_refs = tuple(reference for reference, _hash in sources.values())
    records: list[ReadinessCertificationRecord] = []
    for index, readiness_type in enumerate(READINESS_CERTIFICATION_TYPES, start=1):
        records.append(
            ReadinessCertificationRecord(
                readiness_id=f"v4_3_readiness_{readiness_type}_certification",
                readiness_type=readiness_type,
                readiness_classification=READINESS_CLASSIFICATION_ARCHITECTURAL_CLOSEOUT_PLANNING_READY,
                readiness_state="certified_for_architectural_closeout_planning",
                certified_layer_ids=READINESS_LAYER_IDS,
                evidence_reference_ids=evidence_refs,
                readiness_gap_ids=(),
                governance_instability_ids=(),
                continuity_failure_ids=(),
                integrity_failure_ids=(),
                deterministic_order=index,
            )
        )
    return tuple(records)


def default_state_readiness_summaries() -> tuple[ReadinessStateSummary, ...]:
    continuity = _default_continuity_source()
    state_validation = validate_state_certification_visibility(continuity)
    source_by_state = {
        summary.state_type: summary
        for summary in continuity.state_certification_summaries
    }
    counts = {
        READINESS_STATE_PROHIBITED: state_validation["prohibited_state_certification_count"],
        READINESS_STATE_UNSUPPORTED: state_validation["unsupported_state_certification_count"],
        READINESS_STATE_BLOCKED: state_validation["blocked_state_certification_count"],
        READINESS_STATE_STALE: state_validation["stale_state_certification_count"],
        READINESS_STATE_CONFLICTING: state_validation["conflicting_state_certification_count"],
    }
    summaries: list[ReadinessStateSummary] = []
    for index, state_type in enumerate(READINESS_STATE_TYPES, start=1):
        source = source_by_state[state_type]
        summaries.append(
            ReadinessStateSummary(
                state_summary_id=f"v4_3_readiness_{state_type}_state_summary",
                state_type=state_type,
                affected_layer_ids=source.affected_layer_ids,
                affected_reference_ids=source.affected_reference_ids,
                readiness_count=int(counts[state_type]),
                deterministic_order=index,
            )
        )
    return tuple(summaries)


def default_readiness_diagnostics(
    readiness: tuple[ReadinessCertificationRecord, ...],
    states: tuple[ReadinessStateSummary, ...],
) -> tuple[ReadinessDiagnostic, ...]:
    readiness_ids = tuple(item.readiness_id for item in readiness)
    state_ids = tuple(item.state_summary_id for item in states)
    return (
        ReadinessDiagnostic(
            diagnostic_id="v4_3_readiness_identity_diagnostic",
            diagnostic_category="readiness_certification_identity_visibility",
            severity="info",
            message="Readiness certification identity is deterministic and descriptive-only.",
            affected_readiness_ids=(),
            affected_state_summary_ids=(),
            deterministic_order=1,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_governance_readiness_diagnostic",
            diagnostic_category="governance_readiness_visibility",
            severity="info",
            message="Governance readiness is certified for architectural closeout planning without operational approval.",
            affected_readiness_ids=("v4_3_readiness_governance_readiness_certification",),
            affected_state_summary_ids=(),
            deterministic_order=2,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_continuity_readiness_diagnostic",
            diagnostic_category="continuity_readiness_visibility",
            severity="info",
            message="Continuity readiness is certified from Phase 8 continuity evidence without authorizing orchestration.",
            affected_readiness_ids=("v4_3_readiness_continuity_readiness_certification",),
            affected_state_summary_ids=(),
            deterministic_order=3,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_integrity_readiness_diagnostic",
            diagnostic_category="integrity_readiness_visibility",
            severity="info",
            message="Integrity readiness is certified from Phase 8 hash evidence without production consumption.",
            affected_readiness_ids=("v4_3_readiness_integrity_readiness_certification",),
            affected_state_summary_ids=(),
            deterministic_order=4,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_replay_safe_readiness_diagnostic",
            diagnostic_category="replay_safe_readiness_visibility",
            severity="info",
            message="Replay-safe readiness is certified through stable deterministic serialization and hashing.",
            affected_readiness_ids=("v4_3_readiness_replay_safe_readiness_certification",),
            affected_state_summary_ids=(),
            deterministic_order=5,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_rollback_safe_readiness_diagnostic",
            diagnostic_category="rollback_safe_readiness_visibility",
            severity="info",
            message="Rollback-safe readiness is certified through stable comparable governance evidence.",
            affected_readiness_ids=("v4_3_readiness_rollback_safe_readiness_certification",),
            affected_state_summary_ids=(),
            deterministic_order=6,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_state_readiness_diagnostic",
            diagnostic_category="fail_visible_readiness_state_visibility",
            severity="blocker",
            message="Prohibited, unsupported, blocked, stale, and conflicting states remain visible during readiness certification.",
            affected_readiness_ids=readiness_ids,
            affected_state_summary_ids=state_ids,
            deterministic_order=7,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_non_approval_diagnostic",
            diagnostic_category="non_approval_boundary_visibility",
            severity="prohibited",
            message="Readiness certification certifies enabled_orchestration_approval_count equals 0.",
            affected_readiness_ids=readiness_ids,
            affected_state_summary_ids=state_ids,
            deterministic_order=8,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_non_authorization_diagnostic",
            diagnostic_category="non_authorization_boundary_visibility",
            severity="prohibited",
            message="Readiness certification certifies enabled_orchestration_authorization_count equals 0.",
            affected_readiness_ids=readiness_ids,
            affected_state_summary_ids=state_ids,
            deterministic_order=9,
        ),
        ReadinessDiagnostic(
            diagnostic_id="v4_3_non_execution_non_decision_diagnostic",
            diagnostic_category="non_execution_non_decision_boundary_visibility",
            severity="prohibited",
            message="Readiness certification certifies execution, decision, recommendation, coordination, transition, policy, and capability counts remain 0.",
            affected_readiness_ids=readiness_ids,
            affected_state_summary_ids=state_ids,
            deterministic_order=10,
        ),
    )


def default_readiness_explainability() -> tuple[ReadinessExplainability, ...]:
    affected = READINESS_LAYER_IDS
    return (
        ReadinessExplainability(
            explanation_id="v4_3_readiness_non_executable_explanation",
            explanation_category="orchestration_non_executable",
            summary="Orchestration remains non-executable because Phase 9 certifies readiness evidence only.",
            affected_reference_ids=affected,
            deterministic_order=1,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_readiness_authorization_unavailable_explanation",
            explanation_category="orchestration_authorization_unavailable",
            summary="Orchestration authorization remains unavailable because readiness certification cannot approve or authorize runtime behavior.",
            affected_reference_ids=affected,
            deterministic_order=2,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_readiness_approval_unavailable_explanation",
            explanation_category="orchestration_approval_unavailable",
            summary="Operational readiness approval remains unavailable because Phase 9 only certifies architectural closeout planning readiness.",
            affected_reference_ids=affected,
            deterministic_order=3,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_governance_readiness_explanation",
            explanation_category="governance_readiness_matters",
            summary="Governance readiness matters because the v4.3 chain must be internally stable before architectural closeout planning can rely on it.",
            affected_reference_ids=affected,
            deterministic_order=4,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_continuity_readiness_explanation",
            explanation_category="continuity_readiness_matters",
            summary="Continuity readiness matters because lineage, provenance, diagnostics, and explainability must remain connected across all orchestration governance layers.",
            affected_reference_ids=affected,
            deterministic_order=5,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_integrity_readiness_explanation",
            explanation_category="integrity_readiness_matters",
            summary="Integrity readiness matters because cross-layer evidence hashes must stay stable and internally consistent.",
            affected_reference_ids=affected,
            deterministic_order=6,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_readiness_replay_safe_explanation",
            explanation_category="replay_safe_evidence_matters",
            summary="Replay-safe evidence matters because readiness certification must produce identical evidence across repeated runs.",
            affected_reference_ids=affected,
            deterministic_order=7,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_readiness_rollback_safe_explanation",
            explanation_category="rollback_safe_evidence_matters",
            summary="Rollback-safe evidence matters because readiness certification must remain comparable against prior deterministic governance evidence.",
            affected_reference_ids=affected,
            deterministic_order=8,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_readiness_fail_visible_states_explanation",
            explanation_category="fail_visible_readiness_states_exist",
            summary="Fail-visible readiness states exist so gaps, stale evidence, conflicts, prohibited states, and unsupported states are surfaced rather than inferred away.",
            affected_reference_ids=affected,
            deterministic_order=9,
        ),
        ReadinessExplainability(
            explanation_id="v4_3_readiness_operational_prohibited_explanation",
            explanation_category="operational_orchestration_prohibited",
            summary="Operational orchestration remains prohibited because Phase 9 creates no execution, authorization, approval, decision, routing, scheduling, planner, or production pathway.",
            affected_reference_ids=affected,
            deterministic_order=10,
        ),
    )


def default_orchestration_readiness_certification() -> OrchestrationReadinessCertification:
    identity = default_readiness_certification_identity()
    readiness = default_readiness_certifications()
    states = default_state_readiness_summaries()
    return OrchestrationReadinessCertification(
        identity=identity,
        metadata=default_readiness_certification_metadata(identity),
        readiness_certifications=readiness,
        state_readiness_summaries=states,
        diagnostics=default_readiness_diagnostics(readiness, states),
        explainability_summaries=default_readiness_explainability(),
    )


def readiness_certification_flags(
    certification: OrchestrationReadinessCertification,
) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        certification,
        certification.identity,
        certification.metadata,
        *certification.readiness_certifications,
        *certification.state_readiness_summaries,
        *certification.diagnostics,
        *certification.explainability_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in READINESS_CERTIFICATION_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_readiness_certification_flags(
    certification: OrchestrationReadinessCertification,
) -> dict[str, bool]:
    return {key: value for key, value in readiness_certification_flags(certification).items() if value}


def readiness_certification_identity_key(
    certification: OrchestrationReadinessCertification,
) -> str:
    identity = certification.identity
    return "|".join(
        (
            identity.schema_version,
            identity.readiness_id,
            identity.readiness_version,
            identity.source_manifest_reference,
            identity.source_manifest_hash_reference,
            identity.source_topology_reference,
            identity.source_topology_hash_reference,
            identity.source_capability_reference,
            identity.source_capability_hash_reference,
            identity.source_policy_reference,
            identity.source_policy_hash_reference,
            identity.source_transition_reference,
            identity.source_transition_hash_reference,
            identity.source_coordination_reference,
            identity.source_coordination_hash_reference,
            identity.source_diagnostics_reference,
            identity.source_diagnostics_hash_reference,
            identity.source_continuity_integrity_reference,
            identity.source_continuity_integrity_hash_reference,
            identity.governance_reference,
        )
    )


def readiness_certifications_equal(
    left: OrchestrationReadinessCertification,
    right: OrchestrationReadinessCertification,
) -> bool:
    return serialize_orchestration_readiness_certification(
        left
    ) == serialize_orchestration_readiness_certification(right)


def enabled_coordination_execution_count(certification: OrchestrationReadinessCertification) -> int:
    return int(
        certification.enabled_coordination_execution_count
        or certification.orchestration_coordination_execution_enabled
        or certification.orchestration_dispatch_enabled
    )


def enabled_transition_execution_count(certification: OrchestrationReadinessCertification) -> int:
    return int(certification.enabled_transition_execution_count or certification.orchestration_activation_enabled)


def enabled_policy_enforcement_count(certification: OrchestrationReadinessCertification) -> int:
    return int(
        certification.enabled_policy_enforcement_count
        or certification.orchestration_authorization_enabled
        or certification.orchestration_approval_enabled
        or certification.readiness_approval_enabled
    )


def enabled_operational_capability_count(certification: OrchestrationReadinessCertification) -> int:
    return int(
        certification.enabled_operational_capability_count
        or certification.orchestration_execution_enabled
        or certification.orchestration_activation_enabled
        or certification.orchestration_routing_enabled
        or certification.orchestration_traversal_enabled
        or certification.orchestration_scheduling_enabled
        or certification.orchestration_sequencing_enabled
        or certification.dependency_resolution_enabled
        or certification.planner_integration_enabled
        or certification.production_consumption_enabled
        or certification.runtime_mutation_enabled
        or certification.operational_mutation_enabled
    )


def enabled_orchestration_decision_count(certification: OrchestrationReadinessCertification) -> int:
    return int(
        certification.enabled_orchestration_decision_count
        or certification.orchestration_decision_enabled
        or certification.orchestration_planning_engine_enabled
        or certification.orchestration_decision_engine_enabled
        or any(item.decision_enabled for item in certification.readiness_certifications)
        or any(item.decision_enabled for item in certification.state_readiness_summaries)
        or any(item.decision_enabled for item in certification.diagnostics)
        or any(item.decision_enabled for item in certification.explainability_summaries)
    )


def enabled_orchestration_recommendation_count(certification: OrchestrationReadinessCertification) -> int:
    return int(
        certification.enabled_orchestration_recommendation_count
        or certification.orchestration_recommendation_enabled
        or any(item.recommendation_enabled for item in certification.readiness_certifications)
        or any(item.recommendation_enabled for item in certification.state_readiness_summaries)
        or any(item.recommendation_enabled for item in certification.diagnostics)
        or any(item.recommendation_enabled for item in certification.explainability_summaries)
    )


def enabled_orchestration_authorization_count(certification: OrchestrationReadinessCertification) -> int:
    return int(
        certification.enabled_orchestration_authorization_count
        or certification.orchestration_authorization_enabled
        or certification.implicit_authorization_enabled
        or certification.execution_authorized
        or any(item.authorization_enabled for item in certification.readiness_certifications)
        or any(item.authorization_enabled for item in certification.state_readiness_summaries)
        or any(item.authorization_enabled for item in certification.diagnostics)
        or any(item.authorization_enabled for item in certification.explainability_summaries)
    )


def enabled_orchestration_approval_count(certification: OrchestrationReadinessCertification) -> int:
    return int(
        certification.enabled_orchestration_approval_count
        or certification.orchestration_approval_enabled
        or certification.readiness_approval_enabled
        or certification.readiness_approved
        or any(item.approval_enabled for item in certification.readiness_certifications)
        or any(item.approval_enabled for item in certification.state_readiness_summaries)
        or any(item.approval_enabled for item in certification.diagnostics)
        or any(item.approval_enabled for item in certification.explainability_summaries)
    )


def validate_readiness_certification_identity(
    certification: OrchestrationReadinessCertification,
) -> dict[str, object]:
    identity = certification.identity
    expected_sources = _default_sources()
    source_hash_mismatches: list[str] = []
    actual_hashes = {
        READINESS_LAYER_MANIFEST: identity.source_manifest_hash_reference,
        READINESS_LAYER_TOPOLOGY: identity.source_topology_hash_reference,
        READINESS_LAYER_CAPABILITY: identity.source_capability_hash_reference,
        READINESS_LAYER_POLICY: identity.source_policy_hash_reference,
        READINESS_LAYER_TRANSITION: identity.source_transition_hash_reference,
        READINESS_LAYER_COORDINATION: identity.source_coordination_hash_reference,
        READINESS_LAYER_DIAGNOSTICS: identity.source_diagnostics_hash_reference,
        READINESS_LAYER_CONTINUITY: identity.source_continuity_integrity_hash_reference,
    }
    for layer_id, (_reference, expected_hash) in expected_sources.items():
        if actual_hashes[layer_id] != expected_hash:
            source_hash_mismatches.append(layer_id)
    identity_payload = asdict(identity)
    missing_fields = tuple(
        sorted(
            key
            for key, value in identity_payload.items()
            if isinstance(value, str) and not value
        )
    )
    valid = (
        len(missing_fields) == 0
        and len(source_hash_mismatches) == 0
        and identity.non_executable
        and identity.non_authorizing
        and identity.non_approving
        and identity.non_decisioning
        and identity.descriptive_only
        and not identity.orchestration_execution_enabled
        and not identity.orchestration_authorization_enabled
        and not identity.orchestration_approval_enabled
        and not identity.orchestration_decision_enabled
        and not identity.orchestration_recommendation_enabled
        and not identity.orchestration_activation_enabled
        and not identity.planner_integration_enabled
        and not identity.production_consumption_enabled
    )
    return {
        "valid": valid,
        "missing_identity_fields": missing_fields,
        "source_hash_mismatches": tuple(sorted(source_hash_mismatches)),
        "identity_key": readiness_certification_identity_key(certification),
        "readiness_id": identity.readiness_id,
        "schema_version": identity.schema_version,
        "descriptive_only": identity.descriptive_only,
        "non_executable": identity.non_executable,
        "non_authorizing": identity.non_authorizing,
        "non_approving": identity.non_approving,
        "non_decisioning": identity.non_decisioning,
    }


def validate_readiness_certifications(
    certification: OrchestrationReadinessCertification,
) -> dict[str, object]:
    readiness_ids = tuple(item.readiness_id for item in certification.readiness_certifications)
    duplicate_ids = tuple(sorted(value for value in set(readiness_ids) if readiness_ids.count(value) > 1))
    types = tuple(item.readiness_type for item in certification.readiness_certifications)
    missing_types = tuple(sorted(value for value in READINESS_CERTIFICATION_TYPES if value not in types))
    gap_ids = _sorted_unique(
        gap_id for item in certification.readiness_certifications for gap_id in item.readiness_gap_ids
    )
    instability_ids = _sorted_unique(
        item_id
        for item in certification.readiness_certifications
        for item_id in item.governance_instability_ids
    )
    continuity_failure_ids = _sorted_unique(
        item_id for item in certification.readiness_certifications for item_id in item.continuity_failure_ids
    )
    integrity_failure_ids = _sorted_unique(
        item_id for item in certification.readiness_certifications for item_id in item.integrity_failure_ids
    )
    invalid_classification_ids = tuple(
        sorted(
            item.readiness_id
            for item in certification.readiness_certifications
            if item.readiness_classification
            != READINESS_CLASSIFICATION_ARCHITECTURAL_CLOSEOUT_PLANNING_READY
        )
    )
    non_descriptive = tuple(
        sorted(item.readiness_id for item in certification.readiness_certifications if not item.descriptive_only)
    )
    enabled = tuple(
        sorted(
            item.readiness_id
            for item in certification.readiness_certifications
            if item.authorization_enabled
            or item.approval_enabled
            or item.execution_enabled
            or item.activation_enabled
            or item.decision_enabled
            or item.recommendation_enabled
            or item.planner_integration_enabled
            or item.production_consumption_enabled
        )
    )
    valid = (
        len(duplicate_ids) == 0
        and len(missing_types) == 0
        and len(gap_ids) == 0
        and len(instability_ids) == 0
        and len(continuity_failure_ids) == 0
        and len(integrity_failure_ids) == 0
        and len(invalid_classification_ids) == 0
        and len(non_descriptive) == 0
        and len(enabled) == 0
    )
    return {
        "valid": valid,
        "duplicate_readiness_ids": duplicate_ids,
        "missing_readiness_types": missing_types,
        "invalid_readiness_classification_ids": invalid_classification_ids,
        "readiness_gap_ids": gap_ids,
        "governance_instability_ids": instability_ids,
        "continuity_failure_ids": continuity_failure_ids,
        "integrity_failure_ids": integrity_failure_ids,
        "readiness_gap_count": len(gap_ids),
        "governance_instability_count": len(instability_ids),
        "continuity_failure_count": len(continuity_failure_ids),
        "integrity_failure_count": len(integrity_failure_ids),
        "non_descriptive_readiness_ids": non_descriptive,
        "enabled_readiness_ids": enabled,
        "readiness_certification_count": len(certification.readiness_certifications),
        "replay_safe_readiness_status": all(item.replay_safe for item in certification.readiness_certifications),
        "rollback_safe_readiness_status": all(item.rollback_safe for item in certification.readiness_certifications),
        "governance_readiness_visible": any(
            item.readiness_type == "governance_readiness" and item.governance_safe
            for item in certification.readiness_certifications
        ),
        "continuity_readiness_visible": any(
            item.readiness_type == "continuity_readiness" and item.continuity_safe
            for item in certification.readiness_certifications
        ),
        "integrity_readiness_visible": any(
            item.readiness_type == "integrity_readiness" and item.integrity_safe
            for item in certification.readiness_certifications
        ),
        "readiness_classification": (
            READINESS_CLASSIFICATION_ARCHITECTURAL_CLOSEOUT_PLANNING_READY
            if valid
            else READINESS_CLASSIFICATION_BLOCKED
        ),
    }


def validate_state_readiness_visibility(
    certification: OrchestrationReadinessCertification,
) -> dict[str, object]:
    summaries_by_type = {item.state_type: item for item in certification.state_readiness_summaries}
    missing_state_types = tuple(
        sorted(state_type for state_type in READINESS_STATE_TYPES if state_type not in summaries_by_type)
    )
    enabled = tuple(
        sorted(
            item.state_summary_id
            for item in certification.state_readiness_summaries
            if item.authorization_enabled
            or item.approval_enabled
            or item.execution_enabled
            or item.decision_enabled
            or item.recommendation_enabled
            or item.repair_enabled
            or item.inference_enabled
        )
    )

    def count(state_type: str) -> int:
        return summaries_by_type[state_type].readiness_count if state_type in summaries_by_type else 0

    return {
        "valid": len(missing_state_types) == 0 and len(enabled) == 0,
        "missing_state_types": missing_state_types,
        "enabled_state_summary_ids": enabled,
        "prohibited_state_readiness_count": count(READINESS_STATE_PROHIBITED),
        "unsupported_state_readiness_count": count(READINESS_STATE_UNSUPPORTED),
        "blocked_state_readiness_count": count(READINESS_STATE_BLOCKED),
        "stale_state_readiness_count": count(READINESS_STATE_STALE),
        "conflicting_state_readiness_count": count(READINESS_STATE_CONFLICTING),
        "prohibited_state_readiness_visible": count(READINESS_STATE_PROHIBITED) > 0,
        "unsupported_state_readiness_visible": count(READINESS_STATE_UNSUPPORTED) > 0,
        "blocked_state_readiness_visible": count(READINESS_STATE_BLOCKED) > 0,
        "stale_state_readiness_visible": count(READINESS_STATE_STALE) > 0,
        "conflicting_state_readiness_visible": count(READINESS_STATE_CONFLICTING) > 0,
    }


def validate_readiness_explainability(
    certification: OrchestrationReadinessCertification,
) -> dict[str, object]:
    categories = tuple(
        sorted(summary.explanation_category for summary in certification.explainability_summaries)
    )
    missing_categories = tuple(
        sorted(category for category in REQUIRED_EXPLAINABILITY_CATEGORIES if category not in categories)
    )
    non_descriptive = tuple(
        sorted(
            summary.explanation_id
            for summary in certification.explainability_summaries
            if not summary.descriptive_only
        )
    )
    enabled = tuple(
        sorted(
            summary.explanation_id
            for summary in certification.explainability_summaries
            if summary.authorization_enabled
            or summary.approval_enabled
            or summary.execution_enabled
            or summary.activation_enabled
            or summary.decision_enabled
            or summary.recommendation_enabled
            or summary.planner_integration_enabled
            or summary.production_consumption_enabled
        )
    )
    return {
        "valid": len(missing_categories) == 0 and len(non_descriptive) == 0 and len(enabled) == 0,
        "explainability_categories": categories,
        "missing_explainability_categories": missing_categories,
        "non_descriptive_explanations": non_descriptive,
        "enabled_explanations": enabled,
        "deterministic": all(summary.deterministic for summary in certification.explainability_summaries),
        "replay_safe": all(summary.replay_safe for summary in certification.explainability_summaries),
        "rollback_safe": all(summary.rollback_safe for summary in certification.explainability_summaries),
    }


def validate_readiness_non_execution_authorization_approval_decision(
    certification: OrchestrationReadinessCertification,
) -> dict[str, object]:
    enabled_flags = enabled_readiness_certification_flags(certification)
    coordination_count = enabled_coordination_execution_count(certification)
    transition_count = enabled_transition_execution_count(certification)
    policy_count = enabled_policy_enforcement_count(certification)
    operational_count = enabled_operational_capability_count(certification)
    decision_count = enabled_orchestration_decision_count(certification)
    recommendation_count = enabled_orchestration_recommendation_count(certification)
    authorization_count = enabled_orchestration_authorization_count(certification)
    approval_count = enabled_orchestration_approval_count(certification)
    valid = (
        len(enabled_flags) == 0
        and coordination_count == 0
        and transition_count == 0
        and policy_count == 0
        and operational_count == 0
        and decision_count == 0
        and recommendation_count == 0
        and authorization_count == 0
        and approval_count == 0
        and certification.non_executable
        and certification.non_authorizing
        and certification.non_approving
        and certification.non_decisioning
        and certification.descriptive_only
    )
    return {
        "valid": valid,
        "enabled_readiness_certification_flags": enabled_flags,
        "enabled_coordination_execution_count": coordination_count,
        "enabled_transition_execution_count": transition_count,
        "enabled_policy_enforcement_count": policy_count,
        "enabled_operational_capability_count": operational_count,
        "enabled_orchestration_decision_count": decision_count,
        "enabled_orchestration_recommendation_count": recommendation_count,
        "enabled_orchestration_authorization_count": authorization_count,
        "enabled_orchestration_approval_count": approval_count,
        "non_executable": certification.non_executable,
        "non_authorizing": certification.non_authorizing,
        "non_approving": certification.non_approving,
        "non_decisioning": certification.non_decisioning,
        "descriptive_only": certification.descriptive_only,
        "orchestration_execution_disabled": not certification.orchestration_execution_enabled,
        "orchestration_authorization_disabled": not certification.orchestration_authorization_enabled,
        "orchestration_approval_disabled": not certification.orchestration_approval_enabled,
        "readiness_approval_disabled": not certification.readiness_approval_enabled,
        "readiness_operational_approval_disabled": not certification.readiness_approved,
        "orchestration_decision_disabled": not certification.orchestration_decision_enabled,
        "orchestration_recommendation_disabled": not certification.orchestration_recommendation_enabled,
        "orchestration_routing_disabled": not certification.orchestration_routing_enabled,
        "orchestration_traversal_disabled": not certification.orchestration_traversal_enabled,
        "orchestration_scheduling_disabled": not certification.orchestration_scheduling_enabled,
        "orchestration_sequencing_disabled": not certification.orchestration_sequencing_enabled,
        "orchestration_activation_disabled": not certification.orchestration_activation_enabled,
        "orchestration_coordination_execution_disabled": (
            not certification.orchestration_coordination_execution_enabled
        ),
        "orchestration_dispatch_disabled": not certification.orchestration_dispatch_enabled,
        "orchestration_runtime_behavior_disabled": not certification.orchestration_runtime_behavior_enabled,
        "orchestration_planning_engine_disabled": not certification.orchestration_planning_engine_enabled,
        "orchestration_decision_engine_disabled": not certification.orchestration_decision_engine_enabled,
        "planner_integration_disabled": not certification.planner_integration_enabled,
        "production_consumption_disabled": not certification.production_consumption_enabled,
        "remediation_disabled": not certification.remediation_enabled,
        "repair_disabled": not certification.repair_enabled,
        "inference_disabled": not certification.inference_enabled,
        "ranking_disabled": not certification.ranking_enabled,
        "scoring_disabled": not certification.scoring_enabled,
        "selection_disabled": not certification.selection_enabled,
        "optimization_disabled": not certification.optimization_enabled,
        "runtime_mutation_disabled": not certification.runtime_mutation_enabled,
        "operational_mutation_disabled": not certification.operational_mutation_enabled,
        "hidden_orchestration_pathway_absent": not certification.hidden_orchestration_pathway_enabled,
        "implicit_authorization_absent": not certification.implicit_authorization_enabled,
        "dependency_resolution_disabled": not certification.dependency_resolution_enabled,
    }


def build_readiness_certification_diagnostics(
    certification: OrchestrationReadinessCertification | None = None,
) -> dict[str, Any]:
    source = certification or default_orchestration_readiness_certification()
    identity = validate_readiness_certification_identity(source)
    readiness = validate_readiness_certifications(source)
    states = validate_state_readiness_visibility(source)
    explainability = validate_readiness_explainability(source)
    non_execution = validate_readiness_non_execution_authorization_approval_decision(source)
    continuity = _default_continuity_source()
    continuity_diagnostics = build_continuity_integrity_certification_diagnostics(continuity)
    continuity_non_execution = validate_continuity_non_execution_authorization_decision(continuity)
    continuity_integrity = validate_integrity_certifications(continuity)
    return {
        "readiness_certification_hash": hash_orchestration_readiness_certification(source),
        "readiness_certification_hashes": [
            hash_readiness_certification_record(item) for item in source.readiness_certifications
        ],
        "state_readiness_hashes": [
            hash_readiness_state_summary(item) for item in source.state_readiness_summaries
        ],
        "diagnostic_hashes": [hash_readiness_diagnostic(item) for item in source.diagnostics],
        "explainability_hashes": [
            hash_readiness_explainability(item) for item in source.explainability_summaries
        ],
        "identity_validation": identity,
        "readiness_validation": readiness,
        "state_readiness_validation": states,
        "explainability_validation": explainability,
        "non_execution_authorization_approval_decision_validation": non_execution,
        "phase_8_continuity_diagnostics": continuity_diagnostics,
        "phase_8_integrity_validation": continuity_integrity,
        "phase_8_non_execution_validation": continuity_non_execution,
        "readiness_certification_count": len(source.readiness_certifications),
        "readiness_gap_count": readiness["readiness_gap_count"],
        "governance_instability_count": readiness["governance_instability_count"],
        "continuity_failure_count": readiness["continuity_failure_count"],
        "integrity_failure_count": readiness["integrity_failure_count"],
        "prohibited_state_readiness_count": states["prohibited_state_readiness_count"],
        "unsupported_state_readiness_count": states["unsupported_state_readiness_count"],
        "blocked_state_readiness_count": states["blocked_state_readiness_count"],
        "stale_state_readiness_count": states["stale_state_readiness_count"],
        "conflicting_state_readiness_count": states["conflicting_state_readiness_count"],
        "diagnostic_categories": tuple(sorted(item.diagnostic_category for item in source.diagnostics)),
        "explainability_categories": tuple(
            sorted(item.explanation_category for item in source.explainability_summaries)
        ),
        "enabled_coordination_execution_count": non_execution["enabled_coordination_execution_count"],
        "enabled_transition_execution_count": non_execution["enabled_transition_execution_count"],
        "enabled_policy_enforcement_count": non_execution["enabled_policy_enforcement_count"],
        "enabled_operational_capability_count": non_execution["enabled_operational_capability_count"],
        "enabled_orchestration_decision_count": non_execution["enabled_orchestration_decision_count"],
        "enabled_orchestration_recommendation_count": non_execution[
            "enabled_orchestration_recommendation_count"
        ],
        "enabled_orchestration_authorization_count": non_execution[
            "enabled_orchestration_authorization_count"
        ],
        "enabled_orchestration_approval_count": non_execution["enabled_orchestration_approval_count"],
        "diagnostics_are_descriptive_only": all(item.descriptive_only for item in source.diagnostics),
        "explainability_is_descriptive_only": all(
            item.descriptive_only for item in source.explainability_summaries
        ),
        "explicit_prohibitions": EXPLICIT_ORCHESTRATION_READINESS_PROHIBITIONS,
    }
