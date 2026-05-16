"""Deterministic graph planning intelligence aggregation construction."""

from __future__ import annotations

from collections import Counter

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_compatibility_models import hash_v3_7_compatibility_map
from .v3_7_graph_compatibility_rules import build_v3_7_graph_compatibility_map
from .v3_7_graph_evaluation_models import hash_v3_7_graph_evaluation_chain
from .v3_7_graph_evaluation_replay import build_v3_7_graph_evaluation_replay_packets
from .v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain
from .v3_7_graph_governance_models import hash_v3_7_governance_map
from .v3_7_graph_governance_rules import build_v3_7_graph_governance_map
from .v3_7_graph_hashing import hash_v3_7_graph
from .v3_7_graph_intelligence_findings import build_v3_7_graph_intelligence_findings
from .v3_7_graph_intelligence_models import (
    V3_7_GRAPH_INTELLIGENCE_PHASE_ID,
    V37GraphIntelligenceEvidenceSource,
    V37GraphIntelligenceIdentity,
    V37GraphIntelligenceMetadata,
    V37GraphIntelligenceReplayEvidence,
    V37GraphIntelligenceTotals,
    V37GraphPlanningInsight,
    V37GraphPlanningIntelligenceAggregation,
)
from .v3_7_graph_models import default_v3_7_graph_provenance, default_v3_7_orchestration_planning_graph
from .v3_7_graph_planning_session_models import hash_v3_7_graph_planning_session
from .v3_7_graph_planning_session_snapshots import build_v3_7_graph_planning_session
from .v3_7_graph_scenario_models import hash_v3_7_graph_planning_scenario
from .v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


DEFAULT_V37_GRAPH_INTELLIGENCE_AGGREGATION_ID = "v3_7_graph_planning_intelligence_aggregation_default"


def build_v3_7_graph_intelligence_identity(graph_id: str | None = None) -> V37GraphIntelligenceIdentity:
    source_graph_id = graph_id or default_v3_7_orchestration_planning_graph().identity.graph_id
    key_payload = {
        "aggregation_id": DEFAULT_V37_GRAPH_INTELLIGENCE_AGGREGATION_ID,
        "aggregation_version": "v3.7",
        "graph_id": source_graph_id,
        "phase_id": V3_7_GRAPH_INTELLIGENCE_PHASE_ID,
    }
    return V37GraphIntelligenceIdentity(
        aggregation_id=DEFAULT_V37_GRAPH_INTELLIGENCE_AGGREGATION_ID,
        graph_id=source_graph_id,
        aggregation_version="v3.7",
        phase_id=V3_7_GRAPH_INTELLIGENCE_PHASE_ID,
        stable_identity_key=deterministic_hash(key_payload),
    )


def graph_intelligence_identity_key(identity: V37GraphIntelligenceIdentity) -> str:
    return deterministic_hash(
        {
            "aggregation_id": identity.aggregation_id,
            "aggregation_version": identity.aggregation_version,
            "graph_id": identity.graph_id,
            "phase_id": identity.phase_id,
        }
    )


def graph_intelligence_identities_are_unique(
    identities: tuple[V37GraphIntelligenceIdentity, ...],
) -> bool:
    keys = [identity.stable_identity_key for identity in identities]
    return len(keys) == len(set(keys))


