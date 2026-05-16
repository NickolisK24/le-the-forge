"""Deterministic explainability for v3.7 graph planning scenarios."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_scenario_models import (
    V37_SCENARIO_STATUS_BLOCKED,
    V37_SCENARIO_STATUS_COMPARISON_READY,
    V37_SCENARIO_STATUS_PROHIBITED,
    V37_SCENARIO_STATUS_UNKNOWN,
    V37_SCENARIO_STATUS_UNSUPPORTED,
    V37GraphPlanningScenario,
    V37GraphScenarioVariation,
)
from .v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE = "v3_7_graph_scenario_explainability_stable"
V37_GRAPH_SCENARIO_EXPLAINABILITY_BLOCKED = "v3_7_graph_scenario_explainability_blocked"


@dataclass(frozen=True)
class V37GraphScenarioExplanation:
    explanation_id: str
    subject_type: str
    subject_id: str
    scenario_status: str
    why_present: str
    planning_session_references: tuple[str, ...]
    graph_snapshot_references: tuple[str, ...]
    variation_references: tuple[str, ...]
    evaluation_evidence_references: tuple[str, ...]
    comparison_references: tuple[str, ...]
    visible_finding_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    continuity_references: tuple[str, ...]
    reasoning_chain: tuple[str, ...]
    replay_safe: bool = True
    execution_authorization: bool = False


@dataclass(frozen=True)
class V37GraphScenarioExplainabilityResult:
    explainability_status: str
    replay_safe: bool
    explanation_count: int
    scenario_existence_explanation_count: int
    variation_explanation_count: int
    comparison_explanation_count: int
    replay_explanation_count: int
    visible_finding_explanation_count: int
    blocked_explanation_count: int
    unsupported_explanation_count: int
    prohibited_explanation_count: int
    unknown_explanation_count: int
    changed_between_scenarios_explanation_count: int
    provenance_supported_explanation_count: int
    continuity_supported_explanation_count: int
    missing_explanation_subjects: tuple[str, ...]
    explanations: tuple[V37GraphScenarioExplanation, ...]
    deterministic_explainability_hash: str = ""


def explain_v3_7_graph_scenario(
    scenario: V37GraphPlanningScenario | None = None,
) -> V37GraphScenarioExplainabilityResult:
    planning_scenario = scenario or build_v3_7_graph_planning_scenario()
    explanations = _build_explanations(planning_scenario)
    expected_subjects = {("graph_planning_scenario", planning_scenario.identity.scenario_id)}
    expected_subjects.update(("scenario_variation", item.variation_id) for item in planning_scenario.variations)
    expected_subjects.update(("scenario_comparison", item.comparison_id) for item in planning_scenario.comparison_evidence)
    expected_subjects.update(("scenario_replay_evidence", item.replay_evidence_id) for item in planning_scenario.replay_evidence)
    expected_subjects.update(("scenario_audit_trail", entry.audit_entry_id) for entry in planning_scenario.audit_trail)
    actual_subjects = {(explanation.subject_type, explanation.subject_id) for explanation in explanations}
    missing = tuple(sorted(f"{kind}:{subject_id}" for kind, subject_id in expected_subjects - actual_subjects))
    blocked = bool(missing) or any(
        not explanation.why_present
        or not explanation.provenance_references
        or not explanation.continuity_references
        or explanation.execution_authorization
        for explanation in explanations
    )
    result = V37GraphScenarioExplainabilityResult(
        explainability_status=(
            V37_GRAPH_SCENARIO_EXPLAINABILITY_BLOCKED
            if blocked
            else V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE
        ),
        replay_safe=not blocked,
        explanation_count=len(explanations),
        scenario_existence_explanation_count=sum(1 for item in explanations if item.subject_type == "graph_planning_scenario"),
        variation_explanation_count=sum(1 for item in explanations if item.subject_type == "scenario_variation"),
        comparison_explanation_count=sum(1 for item in explanations if item.subject_type == "scenario_comparison"),
        replay_explanation_count=sum(1 for item in explanations if item.subject_type == "scenario_replay_evidence"),
        visible_finding_explanation_count=sum(1 for item in explanations if item.subject_type == "scenario_audit_trail"),
        blocked_explanation_count=sum(1 for item in explanations if item.scenario_status == V37_SCENARIO_STATUS_BLOCKED),
        unsupported_explanation_count=sum(
            1 for item in explanations if item.scenario_status == V37_SCENARIO_STATUS_UNSUPPORTED
        ),
        prohibited_explanation_count=sum(
            1 for item in explanations if item.scenario_status == V37_SCENARIO_STATUS_PROHIBITED
        ),
        unknown_explanation_count=sum(1 for item in explanations if item.scenario_status == V37_SCENARIO_STATUS_UNKNOWN),
        changed_between_scenarios_explanation_count=sum(
            1 for item in explanations if item.subject_type == "scenario_comparison"
        ),
        provenance_supported_explanation_count=sum(1 for item in explanations if item.provenance_references),
        continuity_supported_explanation_count=sum(1 for item in explanations if item.continuity_references),
        missing_explanation_subjects=missing,
        explanations=tuple(sorted(explanations, key=lambda item: item.explanation_id)),
    )
    return replace(
        result,
        deterministic_explainability_hash=hash_v3_7_graph_scenario_explainability_result(result),
    )


def export_v3_7_graph_scenario_explanation(
    explanation: V37GraphScenarioExplanation,
) -> dict[str, Any]:
    data = asdict(explanation)
    for field_name in (
        "planning_session_references",
        "graph_snapshot_references",
        "variation_references",
        "evaluation_evidence_references",
        "comparison_references",
        "visible_finding_references",
        "provenance_references",
        "continuity_references",
        "reasoning_chain",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_scenario_explainability_result(
    result: V37GraphScenarioExplainabilityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_explanation_subjects"] = sorted(data["missing_explanation_subjects"])
    data["explanations"] = [
        export_v3_7_graph_scenario_explanation(explanation)
        for explanation in sorted(result.explanations, key=lambda item: item.explanation_id)
    ]
    return data


def serialize_v3_7_graph_scenario_explainability_result(
    result: V37GraphScenarioExplainabilityResult,
) -> str:
    return stable_serialize(export_v3_7_graph_scenario_explainability_result(result))


def hash_v3_7_graph_scenario_explainability_result(
    result: V37GraphScenarioExplainabilityResult,
) -> str:
    data = export_v3_7_graph_scenario_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)


def _build_explanations(
    scenario: V37GraphPlanningScenario,
) -> tuple[V37GraphScenarioExplanation, ...]:
    explanations: list[V37GraphScenarioExplanation] = [
        V37GraphScenarioExplanation(
            explanation_id=f"explain_scenario_{scenario.identity.scenario_id}",
            subject_type="graph_planning_scenario",
            subject_id=scenario.identity.scenario_id,
            scenario_status=scenario.status,
            why_present="scenario groups deterministic hypothetical planning evidence without runtime branching",
            planning_session_references=scenario.planning_session_references,
            graph_snapshot_references=scenario.graph_snapshot_references,
            variation_references=tuple(variation.variation_id for variation in scenario.variations),
            evaluation_evidence_references=scenario.evaluation_evidence_references,
            comparison_references=tuple(item.comparison_id for item in scenario.comparison_evidence),
            visible_finding_references=tuple(entry.audit_entry_id for entry in scenario.audit_trail),
            provenance_references=(scenario.provenance.provenance_id,),
            continuity_references=scenario.continuity_hash_references,
            reasoning_chain=("scenario_identity", "planning_session_scope", "hypothetical_variations", "non_executable_boundary"),
        )
    ]
    for variation in scenario.variations:
        explanations.append(_variation_explanation(scenario, variation))
    for comparison in scenario.comparison_evidence:
        explanations.append(
            V37GraphScenarioExplanation(
                explanation_id=f"explain_comparison_{comparison.comparison_id}",
                subject_type="scenario_comparison",
                subject_id=comparison.comparison_id,
                scenario_status=scenario.status,
                why_present="comparison records deterministic deltas between scenario hypotheses without selecting orchestration",
                planning_session_references=scenario.planning_session_references,
                graph_snapshot_references=scenario.graph_snapshot_references,
                variation_references=comparison.compared_variation_ids,
                evaluation_evidence_references=comparison.evaluation_delta_references,
                comparison_references=(comparison.comparison_id,),
                visible_finding_references=(
                    comparison.prohibited_state_delta_references
                    + comparison.unsupported_state_delta_references
                    + comparison.unknown_state_delta_references
                ),
                provenance_references=comparison.provenance_delta_references,
                continuity_references=(
                    comparison.continuity_delta_references
                    + (comparison.deterministic_comparison_hash,)
                ),
                reasoning_chain=("scenario_comparison", "delta_visibility", "not_orchestration_selection"),
            )
        )
    for evidence in scenario.replay_evidence:
        explanations.append(
            V37GraphScenarioExplanation(
                explanation_id=f"explain_replay_{evidence.replay_evidence_id}",
                subject_type="scenario_replay_evidence",
                subject_id=evidence.replay_evidence_id,
                scenario_status=scenario.status,
                why_present="scenario replay evidence preserves deterministic continuity and is not runtime replay state",
                planning_session_references=scenario.planning_session_references,
                graph_snapshot_references=evidence.graph_snapshot_references,
                variation_references=evidence.variation_references,
                evaluation_evidence_references=evidence.evaluation_references,
                comparison_references=tuple(item.comparison_id for item in scenario.comparison_evidence),
                visible_finding_references=(),
                provenance_references=evidence.provenance_references,
                continuity_references=evidence.continuity_hashes,
                reasoning_chain=("scenario_replay_evidence", "continuity_hashes", "non_executable_replay"),
            )
        )
    for entry in scenario.audit_trail:
        explanations.append(
            V37GraphScenarioExplanation(
                explanation_id=f"explain_audit_{entry.audit_entry_id}",
                subject_type="scenario_audit_trail",
                subject_id=entry.audit_entry_id,
                scenario_status=entry.scenario_status,
                why_present=entry.message,
                planning_session_references=scenario.planning_session_references,
                graph_snapshot_references=scenario.graph_snapshot_references,
                variation_references=entry.evidence_references,
                evaluation_evidence_references=scenario.evaluation_evidence_references,
                comparison_references=tuple(item.comparison_id for item in scenario.comparison_evidence),
                visible_finding_references=(entry.audit_entry_id,),
                provenance_references=(scenario.provenance.provenance_id,),
                continuity_references=scenario.continuity_hash_references,
                reasoning_chain=("scenario_audit_trail", entry.scenario_status, "fail_visible", "not_runtime_history"),
            )
        )
    return tuple(explanations)


def _variation_explanation(
    scenario: V37GraphPlanningScenario,
    variation: V37GraphScenarioVariation,
) -> V37GraphScenarioExplanation:
    status = _variation_status(variation)
    return V37GraphScenarioExplanation(
        explanation_id=f"explain_variation_{variation.variation_id}",
        subject_type="scenario_variation",
        subject_id=variation.variation_id,
        scenario_status=status,
        why_present=f"variation models {variation.variation_type} as structural hypothetical evidence only",
        planning_session_references=(variation.planning_session_reference,),
        graph_snapshot_references=(variation.graph_snapshot_reference,),
        variation_references=(variation.variation_id,),
        evaluation_evidence_references=(variation.evaluation_classification,),
        comparison_references=tuple(item.comparison_id for item in scenario.comparison_evidence),
        visible_finding_references=variation.evidence_references,
        provenance_references=(variation.provenance.provenance_id,),
        continuity_references=scenario.continuity_hash_references,
        reasoning_chain=(
            "hypothetical_variation",
            variation.governance_classification,
            variation.compatibility_classification,
            variation.evaluation_classification,
            "not_runtime_branch",
        ),
    )


def _variation_status(variation: V37GraphScenarioVariation) -> str:
    classifications = {
        variation.governance_classification,
        variation.compatibility_classification,
        variation.evaluation_classification,
    }
    if "prohibited" in classifications:
        return V37_SCENARIO_STATUS_PROHIBITED
    if "unsupported" in classifications:
        return V37_SCENARIO_STATUS_UNSUPPORTED
    if "unknown" in classifications:
        return V37_SCENARIO_STATUS_UNKNOWN
    if "governance_restricted" in classifications or "compatibility_restricted" in classifications:
        return V37_SCENARIO_STATUS_BLOCKED
    return V37_SCENARIO_STATUS_COMPARISON_READY
