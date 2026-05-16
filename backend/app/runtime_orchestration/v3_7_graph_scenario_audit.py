"""Deterministic audit infrastructure for v3.7 graph planning scenarios."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance
from .v3_7_graph_scenario_identity import graph_scenario_identity_key
from .v3_7_graph_scenario_models import (
    V37_SCENARIO_STATUS_BLOCKED,
    V37_SCENARIO_STATUS_PROHIBITED,
    V37_SCENARIO_STATUS_UNKNOWN,
    V37_SCENARIO_STATUS_UNSUPPORTED,
    V37GraphPlanningScenario,
)
from .v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


V37_GRAPH_SCENARIO_AUDIT_STABLE = "v3_7_graph_scenario_audit_stable"
V37_GRAPH_SCENARIO_AUDIT_FAILED = "v3_7_graph_scenario_audit_failed"
V37_SCENARIO_AUDIT_VISIBLE_BLOCKED = "v3_7_graph_scenario_visible_blocked"
V37_SCENARIO_AUDIT_VISIBLE_UNSUPPORTED = "v3_7_graph_scenario_visible_unsupported"
V37_SCENARIO_AUDIT_VISIBLE_PROHIBITED = "v3_7_graph_scenario_visible_prohibited"
V37_SCENARIO_AUDIT_VISIBLE_UNKNOWN = "v3_7_graph_scenario_visible_unknown"
V37_SCENARIO_AUDIT_BLOCKED_BY_IDENTITY = "v3_7_graph_scenario_audit_blocked_by_identity"
V37_SCENARIO_AUDIT_BLOCKED_BY_VARIATION = "v3_7_graph_scenario_audit_blocked_by_variation"
V37_SCENARIO_AUDIT_BLOCKED_BY_GRAPH_SNAPSHOT = "v3_7_graph_scenario_audit_blocked_by_graph_snapshot"
V37_SCENARIO_AUDIT_BLOCKED_BY_COMPARISON = "v3_7_graph_scenario_audit_blocked_by_comparison"
V37_SCENARIO_AUDIT_BLOCKED_BY_REPLAY = "v3_7_graph_scenario_audit_blocked_by_replay"
V37_SCENARIO_AUDIT_BLOCKED_BY_ROLLBACK = "v3_7_graph_scenario_audit_blocked_by_rollback"
V37_SCENARIO_AUDIT_BLOCKED_BY_PROVENANCE = "v3_7_graph_scenario_audit_blocked_by_provenance"
V37_SCENARIO_AUDIT_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_scenario_audit_blocked_by_explainability"
V37_SCENARIO_AUDIT_BLOCKED_BY_GOVERNANCE = "v3_7_graph_scenario_audit_blocked_by_governance"
V37_SCENARIO_AUDIT_BLOCKED_BY_COMPATIBILITY = "v3_7_graph_scenario_audit_blocked_by_compatibility"
V37_SCENARIO_AUDIT_BLOCKED_BY_EVALUATION = "v3_7_graph_scenario_audit_blocked_by_evaluation"
V37_SCENARIO_AUDIT_BLOCKED_BY_FINDING_VISIBILITY = "v3_7_graph_scenario_audit_blocked_by_finding_visibility"
V37_SCENARIO_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY = "v3_7_graph_scenario_audit_blocked_by_execution_capability"


@dataclass(frozen=True)
class V37GraphScenarioAuditFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphScenarioAuditResult:
    audit_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    scenario_identity_stable: bool
    scenario_variation_continuity_preserved: bool
    graph_snapshot_continuity_preserved: bool
    scenario_comparison_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    governance_continuity_preserved: bool
    compatibility_continuity_preserved: bool
    evaluation_continuity_preserved: bool
    fail_visible_finding_preservation: bool
    non_execution_guarantee_preserved: bool
    deterministic_audit_hash: str
    findings: tuple[V37GraphScenarioAuditFinding, ...]


def audit_v3_7_graph_scenario(
    scenario: V37GraphPlanningScenario | None = None,
) -> V37GraphScenarioAuditResult:
    planning_scenario = scenario or build_v3_7_graph_planning_scenario()
    findings: list[V37GraphScenarioAuditFinding] = []
    _add_visibility_findings(planning_scenario, findings)

    variation_ids = {variation.variation_id for variation in planning_scenario.variations}
    identity_ok = planning_scenario.identity.stable_identity_key == graph_scenario_identity_key(planning_scenario.identity)
    _append_error_if_false(findings, identity_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_IDENTITY, "scenario", planning_scenario.identity.scenario_id, "scenario identity is unstable")
    variation_ok = bool(planning_scenario.variations) and all(
        variation.scenario_id == planning_scenario.identity.scenario_id
        and variation.planning_session_reference in planning_scenario.planning_session_references
        and variation.graph_snapshot_reference in planning_scenario.graph_snapshot_references
        and variation.structural_hypothetical_evidence_only
        and not variation.executable_orchestration_branch
        for variation in planning_scenario.variations
    )
    _append_error_if_false(findings, variation_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_VARIATION, "scenario", planning_scenario.identity.scenario_id, "scenario variation continuity is incomplete")
    snapshot_ok = bool(planning_scenario.graph_snapshot_references) and all(
        variation.graph_snapshot_reference in planning_scenario.graph_snapshot_references
        for variation in planning_scenario.variations
    )
    _append_error_if_false(findings, snapshot_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_GRAPH_SNAPSHOT, "scenario", planning_scenario.identity.scenario_id, "graph snapshot continuity is incomplete")
    comparison_ok = bool(planning_scenario.comparison_evidence) and all(
        comparison.compared_variation_ids
        and set(comparison.compared_variation_ids).issubset(variation_ids)
        and comparison.deterministic_comparison_hash
        and not comparison.comparison_implies_orchestration_selection
        for comparison in planning_scenario.comparison_evidence
    )
    _append_error_if_false(findings, comparison_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_COMPARISON, "scenario", planning_scenario.identity.scenario_id, "scenario comparison continuity is incomplete")
    replay_ok = bool(planning_scenario.replay_evidence) and all(
        evidence.non_executable_replay_evidence
        and not evidence.runtime_replay_state
        and not evidence.execution_authorization
        and evidence.variation_references
        and evidence.graph_snapshot_references
        and evidence.evaluation_references
        and evidence.continuity_hashes
        for evidence in planning_scenario.replay_evidence
    )
    _append_error_if_false(findings, replay_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_REPLAY, "scenario", planning_scenario.identity.scenario_id, "scenario replay evidence continuity is incomplete")
    rollback_ok = bool(planning_scenario.rollback_continuity_references) and all(
        evidence.rollback_references for evidence in planning_scenario.replay_evidence
    )
    _append_error_if_false(findings, rollback_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_ROLLBACK, "scenario", planning_scenario.identity.scenario_id, "scenario rollback continuity is incomplete")
    provenance_ok = _provenance_continuity_preserved(planning_scenario)
    _append_error_if_false(findings, provenance_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_PROVENANCE, "scenario", planning_scenario.identity.scenario_id, "scenario provenance continuity is incomplete")
    explainability_ok = bool(planning_scenario.explainability_reference_ids) and all(
        comparison.explainability_delta_references for comparison in planning_scenario.comparison_evidence
    )
    _append_error_if_false(findings, bool(explainability_ok), V37_SCENARIO_AUDIT_BLOCKED_BY_EXPLAINABILITY, "scenario", planning_scenario.identity.scenario_id, "scenario explainability continuity is incomplete")
    governance_ok = all(variation.governance_classification for variation in planning_scenario.variations) and all(
        comparison.governance_delta_references for comparison in planning_scenario.comparison_evidence
    )
    _append_error_if_false(findings, governance_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_GOVERNANCE, "scenario", planning_scenario.identity.scenario_id, "scenario governance continuity is incomplete")
    compatibility_ok = all(variation.compatibility_classification for variation in planning_scenario.variations) and all(
        comparison.compatibility_delta_references for comparison in planning_scenario.comparison_evidence
    )
    _append_error_if_false(findings, compatibility_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_COMPATIBILITY, "scenario", planning_scenario.identity.scenario_id, "scenario compatibility continuity is incomplete")
    evaluation_ok = bool(planning_scenario.evaluation_evidence_references) and all(
        variation.evaluation_classification for variation in planning_scenario.variations
    )
    _append_error_if_false(findings, evaluation_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_EVALUATION, "scenario", planning_scenario.identity.scenario_id, "scenario evaluation continuity is incomplete")
    fail_visible_ok = all(entry.fail_visible and not entry.hidden for entry in planning_scenario.audit_trail)
    _append_error_if_false(findings, fail_visible_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_FINDING_VISIBILITY, "scenario", planning_scenario.identity.scenario_id, "scenario audit trail contains hidden or non-visible finding")
    non_execution_ok = _non_execution_guarantee_preserved(planning_scenario)
    _append_error_if_false(findings, non_execution_ok, V37_SCENARIO_AUDIT_BLOCKED_BY_EXECUTION_CAPABILITY, "scenario", planning_scenario.identity.scenario_id, "scenario exposed execution capability")

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphScenarioAuditResult(
        audit_status=V37_GRAPH_SCENARIO_AUDIT_STABLE if error_count == 0 else V37_GRAPH_SCENARIO_AUDIT_FAILED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        scenario_identity_stable=identity_ok,
        scenario_variation_continuity_preserved=variation_ok,
        graph_snapshot_continuity_preserved=snapshot_ok,
        scenario_comparison_continuity_preserved=comparison_ok,
        replay_continuity_preserved=replay_ok,
        rollback_continuity_preserved=rollback_ok,
        provenance_continuity_preserved=provenance_ok,
        explainability_continuity_preserved=bool(explainability_ok),
        governance_continuity_preserved=governance_ok,
        compatibility_continuity_preserved=compatibility_ok,
        evaluation_continuity_preserved=evaluation_ok,
        fail_visible_finding_preservation=fail_visible_ok,
        non_execution_guarantee_preserved=non_execution_ok,
        deterministic_audit_hash="",
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(result, deterministic_audit_hash=hash_v3_7_graph_scenario_audit_result(result))


def export_v3_7_graph_scenario_audit_finding(
    finding: V37GraphScenarioAuditFinding,
) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_scenario_audit_result(
    result: V37GraphScenarioAuditResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_scenario_audit_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_scenario_audit_result(result: V37GraphScenarioAuditResult) -> str:
    return stable_serialize(export_v3_7_graph_scenario_audit_result(result))


def hash_v3_7_graph_scenario_audit_result(result: V37GraphScenarioAuditResult) -> str:
    data = export_v3_7_graph_scenario_audit_result(result)
    data.pop("deterministic_audit_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    scenario: V37GraphPlanningScenario,
    findings: list[V37GraphScenarioAuditFinding],
) -> None:
    status_map = {
        V37_SCENARIO_STATUS_BLOCKED: V37_SCENARIO_AUDIT_VISIBLE_BLOCKED,
        V37_SCENARIO_STATUS_UNSUPPORTED: V37_SCENARIO_AUDIT_VISIBLE_UNSUPPORTED,
        V37_SCENARIO_STATUS_PROHIBITED: V37_SCENARIO_AUDIT_VISIBLE_PROHIBITED,
        V37_SCENARIO_STATUS_UNKNOWN: V37_SCENARIO_AUDIT_VISIBLE_UNKNOWN,
    }
    for entry in scenario.audit_trail:
        status = status_map.get(entry.scenario_status)
        if status:
            findings.append(
                _finding(
                    status,
                    entry.subject_type,
                    entry.subject_id,
                    f"{entry.scenario_status} scenario state remains fail-visible",
                    severity="visibility",
                )
            )


def _append_error_if_false(
    findings: list[V37GraphScenarioAuditFinding],
    condition: bool,
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
) -> None:
    if not condition:
        findings.append(_finding(status, subject_type, subject_id, message))


def _provenance_continuity_preserved(scenario: V37GraphPlanningScenario) -> bool:
    return (
        _provenance_complete(scenario.provenance)
        and all(_provenance_complete(variation.provenance) for variation in scenario.variations)
        and all(evidence.provenance_references for evidence in scenario.replay_evidence)
        and all(comparison.provenance_delta_references for comparison in scenario.comparison_evidence)
    )


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


def _non_execution_guarantee_preserved(scenario: V37GraphPlanningScenario) -> bool:
    return all(
        (
            scenario.scenarios_are_non_executable,
            scenario.hypothetical_planning_evidence_only,
            scenario.hypothetical_variations_are_not_runtime_branches,
            scenario.scenario_replay_evidence_is_not_runtime_replay,
            scenario.comparisons_do_not_imply_orchestration_selection,
            scenario.scenario_status_does_not_authorize_execution,
            scenario.graph_planning_scenarios_do_not_enable_routing_scheduling_dispatch_traversal,
            not scenario.graph_execution_enabled,
            not scenario.scenario_execution_enabled,
            not scenario.runtime_orchestration_enabled,
            not scenario.routing_enabled,
            not scenario.scheduling_enabled,
            not scenario.dispatch_enabled,
            not scenario.graph_traversal_execution_enabled,
            not scenario.optimization_engine_enabled,
            not scenario.recommendation_enabled,
            not scenario.autonomous_orchestration_enabled,
            not scenario.runtime_mutation_enabled,
            not scenario.persistent_runtime_writes_enabled,
            not scenario.execution_capable_scenarios_enabled,
            not scenario.runtime_branching_behavior_enabled,
            not scenario.orchestration_state_machine_enabled,
            not scenario.runtime_orchestration_history_enabled,
            all(
                variation.structural_hypothetical_evidence_only
                and not variation.executable_orchestration_branch
                for variation in scenario.variations
            ),
            all(
                evidence.non_executable_replay_evidence
                and not evidence.runtime_replay_state
                and not evidence.execution_authorization
                for evidence in scenario.replay_evidence
            ),
            all(
                not comparison.comparison_implies_orchestration_selection
                for comparison in scenario.comparison_evidence
            ),
        )
    )


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphScenarioAuditFinding:
    return V37GraphScenarioAuditFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