def build_v3_7_graph_planning_intelligence_aggregation() -> V37GraphPlanningIntelligenceAggregation:
    graph = default_v3_7_orchestration_planning_graph()
    governance = build_v3_7_graph_governance_map(graph)
    compatibility = build_v3_7_graph_compatibility_map(governance)
    evaluation = build_v3_7_graph_evaluation_chain()
    evaluation_replay_packets = build_v3_7_graph_evaluation_replay_packets(evaluation)
    session = build_v3_7_graph_planning_session()
    scenario = build_v3_7_graph_planning_scenario()
    identity = build_v3_7_graph_intelligence_identity(graph.identity.graph_id)
    evidence_sources = _evidence_sources(graph, governance, compatibility, evaluation, session, scenario)
    source_totals = _source_totals(governance, compatibility, evaluation, session, scenario, evaluation_replay_packets)
    totals = V37GraphIntelligenceTotals(**source_totals)
    evidence_source_ids = tuple(source.source_id for source in evidence_sources)
    findings = build_v3_7_graph_intelligence_findings(source_totals, evidence_source_ids)
    insights = _insights(evidence_sources, findings)
    continuity_hashes = tuple(sorted(source.source_hash for source in evidence_sources))
    replay_evidence = (
        V37GraphIntelligenceReplayEvidence(
            replay_evidence_id="v3_7_graph_intelligence_replay_evidence_default",
            aggregation_id=identity.aggregation_id,
            evidence_source_references=evidence_source_ids,
            graph_evidence_references=(graph.identity.graph_id,),
            governance_evidence_references=tuple(finding.finding_id for finding in governance.findings),
            compatibility_evidence_references=tuple(finding.finding_id for finding in compatibility.findings),
            evaluation_evidence_references=tuple(finding.finding_id for finding in evaluation.findings),
            session_evidence_references=tuple(entry.audit_entry_id for entry in session.audit_trail),
            scenario_evidence_references=tuple(entry.audit_entry_id for entry in scenario.audit_trail),
            provenance_references=tuple(
                sorted(source.provenance_references[0] for source in evidence_sources if source.provenance_references)
            ),
            explainability_references=tuple(
                sorted(reference for source in evidence_sources for reference in source.explainability_references)
            ),
            continuity_hashes=continuity_hashes,
            non_executable_replay_evidence=True,
            runtime_replay=False,
            execution_authorization=False,
        ),
    )
    rollback_references = tuple(
        sorted(
            set(evaluation.continuity_evidence[0].rollback_lineage_references)
            | set(session.rollback_evidence[0].rollback_reference_ids)
            | set(scenario.rollback_continuity_references)
        )
    )
    return V37GraphPlanningIntelligenceAggregation(
        identity=identity,
        metadata=(
            V37GraphIntelligenceMetadata("aggregation_semantics", "deterministic_planning_evidence_summary"),
            V37GraphIntelligenceMetadata("insight_boundary", "summaries_do_not_recommend_execution"),
            V37GraphIntelligenceMetadata("runtime_capability", "none"),
        ),
        evidence_sources=evidence_sources,
        totals=totals,
        findings=findings,
        insights=insights,
        replay_evidence=replay_evidence,
        rollback_continuity_references=rollback_references,
        provenance=default_v3_7_graph_provenance(identity.aggregation_id, "graph_planning_intelligence_aggregation"),
        explainability_reference_ids=("v3_7_graph_intelligence_explainability",),
        continuity_hash_references=continuity_hashes,
    )


def _evidence_sources(graph, governance, compatibility, evaluation, session, scenario):
    return (
        V37GraphIntelligenceEvidenceSource(
            source_id="v3_7_intelligence_source_graph_foundations",
            source_type="graph_foundations",
            source_phase_id=graph.identity.phase_id,
            source_reference_id=graph.identity.graph_id,
            source_hash=hash_v3_7_graph(graph),
            provenance_references=(graph.provenance.provenance_id,),
            explainability_references=tuple(item.evidence_id for item in graph.explainability_evidence),
            continuity_references=tuple(item.continuity_id for item in graph.continuity_evidence),
        ),
        V37GraphIntelligenceEvidenceSource(
            source_id="v3_7_intelligence_source_governance",
            source_type="governance",
            source_phase_id=governance.governance_phase_id,
            source_reference_id=governance.graph_id,
            source_hash=hash_v3_7_governance_map(governance),
            provenance_references=tuple(domain.provenance.provenance_id for domain in governance.domains),
            explainability_references=tuple(
                reference
                for item in governance.node_classifications + governance.edge_classifications
                for reference in item.explainability_evidence_ids
            ),
            continuity_references=tuple(item.continuity_id for item in governance.continuity_evidence),
        ),
        V37GraphIntelligenceEvidenceSource(
            source_id="v3_7_intelligence_source_compatibility",
            source_type="compatibility",
            source_phase_id=compatibility.compatibility_phase_id,
            source_reference_id=compatibility.graph_id,
            source_hash=hash_v3_7_compatibility_map(compatibility),
            provenance_references=tuple(domain.provenance.provenance_id for domain in compatibility.domains),
            explainability_references=tuple(
                reference
                for item in compatibility.node_results + compatibility.edge_results
                for reference in item.explainability_evidence_ids
            ),
            continuity_references=tuple(item.continuity_id for item in compatibility.continuity_evidence),
        ),
        V37GraphIntelligenceEvidenceSource(
            source_id="v3_7_intelligence_source_evaluation",
            source_type="evaluation",
            source_phase_id=evaluation.evaluation_phase_id,
            source_reference_id=evaluation.chain_id,
            source_hash=hash_v3_7_graph_evaluation_chain(evaluation),
            provenance_references=(evaluation.provenance.provenance_id,),
            explainability_references=tuple(
                reference for step in evaluation.steps for reference in step.explainability_evidence_ids
            ),
            continuity_references=tuple(item.continuity_id for item in evaluation.continuity_evidence),
        ),
        V37GraphIntelligenceEvidenceSource(
            source_id="v3_7_intelligence_source_session",
            source_type="session",
            source_phase_id=session.identity.phase_id,
            source_reference_id=session.identity.session_id,
            source_hash=hash_v3_7_graph_planning_session(session),
            provenance_references=(session.provenance.provenance_id,),
            explainability_references=session.explainability_reference_ids,
            continuity_references=session.continuity_hash_references,
        ),
        V37GraphIntelligenceEvidenceSource(
            source_id="v3_7_intelligence_source_scenario",
            source_type="scenario",
            source_phase_id=scenario.identity.phase_id,
            source_reference_id=scenario.identity.scenario_id,
            source_hash=hash_v3_7_graph_planning_scenario(scenario),
            provenance_references=(scenario.provenance.provenance_id,),
            explainability_references=scenario.explainability_reference_ids,
            continuity_references=scenario.continuity_hash_references,
        ),
    )


