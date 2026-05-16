"""Fail-visible validation for v3.7 graph planning scenarios."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_scenario_audit import (
    V37_GRAPH_SCENARIO_AUDIT_STABLE,
    audit_v3_7_graph_scenario,
)
from .v3_7_graph_scenario_explainability import (
    V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_scenario,
)
from .v3_7_graph_scenario_identity import graph_scenario_identities_are_unique
from .v3_7_graph_scenario_models import (
    V37_SCENARIO_STATUS_PROHIBITED,
    V37_SCENARIO_STATUS_UNKNOWN,
    V37_SCENARIO_STATUS_UNSUPPORTED,
    V37GraphPlanningScenario,
    hash_v3_7_graph_planning_scenario,
    validate_v3_7_graph_scenario_hash_stability,
    validate_v3_7_graph_scenario_serialization_stability,
)
from .v3_7_graph_scenario_provenance import (
    V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED,
    audit_v3_7_graph_scenario_provenance,
)
from .v3_7_graph_scenario_replay import validate_v3_7_graph_scenario_replay_evidence
from .v3_7_graph_scenario_variations import build_v3_7_graph_planning_scenario


V37_GRAPH_SCENARIO_VALIDATION_STABLE = "v3_7_graph_scenario_validation_stable"
V37_GRAPH_SCENARIO_VALIDATION_BLOCKED = "v3_7_graph_scenario_validation_blocked"
V37_SCENARIO_VALIDATION_VISIBLE_PROHIBITED = "v3_7_graph_scenario_validation_visible_prohibited"
V37_SCENARIO_VALIDATION_VISIBLE_UNSUPPORTED = "v3_7_graph_scenario_validation_visible_unsupported"
V37_SCENARIO_VALIDATION_VISIBLE_UNKNOWN = "v3_7_graph_scenario_validation_visible_unknown"
V37_SCENARIO_VALIDATION_BLOCKED_BY_DUPLICATE_IDENTITY = "v3_7_graph_scenario_blocked_by_duplicate_identity"
V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_VARIATION = "v3_7_graph_scenario_blocked_by_invalid_variation"
V37_SCENARIO_VALIDATION_BLOCKED_BY_MISSING_GRAPH_SNAPSHOT = "v3_7_graph_scenario_blocked_by_missing_graph_snapshot"
V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_REPLAY_EVIDENCE = "v3_7_graph_scenario_blocked_by_invalid_replay_evidence"
V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_COMPARISON = "v3_7_graph_scenario_blocked_by_invalid_comparison"
V37_SCENARIO_VALIDATION_BLOCKED_BY_PROVENANCE = "v3_7_graph_scenario_blocked_by_provenance"
V37_SCENARIO_VALIDATION_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_scenario_blocked_by_explainability"
V37_SCENARIO_VALIDATION_BLOCKED_BY_GOVERNANCE = "v3_7_graph_scenario_blocked_by_governance"
V37_SCENARIO_VALIDATION_BLOCKED_BY_COMPATIBILITY = "v3_7_graph_scenario_blocked_by_compatibility"
V37_SCENARIO_VALIDATION_BLOCKED_BY_EVALUATION = "v3_7_graph_scenario_blocked_by_evaluation"
V37_SCENARIO_VALIDATION_BLOCKED_BY_HIDDEN_STATE = "v3_7_graph_scenario_blocked_by_hidden_state"
V37_SCENARIO_VALIDATION_BLOCKED_BY_SERIALIZATION = "v3_7_graph_scenario_blocked_by_serialization"
V37_SCENARIO_VALIDATION_BLOCKED_BY_HASH = "v3_7_graph_scenario_blocked_by_hash"
V37_SCENARIO_VALIDATION_BLOCKED_BY_EXECUTION_CAPABILITY = "v3_7_graph_scenario_blocked_by_execution_capability"


@dataclass(frozen=True)
class V37GraphScenarioValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphScenarioValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    duplicate_scenario_identity_count: int
    invalid_variation_reference_count: int
    missing_graph_snapshot_reference_count: int
    invalid_replay_evidence_reference_count: int
    invalid_comparison_reference_count: int
    hidden_prohibited_state_count: int
    hidden_unsupported_state_count: int
    hidden_unknown_state_count: int
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    governance_continuity_preserved: bool
    compatibility_continuity_preserved: bool
    evaluation_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    non_execution_guarantee_preserved: bool
    deterministic_scenario_hash: str
    findings: tuple[V37GraphScenarioValidationFinding, ...]
    deterministic_validation_hash: str = ""


def validate_v3_7_graph_scenarios(
    scenarios: tuple[V37GraphPlanningScenario, ...] | None = None,
) -> V37GraphScenarioValidationResult:
    planning_scenarios = scenarios or (build_v3_7_graph_planning_scenario(),)
    primary = planning_scenarios[0]
    findings: list[V37GraphScenarioValidationFinding] = []
    duplicate_count = 0 if graph_scenario_identities_are_unique(tuple(item.identity for item in planning_scenarios)) else 1
    if duplicate_count:
        findings.append(
            _finding(
                V37_SCENARIO_VALIDATION_BLOCKED_BY_DUPLICATE_IDENTITY,
                "graph_planning_scenarios",
                primary.identity.scenario_id,
                "duplicate scenario identity detected",
            )
        )
    for scenario in planning_scenarios:
        _add_visibility_findings(scenario, findings)
        variation_ids = {variation.variation_id for variation in scenario.variations}
        if not scenario.variations or any(
            variation.scenario_id != scenario.identity.scenario_id
            or variation.graph_snapshot_reference not in scenario.graph_snapshot_references
            or variation.executable_orchestration_branch
            or not variation.structural_hypothetical_evidence_only
            for variation in scenario.variations
        ):
            findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_VARIATION, "scenario", scenario.identity.scenario_id, "invalid scenario variation reference"))
        if not scenario.graph_snapshot_references:
            findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_MISSING_GRAPH_SNAPSHOT, "scenario", scenario.identity.scenario_id, "missing graph snapshot reference"))
        if not scenario.replay_evidence or any(
            not evidence.variation_references
            or not evidence.graph_snapshot_references
            or not evidence.evaluation_references
            or not evidence.continuity_hashes
            or evidence.runtime_replay_state
            or evidence.execution_authorization
            for evidence in scenario.replay_evidence
        ):
            findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_REPLAY_EVIDENCE, "scenario", scenario.identity.scenario_id, "invalid scenario replay evidence"))
        if not scenario.comparison_evidence or any(
            not comparison.compared_variation_ids
            or not set(comparison.compared_variation_ids).issubset(variation_ids)
            or comparison.comparison_implies_orchestration_selection
            for comparison in scenario.comparison_evidence
        ):
            findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_COMPARISON, "scenario", scenario.identity.scenario_id, "invalid scenario comparison evidence"))
        for entry in scenario.audit_trail:
            if entry.scenario_status in (V37_SCENARIO_STATUS_PROHIBITED, V37_SCENARIO_STATUS_UNSUPPORTED, V37_SCENARIO_STATUS_UNKNOWN) and (entry.hidden or not entry.fail_visible):
                findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_HIDDEN_STATE, entry.subject_type, entry.subject_id, f"hidden {entry.scenario_status} state detected"))

    audit = audit_v3_7_graph_scenario(primary)
    provenance = audit_v3_7_graph_scenario_provenance(primary)
    explainability = explain_v3_7_graph_scenario(primary)
    replay = validate_v3_7_graph_scenario_replay_evidence(primary)
    serialization = validate_v3_7_graph_scenario_serialization_stability(primary)
    hashing = validate_v3_7_graph_scenario_hash_stability(primary)

    if audit.audit_status != V37_GRAPH_SCENARIO_AUDIT_STABLE:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_VARIATION, "scenario", primary.identity.scenario_id, "scenario audit is unstable"))
    if provenance.provenance_status != V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_PROVENANCE, "scenario", primary.identity.scenario_id, "scenario provenance continuity is incomplete"))
    if explainability.explainability_status != V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_EXPLAINABILITY, "scenario", primary.identity.scenario_id, "scenario explainability continuity is incomplete"))
    if not audit.governance_continuity_preserved:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_GOVERNANCE, "scenario", primary.identity.scenario_id, "scenario governance continuity is incomplete"))
    if not audit.compatibility_continuity_preserved:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_COMPATIBILITY, "scenario", primary.identity.scenario_id, "scenario compatibility continuity is incomplete"))
    if not audit.evaluation_continuity_preserved:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_EVALUATION, "scenario", primary.identity.scenario_id, "scenario evaluation continuity is incomplete"))
    if not replay["replay_continuity_preserved"]:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_REPLAY_EVIDENCE, "scenario", primary.identity.scenario_id, "scenario replay continuity is incomplete"))
    if not replay["rollback_continuity_preserved"]:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_REPLAY_EVIDENCE, "scenario", primary.identity.scenario_id, "scenario rollback continuity is incomplete"))
    if not serialization["stable"]:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_SERIALIZATION, "scenario", primary.identity.scenario_id, "scenario serialization is unstable"))
    if not hashing["stable"]:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_HASH, "scenario", primary.identity.scenario_id, "scenario hash is unstable"))
    if not audit.non_execution_guarantee_preserved:
        findings.append(_finding(V37_SCENARIO_VALIDATION_BLOCKED_BY_EXECUTION_CAPABILITY, "scenario", primary.identity.scenario_id, "scenario exposed execution capability"))

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphScenarioValidationResult(
        validation_status=V37_GRAPH_SCENARIO_VALIDATION_STABLE if error_count == 0 else V37_GRAPH_SCENARIO_VALIDATION_BLOCKED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        duplicate_scenario_identity_count=duplicate_count,
        invalid_variation_reference_count=sum(1 for finding in findings if finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_VARIATION),
        missing_graph_snapshot_reference_count=sum(1 for finding in findings if finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_MISSING_GRAPH_SNAPSHOT),
        invalid_replay_evidence_reference_count=sum(1 for finding in findings if finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_REPLAY_EVIDENCE),
        invalid_comparison_reference_count=sum(1 for finding in findings if finding.status == V37_SCENARIO_VALIDATION_BLOCKED_BY_INVALID_COMPARISON),
        hidden_prohibited_state_count=_hidden_state_count(planning_scenarios, V37_SCENARIO_STATUS_PROHIBITED),
        hidden_unsupported_state_count=_hidden_state_count(planning_scenarios, V37_SCENARIO_STATUS_UNSUPPORTED),
        hidden_unknown_state_count=_hidden_state_count(planning_scenarios, V37_SCENARIO_STATUS_UNKNOWN),
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=explainability.explainability_status == V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE,
        governance_continuity_preserved=audit.governance_continuity_preserved,
        compatibility_continuity_preserved=audit.compatibility_continuity_preserved,
        evaluation_continuity_preserved=audit.evaluation_continuity_preserved,
        replay_continuity_preserved=replay["replay_continuity_preserved"],
        rollback_continuity_preserved=replay["rollback_continuity_preserved"],
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        non_execution_guarantee_preserved=audit.non_execution_guarantee_preserved,
        deterministic_scenario_hash=hash_v3_7_graph_planning_scenario(primary),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(result, deterministic_validation_hash=hash_v3_7_graph_scenario_validation_result(result))


def export_v3_7_graph_scenario_validation_finding(
    finding: V37GraphScenarioValidationFinding,
) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_scenario_validation_result(
    result: V37GraphScenarioValidationResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_scenario_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_scenario_validation_result(
    result: V37GraphScenarioValidationResult,
) -> str:
    return stable_serialize(export_v3_7_graph_scenario_validation_result(result))


def hash_v3_7_graph_scenario_validation_result(
    result: V37GraphScenarioValidationResult,
) -> str:
    data = export_v3_7_graph_scenario_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    scenario: V37GraphPlanningScenario,
    findings: list[V37GraphScenarioValidationFinding],
) -> None:
    status_map = {
        V37_SCENARIO_STATUS_PROHIBITED: V37_SCENARIO_VALIDATION_VISIBLE_PROHIBITED,
        V37_SCENARIO_STATUS_UNSUPPORTED: V37_SCENARIO_VALIDATION_VISIBLE_UNSUPPORTED,
        V37_SCENARIO_STATUS_UNKNOWN: V37_SCENARIO_VALIDATION_VISIBLE_UNKNOWN,
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


def _hidden_state_count(scenarios: tuple[V37GraphPlanningScenario, ...], status: str) -> int:
    return sum(
        1
        for scenario in scenarios
        for entry in scenario.audit_trail
        if entry.scenario_status == status and (entry.hidden or not entry.fail_visible)
    )


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphScenarioValidationFinding:
    return V37GraphScenarioValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
