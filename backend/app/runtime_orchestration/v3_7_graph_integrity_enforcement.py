"""Deterministic integrity enforcement over v3.7 planning evidence."""

from __future__ import annotations

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_integrity_findings import build_v3_7_graph_integrity_findings
from .v3_7_graph_integrity_models import (
    V3_7_GRAPH_INTEGRITY_PHASE_ID,
    V37_INTEGRITY_OUTCOME_BLOCKED,
    V37_INTEGRITY_OUTCOME_INVALID,
    V37_INTEGRITY_OUTCOME_VALID,
    V37GraphIntegrityEnforcementIdentity,
    V37GraphIntegrityEnforcementResult,
    V37GraphIntegrityPolicy,
    V37GraphIntegrityPolicyMetadata,
    V37GraphIntegrityReplayEvidence,
)
from .v3_7_graph_integrity_policies import build_v3_7_graph_integrity_policy
from .v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from .v3_7_graph_intelligence_audit import (
    V37_GRAPH_INTELLIGENCE_AUDIT_STABLE,
    audit_v3_7_graph_intelligence,
)
from .v3_7_graph_intelligence_explainability import (
    V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_intelligence,
)
from .v3_7_graph_intelligence_models import (
    V37GraphPlanningIntelligenceAggregation,
    hash_v3_7_graph_planning_intelligence_aggregation,
)
from .v3_7_graph_intelligence_provenance import (
    V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED,
    audit_v3_7_graph_intelligence_provenance,
)
from .v3_7_graph_intelligence_replay import validate_v3_7_graph_intelligence_replay_evidence
from .v3_7_graph_intelligence_validation import (
    V37_GRAPH_INTELLIGENCE_VALIDATION_STABLE,
    validate_v3_7_graph_intelligence,
)
from .v3_7_graph_models import default_v3_7_graph_provenance


DEFAULT_V37_GRAPH_INTEGRITY_ENFORCEMENT_ID = "v3_7_graph_integrity_enforcement_default"


def build_v3_7_graph_integrity_enforcement_identity(
    policy_id: str,
    aggregation_id: str,
) -> V37GraphIntegrityEnforcementIdentity:
    key_payload = {
        "enforcement_id": DEFAULT_V37_GRAPH_INTEGRITY_ENFORCEMENT_ID,
        "policy_id": policy_id,
        "aggregation_id": aggregation_id,
        "enforcement_version": "v3.7",
        "phase_id": V3_7_GRAPH_INTEGRITY_PHASE_ID,
    }
    return V37GraphIntegrityEnforcementIdentity(
        enforcement_id=DEFAULT_V37_GRAPH_INTEGRITY_ENFORCEMENT_ID,
        policy_id=policy_id,
        aggregation_id=aggregation_id,
        enforcement_version="v3.7",
        phase_id=V3_7_GRAPH_INTEGRITY_PHASE_ID,
        stable_identity_key=deterministic_hash(key_payload),
    )


def graph_integrity_enforcement_identity_key(identity: V37GraphIntegrityEnforcementIdentity) -> str:
    return deterministic_hash(
        {
            "enforcement_id": identity.enforcement_id,
            "policy_id": identity.policy_id,
            "aggregation_id": identity.aggregation_id,
            "enforcement_version": identity.enforcement_version,
            "phase_id": identity.phase_id,
        }
    )


def graph_integrity_enforcement_identities_are_unique(
    identities: tuple[V37GraphIntegrityEnforcementIdentity, ...],
) -> bool:
    keys = [identity.stable_identity_key for identity in identities]
    return len(keys) == len(set(keys))


def enforce_v3_7_graph_planning_integrity(
    aggregation: V37GraphPlanningIntelligenceAggregation | None = None,
    policy: V37GraphIntegrityPolicy | None = None,
) -> V37GraphIntegrityEnforcementResult:
    planning_intelligence = aggregation or build_v3_7_graph_planning_intelligence_aggregation()
    integrity_policy = policy or build_v3_7_graph_integrity_policy()
    identity = build_v3_7_graph_integrity_enforcement_identity(
        integrity_policy.identity.policy_id,
        planning_intelligence.identity.aggregation_id,
    )
    validation = validate_v3_7_graph_intelligence((planning_intelligence,))
    audit = audit_v3_7_graph_intelligence(planning_intelligence)
    provenance = audit_v3_7_graph_intelligence_provenance(planning_intelligence)
    explainability = explain_v3_7_graph_intelligence(planning_intelligence)
    replay = validate_v3_7_graph_intelligence_replay_evidence(planning_intelligence)
    source_ids = tuple(sorted(source.source_id for source in planning_intelligence.evidence_sources)) + (
        planning_intelligence.identity.aggregation_id,
    )
    source_types = tuple(sorted(source.source_type for source in planning_intelligence.evidence_sources)) + (
        "aggregation",
    )
    integrity_totals = _integrity_totals(planning_intelligence, validation, audit, provenance, explainability, replay)
    findings = build_v3_7_graph_integrity_findings(integrity_totals, source_ids)
    active_blocking_findings = tuple(
        finding.finding_id for finding in findings if finding.blocks_validation or finding.active_violation
    )
    continuity_hashes = tuple(
        sorted(
            set(planning_intelligence.continuity_hash_references)
            | {hash_v3_7_graph_planning_intelligence_aggregation(planning_intelligence)}
            | {validation.deterministic_validation_hash}
            | {audit.deterministic_audit_hash}
            | {provenance.deterministic_provenance_hash}
            | {explainability.deterministic_explainability_hash}
        )
    )
    replay_evidence = (
        V37GraphIntegrityReplayEvidence(
            replay_evidence_id="v3_7_graph_integrity_replay_evidence_default",
            enforcement_id=identity.enforcement_id,
            policy_id=integrity_policy.identity.policy_id,
            evidence_source_references=source_ids,
            integrity_finding_references=tuple(finding.finding_id for finding in findings),
            blocked_finding_references=active_blocking_findings,
            provenance_references=tuple(
                sorted(
                    set(source.provenance_references[0] for source in planning_intelligence.evidence_sources if source.provenance_references)
                    | {planning_intelligence.provenance.provenance_id}
                    | {integrity_policy.provenance.provenance_id}
                )
            ),
            explainability_references=tuple(
                sorted(
                    set(planning_intelligence.explainability_reference_ids)
                    | set(reference for source in planning_intelligence.evidence_sources for reference in source.explainability_references)
                    | {"v3_7_graph_integrity_explainability"}
                )
            ),
            continuity_hashes=continuity_hashes,
            non_executable_replay_evidence=True,
            runtime_replay=False,
            execution_authorization=False,
        ),
    )
    outcome = _outcome_from_findings(findings, validation.validation_status, audit.audit_status)
    return V37GraphIntegrityEnforcementResult(
        identity=identity,
        policy=integrity_policy,
        metadata=(
            V37GraphIntegrityPolicyMetadata("enforcement_semantics", "deterministic_planning_integrity_validation"),
            V37GraphIntegrityPolicyMetadata("runtime_capability", "none"),
            V37GraphIntegrityPolicyMetadata("execution_boundary", "valid_integrity_does_not_authorize_execution"),
        ),
        evidence_source_references=source_ids,
        evidence_source_types=source_types,
        enforcement_outcome=outcome,
        findings=findings,
        replay_evidence=replay_evidence,
        rollback_continuity_references=planning_intelligence.rollback_continuity_references,
        provenance=default_v3_7_graph_provenance(identity.enforcement_id, "graph_planning_integrity_enforcement"),
        explainability_reference_ids=("v3_7_graph_integrity_explainability",),
        continuity_hash_references=continuity_hashes,
    )