def _source_totals(governance, compatibility, evaluation, session, scenario, evaluation_replay_packets) -> dict[str, int]:
    session_statuses = Counter(entry.session_status for entry in session.audit_trail)
    scenario_statuses = Counter(entry.scenario_status for entry in scenario.audit_trail)
    scenario_variation_classifications = Counter(
        classification
        for variation in scenario.variations
        for classification in (
            variation.governance_classification,
            variation.compatibility_classification,
            variation.evaluation_classification,
        )
    )
    return {
        "governance_finding_total": len(governance.findings),
        "compatibility_finding_total": len(compatibility.findings),
        "evaluation_finding_total": len(evaluation.findings),
        "session_finding_total": len(session.audit_trail),
        "scenario_finding_total": len(scenario.audit_trail) + len(scenario.variations),
        "prohibited_visibility_total": (
            sum(1 for finding in governance.findings if "prohibited" in finding.governance_classification)
            + compatibility.aggregation.prohibited_relationship_count
            + evaluation.summary.prohibited_finding_count
            + session_statuses["prohibited"]
            + scenario_statuses["prohibited"]
            + scenario_variation_classifications["prohibited"]
        ),
        "unsupported_visibility_total": (
            sum(1 for finding in governance.findings if "unsupported" in finding.governance_classification)
            + compatibility.aggregation.unsupported_relationship_count
            + evaluation.summary.unsupported_finding_count
            + session_statuses["unsupported"]
            + scenario_statuses["unsupported"]
            + scenario_variation_classifications["unsupported"]
        ),
        "unknown_visibility_total": (
            compatibility.aggregation.unknown_relationship_count
            + evaluation.summary.unknown_finding_count
            + session_statuses["unknown"]
            + scenario_statuses["unknown"]
            + scenario_variation_classifications["unknown"]
        ),
        "blocked_visibility_total": session_statuses["blocked"] + scenario_statuses["blocked"],
        "experimental_visibility_total": (
            compatibility.aggregation.experimental_relationship_count
            + evaluation.summary.experimental_finding_count
            + scenario_variation_classifications["experimental"]
        ),
        "continuity_warning_total": evaluation.summary.continuity_warning_count,
        "replay_evidence_total": len(evaluation_replay_packets) + len(session.replay_evidence) + len(scenario.replay_evidence),
        "rollback_evidence_total": len(session.rollback_evidence) + len(scenario.rollback_continuity_references),
        "provenance_evidence_total": (
            1
            + len(governance.domains)
            + len(compatibility.domains)
            + 1
            + 1
            + 1
        ),
        "explainability_evidence_total": (
            len(governance.node_classifications)
            + len(governance.edge_classifications)
            + len(compatibility.node_results)
            + len(compatibility.edge_results)
            + len(evaluation.steps)
            + len(session.explainability_reference_ids)
            + len(scenario.explainability_reference_ids)
        ),
    }


def _insights(evidence_sources, findings) -> tuple[V37GraphPlanningInsight, ...]:
    source_ids = tuple(source.source_id for source in evidence_sources)
    finding_ids = tuple(finding.finding_id for finding in findings)
    provenance_refs = tuple(sorted(reference for source in evidence_sources for reference in source.provenance_references))
    continuity_refs = tuple(sorted(reference for source in evidence_sources for reference in source.continuity_references))
    specs = (
        ("governance_risk", "governance restrictions and prohibited governance evidence remain visible"),
        ("compatibility_risk", "compatibility restrictions, unsupported states, and unknown states remain visible"),
        ("evaluation_uncertainty", "evaluation evidence preserves uncertainty and continuity warnings without path selection"),
        ("session_blocked_state", "planning session blocked, unsupported, prohibited, and unknown states remain visible"),
        ("scenario_delta", "scenario differences summarize deterministic hypothetical deltas without selecting a scenario"),
        ("provenance_continuity", "provenance continuity is summarized across all evidence sources"),
        ("explainability_continuity", "explainability continuity is summarized across all evidence sources"),
        ("replay_rollback_continuity", "replay and rollback continuity are summarized as non-executable evidence"),
    )
    return tuple(
        V37GraphPlanningInsight(
            insight_id=f"v3_7_graph_intelligence_insight_{kind}",
            insight_kind=kind,
            summary=summary,
            evidence_source_references=source_ids,
            finding_references=finding_ids,
            provenance_references=provenance_refs,
            continuity_references=continuity_refs,
            recommends_execution=False,
            selects_runtime_path=False,
            authorizes_orchestration=False,
        )
        for kind, summary in specs
    )
