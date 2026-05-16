"""Provenance continuity for v3.7 graph planning scenarios."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance
from .v3_7_graph_scenario_models import V37GraphPlanningScenario
from .v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED = "v3_7_graph_scenario_provenance_preserved"
V37_GRAPH_SCENARIO_PROVENANCE_BLOCKED = "v3_7_graph_scenario_provenance_blocked"


@dataclass(frozen=True)
class V37GraphScenarioProvenanceResult:
    provenance_status: str
    scenario_creation_provenance_preserved: bool
    planning_session_provenance_preserved: bool
    graph_snapshot_provenance_preserved: bool
    evaluation_provenance_preserved: bool
    replay_provenance_preserved: bool
    rollback_provenance_preserved: bool
    explainability_provenance_preserved: bool
    continuity_provenance_preserved: bool
    comparison_provenance_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    missing_provenance_subjects: tuple[str, ...]
    provenance_record_count: int
    deterministic_provenance_hash: str = ""


def audit_v3_7_graph_scenario_provenance(
    scenario: V37GraphPlanningScenario | None = None,
) -> V37GraphScenarioProvenanceResult:
    planning_scenario = scenario or build_v3_7_graph_planning_scenario()
    missing: list[str] = []
    scenario_ok = _provenance_complete(planning_scenario.provenance)
    if not scenario_ok:
        missing.append(planning_scenario.identity.scenario_id)
    variation_ok = _all_complete(
        ((variation.variation_id, variation.provenance) for variation in planning_scenario.variations),
        missing,
    )
    planning_session_ok = bool(planning_scenario.planning_session_references) and all(
        variation.planning_session_reference in planning_scenario.planning_session_references
        for variation in planning_scenario.variations
    )
    if not planning_session_ok:
        missing.append("scenario_planning_session_reference")
    snapshot_ok = bool(planning_scenario.graph_snapshot_references) and all(
        variation.graph_snapshot_reference in planning_scenario.graph_snapshot_references
        for variation in planning_scenario.variations
    )
    if not snapshot_ok:
        missing.append("scenario_graph_snapshot_reference")
    evaluation_ok = bool(planning_scenario.evaluation_evidence_references)
    if not evaluation_ok:
        missing.append("scenario_evaluation_reference")
    replay_ok = all(evidence.provenance_references for evidence in planning_scenario.replay_evidence)
    if not replay_ok:
        missing.append("scenario_replay_evidence")
    rollback_ok = all(evidence.rollback_references for evidence in planning_scenario.replay_evidence)
    if not rollback_ok:
        missing.append("scenario_rollback_continuity")
    explainability_ok = bool(planning_scenario.explainability_reference_ids) and all(
        comparison.explainability_delta_references for comparison in planning_scenario.comparison_evidence
    )
    if not explainability_ok:
        missing.append("scenario_explainability")
    continuity_ok = bool(planning_scenario.continuity_hash_references) and all(
        evidence.continuity_hashes for evidence in planning_scenario.replay_evidence
    )
    if not continuity_ok:
        missing.append("scenario_continuity")
    comparison_ok = all(comparison.provenance_delta_references for comparison in planning_scenario.comparison_evidence)
    if not comparison_ok:
        missing.append("scenario_comparison")
    replay_continuity_ok = all(evidence.variation_references and evidence.graph_snapshot_references for evidence in planning_scenario.replay_evidence)
    rollback_continuity_ok = all(evidence.rollback_references for evidence in planning_scenario.replay_evidence)
    preserved = all(
        (
            scenario_ok,
            variation_ok,
            planning_session_ok,
            snapshot_ok,
            evaluation_ok,
            replay_ok,
            rollback_ok,
            explainability_ok,
            continuity_ok,
            comparison_ok,
            replay_continuity_ok,
            rollback_continuity_ok,
        )
    )
    records = collect_v3_7_graph_scenario_provenance(planning_scenario)
    result = V37GraphScenarioProvenanceResult(
        provenance_status=V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED if preserved else V37_GRAPH_SCENARIO_PROVENANCE_BLOCKED,
        scenario_creation_provenance_preserved=scenario_ok,
        planning_session_provenance_preserved=planning_session_ok,
        graph_snapshot_provenance_preserved=snapshot_ok,
        evaluation_provenance_preserved=evaluation_ok,
        replay_provenance_preserved=replay_ok,
        rollback_provenance_preserved=rollback_ok,
        explainability_provenance_preserved=bool(explainability_ok),
        continuity_provenance_preserved=continuity_ok,
        comparison_provenance_preserved=comparison_ok,
        replay_continuity_preserved=replay_continuity_ok,
        rollback_continuity_preserved=rollback_continuity_ok,
        missing_provenance_subjects=tuple(sorted(set(missing))),
        provenance_record_count=len(records),
    )
    return replace(
        result,
        deterministic_provenance_hash=hash_v3_7_graph_scenario_provenance_result(result),
    )


def collect_v3_7_graph_scenario_provenance(
    scenario: V37GraphPlanningScenario,
) -> tuple[V37GraphProvenance, ...]:
    records = [scenario.provenance]
    records.extend(variation.provenance for variation in scenario.variations)
    return tuple(sorted(records, key=lambda item: item.provenance_id))


def export_v3_7_graph_scenario_provenance_result(
    result: V37GraphScenarioProvenanceResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_provenance_subjects"] = sorted(data["missing_provenance_subjects"])
    return data


def serialize_v3_7_graph_scenario_provenance_result(
    result: V37GraphScenarioProvenanceResult,
) -> str:
    return stable_serialize(export_v3_7_graph_scenario_provenance_result(result))


def hash_v3_7_graph_scenario_provenance_result(
    result: V37GraphScenarioProvenanceResult,
) -> str:
    data = export_v3_7_graph_scenario_provenance_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)


def _all_complete(records: object, missing: list[str]) -> bool:
    complete = True
    for subject_id, provenance in records:
        if not _provenance_complete(provenance):
            missing.append(subject_id)
            complete = False
    return complete


def _provenance_complete(provenance: V37GraphProvenance) -> bool:
    return all(
        (
            provenance.provenance_id,
            provenance.source_phase_id,
            provenance.source_artifact_id,
            provenance.source_kind,
            provenance.lineage_references,
            provenance.replay_lineage_references,
            provenance.rollback_lineage_references,
            provenance.governance_references,
            provenance.compatibility_references,
            provenance.explainability_references,
        )
    )
