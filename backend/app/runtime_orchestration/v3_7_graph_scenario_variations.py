"""Deterministic planning scenario construction and hypothetical variations."""

from __future__ import annotations

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_models import default_v3_7_graph_provenance
from .v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session
from .v3_7_graph_scenario_comparison import build_v3_7_graph_scenario_comparison_evidence
from .v3_7_graph_scenario_identity import build_v3_7_graph_scenario_identity
from .v3_7_graph_scenario_models import (
    V37_SCENARIO_STATUS_BLOCKED,
    V37_SCENARIO_STATUS_COMPARISON_READY,
    V37_SCENARIO_STATUS_EVALUATED,
    V37_SCENARIO_STATUS_PROHIBITED,
    V37_SCENARIO_STATUS_UNKNOWN,
    V37_SCENARIO_STATUS_UNSUPPORTED,
    V37GraphPlanningScenario,
    V37GraphScenarioAuditTrailEntry,
    V37GraphScenarioMetadata,
    V37GraphScenarioReplayEvidence,
    V37GraphScenarioVariation,
)


def build_v3_7_graph_planning_scenario() -> V37GraphPlanningScenario:
    session = build_v3_7_graph_planning_session()
    identity = build_v3_7_graph_scenario_identity(
        session.identity.session_id,
        session.identity.graph_id,
    )
    snapshot_ids = tuple(snapshot.snapshot_id for snapshot in session.snapshots)
    evaluation_references = tuple(
        sorted(
            {item.evidence_id for item in session.evaluation_evidence}
            | {reference for item in session.evaluation_evidence for reference in item.evaluation_trace_references}
            | {reference for item in session.evaluation_evidence for reference in item.evaluation_finding_references}
        )
    )
    variations = build_v3_7_graph_scenario_variations(identity.scenario_id)
    comparisons = build_v3_7_graph_scenario_comparison_evidence(identity.scenario_id, variations)
    replay_evidence = (
        V37GraphScenarioReplayEvidence(
            replay_evidence_id="v3_7_graph_scenario_replay_evidence_default",
            scenario_id=identity.scenario_id,
            variation_references=tuple(variation.variation_id for variation in variations),
            graph_snapshot_references=snapshot_ids,
            evaluation_references=evaluation_references,
            provenance_references=tuple(
                sorted(
                    {session.provenance.provenance_id}
                    | {variation.provenance.provenance_id for variation in variations}
                )
            ),
            explainability_references=("v3_7_graph_scenario_explainability",),
            continuity_hashes=tuple(
                sorted(
                    set(session.continuity_hash_references)
                    | {comparison.deterministic_comparison_hash for comparison in comparisons}
                    | {deterministic_hash(variation.variation_id) for variation in variations}
                )
            ),
            rollback_references=tuple(
                sorted(
                    {reference for item in session.rollback_evidence for reference in item.rollback_reference_ids}
                    | {item.rollback_evidence_id for item in session.rollback_evidence}
                )
            ),
        ),
    )
    return V37GraphPlanningScenario(
        identity=identity,
        status=V37_SCENARIO_STATUS_COMPARISON_READY,
        metadata=(
            V37GraphScenarioMetadata("scenario_semantics", "deterministic_hypothetical_planning_artifact"),
            V37GraphScenarioMetadata("variation_semantics", "structural_hypothetical_evidence_only"),
            V37GraphScenarioMetadata("comparison_semantics", "comparison_does_not_select_or_execute"),
            V37GraphScenarioMetadata("runtime_capability", "none"),
        ),
        planning_session_references=(session.identity.session_id,),
        graph_snapshot_references=snapshot_ids,
        variations=variations,
        evaluation_evidence_references=evaluation_references,
        comparison_evidence=comparisons,
        replay_evidence=replay_evidence,
        rollback_continuity_references=tuple(
            sorted(reference for item in session.rollback_evidence for reference in item.rollback_reference_ids)
        ),
        audit_trail=build_v3_7_graph_scenario_audit_trail(identity.scenario_id),
        provenance=default_v3_7_graph_provenance(identity.scenario_id, "graph_planning_scenario"),
        explainability_reference_ids=("v3_7_graph_scenario_explainability",),
        continuity_hash_references=tuple(
            sorted(
                set(session.continuity_hash_references)
                | {comparison.deterministic_comparison_hash for comparison in comparisons}
            )
        ),
    )


