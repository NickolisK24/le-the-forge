"""Fail-visible validation for deterministic v3.7 graph foundations."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_explainability import (
    V37_EXPLAINABILITY_STABLE,
    explain_v3_7_graph,
    export_v3_7_graph_explainability_result,
)
from .v3_7_graph_hashing import hash_v3_7_graph, validate_v3_7_graph_hash_stability
from .v3_7_graph_models import V3_7_VISIBILITY_VISIBLE, V37OrchestrationPlanningGraph
from .v3_7_graph_provenance import (
    V37_PROVENANCE_CONTINUITY_PRESERVED,
    audit_v3_7_graph_provenance,
    export_v3_7_graph_provenance_continuity_result,
)
from .v3_7_graph_serialization import validate_v3_7_graph_serialization_stability


V37_GRAPH_VALIDATION_STABLE = "v3_7_graph_validation_stable"
V37_GRAPH_VALIDATION_BLOCKED = "v3_7_graph_validation_blocked"
V37_GRAPH_BLOCKED_BY_DUPLICATE_NODE_IDENTITY = "v3_7_graph_blocked_by_duplicate_node_identity"
V37_GRAPH_BLOCKED_BY_DUPLICATE_EDGE_IDENTITY = "v3_7_graph_blocked_by_duplicate_edge_identity"
V37_GRAPH_BLOCKED_BY_INVALID_EDGE_REFERENCE = "v3_7_graph_blocked_by_invalid_edge_reference"
V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE = "v3_7_graph_blocked_by_prohibited_state"
V37_GRAPH_BLOCKED_BY_UNSUPPORTED_STATE_VISIBILITY_GAP = "v3_7_graph_blocked_by_unsupported_state_visibility_gap"
V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE_VISIBILITY_GAP = "v3_7_graph_blocked_by_prohibited_state_visibility_gap"
V37_GRAPH_BLOCKED_BY_GOVERNANCE_CONTINUITY_VIOLATION = (
    "v3_7_graph_blocked_by_governance_continuity_violation"
)
V37_GRAPH_BLOCKED_BY_PROVENANCE_CONTINUITY_VIOLATION = (
    "v3_7_graph_blocked_by_provenance_continuity_violation"
)
V37_GRAPH_BLOCKED_BY_SERIALIZATION_INSTABILITY = "v3_7_graph_blocked_by_serialization_instability"
V37_GRAPH_BLOCKED_BY_HASH_INSTABILITY = "v3_7_graph_blocked_by_hash_instability"
V37_GRAPH_BLOCKED_BY_EXPLAINABILITY_GAP = "v3_7_graph_blocked_by_explainability_gap"
V37_GRAPH_UNSUPPORTED_STATE_VISIBLE = "v3_7_graph_unsupported_state_visible"
V37_GRAPH_PROHIBITED_STATE_VISIBLE = "v3_7_graph_prohibited_state_visible"


@dataclass(frozen=True)
class V37GraphValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    findings: tuple[V37GraphValidationFinding, ...]
    duplicate_node_identity_count: int
    duplicate_edge_identity_count: int
    invalid_edge_reference_count: int
    unsupported_state_visible_count: int
    prohibited_state_visible_count: int
    serialization_stable: bool
    hash_stable: bool
    deterministic_graph_hash: str
    governance_continuity_preserved: bool
    provenance_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    explainability_continuity_preserved: bool
    non_execution_guarantee_preserved: bool
    deterministic_validation_hash: str = ""


def validate_v3_7_graph(graph: V37OrchestrationPlanningGraph) -> V37GraphValidationResult:
    findings: list[V37GraphValidationFinding] = []
    node_ids = tuple(node.identity.node_id for node in graph.nodes)
    edge_ids = tuple(edge.identity.edge_id for edge in graph.edges)
    duplicate_node_ids = _duplicates(node_ids)
    duplicate_edge_ids = _duplicates(edge_ids)
    findings.extend(
        _finding(
            status=V37_GRAPH_BLOCKED_BY_DUPLICATE_NODE_IDENTITY,
            subject_type="node",
            subject_id=node_id,
            message="duplicate node identity detected",
        )
        for node_id in duplicate_node_ids
    )
    findings.extend(
        _finding(
            status=V37_GRAPH_BLOCKED_BY_DUPLICATE_EDGE_IDENTITY,
            subject_type="edge",
            subject_id=edge_id,
            message="duplicate edge identity detected",
        )
        for edge_id in duplicate_edge_ids
    )

    node_id_set = set(node_ids)
    invalid_edges = tuple(
        edge.identity.edge_id
        for edge in graph.edges
        if edge.identity.source_node_id not in node_id_set or edge.identity.target_node_id not in node_id_set
    )
    findings.extend(
        _finding(
            status=V37_GRAPH_BLOCKED_BY_INVALID_EDGE_REFERENCE,
            subject_type="edge",
            subject_id=edge_id,
            message="edge references a missing source or target node",
        )
        for edge_id in invalid_edges
    )

    _add_non_execution_findings(graph, findings)
    _add_visibility_findings(graph, findings)
    _add_boundary_reference_findings(graph, findings)

    serialization = validate_v3_7_graph_serialization_stability(graph)
    if not serialization["stable"]:
        findings.append(
            _finding(
                status=V37_GRAPH_BLOCKED_BY_SERIALIZATION_INSTABILITY,
                subject_type="graph",
                subject_id=graph.identity.graph_id,
                message="serialization changed across repeated runs",
            )
        )
    hash_stability = validate_v3_7_graph_hash_stability(graph)
    if not hash_stability["stable"]:
        findings.append(
            _finding(
                status=V37_GRAPH_BLOCKED_BY_HASH_INSTABILITY,
                subject_type="graph",
                subject_id=graph.identity.graph_id,
                message="hash changed across repeated runs",
            )
        )

    provenance = audit_v3_7_graph_provenance(graph)
    if provenance.provenance_status != V37_PROVENANCE_CONTINUITY_PRESERVED:
        findings.append(
            _finding(
                status=V37_GRAPH_BLOCKED_BY_PROVENANCE_CONTINUITY_VIOLATION,
                subject_type="graph",
                subject_id=graph.identity.graph_id,
                message="provenance continuity is incomplete",
            )
        )

    explainability = explain_v3_7_graph(graph)
    if explainability.explainability_status != V37_EXPLAINABILITY_STABLE:
        findings.append(
            _finding(
                status=V37_GRAPH_BLOCKED_BY_EXPLAINABILITY_GAP,
                subject_type="graph",
                subject_id=graph.identity.graph_id,
                message="explainability evidence is incomplete",
            )
        )

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphValidationResult(
        validation_status=V37_GRAPH_VALIDATION_STABLE if error_count == 0 else V37_GRAPH_VALIDATION_BLOCKED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
        duplicate_node_identity_count=len(duplicate_node_ids),
        duplicate_edge_identity_count=len(duplicate_edge_ids),
        invalid_edge_reference_count=len(invalid_edges),
        unsupported_state_visible_count=len(graph.unsupported_domains),
        prohibited_state_visible_count=len(graph.prohibited_domains),
        serialization_stable=serialization["stable"],
        hash_stable=hash_stability["stable"],
        deterministic_graph_hash=hash_v3_7_graph(graph),
        governance_continuity_preserved=not _governance_reference_gaps(graph),
        provenance_continuity_preserved=provenance.provenance_status == V37_PROVENANCE_CONTINUITY_PRESERVED,
        replay_continuity_preserved=provenance.replay_continuity_preserved,
        rollback_continuity_preserved=provenance.rollback_continuity_preserved,
        explainability_continuity_preserved=explainability.explainability_status == V37_EXPLAINABILITY_STABLE,
        non_execution_guarantee_preserved=_non_execution_guarantee_preserved(graph),
    )
    return replace(result, deterministic_validation_hash=hash_v3_7_graph_validation_result(result))


def export_v3_7_graph_validation_finding(finding: V37GraphValidationFinding) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_validation_result(result: V37GraphValidationResult) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_validation_result(result: V37GraphValidationResult) -> str:
    return stable_serialize(export_v3_7_graph_validation_result(result))


def hash_v3_7_graph_validation_result(result: V37GraphValidationResult) -> str:
    data = export_v3_7_graph_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def export_v3_7_validation_supporting_evidence(graph: V37OrchestrationPlanningGraph) -> dict[str, Any]:
    return {
        "provenance": export_v3_7_graph_provenance_continuity_result(audit_v3_7_graph_provenance(graph)),
        "explainability": export_v3_7_graph_explainability_result(explain_v3_7_graph(graph)),
    }


def _duplicates(values: tuple[str, ...]) -> tuple[str, ...]:
    counts = Counter(values)
    return tuple(sorted(value for value, count in counts.items() if count > 1))


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphValidationFinding:
    return V37GraphValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )


def _add_non_execution_findings(
    graph: V37OrchestrationPlanningGraph,
    findings: list[V37GraphValidationFinding],
) -> None:
    expected_false = {
        "graph_execution_enabled": graph.graph_execution_enabled,
        "graph_traversal_execution_enabled": graph.graph_traversal_execution_enabled,
        "runtime_dispatch_enabled": graph.runtime_dispatch_enabled,
        "scheduling_enabled": graph.scheduling_enabled,
        "routing_enabled": graph.routing_enabled,
        "mutation_enabled": graph.mutation_enabled,
        "persistent_runtime_writes_enabled": graph.persistent_runtime_writes_enabled,
        "background_processing_enabled": graph.background_processing_enabled,
        "optimization_enabled": graph.optimization_enabled,
        "recommendation_enabled": graph.recommendation_enabled,
        "autonomous_orchestration_enabled": graph.autonomous_orchestration_enabled,
    }
    expected_true = {
        "planning_only": graph.planning_only,
        "structural_reasoning_only": graph.structural_reasoning_only,
        "non_executable": graph.non_executable,
    }
    for field_name, value in expected_false.items():
        if value:
            findings.append(
                _finding(
                    status=V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE,
                    subject_type="graph_flag",
                    subject_id=field_name,
                    message="execution-capable or runtime behavior flag must remain false",
                )
            )
    for field_name, value in expected_true.items():
        if not value:
            findings.append(
                _finding(
                    status=V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE,
                    subject_type="graph_flag",
                    subject_id=field_name,
                    message="planning-only non-executable graph flag must remain true",
                )
            )
    for node in graph.nodes:
        if node.node_executable or node.action_enabled:
            findings.append(
                _finding(
                    status=V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE,
                    subject_type="node",
                    subject_id=node.identity.node_id,
                    message="node implies executable behavior",
                )
            )
    for edge in graph.edges:
        if edge.edge_executable or edge.traversal_enabled or edge.execution_flow_enabled:
            findings.append(
                _finding(
                    status=V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE,
                    subject_type="edge",
                    subject_id=edge.identity.edge_id,
                    message="edge implies execution flow",
                )
            )


def _add_visibility_findings(
    graph: V37OrchestrationPlanningGraph,
    findings: list[V37GraphValidationFinding],
) -> None:
    for finding in graph.unsupported_domains:
        status = (
            V37_GRAPH_UNSUPPORTED_STATE_VISIBLE
            if finding.visibility_status == V3_7_VISIBILITY_VISIBLE
            else V37_GRAPH_BLOCKED_BY_UNSUPPORTED_STATE_VISIBILITY_GAP
        )
        findings.append(
            _finding(
                status=status,
                subject_type="unsupported_domain",
                subject_id=finding.finding_id,
                message=finding.reason,
                severity="visibility" if status == V37_GRAPH_UNSUPPORTED_STATE_VISIBLE else "error",
            )
        )
    for finding in graph.prohibited_domains:
        status = (
            V37_GRAPH_PROHIBITED_STATE_VISIBLE
            if finding.visibility_status == V3_7_VISIBILITY_VISIBLE
            else V37_GRAPH_BLOCKED_BY_PROHIBITED_STATE_VISIBILITY_GAP
        )
        findings.append(
            _finding(
                status=status,
                subject_type="prohibited_domain",
                subject_id=finding.finding_id,
                message=finding.reason,
                severity="visibility" if status == V37_GRAPH_PROHIBITED_STATE_VISIBLE else "error",
            )
        )


def _add_boundary_reference_findings(
    graph: V37OrchestrationPlanningGraph,
    findings: list[V37GraphValidationFinding],
) -> None:
    for subject_type, subject_id, missing_ids in _governance_reference_gaps(graph):
        findings.append(
            _finding(
                status=V37_GRAPH_BLOCKED_BY_GOVERNANCE_CONTINUITY_VIOLATION,
                subject_type=subject_type,
                subject_id=subject_id,
                message=f"missing governance boundary references: {', '.join(missing_ids)}",
            )
        )


def _governance_reference_gaps(graph: V37OrchestrationPlanningGraph) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    known = {boundary.boundary_id for boundary in graph.governance_boundaries}
    continuity_refs = {
        reference
        for continuity in graph.continuity_evidence
        for reference in continuity.governance_lineage_references
    }
    gaps: list[tuple[str, str, tuple[str, ...]]] = []
    for node in graph.nodes:
        missing = tuple(sorted(set(node.governance_boundary_ids) - known))
        if missing:
            gaps.append(("node", node.identity.node_id, missing))
    for edge in graph.edges:
        missing = tuple(sorted(set(edge.governance_boundary_ids) - known))
        if missing:
            gaps.append(("edge", edge.identity.edge_id, missing))
    missing_continuity = tuple(sorted(known - continuity_refs))
    if missing_continuity:
        gaps.append(("graph", graph.identity.graph_id, missing_continuity))
    return tuple(gaps)


def _non_execution_guarantee_preserved(graph: V37OrchestrationPlanningGraph) -> bool:
    return (
        graph.planning_only
        and graph.structural_reasoning_only
        and graph.non_executable
        and not graph.graph_execution_enabled
        and not graph.graph_traversal_execution_enabled
        and not graph.runtime_dispatch_enabled
        and not graph.scheduling_enabled
        and not graph.routing_enabled
        and not graph.mutation_enabled
        and not graph.persistent_runtime_writes_enabled
        and not graph.background_processing_enabled
        and not graph.optimization_enabled
        and not graph.recommendation_enabled
        and not graph.autonomous_orchestration_enabled
        and all(not node.node_executable and not node.action_enabled for node in graph.nodes)
        and all(
            not edge.edge_executable and not edge.traversal_enabled and not edge.execution_flow_enabled
            for edge in graph.edges
        )
    )
