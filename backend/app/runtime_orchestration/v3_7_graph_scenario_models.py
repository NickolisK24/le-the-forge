"""Deterministic v3.7 graph planning scenario models.

Scenarios are immutable hypothetical planning artifacts. They do not execute
graphs, execute scenarios, route work, schedule work, dispatch work, traverse
graphs, mutate runtime state, or represent runtime orchestration branches.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance


V3_7_GRAPH_SCENARIO_PHASE_ID = "v3_7_graph_planning_scenarios"
V37_SCENARIO_STATUS_INITIALIZED = "initialized"
V37_SCENARIO_STATUS_EVALUATED = "evaluated"
V37_SCENARIO_STATUS_BLOCKED = "blocked"
V37_SCENARIO_STATUS_UNSUPPORTED = "unsupported"
V37_SCENARIO_STATUS_PROHIBITED = "prohibited"
V37_SCENARIO_STATUS_UNKNOWN = "unknown"
V37_SCENARIO_STATUS_COMPARISON_READY = "comparison_ready"
V37_SCENARIO_STATUS_AUDIT_FAILED = "audit_failed"
V37_SCENARIO_STATUS_CLOSED = "closed"
V37_GRAPH_SCENARIO_STATUSES: tuple[str, ...] = (
    V37_SCENARIO_STATUS_INITIALIZED,
    V37_SCENARIO_STATUS_EVALUATED,
    V37_SCENARIO_STATUS_BLOCKED,
    V37_SCENARIO_STATUS_UNSUPPORTED,
    V37_SCENARIO_STATUS_PROHIBITED,
    V37_SCENARIO_STATUS_UNKNOWN,
    V37_SCENARIO_STATUS_COMPARISON_READY,
    V37_SCENARIO_STATUS_AUDIT_FAILED,
    V37_SCENARIO_STATUS_CLOSED,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphScenarioIdentity:
    scenario_id: str
    planning_session_id: str
    graph_id: str
    scenario_version: str
    phase_id: str
    stable_identity_key: str


@dataclass(frozen=True)
class V37GraphScenarioMetadata:
    metadata_key: str
    metadata_value: str


@dataclass(frozen=True)
class V37GraphScenarioVariation:
    variation_id: str
    variation_type: str
    scenario_id: str
    planning_session_reference: str
    graph_snapshot_reference: str
    baseline_reference: str
    hypothetical_relationship: str
    governance_classification: str
    compatibility_classification: str
    evaluation_classification: str
    evidence_references: tuple[str, ...]
    provenance: V37GraphProvenance
    structural_hypothetical_evidence_only: bool = True
    executable_orchestration_branch: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class V37GraphScenarioComparisonEvidence:
    comparison_id: str
    scenario_id: str
    baseline_scenario_reference: str
    compared_variation_ids: tuple[str, ...]
    compatibility_delta_references: tuple[str, ...]
    governance_delta_references: tuple[str, ...]
    evaluation_delta_references: tuple[str, ...]
    prohibited_state_delta_references: tuple[str, ...]
    unsupported_state_delta_references: tuple[str, ...]
    unknown_state_delta_references: tuple[str, ...]
    continuity_delta_references: tuple[str, ...]
    provenance_delta_references: tuple[str, ...]
    explainability_delta_references: tuple[str, ...]
    deterministic_comparison_hash: str
    comparison_implies_orchestration_selection: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "compared_variation_ids",
            "compatibility_delta_references",
            "governance_delta_references",
            "evaluation_delta_references",
            "prohibited_state_delta_references",
            "unsupported_state_delta_references",
            "unknown_state_delta_references",
            "continuity_delta_references",
            "provenance_delta_references",
            "explainability_delta_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphScenarioReplayEvidence:
    replay_evidence_id: str
    scenario_id: str
    variation_references: tuple[str, ...]
    graph_snapshot_references: tuple[str, ...]
    evaluation_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    continuity_hashes: tuple[str, ...]
    rollback_references: tuple[str, ...]
    non_executable_replay_evidence: bool = True
    runtime_replay_state: bool = False
    execution_authorization: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "variation_references",
            "graph_snapshot_references",
            "evaluation_references",
            "provenance_references",
            "explainability_references",
            "continuity_hashes",
            "rollback_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphScenarioAuditTrailEntry:
    audit_entry_id: str
    audit_order: int
    audit_type: str
    scenario_status: str
    subject_type: str
    subject_id: str
    message: str
    evidence_references: tuple[str, ...]
    fail_visible: bool = True
    hidden: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class V37GraphPlanningScenario:
    identity: V37GraphScenarioIdentity
    status: str
    metadata: tuple[V37GraphScenarioMetadata, ...]
    planning_session_references: tuple[str, ...]
    graph_snapshot_references: tuple[str, ...]
    variations: tuple[V37GraphScenarioVariation, ...]
    evaluation_evidence_references: tuple[str, ...]
    comparison_evidence: tuple[V37GraphScenarioComparisonEvidence, ...]
    replay_evidence: tuple[V37GraphScenarioReplayEvidence, ...]
    rollback_continuity_references: tuple[str, ...]
    audit_trail: tuple[V37GraphScenarioAuditTrailEntry, ...]
    provenance: V37GraphProvenance
    explainability_reference_ids: tuple[str, ...]
    continuity_hash_references: tuple[str, ...]
    scenarios_are_non_executable: bool = True
    hypothetical_planning_evidence_only: bool = True
    hypothetical_variations_are_not_runtime_branches: bool = True
    scenario_replay_evidence_is_not_runtime_replay: bool = True
    comparisons_do_not_imply_orchestration_selection: bool = True
    scenario_status_does_not_authorize_execution: bool = True
    graph_planning_scenarios_do_not_enable_routing_scheduling_dispatch_traversal: bool = True
    graph_execution_enabled: bool = False
    scenario_execution_enabled: bool = False
    runtime_orchestration_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    graph_traversal_execution_enabled: bool = False
    optimization_engine_enabled: bool = False
    recommendation_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    persistent_runtime_writes_enabled: bool = False
    execution_capable_scenarios_enabled: bool = False
    runtime_branching_behavior_enabled: bool = False
    orchestration_state_machine_enabled: bool = False
    runtime_orchestration_history_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "metadata",
            "planning_session_references",
            "graph_snapshot_references",
            "variations",
            "evaluation_evidence_references",
            "comparison_evidence",
            "replay_evidence",
            "rollback_continuity_references",
            "audit_trail",
            "explainability_reference_ids",
            "continuity_hash_references",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_graph_scenario_identity(identity: V37GraphScenarioIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_graph_scenario_metadata(metadata: V37GraphScenarioMetadata) -> dict[str, Any]:
    return asdict(metadata)


def export_v3_7_graph_scenario_variation(variation: V37GraphScenarioVariation) -> dict[str, Any]:
    data = asdict(variation)
    data["evidence_references"] = sorted(data["evidence_references"])
    data["provenance"] = _export_provenance(variation.provenance)
    return data


def export_v3_7_graph_scenario_comparison_evidence(
    comparison: V37GraphScenarioComparisonEvidence,
) -> dict[str, Any]:
    data = asdict(comparison)
    for field_name in (
        "compared_variation_ids",
        "compatibility_delta_references",
        "governance_delta_references",
        "evaluation_delta_references",
        "prohibited_state_delta_references",
        "unsupported_state_delta_references",
        "unknown_state_delta_references",
        "continuity_delta_references",
        "provenance_delta_references",
        "explainability_delta_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_scenario_replay_evidence(evidence: V37GraphScenarioReplayEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "variation_references",
        "graph_snapshot_references",
        "evaluation_references",
        "provenance_references",
        "explainability_references",
        "continuity_hashes",
        "rollback_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_scenario_audit_trail_entry(entry: V37GraphScenarioAuditTrailEntry) -> dict[str, Any]:
    data = asdict(entry)
    data["evidence_references"] = sorted(data["evidence_references"])
    return data


def export_v3_7_graph_planning_scenario(scenario: V37GraphPlanningScenario) -> dict[str, Any]:
    return {
        "identity": export_v3_7_graph_scenario_identity(scenario.identity),
        "status": scenario.status,
        "metadata": [
            export_v3_7_graph_scenario_metadata(metadata)
            for metadata in sorted(scenario.metadata, key=lambda item: item.metadata_key)
        ],
        "planning_session_references": sorted(scenario.planning_session_references),
        "graph_snapshot_references": sorted(scenario.graph_snapshot_references),
        "variations": [
            export_v3_7_graph_scenario_variation(variation)
            for variation in sorted(scenario.variations, key=lambda item: item.variation_id)
        ],
        "evaluation_evidence_references": sorted(scenario.evaluation_evidence_references),
        "comparison_evidence": [
            export_v3_7_graph_scenario_comparison_evidence(comparison)
            for comparison in sorted(scenario.comparison_evidence, key=lambda item: item.comparison_id)
        ],
        "replay_evidence": [
            export_v3_7_graph_scenario_replay_evidence(evidence)
            for evidence in sorted(scenario.replay_evidence, key=lambda item: item.replay_evidence_id)
        ],
        "rollback_continuity_references": sorted(scenario.rollback_continuity_references),
        "audit_trail": [
            export_v3_7_graph_scenario_audit_trail_entry(entry)
            for entry in sorted(scenario.audit_trail, key=lambda item: (item.audit_order, item.audit_entry_id))
        ],
        "provenance": _export_provenance(scenario.provenance),
        "explainability_reference_ids": sorted(scenario.explainability_reference_ids),
        "continuity_hash_references": sorted(scenario.continuity_hash_references),
        "scenarios_are_non_executable": scenario.scenarios_are_non_executable,
        "hypothetical_planning_evidence_only": scenario.hypothetical_planning_evidence_only,
        "hypothetical_variations_are_not_runtime_branches": scenario.hypothetical_variations_are_not_runtime_branches,
        "scenario_replay_evidence_is_not_runtime_replay": scenario.scenario_replay_evidence_is_not_runtime_replay,
        "comparisons_do_not_imply_orchestration_selection": scenario.comparisons_do_not_imply_orchestration_selection,
        "scenario_status_does_not_authorize_execution": scenario.scenario_status_does_not_authorize_execution,
        "graph_planning_scenarios_do_not_enable_routing_scheduling_dispatch_traversal": (
            scenario.graph_planning_scenarios_do_not_enable_routing_scheduling_dispatch_traversal
        ),
        "graph_execution_enabled": scenario.graph_execution_enabled,
        "scenario_execution_enabled": scenario.scenario_execution_enabled,
        "runtime_orchestration_enabled": scenario.runtime_orchestration_enabled,
        "routing_enabled": scenario.routing_enabled,
        "scheduling_enabled": scenario.scheduling_enabled,
        "dispatch_enabled": scenario.dispatch_enabled,
        "graph_traversal_execution_enabled": scenario.graph_traversal_execution_enabled,
        "optimization_engine_enabled": scenario.optimization_engine_enabled,
        "recommendation_enabled": scenario.recommendation_enabled,
        "autonomous_orchestration_enabled": scenario.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": scenario.runtime_mutation_enabled,
        "persistent_runtime_writes_enabled": scenario.persistent_runtime_writes_enabled,
        "execution_capable_scenarios_enabled": scenario.execution_capable_scenarios_enabled,
        "runtime_branching_behavior_enabled": scenario.runtime_branching_behavior_enabled,
        "orchestration_state_machine_enabled": scenario.orchestration_state_machine_enabled,
        "runtime_orchestration_history_enabled": scenario.runtime_orchestration_history_enabled,
    }


def export_v3_7_graph_scenario_counts(scenario: V37GraphPlanningScenario) -> dict[str, int]:
    return {
        "scenario_count": 1,
        "variation_count": len(scenario.variations),
        "comparison_count": len(scenario.comparison_evidence),
        "replay_evidence_count": len(scenario.replay_evidence),
        "audit_trail_count": len(scenario.audit_trail),
    }


def serialize_v3_7_graph_planning_scenario(scenario: V37GraphPlanningScenario) -> str:
    return stable_serialize(export_v3_7_graph_planning_scenario(scenario))


def hash_v3_7_graph_planning_scenario(scenario: V37GraphPlanningScenario) -> str:
    return deterministic_hash(export_v3_7_graph_planning_scenario(scenario))


def validate_v3_7_graph_scenario_serialization_stability(
    scenario: V37GraphPlanningScenario,
) -> dict[str, Any]:
    first = serialize_v3_7_graph_planning_scenario(scenario)
    second = serialize_v3_7_graph_planning_scenario(scenario)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_graph_planning_scenario",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_graph_scenario_hash_stability(scenario: V37GraphPlanningScenario) -> dict[str, Any]:
    first = hash_v3_7_graph_planning_scenario(scenario)
    second = hash_v3_7_graph_planning_scenario(scenario)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_graph_planning_scenario",
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
