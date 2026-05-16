"""Fail-visible validation for v3.7 graph compatibility reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_compatibility_explainability import (
    V37_COMPATIBILITY_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_compatibility,
)
from .v3_7_graph_compatibility_models import (
    V37_COMPATIBILITY_VISIBILITY_VISIBLE,
    V37_COMPATIBILITY_RESTRICTED,
    V37_COMPATIBLE,
    V37_EXPERIMENTAL_COMPATIBILITY,
    V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
    V37_INCOMPATIBLE,
    V37_PROHIBITED_COMPATIBILITY,
    V37_UNKNOWN_COMPATIBILITY,
    V37_UNSUPPORTED_COMPATIBILITY,
    V37GraphCompatibilityMap,
    hash_v3_7_compatibility_map,
    validate_v3_7_compatibility_hash_stability,
    validate_v3_7_compatibility_serialization_stability,
)
from .v3_7_graph_compatibility_provenance import (
    V37_COMPATIBILITY_PROVENANCE_PRESERVED,
    audit_v3_7_graph_compatibility_provenance,
)


V37_COMPATIBILITY_VALIDATION_STABLE = "v3_7_graph_compatibility_validation_stable"
V37_COMPATIBILITY_VALIDATION_BLOCKED = "v3_7_graph_compatibility_validation_blocked"
V37_COMPATIBILITY_COMPATIBLE_VISIBLE = "v3_7_graph_compatibility_compatible_visible"
V37_COMPATIBILITY_INCOMPATIBLE_VISIBLE = "v3_7_graph_compatibility_incompatible_visible"
V37_COMPATIBILITY_UNSUPPORTED_VISIBLE = "v3_7_graph_compatibility_unsupported_visible"
V37_COMPATIBILITY_PROHIBITED_VISIBLE = "v3_7_graph_compatibility_prohibited_visible"
V37_COMPATIBILITY_UNKNOWN_VISIBLE = "v3_7_graph_compatibility_unknown_visible"
V37_COMPATIBILITY_BLOCKED_BY_PROHIBITED_STATE = "v3_7_graph_compatibility_blocked_by_prohibited_state"
V37_COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_STATE = "v3_7_graph_compatibility_blocked_by_unsupported_state"
V37_COMPATIBILITY_BLOCKED_BY_UNKNOWN_STATE = "v3_7_graph_compatibility_blocked_by_unknown_state"
V37_COMPATIBILITY_BLOCKED_BY_MISSING_METADATA = "v3_7_graph_compatibility_blocked_by_missing_metadata"
V37_COMPATIBILITY_BLOCKED_BY_INCOMPATIBLE_NODE_RELATIONSHIP = (
    "v3_7_graph_compatibility_blocked_by_incompatible_node_relationship"
)
V37_COMPATIBILITY_BLOCKED_BY_INCOMPATIBLE_EDGE_RELATIONSHIP = (
    "v3_7_graph_compatibility_blocked_by_incompatible_edge_relationship"
)
V37_COMPATIBILITY_BLOCKED_BY_GOVERNANCE_VIOLATION = "v3_7_graph_compatibility_blocked_by_governance_violation"
V37_COMPATIBILITY_BLOCKED_BY_PROVENANCE_DISCONTINUITY = (
    "v3_7_graph_compatibility_blocked_by_provenance_discontinuity"
)
V37_COMPATIBILITY_BLOCKED_BY_EXPLAINABILITY_DISCONTINUITY = (
    "v3_7_graph_compatibility_blocked_by_explainability_discontinuity"
)
V37_COMPATIBILITY_BLOCKED_BY_SERIALIZATION_INSTABILITY = (
    "v3_7_graph_compatibility_blocked_by_serialization_instability"
)
V37_COMPATIBILITY_BLOCKED_BY_HASH_INSTABILITY = "v3_7_graph_compatibility_blocked_by_hash_instability"
V37_COMPATIBILITY_BLOCKED_BY_EXECUTION_CAPABILITY = "v3_7_graph_compatibility_blocked_by_execution_capability"


@dataclass(frozen=True)
class V37GraphCompatibilityValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphCompatibilityValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    prohibited_state_count: int
    unsupported_state_count: int
    unknown_state_count: int
    incompatible_node_relationship_count: int
    incompatible_edge_relationship_count: int
    missing_metadata_count: int
    governance_aware_outcome_count: int
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    serialization_stable: bool
    hash_stable: bool
    non_execution_guarantee_preserved: bool
    deterministic_compatibility_hash: str
    findings: tuple[V37GraphCompatibilityValidationFinding, ...]
    deterministic_validation_hash: str = ""


def validate_v3_7_graph_compatibility(
    compatibility_map: V37GraphCompatibilityMap,
) -> V37GraphCompatibilityValidationResult:
    findings: list[V37GraphCompatibilityValidationFinding] = []
    _add_visibility_findings(compatibility_map, findings)
    _add_result_findings(compatibility_map, findings)
    _add_continuity_findings(compatibility_map, findings)
    _add_non_execution_findings(compatibility_map, findings)

    serialization = validate_v3_7_compatibility_serialization_stability(compatibility_map)
    if not serialization["stable"]:
        findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_SERIALIZATION_INSTABILITY, "compatibility_map", compatibility_map.graph_id, "compatibility serialization is unstable"))
    hashing = validate_v3_7_compatibility_hash_stability(compatibility_map)
    if not hashing["stable"]:
        findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_HASH_INSTABILITY, "compatibility_map", compatibility_map.graph_id, "compatibility hash is unstable"))

    provenance = audit_v3_7_graph_compatibility_provenance(compatibility_map)
    if provenance.provenance_status != V37_COMPATIBILITY_PROVENANCE_PRESERVED:
        findings.append(
            _finding(
                V37_COMPATIBILITY_BLOCKED_BY_PROVENANCE_DISCONTINUITY,
                "compatibility_map",
                compatibility_map.graph_id,
                "compatibility provenance continuity is incomplete",
            )
        )
    explainability = explain_v3_7_graph_compatibility(compatibility_map)
    if explainability.explainability_status != V37_COMPATIBILITY_EXPLAINABILITY_STABLE:
        findings.append(
            _finding(
                V37_COMPATIBILITY_BLOCKED_BY_EXPLAINABILITY_DISCONTINUITY,
                "compatibility_map",
                compatibility_map.graph_id,
                "compatibility explainability continuity is incomplete",
            )
        )

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphCompatibilityValidationResult(
        validation_status=(
            V37_COMPATIBILITY_VALIDATION_STABLE
            if error_count == 0
            else V37_COMPATIBILITY_VALIDATION_BLOCKED
        ),
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        prohibited_state_count=_result_class_count(compatibility_map, V37_PROHIBITED_COMPATIBILITY),
        unsupported_state_count=_result_class_count(compatibility_map, V37_UNSUPPORTED_COMPATIBILITY),
        unknown_state_count=_result_class_count(compatibility_map, V37_UNKNOWN_COMPATIBILITY),
        incompatible_node_relationship_count=sum(
            1 for result in compatibility_map.node_results if result.compatibility_classification == V37_INCOMPATIBLE
        ),
        incompatible_edge_relationship_count=sum(
            1 for result in compatibility_map.edge_results if result.compatibility_classification == V37_INCOMPATIBLE
        ),
        missing_metadata_count=sum(
            1 for finding in findings if finding.status == V37_COMPATIBILITY_BLOCKED_BY_MISSING_METADATA
        ),
        governance_aware_outcome_count=_result_class_count(
            compatibility_map,
            V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
        ) + _result_class_count(compatibility_map, V37_COMPATIBILITY_RESTRICTED),
        provenance_continuity_preserved=provenance.provenance_status == V37_COMPATIBILITY_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=(
            explainability.explainability_status == V37_COMPATIBILITY_EXPLAINABILITY_STABLE
        ),
        replay_continuity_preserved=provenance.replay_continuity_preserved,
        rollback_continuity_preserved=provenance.rollback_continuity_preserved,
        serialization_stable=serialization["stable"],
        hash_stable=hashing["stable"],
        non_execution_guarantee_preserved=_non_execution_guarantee_preserved(compatibility_map),
        deterministic_compatibility_hash=hash_v3_7_compatibility_map(compatibility_map),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(
        result,
        deterministic_validation_hash=hash_v3_7_graph_compatibility_validation_result(result),
    )


def export_v3_7_graph_compatibility_validation_finding(
    finding: V37GraphCompatibilityValidationFinding,
) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_compatibility_validation_result(
    result: V37GraphCompatibilityValidationResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_compatibility_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_compatibility_validation_result(
    result: V37GraphCompatibilityValidationResult,
) -> str:
    return stable_serialize(export_v3_7_graph_compatibility_validation_result(result))


def hash_v3_7_graph_compatibility_validation_result(
    result: V37GraphCompatibilityValidationResult,
) -> str:
    data = export_v3_7_graph_compatibility_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphCompatibilityValidationFinding:
    return V37GraphCompatibilityValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )


def _add_visibility_findings(
    compatibility_map: V37GraphCompatibilityMap,
    findings: list[V37GraphCompatibilityValidationFinding],
) -> None:
    status_by_classification = {
        V37_COMPATIBLE: V37_COMPATIBILITY_COMPATIBLE_VISIBLE,
        V37_INCOMPATIBLE: V37_COMPATIBILITY_INCOMPATIBLE_VISIBLE,
        V37_UNSUPPORTED_COMPATIBILITY: V37_COMPATIBILITY_UNSUPPORTED_VISIBLE,
        V37_PROHIBITED_COMPATIBILITY: V37_COMPATIBILITY_PROHIBITED_VISIBLE,
        V37_UNKNOWN_COMPATIBILITY: V37_COMPATIBILITY_UNKNOWN_VISIBLE,
    }
    for finding in compatibility_map.findings:
        if finding.visibility_status != V37_COMPATIBILITY_VISIBILITY_VISIBLE:
            findings.append(
                _finding(
                    V37_COMPATIBILITY_BLOCKED_BY_MISSING_METADATA,
                    finding.subject_type,
                    finding.subject_id,
                    "compatibility finding visibility is missing",
                )
            )
            continue
        status = status_by_classification.get(finding.compatibility_classification)
        if status:
            findings.append(
                _finding(
                    status,
                    finding.subject_type,
                    finding.subject_id,
                    finding.reason,
                    severity="visibility",
                )
            )


def _add_result_findings(
    compatibility_map: V37GraphCompatibilityMap,
    findings: list[V37GraphCompatibilityValidationFinding],
) -> None:
    for result in compatibility_map.node_results:
        if not result.source_domain_id or not result.target_domain_id or not result.rule_id:
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_MISSING_METADATA, "node_compatibility", result.relationship_id, "node compatibility metadata is missing"))
        _add_state_finding("node_compatibility", result.relationship_id, result.compatibility_classification, findings)
        if result.node_relationship_implies_runtime_ordering:
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_EXECUTION_CAPABILITY, "node_compatibility", result.relationship_id, "node compatibility implies runtime ordering"))
        if result.compatibility_classification == V37_INCOMPATIBLE:
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_INCOMPATIBLE_NODE_RELATIONSHIP, "node_compatibility", result.relationship_id, "node compatibility is incompatible"))
    for result in compatibility_map.edge_results:
        if not result.rule_id or not result.domain_compatibility_classification:
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_MISSING_METADATA, "edge_compatibility", result.edge_id, "edge compatibility metadata is missing"))
        _add_state_finding("edge_compatibility", result.edge_id, result.compatibility_classification, findings)
        if result.edge_compatibility_implies_traversal or result.traversal_enabled:
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_EXECUTION_CAPABILITY, "edge_compatibility", result.edge_id, "edge compatibility implies traversal"))
        if result.compatibility_classification == V37_INCOMPATIBLE:
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_INCOMPATIBLE_EDGE_RELATIONSHIP, "edge_compatibility", result.edge_id, "edge compatibility is incompatible"))
        if (
            result.compatibility_classification == V37_COMPATIBLE
            and "prohibited" in result.edge_governance_classification
        ):
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_GOVERNANCE_VIOLATION, "edge_compatibility", result.edge_id, "edge compatibility ignores prohibited governance"))


def _add_state_finding(
    subject_type: str,
    subject_id: str,
    classification: str,
    findings: list[V37GraphCompatibilityValidationFinding],
) -> None:
    if classification == V37_PROHIBITED_COMPATIBILITY:
        findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_PROHIBITED_STATE, subject_type, subject_id, "prohibited compatibility state"))
    if classification == V37_UNSUPPORTED_COMPATIBILITY:
        findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_STATE, subject_type, subject_id, "unsupported compatibility state"))
    if classification == V37_UNKNOWN_COMPATIBILITY:
        findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_UNKNOWN_STATE, subject_type, subject_id, "unknown compatibility state"))


def _add_continuity_findings(
    compatibility_map: V37GraphCompatibilityMap,
    findings: list[V37GraphCompatibilityValidationFinding],
) -> None:
    for subject_id, message in _continuity_gaps(compatibility_map):
        findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_MISSING_METADATA, "continuity", subject_id, message))


def _add_non_execution_findings(
    compatibility_map: V37GraphCompatibilityMap,
    findings: list[V37GraphCompatibilityValidationFinding],
) -> None:
    expected_false = {
        "graph_execution_enabled": compatibility_map.graph_execution_enabled,
        "node_execution_enabled": compatibility_map.node_execution_enabled,
        "edge_traversal_execution_enabled": compatibility_map.edge_traversal_execution_enabled,
        "runtime_orchestration_enabled": compatibility_map.runtime_orchestration_enabled,
        "routing_enabled": compatibility_map.routing_enabled,
        "scheduling_enabled": compatibility_map.scheduling_enabled,
        "dispatch_enabled": compatibility_map.dispatch_enabled,
        "graph_optimization_enabled": compatibility_map.graph_optimization_enabled,
        "recommendation_enabled": compatibility_map.recommendation_enabled,
        "autonomous_orchestration_enabled": compatibility_map.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": compatibility_map.runtime_mutation_enabled,
        "background_graph_processing_enabled": compatibility_map.background_graph_processing_enabled,
        "graph_path_selection_enabled": compatibility_map.graph_path_selection_enabled,
    }
    expected_true = {
        "compatibility_reasoning_is_non_executable": compatibility_map.compatibility_reasoning_is_non_executable,
        "compatibility_does_not_authorize_execution": compatibility_map.compatibility_does_not_authorize_execution,
        "edge_compatibility_does_not_imply_traversal": compatibility_map.edge_compatibility_does_not_imply_traversal,
        "node_compatibility_does_not_imply_runtime_ordering": (
            compatibility_map.node_compatibility_does_not_imply_runtime_ordering
        ),
        "structural_planning_evidence_only": compatibility_map.structural_planning_evidence_only,
    }
    for field_name, value in expected_false.items():
        if value:
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_EXECUTION_CAPABILITY, "compatibility_flag", field_name, "execution-capable compatibility flag must remain false"))
    for field_name, value in expected_true.items():
        if not value:
            findings.append(_finding(V37_COMPATIBILITY_BLOCKED_BY_EXECUTION_CAPABILITY, "compatibility_flag", field_name, "non-executable compatibility flag must remain true"))


def _continuity_gaps(compatibility_map: V37GraphCompatibilityMap) -> tuple[tuple[str, str], ...]:
    if not compatibility_map.continuity_evidence:
        return ((compatibility_map.graph_id, "compatibility continuity evidence is missing"),)
    continuity = compatibility_map.continuity_evidence[0]
    gaps: list[tuple[str, str]] = []
    if {item.domain_id for item in compatibility_map.domains} - set(continuity.domain_ids):
        gaps.append((continuity.continuity_id, "domain continuity references are incomplete"))
    if {item.rule_id for item in compatibility_map.rules} - set(continuity.rule_ids):
        gaps.append((continuity.continuity_id, "rule continuity references are incomplete"))
    if {item.relationship_id for item in compatibility_map.node_results} - set(continuity.node_relationship_ids):
        gaps.append((continuity.continuity_id, "node relationship continuity references are incomplete"))
    if {item.edge_id for item in compatibility_map.edge_results} - set(continuity.edge_relationship_ids):
        gaps.append((continuity.continuity_id, "edge relationship continuity references are incomplete"))
    if {item.finding_id for item in compatibility_map.findings} - set(continuity.finding_ids):
        gaps.append((continuity.continuity_id, "finding continuity references are incomplete"))
    return tuple(gaps)


def _result_class_count(compatibility_map: V37GraphCompatibilityMap, classification: str) -> int:
    return sum(
        1
        for result in compatibility_map.node_results
        if result.compatibility_classification == classification
    ) + sum(
        1
        for result in compatibility_map.edge_results
        if result.compatibility_classification == classification
    )


def _non_execution_guarantee_preserved(compatibility_map: V37GraphCompatibilityMap) -> bool:
    return (
        compatibility_map.compatibility_reasoning_is_non_executable
        and compatibility_map.compatibility_does_not_authorize_execution
        and compatibility_map.edge_compatibility_does_not_imply_traversal
        and compatibility_map.node_compatibility_does_not_imply_runtime_ordering
        and compatibility_map.structural_planning_evidence_only
        and not compatibility_map.graph_execution_enabled
        and not compatibility_map.node_execution_enabled
        and not compatibility_map.edge_traversal_execution_enabled
        and not compatibility_map.runtime_orchestration_enabled
        and not compatibility_map.routing_enabled
        and not compatibility_map.scheduling_enabled
        and not compatibility_map.dispatch_enabled
        and not compatibility_map.graph_optimization_enabled
        and not compatibility_map.recommendation_enabled
        and not compatibility_map.autonomous_orchestration_enabled
        and not compatibility_map.runtime_mutation_enabled
        and not compatibility_map.background_graph_processing_enabled
        and not compatibility_map.graph_path_selection_enabled
        and all(not result.node_relationship_implies_runtime_ordering for result in compatibility_map.node_results)
        and all(
            not result.edge_compatibility_implies_traversal and not result.traversal_enabled
            for result in compatibility_map.edge_results
        )
    )