def build_v3_7_graph_scenario_variations(
    scenario_id: str | None = None,
) -> tuple[V37GraphScenarioVariation, ...]:
    session = build_v3_7_graph_planning_session()
    resolved_scenario_id = scenario_id or "v3_7_graph_planning_scenario_default"
    snapshot_id = session.snapshots[0].snapshot_id
    baseline = "v3_7_graph_planning_scenario_baseline"
    specs = (
        (
            "structural_relationship_alternative",
            "hypothetical_structural_relationship",
            "supported",
            "compatible",
            "compatible",
        ),
        (
            "governance_classification_alternative",
            "hypothetical_governance_boundary",
            "governance_restricted",
            "governance_restricted",
            "governance_restricted",
        ),
        (
            "compatibility_classification_alternative",
            "hypothetical_compatibility_boundary",
            "compatibility_restricted",
            "compatibility_restricted",
            "compatibility_restricted",
        ),
        (
            "evaluation_chain_alternative",
            "hypothetical_evaluation_chain",
            "supported",
            "compatible",
            "experimental",
        ),
        (
            "prohibited_state_alternative",
            "hypothetical_prohibited_state",
            "prohibited",
            "prohibited",
            "prohibited",
        ),
        (
            "unsupported_state_alternative",
            "hypothetical_unsupported_state",
            "unsupported",
            "unsupported",
            "unsupported",
        ),
        (
            "unknown_state_alternative",
            "hypothetical_unknown_state",
            "unknown",
            "unknown",
            "unknown",
        ),
    )
    variations = []
    for order, (
        variation_type,
        relationship,
        governance_classification,
        compatibility_classification,
        evaluation_classification,
    ) in enumerate(specs, start=1):
        variation_id = f"v3_7_graph_scenario_variation_{order:04d}_{variation_type}"
        variations.append(
            V37GraphScenarioVariation(
                variation_id=variation_id,
                variation_type=variation_type,
                scenario_id=resolved_scenario_id,
                planning_session_reference=session.identity.session_id,
                graph_snapshot_reference=snapshot_id,
                baseline_reference=baseline,
                hypothetical_relationship=relationship,
                governance_classification=governance_classification,
                compatibility_classification=compatibility_classification,
                evaluation_classification=evaluation_classification,
                evidence_references=(
                    session.identity.session_id,
                    snapshot_id,
                    relationship,
                    governance_classification,
                    compatibility_classification,
                    evaluation_classification,
                ),
                provenance=default_v3_7_graph_provenance(variation_id, "graph_planning_scenario_variation"),
            )
        )
    return tuple(variations)


def build_v3_7_graph_scenario_audit_trail(
    scenario_id: str,
) -> tuple[V37GraphScenarioAuditTrailEntry, ...]:
    entries = (
        _entry(1, "scenario_status", V37_SCENARIO_STATUS_COMPARISON_READY, scenario_id, "scenario comparison evidence is structurally ready"),
        _entry(2, "blocked_visibility", V37_SCENARIO_STATUS_BLOCKED, scenario_id, "blocked scenario states remain fail-visible when present"),
        _entry(3, "unsupported_visibility", V37_SCENARIO_STATUS_UNSUPPORTED, scenario_id, "unsupported scenario states remain fail-visible"),
        _entry(4, "prohibited_visibility", V37_SCENARIO_STATUS_PROHIBITED, scenario_id, "prohibited scenario states remain fail-visible"),
        _entry(5, "unknown_visibility", V37_SCENARIO_STATUS_UNKNOWN, scenario_id, "unknown scenario states remain fail-visible"),
        _entry(6, "evaluation_visibility", V37_SCENARIO_STATUS_EVALUATED, scenario_id, "scenario evaluation evidence remains structural"),
        _entry(7, "non_execution_boundary", V37_SCENARIO_STATUS_COMPARISON_READY, scenario_id, "scenario contains hypothetical planning evidence only"),
    )
    return entries


def _entry(
    order: int,
    audit_type: str,
    status: str,
    scenario_id: str,
    message: str,
) -> V37GraphScenarioAuditTrailEntry:
    return V37GraphScenarioAuditTrailEntry(
        audit_entry_id=f"v3_7_graph_scenario_audit_{order:04d}_{audit_type}",
        audit_order=order,
        audit_type=audit_type,
        scenario_status=status,
        subject_type="graph_planning_scenario",
        subject_id=scenario_id,
        message=message,
        evidence_references=(scenario_id, audit_type),
        fail_visible=True,
        hidden=False,
    )
