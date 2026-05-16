"""Deterministic v3.7 graph planning intelligence aggregation models.

Aggregations summarize existing planning evidence. They do not execute graphs,
recommend orchestration, select runtime paths, route work, schedule work,
dispatch work, traverse graphs, or make runtime decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance


V3_7_GRAPH_INTELLIGENCE_PHASE_ID = "v3_7_graph_planning_intelligence_aggregation"
V37_INTELLIGENCE_FINDING_GOVERNANCE_VISIBLE = "governance_visible"
V37_INTELLIGENCE_FINDING_COMPATIBILITY_VISIBLE = "compatibility_visible"
V37_INTELLIGENCE_FINDING_EVALUATION_VISIBLE = "evaluation_visible"
V37_INTELLIGENCE_FINDING_SESSION_VISIBLE = "session_visible"
V37_INTELLIGENCE_FINDING_SCENARIO_VISIBLE = "scenario_visible"
V37_INTELLIGENCE_FINDING_BLOCKED_VISIBLE = "blocked_visible"
V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE = "unsupported_visible"
V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE = "prohibited_visible"
V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE = "unknown_visible"
V37_INTELLIGENCE_FINDING_EXPERIMENTAL_VISIBLE = "experimental_visible"
V37_INTELLIGENCE_FINDING_CONTINUITY_WARNING_VISIBLE = "continuity_warning_visible"
V37_INTELLIGENCE_FINDING_PROVENANCE_CONTINUITY_VISIBLE = "provenance_continuity_visible"
V37_INTELLIGENCE_FINDING_EXPLAINABILITY_CONTINUITY_VISIBLE = "explainability_continuity_visible"
V37_INTELLIGENCE_FINDING_REPLAY_CONTINUITY_VISIBLE = "replay_continuity_visible"
V37_INTELLIGENCE_FINDING_ROLLBACK_CONTINUITY_VISIBLE = "rollback_continuity_visible"
V37_INTELLIGENCE_FINDING_CLASSIFICATIONS: tuple[str, ...] = (
    V37_INTELLIGENCE_FINDING_GOVERNANCE_VISIBLE,
    V37_INTELLIGENCE_FINDING_COMPATIBILITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_EVALUATION_VISIBLE,
    V37_INTELLIGENCE_FINDING_SESSION_VISIBLE,
    V37_INTELLIGENCE_FINDING_SCENARIO_VISIBLE,
    V37_INTELLIGENCE_FINDING_BLOCKED_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE,
    V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE,
    V37_INTELLIGENCE_FINDING_EXPERIMENTAL_VISIBLE,
    V37_INTELLIGENCE_FINDING_CONTINUITY_WARNING_VISIBLE,
    V37_INTELLIGENCE_FINDING_PROVENANCE_CONTINUITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_EXPLAINABILITY_CONTINUITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_REPLAY_CONTINUITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_ROLLBACK_CONTINUITY_VISIBLE,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphIntelligenceIdentity:
    aggregation_id: str
    graph_id: str
    aggregation_version: str
    phase_id: str
    stable_identity_key: str


@dataclass(frozen=True)
class V37GraphIntelligenceMetadata:
    metadata_key: str
    metadata_value: str


@dataclass(frozen=True)
class V37GraphIntelligenceEvidenceSource:
    source_id: str
    source_type: str
    source_phase_id: str
    source_reference_id: str
    source_hash: str
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    continuity_references: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in ("provenance_references", "explainability_references", "continuity_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphIntelligenceFinding:
    finding_id: str
    finding_classification: str
    source_type: str
    subject_id: str
    visibility_status: str
    summary: str
    evidence_references: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False
    execution_recommendation: bool = False
    runtime_path_selection: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class V37GraphPlanningInsight:
    insight_id: str
    insight_kind: str
    summary: str
    evidence_source_references: tuple[str, ...]
    finding_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    continuity_references: tuple[str, ...]
    recommends_execution: bool = False
    selects_runtime_path: bool = False
    authorizes_orchestration: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_source_references",
            "finding_references",
            "provenance_references",
            "continuity_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphIntelligenceTotals:
    governance_finding_total: int
    compatibility_finding_total: int
    evaluation_finding_total: int
    session_finding_total: int
    scenario_finding_total: int
    prohibited_visibility_total: int
    unsupported_visibility_total: int
    unknown_visibility_total: int
    blocked_visibility_total: int
    experimental_visibility_total: int
    continuity_warning_total: int
    replay_evidence_total: int
    rollback_evidence_total: int
    provenance_evidence_total: int
    explainability_evidence_total: int


@dataclass(frozen=True)
class V37GraphIntelligenceReplayEvidence:
    replay_evidence_id: str
    aggregation_id: str
    evidence_source_references: tuple[str, ...]
    graph_evidence_references: tuple[str, ...]
    governance_evidence_references: tuple[str, ...]
    compatibility_evidence_references: tuple[str, ...]
    evaluation_evidence_references: tuple[str, ...]
    session_evidence_references: tuple[str, ...]
    scenario_evidence_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    continuity_hashes: tuple[str, ...]
    non_executable_replay_evidence: bool = True
    runtime_replay: bool = False
    execution_authorization: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_source_references",
            "graph_evidence_references",
            "governance_evidence_references",
            "compatibility_evidence_references",
            "evaluation_evidence_references",
            "session_evidence_references",
            "scenario_evidence_references",
            "provenance_references",
            "explainability_references",
            "continuity_hashes",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphPlanningIntelligenceAggregation:
    identity: V37GraphIntelligenceIdentity
    metadata: tuple[V37GraphIntelligenceMetadata, ...]
    evidence_sources: tuple[V37GraphIntelligenceEvidenceSource, ...]
    totals: V37GraphIntelligenceTotals
    findings: tuple[V37GraphIntelligenceFinding, ...]
    insights: tuple[V37GraphPlanningInsight, ...]
    replay_evidence: tuple[V37GraphIntelligenceReplayEvidence, ...]
    rollback_continuity_references: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_reference_ids: tuple[str, ...]
    continuity_hash_references: tuple[str, ...]
    aggregation_is_non_executable: bool = True
    planning_evidence_summarization_only: bool = True
    aggregated_insights_are_not_recommendations: bool = True
    aggregated_insights_do_not_authorize_execution: bool = True
    aggregation_does_not_select_graph_paths: bool = True
    aggregation_does_not_select_scenarios_for_execution: bool = True
    aggregation_does_not_enable_routing_scheduling_dispatch_traversal_runtime_orchestration: bool = True
    graph_execution_enabled: bool = False
    aggregation_driven_execution_enabled: bool = False
    orchestration_selection_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    graph_traversal_execution_enabled: bool = False
    optimization_engine_enabled: bool = False
    recommendation_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    persistent_runtime_writes_enabled: bool = False
    runtime_decision_making_enabled: bool = False
    path_ranking_for_execution_enabled: bool = False
    scenario_selection_for_execution_enabled: bool = False
    executable_planning_insights_enabled: bool = False
    orchestration_state_machine_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "metadata",
            "evidence_sources",
            "findings",
            "insights",
            "replay_evidence",
            "rollback_continuity_references",
            "explainability_reference_ids",
            "continuity_hash_references",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_graph_intelligence_identity(identity: V37GraphIntelligenceIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_graph_intelligence_metadata(metadata: V37GraphIntelligenceMetadata) -> dict[str, Any]:
    return asdict(metadata)


def export_v3_7_graph_intelligence_evidence_source(source: V37GraphIntelligenceEvidenceSource) -> dict[str, Any]:
    data = asdict(source)
    for field_name in ("provenance_references", "explainability_references", "continuity_references"):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_intelligence_finding(finding: V37GraphIntelligenceFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_references"] = sorted(data["evidence_references"])
    return data


def export_v3_7_graph_planning_insight(insight: V37GraphPlanningInsight) -> dict[str, Any]:
    data = asdict(insight)
    for field_name in (
        "evidence_source_references",
        "finding_references",
        "provenance_references",
        "continuity_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_intelligence_totals(totals: V37GraphIntelligenceTotals) -> dict[str, int]:
    return asdict(totals)


def export_v3_7_graph_intelligence_replay_evidence(evidence: V37GraphIntelligenceReplayEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "evidence_source_references",
        "graph_evidence_references",
        "governance_evidence_references",
        "compatibility_evidence_references",
        "evaluation_evidence_references",
        "session_evidence_references",
        "scenario_evidence_references",
        "provenance_references",
        "explainability_references",
        "continuity_hashes",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_planning_intelligence_aggregation(
    aggregation: V37GraphPlanningIntelligenceAggregation,
) -> dict[str, Any]:
    return {
        "identity": export_v3_7_graph_intelligence_identity(aggregation.identity),
        "metadata": [
            export_v3_7_graph_intelligence_metadata(metadata)
            for metadata in sorted(aggregation.metadata, key=lambda item: item.metadata_key)
        ],
        "evidence_sources": [
            export_v3_7_graph_intelligence_evidence_source(source)
            for source in sorted(aggregation.evidence_sources, key=lambda item: item.source_id)
        ],
        "totals": export_v3_7_graph_intelligence_totals(aggregation.totals),
        "findings": [
            export_v3_7_graph_intelligence_finding(finding)
            for finding in sorted(aggregation.findings, key=lambda item: item.finding_id)
        ],
        "insights": [
            export_v3_7_graph_planning_insight(insight)
            for insight in sorted(aggregation.insights, key=lambda item: item.insight_id)
        ],
        "replay_evidence": [
            export_v3_7_graph_intelligence_replay_evidence(evidence)
            for evidence in sorted(aggregation.replay_evidence, key=lambda item: item.replay_evidence_id)
        ],
        "rollback_continuity_references": sorted(aggregation.rollback_continuity_references),
        "provenance": _export_provenance(aggregation.provenance),
        "explainability_reference_ids": sorted(aggregation.explainability_reference_ids),
        "continuity_hash_references": sorted(aggregation.continuity_hash_references),
        "aggregation_is_non_executable": aggregation.aggregation_is_non_executable,
        "planning_evidence_summarization_only": aggregation.planning_evidence_summarization_only,
        "aggregated_insights_are_not_recommendations": aggregation.aggregated_insights_are_not_recommendations,
        "aggregated_insights_do_not_authorize_execution": aggregation.aggregated_insights_do_not_authorize_execution,
        "aggregation_does_not_select_graph_paths": aggregation.aggregation_does_not_select_graph_paths,
        "aggregation_does_not_select_scenarios_for_execution": aggregation.aggregation_does_not_select_scenarios_for_execution,
        "aggregation_does_not_enable_routing_scheduling_dispatch_traversal_runtime_orchestration": (
            aggregation.aggregation_does_not_enable_routing_scheduling_dispatch_traversal_runtime_orchestration
        ),
        "graph_execution_enabled": aggregation.graph_execution_enabled,
        "aggregation_driven_execution_enabled": aggregation.aggregation_driven_execution_enabled,
        "orchestration_selection_enabled": aggregation.orchestration_selection_enabled,
        "routing_enabled": aggregation.routing_enabled,
        "scheduling_enabled": aggregation.scheduling_enabled,
        "dispatch_enabled": aggregation.dispatch_enabled,
        "graph_traversal_execution_enabled": aggregation.graph_traversal_execution_enabled,
        "optimization_engine_enabled": aggregation.optimization_engine_enabled,
        "recommendation_enabled": aggregation.recommendation_enabled,
        "autonomous_orchestration_enabled": aggregation.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": aggregation.runtime_mutation_enabled,
        "persistent_runtime_writes_enabled": aggregation.persistent_runtime_writes_enabled,
        "runtime_decision_making_enabled": aggregation.runtime_decision_making_enabled,
        "path_ranking_for_execution_enabled": aggregation.path_ranking_for_execution_enabled,
        "scenario_selection_for_execution_enabled": aggregation.scenario_selection_for_execution_enabled,
        "executable_planning_insights_enabled": aggregation.executable_planning_insights_enabled,
        "orchestration_state_machine_enabled": aggregation.orchestration_state_machine_enabled,
    }


def export_v3_7_graph_intelligence_counts(
    aggregation: V37GraphPlanningIntelligenceAggregation,
) -> dict[str, int]:
    return {
        "aggregation_count": 1,
        "evidence_source_count": len(aggregation.evidence_sources),
        "finding_count": len(aggregation.findings),
        "insight_count": len(aggregation.insights),
        "replay_evidence_count": len(aggregation.replay_evidence),
        "rollback_continuity_reference_count": len(aggregation.rollback_continuity_references),
    }


def serialize_v3_7_graph_planning_intelligence_aggregation(
    aggregation: V37GraphPlanningIntelligenceAggregation,
) -> str:
    return stable_serialize(export_v3_7_graph_planning_intelligence_aggregation(aggregation))


def hash_v3_7_graph_planning_intelligence_aggregation(
    aggregation: V37GraphPlanningIntelligenceAggregation,
) -> str:
    return deterministic_hash(export_v3_7_graph_planning_intelligence_aggregation(aggregation))


def validate_v3_7_graph_intelligence_serialization_stability(
    aggregation: V37GraphPlanningIntelligenceAggregation,
) -> dict[str, Any]:
    first = serialize_v3_7_graph_planning_intelligence_aggregation(aggregation)
    second = serialize_v3_7_graph_planning_intelligence_aggregation(aggregation)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_graph_planning_intelligence_aggregation",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_graph_intelligence_hash_stability(
    aggregation: V37GraphPlanningIntelligenceAggregation,
) -> dict[str, Any]:
    first = hash_v3_7_graph_planning_intelligence_aggregation(aggregation)
    second = hash_v3_7_graph_planning_intelligence_aggregation(aggregation)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_graph_planning_intelligence_aggregation",
    }


def _export_provenance(provenance: V37GraphProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field_name in (
        "lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "governance_references",
        "compatibility_references",
        "explainability_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data