def _integrity_totals(aggregation, validation, audit, provenance, explainability, replay) -> dict[str, int | bool]:
    execution_boundary_violation = _execution_boundary_violation(aggregation)
    return {
        "invalid_integrity_count": 0 if validation.valid and audit.valid else 1,
        "blocked_integrity_count": 0,
        "warning_integrity_count": 0,
        "continuity_violation_count": 0
        if all(
            (
                validation.deterministic_serialization_stable,
                validation.deterministic_hash_stable,
                validation.replay_continuity_preserved,
                validation.rollback_continuity_preserved,
                audit.evidence_source_continuity_preserved,
                audit.governance_aggregation_continuity_preserved,
                audit.compatibility_aggregation_continuity_preserved,
                audit.evaluation_aggregation_continuity_preserved,
                audit.session_aggregation_continuity_preserved,
                audit.scenario_aggregation_continuity_preserved,
            )
        )
        else 1,
        "provenance_violation_count": 0
        if provenance.provenance_status == V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED
        else 1,
        "explainability_violation_count": 0
        if explainability.explainability_status == V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE
        else 1,
        "replay_violation_count": 0 if replay["replay_continuity_preserved"] else 1,
        "rollback_violation_count": 0 if replay["rollback_continuity_preserved"] else 1,
        "execution_boundary_violation_count": 1 if execution_boundary_violation else 0,
        "hidden_prohibited_state_count": validation.hidden_prohibited_finding_count,
        "hidden_unsupported_state_count": validation.hidden_unsupported_finding_count,
        "hidden_unknown_state_count": validation.hidden_unknown_finding_count,
    }


def _outcome_from_findings(findings, validation_status: str, audit_status: str) -> str:
    if any(finding.blocks_validation for finding in findings):
        return V37_INTEGRITY_OUTCOME_BLOCKED
    if validation_status != V37_GRAPH_INTELLIGENCE_VALIDATION_STABLE:
        return V37_INTEGRITY_OUTCOME_INVALID
    if audit_status != V37_GRAPH_INTELLIGENCE_AUDIT_STABLE:
        return V37_INTEGRITY_OUTCOME_INVALID
    return V37_INTEGRITY_OUTCOME_VALID


def _execution_boundary_violation(aggregation: V37GraphPlanningIntelligenceAggregation) -> bool:
    blocked_phrases = (
        "should execute",
        "recommend execution",
        "select runtime path",
        "authorize orchestration",
        "rank for execution",
        "runtime guidance",
        "route graph",
        "dispatch graph",
        "schedule graph",
        "traverse graph",
    )
    return any(
        (
            aggregation.graph_execution_enabled,
            aggregation.aggregation_driven_execution_enabled,
            aggregation.orchestration_selection_enabled,
            aggregation.routing_enabled,
            aggregation.scheduling_enabled,
            aggregation.dispatch_enabled,
            aggregation.graph_traversal_execution_enabled,
            aggregation.optimization_engine_enabled,
            aggregation.recommendation_enabled,
            aggregation.runtime_decision_making_enabled,
            aggregation.path_ranking_for_execution_enabled,
            aggregation.scenario_selection_for_execution_enabled,
            aggregation.executable_planning_insights_enabled,
            any(
                insight.recommends_execution
                or insight.selects_runtime_path
                or insight.authorizes_orchestration
                or any(phrase in insight.summary.lower() for phrase in blocked_phrases)
                for insight in aggregation.insights
            ),
            any(
                finding.execution_recommendation
                or finding.runtime_path_selection
                or any(phrase in finding.summary.lower() for phrase in blocked_phrases)
                for finding in aggregation.findings
            ),
        )
    )
