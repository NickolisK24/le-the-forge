"""Certification for v4.3 orchestration continuity and integrity.

The certification layer validates descriptive governance evidence across
Phases 1 through 7. It exposes continuity, integrity, lineage, provenance,
replay-safety, rollback-safety, stale-state, conflicting-state, and fail-visible
certification summaries without authorizing, deciding, executing, activating,
repairing, inferring, routing, traversing, scheduling, sequencing, integrating
with planners, or consuming production bundles.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from .orchestration_capability_hashing import hash_orchestration_capability_visibility
from .orchestration_capability_models import default_orchestration_capability_visibility
from .orchestration_continuity_hashing import (
    hash_certification_state_summary,
    hash_continuity_certification_diagnostic,
    hash_continuity_certification_explainability,
    hash_continuity_certification_record,
    hash_integrity_certification_record,
    hash_orchestration_continuity_integrity_certification,
)
from .orchestration_continuity_models import (
    CERTIFICATION_LAYER_CAPABILITY,
    CERTIFICATION_LAYER_COORDINATION,
    CERTIFICATION_LAYER_DIAGNOSTICS,
    CERTIFICATION_LAYER_IDS,
    CERTIFICATION_LAYER_MANIFEST,
    CERTIFICATION_LAYER_POLICY,
    CERTIFICATION_LAYER_TOPOLOGY,
    CERTIFICATION_LAYER_TRANSITION,
    CERTIFICATION_STATE_BLOCKED,
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_CONFLICTING,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_STALE,
    CERTIFICATION_STATE_TYPES,
    CERTIFICATION_STATE_UNSUPPORTED,
    CONTINUITY_CERTIFICATION_TYPES,
    EXPLICIT_ORCHESTRATION_CONTINUITY_PROHIBITIONS,
    CertificationStateSummary,
    ContinuityCertificationDiagnostic,
    ContinuityCertificationExplainability,
    ContinuityCertificationRecord,
    IntegrityCertificationRecord,
    OrchestrationContinuityIntegrityCertification,
    default_continuity_certification_identity,
    default_continuity_certification_metadata,
)
from .orchestration_continuity_serialization import (
    serialize_orchestration_continuity_integrity_certification,
)
from .orchestration_coordination_hashing import hash_orchestration_coordination_visibility
from .orchestration_coordination_models import default_orchestration_coordination_visibility
from .orchestration_diagnostics_aggregation import (
    build_orchestration_diagnostics_aggregation_diagnostics,
    default_orchestration_diagnostics_aggregation,
    validate_diagnostics_aggregation_non_execution_and_non_decision,
    validate_diagnostics_aggregation_state_visibility,
)
from .orchestration_diagnostics_hashing import hash_orchestration_diagnostics_aggregation
from .orchestration_manifest_hashing import hash_orchestration_manifest
from .orchestration_manifest_models import default_orchestration_manifest
from .orchestration_policy_hashing import hash_orchestration_policy_visibility
from .orchestration_policy_models import default_orchestration_policy_visibility
from .orchestration_topology_hashing import hash_orchestration_topology
from .orchestration_topology_models import default_orchestration_topology
from .orchestration_transition_hashing import hash_orchestration_transition_visibility
from .orchestration_transition_models import default_orchestration_transition_visibility


CONTINUITY_CERTIFICATION_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "orchestration_authorization_enabled",
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
    "execution_enabled",
    "activation_enabled",
    "decision_enabled",
    "recommendation_enabled",
    "mutation_enabled",
)

REQUIRED_EXPLAINABILITY_CATEGORIES: tuple[str, ...] = (
    "orchestration_non_executable",
    "orchestration_authorization_unavailable",
    "governance_consistency_matters",
    "lineage_continuity_matters",
    "provenance_continuity_matters",
    "replay_safe_evidence_matters",
    "rollback_safe_evidence_matters",
    "fail_visible_inconsistencies_exist",
    "operational_orchestration_prohibited",
)


def _sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({value for value in values if value}))


def _default_sources() -> dict[str, tuple[str, str]]:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    policy = default_orchestration_policy_visibility()
    transition = default_orchestration_transition_visibility()
    coordination = default_orchestration_coordination_visibility()
    diagnostics = default_orchestration_diagnostics_aggregation()
    return {
        CERTIFICATION_LAYER_MANIFEST: (
            manifest.identity.manifest_id,
            hash_orchestration_manifest(manifest),
        ),
        CERTIFICATION_LAYER_TOPOLOGY: (
            topology.identity.topology_id,
            hash_orchestration_topology(topology),
        ),
        CERTIFICATION_LAYER_CAPABILITY: (
            capability.identity.capability_set_id,
            hash_orchestration_capability_visibility(capability),
        ),
        CERTIFICATION_LAYER_POLICY: (
            policy.identity.policy_set_id,
            hash_orchestration_policy_visibility(policy),
        ),
        CERTIFICATION_LAYER_TRANSITION: (
            transition.identity.transition_set_id,
            hash_orchestration_transition_visibility(transition),
        ),
        CERTIFICATION_LAYER_COORDINATION: (
            coordination.identity.coordination_set_id,
            hash_orchestration_coordination_visibility(coordination),
        ),
        CERTIFICATION_LAYER_DIAGNOSTICS: (
            diagnostics.identity.aggregation_id,
            hash_orchestration_diagnostics_aggregation(diagnostics),
        ),
    }


def default_continuity_certifications() -> tuple[ContinuityCertificationRecord, ...]:
    sources = _default_sources()
    evidence_refs = tuple(reference for reference, _hash in sources.values())
    certifications: list[ContinuityCertificationRecord] = []
    for index, certification_type in enumerate(CONTINUITY_CERTIFICATION_TYPES, start=1):
        certifications.append(
            ContinuityCertificationRecord(
                certification_id=f"v4_3_continuity_{certification_type}_certification",
                certification_type=certification_type,
                certification_state=CERTIFICATION_STATE_CERTIFIED,
                certified_layer_ids=CERTIFICATION_LAYER_IDS,
                evidence_reference_ids=evidence_refs,
                continuity_gap_ids=(),
                integrity_failure_ids=(),
                deterministic_order=index,
            )
        )
    return tuple(certifications)


def default_integrity_certifications() -> tuple[IntegrityCertificationRecord, ...]:
    sources = _default_sources()
    records: list[IntegrityCertificationRecord] = []
    for index, layer_id in enumerate(CERTIFICATION_LAYER_IDS, start=1):
        source_reference, source_hash = sources[layer_id]
        records.append(
            IntegrityCertificationRecord(
                integrity_id=f"v4_3_integrity_{layer_id}_hash_certification",
                layer_id=layer_id,
                source_reference_id=source_reference,
                expected_hash_reference=source_hash,
                actual_hash_reference=source_hash,
                integrity_state=CERTIFICATION_STATE_CERTIFIED,
                integrity_failure_ids=(),
                continuity_gap_ids=(),
                deterministic_order=index,
            )
        )
    return tuple(records)


def default_state_certification_summaries() -> tuple[CertificationStateSummary, ...]:
    diagnostics = default_orchestration_diagnostics_aggregation()
    state_validation = validate_diagnostics_aggregation_state_visibility(diagnostics)
    source_by_state = {
        summary.state_type: summary
        for summary in diagnostics.cross_layer_state_summaries
    }
    counts = {
        CERTIFICATION_STATE_PROHIBITED: state_validation["prohibited_state_count"],
        CERTIFICATION_STATE_UNSUPPORTED: state_validation["unsupported_state_count"],
        CERTIFICATION_STATE_BLOCKED: state_validation["blocked_state_count"],
        CERTIFICATION_STATE_STALE: state_validation["stale_state_count"],
        CERTIFICATION_STATE_CONFLICTING: state_validation["conflicting_state_count"],
    }
    summaries: list[CertificationStateSummary] = []
    for index, state_type in enumerate(CERTIFICATION_STATE_TYPES, start=1):
        source = source_by_state[state_type]
        summaries.append(
            CertificationStateSummary(
                state_summary_id=f"v4_3_certification_{state_type}_state_summary",
                state_type=state_type,
                affected_layer_ids=source.source_layer_ids,
                affected_reference_ids=source.affected_reference_ids,
                certification_count=int(counts[state_type]),
                deterministic_order=index,
            )
        )
    return tuple(summaries)


def default_continuity_certification_diagnostics(
    continuity: tuple[ContinuityCertificationRecord, ...],
    integrity: tuple[IntegrityCertificationRecord, ...],
    states: tuple[CertificationStateSummary, ...],
) -> tuple[ContinuityCertificationDiagnostic, ...]:
    certification_ids = tuple(item.certification_id for item in continuity)
    integrity_ids = tuple(item.integrity_id for item in integrity)
    state_ids = tuple(item.state_summary_id for item in states)
    return (
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_continuity_identity_diagnostic",
            diagnostic_category="continuity_certification_identity_visibility",
            severity="info",
            message="Continuity certification identity is deterministic and descriptive-only.",
            affected_certification_ids=(),
            affected_integrity_ids=(),
            affected_state_summary_ids=(),
            deterministic_order=1,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_lineage_continuity_diagnostic",
            diagnostic_category="lineage_continuity_visibility",
            severity="info",
            message="Lineage continuity is certified across v4.3 orchestration governance layers without planner integration.",
            affected_certification_ids=("v4_3_continuity_lineage_continuity_certification",),
            affected_integrity_ids=(),
            affected_state_summary_ids=(),
            deterministic_order=2,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_provenance_continuity_diagnostic",
            diagnostic_category="provenance_continuity_visibility",
            severity="info",
            message="Provenance continuity is certified across v4.3 orchestration governance layers without production consumption.",
            affected_certification_ids=("v4_3_continuity_provenance_continuity_certification",),
            affected_integrity_ids=(),
            affected_state_summary_ids=(),
            deterministic_order=3,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_governance_consistency_diagnostic",
            diagnostic_category="governance_consistency_visibility",
            severity="info",
            message="Governance consistency is certified as descriptive evidence and cannot authorize orchestration.",
            affected_certification_ids=("v4_3_continuity_governance_continuity_certification",),
            affected_integrity_ids=integrity_ids,
            affected_state_summary_ids=(),
            deterministic_order=4,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_cross_layer_integrity_diagnostic",
            diagnostic_category="cross_layer_integrity_visibility",
            severity="info",
            message="Cross-layer integrity hashes match deterministic source evidence.",
            affected_certification_ids=(),
            affected_integrity_ids=integrity_ids,
            affected_state_summary_ids=(),
            deterministic_order=5,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_replay_safe_certification_diagnostic",
            diagnostic_category="replay_safe_certification_visibility",
            severity="info",
            message="Replay-safe evidence remains stable across continuity and integrity certification.",
            affected_certification_ids=("v4_3_continuity_replay_safe_certification_certification",),
            affected_integrity_ids=(),
            affected_state_summary_ids=(),
            deterministic_order=6,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_rollback_safe_certification_diagnostic",
            diagnostic_category="rollback_safe_certification_visibility",
            severity="info",
            message="Rollback-safe evidence remains stable across continuity and integrity certification.",
            affected_certification_ids=("v4_3_continuity_rollback_safe_certification_certification",),
            affected_integrity_ids=(),
            affected_state_summary_ids=(),
            deterministic_order=7,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_state_certification_diagnostic",
            diagnostic_category="fail_visible_state_certification_visibility",
            severity="blocker",
            message="Prohibited, unsupported, blocked, stale, and conflicting governance states are certified as fail-visible evidence.",
            affected_certification_ids=certification_ids,
            affected_integrity_ids=(),
            affected_state_summary_ids=state_ids,
            deterministic_order=8,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_non_authorization_diagnostic",
            diagnostic_category="non_authorization_boundary_visibility",
            severity="prohibited",
            message="Continuity certification certifies enabled_orchestration_authorization_count equals 0.",
            affected_certification_ids=certification_ids,
            affected_integrity_ids=integrity_ids,
            affected_state_summary_ids=state_ids,
            deterministic_order=9,
        ),
        ContinuityCertificationDiagnostic(
            diagnostic_id="v4_3_non_execution_non_decision_diagnostic",
            diagnostic_category="non_execution_non_decision_boundary_visibility",
            severity="prohibited",
            message="Continuity certification certifies execution, decision, recommendation, coordination, transition, policy, and capability counts remain 0.",
            affected_certification_ids=certification_ids,
            affected_integrity_ids=integrity_ids,
            affected_state_summary_ids=state_ids,
            deterministic_order=10,
        ),
    )


def default_continuity_certification_explainability() -> tuple[ContinuityCertificationExplainability, ...]:
    affected = CERTIFICATION_LAYER_IDS
    return (
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_non_executable_explanation",
            explanation_category="orchestration_non_executable",
            summary="Orchestration remains non-executable because Phase 8 certifies governance evidence only.",
            affected_reference_ids=affected,
            deterministic_order=1,
        ),
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_authorization_unavailable_explanation",
            explanation_category="orchestration_authorization_unavailable",
            summary="Orchestration authorization remains unavailable because certification cannot approve execution or readiness.",
            affected_reference_ids=affected,
            deterministic_order=2,
        ),
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_governance_consistency_explanation",
            explanation_category="governance_consistency_matters",
            summary="Governance consistency matters because cross-layer evidence must remain auditable before any future governance modeling can rely on it.",
            affected_reference_ids=affected,
            deterministic_order=3,
        ),
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_lineage_explanation",
            explanation_category="lineage_continuity_matters",
            summary="Lineage continuity matters because each orchestration governance layer must preserve deterministic source ancestry.",
            affected_reference_ids=affected,
            deterministic_order=4,
        ),
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_provenance_explanation",
            explanation_category="provenance_continuity_matters",
            summary="Provenance continuity matters because certification must preserve evidence origin without production consumption.",
            affected_reference_ids=affected,
            deterministic_order=5,
        ),
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_replay_safe_explanation",
            explanation_category="replay_safe_evidence_matters",
            summary="Replay-safe evidence matters because certification must produce stable deterministic outputs across repeated runs.",
            affected_reference_ids=affected,
            deterministic_order=6,
        ),
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_rollback_safe_explanation",
            explanation_category="rollback_safe_evidence_matters",
            summary="Rollback-safe evidence matters because certification must remain safe to compare across prior governance evidence snapshots.",
            affected_reference_ids=affected,
            deterministic_order=7,
        ),
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_fail_visible_explanation",
            explanation_category="fail_visible_inconsistencies_exist",
            summary="Fail-visible inconsistencies exist so stale, conflicting, missing, or broken evidence is reported rather than inferred away.",
            affected_reference_ids=affected,
            deterministic_order=8,
        ),
        ContinuityCertificationExplainability(
            explanation_id="v4_3_continuity_operational_prohibited_explanation",
            explanation_category="operational_orchestration_prohibited",
            summary="Operational orchestration remains prohibited because continuity certification does not execute, authorize, decide, route, traverse, schedule, sequence, dispatch, activate, or mutate runtime behavior.",
            affected_reference_ids=affected,
            deterministic_order=9,
        ),
    )


def default_orchestration_continuity_integrity_certification() -> OrchestrationContinuityIntegrityCertification:
    identity = default_continuity_certification_identity()
    continuity = default_continuity_certifications()
    integrity = default_integrity_certifications()
    states = default_state_certification_summaries()
    return OrchestrationContinuityIntegrityCertification(
        identity=identity,
        metadata=default_continuity_certification_metadata(identity),
        continuity_certifications=continuity,
        integrity_certifications=integrity,
        state_certification_summaries=states,
        diagnostics=default_continuity_certification_diagnostics(continuity, integrity, states),
        explainability_summaries=default_continuity_certification_explainability(),
    )


def continuity_certification_flags(
    certification: OrchestrationContinuityIntegrityCertification,
) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        certification,
        certification.identity,
        certification.metadata,
        *certification.continuity_certifications,
        *certification.integrity_certifications,
        *certification.state_certification_summaries,
        *certification.diagnostics,
        *certification.explainability_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CONTINUITY_CERTIFICATION_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_continuity_certification_flags(
    certification: OrchestrationContinuityIntegrityCertification,
) -> dict[str, bool]:
    return {key: value for key, value in continuity_certification_flags(certification).items() if value}


def continuity_certification_identity_key(
    certification: OrchestrationContinuityIntegrityCertification,
) -> str:
    identity = certification.identity
    return "|".join(
        (
            identity.schema_version,
            identity.certification_id,
            identity.certification_version,
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
            identity.governance_reference,
        )
    )


def continuity_certifications_equal(
    left: OrchestrationContinuityIntegrityCertification,
    right: OrchestrationContinuityIntegrityCertification,
) -> bool:
    return serialize_orchestration_continuity_integrity_certification(
        left
    ) == serialize_orchestration_continuity_integrity_certification(right)


def enabled_coordination_execution_count(
    certification: OrchestrationContinuityIntegrityCertification,
) -> int:
    return int(
        certification.enabled_coordination_execution_count
        or certification.orchestration_coordination_execution_enabled
        or certification.orchestration_dispatch_enabled
    )


def enabled_transition_execution_count(
    certification: OrchestrationContinuityIntegrityCertification,
) -> int:
    return int(certification.enabled_transition_execution_count or certification.orchestration_activation_enabled)


def enabled_policy_enforcement_count(
    certification: OrchestrationContinuityIntegrityCertification,
) -> int:
    return int(
        certification.enabled_policy_enforcement_count
        or certification.orchestration_authorization_enabled
        or certification.readiness_approval_enabled
    )


def enabled_operational_capability_count(
    certification: OrchestrationContinuityIntegrityCertification,
) -> int:
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


def enabled_orchestration_decision_count(
    certification: OrchestrationContinuityIntegrityCertification,
) -> int:
    return int(
        certification.enabled_orchestration_decision_count
        or certification.orchestration_decision_enabled
        or any(item.decision_enabled for item in certification.continuity_certifications)
        or any(item.decision_enabled for item in certification.integrity_certifications)
        or any(item.decision_enabled for item in certification.state_certification_summaries)
        or any(item.decision_enabled for item in certification.diagnostics)
        or any(item.decision_enabled for item in certification.explainability_summaries)
    )


def enabled_orchestration_recommendation_count(
    certification: OrchestrationContinuityIntegrityCertification,
) -> int:
    return int(
        certification.enabled_orchestration_recommendation_count
        or certification.orchestration_recommendation_enabled
        or certification.ranking_enabled
        or certification.scoring_enabled
        or certification.selection_enabled
        or certification.optimization_enabled
        or any(item.recommendation_enabled for item in certification.continuity_certifications)
        or any(item.recommendation_enabled for item in certification.integrity_certifications)
        or any(item.recommendation_enabled for item in certification.state_certification_summaries)
        or any(item.recommendation_enabled for item in certification.diagnostics)
        or any(item.recommendation_enabled for item in certification.explainability_summaries)
    )


def enabled_orchestration_authorization_count(
    certification: OrchestrationContinuityIntegrityCertification,
) -> int:
    return int(
        certification.enabled_orchestration_authorization_count
        or certification.orchestration_authorization_enabled
        or certification.readiness_approval_enabled
        or certification.implicit_authorization_enabled
        or any(item.authorization_enabled for item in certification.continuity_certifications)
        or any(item.authorization_enabled for item in certification.integrity_certifications)
        or any(item.authorization_enabled for item in certification.state_certification_summaries)
        or any(item.authorization_enabled for item in certification.diagnostics)
        or any(item.authorization_enabled for item in certification.explainability_summaries)
    )


def validate_continuity_certification_identity(
    certification: OrchestrationContinuityIntegrityCertification,
) -> dict[str, object]:
    fields = asdict(certification.identity)
    required = (
        "certification_id",
        "certification_version",
        "certification_classification",
        "source_manifest_reference",
        "source_manifest_hash_reference",
        "source_topology_reference",
        "source_topology_hash_reference",
        "source_capability_reference",
        "source_capability_hash_reference",
        "source_policy_reference",
        "source_policy_hash_reference",
        "source_transition_reference",
        "source_transition_hash_reference",
        "source_coordination_reference",
        "source_coordination_hash_reference",
        "source_diagnostics_reference",
        "source_diagnostics_hash_reference",
        "schema_version",
        "governance_reference",
        "continuity_reference",
        "integrity_reference",
        "lineage_reference",
        "provenance_reference",
        "diagnostics_reference",
        "explainability_reference",
        "replay_reference",
        "rollback_reference",
        "non_execution_reference",
        "non_authorization_reference",
        "non_decision_reference",
    )
    missing_fields = tuple(sorted(field for field in required if not fields.get(field)))
    defaults = _default_sources()
    expected_hashes = {
        CERTIFICATION_LAYER_MANIFEST: certification.identity.source_manifest_hash_reference,
        CERTIFICATION_LAYER_TOPOLOGY: certification.identity.source_topology_hash_reference,
        CERTIFICATION_LAYER_CAPABILITY: certification.identity.source_capability_hash_reference,
        CERTIFICATION_LAYER_POLICY: certification.identity.source_policy_hash_reference,
        CERTIFICATION_LAYER_TRANSITION: certification.identity.source_transition_hash_reference,
        CERTIFICATION_LAYER_COORDINATION: certification.identity.source_coordination_hash_reference,
        CERTIFICATION_LAYER_DIAGNOSTICS: certification.identity.source_diagnostics_hash_reference,
    }
    hash_mismatches = tuple(
        sorted(
            layer_id
            for layer_id, (_reference, source_hash) in defaults.items()
            if expected_hashes[layer_id] != source_hash
        )
    )
    return {
        "valid": len(missing_fields) == 0 and len(hash_mismatches) == 0,
        "missing_identity_fields": missing_fields,
        "source_hash_mismatches": hash_mismatches,
        "identity_key": continuity_certification_identity_key(certification),
        "certification_id": certification.identity.certification_id,
        "schema_version": certification.identity.schema_version,
        "descriptive_only": certification.identity.descriptive_only,
        "non_executable": certification.identity.non_executable,
        "non_authorizing": certification.identity.non_authorizing,
        "non_decisioning": certification.identity.non_decisioning,
    }


def validate_continuity_certifications(
    certification: OrchestrationContinuityIntegrityCertification,
) -> dict[str, object]:
    certification_ids = tuple(item.certification_id for item in certification.continuity_certifications)
    duplicate_ids = tuple(
        sorted(value for value in set(certification_ids) if certification_ids.count(value) > 1)
    )
    types = tuple(item.certification_type for item in certification.continuity_certifications)
    missing_types = tuple(
        sorted(value for value in CONTINUITY_CERTIFICATION_TYPES if value not in types)
    )
    gap_ids = _sorted_unique(
        gap_id for item in certification.continuity_certifications for gap_id in item.continuity_gap_ids
    )
    integrity_failure_ids = _sorted_unique(
        failure_id for item in certification.continuity_certifications for failure_id in item.integrity_failure_ids
    )
    non_descriptive = tuple(
        sorted(item.certification_id for item in certification.continuity_certifications if not item.descriptive_only)
    )
    enabled = tuple(
        sorted(
            item.certification_id
            for item in certification.continuity_certifications
            if item.authorization_enabled
            or item.execution_enabled
            or item.activation_enabled
            or item.decision_enabled
            or item.recommendation_enabled
            or item.planner_integration_enabled
            or item.production_consumption_enabled
        )
    )
    return {
        "valid": (
            len(duplicate_ids) == 0
            and len(missing_types) == 0
            and len(gap_ids) == 0
            and len(integrity_failure_ids) == 0
            and len(non_descriptive) == 0
            and len(enabled) == 0
        ),
        "duplicate_certification_ids": duplicate_ids,
        "missing_certification_types": missing_types,
        "continuity_gap_ids": gap_ids,
        "integrity_failure_ids": integrity_failure_ids,
        "continuity_gap_count": len(gap_ids),
        "integrity_failure_count": len(integrity_failure_ids),
        "non_descriptive_certification_ids": non_descriptive,
        "enabled_certification_ids": enabled,
        "continuity_certification_count": len(certification.continuity_certifications),
        "replay_safe_certification_status": all(item.replay_safe for item in certification.continuity_certifications),
        "rollback_safe_certification_status": all(
            item.rollback_safe for item in certification.continuity_certifications
        ),
        "lineage_consistency_visible": any(
            item.certification_type == "lineage_continuity" and item.lineage_safe
            for item in certification.continuity_certifications
        ),
        "provenance_consistency_visible": any(
            item.certification_type == "provenance_continuity" and item.provenance_safe
            for item in certification.continuity_certifications
        ),
        "governance_consistency_visible": any(
            item.certification_type == "governance_continuity" and item.governance_consistent
            for item in certification.continuity_certifications
        ),
    }


def validate_integrity_certifications(
    certification: OrchestrationContinuityIntegrityCertification,
) -> dict[str, object]:
    integrity_ids = tuple(item.integrity_id for item in certification.integrity_certifications)
    duplicate_ids = tuple(sorted(value for value in set(integrity_ids) if integrity_ids.count(value) > 1))
    missing_layers = tuple(
        sorted(
            layer_id
            for layer_id in CERTIFICATION_LAYER_IDS
            if layer_id not in {item.layer_id for item in certification.integrity_certifications}
        )
    )
    hash_mismatch_ids = tuple(
        sorted(
            item.integrity_id
            for item in certification.integrity_certifications
            if item.expected_hash_reference != item.actual_hash_reference
        )
    )
    failure_ids = _sorted_unique(
        failure_id for item in certification.integrity_certifications for failure_id in item.integrity_failure_ids
    )
    gap_ids = _sorted_unique(
        gap_id for item in certification.integrity_certifications for gap_id in item.continuity_gap_ids
    )
    enabled = tuple(
        sorted(
            item.integrity_id
            for item in certification.integrity_certifications
            if item.authorization_enabled
            or item.execution_enabled
            or item.activation_enabled
            or item.decision_enabled
            or item.recommendation_enabled
            or item.planner_integration_enabled
            or item.production_consumption_enabled
        )
    )
    return {
        "valid": (
            len(duplicate_ids) == 0
            and len(missing_layers) == 0
            and len(hash_mismatch_ids) == 0
            and len(failure_ids) == 0
            and len(gap_ids) == 0
            and len(enabled) == 0
        ),
        "duplicate_integrity_ids": duplicate_ids,
        "missing_integrity_layers": missing_layers,
        "hash_mismatch_ids": hash_mismatch_ids,
        "integrity_failure_ids": failure_ids,
        "continuity_gap_ids": gap_ids,
        "integrity_failure_count": len(failure_ids) + len(hash_mismatch_ids),
        "continuity_gap_count": len(gap_ids),
        "enabled_integrity_ids": enabled,
        "integrity_certification_count": len(certification.integrity_certifications),
        "cross_layer_integrity_visible": len(certification.integrity_certifications) == len(CERTIFICATION_LAYER_IDS),
        "replay_safe_certification_status": all(item.replay_safe for item in certification.integrity_certifications),
        "rollback_safe_certification_status": all(
            item.rollback_safe for item in certification.integrity_certifications
        ),
        "governance_consistency_visible": all(
            item.governance_consistent for item in certification.integrity_certifications
        ),
    }


def validate_state_certification_visibility(
    certification: OrchestrationContinuityIntegrityCertification,
) -> dict[str, object]:
    summaries_by_type = {item.state_type: item for item in certification.state_certification_summaries}
    missing_state_types = tuple(
        sorted(state_type for state_type in CERTIFICATION_STATE_TYPES if state_type not in summaries_by_type)
    )
    enabled = tuple(
        sorted(
            item.state_summary_id
            for item in certification.state_certification_summaries
            if item.authorization_enabled
            or item.execution_enabled
            or item.decision_enabled
            or item.recommendation_enabled
            or item.repair_enabled
            or item.inference_enabled
        )
    )
    return {
        "valid": len(missing_state_types) == 0 and len(enabled) == 0,
        "missing_state_types": missing_state_types,
        "enabled_state_summary_ids": enabled,
        "prohibited_state_certification_count": summaries_by_type[CERTIFICATION_STATE_PROHIBITED].certification_count,
        "unsupported_state_certification_count": summaries_by_type[
            CERTIFICATION_STATE_UNSUPPORTED
        ].certification_count,
        "blocked_state_certification_count": summaries_by_type[CERTIFICATION_STATE_BLOCKED].certification_count,
        "stale_state_certification_count": summaries_by_type[CERTIFICATION_STATE_STALE].certification_count,
        "conflicting_state_certification_count": summaries_by_type[
            CERTIFICATION_STATE_CONFLICTING
        ].certification_count,
        "prohibited_state_certification_visible": summaries_by_type[
            CERTIFICATION_STATE_PROHIBITED
        ].certification_count
        > 0,
        "unsupported_state_certification_visible": summaries_by_type[
            CERTIFICATION_STATE_UNSUPPORTED
        ].certification_count
        > 0,
        "blocked_state_certification_visible": summaries_by_type[CERTIFICATION_STATE_BLOCKED].certification_count
        > 0,
        "stale_state_certification_visible": summaries_by_type[CERTIFICATION_STATE_STALE].certification_count > 0,
        "conflicting_state_certification_visible": summaries_by_type[
            CERTIFICATION_STATE_CONFLICTING
        ].certification_count
        > 0,
    }


def validate_continuity_explainability(
    certification: OrchestrationContinuityIntegrityCertification,
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


def validate_continuity_non_execution_authorization_decision(
    certification: OrchestrationContinuityIntegrityCertification,
) -> dict[str, object]:
    enabled_flags = enabled_continuity_certification_flags(certification)
    coordination_count = enabled_coordination_execution_count(certification)
    transition_count = enabled_transition_execution_count(certification)
    policy_count = enabled_policy_enforcement_count(certification)
    operational_count = enabled_operational_capability_count(certification)
    decision_count = enabled_orchestration_decision_count(certification)
    recommendation_count = enabled_orchestration_recommendation_count(certification)
    authorization_count = enabled_orchestration_authorization_count(certification)
    return {
        "valid": (
            len(enabled_flags) == 0
            and coordination_count == 0
            and transition_count == 0
            and policy_count == 0
            and operational_count == 0
            and decision_count == 0
            and recommendation_count == 0
            and authorization_count == 0
            and certification.non_executable
            and certification.non_authorizing
            and certification.non_decisioning
            and certification.descriptive_only
        ),
        "enabled_continuity_certification_flags": enabled_flags,
        "enabled_coordination_execution_count": coordination_count,
        "enabled_transition_execution_count": transition_count,
        "enabled_policy_enforcement_count": policy_count,
        "enabled_operational_capability_count": operational_count,
        "enabled_orchestration_decision_count": decision_count,
        "enabled_orchestration_recommendation_count": recommendation_count,
        "enabled_orchestration_authorization_count": authorization_count,
        "non_executable": certification.non_executable,
        "non_authorizing": certification.non_authorizing,
        "non_decisioning": certification.non_decisioning,
        "descriptive_only": certification.descriptive_only,
        "orchestration_execution_disabled": not certification.orchestration_execution_enabled,
        "orchestration_authorization_disabled": not certification.orchestration_authorization_enabled,
        "readiness_approval_disabled": not certification.readiness_approval_enabled,
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
        "orchestration_runtime_behavior_disabled": (
            not certification.orchestration_runtime_behavior_enabled
        ),
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


def build_continuity_integrity_certification_diagnostics(
    certification: OrchestrationContinuityIntegrityCertification | None = None,
) -> dict[str, Any]:
    source = certification or default_orchestration_continuity_integrity_certification()
    identity = validate_continuity_certification_identity(source)
    continuity = validate_continuity_certifications(source)
    integrity = validate_integrity_certifications(source)
    states = validate_state_certification_visibility(source)
    explainability = validate_continuity_explainability(source)
    non_execution = validate_continuity_non_execution_authorization_decision(source)
    diagnostics_aggregation = default_orchestration_diagnostics_aggregation()
    diagnostics_validation = build_orchestration_diagnostics_aggregation_diagnostics(diagnostics_aggregation)
    diagnostics_non_execution = validate_diagnostics_aggregation_non_execution_and_non_decision(
        diagnostics_aggregation
    )
    return {
        "continuity_integrity_certification_hash": hash_orchestration_continuity_integrity_certification(source),
        "continuity_certification_hashes": [
            hash_continuity_certification_record(item) for item in source.continuity_certifications
        ],
        "integrity_certification_hashes": [
            hash_integrity_certification_record(item) for item in source.integrity_certifications
        ],
        "state_certification_hashes": [
            hash_certification_state_summary(item) for item in source.state_certification_summaries
        ],
        "diagnostic_hashes": [
            hash_continuity_certification_diagnostic(item) for item in source.diagnostics
        ],
        "explainability_hashes": [
            hash_continuity_certification_explainability(item)
            for item in source.explainability_summaries
        ],
        "identity_validation": identity,
        "continuity_validation": continuity,
        "integrity_validation": integrity,
        "state_certification_validation": states,
        "explainability_validation": explainability,
        "non_execution_authorization_decision_validation": non_execution,
        "phase_7_diagnostics_validation": diagnostics_validation,
        "phase_7_non_execution_validation": diagnostics_non_execution,
        "continuity_certification_count": len(source.continuity_certifications),
        "integrity_certification_count": len(source.integrity_certifications),
        "continuity_gap_count": continuity["continuity_gap_count"] + integrity["continuity_gap_count"],
        "integrity_failure_count": continuity["integrity_failure_count"] + integrity["integrity_failure_count"],
        "prohibited_state_certification_count": states["prohibited_state_certification_count"],
        "unsupported_state_certification_count": states["unsupported_state_certification_count"],
        "blocked_state_certification_count": states["blocked_state_certification_count"],
        "stale_state_certification_count": states["stale_state_certification_count"],
        "conflicting_state_certification_count": states["conflicting_state_certification_count"],
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
        "diagnostics_are_descriptive_only": all(item.descriptive_only for item in source.diagnostics),
        "explainability_is_descriptive_only": all(
            item.descriptive_only for item in source.explainability_summaries
        ),
        "explicit_prohibitions": EXPLICIT_ORCHESTRATION_CONTINUITY_PROHIBITIONS,
    }
